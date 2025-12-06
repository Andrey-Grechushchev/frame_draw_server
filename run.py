# run.py

from app.server import app
from flask import jsonify
from werkzeug.exceptions import HTTPException
from configs.config_log import logger

# === Глобальный обработчик ошибок ===
@app.errorhandler(Exception)
def handle_exception(e):
    # Если это "нормальная" HTTP-ошибка (404, 405 и т.п.) — отдать её как есть
    if isinstance(e, HTTPException):
        return e

    # А всё остальное логируем как реально неожиданные ошибки
    logger.exception("Unhandled exception:")
    response = {
        "error": str(e),
        "type": type(e).__name__,
    }
    return jsonify(response), 500


# === Точка входа ===
if __name__ == "__main__":
    logger.info("Starting Flask server...")
    # debug=True удобно для разработки; для продакшена выставить debug=False
    app.run(host="0.0.0.0", port=5000, debug=True)
