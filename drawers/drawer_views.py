# drawer_views.py
# UTC+5: 2025-05-13 00:51 — подключен отдельный модуль для рисования чертёжных видов

import svgwrite
from configs.config import (DEFAULT_NECK_LENGTH, NECK_RING_DIFF_DEFAULT, DEFAULT_BOTTOM_DIAMETER_PRESENCE, bottom_thickness_mm, 
    venturi_height_mm, venturi_diameter_1_mm, venturi_diameter_2_mm, overlap_lock, support_lock_ring)
from drawers.drawer_shapes import Line, Circle, Rect, Ellipse, Polyline, Polygon, Text, ThickPolyline
from drawers.drawer_dimenstions import draw_dimension, draw_diameter_dimension 
from frame_calculations import calculate_frame_length_match
from math import sin, cos, radians, degrees, hypot, tan, pi
import numpy as np
from configs.config_log import logger


# Добавление группы для фигуры
def draw_views(dwg: svgwrite.Drawing, combined_values: dict):
    
       

    # Начало координат вида слева на оси симметрии каркаса
    frame_parts_count = int(combined_values["frame_parts_count"])                       # Кол-во частей каркаса                        
    frame_length = int(combined_values["frame_length_mm"])                              # Длина каркаса
    frame_diameter = int(combined_values["frame_diameter_mm"])                          # Диаметр каркаса
    neck_length = int(combined_values["neck_length"])                                   # Длина оголовка
    neck_length_presence = combined_values["neck_length_presence"]                      # Наличие размера длины оголовка                                
    longitudinal_rod_diameter = int(combined_values["longitudinal_rod_diameter_mm"])    # Диметра продлольного прутка
    ring_wire_diameter = int(combined_values["ring_wire_diameter_mm"])                  # Диаметр проволоки кольца
    venturi_presence = int(combined_values["venturi_presence"])                         # Наличие Вентури
    venturi_diameter_mm = int(combined_values["venturi_diameter_mm"])                   # Диаметр фланца Вентури
    bottom_diameter = int(combined_values["bottom_diameter"])                           # Диаметр донышка
    bottom_diameter_presence = DEFAULT_BOTTOM_DIAMETER_PRESENCE                         # Наличие размера донышка (всегда включено)
    bottom_length_mm = int(combined_values["bottom_length_mm"])                         # Высота донышка
    rod_count = int(combined_values["rod_count"])                                       # Кол-во прутков, шт.
    bottom_presence = combined_values["bottom_presence"]                                # Наличие донышка
    count_of_steps_rings_frame_1 = int(combined_values["count_of_steps_rings_frame_1"])
    count_of_steps_rings_frame_2 = int(combined_values["count_of_steps_rings_frame_2"])
    count_of_steps_rings_frame_3 = int(combined_values["count_of_steps_rings_frame_3"])
    frame_length_1 = int(combined_values["frame_length_1"])
    frame_length_2 = int(combined_values["frame_length_2"])
    frame_length_3 = int(combined_values["frame_length_3"])
    

    # logger.debug(f"last_ring_to_bottom_length = {combined_values['last_ring_to_bottom_length']}")

    last_ring_to_bottom_length = int(combined_values["last_ring_to_bottom_length"])                 # Расстояние от последнего кольца до донышка
    last_ring_to_bottom_length_presence = combined_values["last_ring_to_bottom_length_presence"]    # Наличие размера до донышка
    distance_between_rings = int(combined_values["distance_between_rings"])                         # Расстояние между кольцами (шаг)
    
    count_of_rings = int(combined_values["count_of_rings"])                                         # Количество колец для каркаса без замков
    neck_ring_inner_diameter_presence = combined_values["neck_ring_inner_diameter_presence"]        # Наличие размера внутреннего диаметра кольца горловины

    # Координаты главноего вида
    translate_x_main_view = 72
    translate_y_main_view = 60
    scale_view_main_view = 2.5
    scale_dim_line_main_view = 1
    match frame_parts_count:
        case 1:
            step_lock = 0 # дополнительный шаг для замка
            add_lock = 0
            scale_view_lock = 1
        case 2:
            step_lock = 1
            add_lock = 0
            scale_view_lock = 1.3
            translate_y_main_view += 10 # опустить главный вид ниже на 10 чтобы размеры не упирались в рамку
        case 3:
            step_lock = 1
            add_lock = 1
            scale_view_lock = 2.0


    # Задаём параметры вида
    main_view = dwg.g(id='main_view', fill='none', font_family="GOST type A", 
                      font_size=5, stroke_width=0.4, text_anchor='middle', 
                      transform=f"scale({96/25.4}, {96/25.4}) translate({translate_x_main_view}, {translate_y_main_view}) scale({scale_dim_line_main_view/(scale_view_main_view*scale_view_lock)}, {scale_dim_line_main_view/(scale_view_main_view*scale_view_lock)})")
    # Задаём параметры размерных линий для вида 
    main_view_dim = dwg.g(id='main_view_dim', fill='none', font_family="GOST type A", 
                    font_size=5, stroke_width=0.4, text_anchor='middle', 
                    transform=f"scale({96/25.4}, {96/25.4}) translate({translate_x_main_view}, {translate_y_main_view}) scale({scale_dim_line_main_view/(scale_view_main_view)}, {scale_dim_line_main_view/(scale_view_main_view)})")


    # Провера есть ли Вентури
    if venturi_presence:
        neck_ring_diameter_diff_mm = 0 # Расширения нет, для Вентури без раструба
    else: 
        neck_ring_diameter_diff_mm = NECK_RING_DIFF_DEFAULT

    ring_diameter = frame_diameter - 2 * longitudinal_rod_diameter                      # Диаметр кольца
    ring_midline_diameter = ring_diameter - ring_wire_diameter                          # Диаметр кольца по средней линии
    neck_ring_diameter = neck_ring_diameter_diff_mm + ring_diameter                     # Диаметр кольца горловины
    neck_ring_midline_diameter = neck_ring_diameter_diff_mm + ring_midline_diameter     # Диаметр кольца горловины по средней линии
    
    gap = 100               # разрыв на чертеже, расстояние между кольцами на виде с разрывами
    lock_bend = 15.4        # насколько загнут кончек проволки в замке
    distansce_lock_on_view = add_lock*(overlap_lock+(step_lock+1)*distance_between_rings+gap) # Расстояние между замками на виде
    
    last_ring_on_view = (ring_wire_diameter/2 + neck_length + gap + distance_between_rings*(step_lock+1) + step_lock*overlap_lock + gap +
                        add_lock*distansce_lock_on_view)   # Положение последнего кольца  
    frame_length_on_view = last_ring_on_view + last_ring_to_bottom_length                           # Длина каркаса на виде с учётом разрывов
    

    # Рисуем Вентури
    if venturi_presence: # Проверка есть ли Вентури
        # venturi_height_mm = 175 # Высота Вентури, мм Нужно внести в водимые данные или получать из расчётов
        # venturi_diameter_1_mm = 88 # Диаметр Вентури, мм
        # venturi_diameter_2_mm = 90
        # venturi_diameter_mm 134
        vr1 = 29.3
        vx1, vy1 = 138, 25.27
        vr2 = 8
        vx2, vy2 = 167.9, 40.40
        
        # Рисуем конус Вентури
        venturi_path_cone = dwg.path(d=( 
            f"M {0},{0} "                                       
            f"V {-venturi_diameter_1_mm / 2} "  
            f"L {vx1}, {-vy1} "
            f"A {vr1},{vr1} 0 0 0 {vx2},{-vy2} "
            f"A {vr2 },{vr2 } 0 0 1 {venturi_height_mm},{-venturi_diameter_1_mm / 2} "
            f"V {0} "
            f"V {venturi_diameter_2_mm / 2} "
            f"A {vr2 },{vr2 } 0 0 1 {vx2},{vy2} "
            f"A {vr1},{vr1} 0 0 0 {vx1},{vy1} "
            f"L {0}, {venturi_diameter_1_mm / 2} "
            f"Z"                                                        # Замыкаем
        ), stroke_width=1, fill='white', stroke='black')

        main_view.add(venturi_path_cone)


    # Координаты для прутков и колец
    xnr, ynr = ( ring_wire_diameter / 2, neck_ring_midline_diameter / 2 )   # Начало оголовка
    xr1, yr1 = ( xnr + neck_length, ring_midline_diameter / 2 )             # + длина оголовка = первое кольцо
    xr2, yr2 = ( xr1 + gap, yr1 )                                           # + разрыв
    xr3, yr3 = ( xr2 + distance_between_rings*(step_lock), yr1 )       # + расстояиние шага
    xr4, yr4 = ( xr3 + distance_between_rings + step_lock*overlap_lock, yr1 )
    xr5, yr5 = ( xr4 + gap, yr1 )                                           # + разрыв
    xsr1, ysr1 = ( xr3 - support_lock_ring*step_lock, yr1 ) # кольцо 1 усиления замка
    xsr2, ysr2 = ( xr3 + (support_lock_ring + overlap_lock)*step_lock, yr1 ) # кольцо 2 усиления замка 
    #кольца для кторого замка
    xr3_2l, yr3_2l = ( xr2 + distance_between_rings*(step_lock) + distansce_lock_on_view, yr1 )
    xr4_2l, yr4_2l = ( xr3 + distance_between_rings + step_lock*overlap_lock + distansce_lock_on_view, yr1 )
    xr5_2l, yr5_2l = ( xr4 + gap + distansce_lock_on_view, yr1 )                                           # + разрыв
    xsr1_2l, ysr1_2l = ( xr3 - support_lock_ring*step_lock + distansce_lock_on_view, yr1 ) # кольцо 1 усиления замка
    xsr2_2l, ysr2_2l = ( xr3 + (support_lock_ring + overlap_lock)*step_lock + distansce_lock_on_view, yr1 ) # кольцо 2 усиления замка  


    coord_neck_ring =   [(xnr, -ynr), (xnr, ynr)]       # Кольцо оголовка
    coord_ring_1 =      [(xr1, -yr1), (xr1, yr1)]       # Кольцо 1
    coord_ring_2 =      [(xr2, -yr2), (xr2, yr2)]       # Кольцо 2
    coord_ring_3 =      [(xr3, -yr3), (xr3, yr3)]       # Кольцо 3
    coord_ring_4 =      [(xr4, -yr4), (xr4, yr4)]       # Кольцо 4
    coord_ring_5 =      [(xr5, -yr5), (xr5, yr5)]       # Кольцо 5
    coord_ring_sup1 =   [(xsr1, -ysr1), (xsr1, ysr1)]   # Кольцо 1 усиления замка
    coord_ring_sup2 =   [(xsr2, -ysr2), (xsr2, ysr2)]   # Кольцо 2 усиления замка 
    #кольца для кторого замка
    coord_ring_3_2l =   [(xr3_2l, -yr3_2l), (xr3_2l, yr3_2l)]        # Кольцо 3
    coord_ring_4_2l =      [(xr4_2l, -yr4_2l), (xr4_2l, yr4_2l)]       # Кольцо 4
    coord_ring_5_2l =      [(xr5_2l, -yr5_2l), (xr5_2l, yr5_2l)]       # Кольцо 5
    coord_ring_sup1_2l =   [(xsr1_2l, -ysr1_2l), (xsr1_2l, ysr1_2l)]   # Кольцо 1 усиления замка
    coord_ring_sup2_2l =   [(xsr2_2l, -ysr2_2l), (xsr2_2l, ysr2_2l)]   # Кольцо 2 усиления замка 

    coord_rings = [coord_neck_ring, coord_ring_1, coord_ring_2, coord_ring_3, coord_ring_4, coord_ring_5, coord_ring_sup1, coord_ring_sup2, 
                   coord_ring_3_2l, coord_ring_4_2l, coord_ring_5_2l, coord_ring_sup1_2l, coord_ring_sup2_2l]

    coord_rods = []
    step = 360 / rod_count
    for angle in np.arange(-90, 91, step):
        coord_rod= [(xnr, -(neck_ring_diameter + longitudinal_rod_diameter) / 2 * sin(radians(angle))), 
                    (xr1, -(ring_diameter + longitudinal_rod_diameter) / 2 * sin(radians(angle))),
                    (xr5_2l, -(ring_diameter + longitudinal_rod_diameter) / 2 * sin(radians(angle))),
                    (frame_length_on_view - bottom_thickness_mm - longitudinal_rod_diameter/2 , 
                    -(bottom_diameter - 2 * bottom_thickness_mm - ring_wire_diameter) / 2 * sin(radians(angle)))]
        
        coord_rods += [coord_rod]

    # Рисуем кольца прутки
    for i in coord_rings:
        ThickPolyline(i, ring_wire_diameter, stroke='black', stroke_width=1*scale_view_lock, fill='white').draw(dwg, main_view)
    for i in coord_rods:
        ThickPolyline(i, longitudinal_rod_diameter, stroke='black', stroke_width=1*scale_view_lock, fill='white').draw(dwg, main_view)


    # Рисуем донышко
    if bottom_presence: # Проверка есть ли донышко
        
        x_bot, y_bot = (frame_length_on_view - bottom_length_mm), (-bottom_diameter/2)
        width, height = bottom_length_mm, bottom_diameter
        r = 3  # радиус скругления

        bottom_path = dwg.path(d=(
            f"M {x_bot},{y_bot} "                                       # Верхний левый угол  
            f"H {x_bot + width - r} "                                   # Горизонтально до начала скругления
            f"A {r},{r} 0 0 1 {x_bot + width},{y_bot + r} "             # Скругление в правый верх
            f"V {y_bot + height - r} "                                  # Вертикально вниз до начала нижнего скругления
            f"A {r},{r} 0 0 1 {x_bot + width - r},{y_bot + height} "    # Скругление в правый низ
            f"H {x_bot} "                                               # Горизонтально влево
            f"Z"                                                        # Замыкаем
        ), stroke_width=1*scale_view_lock, fill='white', stroke='black')

        main_view.add(bottom_path)


    # Рисуем фланец Вентури
    if venturi_presence: # Проверка есть ли Вентури
        # venturi_diameter_mm = 134 # Диаметр фланца Вентури
        vr3 = 3 
        # Рисуем фланец
        venturi_path_flange = dwg.path(d=(
            f"M {0},{0} "                                       
            f"V {-venturi_diameter_mm / 2 + vr3} "  
            f"A {vr3},{vr3} 0 0 1 {vr3},{-venturi_diameter_mm / 2} "
            f"H {13}"
            f"V {0} "
            f"V {venturi_diameter_mm / 2} "
            f"H {vr3}" 
            f"A {vr3},{vr3} 0 0 1 {0},{venturi_diameter_mm / 2 - vr3} " 
            f"Z"                                                        # Замыкаем
        ), stroke_width=1, fill='white', stroke='black') 
        
        main_view.add(venturi_path_flange)


    # Рисуем замок
    if frame_parts_count != 1: # когда количество частей не равно 1

        # Вспомогательная функция для добавления точек дуги "когтя"
        def add_arc_points(coord_list, n, ang1, ang2, cx, cy, radius, angle):
            """
            Добавляет n промежуточных точек на дуге между углами ang1 и ang2
            (в градусах) и дописывает их в список coord_list.

            Особенности:
            - Используется n+2 равномерно распределённых угла от ang1 до ang2,
            затем отбрасываются крайние (ang1 и ang2), чтобы остались только
            внутренние точки дуги.
            - Система координат предполагает ось Y направленной вниз (как в SVG):
            поэтому по Y используется вычитание: y = cy - radius * sin(...).
            
            Параметры:
                coord_list : list
                    Список, в который будут добавлены точки в виде кортежей (x, y).
                n : int
                    Количество внутренних точек на дуге.
                ang1 : float
                    Начальный угол дуги в градусах.
                ang2 : float
                    Конечный угол дуги в градусах.
                cx, cy : float
                    Координаты центра дуги.
                radius : float
                    Радиус дуги.
            """
            # Формируем n+2 точек от ang1 до ang2 и берём только внутренние (без крайних)
            angles = np.linspace(ang1, ang2, n + 2)[1:-1]

            for ang in angles:
                x = cx + radius * cos(radians(ang))
                # Ось Y направлена вниз, поэтому вычитаем синус
                y = cy - radius * sin(radians(ang))
                coord_list.append((x, y * sin(radians(angle))))

        
        def mirror_points_by_vertical_axis(groups, mirror_x):
            """
            Отражает точки относительно вертикальной оси x = mirror_x.
            
            :param groups: список списков точек, например:
                        [
                            [(x1, y1), (x2, y2)],
                            [(x3, y3), (x4, y4)],
                        ]
            :param mirror_x: координата вертикальной оси отражения (x = mirror_x)
            :return: новый список с тем же уровнем вложенности, но с отражёнными по x точками
            """
            mirrored_groups = []

            for group in groups:
                mirrored_group = []
                for x, y in group:
                    # Смещаем к оси, меняем знак, возвращаем обратно
                    # x' = 2 * mirror_x - x
                    x_new = 2 * mirror_x - x
                    mirrored_group.append((x_new, y))
                mirrored_groups.append(mirrored_group)

            return mirrored_groups
        

        def merge_zipped_groups(list_a, list_b):
            """
            Сливает два списка списков (list_a и list_b) по принципу "молнии".

            Условия:
            - len(list_a) == len(list_b)

            Правила слияния (n = длина списков):
            - Первая часть: индексы 0 .. mid (включительно) → A[i], B[i]
            - Вторая часть: индексы mid+1 .. n-1 → B[i], A[i]

            где mid = n // 2 (целая часть деления).
            При нечётной длине "средний" элемент (mid) попадает в первую часть.

            Примеры порядка индексов:
            n = 4 (mid = 2):
                A0,B0, A1,B1,  B2,A2, B3,A3
            n = 5 (mid = 2):
                A0,B0, A1,B1, A2,B2,  B3,A3, B4,A4
            """
            if len(list_a) != len(list_b):
                raise ValueError("Списки должны быть одинаковой длины")

            n = len(list_a)
            if n == 0:
                return []

            mid = n // 2  # "центр", при нечётной длине включён в первую часть

            merged = []

            # Первая часть: от 0 до mid включительно → A, потом B
            for i in range(mid + 1):
                merged.append(list_a[i])
                merged.append(list_b[i])

            # Вторая часть: от mid+1 до конца → B, потом A
            for i in range(mid + 1, n):
                merged.append(list_b[i])
                merged.append(list_a[i])

            return merged
        
        # Прямоугольник-разрыв под замок
        centr_lock_x = ring_wire_diameter/2 + neck_length + gap + distance_between_rings + overlap_lock/2  # координаты центра замка по x
        centr_lock_y = 0                                                                        # координаты центра замка по y

        break_width = 90                                     # ширина зоны разрыва
        break_height = ring_midline_diameter + 20            # высота зоны разрыва

        break_x = centr_lock_x - break_width/2               # координаты для рисования разрыва x
        break_y = centr_lock_y - break_height/2              # координаты для рисования разрыва y

        rect_insert = (break_x, break_y)
        rect_size = (break_width, break_height)

        # Белый прямоугольник поверх существующей геометрии
        Rect(insert=rect_insert, size=rect_size, stroke="white", fill="white").draw(dwg, main_view)
        Rect(insert=(break_x + distansce_lock_on_view, break_y), size=rect_size, stroke="white", fill="white").draw(dwg, main_view) # второй замок
      
        def build_lock_wire_polyline(
                    centr_lock_x,
                    angle,
                    frame_diameter,
                    longitudinal_rod_diameter,
                    overlap_lock,
                    ring_wire_diameter,
                    gap,
                    distance_between_rings,
                ):

            # Координаты для соединителя "коготь"
            midline_rod_lock = frame_diameter / 2 - longitudinal_rod_diameter / 2  # средняя линия проволоки замка, положение по y
            coord_lock_line_start_x = centr_lock_x - (overlap_lock/2 - ring_wire_diameter/2)
            coord_lock_line_start_y = - midline_rod_lock

            coord_lock_line = []

            # стартовые точки
            
            coord_lock_line.append((centr_lock_x -(gap/2 + distance_between_rings + overlap_lock/2), coord_lock_line_start_y * sin(radians(angle))))
            coord_lock_line.append((coord_lock_line_start_x + 4, (coord_lock_line_start_y + 0) * sin(radians(angle))))

            # --- Дуга 1 ---
            add_arc_points(
                coord_list=coord_lock_line,
                n=15,
                ang1=90.00,
                ang2=66.56,
                cx=coord_lock_line_start_x + 4,
                cy=coord_lock_line_start_y + 11.50,
                radius=11.50,
                angle=angle,
            )

            coord_lock_line.append((coord_lock_line_start_x + 8.57, (coord_lock_line_start_y + 0.95) * sin(radians(angle))))
            coord_lock_line.append((coord_lock_line_start_x + 20.81, (coord_lock_line_start_y + 6.25) * sin(radians(angle))))

            # --- Дуга 2 ---
            add_arc_points(
                coord_list=coord_lock_line,
                n=15,
                ang1=246.56,
                ang2=329.54,
                cx=coord_lock_line_start_x + 22,
                cy=coord_lock_line_start_y + 3.50,
                radius=3.00,
                angle=angle,
            )

            coord_lock_line.append((coord_lock_line_start_x + 24.59, (coord_lock_line_start_y + 5.02) * sin(radians(angle))))

            # --- Дуга 3 ---
            add_arc_points(
                coord_list=coord_lock_line,
                n=15,
                ang1=149.54,
                ang2=86.94,
                cx=coord_lock_line_start_x + 26.31,
                cy=coord_lock_line_start_y + 6.04,
                radius=2.00,
                angle=angle,
            )

            coord_lock_line.append((coord_lock_line_start_x + 26.42, (coord_lock_line_start_y + 4.04) * sin(radians(angle))))

            # --- Дуга 4 ---
            add_arc_points(
                coord_list=coord_lock_line,
                n=15,
                ang1=86.94,
                ang2=45.00,
                cx=coord_lock_line_start_x + 25,
                cy=coord_lock_line_start_y + 30.50,
                radius=26.50,
                angle=angle,
            )

            coord_lock_line.append((coord_lock_line_start_x + 43.74, (coord_lock_line_start_y + 11.76) * sin(radians(angle))))
            coord_lock_line.append((coord_lock_line_start_x + 50.94, (coord_lock_line_start_y + 18.96) * sin(radians(angle))))
            
            # ThickPolyline(coord_lock_line, longitudinal_rod_diameter, stroke='black', stroke_width=1, fill='white').draw(dwg, main_view)

            # # Белый прямоугольник поверх существующей геометрии чтобы скрыть место стыка слева

            # patch_width = 5                                                # ширина зоны 
            # patch_height = longitudinal_rod_diameter - (0.5 * 2)           # высота зоны за минусом ширины линии

            # patch_x = coord_lock_line_start_x - break_width / 2 - patch_width / 2               # координаты для рисования заплатки x
            # patch_y = coord_lock_line_start_y * sin(radians(angle)) - patch_height / 2              # координаты для рисования заплатки y

            # rect_insert = (patch_x, patch_y)
            # rect_size = (patch_width, patch_height)
            # # logger.debug(f"coord_lock_line_start_x = {coord_lock_line_start_x}")
            # # logger.debug(f"coord_lock_line_start_y = {coord_lock_line_start_y}")
            # # logger.debug(f"rect_insert = {rect_insert}")
            # # logger.debug(f"rect_size = {rect_size}")

            # Rect(insert=rect_insert, size=rect_size, stroke="white", fill="white").draw(dwg, main_view) # Заплатка на стык с полукругом на конце ThickPolyline
            # Line(start=(patch_x - 1, coord_lock_line_start_y * sin(radians(angle)) - longitudinal_rod_diameter/2), end=(patch_x + patch_width + 1, coord_lock_line_start_y * sin(radians(angle)) - longitudinal_rod_diameter/2)).draw(dwg, main_view) # Заплатка на заплатку для линий верх
            # Line(start=(patch_x - 1, coord_lock_line_start_y * sin(radians(angle)) + longitudinal_rod_diameter/2), end=(patch_x + patch_width + 1, coord_lock_line_start_y * sin(radians(angle)) + longitudinal_rod_diameter/2)).draw(dwg, main_view) # Заплатка на заплатку для линий низ
            
            return coord_lock_line
    
        def add_lock(centr_lock_x):
            # Координаты для соединителя "коготь"
            midline_rod_lock = frame_diameter / 2 - longitudinal_rod_diameter / 2  # средняя линия проволоки замка, положение по y
            coord_lock_line_start_x = centr_lock_x - (overlap_lock/2 - ring_wire_diameter/2)
            coord_lock_line_start_y = - midline_rod_lock

            coord_lock_lines = []
            for angle in np.arange(-90, 91, step):
                
                coord_lock_line = build_lock_wire_polyline(centr_lock_x,angle,frame_diameter,longitudinal_rod_diameter,
                                                           overlap_lock,ring_wire_diameter,gap,distance_between_rings)

                coord_lock_lines += [coord_lock_line] # собираем все прутки замка


            coord_lock_ring = [((coord_lock_line_start_x + overlap_lock - ring_wire_diameter/2),(coord_lock_line_start_y + 3.50)),((coord_lock_line_start_x + overlap_lock - ring_wire_diameter/2), -(coord_lock_line_start_y + 3.50))] # кольцо замка, рисуем польцо противоплодней части
            
            ThickPolyline(coord_lock_ring, ring_wire_diameter, stroke='black', stroke_width=1*scale_view_lock, fill='white').draw(dwg, main_view)

            # Отзеркаленный список
            coord_lock_lines_mirror = mirror_points_by_vertical_axis(coord_lock_lines, centr_lock_x)

            # Сшиваем оба списка вместе
            merged_lock_lines = merge_zipped_groups(coord_lock_lines, coord_lock_lines_mirror)

            for i in merged_lock_lines:
                ThickPolyline(i, longitudinal_rod_diameter, stroke='black', stroke_width=1*scale_view_lock, fill='white').draw(dwg, main_view)

            coord_lock_ring_mirror = mirror_points_by_vertical_axis([coord_lock_ring], centr_lock_x)

            for ring_points in coord_lock_ring_mirror:
                ThickPolyline(ring_points, ring_wire_diameter, stroke='black', stroke_width=1*scale_view_lock, fill='white').draw(dwg, main_view)

            
            # for angle in np.arange(-90, 91, step): # заплатки справа
            #                 # Белый прямоугольник поверх существующей геометрии чтобы скрыть место стыка слева

            #     # patch_width = 5                                                # ширина зоны 
            #     # patch_height = longitudinal_rod_diameter - (0.5 * 2)           # высота зоны за минусом ширины линии

                

            #     patch_x = coord_lock_line_start_x + break_width / 2 + 20 - patch_width / 2               # координаты для рисования заплатки x , 20 смещение на отзеркаливание
            #     patch_y = coord_lock_line_start_y * sin(radians(angle)) - patch_height / 2              # координаты для рисования заплатки y

            #     rect_insert = (patch_x, patch_y)
            #     rect_size = (patch_width, patch_height)
            #     # logger.debug(f"coord_lock_line_start_x = {coord_lock_line_start_x}")
            #     # logger.debug(f"coord_lock_line_start_y = {coord_lock_line_start_y}")
            #     # logger.debug(f"rect_insert = {rect_insert}")
            #     # logger.debug(f"rect_size = {rect_size}")

            #     Rect(insert=rect_insert, size=rect_size, stroke="white", fill="white").draw(dwg, main_view) # Заплатка на стык с полукругом на конце ThickPolyline
            #     Line(start=(patch_x - 1, coord_lock_line_start_y * sin(radians(angle)) - longitudinal_rod_diameter/2), end=(patch_x + patch_width + 1, coord_lock_line_start_y * sin(radians(angle)) - longitudinal_rod_diameter/2)).draw(dwg, main_view) # Заплатка на заплатку для линий верх
            #     Line(start=(patch_x - 1, coord_lock_line_start_y * sin(radians(angle)) + longitudinal_rod_diameter/2), end=(patch_x + patch_width + 1, coord_lock_line_start_y * sin(radians(angle)) + longitudinal_rod_diameter/2)).draw(dwg, main_view) # Заплатка на заплатку для линий низ



                
            # coord_rods = []
            # step = 360 / rod_count
            # for angle in np.arange(-90, 91, step):
            #     coord_rod= [(ring_wire_diameter/2, -(neck_ring_diameter + longitudinal_rod_diameter) / 2 * sin(radians(angle))), 
            #                 (ring_wire_diameter/2 + neck_length, -(ring_diameter + longitudinal_rod_diameter) / 2 * sin(radians(angle))),
            #                 (ring_wire_diameter/2 + neck_length + 100 + distance_between_rings + 100, -(ring_diameter + longitudinal_rod_diameter) / 2 * sin(radians(angle))),
            #                 (frame_length_on_view - bottom_thickness_mm - longitudinal_rod_diameter/2 , -(bottom_diameter - 2 * bottom_thickness_mm - ring_wire_diameter) / 2 * sin(radians(angle)))]
            #     coord_rods += [coord_rod]

            # # Рисуем кольца прутки
            # for i in coord_rings:
            #     ThickPolyline(i, ring_wire_diameter, stroke='black', stroke_width=1, fill='white').draw(dwg, main_view)
            # for i in coord_rods:
            #     ThickPolyline(i, longitudinal_rod_diameter, stroke='black', stroke_width=1, fill='white').draw(dwg, main_view)

        # Рисуем замки
        add_lock(centr_lock_x)
        add_lock(centr_lock_x + distansce_lock_on_view)

        # Координаты для выносного элемента Б на главном виде
        cx_B = centr_lock_x + 30/2
        cy_B = -ring_midline_diameter/2 + 5
        cr_B = 35
        angle_line_B = radians(60) # угол наклона выносной линии(от вертикали)
        dist1_line_B = 30 # длина наклоной линии
        dist2_line_B = 20 # длина плочки под букву
        x1_B = cx_B + cr_B * sin(angle_line_B)
        y1_B = cy_B - cr_B * cos(angle_line_B)
        x2_B = x1_B + dist1_line_B * sin(angle_line_B)
        y2_B = y1_B - dist1_line_B * cos(angle_line_B)
        x3_B = x2_B + dist2_line_B
        y3_B = y2_B
        Circle((cx_B, cy_B), cr_B, stroke_width=1*scale_view_lock, ).draw(dwg, main_view)
        Polyline([(x1_B,y1_B), (x2_B,y2_B), (x3_B,y3_B)], stroke_dasharray='1,0', stroke_width=1*scale_view_lock).draw(dwg, main_view)
        Text("Б", (x2_B + dist2_line_B / 2 , (y2_B - 5)), stroke_width=0.01, font_size=15*scale_view_lock).draw(dwg, main_view)




    # Осевая линия
    Line((-10,0), (frame_length_on_view + 10, 0), stroke_width=0.4*scale_view_lock, dasharray="14,4,2,4").draw(dwg, main_view) 

    # Рисуем разрывы
    x1 = 18.1
    x2 = 7.8
    x3 = 12.5
    y1 = 36.2
    y2 = 46.5
    y3 = 80.2
    coord_gap = [[(x3,y3), (x2,y2), (x1,y1), 
                 (x2,-y1), (x1,-y2), (x3,-y3)], 
                 [(-x3,-y3), (-x2,-y2), (-x1,-y1), 
                 (-x2, y1), (-x1, y2), (-x3,y3)]]
    x1_gap = ring_wire_diameter / 2 + neck_length + gap/2
    x2_gap = gap/2 + distance_between_rings * (step_lock+1) + step_lock*overlap_lock + gap/2
    main_view_sub1 = dwg.g(id='main_view_sub1', transform=f"translate({x1_gap}, 0)") 
    main_view_sub2 = dwg.g(id='main_view_sub2', transform=f"translate({x1_gap + x2_gap}, 0)") 
    main_view_sub3 = dwg.g(id='main_view_sub2', transform=f"translate({x1_gap + x2_gap + distansce_lock_on_view}, 0)") 

    main_view_subs = [main_view_sub1, main_view_sub2, main_view_sub3]

    for i in main_view_subs:
        Polygon([pt for group in coord_gap for pt in group], # [pt for group in coord_gap for pt in group] - распремляем структуру до одного уровня
                stroke='none', fill='white').draw(dwg, i) 
        for j in coord_gap:
            Polyline(j, stroke_dasharray='4,2', 
                    stroke_width=0.4*scale_view_lock, stroke='black').draw(dwg, i)
            # logger.info(f"i = {i}, j = {j}")
        main_view.add(i)

    



    ### Рисуем размеры на главном виде
    
    
    

    # Длина каркаса
    draw_dimension(dwg, main_view_dim, (0,0), (frame_length_on_view,0), offset=frame_diameter/2 + 75, value=frame_length, 
                scale_dim=scale_view_lock, line_stroke='black', line_width=0.6, font_size=12, marker_id='arrow_end')
        
    if bottom_presence: # Проверка есть ли донышко
        # Высота донышка
        if frame_parts_count != 3:
            draw_dimension(dwg, main_view_dim, (x_bot, y_bot), (x_bot + bottom_length_mm, y_bot), offset=-20, value=bottom_length_mm,
                        scale_dim=scale_view_lock, line_stroke='black', line_width=0.6, font_size=12, marker_id='arrow_start', ref=True)
        else: # слишком узко стало из-за масштаба, значение надо вынести в сторону
            draw_dimension(dwg, main_view_dim, (x_bot, y_bot), (x_bot + bottom_length_mm, y_bot), offset=-20, value=" ",
                        scale_dim=scale_view_lock, line_stroke='black', line_width=0.6, font_size=12, marker_id='arrow_start')
            Text(f"{bottom_length_mm}*", ((x_bot + bottom_length_mm + 35)/scale_view_lock, (y_bot-7)/scale_view_lock-20), stroke_width=0.01, font_size=12).draw(dwg, main_view_dim)
            Line(start=((x_bot + bottom_length_mm)/scale_view_lock, (y_bot)/scale_view_lock-20), end=((x_bot + bottom_length_mm + 50)/scale_view_lock, (y_bot)/scale_view_lock-20), stroke_width=0.6).draw(dwg, main_view_dim)
        
        if bottom_diameter_presence: # Проверка есть ли размер у донышка
            # Диаметр донышка
            draw_dimension(dwg, main_view_dim, (x_bot,y_bot+bottom_diameter), (x_bot, y_bot), offset=50, value=bottom_diameter, 
                        scale_dim = scale_view_lock, line_stroke='black', line_width=0.6, font_size=12, marker_id='arrow_end', show_diameter_symbol=True, ref=True)
    
    if venturi_presence: # Проверка есть ли Вентури
        # Диаметр фланца Вентури
        draw_dimension(dwg, main_view_dim, (0, (venturi_diameter_mm/2)), (0, -(venturi_diameter_mm/2)),
                offset=-50, value=(venturi_diameter_mm), 
                scale_dim = scale_view_lock, line_stroke='black', line_width=0.6, font_size=12, marker_id='arrow_end', show_diameter_symbol=True)        
    else: # Проверка размер горловины рисуется когда нет Вентури
        # Диаметр горловины
        draw_dimension(dwg, main_view_dim, (0, (frame_diameter/2 + neck_ring_diameter_diff_mm/2)), (0, -(frame_diameter/2 + neck_ring_diameter_diff_mm/2)),
                        offset=-50, value=(frame_diameter + neck_ring_diameter_diff_mm), 
                        scale_dim = scale_view_lock, line_stroke='black', line_width=0.6, font_size=12, marker_id='arrow_end', show_diameter_symbol=True)
        
    
    if neck_ring_inner_diameter_presence: # Проверка есть размер внутреннего диаметра кольца горловины
        # Внутренний диаметр кольца горловины
        draw_dimension(dwg, main_view_dim, (0, (neck_ring_diameter/2 - ring_wire_diameter)), (0, -(neck_ring_diameter/2 - ring_wire_diameter)),
                        offset=-30, value=(neck_ring_diameter - 2*ring_wire_diameter), 
                        scale_dim = scale_view_lock, line_stroke='black', line_width=0.6, font_size=12, marker_id='arrow_end', show_diameter_symbol=True)
    
    if neck_length_presence:
        # Длина оголовка
        draw_dimension(dwg, main_view_dim, (0, ring_midline_diameter/2), (ring_wire_diameter/2 + neck_length, ring_midline_diameter/2),
                    offset=60, value=(neck_length), 
                    scale_dim = scale_view_lock, line_stroke='black', line_width=0.6, font_size=12, marker_id='arrow_end', ref=True)

    if last_ring_to_bottom_length_presence:
        # Расстояние от последнего кольца до донышка из справочного значения
        draw_dimension(dwg, main_view_dim, (last_ring_on_view, ring_midline_diameter/2), (frame_length_on_view, ring_midline_diameter/2),
                    offset=60, value=(last_ring_to_bottom_length), 
                    scale_dim = scale_view_lock, line_stroke='black', line_width=0.6, font_size=12, marker_id='arrow_end', ref=True)
    
    if frame_parts_count == 1:
        # Расстояние от первого до последнего кольца из справочного значения
        ref_first_to_last_ring_length = f"{count_of_rings - 1} x {distance_between_rings} = {(count_of_rings - 1)*int(distance_between_rings)}"
            # logger.debug(f"ref_first_to_last_ring_length = {ref_first_to_last_ring_length}")
        draw_dimension(dwg, main_view_dim, (ring_wire_diameter/2 + neck_length, ring_midline_diameter/2), (last_ring_on_view, ring_midline_diameter/2),
                    offset=60, value=(ref_first_to_last_ring_length), 
                    scale_dim = scale_view_lock, line_stroke='black', line_width=0.6, font_size=12, marker_id='arrow_end', ref=True)
    
    if frame_parts_count == 2:
        # Расстояние от первого до кольца замка
        ref_first_to_lock_ring_length = f"{count_of_steps_rings_frame_1} x {distance_between_rings} = {(count_of_steps_rings_frame_1)*int(distance_between_rings)}"
            # logger.debug(f"ref_first_to_last_ring_length = {ref_first_to_last_ring_length}")
        draw_dimension(dwg, main_view_dim, (ring_wire_diameter/2 + neck_length, ring_midline_diameter/2), (centr_lock_x-overlap_lock/2, ring_midline_diameter/2),
                    offset=60, value=(ref_first_to_lock_ring_length), 
                    scale_dim = scale_view_lock, line_stroke='black', line_width=0.6, font_size=12, marker_id='arrow_end', ref=True)
        # Расстояние от замка до последнего кольца
        ref_lock_to_last_ring_length = f"{count_of_steps_rings_frame_2} x {distance_between_rings} = {(count_of_steps_rings_frame_2)*int(distance_between_rings)}"
            # logger.debug(f"ref_first_to_last_ring_length = {ref_first_to_last_ring_length}")
        draw_dimension(dwg, main_view_dim, (centr_lock_x+overlap_lock/2, ring_midline_diameter/2), (last_ring_on_view, ring_midline_diameter/2),
                    offset=60, value=(ref_lock_to_last_ring_length), 
                    scale_dim = scale_view_lock, line_stroke='black', line_width=0.6, font_size=12, marker_id='arrow_end', ref=True)
        
        # Шаг до кольца
        draw_dimension(dwg, main_view_dim, (centr_lock_x-overlap_lock/2-distance_between_rings, ring_midline_diameter/2), (centr_lock_x-overlap_lock/2, ring_midline_diameter/2), 
                    offset=40, value=distance_between_rings, 
                    scale_dim=scale_view_lock, line_stroke='black', line_width=0.6, font_size=12, marker_id='arrow_end')
        # Шаг после кольца
        draw_dimension(dwg, main_view_dim, (centr_lock_x+overlap_lock/2, ring_midline_diameter/2), (centr_lock_x+overlap_lock/2+distance_between_rings, ring_midline_diameter/2), 
                    offset=40, value=distance_between_rings, 
                    scale_dim=scale_view_lock, line_stroke='black', line_width=0.6, font_size=12, marker_id='arrow_end')
        
        # Кольцо усиления до замка
        draw_dimension(dwg, main_view_dim, (centr_lock_x-overlap_lock/2-support_lock_ring, ring_midline_diameter/2), (centr_lock_x-overlap_lock/2, ring_midline_diameter/2), 
                    offset=25, value=support_lock_ring, 
                    scale_dim=scale_view_lock, line_stroke='black', line_width=0.6, font_size=12, marker_id='arrow_end')
        # Кольцо усиления после замка
        draw_dimension(dwg, main_view_dim, (centr_lock_x+overlap_lock/2, ring_midline_diameter/2), (centr_lock_x+overlap_lock/2+support_lock_ring, ring_midline_diameter/2), 
                    offset=25, value=support_lock_ring, 
                    scale_dim=scale_view_lock, line_stroke='black', line_width=0.6, font_size=12, marker_id='arrow_end')
        # Нахлёст соединения
        draw_dimension(dwg, main_view_dim, (centr_lock_x-overlap_lock/2, ring_midline_diameter/2), (centr_lock_x+overlap_lock/2, ring_midline_diameter/2), 
                    offset=25, value=overlap_lock,
                    scale_dim=scale_view_lock, line_stroke='black', line_width=0.6, font_size=12, marker_id='arrow_start')
        
        # Длина первой детали
        draw_dimension(dwg, main_view_dim, (0, -ring_midline_diameter/2+lock_bend), (centr_lock_x+overlap_lock/2+30, -ring_midline_diameter/2+lock_bend), 
                    offset=-(lock_bend+70)/scale_view_lock, value=frame_length_1, 
                    scale_dim=scale_view_lock, line_stroke='black', line_width=0.6, font_size=12, marker_id='arrow_end')
        
        # Перекрытие для размерных линий
        size_x = float(4)
        size_y = float(4)
        rect_size = (size_x, size_y)
        insert_x = ((centr_lock_x+overlap_lock/2+30)- size_x/2)/scale_view_lock
        insert_y = ((-ring_midline_diameter/2+lock_bend)-(lock_bend+55))/scale_view_lock - size_y/2
        rect_insert = (insert_x, insert_y)
        
        Rect(insert=rect_insert, size=rect_size, stroke="white", fill="white").draw(dwg, main_view_dim) # white
        
        # Длина второй детали
        draw_dimension(dwg, main_view_dim, (centr_lock_x-overlap_lock/2-30, -ring_midline_diameter/2+lock_bend), (frame_length_on_view, -ring_midline_diameter/2+lock_bend), 
                    offset=-(lock_bend+55)/scale_view_lock, value=frame_length_2, 
                    scale_dim=scale_view_lock, line_stroke='black', line_width=0.6, font_size=12, marker_id='arrow_end') 

    if frame_parts_count == 3:
        # Расстояние от первого до кольца замка
        ref_first_to_lock1_ring_length = f"{count_of_steps_rings_frame_1} x {distance_between_rings} = {(count_of_steps_rings_frame_1)*int(distance_between_rings)}"
            # logger.debug(f"ref_first_to_last_ring_length = {ref_first_to_last_ring_length}")
        draw_dimension(dwg, main_view_dim, (ring_wire_diameter/2 + neck_length, ring_midline_diameter/2), (centr_lock_x-overlap_lock/2, ring_midline_diameter/2),
                    offset=60, value=(ref_first_to_lock1_ring_length), 
                    scale_dim = scale_view_lock, line_stroke='black', line_width=0.6, font_size=12, marker_id='arrow_end', ref=True)
        # Расстояние от замка до последнего кольца
        ref_lock1_to_lock2_ring_length = f"{count_of_steps_rings_frame_2} x {distance_between_rings} = {(count_of_steps_rings_frame_2)*int(distance_between_rings)}"
            # logger.debug(f"ref_first_to_last_ring_length = {ref_first_to_last_ring_length}")
        draw_dimension(dwg, main_view_dim, (centr_lock_x+overlap_lock/2, ring_midline_diameter/2), (centr_lock_x-overlap_lock/2+distansce_lock_on_view, ring_midline_diameter/2),
                    offset=60, value=(ref_lock1_to_lock2_ring_length), 
                    scale_dim = scale_view_lock, line_stroke='black', line_width=0.6, font_size=12, marker_id='arrow_end', ref=True)
        # Расстояние от замка до последнего кольца
        ref_lock2_to_last_ring_length = f"{count_of_steps_rings_frame_3} x {distance_between_rings} = {(count_of_steps_rings_frame_3)*int(distance_between_rings)}"
            # logger.debug(f"ref_first_to_last_ring_length = {ref_first_to_last_ring_length}")
        draw_dimension(dwg, main_view_dim, (centr_lock_x+overlap_lock/2+distansce_lock_on_view, ring_midline_diameter/2), (last_ring_on_view, ring_midline_diameter/2),
                    offset=60, value=(ref_lock2_to_last_ring_length), 
                    scale_dim = scale_view_lock, line_stroke='black', line_width=0.6, font_size=12, marker_id='arrow_end', ref=True)
        
        # Шаг до кольца
        draw_dimension(dwg, main_view_dim, (centr_lock_x-overlap_lock/2-distance_between_rings, ring_midline_diameter/2), (centr_lock_x-overlap_lock/2, ring_midline_diameter/2), 
                    offset=40, value=distance_between_rings, 
                    scale_dim=scale_view_lock, line_stroke='black', line_width=0.6, font_size=12, marker_id='arrow_end')
        # Шаг после кольца
        draw_dimension(dwg, main_view_dim, (centr_lock_x+overlap_lock/2, ring_midline_diameter/2), (centr_lock_x+overlap_lock/2+distance_between_rings, ring_midline_diameter/2), 
                    offset=40, value=distance_between_rings, 
                    scale_dim=scale_view_lock, line_stroke='black', line_width=0.6, font_size=12, marker_id='arrow_end')
        
        # Кольцо усиления до замка
        draw_dimension(dwg, main_view_dim, (centr_lock_x-overlap_lock/2-support_lock_ring, ring_midline_diameter/2), (centr_lock_x-overlap_lock/2, ring_midline_diameter/2), 
                    offset=25, value=support_lock_ring, 
                    scale_dim=scale_view_lock, line_stroke='black', line_width=0.6, font_size=12, marker_id='arrow_end')
        # Кольцо усиления после замка
        draw_dimension(dwg, main_view_dim, (centr_lock_x+overlap_lock/2, ring_midline_diameter/2), (centr_lock_x+overlap_lock/2+support_lock_ring, ring_midline_diameter/2), 
                    offset=25, value=support_lock_ring, 
                    scale_dim=scale_view_lock, line_stroke='black', line_width=0.6, font_size=12, marker_id='arrow_end')
        # Нахлёст соединения
        draw_dimension(dwg, main_view_dim, (centr_lock_x-overlap_lock/2, ring_midline_diameter/2), (centr_lock_x+overlap_lock/2, ring_midline_diameter/2), 
                    offset=25, value=overlap_lock,
                    scale_dim=scale_view_lock, line_stroke='black', line_width=0.6, font_size=12, marker_id='arrow_start')
        
        # Шаг после кольца
        draw_dimension(dwg, main_view_dim, (centr_lock_x+overlap_lock/2+distansce_lock_on_view, ring_midline_diameter/2), (centr_lock_x+overlap_lock/2+distance_between_rings+distansce_lock_on_view, ring_midline_diameter/2), 
                    offset=40, value=distance_between_rings, 
                    scale_dim=scale_view_lock, line_stroke='black', line_width=0.6, font_size=12, marker_id='arrow_end')
        
        # Кольцо усиления до замка
        draw_dimension(dwg, main_view_dim, (centr_lock_x-overlap_lock/2-support_lock_ring+distansce_lock_on_view, ring_midline_diameter/2), (centr_lock_x-overlap_lock/2+distansce_lock_on_view, ring_midline_diameter/2), 
                    offset=25, value=support_lock_ring, 
                    scale_dim=scale_view_lock, line_stroke='black', line_width=0.6, font_size=12, marker_id='arrow_end')
        # Кольцо усиления после замка
        draw_dimension(dwg, main_view_dim, (centr_lock_x+overlap_lock/2+distansce_lock_on_view, ring_midline_diameter/2), (centr_lock_x+overlap_lock/2+support_lock_ring+distansce_lock_on_view, ring_midline_diameter/2), 
                    offset=25, value=support_lock_ring, 
                    scale_dim=scale_view_lock, line_stroke='black', line_width=0.6, font_size=12, marker_id='arrow_end')
        # Нахлёст соединения
        draw_dimension(dwg, main_view_dim, (centr_lock_x-overlap_lock/2+distansce_lock_on_view, ring_midline_diameter/2), (centr_lock_x+overlap_lock/2+distansce_lock_on_view, ring_midline_diameter/2), 
                    offset=25, value=overlap_lock,
                    scale_dim=scale_view_lock, line_stroke='black', line_width=0.6, font_size=12, marker_id='arrow_start')
        
        # Длина первой детали
        draw_dimension(dwg, main_view_dim, (0, -ring_midline_diameter/2+lock_bend), (centr_lock_x+overlap_lock/2+30, -ring_midline_diameter/2+lock_bend), 
                    offset=-(lock_bend+100)/scale_view_lock, value=frame_length_1, 
                    scale_dim=scale_view_lock, line_stroke='black', line_width=0.6, font_size=12, marker_id='arrow_end')
        
        # Длина третьей детали
        draw_dimension(dwg, main_view_dim, (centr_lock_x-overlap_lock/2-30+distansce_lock_on_view, -ring_midline_diameter/2+lock_bend), (frame_length_on_view, -ring_midline_diameter/2+lock_bend), 
                    offset=-(lock_bend+100)/scale_view_lock, value=frame_length_3, 
                    scale_dim=scale_view_lock, line_stroke='black', line_width=0.6, font_size=12, marker_id='arrow_end')       

        # Перекрытие для размерных линий
        size_x = float(4)
        size_y = float(4)
        rect_size = (size_x, size_y)
        insert_x = ((centr_lock_x+overlap_lock/2+30)- size_x/2)/scale_view_lock
        insert_y = ((-ring_midline_diameter/2+lock_bend)-(lock_bend+80))/scale_view_lock - size_y/2
        rect_insert = (insert_x, insert_y)
        Rect(insert=rect_insert, size=rect_size, stroke="white", fill="white").draw(dwg, main_view_dim) # white

         # Перекрытие для размерных линий
        size_x = float(4)
        size_y = float(4)
        rect_size = (size_x, size_y)
        insert_x = ((centr_lock_x-overlap_lock/2-30+distansce_lock_on_view)- size_x/2)/scale_view_lock
        insert_y = ((-ring_midline_diameter/2+lock_bend)-(lock_bend+80))/scale_view_lock - size_y/2
        rect_insert = (insert_x, insert_y)
        Rect(insert=rect_insert, size=rect_size, stroke="white", fill="white").draw(dwg, main_view_dim) # white

        # Длина второй детали
        draw_dimension(dwg, main_view_dim, (centr_lock_x-overlap_lock/2-30, -ring_midline_diameter/2+lock_bend), (centr_lock_x+overlap_lock/2+30+distansce_lock_on_view, -ring_midline_diameter/2+lock_bend), 
                    offset=-(lock_bend+80)/scale_view_lock, value=frame_length_2, 
                    scale_dim=scale_view_lock, line_stroke='black', line_width=0.6, font_size=12, marker_id='arrow_end') 

    #  Пишем предупреждение о том, что проверка длины каркаса не прошла
    _, _, _, _, check_status = calculate_frame_length_match(combined_values)
    if not check_status: 
        Text("Проверка длины каркаса не пройдена, размеры некорректные", insert=(400, 150), font_size=40, fill="orangered", stroke_width = 10, rotate=-15).draw(dwg, main_view_dim)
     
    
    # Рисуем обозначене сечения
    x_section = (ring_wire_diameter/2 + neck_length) / scale_view_lock# Положение знака сечения по оси x
    offset_y = 10 # Расстояние между каркасом и знаком сечения
    y_section = (frame_diameter/2 + offset_y) / scale_view_lock # Положение знака сечения по оси y
    length_line_section = 35  # Длина линии знака сечения
    length_arrow = 35  # Длина стрелки к знаку сечения

    Line((x_section, y_section), (x_section, y_section+length_line_section), stroke="black", stroke_width=3).draw(dwg, main_view_dim)
    arrow_section_line_1 = dwg.line((x_section-length_arrow, (y_section + length_line_section - 10)), (x_section, (y_section + length_line_section - 10)), stroke="black", stroke_width=2)
    arrow_section_line_1.set_markers((None, None, '#arrow_section_end'))
    main_view_dim.add(arrow_section_line_1)
    Text("A", (x_section-length_arrow + 5, (y_section + length_line_section - 10 + 13)), stroke_width=0.01, font_size=15).draw(dwg, main_view_dim)

    Line((x_section, -y_section), (x_section, -(y_section+length_line_section)), stroke="black", stroke_width=3).draw(dwg, main_view_dim)
    arrow_section_line_2 = dwg.line((x_section-length_arrow, -(y_section + length_line_section - 10)), (x_section, -(y_section + length_line_section - 10)), stroke="black", stroke_width=2)
    arrow_section_line_2.set_markers((None, None, '#arrow_section_end'))
    main_view_dim.add(arrow_section_line_2)
    Text("A", (x_section-length_arrow + 5, -(y_section + length_line_section - 10 + 3)), stroke_width=0.01, font_size=15).draw(dwg, main_view_dim)












    # Координаты вида сечения
    translate_x_view_1 = 120
    translate_y_view_1 = 220
    scale_view_view_1 = 2.5
    scale_dim_line_view_1 = 2
    # Добавляем вид сечения / Задаём параметры вида
    view_1 = dwg.g(id='view_1', fill='none', font_family="GOST type A", 
                      font_size=5, stroke_width=0.5, text_anchor='middle', dominant_baseline="central", 
                      transform=f"scale({96/25.4}, {96/25.4}) translate({translate_x_view_1}, {translate_y_view_1}) scale({scale_dim_line_view_1/scale_view_view_1}, {scale_dim_line_view_1/scale_view_view_1})")
    
    # Начало координат вида слева на оси симметрии каркаса
        
    r = ring_diameter/2 + longitudinal_rod_diameter/2 
    # Circle((0,0), ring_diameter/2, stroke_width=0.5, fill="url(#hatch30)").draw(dwg, view_1)
    circle = dwg.circle((0,0), ring_diameter/2, stroke="black", stroke_width=0.5, fill="url(#hatch_1.5)")
    circle.rotate(30, (0, 0))
    view_1.add(circle)


    Circle((0,0), ring_diameter/2 - ring_wire_diameter, stroke_width=0.5, fill="white").draw(dwg, view_1)

    for angle in np.arange(0, 360, step):
        centr = r*sin(radians(angle)),-(r)*cos(radians(angle))
        # Circle((r*sin(radians(angle)),-(r)*cos(radians(angle))), longitudinal_rod_diameter/2, stroke_width=0.5, fill="url(#hatch120)").draw(dwg, view_1)
        circle = dwg.circle(centr, longitudinal_rod_diameter/2, stroke="black", stroke_width=0.5, fill="url(#hatch_0.5)")
        circle.rotate(60, centr)
        view_1.add(circle)

        line = dwg.line((0,-(r + longitudinal_rod_diameter/2 + 2)), (0,-(r - longitudinal_rod_diameter/2 - 2)), stroke='black', stroke_width=0.2)
        line.dasharray("7,2,1,2")
        line.rotate(angle, center=(0, 0))
        view_1.add(line)
    # ThickPolyline.draw(dwg, view_1)
    # Подпись вида    
    Text("A-A (1:1)", (0,(-(r + 10))), stroke_width=0.01, font_size=8).draw(dwg, view_1)
    # Осевые линии
    Line((-(r+5),0), (r+5,0), stroke_width=0.2, dasharray="7,2,1,2").draw(dwg, view_1)
    Line((0,-(r+5)), (0,r+5), stroke_width=0.2, dasharray="7,2,1,2").draw(dwg, view_1)
    Circle((0,0), r, stroke_width=0.2, dasharray="7,2,1,2").draw(dwg, view_1)
    
    # Рисуем размеры на виде с сечением
    # Диаметр продольного прутка
    angle_dim_rod = radians(20) # Под каким углом линия подходит к окружности
    offset_line_dim_rod = 3 # Расстояние полочки от центра окружности
    length_line_dim_rod = 25 # Длина полочки
    x1_dim_rod = (longitudinal_rod_diameter/2+offset_line_dim_rod)/tan(pi-angle_dim_rod)
    x2_dim_rod = -longitudinal_rod_diameter/2*cos(angle_dim_rod)
    y1_dim_rod = ring_diameter/2 + longitudinal_rod_diameter + offset_line_dim_rod
    y2_dim_rod = ring_diameter/2 + longitudinal_rod_diameter/2*(1+sin(angle_dim_rod))
    coord_1_dim_rod = (x1_dim_rod - length_line_dim_rod, y1_dim_rod)
    coord_2_dim_rod = (x1_dim_rod, y1_dim_rod)
    coord_3_dim_rod = (x2_dim_rod, y2_dim_rod)

    line_1_dim_rod = dwg.line(coord_1_dim_rod, coord_2_dim_rod, stroke='black', stroke_width=0.3)
    view_1.add(line_1_dim_rod)
    line_2_dim_rod = dwg.line(coord_2_dim_rod, coord_3_dim_rod, stroke='black', stroke_width=0.3)
    line_2_dim_rod.set_markers((None, None, '#arrow_end'))
    view_1.add(line_2_dim_rod) 

    text = dwg.text("", insert=(x1_dim_rod-length_line_dim_rod/2, y1_dim_rod-3), 
                    font_size=6, fill='black',text_anchor="middle")
    
    text.add(dwg.tspan("Ø", stroke_width=0.1, font_family="Arial", font_size=6))
    text.add(dwg.tspan(longitudinal_rod_diameter, stroke_width=0.1, font_size=6))       
    view_1.add(text)

    text_dim_rod = "прутка" if rod_count == 24 or rod_count == 22 else "прутков"
    text = dwg.text(f"{rod_count} {text_dim_rod}", insert=(x1_dim_rod-length_line_dim_rod/2, y1_dim_rod+3), 
                    font_size=6, stroke_width=0.1, fill='black',text_anchor="middle")
    view_1.add(text)






    # poly = ThickPolyline(
    # points=[(50, 50), (120, -50), (250, 50)],
    # thickness=20,
    # fill="hatch_30",
    # stroke="black",
    # stroke_width=1
    # )
    # poly.draw(dwg, view_1)
    # # add_hatch_fill(view_1, poly, spacing=4)
    # # add_hatch_fill(dwg, poly, spacing=4)
    





    # Диаметр проволоки кольца
    angle_dim_ring = 40 # Угол наклона размерной линии
    l_dim_ring = 10 # Длина линии, котороя водходит от полочки к окружности
    length_line_dim_ring = 10 # Длина полочки
    x1_dim_ring = -(ring_diameter/2 + l_dim_ring)*cos(radians(angle_dim_ring))
    y1_dim_ring = -(ring_diameter/2 + l_dim_ring)*sin(radians(angle_dim_ring))
    x2_dim_ring = -(ring_diameter/2)*cos(radians(angle_dim_ring))
    y2_dim_ring = -(ring_diameter/2)*sin(radians(angle_dim_ring))
    coord_1_dim_ring = (x1_dim_ring, y1_dim_ring)
    coord_2_dim_ring = (x2_dim_ring, y2_dim_ring)
    coord_3_dim_ring = (x1_dim_ring - length_line_dim_ring, y1_dim_ring)

    line_1_dim_ring = dwg.line(coord_1_dim_ring, coord_2_dim_ring, stroke='black', stroke_width=0.3)
    line_1_dim_ring.set_markers((None, None, '#arrow_end'))
    view_1.add(line_1_dim_ring) 
    line_2_dim_ring = dwg.line(coord_2_dim_ring, (0, 0), stroke='black', stroke_width=0.3)
    view_1.add(line_2_dim_ring)
    line_3_dim_ring = dwg.line(coord_3_dim_ring, coord_1_dim_ring, stroke='black', stroke_width=0.3)
    view_1.add(line_3_dim_ring)

    text = dwg.text("", insert=(x1_dim_ring - length_line_dim_ring/2, y1_dim_ring - 3 ), 
                font_size=6, fill='black',text_anchor="middle")
    
    text.add(dwg.tspan("Ø", stroke_width=0.1, font_family="Arial", font_size=6))
    text.add(dwg.tspan(ring_wire_diameter, stroke_width=0.1, font_size=6))       
    view_1.add(text)
    

    # Внутренний диаметр кольца
    draw_diameter_dimension(dwg, view_1, center=(0,0), radius=(ring_diameter/2-ring_wire_diameter), 
                            angle_deg=angle_dim_ring, value=(ring_diameter-2*ring_wire_diameter),
                            line_width=0.3, font_size=6, marker_id="arrow_end",
                            shift_factor=-0.4, norm_offset=-3)
    
    # Диаметр каркаса
    draw_dimension(dwg, view_1, (0,frame_diameter/2), (0,-frame_diameter/2), offset=frame_diameter/2+20, value=frame_diameter, text_offset=-3,
                   line_stroke='black', line_width=0.3, font_size=6, scale_dim_line_offset=scale_dim_line_view_1, marker_id='arrow_end', show_diameter_symbol=True)

    


    if frame_parts_count !=1:
        # Координаты вида Б выносной элемент
        translate_x_view_2 = 235
        translate_y_view_2 = 163
        scale_view_view_2 = 2.5
        r_view_2 = 50 # средний радиус белого кольца для закрашивания
        stroke_width_view_2 = 30 # ширина белого кольца для закрашивания
        scale_dim_line_view_2 = 2
        def shift_points(points, dx, dy):
            return [(x + dx, y + dy) for x, y in points]
        
        # Добавляем вид Б выносной элемент / Задаём параметры вида
        view_2 = dwg.g(id='view_2', fill='none', font_family="GOST type A", 
                        font_size=5, stroke_width=0.5, text_anchor='middle', dominant_baseline="central", 
                        transform=f"scale({96/25.4}, {96/25.4}) translate({translate_x_view_2}, {translate_y_view_2}) scale({scale_dim_line_view_2/scale_view_view_2}, {scale_dim_line_view_2/scale_view_view_2})")
        

        coord_lock_wire = build_lock_wire_polyline(centr_lock_x=0, angle=90, frame_diameter=frame_diameter, longitudinal_rod_diameter=longitudinal_rod_diameter,
                                                    overlap_lock=overlap_lock, ring_wire_diameter=ring_wire_diameter, gap=30, distance_between_rings=0)
    
    
        midline_rod_lock = frame_diameter / 2 - longitudinal_rod_diameter / 2
        dx = overlap_lock/2
        dy = -(-midline_rod_lock+ring_wire_diameter/2+longitudinal_rod_diameter/2)
        coord_lock_wire = shift_points(coord_lock_wire, dx=dx, dy=dy)
        
        # рисуем метку центра
        def mark_center(centr, mark_length, stroke_width, container):
            cx, cy = centr
            Line((cx-mark_length/2,cy),(cx+mark_length/2,cy),stroke_width=stroke_width, dasharray="4,1,0.5,1").draw(dwg, container)
            Line((cx,cy-mark_length/2),(cx,cy+mark_length/2),stroke_width=stroke_width, dasharray="4,1,0.5,1").draw(dwg, container)   

        coord_ring_lock_wire = [(-(overlap_lock/2),-midline_rod_lock+ring_wire_diameter/2+longitudinal_rod_diameter/2 ),
                                (- (overlap_lock/2),-midline_rod_lock+ring_wire_diameter/2+longitudinal_rod_diameter/2+60)]
        coord_ring_lock_wire = shift_points(coord_ring_lock_wire, dx=dx, dy=dy)

        ThickPolyline(coord_lock_wire, longitudinal_rod_diameter, stroke='black', stroke_width=0.5, fill='white').draw(dwg, view_2)
        ThickPolyline(coord_ring_lock_wire, ring_wire_diameter, stroke='black', stroke_width=0.5, fill='white').draw(dwg, view_2)
        # метка центра отсчёта
        # mark_center ((0,0), 6, stroke_width=0.1, container=view_2)
        # Circle((0, 0), 3, stroke_width=0.1, ).draw(dwg, view_2)
        
        # центра окружности выносного элемента
        cx_view_2 = overlap_lock
        cy_view_2 = 10
        Circle((cx_view_2, cy_view_2), r_view_2, stroke_width=stroke_width_view_2 , stroke='white' ).draw(dwg, view_2)
        Circle((cx_view_2, cy_view_2), r_view_2-stroke_width_view_2/2, stroke_width=0.3).draw(dwg, view_2)
        # Подпись вида    
        Text("Б (1:1)", (cx_view_2,(cy_view_2-r_view_2+stroke_width_view_2/2-10)), stroke_width=0.01, font_size=8).draw(dwg, view_2)
        Text("типовое", (cx_view_2,(cy_view_2-r_view_2+stroke_width_view_2/2-4)), stroke_width=0.01, font_size=6).draw(dwg, view_2)
        coord_marks_centr = [
            (ring_wire_diameter/2+4+18,0), # не понял почему надо ещё отнять ring_wire_diameter/2
            (ring_wire_diameter/2+4,10-ring_wire_diameter/2),
            (ring_wire_diameter/2+4+18+3,29-ring_wire_diameter/2), ]
        for i in coord_marks_centr:
            mark_center(i, 10, stroke_width=0.3, container=view_2)

        # Размеры выносного элемента
        draw_dimension(dwg, view_2, (0,-ring_wire_diameter/2+29), (0, -ring_wire_diameter/2), 
                    offset=-30, value=29, text_offset=-3,
                    line_stroke='black', line_width=0.3, font_size=6, marker_id='arrow_end',scale_dim_line_offset=scale_dim_line_view_2)
        Line((0,-ring_wire_diameter/2+29),(22,-ring_wire_diameter/2+29),stroke_width=0.3,).draw(dwg, view_2)
        draw_dimension(dwg, view_2, (4,-ring_wire_diameter/2+10), (4, -ring_wire_diameter/2), 
                    offset=-27, value=10, text_offset=-3,
                    line_stroke='black', line_width=0.3, font_size=6, marker_id='arrow_start', scale_dim_line_offset=scale_dim_line_view_2)
        
        draw_dimension(dwg, view_2, (4,-ring_wire_diameter/2+ring_wire_diameter/2), (4, -ring_wire_diameter/2), 
                    offset=-20, value=" ", text_offset=-3,
                    line_stroke='black', line_width=0.3, font_size=6, marker_id='arrow_slash', scale_dim_line_offset=scale_dim_line_view_2)
        draw_dimension(dwg, view_2, (4,-ring_wire_diameter/2), (4, -ring_wire_diameter/2-longitudinal_rod_diameter), 
                    offset=-20, value=" ", text_offset=-3,
                    line_stroke='black', line_width=0.3, font_size=6, marker_id='arrow_slash', scale_dim_line_offset=scale_dim_line_view_2)
        Line((0,0),(ring_wire_diameter/2+4+18,0),stroke_width=0.3,).draw(dwg, view_2)
        Line((-20+4,-ring_wire_diameter/2+8),(-20+4,-ring_wire_diameter/2-(5+10)),stroke_width=0.3,).draw(dwg, view_2)
        Text(f"Ø", (-20+4-3, -(ring_wire_diameter/2+longitudinal_rod_diameter+5)), stroke_width=0.01, font_size=6, font_family="Arial", rotate=-90).draw(dwg, view_2)
        Text(f"{longitudinal_rod_diameter}*", (-20+4-3, -(ring_wire_diameter/2+longitudinal_rod_diameter+10)), stroke_width=0.01, font_size=6, rotate=-90).draw(dwg, view_2)
        Text(f"{int(ring_wire_diameter/2)}", (-20+4-3, -(ring_wire_diameter/2-5)), stroke_width=0.01, font_size=6, rotate=-90).draw(dwg, view_2)
        
        draw_dimension(dwg, view_2, (-ring_wire_diameter/2, -ring_wire_diameter/2+29), (ring_wire_diameter/2, -ring_wire_diameter/2+29), 
                    offset=25, value=" ", text_offset=-3,
                    line_stroke='black', line_width=0.3, font_size=6, marker_id='arrow_slash', scale_dim_line_offset=scale_dim_line_view_2)
        draw_dimension(dwg, view_2, (ring_wire_diameter/2, -ring_wire_diameter/2+29), (ring_wire_diameter/2+4, -ring_wire_diameter/2+29), 
                    offset=25, value="4", text_offset=-3,
                    line_stroke='black', line_width=0.3, font_size=6, marker_id='arrow_slash', scale_dim_line_offset=scale_dim_line_view_2)
        draw_dimension(dwg, view_2, (ring_wire_diameter/2+4, -ring_wire_diameter/2+29), (ring_wire_diameter/2+4+18, -ring_wire_diameter/2+29), 
                    offset=25, value="18", text_offset=-3,
                    line_stroke='black', line_width=0.3, font_size=6, marker_id='arrow_end', scale_dim_line_offset=scale_dim_line_view_2)
        draw_dimension(dwg, view_2, (ring_wire_diameter/2+4+18, -ring_wire_diameter/2+29), (ring_wire_diameter/2+4+18+3, -ring_wire_diameter/2+29), 
                    offset=25, value=" ", text_offset=-3,
                    line_stroke='black', line_width=0.3, font_size=6, marker_id='arrow_start', scale_dim_line_offset=scale_dim_line_view_2)
        Line((-ring_wire_diameter/2-15,-ring_wire_diameter/2+29+25),(ring_wire_diameter/2+4+18+3+15, -ring_wire_diameter/2+29+25),stroke_width=0.3,).draw(dwg, view_2)
        Text(f"Ø", (-ring_wire_diameter/2-10, -ring_wire_diameter/2+29+25-3), stroke_width=0.01, font_size=6, font_family="Arial", ).draw(dwg, view_2)
        Text(f"{int(ring_wire_diameter)}*", (-ring_wire_diameter/2-5,-ring_wire_diameter/2+29+25-3), stroke_width=0.01, font_size=6, ).draw(dwg, view_2)
        Text("3", (ring_wire_diameter/2+4+18+3+8,-ring_wire_diameter/2+29+25-3), stroke_width=0.01, font_size=6, ).draw(dwg, view_2)
        Line((ring_wire_diameter/2+4,-ring_wire_diameter/2+29),(ring_wire_diameter/2+4, -ring_wire_diameter/2-longitudinal_rod_diameter),stroke_width=0.3,).draw(dwg, view_2)
        Line((ring_wire_diameter/2+4+18,-ring_wire_diameter/2+29),(ring_wire_diameter/2+4+18, 0),stroke_width=0.3,).draw(dwg, view_2)
        draw_dimension(dwg, view_2, (ring_wire_diameter/2, -ring_wire_diameter/2+17), (ring_wire_diameter/2+52.5, -ring_wire_diameter/2+17), 
                    offset=47, value="52", text_offset=-3,
                    line_stroke='black', line_width=0.3, font_size=6, marker_id='arrow_end', scale_dim_line_offset=scale_dim_line_view_2)
        def draw_leader_with_text(dwg, container, center, radius, angle_from_vertical_deg, line_length, text, along_offset=0, flip=False):
            a = radians(angle_from_vertical_deg)
            k = 1 if not flip else -1
            line_cx, line_cy = center           
            # концы линии
            line_x1 = line_cx + radius * sin(a)
            line_y1 = line_cy - radius * cos(a)
            line_x2 = line_x1 + line_length * sin(a) * k
            line_y2 = line_y1 - line_length * cos(a) * k
            line_start = (line_x2, line_y2)
            line_end   = (line_x1, line_y1)
            # линия со стрелкой
            arrow_section_line_1 = dwg.line(start=line_start, end=line_end, stroke="black", stroke_width=0.3 )
            arrow_section_line_1.set_markers((None, None, '#arrow_end'))
            view_2.add(arrow_section_line_1)
            # середина
            mid_x = (line_x1 + line_x2) / 2
            mid_y = (line_y1 + line_y2) / 2
            # нормаль (перпендикуляр)
            n = 1 if angle_from_vertical_deg > 180 else -1
            nx =  cos(a) * n
            ny =  sin(a) * n

            tx_dir = sin(a) * k
            ty_dir = -cos(a) * k
            offset = 3  # расстояние от линии
            tx = mid_x + nx * offset - tx_dir * along_offset
            ty = mid_y + ny * offset - ty_dir * along_offset
            # угол поворота текста вдоль линии
            angle_deg = - 90 + angle_from_vertical_deg
            angle_deg = angle_deg  if angle_from_vertical_deg < 180 else angle_deg - 180
            Text(text, (tx, ty), stroke_width=0.01, font_size=6, rotate=angle_deg).draw(dwg, container)
        
        draw_leader_with_text(dwg, view_2, ((ring_wire_diameter/2 + 4), (-ring_wire_diameter/2 + 10)), 
                              radius=13, angle_from_vertical_deg=20, line_length=15, text="R13", along_offset=-2)       
        draw_leader_with_text(dwg, view_2, ((ring_wire_diameter/2 + 4 + 18), 0), 
                        radius=1.5, angle_from_vertical_deg=150, line_length=13, text="R1,5", along_offset=-2)
        draw_leader_with_text(dwg, view_2, ((ring_wire_diameter/2 + 4 + 18 + 4.31), (-ring_wire_diameter/2 + 4.54)), 
                        radius=3.5, angle_from_vertical_deg=340, line_length=15, text="R3,5", along_offset=-2)
        draw_leader_with_text(dwg, view_2, ((ring_wire_diameter/2 + 4 + 18 + 3), (-ring_wire_diameter/2 + 29)), 
                        radius=25, angle_from_vertical_deg=45, line_length=25, text="R25", flip=True)
        

        dwg.add(view_2) # вид Б

    # порядок рисования видов на чертеже
    dwg.add(main_view)
    dwg.add(main_view_dim)
    dwg.add(view_1) # вид A
    
    
def add_hatch_fill(dwg, shape, spacing=5, angle=45, stroke='black', stroke_width=0.5):
    """
    Добавляет штриховку к фигуре (в том числе обёрткам) через clipPath.
    shape — либо svgwrite.Circle/Path, либо твой класс с атрибутом .shape
    """
    # Если shape — твой класс-обёртка, извлекаем оригинальный SVG-объект
    if hasattr(shape, 'shape'):
        shape = shape.shape

    # Проверяем тип и создаём копию фигуры
    if isinstance(shape, svgwrite.shapes.Circle):
        center_x = float(shape.attribs['cx'])
        center_y = float(shape.attribs['cy'])
        r = float(shape.attribs['r'])
        copied_shape = dwg.circle(center=(center_x, center_y), r=r)
        min_x, min_y = center_x - r, center_y - r
        max_x, max_y = center_x + r, center_y + r

    elif isinstance(shape, svgwrite.path.Path):
        d = shape.attribs['d']
        copied_shape = dwg.path(d=d)
        # Предполагаем границы (можно уточнить при необходимости)
        min_x, min_y = -100, -100
        max_x, max_y = 100, 100

    else:
        raise TypeError(f"Тип {type(shape)} не поддерживается для штриховки.")

    # Создаем clipPath
    clip_id = f"clip_{id(shape)}"
    clip = dwg.defs.add(dwg.clipPath(id=clip_id))
    clip.add(copied_shape)

    # Генерируем штриховку под углом
    width = max_x - min_x
    height = max_y - min_y

    angle_rad = radians(angle)
    length = hypot(width, height) * 1.5
    dx = spacing / sin(angle_rad)

    x = min_x - width
    while x < max_x + width:
        x1 = x
        y1 = min_y - height
        x2 = x + length * cos(angle_rad)
        y2 = y1 + length * sin(angle_rad)

        line = dwg.line(start=(x1, y1), end=(x2, y2), stroke=stroke, stroke_width=stroke_width)
        line['clip-path'] = f"url(#{clip_id})"
        dwg.add(line)

        x += dx