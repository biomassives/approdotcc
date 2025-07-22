#!/usr/bin/env python3
"""
Page Generator for Appro Community Connector
- Uses Jinja2 for robust templating to handle complex data and logic.
- Centralizes all content and configuration in content.json.
"""

import os
import json
from jinja2 import Environment, FileSystemLoader

# --- Configuration ---
# All paths and filenames are defined here for easy changes.
TEMPLATES_DIR = "templates"
OUTPUT_DIR = "output"
CONTENT_PATH = "content.json"

# Maps your final HTML filenames to their template files.
# Add your new complex page here.
TEMPLATES = {
    "solar_cooker.html": "solar_cooker_template.html",
    "biodiversity.html": "biodiversity_template.html" # New complex page
}

def generate_pages():
    """Main page generation function using the Jinja2 library."""
    
    # Set up the Jinja2 environment to find templates in the './templates' folder.
    print(f"🔎 Initializing Jinja2 environment from './{TEMPLATES_DIR}'...")
    env = Environment(loader=FileSystemLoader(TEMPLATES_DIR), autoescape=True)

    # Load all site data from the single source of truth.
    print(f"📂 Loading all content from '{CONTENT_PATH}'...")
    with open(CONTENT_PATH, 'r', encoding='utf-8') as f:
        all_content = json.load(f)

    # Generate pages for each language defined in the content file.
    for lang_code, data_for_lang in all_content.items():
        print(f"\n🌐 Generating pages for language: '{lang_code}'")
        lang_dir = os.path.join(OUTPUT_DIR, lang_code)
        os.makedirs(lang_dir, exist_ok=True)
        
        # Now, render each template defined in the TEMPLATES mapping.
        for output_filename, template_filename in TEMPLATES.items():
            print(f"  📝 Rendering '{output_filename}' using '{template_filename}'...")
            try:
                template = env.get_template(template_filename)
                
                # Pass all data for the current language to the template.
                output_html = template.render(data_for_lang)

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
