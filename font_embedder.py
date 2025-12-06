# UTC+5 2025-05-18
# Расширенный класс подключения шрифта в SVG

import base64
import sys
from pathlib import Path
from configs.config_log import logger
from utils.utils_core import resource_path
from configs.config import ASSETS_DIR

print(sys.version)

def add_fonts(dwg):
    # Подключаем шрифт (автоматически встраивает в .exe, а при отладке — ссылкой)
    font_embedder = FontEmbedder(
        relative_font_path=f"{ASSETS_DIR}/GOST_A.TTF",
        font_family="GOST type A",
        mode="embed"
    )

    # Добавляем в defs
    dwg.defs.add(dwg.style(font_embedder.get_css()))


class FontEmbedder:
    def __init__(self, relative_font_path, font_family="CustomFont", mode="auto"):
        """
        relative_font_path — путь к шрифту относительно проекта или assets
        font_family — имя, которым шрифт будет доступен в SVG
        mode: 'auto' (по умолчанию), 'embed' (встраивать), 'link' (подключать)
        """
        self.font_family = font_family
        self.font_path = resource_path(relative_font_path)
        self.mode = self._resolve_mode(mode)

    def _resolve_mode(self, mode):
        if mode == "auto":
            # Если работаем из .exe (есть _MEIPASS), встраиваем
            return "embed" if hasattr(sys, '_MEIPASS') else "link"
        return mode

    def get_css(self):
        """Генерирует CSS код подключения шрифта"""
        if self.mode == "embed":
            return self._get_embedded_font_css()
        else:
            return self._get_linked_font_css()

    def _get_embedded_font_css(self):
        font_bytes = Path(self.font_path).read_bytes()
        b64_str = base64.b64encode(font_bytes).decode("utf-8")

        mime = self._detect_mime(self.font_path)
        return f"""
        @font-face {{
            font-family: "{self.font_family}";
            src: url("data:{mime};base64,{b64_str}") format("truetype");
        }}
        """

    def _get_linked_font_css(self):
        rel_path = Path(self.font_path).name  # Только имя файла (относительно SVG)
        return f"""
        @font-face {{
            font-family: "{self.font_family}";
            src: url("{rel_path}");
        }}
        """

    @staticmethod
    def _detect_mime(path):
        ext = Path(path).suffix.lower()
        return {
            '.ttf': 'font/ttf',
            '.otf': 'font/otf',
            '.woff': 'font/woff',
            '.woff2': 'font/woff2',
        }.get(ext, 'application/octet-stream')
