# config.py
# Конфигурационные значения для приложения

import sys

#Режим отладки
# Определение, запущено ли как .exe
IS_EXE = getattr(sys, 'frozen', False)

# Режим отладки (True для .py, False для .exe)
DEBUG = not IS_EXE

# Сохранять PDF в режиме отлaдки
SAVE_AS_PDF = True

# Сохранять в обход формы ввода данных, используются значения по умолчанию
SAVE_WITHOUT_GUI = False

# Настройки логирования
LOG_FILE = "logs/app.log"
LOG_LEVEL = 10 if DEBUG else 20 # будут отображаться только те сообщения, которые равны или выше этого уровня.
# logging.debug("Отладочная информация")        10
# logging.info("Операция выполнена успешно")    20
# logging.warning("Это предупреждение")         30
# logging.error("Произошла ошибка")             40
# logging.critical("Критическая ошибка")        50

# Папка для сохранения данных
SAVE_FOLDER = "output" if DEBUG else ""


#Состояние
# Название прграммы
NAME_PRORAMM = "Чертежи на каркасы"

# Размер окна прорграммы
SIZE_WINDOW = "700x500"

# Имя файла по умолчанию
DEFAULT_FILENAME = "drawing"

# Директория для хранения ресурсов, например, иконок
ASSETS_DIR = "assets"

# Переменные нужные для расчёт, но не отображаются

bottom_thickness_mm = 1 # Толщина донышка, мм
# bottom_length_mm = 18 # Высота донышка,мм
overlap_lock = 24 # Нахлёст соединения
lock_length_mm = 52 # Расстояние замка коготь от кольца до кончика
support_lock_ring = 60  # Расстояние кольца замка до кольца усиления
NECK_RING_DIFF_DEFAULT = 20 # Насколько диаметр горловины больше диаметра кольца
venturi_height_mm = 175 # Высота Вентури, мм 
venturi_diameter_1_mm = 88 # Диаметр Вентури у фланца, мм
venturi_diameter_2_mm = 90 # Диаметр Вентури с обратной стороны, мм


# Материалы и их плотности, кг/м3
material_density = {
    "09Г2С": 7850,
    "Св-08А": 7860,
    "12Х18Н9": 7950,
    "12Х18Н10Т": 7900,
    "08Х18Н10": 7900,
}


# Переменные для рамки чертежа A3
DEFAULT_PART_NUMBER = "Aspex" # Обозначение -0 -11
DEFAULT_DESIGNER = "" # Разраб. -1
DEFAULT_SCRUTINEER = "" # Пров. -2
DEFAULT_SUPERVISOR = "" # Т.контр. -4
DEFAULT_DOCUMENT_CONTROLLER = "" # Н.контр. -5
DEFAULT_CONFIRMER = "" # Утв. -6 
DEFAULT_LETTER_CODE_LEFT = "" # Литера слева У -7
DEFAULT_LETTER_CODE_CENTR = "" # Литера по центру О -3
DEFAULT_CURRENT_SHEETS = "1" #Текущий лист -8
DEFAULT_WEIGHT = "2.09" # Масса -9
DEFAULT_SCALE = "1:2.5" # Масштаб -38
DEFAULT_ALL_SHEETS = "1" # Листов -39
DEFAULT_COMPONENT_IDENTIFICATION = "Каркас" # Намименование -40
DEFAULT_MATERIAL = "09Г2С" # Материал -41 09Г2С ГОСТ 10884-94


# Паременные для чертежа модели
DEFAULT_FRAME_PARTS_COUNT = "1"  # Кол-во частей каркаса, шт.
DEFAULT_FRAME_LENGTH_MM = "3000"  # Длина каркаса, мм
DEFAULT_FRAME_DIAMETER_MM = "110"  # Диаметр каркаса, мм
DEFAULT_LONGITUDINAL_ROD_DIAMETER_MM = "3"  # Диаметр продольного прутка, мм
DEFAULT_ROD_COUNT = "6"  # Кол-во прутков, шт.
DEFAULT_RING_WIRE_DIAMETER_MM = "4"  # Диаметр проволоки кольца, мм
DEFAULT_BOTTOM_PRESENCE = "да"  # Наличие донышка (да/нет)
DEFAULT_BOTTOM_THICKNESS_MM = "1"  # Толщина донышка, мм
DEFAULT_BOTTOM_LENGTH_MM = "18"  # Высота донышка, мм
DEFAULT_VENTURI_PRESENCE = "нет"  # Наличие Вентури (да/нет)
DEFAULT_VENTURI_DIAMETER_MM = "134"  # Диаметр Вентури, мм (значение по умолчанию — нужно уточнить диапазон)
DEFAULT_VENTURI_THICKNESS_MM = "1"  # Толщина Вентури, мм
DEFAULT_WIRE_MATERIAL = DEFAULT_MATERIAL  # Материал проволоки
DEFAULT_LOCK_TYPE = "Без замка"  # Тип замка
DEFAULT_COATING_TYPE = "Без окраски"  # Тип покрытия
DEFAULT_HEAD_TYPE = "Раструб" # Тип оголовка
DEFAULT_BOTTOM_DIAMETER = int(DEFAULT_FRAME_DIAMETER_MM) - 4 # Диаметр донышка
DEFAULT_BOTTOM_DIAMETER_PRESENCE = "да" # Наличие размера донышка
DEFAULT_NECK_LENGTH = "230" # Длина оголовка
DEFAULT_NECK_LENGTH_PRESENCE = "да"
DEFAULT_DISTANCE_BETWEEN_RINGS = "207" # Расстояние между кольцами
DEFAULT_DISTANCE_BETWEEN_RINGS_PRESENCE = "нет" 
DEFAULT_LAST_RING_TO_BOTTOM_LENGTH = "79"
DEFAULT_LAST_RING_TO_BOTTOM_LENGTH_PRESENCE = "нет"


# Словари для формирования формы ввода данных - key: (label_text, default_value)

# Основная надпись
DEFAULT_VALUES_TITLE_BLOCK = {
    # "part_number": ("Обозначение:", DEFAULT_PART_NUMBER),
    "component_identification": ("Наименование:", DEFAULT_COMPONENT_IDENTIFICATION),
    "designer": ("Разработал:", DEFAULT_DESIGNER),
    "scrutineer": ("Проверил:", DEFAULT_SCRUTINEER),
    "supervisor": ("Тех. контр:", DEFAULT_SUPERVISOR),
    "document_controller": ("Норм. контр:", DEFAULT_DOCUMENT_CONTROLLER),
    "confirmer": ("Утвердил:", DEFAULT_CONFIRMER),
    # "letter_code_left": ("Литера слева:", DEFAULT_LETTER_CODE_LEFT),
    # "letter_code_centr": ("Литера по центру:", DEFAULT_LETTER_CODE_CENTR),
    # "current_sheets": ("Текущий лист:", DEFAULT_CURRENT_SHEETS),
    # "all_sheets": ("Листов:", DEFAULT_ALL_SHEETS),
    # "weight": ("Масса:", DEFAULT_WEIGHT),
    # "scale": ("Масштаб:", DEFAULT_SCALE),
    # "material": ("Материал:", DEFAULT_MATERIAL),
}

# Технические данные для рассчёта каркаса и рисования чертежа
DEFAULT_VALUES_DRAWING = {
    "frame_parts_count": ("Кол-во частей каркаса, шт.", DEFAULT_FRAME_PARTS_COUNT),
    "frame_length_mm": ("Длина каркаса, мм", DEFAULT_FRAME_LENGTH_MM),
    "frame_diameter_mm": ("Диаметр каркаса, мм", DEFAULT_FRAME_DIAMETER_MM),
    "longitudinal_rod_diameter_mm": ("Диаметр продольного прутка, мм", DEFAULT_LONGITUDINAL_ROD_DIAMETER_MM),
    "rod_count": ("Кол-во прутков, шт.", DEFAULT_ROD_COUNT),
    "ring_wire_diameter_mm": ("Диаметр проволоки кольца, мм", DEFAULT_RING_WIRE_DIAMETER_MM),
    "lock_type": ("Тип замка", DEFAULT_LOCK_TYPE),
    "coating_type": ("Тип покрытия", DEFAULT_COATING_TYPE), 
    "head_type": ("Тип оголовка", DEFAULT_HEAD_TYPE),  
    "wire_material": ("Материал проволоки", DEFAULT_WIRE_MATERIAL),
    "venturi_presence": ("Наличие Вентури (да/нет)", DEFAULT_VENTURI_PRESENCE),
    "venturi_diameter_mm": ("Диаметр Вентури, мм", DEFAULT_VENTURI_DIAMETER_MM),
    "venturi_thickness_mm": ("Толщина Вентури, мм", DEFAULT_VENTURI_THICKNESS_MM),
    "wire_material": ("Материал проволоки", DEFAULT_WIRE_MATERIAL),

    "bottom_presence": ("Наличие донышка (да/нет)", DEFAULT_BOTTOM_PRESENCE),
    "bottom_thickness_mm": ("Толщина донышка, мм", DEFAULT_BOTTOM_THICKNESS_MM),

    "bottom_length_mm": ("Высота донышка, мм", DEFAULT_BOTTOM_LENGTH_MM),

    # "bottom_diameter_presence": ("Наличие размера донышка", DEFAULT_BOTTOM_DIAMETER_PRESENCE),
    # "bottom_diameter": ("Диаметр донышка, мм", DEFAULT_BOTTOM_DIAMETER, True),
    
    "neck_ring_inner_diameter_presence": ("Внутр. диам. кольца раструба", "нет"),

    "neck_length_presence": ("Наличие размера оголовка", DEFAULT_NECK_LENGTH_PRESENCE),
    "neck_length": ("Длина оголовка, мм <1>", DEFAULT_NECK_LENGTH, True),

    "distance_between_rings": ("Шаг между кольцами, мм <3>", DEFAULT_DISTANCE_BETWEEN_RINGS),

    "last_ring_to_bottom_length_presence": ("Наличие размера до донышка", DEFAULT_LAST_RING_TO_BOTTOM_LENGTH_PRESENCE ),
    "last_ring_to_bottom_length": ("Расстояние до донышка, мм <2>", DEFAULT_LAST_RING_TO_BOTTOM_LENGTH, True), 
    
    "calc_segment_count_presence": ("", "нет"),
    "calc_segment_count": ("Кол-во шагов, шт. <4>", ""),
    "calc_frame_length": ("Проверка длины каркаса", "", True),
    
}

# Имя файла
DEFAULT_VALUES_FILENAME = {
    "filename": ("Имя файла:", DEFAULT_FILENAME)
}

ALL_BLOCKS = {
    **DEFAULT_VALUES_TITLE_BLOCK,
    **DEFAULT_VALUES_DRAWING,
    **DEFAULT_VALUES_FILENAME,
}

# --- Группы полей ---
FORM_SECTIONS = { 
    "Технические данные": DEFAULT_VALUES_DRAWING,
    "Основная надпись": DEFAULT_VALUES_TITLE_BLOCK,
    "Имя файла": DEFAULT_VALUES_FILENAME
}


# Определяем, какие поля требуют выпадающего списка
dropdown_fields = {
    "frame_parts_count": ["1", "2", "3"],
    "rod_count": ["6", "8", "10", "12", "14", "16", "18", "20", "22", "24"],
    "coating_type": ["Без окраски","Окраска", "Оцинковка"],
    "lock_type": ["Без замка", "Коготь"],
    "wire_material": list(material_density.keys()),
    "head_type": ["Раструб", "Воротник"]
}


# Определяем, какие поля требуют галочки
checkbox_fields = {
    "bottom_presence": "да",
    "venturi_presence": "да",
    "neck_ring_inner_diameter_presence": "да",
    # "bottom_diameter_presence": "да",
    "neck_length_presence": "да",
    "last_ring_to_bottom_length_presence": "да",
    "calc_segment_count_presence": "да"
}


# Определяем, какие поля требуют проверки числового ввода
numeric_fields = [
    "frame_length_mm", "frame_diameter_mm", "longitudinal_rod_diameter_mm",
    "ring_wire_diameter_mm", "bottom_thickness_mm",
    "venturi_diameter_mm", "venturi_thickness_mm",
    "neck_length", "distance_between_rings",
    "last_ring_to_bottom_length", "bottom_length_mm",
    "calc_segment_count", "calc_frame_length"
]

# Определяем какие поля буду только в левой части
left_only_fields = [
    "venturi_presence", 
    "bottom_presence",
    "neck_ring_inner_diameter_presence",
]


# Ключ — имя поля, значение — имя чекбокса, который влияет на его активность
linked_checkboxes = {
    # "bottom_diameter": "bottom_diameter_presence", # погасил потому что не нужно поле ввода
    "neck_length": "neck_length_presence",
    "last_ring_to_bottom_length": "last_ring_to_bottom_length_presence",
    "calc_segment_count": "calc_segment_count_presence"

}

# Переменные для таблицы чертежа (порядок важен)
spec_table = [
    "frame_parts_count",
    "frame_length_mm",
    "frame_diameter_mm",
    "longitudinal_rod_diameter_mm",
    "rod_count",
    "ring_wire_diameter_mm",
    "bottom_presence",
    "venturi_presence",
    "lock_type",
    "coating_type",
    "material"
]




# Определяем подсказки для групп полей
group_tooltips = {
    "Основная надпись": 
"""Данные, которые будут отображены в основной надписи на чертеже. 
Заполните фамилии ответственных участников.""",

    "Технические данные": 
"""Основные параметры каркаса. Заполняются обязательно.
Эти значения влияют на чертёж и расчёты. """,

    "Справочные данные": 
"""Необязательные параметры. Используются только для информации 
и не отображаются на чертеже, если оставить пустыми.""",

    "Имя файла": 
"""Имя файла, в котором будет сохранён чертёж. 
Без расширения. Можно оставить по умолчанию."""
}


# Определяем подсказки для каждого поля
field_tooltips = {
    "frame_parts_count": "Односоставной, двусоставной, трехсоставной", # \nВременно доступно только 'Односоставной' \nРеализуется в дальнейшем",
    "frame_length_mm": "Общая длина каркаса",
    "frame_diameter_mm": "Наружный диаметр каркаса",
    "longitudinal_rod_diameter_mm": "Диаметр продольного прутка",
    "rod_count": "Кол-во продольных прутков в каркасе",
    "ring_wire_diameter_mm": "Диаметр поперечного прутка - кольца",
    "bottom_presence": "Наличие донышка в нижней части каркаса",
    "bottom_thickness_mm": "Толщина материала донышка",
    "venturi_presence": "Наличие сопла Вентури в верхней части каркаса", # \nВременно недоступно \nРеализуется в дальнейшем",
    "venturi_diameter_mm": "Наружный диаметр сопла Вентури",
    "venturi_thickness_mm": "Толщина материала сопла Вентури",
    "wire_material": "Марка стали каркаса",
    "lock_type": "Наличие и тип сочленения составных частей каркаса", # \nВременно доступно только 'Без замка' \nРеализуется в дальнейшем",
    "coating_type": "Наличие и тип дополнительного покрытия каркаса",
    "bottom_length_mm": "Высота боковой стенки донышка",
    "neck_ring_inner_diameter_presence": "Внутренний диаметр кольца раструба каркаса",
    "neck_length": "Расстояние от первого кольца до оголовка",
    "neck_length_presence": "Наличие размера на оголовке",
    "head_type": "Тип оголовка каркаса", # \nВременно доступно только 'Раструб' \nРеализуется в дальнейшем",
    "distance_between_rings": "Расстояние между кольцами каркаса, одинаковое по всей длине каркаса",

    "last_ring_to_bottom_length": "Расстояние от последнего кольца до донышка \nДолжен быть больше высоты донышка",
    "last_ring_to_bottom_length_presence": "Наличие размера расстояния от последнего кольца до донышка",

    "bottom_diameter": "Наружный диаметр донышка", 

    "bottom_diameter": "Наружный диаметр донышка",
    # 'bottom_diameter_presence': "Наличие размера на донышке",

    "calc_segment_count_presence": "Округление в большую или меньшую сторону",
    "calc_frame_length": "Рассчётное значение длины каркаса для проверки \n<1>+<2>+<3>*<4> \nСкорректируйте значения <1>, <2>, <3> или <4>",

    "calc_segment_count": "Рассчётное количество шагов",

    "rings_calculation_explanation": "Пояснение рассчёта количества шагов \nДробное значение округлется до целого в большую или меньшую сторону",


    # "part_number": ("Обозначение:", DEFAULT_PART_NUMBER),
    "component_identification": "Название детали",
    "designer": "Разработчик",
    "scrutineer": "Проверяющий",
    "supervisor": "Технологический контролёр",
    "document_controller": "Нормоконтролёр",
    "confirmer": "Утверждающий",
    # "letter_code_left": ("Литера слева:", DEFAULT_LETTER_CODE_LEFT),
    # "letter_code_centr": ("Литера по центру:", DEFAULT_LETTER_CODE_CENTR),
    # "current_sheets": ("Текущий лист:", DEFAULT_CURRENT_SHEETS),
    # "all_sheets": ("Листов:", DEFAULT_ALL_SHEETS),
    # "weight": ("Масса:", DEFAULT_WEIGHT),
    # "scale": ("Масштаб:", DEFAULT_SCALE),


    "filename": "Имя файла (без расширения)",
}


