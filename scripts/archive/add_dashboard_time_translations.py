#!/usr/bin/env python3
"""Add missing dashboard time-related translations to all locale files."""

import json

# Translation mappings
translations = {
    "el": {  # Greek
        "justNow": "μόλις τώρα",
        "minAgo": "πριν {{count}} λεπτά"
    },
    "ar": {  # Arabic
        "justNow": "الآن",
        "minAgo": "منذ {{count}} دقيقة"
    },
    "es": {  # Spanish
        "justNow": "justo ahora",
        "minAgo": "hace {{count}} min"
    },
    "tr": {  # Turkish
        "justNow": "şimdi",
        "minAgo": "{{count}} dk önce"
    },
    "no": {  # Norwegian
        "justNow": "akkurat nå",
        "minAgo": "{{count}} min siden"
    }
}

def add_translations(lang_code, translations_dict):
    """Add translations to a specific language file."""
    file_path = f"frontend/src/locales/{lang_code}.json"
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Add the new keys to dashboard section
        if "dashboard" in data:
            data["dashboard"]["justNow"] = translations_dict["justNow"]
            data["dashboard"]["minAgo"] = translations_dict["minAgo"]
        
        # Write back
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ Updated {lang_code}.json")
        
    except Exception as e:
        print(f"❌ Error updating {lang_code}.json: {e}")

# Process all languages
for lang_code, trans in translations.items():
    add_translations(lang_code, trans)

print("\n✅ All dashboard time translations added!")
