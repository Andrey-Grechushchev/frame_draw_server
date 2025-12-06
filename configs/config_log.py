# config_log.py

import logging
from configs.config import LOG_FILE, DEBUG, LOG_LEVEL

# Создаем (или получаем) логгер с общим именем
logger = logging.getLogger("app_logger")
logger.setLevel(LOG_LEVEL)

# Удалим все старые обработчики (если они есть)
if logger.hasHandlers():
    logger.handlers.clear()

# Настройка форматирования
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

# Вывод в консоль
console_handler = logging.StreamHandler()
console_handler.setLevel(LOG_LEVEL)
console_handler.setFormatter(formatter)

if DEBUG:
    # Запись в файл
    file_handler = logging.FileHandler(LOG_FILE, mode="a", encoding="utf-8")
    file_handler.setLevel(LOG_LEVEL)
    file_handler.setFormatter(formatter)

    # Назначение обработчиков
    logger.addHandler(file_handler)

logger.addHandler(console_handler)

# logging.debug("Отладочная информация")        10
# logging.info("Операция выполнена успешно")    20
# logging.warning("Это предупреждение")         30
# logging.error("Произошла ошибка")             40
# logging.critical("Критическая ошибка")        50
