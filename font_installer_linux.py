import os
import shutil
import subprocess
from configs.config import ASSETS_DIR

def is_font_installed(font_name):
    """Проверить, установлен ли шрифт font_name через fc-list."""
    try:
        result = subprocess.run(["fc-list", ":family"], capture_output=True, text=True, check=True)
        fonts = result.stdout.lower()
        return font_name.lower() in fonts
    except Exception as e:
        print(f"Ошибка проверки шрифтов: {e}")
        return False

def install_font_from_project(font_filename, font_name):
    """Установить шрифт из проекта, если он не установлен."""
    if is_font_installed(font_name):
        print(f"Шрифт '{font_name}' уже установлен.")
        return True

    print(f"Шрифт '{font_name}' не найден, начинаем установку...")

    project_dir = os.path.dirname(os.path.abspath(__file__))
    font_path = os.path.join(project_dir, ASSETS_DIR, font_filename)

    if not os.path.isfile(font_path):
        print(f"Файл шрифта '{font_filename}' не найден в проекте.")
        return False

    user_fonts_dir = os.path.expanduser("~/.local/share/fonts")
    os.makedirs(user_fonts_dir, exist_ok=True)

    dest_path = os.path.join(user_fonts_dir, font_filename)
    try:
        shutil.copy(font_path, dest_path)
        print(f"Скопирован файл шрифта в {dest_path}")
    except Exception as e:
        print(f"Ошибка копирования файла шрифта: {e}")
        return False

    try:
        subprocess.run(["fc-cache", "-f", "-v"], check=True)
        print("Кэш шрифтов обновлен.")
    except subprocess.CalledProcessError as e:
        print(f"Ошибка обновления кэша шрифтов: {e}")
        return False

    # Проверим установку еще раз
    if is_font_installed(font_name):
        print(f"Шрифт '{font_name}' успешно установлен и готов к использованию.")
        return True
    else:
        print(f"Шрифт '{font_name}' не найден после установки.")
        return False


if __name__ == "__main__":
    # Укажите имя файла шрифта и системное имя шрифта
    font_file = "GOST_A.TTF"
    font_name = "GOST type A"  # Имя шрифта для fc-list и Tkinter

    install_font_from_project(font_file, font_name)
