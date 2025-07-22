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

    # Track missing page data per language for skeleton
    missing_pages = {}

    for lang_code, lang_data in all_content.items():
        print(f"\n🌐 Generating pages for language: '{lang_code}'...")
        lang_dir = os.path.join(OUTPUT_DIR, lang_code)
        os.makedirs(lang_dir, exist_ok=True)
        missing_pages[lang_code] = []

        # Build site context
        site_context = {k.replace('site_', ''): v for k, v in lang_data.items() if k.startswith('site_')}
        if not site_context:
            site_context = dict(lang_data)

        # Prepare global sections
        globals_ctx = {key: lang_data.get(key, {}) for key in [
            'assets', 'navigation', 'colors', 'layout', 'security', 'footer'
        ]}

        for template_filename in template_files:
            page_key = template_filename.replace('_template.html', '')
            output_file = f"{page_key}.html"

            # Gather or build page data
            page_data = lang_data.get(page_key) or lang_data.get(f"{page_key}_page")
            if not page_data:
                prefix = f"{page_key}_"
                collected = {k[len(prefix):]: v for k, v in lang_data.items() if k.startswith(prefix)}
                page_data = collected or None

            if not page_data:
                print(f"  ⚠ Skipping '{output_file}' - no data.")
                # record skeleton for this missing page
                missing_pages[lang_code].append(page_key)
                continue

            # Build context for rendering
            context = {
                'site': site_context,
                'page': page_data,
                page_key: page_data,
                f"{page_key}_page": page_data,
                'content': page_data,
                **globals_ctx
            }
            # Solar-specific data context
            if 'solar_data' in lang_data:
                sd = lang_data['solar_data']
            elif 'books' in page_data:
                sd = {'books': page_data['books']}
            else:
                sd = {'books': lang_data.get('books', {})}
            context['solar_data'] = sd
            context['books'] = sd.get('books', {})

            # Legacy alias
            if page_key == 'solar_oven':
                context['solar_cooking'] = page_data

            # Render and write
            tpl = env.get_template(template_filename)
            out_html = tpl.render(**context)
            out_path = os.path.join(lang_dir, output_file)
            with open(out_path, 'w', encoding='utf-8') as f:
                f.write(out_html)
            print(f"  ✅ Created: {out_path}")

    # After generation, print skeleton for missing pages
    skeleton = {}
    for lang, pages in missing_pages.items():
        if not pages:
            continue
        skeleton[lang] = {}
        for key in pages:
            skeleton[lang][key] = {
                "title": "<Title>",
                "intro": "<Intro text>",
                # video list in standard format
                f"{key}_videos": [
                    {
                        "title": "<Video Title>",
                        "description": "<Description>",
                        "video_link": "<YouTube URL>",
                        "transcription_link": "<Transcription URL>",
                        "check_data_link": "<Video URL>"
                    }
                ],
                # placeholder for other page-specific content
                "content": []
            }
    if skeleton:
        print("\n⚙️ Missing page data skeleton:\n")
        print(json.dumps(skeleton, indent=2, ensure_ascii=False))

    print(f"\n🎉 Generation complete! Check '{OUTPUT_DIR}'.")


def build_schema():
    """Outputs full skeleton JSON structure for all templates and globals."""
    schema = {}
    template_files = [fname for fname in os.listdir(TEMPLATES_DIR)
                      if fname.endswith('_template.html')]
    page_keys = [fname.replace('_template.html', '') for fname in template_files]

    # default placeholder languages
    for lang in ['en', 'sp']:
        schema[lang] = {}
        # site globals
        schema[lang]['site_name'] = "Your site name"
        # per-page skeletons
        for key in page_keys:
            schema[lang][key] = {
                "title": f"{key.title()} Title",
                "intro": "<Intro text>",
                f"{key}_videos": [
                    {
                        "title": "<Video Title>",
                        "description": "<Description>",
                        "video_link": "<YouTube URL>",
                        "transcription_link": "<Transcription URL>",
                        "check_data_link": "<Video URL>"
                    }
                ],
                "content": []
            }
        # optional global sections
        for section in ['assets', 'navigation', 'colors', 'layout', 'security', 'footer']:
            schema[lang][section] = {}
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

