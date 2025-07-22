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

import json

data = {
    "lang": "en",
    "site_name": "Appropriate Technology Hub",
    "site_short_name": "Appro-Tech",
    "site_domain": "appro-tech.org",
    "color_header_bg": "yellow-600",
    "color_security": "#f59e0b",
    "assets_tailwind_js": "https://cdn.tailwindcss.com",
    "assets_flowbite_js": "https://unpkg.com/flowbite@1.4.7/dist/flowbite.js",
    "assets_flowbite_cdn": "https://cdnjs.cloudflare.com/ajax/libs/flowbite/1.6.5/flowbite.min.js",
    "assets_main_css": "/styles/main.css",
    "assets_logo_image": "/images/logo-solar-oven.png",
    "assets_favicon": "/images/favicon-solar.png",
    "lattice_security_level": "High",
    "lattice_session_id": "session_xyz_789",
    "solar_cooking": {
        "title": "The Evolution of Solar Cooking",
        "hero_image": "/images/solar-oven-hero.png",
        "hero_alt": "Modern Solar Oven with a Cardboard Reflector",
        "hero_title": "Solar Cooking: From Heavy Boxes to Portable Powerhouses",
        "tip_text": "A simple, well-designed cardboard reflector can significantly boost a solar oven's efficiency and cooking temperature.",
        "books": {
            "history": {
                "title": "A Brief History of Solar Ovens",
                "slides": [
                    {
                        "title": "Early Innovations",
                        "content": "<p>The concept of harnessing the sun's energy for cooking dates back to the 18th century with Horace-Bénédict de Saussure's 'hot box.' These initial designs were simple insulated boxes with a glass top to effectively trap heat.</p><div class='historical-note'>These pioneering ovens could achieve temperatures sufficient for cooking fruits and slow-cooking other foods.</div>"
                    },
                    {
                        "title": "Mid-20th Century Designs",
                        "content": "<p>The 1950s saw a resurgence in solar cooking interest, with innovators like Maria Telkes developing more practical and efficient designs. However, these models were often bulky and constructed from heavy materials like wood and glass, limiting their portability.</p>"
                    },
                    {
                        "title": "The Rise of Lightweight Panel Cookers",
                        "content": "<p>In the 1990s, panel cookers such as the 'CooKit' became popular. These were lightweight and foldable, made from cardboard and aluminum foil. This design made them highly accessible for communities in developing nations.</p>"
                    }
                ]
            },
            "evolution": {
                "title": "The EWB Solar Oven Evolution",
                "slides": [
                    {
                        "title": "Classic EWB Solar Ovens",
                        "content": "<p>Engineers Without Borders (EWB) has been instrumental in promoting various solar oven designs. Early successful models were highly effective but often required durable and less portable materials to achieve high temperatures for safe cooking and water pasteurization.</p>"
                    },
                    {
                        "title": "The Demand for Portability and Durability",
                        "content": "<p>Field experience revealed that for many users, particularly in nomadic or refugee communities, portability and durability were paramount. Heavy wooden boxes were difficult to move, and glass components were prone to breaking during transport.</p>"
                    },
                    {
                        "title": "The Cardboard Reflector Innovation",
                        "content": "<p>A significant evolution in solar oven design was the adoption of a large, foldable cardboard reflector. This innovation merges the low cost and light weight of panel cookers with the superior heat-trapping efficiency of box ovens.</p><ul><li><b>Durable:</b> Laminated or specially treated cardboard offers surprising resistance to weather.</li><li><b>Movable:</b> The entire oven, including the reflector, can be folded flat, making it exceptionally easy to transport.</li><li><b>Efficient:</b> The large reflector panel concentrates a greater amount of sunlight, significantly increasing the oven's cooking temperatures.</li></ul>"
                    }
                ]
            },
            "diy": {
                "title": "Build Your Own Solar Oven",
                "slides": [
                    {
                        "title": "Essential Materials",
                        "content": "<p>You can construct a durable and movable solar oven using readily available materials:</p><ul><li>Two cardboard boxes, with one fitting inside the other.</li><li>A large piece of cardboard for the main reflector panel.</li><li>Standard aluminum foil.</li><li>Non-toxic black paint for heat absorption.</li><li>Glue or another suitable adhesive.</li><li>A turkey-sized oven bag or a pane of glass/plexiglass for the lid.</li></ul>"
                    },
                    {
                        "title": "Fundamental Construction Steps",
                        "content": "<p>1. Place the smaller box inside the larger one, using crumpled newspaper to insulate the gap between them.</p><p>2. Line the interior of the smaller box and the large reflector panel with aluminum foil, ensuring the shiny side is out.</p><p>3. Paint a dark-colored pot black to maximize heat absorption.</p><p>4. Fashion a lid using the oven bag or glass to create a greenhouse effect, trapping heat inside.</p><p>5. Attach the reflector panel to the box at an angle to effectively direct sunlight into the cooking chamber.</p>"
                    },
                    {
                        "title": "Tips for Maximum Performance",
                        "content": "<p>For optimal results, orient your oven to face the sun and adjust its position approximately every hour. Utilize a dark, lightweight pot with a secure lid to enhance heat absorption. The cardboard reflector is the key component for achieving higher temperatures more rapidly.</p>"
                    }
                ]
            }
        },
        "community_impact": {
            "title": "Community Empowerment Through Solar Cooking",
            "description": "Durable, movable solar ovens empower communities by offering a low-cost, fuel-free method for cooking food and pasteurizing water. This reduces dependence on firewood, which in turn helps to combat deforestation and lessens the time-consuming burden of fuel collection, often carried out by women and children.",
            "examples": "In various settings, from refugee camps to rural villages, these ovens contribute to improved health, create more time for education and economic pursuits, and enhance overall safety."
        },
        "innovation": {
            "icon": "💡",
            "title": "Continuing Innovation in Solar Technology",
            "description": "The evolution of solar cooking is ongoing, with research focused on developing better materials for heat retention and reflectivity. New designs aim to be even easier to assemble and transport, with a continued emphasis on appropriate technology—solutions that are effective, affordable, and locally sustainable."
        },
        "advanced": {
            "title": "The Technical Aspects of Solar Cooking",
            "description": "The design of a solar oven leverages fundamental physics: the greenhouse effect is used to trap infrared radiation, while parabolic reflection concentrates sunlight onto the cooking vessel. The use of a cardboard reflector is a prime example of applying low-tech materials to achieve high-tech results.",
            "historical_note": "The core principles remain the same as those of de Saussure's original 'hot box,' but have been significantly optimized for portability and performance through the use of modern, accessible materials."
        }
    }
}

# This dictionary would be passed to the template rendering function.
# The 'books' data is converted to a JSON string to be safely embedded in a script tag.
data["solar_book_data_js"] = json.dumps(data["solar_cooking"]["books"])





# Template mappings
TEMPLATES = {
    "soakpit.html": "templates/soakpit_template.html",
    "mycelium_use.html": "templates/mycelium_template.html",
    "solar_cooker.html": "templates/solar_cooker_template.html",
    "water_security.html": "templates/water_security_template.html"  # New water template
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
