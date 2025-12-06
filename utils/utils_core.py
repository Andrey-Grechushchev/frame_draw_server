# utils_core.py         
# Общие функции, без GUI

import sys
import webbrowser
from pathlib import Path
from math import pi

import tempfile
import threading
import time
import os
from configs.config_log import logger


def resource_path(relative_path):
    """Возвращает абсолютный путь к ресурсу, работает как в .py, так и в .exe"""

    if hasattr(sys, '_MEIPASS'):
        # Если запущено из .exe (PyInstaller), используем временную папку _MEIPASS
        base_path = Path(sys._MEIPASS)
    else:
        # Иначе используем папку с главным исполняемым скриптом
        try:
            base_path = Path(sys.modules['__main__'].__file__).resolve().parent
        except AttributeError:
            # Если __main__.__file__ не доступен, fallback на текущий файл
            base_path = Path(__file__).resolve().parent
      
    # base_path = getattr(sys, '_MEIPASS', Path(__file__).parent)

    full_path = str(Path(base_path) / relative_path)
    
    # logger.info(f"full_path = {full_path}")
    return full_path


def open_svg_in_browser_and_cleanup(svg_data: str, disable_svg_debug: bool):
    """
    Если отладка SVG разрешена (disable_svg_debug=False), сохраняет SVG во временный файл,
    открывает его в Edge и удаляет через несколько секунд.
    
    :param svg_data: Строка SVG-контента (dwg.tostring()).
    :param disable_svg_debug: Флаг отключения отладочного вывода.
    """
    if disable_svg_debug:
        logger.info("SVG отладка отключена — просмотр не будет выполнен.")
        return

    try:
        # Создаём временный файл
        with tempfile.NamedTemporaryFile(delete=False, suffix=".svg", mode="w", encoding="utf-8") as tmp:
            tmp.write(svg_data)
            tmp_path = tmp.name

        logger.info(f"Временный SVG сохранён: {tmp_path}")

        # Открываем SVG в Edge
        edge_path = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
        webbrowser.register('edge', None, webbrowser.BackgroundBrowser(edge_path))
        webbrowser.get("edge").open(f"file://{tmp_path}")
        logger.info("SVG открыт в браузере Microsoft Edge")

        # Запускаем фоновую задачу на удаление файла
        def delayed_cleanup(path):
            time.sleep(5)  # можно увеличить, если нужно
            try:
                os.remove(path)
                logger.info(f"Временный SVG удалён: {path}")
            except Exception as e:
                logger.warning(f"Не удалось удалить временный SVG: {e}")

        threading.Thread(target=delayed_cleanup, args=(tmp_path,), daemon=True).start()

    except Exception as e:
        logger.warning(f"Ошибка при открытии SVG в браузере: {e}")

def save_svg_if_enabled(dwg, disable_svg_debug, svg_path):
    """Сохраняет SVG-файл, если включено в настройках."""
    if not disable_svg_debug:
        logger.info(f"Попытка сохранить SVG в: {svg_path}")
        try:
            dwg.saveas(svg_path)
            logger.info(f"SVG файл сохранён как: {svg_path}")

            # Открываем SVG в Edge
            # Регистрируем Edge как браузер         
            webbrowser.register('edge', None, webbrowser.BackgroundBrowser("C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"))
            # Открываем SVG в Edge  
            webbrowser.get("edge").open(f"file://{svg_path}")

        except Exception as svg_debug_err:
            logger.warning(f"Не удалось сохранить SVG отладочный файл: {svg_debug_err}") 


def mm_to_pt(num):
    """Переводит мм в pt (points)"""
    return num*96/25.4


def pt_to_mm(num):
    """Переводит pt (points) в мм"""
    return num/96*25.4


def mm3_to_m3(value_mm3: float) -> float:
    """Converts cubic millimeters to cubic meters."""
    return value_mm3 * 1e-9


def vol_cylinder(length, diameter):
    """
    Вычисляет объём цилиндра по длине и диаметру.

    Параметры:
        length (float): Высота или длина цилиндра.
        diameter (float): Диаметр основания цилиндра.

    Возвращает:
        float: Объём цилиндра.
    """
    return pi * length * (diameter / 2) ** 2


def circle_length(diameter):
    """
    Вычисляет длину окружности по её диаметру.

    Параметры:
        diameter (float): Диаметр окружности.

    Возвращает:
        float: Длина окружности.
    """
    return pi * diameter


