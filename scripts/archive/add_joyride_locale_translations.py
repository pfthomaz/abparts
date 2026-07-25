#!/usr/bin/env python3
"""
Add missing Joyride locale translations for step counter and open button
"""

import json
import os

# Define the additional Joyride locale translations
joyride_locale_translations = {
    "en": {
        "tour": {
            "open": "Open",
            "step": "Step",
            "of": "of"
        }
    },
    "el": {
        "tour": {
            "open": "Άνοιγμα",
            "step": "Βήμα",
            "of": "από"
        }
    },
    "ar": {
        "tour": {
            "open": "فتح",
            "step": "خطوة",
            "of": "من"
        }
    },
    "es": {
        "tour": {
            "open": "Abrir",
            "step": "Paso",
            "of": "de"
        }
    },
    "tr": {
        "tour": {
            "open": "Aç",
            "step": "Adım",
            "of": "/"
        }
    },
    "no": {
        "tour": {
            "open": "Åpne",
            "step": "Steg",
            "of": "av"
        }
    }
}

def update_translations_file(file_path, translations):
    """Update translations in a JSON file"""
    try:
        # Read existing translations
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Add the new tour locale keys
        if 'tour' in data:
            data['tour'].update(translations['tour'])
        else:
            data['tour'] = translations['tour']
        
        # Write back to file
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Updated {file_path}")
        
    except Exception as e:
        print(f"❌ Error updating {file_path}: {e}")

def main():
    """Add Joyride locale translations to all locale files"""
    print("Adding Joyride locale translations to locale files...")
    
    locales_dir = "frontend/src/locales"
    
    for lang_code, translations in joyride_locale_translations.items():
        file_path = os.path.join(locales_dir, f"{lang_code}.json")
        if os.path.exists(file_path):
            update_translations_file(file_path, translations)
        else:
            print(f"⚠️  Locale file not found: {file_path}")
    
    print("\n🎉 Joyride locale translations added successfully!")
    print("\nAdded translations for:")
    print("- 'open' button")
    print("- 'step' counter text")
    print("- 'of' connector word")
    print("- All 6 languages supported")
    print("\nNow 'Step 3 of 7' will be properly localized!")

if __name__ == "__main__":
    main()