#!/usr/bin/env python3
"""
Page Generator for Appro Community Connector
- Uses Jinja2 for robust templating to handle complex data and logic.
- Centralizes all content and configuration in content.json.
- Dynamically detects templates to support adding new pages without code changes.
"""

import os
import json
from jinja2 import Environment, FileSystemLoader

# --- Configuration ---
TEMPLATES_DIR = "templates"
OUTPUT_DIR = "output"
CONTENT_PATH = "content.json"


def generate_pages():
    """Main page generation function using the Jinja2 library."""
    # Initialize Jinja2 environment
    print(f"🔎 Initializing Jinja2 environment from './{TEMPLATES_DIR}'...")
    env = Environment(loader=FileSystemLoader(TEMPLATES_DIR), autoescape=True)

    # Load content
    print(f"📂 Loading all content from '{CONTENT_PATH}'...")
    with open(CONTENT_PATH, 'r', encoding='utf-8') as f:
        all_content = json.load(f)

    # Discover all template files
    template_files = [fname for fname in os.listdir(TEMPLATES_DIR)
                      if fname.endswith('_template.html')]

    # Generate pages for each language
    for lang_code, data_for_lang in all_content.items():
        print(f"\n🌐 Generating pages for language: '{lang_code}'")
        lang_dir = os.path.join(OUTPUT_DIR, lang_code)
        os.makedirs(lang_dir, exist_ok=True)

        for template_filename in template_files:
            # Derive output filename by stripping suffix
            output_filename = template_filename.replace('_template.html', '.html')
            print(f"  📝 Rendering '{output_filename}' using '{template_filename}'...")
            try:
                template = env.get_template(template_filename)
                output_html = template.render(**data_for_lang)

                # Write output
                output_path = os.path.join(lang_dir, output_filename)
                with open(output_path, 'w', encoding='utf-8') as out_f:
                    out_f.write(output_html)

                print(f"  ✅ Created: {output_path}")

            except Exception as e:
                print(f"  ❌ Error processing {template_filename}: {e}")

    print(f"\n🎉 Page generation complete! Files are in the '{OUTPUT_DIR}/' directory.")


if __name__ == "__main__":
    print("🚀 Appro Community Connector - Page Generator")
    print("=" * 50)
    generate_pages()

