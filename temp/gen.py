import os
from pathlib import Path

# Map long language names to 2-letter folder codes
lang_map = {
    "amh": "am", "ar": "ar", "dari": "fa", "eng": "en", "hausa": "ha",
    "ja": "ja", "luo": "lu", "qu": "qu", "sh": "sh", "sp": "es",
    "sw": "sw", "ukr": "uk", "vi": "vi", "we": "we", "yo": "yo"
}

topics = {
    "water.html": "Water Desalination",
    "waste.html": "Waste Management",
    "fuel-briquette.html": "Fuel Briquette",
    "solar-cooking.html": "Solar Cooking",
    "mycelial.html": "Mycelial Food Security"
}

base_dir = Path.cwd()
template = """
<!DOCTYPE html>
<html lang="{lang_code}">
<head>
  <meta charset="utf-8">
  <title>{title} - {lang_code}</title>
  <script defer src="/header.js"></script>
  <link rel="stylesheet" href="/local-styles.css">
</head>
<body>
  <h1>{title} ({lang_code})</h1>
  <div id="transcript">Loading transcript...</div>

  <script>
    fetch('/solarcooking/lang/vid1_{lang_key}.txt')
      .then(response => response.text())
      .then(data => {{
        document.getElementById('transcript').textContent = data;
      }})
      .catch(err => {{
        document.getElementById('transcript').textContent = 'Transcript not available.';
      }});
  </script>
</body>
</html>
"""

output_root = base_dir  # Can be changed to "build/" or "public/"

for lang_key, folder_code in lang_map.items():
    lang_folder = output_root / folder_code
    lang_folder.mkdir(exist_ok=True)
    
    for filename, topic_title in topics.items():
        content = template.format(
            lang_code=folder_code,
            lang_key=lang_key,
            title=topic_title
        )
        with open(lang_folder / filename, 'w', encoding='utf-8') as f:
            f.write(content)

print("✅ Language pages generated.")

