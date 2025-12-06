# main.py
from trial_guard import *  # noqa: F401

from configs.config_log import logger
from gui_app import create_gui


if __name__ == "__main__":
    try:
        logger.info("Запуск приложения...")
        create_gui()
    except Exception as e:
        logger.error(f"Ошибка при запуске приложения: {e}")
