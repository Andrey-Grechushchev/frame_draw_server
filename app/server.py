# app/server.py

"""
Flask-сервер для генерации PDF-чертежей по данным из HTML-формы.

Основные функции:
- Принимает POST-запрос на /generate с полями формы.
- Выполняет проверку авторизации по токену (через заголовок Authorization).
- Обрабатывает чекбоксы: если передано "on" — преобразует в True, иначе False.
- Создаёт уникальное имя PDF-файла с учётом текущей даты и времени.
- Сохраняет файлы в папке static/downloads/YYYY-MM-DD/.
- Вызывает функцию `generate_pdf_safe`, которая запускает генерацию PDF в отдельном процессе
  (изолировано от основного потока Flask, надёжнее при использовании CairoSVG).
- По завершении отдаёт PDF-файл пользователю с заголовками Content-Disposition.
- При ошибке возвращает JSON-ответ с описанием исключения.

Особенности:
- Используется `multiprocessing` для предотвращения проблем с CairoSVG в однопоточном сервере.
- Переменные окружения загружаются через `dotenv`, включая SECRET_TOKEN.
- Структура гибкая: путь сохранения и имя файла формируются динамически.
- Поддержка CORS включена (`flask_cors.CORS`) для работы с фронтендом, запущенным отдельно.
- Уникальность файлов обеспечивается за счёт добавления временной метки.

Применение:
- Подходит для интеграции с HTML-формами, SPA или другими клиентами, которые могут отправить POST-запрос.
- Может использоваться как временный прототип или база для последующей адаптации под CMS (например, Drupal).

Важно:
- Текущий подход не использует встроенные механизмы безопасности Drupal (CSRF, сессии, формы).
- Не совместим напрямую с Drupal Form API — требует доработки, если интеграция планируется напрямую в CMS.
"""

from flask import Flask, request, jsonify, send_file, render_template
from flask_cors import CORS
import os
from datetime import datetime
from multiprocessing import Process, Queue
from generate_drawing import generate_pdf
from configs.config import DEFAULT_FILENAME, checkbox_fields
from configs.config_log import logger
from dotenv import load_dotenv

load_dotenv()

# Корень проекта (на уровень выше app/)
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# Говорим Flask, где лежат templates/
app = Flask(__name__, template_folder=os.path.join(BASE_DIR, "templates"))
CORS(app)

# Конфигурация
# По умолчанию используем тот же токен, что и в форме, чтобы dev-окружение работало без .env
SECRET_TOKEN = os.getenv("SECRET_TOKEN", "secure_token_Aspex")


def generate_pdf_safe(svg_path, pdf_path, values, disable_svg_debug, save_pdf, draw_debug_grid):
    """
    Безопасно запускает процесс генерации PDF-файла в отдельном процессе с поддержкой
    возврата результата через очередь.

    Аргументы:
        svg_path (str): Путь к SVG-файлу, который нужно отрендерить.
        pdf_path (str): Путь, по которому будет сохранён итоговый PDF-файл.
        values (dict): Данные, используемые для генерации чертежа (например, размеры, настройки).
        disable_svg_debug (bool): Отключить отладочную информацию в SVG (например, сетку, направляющие).
        save_pdf (bool): Флаг, указывающий, нужно ли сохранять PDF на диск.
        draw_debug_grid (bool): Включает отображение вспомогательной сетки (для отладки).
    
    Возвращает:
        dict: Словарь с результатом выполнения (например,
              {"status": "OK", "path": "/path/to/file.pdf"}
              или {"status": "error", "message": "..."}).

    Примечание:
        Использует multiprocessing для изоляции и предотвращения ошибок,
        связанных с рендерингом PDF через CairoSVG.
    """
    queue = Queue()
    process = Process(
        target=generate_pdf,
        args=(svg_path, pdf_path, values, disable_svg_debug, save_pdf, draw_debug_grid, queue),
    )
    process.start()
    process.join()
    # logger.debug(f"Процесс завершился с кодом: {process.exitcode}")
    return queue.get()


@app.route("/", methods=["GET"])
def index():
    """Отдаёт HTML-форму для ввода данных."""
    # Для отладки, чтобы точно видеть, что этот код выполняется
    print(">>> index() called, rendering form.html")
    return render_template("form.html")


@app.route("/generate", methods=["POST"])
def generate_pdf_route():
    """Маршрут, принимающий данные формы и возвращающий PDF-файл."""
    try:
        # Проверка токена
        auth_header = request.headers.get("Authorization")
        if not auth_header or auth_header != f"Bearer {SECRET_TOKEN}":
            return jsonify({"error": "Unauthorized"}), 401

        # Получаем все поля из формы
        form_data = request.form.to_dict()
        filename = form_data.get("filename") or DEFAULT_FILENAME

        # Обработка checkbox-полей
        for field in checkbox_fields:
            if field in form_data:
                # Если в форме значение 'on', меняем на True
                form_data[field] = form_data[field] == "on"
            else:
                # Если чекбокс не передан — устанавливаем False
                form_data[field] = False

        # logger.debug(form_data)

        today = datetime.now().strftime("%Y-%m-%d")
        save_dir = os.path.join(BASE_DIR, "static", "downloads", today)
        os.makedirs(save_dir, exist_ok=True)

        # Уникальное имя файла
        current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        pdf_path = os.path.join(save_dir, f"{filename}_{current_time}.pdf")



        # Генерация
        generate_pdf_safe(
            svg_path=None,
            pdf_path=pdf_path,
            values=form_data,
            disable_svg_debug=True,
            save_pdf=True,
            draw_debug_grid=False,
        )

        # Проверка существования файла
        if not os.path.exists(pdf_path):
            logger.error(f"Файл PDF не найден: {pdf_path}")
            return jsonify({"error": "Файл не найден"}), 500

        # logger.debug(f"pdf_path = {pdf_path}")

        # Отдаём файл
        return send_file(
            pdf_path,
            as_attachment=True,
            download_name=f"{filename}.pdf",
            mimetype="application/pdf",
        )

    except Exception as e:  # noqa: BLE001
        logger.exception("Ошибка при генерации PDF:")
        return jsonify({"error": str(e), "type": type(e).__name__}), 500
