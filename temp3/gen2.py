#!/usr/bin/env python3
"""
Page Generator for Appro Community Connector
- Uses Jinja2 for robust templating to handle complex data and logic.
- Centralizes all content and configuration in content.json.
- Dynamically detects templates to support adding new pages without code changes.
- Can output a skeleton data object JSON for missing pages to help users build content.
"""

import os
import json
import argparse
from jinja2 import Environment, FileSystemLoader

# --- Configuration ---
TEMPLATES_DIR = "templates"
OUTPUT_DIR = "output"
CONTENT_PATH = "content.json"


def generate_pages(all_content):
    """Main page generation function using the Jinja2 library."""
    env = Environment(loader=FileSystemLoader(TEMPLATES_DIR), autoescape=True)
    template_files = [fname for fname in os.listdir(TEMPLATES_DIR)
                      if fname.endswith('_template.html')]

    for lang_code, lang_data in all_content.items():
        print(f"\n🌐 Generating pages for language: '{lang_code}'...")
        lang_dir = os.path.join(OUTPUT_DIR, lang_code)
        os.makedirs(lang_dir, exist_ok=True)

        # Build site context
        site_context = {k.replace('site_', ''): v for k, v in lang_data.items() if k.startswith('site_')}
        if not site_context:
            site_context = dict(lang_data)

        # Prepare globals
        globals_ctx = {key: lang_data.get(key, {}) for key in [
            'assets', 'navigation', 'colors', 'layout', 'security', 'footer'
        ]}

        for template_filename in template_files:
            page_key = template_filename.replace('_template.html', '')
            output_file = f"{page_key}.html"

            # Gather or build page data
            page_data = lang_data.get(page_key) or lang_data.get(f"{page_key}_page")
            if not page_data:
                # attempt to assemble from flat keys
                prefix = f"{page_key}_"
                collected = {k[len(prefix):]: v for k, v in lang_data.items() if k.startswith(prefix)}
                if collected:
                    page_data = collected

            if not page_data:
                print(f"  ⚠ Skipping '{output_file}' - no data. Use --schema to generate a skeleton.")
                continue

            # Build context
            context = {
                'site': site_context,
                'page': page_data,
                page_key: page_data,
                f"{page_key}_page": page_data,
                'content': page_data,
                **globals_ctx
            }
            # Solar-specific data
            if 'solar_data' in lang_data:
                solar_data = lang_data['solar_data']
            elif 'books' in page_data:
                solar_data = {'books': page_data['books']}
            else:
                solar_data = {'books': lang_data.get('books', {})}
            context['solar_data'] = solar_data
            context['books'] = solar_data.get('books', {})

            # Legacy alias
            if page_key == 'solar_oven':
                context['solar_cooking'] = page_data

            # Render
            tpl = env.get_template(template_filename)
            out_html = tpl.render(**context)
            out_path = os.path.join(lang_dir, output_file)
            with open(out_path, 'w', encoding='utf-8') as f:
                f.write(out_html)
            print(f"  ✅ Created: {out_path}")

    print(f"\n🎉 Generation complete! Check '{OUTPUT_DIR}'.")


def build_schema():
    """Outputs skeleton JSON structure for all templates by language."""
    schema = {}
    template_files = [fname for fname in os.listdir(TEMPLATES_DIR)
                      if fname.endswith('_template.html')]
    page_keys = [fname.replace('_template.html', '') for fname in template_files]

    # default languages placeholder
    sample_langs = ['en', 'sp']
    for lang in sample_langs:
        schema[lang] = {}
        # include site placeholders
        schema[lang]['site_name'] = "Your site name"
        # per-page skeletons
        for key in page_keys:
            schema[lang][key] = {"title": f"{key.title()} Title", "intro": "...", "content": []}
        # optional global sections
        schema[lang]['assets'] = {}
        schema[lang]['navigation'] = {}
        schema[lang]['colors'] = {}
        schema[lang]['layout'] = {}
        schema[lang]['security'] = {}
        schema[lang]['footer'] = {}
    print(json.dumps(schema, indent=2, ensure_ascii=False))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Generate pages or output schema')
    parser.add_argument('--schema', action='store_true', help='Print a skeleton JSON for content.json')
    args = parser.parse_args()

    if args.schema:
        build_schema()
    else:
        if not os.path.exists(CONTENT_PATH):
            print(f"Error: '{CONTENT_PATH}' not found.")
        else:
            with open(CONTENT_PATH, 'r', encoding='utf-8') as cf:
                data = json.load(cf)
            generate_pages(data)

