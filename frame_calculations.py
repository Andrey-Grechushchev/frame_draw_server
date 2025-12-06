# frame_calculations.py
# UTC+5: 2025-05-11 17:35 — подключен отдельный модуль для расчёта конструкции

from math import ceil, floor
from utils.utils_core import mm3_to_m3, vol_cylinder, circle_length
from configs.config import (
DEFAULT_DISTANCE_BETWEEN_RINGS, DEFAULT_NECK_LENGTH, 
bottom_thickness_mm, NECK_RING_DIFF_DEFAULT, DEFAULT_SCALE,
venturi_height_mm, material_density, overlap_lock, lock_length_mm,
)
from configs.config_log import logger

# Не зависит от количесства частей коркаса, потому что итоговое значение влияет только на рисование и проверку длины каркаса. 
# Для рассчёта массы дополнительных колец считается отдельно
# Формула рассчёта колчества колец с округлением вверх
def calc_num_rings_ceil(frame_length_mm, neck_length, distance_between_rings, frame_parts_count):
    return ceil( (frame_length_mm - neck_length) / distance_between_rings + 1)


# Формула рассчёта колчества колец с округлением вниз
def calc_num_rings_floor(frame_length_mm, neck_length, distance_between_rings, frame_parts_count):
    return floor( (frame_length_mm - neck_length) / distance_between_rings + 1)


# Считает и добавляет количество колец
def add_count_of_rings(input_dict):
    
    distance_between_rings = float(input_dict["distance_between_rings"])
    neck_length = float(input_dict["neck_length"])
    frame_length_mm = float(input_dict["frame_length_mm"])
    frame_parts_count = float(input_dict["frame_parts_count"])
    calc_segment_count_presence = input_dict["calc_segment_count_presence"]

    # logger.info(f"Запуск рассчётов...")
    # logger.debug(f"frame_length_mm = {frame_length_mm}")
    # logger.debug(f"neck_length = {neck_length}")
    # logger.debug(f"distance_between_rings = {distance_between_rings}")
    # logger.debug(f"frame_parts_count = {frame_parts_count}")
    # logger.debug(f"last_ring_to_bottom_length = {last_ring_to_bottom_length}")
    # logger.debug(f"frame_parts_count = {frame_parts_count}")
    
    if calc_segment_count_presence:
        num_rings = calc_num_rings_ceil (frame_length_mm, neck_length, 
                                        distance_between_rings, frame_parts_count)
    else:
        num_rings = calc_num_rings_floor (frame_length_mm, neck_length, 
                                        distance_between_rings, frame_parts_count)

    count_of_rings = {"count_of_rings": str(num_rings)} # Кол-во колец, шт.
    # logger.info(f"count_of_rings = {count_of_rings['count_of_rings']}")

    return input_dict.update(count_of_rings)


# Считаем и добавляем расчётное количество колец в каждом сегменте каркаса и длины каждого сегмента
def add_calc_frame_layout(input_dict):
    """
    Расчёт распределения колец и фактической длины каждой части каркаса.

    Функция используется как «расчётное ядро», независимое от GUI.
    На вход подаётся словарь с исходными параметрами каркаса, на выходе
    в этот же словарь добавляются:
      - count_of_steps_rings_frame_1, count_of_steps_rings_frame_2, count_of_steps_rings_frame_3 —
        количество шагов колец в каждой части каркаса (от оголовка к донышку);
      - frame_length_1, frame_length_2, frame_length_3 —
        расчётная длина каждой части каркаса с учётом:
          * расстояний между кольцами;
          * длины горловины;
          * длины «замков» (lock_length_mm);
          * половины диаметра проволоки кольца (добавка по 0.5*d на край).

    Ожидаемые ключи во входном словаре input_dict:
      - "last_ring_to_bottom_length"  — расстояние от последнего кольца до донышка, мм;
      - "distance_between_rings"      — шаг между кольцами, мм;
      - "neck_length"                 — длина горловины, мм;
      - "frame_length_mm"             — общая длина каркаса, мм;
      - "frame_parts_count"           — количество частей каркаса (1, 2 или 3);
      - "ring_wire_diameter_mm"       — диаметр проволоки кольца, мм;
      - "count_of_rings"              — общее количество колец.

    Функция:
      1. Преобразует значения из словаря к числовым типам.
      2. В зависимости от количества частей каркаса распределяет кольца
         по частям (от оголовка к донышку).
      3. Для каждой части рассчитывает её фактическую длину вдоль оси каркаса.
      4. Записывает результаты обратно в input_dict в виде строк.

    Возвращает:
      - обновлённый словарь input_dict (тот же объект, который был на входе).
    """

    last_ring_to_bottom_length = float(input_dict["last_ring_to_bottom_length"])
    distance_between_rings = float(input_dict["distance_between_rings"])
    neck_length = float(input_dict["neck_length"])
    frame_length_mm = int(input_dict["frame_length_mm"])
    frame_parts_count = int(input_dict["frame_parts_count"])  # важно: int для корректной работы match
    ring_wire_diameter_mm = float(input_dict["ring_wire_diameter_mm"])
    count_of_rings = int(input_dict["count_of_rings"])
 
    # Нумерация частей каркаса: 1 — от оголовка, 2 — средняя, 3 — к донышку
    match frame_parts_count:
        case 1:
            # Весь каркас — одной частью
            count_of_steps_rings_frame_1 = count_of_rings
            count_of_steps_rings_frame_2 = 0
            count_of_steps_rings_frame_3 = 0
            frame_length_1 = frame_length_mm
            frame_length_2 = 0
            frame_length_3 = 0

        case 2:
            # Делим кольца между верхней и нижней частью,
            # одно кольцо «теряется» на стыке (замке), поэтому count_of_rings - 1
            count_of_steps_rings_frame_1 = floor((count_of_rings - 1) / 2)
            count_of_steps_rings_frame_2 = count_of_rings - 1 - int(count_of_steps_rings_frame_1)
            count_of_steps_rings_frame_3 = 0

            # Длина части 1: горловина + кольца + замок + половина диаметра проволоки
            frame_length_1 = (
                count_of_steps_rings_frame_1 * distance_between_rings
                + neck_length
                + lock_length_mm
                + ring_wire_diameter_mm / 2
            )
            # Длина части 2: кольца + донышко + замок + половина диаметра проволоки
            frame_length_2 = (
                count_of_steps_rings_frame_2 * distance_between_rings
                + last_ring_to_bottom_length
                + lock_length_mm
                + ring_wire_diameter_mm / 2
            )
            frame_length_3 = 0

        case 3:
            # Для трёх частей логика распределения такая:
            # 1) сначала считаем количество шагов во второй части,
            # 2) затем в третьей, 3) остаток — в первой.
            count_of_steps_rings_frame_2 = ceil((count_of_rings - 1) / 3)
            count_of_steps_rings_frame_3 = ceil((count_of_rings - 1 - int(count_of_steps_rings_frame_2)) / 2)
            count_of_steps_rings_frame_1 = (
                count_of_rings - 1 - int(count_of_steps_rings_frame_3) - int(count_of_steps_rings_frame_2)
            )

            # Верхняя часть: горловина + кольца + замок + половина диаметра проволоки
            frame_length_1 = (
                count_of_steps_rings_frame_1 * distance_between_rings
                + neck_length
                + lock_length_mm
                + ring_wire_diameter_mm / 2
            )
            # Средняя часть: кольца + два замка (сверху и снизу) + две половины диаметра проволоки
            frame_length_2 = (
                count_of_steps_rings_frame_2 * distance_between_rings
                + (lock_length_mm + ring_wire_diameter_mm / 2) * 2
            )
            # Нижняя часть: кольца + донышко + замок + половина диаметра проволоки
            frame_length_3 = (
                count_of_steps_rings_frame_3 * distance_between_rings
                + last_ring_to_bottom_length
                + lock_length_mm
                + ring_wire_diameter_mm / 2
            )

        case _:
            raise ValueError(f"Unsupported frame_parts_count={frame_parts_count}")

    # Сохраняем результаты обратно в словарь в текстовом виде (для GUI / HTML-форм)
    input_dict.update({"count_of_steps_rings_frame_1": str(count_of_steps_rings_frame_1)})
    input_dict.update({"count_of_steps_rings_frame_2": str(count_of_steps_rings_frame_2)})
    input_dict.update({"count_of_steps_rings_frame_3": str(count_of_steps_rings_frame_3)})
    input_dict.update({"frame_length_1": str(int(frame_length_1))})
    input_dict.update({"frame_length_2": str(int(frame_length_2))})
    input_dict.update({"frame_length_3": str(int(frame_length_3))})

    return input_dict


# Сравнивает рассчитанную длину каркаса с заданной и формирует пояснение
def calculate_frame_length_match(input_dict):
    """
    Чистый расчёт:
    Сравнивает рассчитанную длину каркаса с заданной и формирует пояснение.
    На вход — словарь с данными.
    """
    add_count_of_rings(input_dict)
    add_calc_frame_layout(input_dict)

    last_ring_to_bottom_length = float(input_dict["last_ring_to_bottom_length"])
    distance_between_rings = float(input_dict["distance_between_rings"])
    neck_length = float(input_dict["neck_length"])
    frame_length_mm = float(input_dict["frame_length_mm"])
    frame_parts_count = float(input_dict["frame_parts_count"])

    count_of_rings = int(input_dict["count_of_rings"])
    count_of_steps_rings_frame_1 = input_dict["count_of_steps_rings_frame_1"]
    count_of_steps_rings_frame_2 = input_dict["count_of_steps_rings_frame_2"]
    count_of_steps_rings_frame_3 = input_dict["count_of_steps_rings_frame_3"]
    # frame_length_1 = int(float(input_dict["frame_length_1"]))
    # frame_length_2 = int(float(input_dict["frame_length_2"]))
    # frame_length_3 = int(float(input_dict["frame_length_3"]))

    
    # logger.info(f"count_of_rings = {count_of_rings}")
    
    result = neck_length + distance_between_rings * (count_of_rings - 1) + last_ring_to_bottom_length + overlap_lock * (frame_parts_count - 1)
    check_status = False
    
    if result > frame_length_mm:
        output = f"{int(result)} > {int(frame_length_mm)}"
        bg_color = "salmon"
    elif result < frame_length_mm:
        output = f"{int(result)} < {int(frame_length_mm)}"
        bg_color = "salmon"
    else:
        output = f"{int(result)} = {int(frame_length_mm)}"
        bg_color = "lightgreen"
        check_status = True

    
    match frame_parts_count:
        case 1:
            overlap = f""
            n_step_1 = f""
            n_step_2 = f""
            n_step_3 = f""
            conjunction_1 = "" 
            conjunction_2 = ""
            conjunction_3 = ""

        case 2:
            overlap = f" - {overlap_lock}"
            n_step_1 = count_of_steps_rings_frame_1
            n_step_2 = count_of_steps_rings_frame_2
            n_step_3 = ""
            conjunction_1 = "  –> "
            conjunction_2 = " — " 
            conjunction_3 = ""

        case 3:
            overlap = f" - {(overlap_lock)}*{int(frame_parts_count - 1)}"
            n_step_2 = count_of_steps_rings_frame_2
            n_step_3 = count_of_steps_rings_frame_3
            n_step_1 = count_of_steps_rings_frame_1
            conjunction_1 = "  –> "
            conjunction_2 = " — "
            conjunction_3 = " — "

    # строчка, что будет написано в пояснении к формуле рассчёта
    rings_calculation_explanation = (
        f"({int(frame_length_mm)} - {int(neck_length)}{(overlap)}) / {int(distance_between_rings)}"
        f" = {round(((frame_length_mm - neck_length - overlap_lock * (frame_parts_count - 1)) / distance_between_rings), 1)} ≈ {count_of_rings - 1}"
        f"{conjunction_1}{n_step_1}{conjunction_2}{n_step_2}{conjunction_3}{n_step_3}"
        # f"{frame_length_1} {frame_length_2} {frame_length_3}"
    )

    return output, bg_color, count_of_rings, rings_calculation_explanation, check_status


# Принцип наименования обозначения изделия
def add_generated_part_number(input_dict):
    part_number_generated = {
        "part_number": (
            f"AFK-"
            f"{input_dict['frame_length_mm']}-"
            f"{str(int(input_dict['frame_parts_count'])-1)}-"
            f"{input_dict['frame_diameter_mm']}-"
            f"{input_dict['longitudinal_rod_diameter_mm']}-"
            f"{input_dict['rod_count']}-"
            f"{input_dict['ring_wire_diameter_mm']}-"
            f"{input_dict['count_of_rings']}-"
            f"{'V' if input_dict['venturi_presence'] else '0'}-"
            f"{input_dict['wire_material']}"
        )
    }
    # logger.info(f"part_number = {part_number_generated['part_number']}")
    return input_dict.update(part_number_generated)

# Cчитает и добавляет массу
def add_calc_weight(input_dict):


    # Диаметр заготовки под донышко, мм
    bottom_blank_diameter_mm = int(input_dict["frame_diameter_mm"]) + 12 * 2 

    # Диаметр средней линии кольца
    ring_midline_diameter_mm = int(input_dict["frame_diameter_mm"]) - 2*int(input_dict["longitudinal_rod_diameter_mm"]) - int(input_dict["ring_wire_diameter_mm"])

    # Расчетный объем прутка, мм3
    calc_vol_longitudinal_rod = vol_cylinder ( int(input_dict['frame_length_mm']), int(input_dict["longitudinal_rod_diameter_mm"]) ) 

    # Расчетный объем кольца, мм3
    calc_vol_ring = vol_cylinder( circle_length(ring_midline_diameter_mm), int(input_dict["ring_wire_diameter_mm"]) ) 

    # Расчетный объем кольца горловины, мм3
    
        # Провера есть ли Вентури
    if input_dict["venturi_presence"] == 1:
        neck_ring_diameter_diff_mm = 0 # Расширения нет, для Вентури без раструба
    else: 
        neck_ring_diameter_diff_mm = NECK_RING_DIFF_DEFAULT

    calc_vol_neck_ring = vol_cylinder( circle_length(ring_midline_diameter_mm) + neck_ring_diameter_diff_mm, int(input_dict['ring_wire_diameter_mm']) )

    # Расчетный объем проволоки для одного стержня замка замка , мм3 (для когтя надо добавить на один стержень 90 мм) Задвиавается относительно уже введённого объёма однго стержня
    calc_vol_lock = vol_cylinder ( 90, int(input_dict["longitudinal_rod_diameter_mm"]) ) 

    # Расчетный объем донышка, мм3
    calc_vol_bottom = vol_cylinder ( bottom_thickness_mm, bottom_blank_diameter_mm ) 

    #Расчетный объем Вентури, мм3 расчитывается как объём тонкостенного цилиндра???
    calc_vol_venturi = (
                    vol_cylinder( venturi_height_mm, int(input_dict["venturi_diameter_mm"]) ) -
                    vol_cylinder( venturi_height_mm, int(input_dict["venturi_diameter_mm"]) - 2 * int(input_dict["venturi_thickness_mm"]) )
    )
    
    # Общий объем каркаса, м3
    calc_vol_frame = (                                                          
                    calc_vol_longitudinal_rod * int(input_dict['rod_count']) +
                    calc_vol_ring * (int(input_dict['count_of_rings']) * 3 - 1 + int(input_dict['frame_parts_count']) - 1) + # добавляем по три кольца на каждый замок
                    (calc_vol_lock * int(input_dict['frame_parts_count']) - 1) * int(input_dict['rod_count']) +
                    calc_vol_neck_ring * 1 +
                    calc_vol_bottom +
                    calc_vol_venturi * (1 if input_dict['venturi_presence'] else 0)
    )

    # logger.debug(input_dict)
    
    # масса = общий объём * плотность стали
    calc_weight = mm3_to_m3(calc_vol_frame) * material_density[input_dict["wire_material"]]
    
    # logger.info(    
    #     f"bottom_blank_diameter_mm = {bottom_blank_diameter_mm} mm, "
    #     f"ring_midline_diameter_mm = {ring_midline_diameter_mm} mm, "
    #     f"calc_vol_longitudinal_rod = {calc_vol_longitudinal_rod:.2f} mm3, "
    #     f"calc_vol_ring = {calc_vol_ring:.2f} mm3, "
    #     f"calc_vol_lock = {calc_vol_lock:.2f} mm3,"
    #     f"calc_vol_neck_ring = {calc_vol_neck_ring:.2f} mm3, "
    #     f"calc_vol_bottom = {calc_vol_bottom:.2f} mm3, "
    #     f"calc_vol_venturi = {calc_vol_venturi:.2f} mm3, "
    #     f"calc_vol_frame = {calc_vol_frame:.2f} mm3, "
    #     f"calc_weight = {calc_weight:.2f} kg"
    #     )

    return input_dict.update({"weight": f"{calc_weight:.2f}"}) # 

# Добавляем значение маштаба для записи на чертеже в зависимости от крупности вида, зависит от количества частей, чтобы всё умещалось. 
# Значения примерно соответствуют, подбирал в конкретных случаях вручную.
def add_scale_on_title_block(input_dict):
    frame_parts_count = float(input_dict["frame_parts_count"])
    scale = DEFAULT_SCALE
    if frame_parts_count == 2:
        scale = "1 : 4"
    if frame_parts_count == 3:  
        scale = "1 : 5"
    return input_dict.update({"scale": scale}) 

def add_material_as_wire_material(input_dict):
    input_dict["material"] = input_dict["wire_material"]
    return input_dict

# Считаем и добавляем диаметр донышка 
def add_bottom_diameter(input_dict):
    '''
    Внутренний диаеметр кольца плюс два диаметра продольного прутка. То же самое что диаметр каркаса минус два диаметра проволоки кольца
    А так же две толщины заготовки
    '''
    bottom_diameter = {"bottom_diameter": str( int(input_dict['frame_diameter_mm']) - 2 * int(input_dict["ring_wire_diameter_mm"]) + 
                                              2 * int(input_dict['bottom_thickness_mm']))}
    return input_dict.update(bottom_diameter)




     


