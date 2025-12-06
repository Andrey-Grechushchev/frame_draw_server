# dependencies.py

# Главный словарь зависимостей между полями
# Ключ: имя поля-источника (source_field)
# Значение: список правил:
#   {"expression": <строка-выражение>, "affects": [список полей]}
DEPENDENT_FIELDS = {}

def add_dependency(source_field, condition_expr, affected_fields):
    """
    Добавляет правило зависимости между полями формы.

    Если условие condition_expr возвращает True, то поля из affected_fields
    будут отключены (disabled). Если False — эти поля останутся включёнными
    (если никакое другое правило не потребовало их отключить).

    :param source_field: str
        Ключ поля-источника, при изменении которого будет проверяться условие.
        Обычно это имя поля из словаря entries (например, "frame_parts_count",
        "head_type", "bottom_presence" и т.п.).

    :param condition_expr: str
        Выражение на Python, которое возвращает True, если ЗАВИСИМЫЕ поля
        нужно отключить. Выражение выполняется через eval() внутри
        evaluate_expression().

        Внутри condition_expr можно использовать имена ЛЮБЫХ полей формы:
        - source_field (то есть само поле-источник)
        - другие поля, если логика зависит от нескольких значений.

        evaluate_expression() автоматически подставляет текущие значения
        полей из entries/checkbox_vars.

        Примеры выражений:
            "frame_parts_count in ['1', 1]"
                — отключить связанные поля, если количество частей каркаса равно 1

            "bottom_presence in [False, 'нет', 'Нет', 'НЕТ']"
                — отключить зависимые поля, если донышко не выбрано

            "head_type not in ['Раструб']"
                — отключить зависимое поле, если тип оголовка не «Раструб»

            "check1 == True"
                — значение чекбокса check1 установлено

            "mode == 'auto'"
                — поле mode установлено в 'auto' (например, выпадающий список)

            "value in ['нет', False]"
                — значение — «нет» или False (подходит и для чекбоксов, и для строк)

            "int(count) < 3"
                — числовое значение поля count меньше 3

            "not option_enabled"
                — чекбокс option_enabled не установлен

    :param affected_fields: list[str]
        Список ключей полей, которые будут отключены (state='disabled'),
        если условие condition_expr истинно (True).
        Если условие ложно (False) и никаких других правил не требуют
        отключения этих полей, то они будут включены (state='normal' или
        'readonly' для Combobox).

        Примеры:
            ["lock_type"]
            ["bottom_thickness_mm", "bottom_length_mm", "bottom_diameter"]
            ["neck_ring_inner_diameter_presence"]

    ---------------------------------------------
    Как работают несколько правил для одного поля:
    ---------------------------------------------

    Можно добавить несколько зависимостей для одного и того же source_field.
    Например:

        add_dependency(
            "head_type",
            "head_type not in ['Раструб']",
            ["neck_ring_inner_diameter_presence"]
        )

        add_dependency(
            "head_type",
            "head_type in ['Раструб']",
            ["head_type"]
        )

    В DEPENDENT_FIELDS это будет выглядеть так:

        DEPENDENT_FIELDS["head_type"] = [
            {
                "expression": "head_type not in ['Раструб']",
                "affects": ["neck_ring_inner_diameter_presence"],
            },
            {
                "expression": "head_type in ['Раструб']",
                "affects": ["head_type"],
            },
        ]

    handle_dependencies() при изменении head_type:
        1) по каждому правилу считает disable = evaluate_expression(expression)
        2) для всех affected из этого правила накапливает "нужно ли отключить"
           (если хотя бы одно правило даёт True — поле будет disabled)
        3) затем выставляет итоговое состояние для каждого зависимого поля.

    То есть:
        - каждое правило управляет ТОЛЬКО своими полями из affected_fields
        - одно правило больше не "портит" чужие зависимости, как было в старой
          реализации с общими conditions/affects

    Важно:
    - Если condition_expr внутри evaluate_expression вызывает ошибку
      (например, int("") или обращение к несуществующему полю),
      evaluate_expression должна вернуть False, и правило не отключает поля.
    - Проверка зависимости для source_field должна выполняться каждый раз,
      когда значение source_field меняется. Это делает handle_dependencies(),
      который вызывается из биндов (Entry.bind, Combobox.bind, trace_add и т.д.).
    """

    rule = {
        "expression": condition_expr,
        "affects": list(affected_fields),
    }

    rules = DEPENDENT_FIELDS.setdefault(source_field, [])

    # Защита от полного дублирования одного и того же правила
    for existing in rules:
        if (
            existing.get("expression") == rule["expression"]
            and set(existing.get("affects", [])) == set(rule["affects"])
        ):
            return

    rules.append(rule)

# -----------------------------
# Здесь добавляются все зависимости:
# -----------------------------

# Зависимость от количества частей каркаса
add_dependency(
    "frame_parts_count",
    "frame_parts_count in ['1', 1]",
    ["lock_type"]
)

# Зависимости от наличия донышка
add_dependency(
    "bottom_presence",
    "bottom_presence in [False, 'нет', 'Нет', 'НЕТ']",
    [
        "bottom_thickness_mm",
        "bottom_length_mm",
        "bottom_diameter",
        "bottom_diameter",
        # "bottom_diameter_presence"
    ]
)

# Зависимость: если нет выбора диаметра, то отключить поле диаметра
# add_dependency(
#     "bottom_diameter_presence",
#     "bottom_diameter_presence in [False, 'нет', 'Нет', 'НЕТ']",
#     ["bottom_diameter"]
# )

# Если нет выбора длины оголовка, то отключить поле оголовка
add_dependency(
    "neck_length_presence",
    "neck_length_presence in [False, 'нет', 'Нет', 'НЕТ']",
    ["neck_length"]
)


# Если нет выбора длины оголовка, то отключить поле оголовка
add_dependency(
    "last_ring_to_bottom_length_presence",
    "last_ring_to_bottom_length_presence in [False, 'нет', 'Нет', 'НЕТ']",
    ["last_ring_to_bottom_length"]
)


# # Если ни дно, ни диаметр не выбраны, то отключить поле диаметра
# add_dependency(
#     "bottom_diameter",
#     "bottom_presence in [False, 'нет', 'Нет', 'НЕТ'] or bottom_diameter_presence in [False, 'нет', 'Нет', 'НЕТ']", #"bottom_presence in [False, 'нет', 'Нет', 'НЕТ'] or bottom_diameter_presence in [False, 'нет', 'Нет', 'НЕТ']",
#     ["bottom_diameter"]
# )

# Если нет Вентури, то отключаем поля с его упоминанием
add_dependency(
    "venturi_presence",
    "venturi_presence in [False, 'нет', 'Нет', 'НЕТ']",
    [
        "venturi_diameter_mm",
        "venturi_thickness_mm",
    ]
)

# Если есть Вентури, то отключаем поле с выбором внутреннего диаметра раструба
add_dependency(
    "venturi_presence",
    "venturi_presence in [True, 'да', 'Да', 'ДА']",
    ["neck_ring_inner_diameter_presence"]
)

# Если выбираем тип оголовка отличный от Раструба, отключаем переключатель размера внутреннего диаметра кольца раструба
add_dependency(
    "head_type",
    "head_type not in ['Раструб']",
    ["neck_ring_inner_diameter_presence"]
)


# Временные фиксации

# add_dependency(
#     "frame_parts_count",
#     "frame_parts_count in ['1', 1]",
#     ["frame_parts_count"]
# )

add_dependency(
    "head_type",
    "head_type in ['Раструб']",
    ["head_type"]
)

# add_dependency(
#     "venturi_presence",
#     "venturi_presence in [False, 'нет', 'Нет', 'НЕТ']",
#     ["venturi_presence"]
# )