#!/usr/bin/env python3
"""
Enhanced Page Generator for Appro Community Connector
Supports solar cooker interactive books with lattice security
"""

import os
import json
from typing import Dict, Any
import uuid
from datetime import datetime

# Template mappings
TEMPLATES = {
    "soakpit.html": "templates/soakpit_template.html",
    "mycelium_use.html": "templates/mycelium_template.html",
    "solar_cooker.html": "templates/solar_cooker_template.html"  # New template
}

# Configuration
OUTPUT_DIR = "output"
CONTENT_PATH = "content.json"
ASSETS_PATH = "assets"

class LatticeSecurityGenerator:
    """Generates lattice security tokens and configurations"""
    
    def __init__(self):
        self.session_id = str(uuid.uuid4())
        self.timestamp = datetime.now().isoformat()
    
    def generate_security_context(self, lang_code: str, page_type: str) -> Dict[str, Any]:
        """Generate security context for lattice integration"""
        return {
            "lattice_session_id": self.session_id,
            "lattice_timestamp": self.timestamp,
            "lattice_lang": lang_code,
            "lattice_page_type": page_type,
            "lattice_domain": "hub.approvideo.org",
            "lattice_security_level": "community-verified"
        }

def render_template(template_str: str, values: Dict[str, Any]) -> str:
    """Enhanced template renderer with nested object support"""
    
    def replace_nested(template: str, data: Dict[str, Any], prefix: str = "") -> str:
        """Recursively replace nested placeholders"""
        for key, val in data.items():
            full_key = f"{prefix}{key}" if prefix else key
            placeholder = f"{{{{ {full_key} }}}}"
            
            if isinstance(val, dict):
                # Handle nested objects
                template = replace_nested(template, val, f"{full_key}.")
            elif isinstance(val, list):
                # Handle arrays (for videos, slides, etc.)
                if val and isinstance(val[0], dict):
                    # Array of objects - convert to JSON for JavaScript
                    json_str = json.dumps(val, ensure_ascii=False)
                    template = template.replace(placeholder, json_str)
                else:
                    # Simple array - join with separator
                    template = template.replace(placeholder, ", ".join(map(str, val)))
            else:
                # Simple value replacement
                replacement = str(val) if val is not None else ""
                template = template.replace(placeholder, replacement)
        
        return template
    
    return replace_nested(template_str, values)

def generate_solar_book_data(lang_content: Dict[str, Any]) -> str:
    """Generate JavaScript object for solar book data"""
    
    # Get solar-specific content or use defaults
    solar_content = lang_content.get('solar_cooker', {})
    
    book_data = {
        "metadata": {
            "version": "1.0.0",
            "domain": "hub.approvideo.org",
            "latticeSecured": True,
            "lastUpdated": datetime.now().isoformat(),
            "language": lang_content.get('lang', 'en')
        },
        "books": {
            "foundations": solar_content.get('foundations_slides', []),
            "techniques": solar_content.get('techniques_slides', []),
            "impact": solar_content.get('impact_slides', [])
        }
    }
    
    return json.dumps(book_data, ensure_ascii=False, indent=2)

def enhance_content_with_solar(content: Dict[str, Any]) -> Dict[str, Any]:
    """Add solar cooker data and enhanced features to content"""
    
    lattice_gen = LatticeSecurityGenerator()
    
    for lang_code, lang_content in content.items():
        # Add security context
        security_context = lattice_gen.generate_security_context(lang_code, "solar_cooker")
        lang_content.update(security_context)
        
        # Generate solar book data for JavaScript
        lang_content['solar_book_data_js'] = generate_solar_book_data(lang_content)
        
        # Add asset paths
        lang_content.update({
            'assets_tailwind_js': '/js/tailwind-3.4.16.es',
            'assets_flowbite_js': '/js/flowbite.min.js',
            'assets_flowbite_cdn': 'https://cdnjs.cloudflare.com/ajax/libs/flowbite/2.2.0/flowbite.min.js',
            'assets_main_css': '/style.css',
            'assets_favicon': '/favicon.ico',
            'assets_logo_image': '/images/favicon.webp',
            'site_domain': 'hub.approvideo.org',
            'site_name': 'Appro Community Connector',
            'site_short_name': 'Appro C C'
        })
        
        # Add color scheme
        lang_content.update({
            'color_header_bg': 'emerald-600',
            'color_section_header': 'yellow-600',
            'color_accent': '#d97706',
            'color_security': '#10b981'
        })
    
    return content

def generate_pages():
    """Main page generation function"""
    
    # Load content
    print("📂 Loading content...")
    with open(CONTENT_PATH, 'r', encoding='utf-8') as f:
        content = json.load(f)
    
    # Enhance content with solar cooker data
    print("🔒 Enhancing content with lattice security...")
    content = enhance_content_with_solar(content)
    
    # Generate pages for each language
    for lang_code, translations in content.items():
        print(f"\n🌐 Generating pages for language: {lang_code}")
        
        lang_dir = os.path.join(OUTPUT_DIR, lang_code)
        os.makedirs(lang_dir, exist_ok=True)
        
        # Generate each template
        for filename, template_path in TEMPLATES.items():
            print(f"  📝 Processing {filename}...")
            
            try:
                # Load template
                with open(template_path, 'r', encoding='utf-8') as f:
                    template = f.read()
                
                # Render template
                output = render_template(template, translations)
                
                # Write output
                output_path = os.path.join(lang_dir, filename)
                with open(output_path, 'w', encoding='utf-8') as out_f:
                    out_f.write(output)
                
                print(f"  ✅ Created: {output_path}")
                
            except FileNotFoundError:
                print(f"  ⚠️  Template not found: {template_path}")
            except Exception as e:
                print(f"  ❌ Error processing {filename}: {str(e)}")
    
    print(f"\n🎉 Page generation complete! Files created in '{OUTPUT_DIR}/' directory")

def validate_content_structure():
    """Validate that content.json has required structure"""
    
    try:
        with open(CONTENT_PATH, 'r', encoding='utf-8') as f:
            content = json.load(f)
        
        required_languages = ['en']  # Minimum required
        missing_languages = []
        
        for lang in required_languages:
            if lang not in content:
                missing_languages.append(lang)
        
        if missing_languages:
            print(f"⚠️  Missing required languages: {missing_languages}")
            return False
        
        print("✅ Content structure validation passed")
        return True
        
    except FileNotFoundError:
        print(f"❌ Content file not found: {CONTENT_PATH}")
        return False
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON in content file: {str(e)}")
        return False

def create_example_templates():
    """Create example template files if they don't exist"""
    
    templates_dir = "templates"
    os.makedirs(templates_dir, exist_ok=True)
    
    # Solar cooker template example
    solar_template_path = os.path.join(templates_dir, "solar_cooker_template.html")
    
    if not os.path.exists(solar_template_path):
        print(f"📋 Creating example template: {solar_template_path}")
        
        example_template = '''<!DOCTYPE html>
<html lang="{{ lang }}">
<head>
    <meta charset="UTF-8">
    <title>{{ solar_cooker.title }} - {{ site_name }}</title>
    <!-- Add your meta tags and CSS here -->
</head>
<body>
    <h1>{{ solar_cooker.title }}</h1>
    <p>{{ solar_cooker.intro }}</p>
    
    <!-- Solar book data will be injected here -->
    <script>
        const solarBookData = {{ solar_book_data_js }};
        // Your JavaScript code here
    </script>
</body>
</html>'''
        
        with open(solar_template_path, 'w', encoding='utf-8') as f:
            f.write(example_template)

if __name__ == "__main__":
    print("🚀 Appro Community Connector - Page Generator")
    print("=" * 50)
    
    # Validate content structure
    if not validate_content_structure():
        print("❌ Content validation failed. Please fix issues before proceeding.")
        exit(1)
    
    # Create example templates if needed
    create_example_templates()
    
    # Generate pages
    generate_pages()
    
    print("\n💡 Next steps:")
    print("  1. Review generated files in 'output/' directory")
    print("  2. Test solar cooker interactive books")
    print("  3. Verify lattice security integration")
    print("  4. Deploy to hub.approvideo.org")
