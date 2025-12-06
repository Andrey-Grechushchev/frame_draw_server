# run.py

from app.server import app
from flask import jsonify
from configs.config_log import logger

# === Глобальный обработчик ошибок ===
@app.errorhandler(Exception)
def handle_exception(e):
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
