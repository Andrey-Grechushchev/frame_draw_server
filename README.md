# Генерация чертежа в PDF

Простое приложение на Python с GUI (Tkinter) для генерации чертежей в SVG и преобразования в PDF.

## Зависимости

### Зависимости для Linux сервера:

- Python 3.11.9
- python-dotenv==1.1.0
- Flask==3.1.1
- flask-cors==6.0.0
- CairoSVG==2.7.1
- svgwrite==1.4.3
- pyinstaller==6.13.0
- numpy==2.2.5

### Зависимости для разработки с GUI:

- pillow==11.1.0
- pywin32-ctypes==0.2.3

## Установка зависимостей

### Установка зависимостей для Linux сервера:

```
pip install -r requirements-server.txt
```

### Установка зависимостей для разработки с GUI:

```
pip install -r requirements-dev.txt
```

## Установка шрифта для Linux сервера:
модуль для автоматической установки кастомных шрифтов из проекта в пользовательскую папку шрифтов Linux с обновлением кэша.
```
python font_installer_linux.py
```

## Запуск для разработки c GUI:

```
python main.py 
```

## Запуск сервера Flask:

```
python run.py
```

## Запуск встроенного в Python HTTP-сервер

```
cd templates; python -m http.server 8000
```

## Сборка .exe

```
python build.py           -> demo
python build.py demo      -> demo
python build.py release   -> release
```

## Дерево файлов 

```
tree /F /A > tree.txt
```


```
python -m PyInstaller --onefile --clean --windowed --noconsole --icon="assets/icon.ico" --add-data "assets/icon.ico;assets" --add-data "assets/GOST_A.TTF;assets" --add-binary "assets/libcairo-2.dll;." --name "Чертежи на каркасы" main.py 
```

venv\Scripts\activate



python3 -m venv venv
source venv/bin/activate
pip install -r requirements-server.txt


cd /home/aspex/frame_draw_server
source venv/bin/activate

curl -v http://127.0.0.1:5000/ # проверка работы сервера Flask
ss -tulpn | grep 5000 # открыт ли порт

Теперь, когда sudo работает, твой стандартный цикл такой:
Локально (Windows):
git add .
git commit -m "Описание изменений"
git push
На сервере под aspex:
ssh aspex@31.207.75.93
cd /home/aspex/frame_draw_server
git pull
# если менялся requirements-server.txt:
source venv/bin/activate
pip install -r requirements-server.txt
sudo systemctl restart frame_draw_server.service
sudo systemctl status frame_draw_server.service

Проверка:
на сервере: curl -i http://127.0.0.1:5000/
из браузера: http://31.207.75.93:5000/
Если хочешь, дальше можем сделать небольшой deploy.sh, чтобы на сервере всё свелось к одной команде типа ./deploy.sh.
