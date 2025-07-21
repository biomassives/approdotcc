import os
import json

TEMPLATES = {
    "soakpit.html": "templates/soakpit_template.html",
    "mycelium_use.html": "templates/mycelium_template.html"
}

OUTPUT_DIR = "output"
CONTENT_PATH = "content.json"

def render_template(template_str, values):
    for key, val in values.items():
        template_str = template_str.replace(f"{{{{ {key} }}}}", val)
    return template_str

def generate_pages():
    with open(CONTENT_PATH, 'r', encoding='utf-8') as f:
        content = json.load(f)

    for lang_code, translations in content.items():
        lang_dir = os.path.join(OUTPUT_DIR, lang_code)
        os.makedirs(lang_dir, exist_ok=True)

        for filename, template_path in TEMPLATES.items():
            with open(template_path, 'r', encoding='utf-8') as f:
                template = f.read()
            output = render_template(template, translations)

            output_path = os.path.join(lang_dir, filename)
            with open(output_path, 'w', encoding='utf-8') as out_f:
                out_f.write(output)
                print(f"✅ Created: {output_path}")

if __name__ == "__main__":
    generate_pages()

