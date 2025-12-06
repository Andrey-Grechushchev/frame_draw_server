# generate_drawing.py
# UTC+5: 2025-05-10 15:35 — подключен отдельный модуль для рисования рамки

import svgwrite 
import cairosvg
from configs.config_log import logger
from utils.utils_core import save_svg_if_enabled, open_svg_in_browser_and_cleanup
from configs.config import (
    DEBUG, ALL_BLOCKS,
    DEFAULT_VALUES_TITLE_BLOCK,
    DEFAULT_VALUES_DRAWING,
    DEFAULT_VALUES_FILENAME
)

from drawers.drawer_title_block import draw_title_block  # <-- подключаем новую функцию
from drawers.drawer_dimenstions import draw_grid, draw_dimension, add_arrow_markers, draw_note # <-- подключаем новую функцию
from drawers.drawer_table import draw_table
from drawers.drawer_views import draw_views
from font_embedder import add_fonts
from frame_calculations import (add_generated_part_number, add_count_of_rings, add_calc_weight, add_calc_frame_layout,
                                add_material_as_wire_material, add_bottom_diameter, add_scale_on_title_block)
   

def generate_pdf(svg_path=None, pdf_path=None, values=None, disable_svg_debug=False, save_pdf=False, draw_debug_grid=False, queue=None):
    """
    Генерирует PDF-файл чертежа детали на основе входных параметров.

        Функция выполняет следующие этапы:
        1. Объединяет значения по умолчанию с переданными пользователем.
        2. Добавляет вычисляемые параметры, такие как масса, обозначение, количество колец и материал.
        3. Создаёт чертёж в формате SVG с указанием размера листа (A3) и всех необходимых элементов (рамка, виды, таблицы, примечания).
        4. При необходимости сохраняет SVG-файл для отладки.
        5. Преобразует SVG в PDF с помощью CairoSVG.
        6. Возвращает результат через очередь, если она задана (например, при запуске в отдельном процессе).

        Аргументы:
            svg_path (str, optional): Путь для сохранения промежуточного SVG-файла (если не отключена отладка).
            pdf_path (str): Путь, по которому будет сохранён итоговый PDF-файл.
            values (dict, optional): Пользовательские параметры, влияющие на чертёж (например, размеры, текст, маркировка).
            disable_svg_debug (bool): Если True — SVG-файл не сохраняется для отладки.
            save_pdf (bool): Если True — PDF будет сохранён (используется даже в режиме отладки).
            draw_debug_grid (bool): Если True — добавляется вспомогательная размерная сетка в SVG.
            queue (multiprocessing.Queue, optional): Очередь для передачи результата выполнения (успех или ошибка) при запуске в отдельном процессе.

        Возвращает:
            None. Но результат (успешное завершение или ошибка) может быть помещён в очередь, если она передана.

        Примечания:
            - Размер чертежа задаётся в миллиметрах (A3: 420 мм × 297 мм), но внутренний viewBox используется в пикселях (1587.48 × 1122.56).
            - Используется масштабное соответствие: 1 pt = 1.333... px.
            - CairoSVG используется для преобразования SVG в PDF; в некоторых средах (особенно на Windows) рекомендуется запускать в отдельном процессе из-за проблем с GDI.

        Исключения:
            В случае ошибки генерации SVG или PDF выбрасывается исключение с текстом ошибки. Дополнительно ошибка может быть передана в очередь.
    """
    '''
    Значения для рамки в пунктах (pt), размеры на всплывашке в просмотровщике SVG в пикселях (px)
    пункт (pt) = 1/72 дюйма
    1 дюйм = 96 пикселей
    1 pt = 96 / 72 = 1.333... px (строим/пишем 100pt, видим 133,33px)
    Но из-за 
    dwg = svgwrite.Drawing(size=("1190.64pt", "841.92pt"))
    dwg.attribs['viewBox']="0 0 1190.64 841.92"
    У нас всё масштабируется на экране в 1,333 (1 pt = 96 px / 72 pt = 1.333... px)
    И если теперь указать размерность для элемента pt, то он переведётся в px (*1,333) и потом на экране увидим ещё и масштабирование (*1,333). 
    Итого 1,777 на экране. Но зато при печати всё будет корректно отображаться в размерах.   
    '''
    
    # Изменяем словарь с формы {key: (label_text, default_value)} на форму {key: default_value}
    default_values = {key: value[1] for key, value in ALL_BLOCKS.items()}
    
    # Объединяем с введёнными значениями из формы ввода данных
    combined_values = {**default_values, **(values or {})}
    
    logger.info(f"Запуск рассчётов...")

    # Добавляем кол-во колец в изделии без замков
    add_count_of_rings(combined_values)
    
    # Добавляем расчётное количество колец в каждом сегменте каркаса и длины каждого сегмента
    add_calc_frame_layout(combined_values)

    # Дабавляем значение диаметра донышка
    add_bottom_diameter(combined_values)

    # Добавляем сгененрированное обозначения изделия
    add_generated_part_number(combined_values)

    # Добавляем рассчётную массу
    add_calc_weight(combined_values)

    # Добавляем изменённое значение масштаба для 2-х и 3-х составных каркасов
    add_scale_on_title_block(combined_values)
    
    # Добавляем материал как материал проволоки
    add_material_as_wire_material(combined_values)

    # logger.debug(f"Используемые значения: {combined_values}")

      # Создание SVG в памяти        
    try:
        # dwg = svgwrite.Drawing(size=("1190.64pt", "841.92pt"), profile='full')
        dwg = svgwrite.Drawing(size=("420mm", "297mm"), profile='full')
        dwg.attribs['overflow'] = 'visible'
        # dwg.attribs['viewBox'] = "0 0 420 297"
        dwg.attribs['viewBox'] = "0 0 1587.48 1122.56"
        
        """
        px	пиксели (по умолчанию)
        mm	миллиметры
        cm	сантиметры
        in	дюймы
        pt	пункты (1 pt = 1/72 in)
        pc	пика (1 pc = 12 pt)
        %
        
        """

        
        add_fonts(dwg)

        # Добавляем стрелку маркера
        add_arrow_markers(dwg)
        
        if draw_debug_grid:
            draw_grid(dwg) # размерная сетка

        draw_note(dwg) # примечания
        
        draw_title_block(dwg, combined_values, default_values) # <-- вызов отдельного модуля для рамки

        draw_table(dwg, combined_values)# <-- вызов отдельного модуля для таблички

        draw_views(dwg, combined_values)# <-- вызов отдельного модуля для чертёжных видов

        # Сохраняем SVG файл, если не отключено disable_svg_debug
        # save_svg_if_enabled(dwg, disable_svg_debug, svg_path)

        # Получаем SVG как строку для PDF генерации
        # logger.debug(f"SVG файл выглядит так: {dwg.tostring()}")
        svg_string = dwg.tostring()

        # Cохраняем, открываем и потом (через 5 сек) удаляем временный SVG-файл
        open_svg_in_browser_and_cleanup(svg_string, disable_svg_debug)
        
    except Exception as e:
        logger.error(f"Ошибка при создании SVG: {e}")
        raise Exception(f"Ошибка при генерации чертежа: {e}")

    if not DEBUG or save_pdf:
        # Преобразование SVG → PDF через CairoSVG
        try:
            cairosvg.svg2pdf(bytestring=svg_string.encode("utf-8"), write_to=pdf_path)
            if queue is not None:
                queue.put({"status": "OK", "path": pdf_path})
            logger.info(f"PDF файл успешно создан: {pdf_path}")   
        except Exception as e:
            if queue is not None:
                import traceback
                queue.put({
                    "status": "error",
                    "message": str(e),
                    "trace": traceback.format_exc()
                })
            logger.error(f"Ошибка при генерации PDF: {e}")
            raise Exception(f"Ошибка при создании PDF: {e}")
            


