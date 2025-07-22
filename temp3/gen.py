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

    # Load content JSON
    print(f"📂 Loading all content from '{CONTENT_PATH}'...")
    with open(CONTENT_PATH, 'r', encoding='utf-8') as f:
        all_content = json.load(f)

    # Discover all template files
    template_files = [fname for fname in os.listdir(TEMPLATES_DIR)
                      if fname.endswith('_template.html')]

    # Generate pages for each language
    for lang_code, lang_data in all_content.items():
        print(f"\n🌐 Generating pages for language: '{lang_code}'")
        lang_dir = os.path.join(OUTPUT_DIR, lang_code)
        os.makedirs(lang_dir, exist_ok=True)

        # Build site-wide context from 'site_' prefixed keys
        site_context = {k.replace('site_', ''): v for k, v in lang_data.items() if k.startswith('site_')}
        if not site_context:
            site_context = {**lang_data}

        # Prepare globals
        globals_ctx = {key: lang_data.get(key, {}) for key in [
            'assets', 'navigation', 'colors', 'layout', 'security', 'footer'
        ]}

        for template_filename in template_files:
            page_key = template_filename.replace('_template.html', '')
            output_file = f"{page_key}.html"
            print(f"  📝 Rendering '{output_file}' using '{template_filename}'...")

            # Gather page data
            page_data = None
            # direct object
            if page_key in lang_data:
                page_data = lang_data[page_key]
            # page variant
            elif f"{page_key}_page" in lang_data:
                page_data = lang_data[f"{page_key}_page"]
            # flat prefix keys
            else:
                prefix = f"{page_key}_"
                flat = {k[len(prefix):]: v for k, v in lang_data.items() if k.startswith(prefix)}
                if flat:
                    page_data = flat

            if not page_data:
                print(f"  ⚠ Skipping '{output_file}' (no page data found)")
                continue

            # Context assembly
            context = {
                'site': site_context,
                'page': page_data,
                f'{page_key}': page_data,
                f'{page_key}_page': page_data,
                'content': page_data,
                **globals_ctx
            }

            # Special handling for solar book templates
            if 'solar_data' in lang_data:
                solar_data = lang_data['solar_data']
            elif 'books' in page_data:
                solar_data = {'books': page_data['books']}
            else:
                solar_data = {'books': lang_data.get('books', {})}
            context['solar_data'] = solar_data
            context['books'] = solar_data.get('books', {})

            # Legacy aliases
            if page_key == 'solar_oven':
                context['solar_cooking'] = page_data

            try:
                tpl = env.get_template(template_filename)
                output_html = tpl.render(**context)

                with open(os.path.join(lang_dir, output_file), 'w', encoding='utf-8') as outf:
                    outf.write(output_html)
                print(f"  ✅ Created: {lang_code}/{output_file}")

            except Exception as err:
                print(f"  ❌ Error rendering {template_filename}: {err}")

    print(f"\n🎉 Page generation complete! Check '{OUTPUT_DIR}' for output.")

if __name__ == '__main__':
    print("🚀 Appro Community Connector - Page Generator")
    print("=" * 50)
    generate_pages()

