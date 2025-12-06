# drawer_table.py

import svgwrite
from configs.config_log import logger
from configs.config import spec_table
from drawers.drawer_shapes import Line, Circle, Rect, Ellipse, Polyline, Polygon, Text

def draw_table(dwg: svgwrite.Drawing, combined_values: dict):
    table = dwg.g(id='table', fill='none', font_family="GOST type A", 
                  font_size=5, text_anchor='middle', dominant_baseline="central", 
                  transform=f"scale({96/25.4}, {96/25.4}) translate(290, 135)") #text_anchor='middle', dominant_baseline="central"
    
    Line(start=(0, 0), end=(122, 0), stroke='black', stroke_width=0.45).draw(dwg, table)
    for i in range(10, 10+6*11+1, 6):
        Line(start=(0, i), end=(122, i), stroke='black', stroke_width=0.45).draw(dwg, table)
    Line(start=(0, 0), end=(0, 10+6*11), stroke='black', stroke_width=0.45).draw(dwg, table)
    Line(start=(12, 0), end=(12, 10+6*11), stroke='black', stroke_width=0.45).draw(dwg, table)
    Line(start=(12+70, 0), end=(12+70, 10+6*11), stroke='black', stroke_width=0.45).draw(dwg, table)
    Line(start=(12+70+40, 0), end=(12+70+40, 10+6*11), stroke='black', stroke_width=0.45).draw(dwg, table)
    
    Text("Параметр", insert=(12+35, 5), font_size=7, stroke_width = 0.01).draw(dwg, table)

    Text("Количество замков, шт", insert=(12+35, 10+6*0+3), font_size=5, stroke_width = 0.01).draw(dwg, table)
    Text("Длина каркаса, мм", insert=(12+35, 10+6*1+3), font_size=5, stroke_width = 0.01).draw(dwg, table)
    Text("Диаметр каркаса, мм", insert=(12+35, 10+6*2+3), font_size=5, stroke_width = 0.01).draw(dwg, table)
    Text("Диаметр продольного прутка, мм", insert=(12+35, 10+6*3+3), font_size=5, stroke_width = 0.01).draw(dwg, table)
    Text("Кол-во прутков, шт.", insert=(12+35, 10+6*4+3), font_size=5, stroke_width = 0.01).draw(dwg, table)
    Text("Диаметр проволоки кольца, мм, шт", insert=(12+35, 10+6*5+3), font_size=5, stroke_width = 0.01).draw(dwg, table)
    Text("Наличие донышка (да/нет)", insert=(12+35, 10+6*6+3), font_size=5, stroke_width = 0.01).draw(dwg, table)
    Text("Наличие Вентури (да/нет)", insert=(12+35, 10+6*7+3), font_size=5, stroke_width = 0.01).draw(dwg, table)
    Text("Тип замка", insert=(12+35, 10+6*8+3), font_size=5, stroke_width = 0.01).draw(dwg, table)
    Text("Тип покрытия", insert=(12+35, 10+6*9+3), font_size=5, stroke_width = 0.01).draw(dwg, table)
    Text("Материал", insert=(12+35, 10+6*10+3), font_size=5, stroke_width = 0.01).draw(dwg, table)

    Text("Значение", insert=(12+70+20, 5), font_size=7, stroke_width = 0.01).draw(dwg, table)

    Text(f"{str(int(combined_values['frame_parts_count'])-1)}", insert=(12+70+20, 10+6*0+3), font_size=5, stroke_width = 0.01).draw(dwg, table)
    Text(f"{combined_values['frame_length_mm']}", insert=(12+70+20, 10+6*1+3), font_size=5, stroke_width = 0.01).draw(dwg, table)
    Text(f"{combined_values['frame_diameter_mm']}", insert=(12+70+20, 10+6*2+3), font_size=5, stroke_width = 0.01).draw(dwg, table)
    Text(f"{combined_values['longitudinal_rod_diameter_mm']}", insert=(12+70+20, 10+6*3+3), font_size=5, stroke_width = 0.01).draw(dwg, table)
    Text(f"{combined_values['rod_count']}", insert=(12+70+20, 10+6*4+3), font_size=5, stroke_width = 0.01).draw(dwg, table)
    Text(f"{combined_values['ring_wire_diameter_mm']}", insert=(12+70+20, 10+6*5+3), font_size=5, stroke_width = 0.01).draw(dwg, table)
    Text(f"{'да' if combined_values['bottom_presence'] else 'нет'}", insert=(12+70+20, 10+6*6+3), font_size=5, stroke_width = 0.01).draw(dwg, table)
    Text(f"{'да' if combined_values['venturi_presence'] else 'нет'}", insert=(12+70+20, 10+6*7+3), font_size=5, stroke_width = 0.01).draw(dwg, table)
    Text(f"{combined_values['lock_type']}", insert=(12+70+20, 10+6*8+3), font_size=5, stroke_width = 0.01).draw(dwg, table)
    Text(f"{combined_values['coating_type']}", insert=(12+70+20, 10+6*9+3), font_size=5, stroke_width = 0.01).draw(dwg, table)
    Text(f"Сталь {combined_values['wire_material']}", insert=(12+70+20, 10+6*10+3), font_size=5, stroke_width = 0.01).draw(dwg, table)

    for i in range(0, 11, 1):
        Text(f"{i+1}", insert=(6, 10+6*i+3), font_size=5, stroke_width = 0.01).draw(dwg, table)

    Text("№", insert=(6, 2.5), font_size=5, stroke_width = 0.01).draw(dwg, table)  
    Text("п/п", insert=(6, 7.5), font_size=5, stroke_width = 0.01).draw(dwg, table)

    dwg.add(table)