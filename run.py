# run.py

import os
import sys

# Гарантируем, что корень проекта есть в sys.path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from flask import jsonify
from werkzeug.exceptions import HTTPException
from configs.config_log import logger
from app.server import app


# === Глобальный обработчик ошибок ===
@app.errorhandler(Exception)
def handle_exception(e):
    """
    Логируем все неожиданные исключения.
    HTTP-исключения (404, 405 и т.п.) отдаём как есть.
    """
    if isinstance(e, HTTPException):
        return e

    logger.exception("Unhandled exception:")
    response = {
        "error": str(e),
        "type": type(e).__name__,
    }
    return jsonify(response), 500


# === Точка входа ===
if __name__ == "__main__":
    logger.info("Starting Flask server...")
    # Для отладки можно посмотреть версию Python
    print(sys.version)
    app.run(host="0.0.0.0", port=5000, debug=False)

