# UTC+5: 2025-05-10 18:30 — вынесено рисование размеров в отдельный модуль
# drawer_dimenstions.py

import numpy as np
from math import atan2, degrees, radians, cos, sin
from utils.utils_core import mm_to_pt, pt_to_mm
from drawers.drawer_shapes import HatchPattern
from configs.config_log import logger

def add_arrow_markers(dwg):
    marker = dwg.marker(id='arrow_end',
                        insert=(14, 3.5),
                        size=(14, 7),
                        viewBox="0 0 14 7",
                        orient="auto",
                        markerUnits="strokeWidth")

    # Простая стрелка
    arrow = dwg.path(d="M 0 0 L 14 3.5 L 0 7 Z", fill="black")
    marker.add(arrow)
    dwg.defs.add(marker)

    marker = dwg.marker(id='arrow_start',
                        insert=(0, 3.5),
                        size=(28, 7),
                        viewBox="0 0 28 7",
                        orient="auto",
                        markerUnits="strokeWidth")

    # Простая стрелка
    arrow = dwg.path(d="M 0 3.5 L 14 0 L 14 3 L 28 3 L 28 4 L 14 4 L 14 7 Z", fill="black")
    marker.add(arrow)
    dwg.defs.add(marker)


    dim_slash = 10
    marker = dwg.marker(id='arrow_slash',
                        insert=(dim_slash/2, dim_slash/2),
                        size=(dim_slash, dim_slash),
                        viewBox=f"0 0 {dim_slash} {dim_slash}",
                        orient="auto",
                        markerUnits="strokeWidth")

    # Косая черта
    # slash = dwg.path(d="M 0 0 L 7 1.75 L 0 3.5 Z", fill="black")
    slash = dwg.line(start=(0,dim_slash), end=(dim_slash,0), stroke="black", stroke_width=1, stroke_linecap="round")
    marker.add(slash)
    dwg.defs.add(marker)


    marker = dwg.marker(id='arrow_section_end',
                    insert=(7, 1.75),
                    size=(7, 3.5),
                    viewBox="0 0 7 3.5",
                    orient="auto",
                    markerUnits="strokeWidth")

    # Простая стрелка
    arrow = dwg.path(d="M 0 0 L 7 1.75 L 0 3.5 Z", fill="black")
    marker.add(arrow)
    dwg.defs.add(marker)

    
# Добавляем линейный размер. Строго слева направа.
def draw_dimension(dwg, container, pt1, pt2, offset=10, value=None, scale_dim = 1, text_offset=-7, 
                   line_stroke='black', line_width=1, font_size=5, scale_dim_line_offset=1,
                    marker_id='arrow_end', show_diameter_symbol=False, ref=False):
    if value != "":
        x1, y1 = pt1
        x2, y2 = pt2

        x1 = x1 / scale_dim
        x2 = x2 / scale_dim
        y1 = y1 / scale_dim
        y2 = y2 / scale_dim
        pt1 = (x1, y1)
        pt2 = (x2, y2)
        

        ext = 5 if offset > 0 else -5 # длина выступа выносных линий
        ext /= scale_dim_line_offset # масштабируем кончики выносных линий
        # Вектор направления
        dx = x2 - x1
        dy = y2 - y1
        length = (dx**2 + dy**2)**0.5
        angle = atan2(dy, dx)

        # Нормаль для смещения
        nx = -sin(angle)
        ny = cos(angle)
        
        # Смещённые точки
        p1_offset = (x1 + nx * offset, y1 + ny * offset)
        p2_offset = (x2 + nx * offset, y2 + ny * offset)

        # Центр основной линии
        mid_x = (p1_offset[0] + p2_offset[0]) / 2
        mid_y = (p1_offset[1] + p2_offset[1]) / 2

        # Основная линия из двух частей
        line1 = dwg.line(start=(mid_x, mid_y), end=p1_offset, stroke=line_stroke, stroke_width=line_width)
        line1.set_markers((None, None, f'#{marker_id}'))
        container.add(line1)

        line2 = dwg.line(start=(mid_x, mid_y), end=p2_offset, stroke=line_stroke, stroke_width=line_width)
        line2.set_markers((None, None, f'#{marker_id}'))
        container.add(line2)

        # Выносные линии
        p1_ext = (x1 + nx * (offset + ext), y1 + ny * (offset + ext))
        p2_ext = (x2 + nx * (offset + ext), y2 + ny * (offset + ext))
        container.add(dwg.line(start=pt1, end=p1_ext, stroke=line_stroke, stroke_width=line_width))
        container.add(dwg.line(start=pt2, end=p2_ext, stroke=line_stroke, stroke_width=line_width))

        # Текст
        if value is None:
            value = f"{round(length, 1)}"

        tx = mid_x + nx * text_offset
        ty = mid_y + ny * text_offset

        text = dwg.text("", insert=(tx, ty), font_size=font_size, fill='black',
                        text_anchor="middle", dominant_baseline="central",
                        transform=f"rotate({degrees(angle)} {tx} {ty})")

        if ref:
            value = f"{value}*"

        if show_diameter_symbol:
            text.add(dwg.tspan("Ø ", stroke_width=0.1, font_family="Arial", font_size=font_size))
            text.add(dwg.tspan(value, stroke_width=0.1, font_size=font_size))
        else:
            text.add(dwg.tspan(value, stroke_width=0.1, font_size=font_size))

        container.add(text)


def draw_diameter_dimension(dwg, container, center, radius, angle_deg=0, value=None,
                            line_stroke='black', line_width=1, font_size=5, marker_id='arrow',
                            shift_factor=0.4, norm_offset=-5): # shift_factor от -1.0 до 1.0 вдоль размерной линии, при =0 в центре
    angle = radians(angle_deg)
    dx = cos(angle)
    dy = sin(angle)

    # Точки на окружности по направлению угла
    start = (center[0] - dx * radius, center[1] - dy * radius)
    end = (center[0] + dx * radius, center[1] + dy * radius)

    # Размерная линия от центра в каждую сторону (две части)
    line1 = dwg.line(start=center, end=start, stroke=line_stroke, stroke_width=line_width)
    line1.set_markers((None, None, f'#{marker_id}'))
    container.add(line1)

    line2 = dwg.line(start=center, end=end, stroke=line_stroke, stroke_width=line_width)
    line2.set_markers((None, None, f'#{marker_id}'))
    container.add(line2)

    # Значение размера (если не указано)
    if value is None:
        value = f"{round(2 * radius, 1)}"

    # Смещение вдоль линии (от центра к концу) — не по центру
    text_base_x = center[0] + dx * radius * shift_factor
    text_base_y = center[1] + dy * radius * shift_factor

    # Смещение от линии (перпендикулярное)
    nx = -dy
    ny = dx
    text_x = text_base_x + nx * norm_offset
    text_y = text_base_y + ny * norm_offset

    # Текст с отдельным символом Ø
    text_elem = dwg.text("",
                         insert=(text_x, text_y),
                         font_size=font_size,
                         stroke_width=0.1,
                         fill='black',
                         text_anchor="middle",
                         dominant_baseline="central",
                         transform=f"rotate({angle_deg} {text_x} {text_y})")

    text_elem.add(dwg.tspan("Ø", stroke_width=0.1, font_family="Arial", font_size=font_size))
    text_elem.add(dwg.tspan(value, font_size=font_size))

    container.add(text_elem)


# сетка размерная
def draw_grid(dwg, spacing=mm_to_pt(10), width=mm_to_pt(420), height=mm_to_pt(297)):
    for x in np.arange(0, width, spacing):
        dwg.add(dwg.line(start=(x, 0), end=(x, height), stroke='lightgray'))
        dwg.add(dwg.text(int(pt_to_mm(x)), insert=(x, mm_to_pt(5)), font_family="GOST type A", font_size=15,fill="silver"))
    for x in np.arange(0, width, spacing*5):
        dwg.add(dwg.line(start=(x, 0), end=(x, height), stroke='silver'))
    for y in np.arange(0, height, spacing):
        dwg.add(dwg.line(start=(0, y), end=(width, y), stroke='lightgray'))
        dwg.add(dwg.text(int(pt_to_mm(y)), insert=(mm_to_pt(2), y), font_family="GOST type A", font_size=15,fill="silver"))
    for y in np.arange(0, height, spacing*5):
        dwg.add(dwg.line(start=(0, y), end=(width, y), stroke='silver'))

# Примечание
def draw_note(dwg):
    text = dwg.text("", insert=(830, 830), font_size=20, font_family='GOST type A', fill='black',)

    lines = ["1. * Размеры справочные.", 
             "2. Общие допуски по ГОСТ 30893.2 - vL.", 
             "3. Острые кромки на наружней поверхности не допускаются."]
    line_height = 25  # расстояние между строками

    for i, line in enumerate(lines):
        tspan = dwg.tspan(line, x=[875], dy=[line_height if i > 0 else 0])
        text.add(tspan)

    dwg.add(text)

# Создаем паттерн штриховки
def add_hatch_patterns(dwg):
    
    hatch1 = HatchPattern(
        id='hatch30',
        angle=30,
        spacing=1.5,
        stroke='black',
        stroke_width=0.2 
    )
    pattern1 = hatch1.generate(dwg)
    dwg.defs.add(pattern1)

    hatch2 = HatchPattern(
        id='hatch120',
        angle=120,
        spacing=0.5,
        stroke='black',
        stroke_width=0.2 
    )
    pattern2 = hatch2.generate(dwg)
    dwg.defs.add(pattern2) # нужен чтобы сработала строчка по id fill=f"url(#{hatch.id})")

    hatch3 = HatchPattern(
        id='hatch_1.5',
        angle=0,
        spacing=1.5,
        stroke='black',
        stroke_width=0.2 
    )
    pattern3 = hatch3.generate(dwg)
    dwg.defs.add(pattern3)

    hatch4 = HatchPattern(
        id='hatch_0.5',
        angle=0,
        spacing=0.5,
        stroke='black',
        stroke_width=0.2 
    )
    pattern4 = hatch4.generate(dwg)
    dwg.defs.add(pattern4)
        