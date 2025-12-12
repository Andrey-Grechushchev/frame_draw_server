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
import ipaddress

load_dotenv()

# Корень проекта (на уровень выше app/)
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# Говорим Flask, где лежат templates/
app = Flask(__name__, template_folder=os.path.join(BASE_DIR, "templates"))
CORS(app)

# Конфигурация

SECRET_TOKEN = os.getenv("SECRET_TOKEN", "")


# Белый список IP, которым разрешён доступ к сервису.
# Формат переменной окружения ALLOWED_IPS:
# "127.0.0.1,31.207.75.93,10.0.0.0/24"
ALLOWED_IPS_RAW = os.getenv("ALLOWED_IPS", "").strip()
ALLOWED_NETWORKS = []

if ALLOWED_IPS_RAW:
    # Явный режим "всех пускаем"
    if ALLOWED_IPS_RAW == "*":
        ALLOW_ALL_IPS = True
        logger.info("IP-фильтрация отключена: ALLOWED_IPS='*' — разрешены все IP.")
    else:
        for part in ALLOWED_IPS_RAW.split(","):
            part = part.strip()
            if not part:
                continue
            try:
                # Если в записи есть "/", считаем это подсетью (CIDR),
                # иначе интерпретируем как одиночный адрес /32
                if "/" in part:
                    net = ipaddress.ip_network(part, strict=False)
                else:
                    net = ipaddress.ip_network(part + "/32", strict=False)
                ALLOWED_NETWORKS.append(net)
            except ValueError:
                logger.error(f"Некорректная запись в ALLOWED_IPS: {part}")


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


def get_client_ip() -> str:
    """
    Определяет IP клиента.
    Если сервис будет стоять за reverse-proxy (Nginx/Apache),
    можно использовать заголовок X-Forwarded-For.
    Сейчас берём первый IP из X-Forwarded-For (если есть),
    иначе стандартный request.remote_addr.
    """
    forwarded_for = request.headers.get("X-Forwarded-For", "")
    if forwarded_for:
        # формат: "ip1, ip2, ip3" -> берём первый
        ip = forwarded_for.split(",")[0].strip()
        return ip

    return request.remote_addr or "0.0.0.0"


def is_ip_allowed(ip: str) -> bool:
    """
    Проверяет, разрешён ли IP.

    Логика:
    - Если ALLOW_ALL_IPS=True  -> всегда True (проверка отключена явно через "*").
    - Если ALLOWED_NETWORKS пуст -> считаем, что ограничений нет (поведение по умолчанию).
    - Иначе проверяем, попадает ли IP в одну из подсетей.
    """
    if ALLOW_ALL_IPS:
        return True

    if not ALLOWED_NETWORKS:
        # Белый список не задан — пропускаем всех
        return True

    try:
        addr = ipaddress.ip_address(ip)
    except ValueError:
        # Невалидный IP — считаем, что ему доступ запрещён
        return False

    for net in ALLOWED_NETWORKS:
        if addr in net:
            return True

    return False



@app.before_request
def limit_remote_addr():
    """
    Глобальный фильтр запросов: ограничение по IP.
    Применяем только к "боевым" эндпоинтам: index и generate_pdf_route.
    Остальное (static, health-check и т.п.) не трогаем.
    """
    # request.endpoint = имя view-функции ("index", "generate_pdf_route", "static", ...)
    if request.endpoint in ("index", "generate_pdf_route"):
        client_ip = get_client_ip()
        if not is_ip_allowed(client_ip):
            logger.warning(f"Доступ запрещён для IP: {client_ip}")
            return jsonify({"error": "Forbidden: IP not allowed"}), 403



@app.route("/", methods=["GET"])
def index():
    """Отдаёт HTML-форму для ввода данных."""
    # Для отладки, чтобы точно видеть, что этот код выполняется
    print(">>> index() called, rendering form.html")
    return render_template("form.html", api_token=SECRET_TOKEN)


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
