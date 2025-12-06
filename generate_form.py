from configs.config import FORM_SECTIONS, checkbox_fields, dropdown_fields, numeric_fields, linked_checkboxes
from dependencies import DEPENDENT_FIELDS
import os

HTML_START = '''<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <title>Форма ввода</title>
    <style>
        label { display: block; margin-top: 10px; }
        input, select { width: 300px; padding: 5px; }
        fieldset { margin-bottom: 20px; padding: 10px; }
    </style>
</head>
<body>
    <form id="form">
'''

HTML_END = '''
        <br><br>
        <button type="submit">Сгенерировать</button>
    </form>

    <script>
        const DEPENDENCIES = %s;

        function updateDependencies() {
            for (const [source, info] of Object.entries(DEPENDENCIES)) {
                const sourceValue = document.getElementById(source)?.value;
                for (const expr of info.conditions) {
                    let conditionResult = false;
                    try {
                        const context = {};
                        for (const el of document.getElementById("form").elements) {
                            if (el.id) context[el.id] = el.type === 'checkbox' ? el.checked : el.value;
                        }
                        conditionResult = Function("with(this) { return (" + expr.expression + ") }").call(context);
                    } catch (e) {}

                    for (const affected of info.affects) {
                        const field = document.getElementById(affected);
                        if (field) field.disabled = conditionResult;
                    }
                }
            }
        }

        document.getElementById("form").addEventListener("input", updateDependencies);
        window.addEventListener("DOMContentLoaded", updateDependencies);
    </script>
</body>
</html>
''' % repr(DEPENDENT_FIELDS)


def generate_html():
    html = [HTML_START]

    for section_name, section_fields in FORM_SECTIONS.items():
        html.append(f'<fieldset><legend><strong>{section_name}</strong></legend>')
        for key, (label, default, *_rest) in section_fields.items():
            html.append(f'<label for="{key}">{label}</label>')

            if key in checkbox_fields:
                checked = 'checked' if default == checkbox_fields[key] else ''
                html.append(f'<input type="checkbox" id="{key}" name="{key}" {checked}>')

            elif key in dropdown_fields:
                html.append(f'<select id="{key}" name="{key}">')
                for option in dropdown_fields[key]:
                    selected = 'selected' if str(option) == str(default) else ''
                    html.append(f'<option value="{option}" {selected}>{option}</option>')
                html.append('</select>')

            else:
                input_type = "number" if key in numeric_fields else "text"
                html.append(f'<input type="{input_type}" id="{key}" name="{key}" value="{default}">')

        html.append('</fieldset>')

    html.append(HTML_END)
    return "\n".join(html)


def write_to_file(filepath="templates/form.html"):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(generate_html())
    print(f"HTML-форма успешно сохранена в {filepath}")


if __name__ == "__main__":
    write_to_file()
