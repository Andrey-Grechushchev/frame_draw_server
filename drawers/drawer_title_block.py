# UTC+5: 2025-05-10 15:30 — вынесено рисование рамки в отдельный модуль

import svgwrite
from configs.config_log import logger
from configs.config_title_block import (
    stroke_width_title_block_A3_GOST, Mx_title_block_A3_GOST, My_title_block_A3_GOST,
    Lx_title_block_A3_GOST, Ly_title_block_A3_GOST, text_text_title_block_A3_GOST, 
    x_pos_text_title_block_A3_GOST, y_pos_text_title_block_A3_GOST, font_size_title_block_A3_GOST, 
    x_rot_text_title_block_A3_GOST, y_rot_text_title_block_A3_GOST, ang_rot_text_title_block_A3_GOST,
    INDEX_TEXT_TITLE_BLOCK_A3_GOST
)

def draw_title_block(dwg: svgwrite.Drawing, combined_values: dict, default_values: dict):
    """
    Добавляет на чертеж рамку формата A3 по ГОСТ и надписи.

    :param dwg: Объект svgwrite.Drawing
    :param combined_values: Значения для заполнения полей надписи
    :param default_values: Значения по умолчанию
    """
    # Основная надпись A3
    #Линии A3
    
    if (len(Mx_title_block_A3_GOST) + len(My_title_block_A3_GOST) + 
        len(Lx_title_block_A3_GOST) + len(Ly_title_block_A3_GOST)) / 4 == len(stroke_width_title_block_A3_GOST):
        for i in range(len(stroke_width_title_block_A3_GOST)):
            dwg.add(dwg.line(
                start=(Mx_title_block_A3_GOST[i], My_title_block_A3_GOST[i]),
                end=(Lx_title_block_A3_GOST[i], Ly_title_block_A3_GOST[i]),
                stroke="black",
                stroke_width=stroke_width_title_block_A3_GOST[i]
            ))

    # Надписи
    if (len(text_text_title_block_A3_GOST) + len(x_pos_text_title_block_A3_GOST) +
        len(y_pos_text_title_block_A3_GOST) + len(font_size_title_block_A3_GOST) + 
        len(x_rot_text_title_block_A3_GOST) + len(y_rot_text_title_block_A3_GOST)) / 6 == len(ang_rot_text_title_block_A3_GOST):
    # Проход по текстовым полям рамки
        for i in range(len(font_size_title_block_A3_GOST)):
            text_content = text_text_title_block_A3_GOST[i]
            # Ищем ключ, которому принадлежит индекс `i`
            key_for_i = next((k for k, indices in INDEX_TEXT_TITLE_BLOCK_A3_GOST.items() if i in indices), None)
            if key_for_i:
                current_value = combined_values.get(key_for_i)
                default_value = default_values.get(key_for_i)
                # logger.debug(f"i: {i}, key: '{key_for_i}', index_list: {INDEX_TEXT_TITLE_BLOCK_A3_GOST[key_for_i]}, старое='{default_value}', новое='{current_value}'")
                if current_value != default_value:
                    # logger.debug(f"ЗАМЕНА: ключ='{key_for_i}', индекс={i}, старое='{default_value}', новое='{current_value}'")
                    text_content = current_value

            # Добавляем слово сталь перед маркой материала
            if i == 41: # Материал
                text_content = f"Сталь {text_content}"

            scale_dict = { # Коэффиуиенты масштабирования
                0: 27, # 0: Обозначение внизу
                11: 24.5, # 11: Обозначение сверху
                41: 13 # 41: Материал
            }

            # # Динамическое масштабирование по длине надписи Обозначения на основе длины (формируется по шаблону, на длину сильнее все влияет марка стали материала)
            # if i == 0 or i == 11: # 0: Обозначение внизу, 11: Обозначение сверху
            #     char_width = 1
            #     max_width = 27 if i == 0 else 24.5
            #     scale_x = max_width / (char_width * len(text_content)) 
            #     # scale_x = 0.75 if i == 0 else 0.78 #при i==0 обозначение внизу (сжатие 0,8), при i==11 обозначение сверху (сжатие 0,78)

            
                
            if i in scale_dict:
                char_width = 1
                max_width = scale_dict[i]
                scale_x = max_width / (char_width * len(text_content))
            else:
                scale_x = 1 

                # print(i, max_width, scale_x )    
                            

            dwg.add(dwg.text(
                text_content,
                insert=(x_pos_text_title_block_A3_GOST[i], y_pos_text_title_block_A3_GOST[i]),
                transform=f"rotate({ang_rot_text_title_block_A3_GOST[i]} {x_rot_text_title_block_A3_GOST[i]},{y_rot_text_title_block_A3_GOST[i]}) "
                f"{f'translate({x_pos_text_title_block_A3_GOST[i] * (1 - scale_x)}, 0) scale({scale_x}, 1)'}",# сжатие относительно точки встаки на основе коэффициентов из словаря
                # f"{f'translate({x_pos_text_title_block_A3_GOST[i] * (1 - scale_x)}, 0) scale({scale_x}, 1)' if i==0 or i==11 else f''}", # сжатие относительно точки встаки
                # f"{f'translate({x_pos_text_title_block_A3_GOST[i]*(1-scale_x)/scale_x}, 0) scale({scale_x}, 1)' if i==0 else f''}", # сжатие относительно центра
                font_family="GOST type A",
                font_size=font_size_title_block_A3_GOST[i],
                fill="black"
            ))

# INDEX_TEXT_TITLE_BLOCK_A3_GOST = {
#     "part_number": [0, 11], #DEFAULT_PART_NUMBER,
#     "designer": [1], #: DEFAULT_DESIGNER, 
#     "scrutineer": [2], #: DEFAULT_SCRUTINEER, 
#     "supervisor": [4], #: DEFAULT_SUPERVISOR, 
#     "document_controller": [5], #: DEFAULT_DOCUMENT_CONTROLLER, 
#     "confirmer": [6], #: DEFAULT_CONFIRMER, 
#     "letter_code_left": [7], #: DEFAULT_LETTER_CODE_LEFT, 
#     "letter_code_centr": [3], #: DEFAULT_LETTER_CODE_CENTR,
#     "current_sheets": [8], #: DEFAULT_CURRENT_SHEETS, 
#     "weight": [9], #: DEFAULT_WEIGHT, 
#     "scale": [38], #: DEFAULT_SCALE, 
#     "all_sheets": [39], #: DEFAULT_ALL_SHEETS, 
#     "component_identification": [40], #: DEFAULT_COMPONENT_IDENTIFICATION, 
#     "material": [41], #: DEFAULT_MATERIAL
# }

            
