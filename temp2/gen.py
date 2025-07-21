import os

# Supported languages and labels
languages = {
    "en": "English",
    "vi": "Vietnamese",
    "ar": "Arabic",
    "sw": "Swahili",
    "yo": "Yoruba",
    "am": "Amharic",
    "uk": "Ukrainian",
    "es": "Spanish",
    "ja": "Japanese",
    "qu": "Quechua",
    "sh": "Serbo-Croatian",
    "we": "Wolof",
    "lu": "Luo",
    "ha": "Hausa",
    "fa": "Dari"
}

# Page topics and titles
topics = {
    "waste": "Waste Management",
    "water": "Water Security",
    "solar": "Solar Cooking",
    "briquette": "Fuel Briquette"
}

# HTML Template
template = """<!DOCTYPE html>
<html lang="{lang_code}">
<head>
    <meta charset="UTF-8">
    <title>{title} ({lang_code})</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="stylesheet" href="/style.css">
    <script src="/js/tailwind-3.4.16.es"></script>
</head>
<body class="bg-white text-gray-900">
    <header class="bg-orange-600 text-white p-4 flex justify-between items-center">
        <h1 class="text-xl font-bold"><a href="/">Appro Community Connector</a></h1>
        <div>
            <label for="languageSelect">🌐 Language:</label>
            <select id="languageSelect" class="text-black px-2 py-1 rounded">
                {lang_options}
            </select>
        </div>
    </header>

    <main class="p-6">
        <h2 class="text-2xl font-semibold mb-4">{title} ({lang_code})</h2>
        <p>This is a placeholder for the <strong>{title}</strong> page in <strong>{lang_name}</strong>.</p>
        <p><a href="/index.html" class="text-blue-600 underline">Back to homepage</a></p>
    </main>

    <script>
    document.addEventListener("DOMContentLoaded", () => {{
        const langSelector = document.getElementById("languageSelect");
        langSelector.value = "{lang_code}";
        langSelector.addEventListener("change", () => {{
            const newLang = langSelector.value;
            const currentPage = "{topic}.html";
            window.location.href = `/${{newLang}}/${{currentPage}}`;
        }});
    }});
    </script>
</body>
</html>
"""

# Generate language dropdown options
def generate_lang_options(current_code):
    options = []
    for code, name in languages.items():
        selected = "selected" if code == current_code else ""
        options.append(f'<option value="{code}" {selected}>{name}</option>')
    return "\n                ".join(options)

# Main generator loop
for lang_code, lang_name in languages.items():
    os.makedirs(lang_code, exist_ok=True)
    for topic, title in topics.items():
        output_path = os.path.join(lang_code, f"{topic}.html")
        html_content = template.format(
            lang_code=lang_code,
            lang_name=lang_name,
            topic=topic,
            title=title,
            lang_options=generate_lang_options(lang_code)
        )
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html_content)

print("✅ Language pages generated successfully.")

