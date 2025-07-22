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
CONTENT_PATH = "content2.json"



def generate_pages(all_content):
    """Main page generation function using the new config/pages structure."""
    env = Environment(loader=FileSystemLoader(TEMPLATES_DIR), autoescape=True)
    template_files = [fname for fname in os.listdir(TEMPLATES_DIR) if fname.endswith('_template.html')]

    missing_page_skeletons = {}

    for lang_code, lang_data in all_content.items():
        print(f"\n🌐 Generating pages for language: '{lang_code}'...")
        lang_dir = os.path.join(OUTPUT_DIR, lang_code)
        os.makedirs(lang_dir, exist_ok=True)

        # --- NEW: Separate config and pages data from the JSON ---
        config_data = lang_data.get('config', {})
        pages_list = lang_data.get('pages', [])
        # Convert the list of pages into a dictionary keyed by 'slug' for easy lookup
        pages_by_slug = {p.get('slug'): p for p in pages_list}

        for template_filename in template_files:
            # The page key is derived from the template name, e.g., "soakpit"
            page_key = template_filename.replace('_template.html', '')
            output_file = f"{page_key}.html"

            # --- REVISED: Simplified data lookup ---
            # Find the page data from our new pages_by_slug dictionary
            page_data = pages_by_slug.get(page_key)

            if not page_data:
                print(f"  ⚠ Skipping '{output_file}' - no data found for slug '{page_key}'.")
                # Logic to handle missing page skeleton can be added here if needed
                continue

            # --- REVISED: Cleaned up context for the template ---
            # We now pass the clean config and page objects to the template
            context = {
                'config': config_data,
                'page': page_data,
                'lang': lang_code
            }

            # Render and write the page
            tpl = env.get_template(template_filename)
            out_html = tpl.render(**context)
            out_path = os.path.join(lang_dir, output_file)
            with open(out_path, 'w', encoding='utf-8') as f:
                f.write(out_html)
            print(f"  ✅ Created: {out_path}")

    # You can add back the skeleton generation logic here if you still need it
    # ...

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

