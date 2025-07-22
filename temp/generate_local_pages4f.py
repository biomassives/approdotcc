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
    for lang_code, data_for_lang in all_content.items():
        print(f"\n🌐 Generating pages for language: '{lang_code}'")
        lang_dir = os.path.join(OUTPUT_DIR, lang_code)
        os.makedirs(lang_dir, exist_ok=True)

        # Build site-wide context from any 'site_' prefixed keys
        site_context = {k[len('site_'):]: v for k, v in data_for_lang.items() if k.startswith('site_')}
        if not site_context:
            # Fallback to full language data if no site_ keys
            site_context = data_for_lang

        for template_filename in template_files:
            # Derive page key and output filename
            page_key = template_filename.replace('_template.html', '')
            output_filename = f"{page_key}.html"
            print(f"  📝 Rendering '{output_filename}' using '{template_filename}'...")

            # Page-specific data: direct or '_page' suffix
            page_data = data_for_lang.get(page_key) or data_for_lang.get(f"{page_key}_page") or {}

            # Skip rendering if no data
            if not page_data:
                print(f"  ⚠ Skipping '{output_filename}' (no data found)")
                continue

            # Build Jinja context
            context = {
                'site': site_context,
                page_key: page_data,
                f"{page_key}_page": page_data,
                'page': page_data,
                'content': page_data
            }

            # Inject all global sections (fallback to empty dict)
            for global_key in ['assets', 'navigation', 'colors', 'layout', 'security', 'footer']:
                context[global_key] = data_for_lang.get(global_key, {})

            # Build solar_data and books for solar pages
            if 'solar_data' in data_for_lang:
                solar_data = data_for_lang['solar_data']
            elif 'books' in page_data:
                solar_data = {'books': page_data['books']}
            else:
                solar_data = {'books': data_for_lang.get('books', {})}

            context['solar_data'] = solar_data
            context['books'] = solar_data.get('books', {})

            # Legacy alias for solar_oven templates
            if page_key == 'solar_oven':
                context['solar_cooking'] = page_data

            try:
                template = env.get_template(template_filename)
                rendered = template.render(**context)

                # Write to file
                out_path = os.path.join(lang_dir, output_filename)
                with open(out_path, 'w', encoding='utf-8') as out_f:
                    out_f.write(rendered)
                print(f"  ✅ Created: {out_path}")

            except Exception as e:
                print(f"  ❌ Error processing {template_filename}: {e}")

    print(f"\n🎉 Page generation complete! Files are in '{OUTPUT_DIR}/' directory.")


if __name__ == "__main__":
    print("🚀 Appro Community Connector - Page Generator")
    print("=" * 50)
    generate_pages()

