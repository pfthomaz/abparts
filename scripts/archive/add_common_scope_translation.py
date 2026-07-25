#!/usr/bin/env python3
"""
Add common.scope translation key to all locale files
"""

import json
import os

# Define the scope translations for all languages
scope_translations = {
    "en": {
        "common": {
            "scope": "Scope"
        }
    },
    "el": {
        "common": {
            "scope": "Εμβέλεια"
        }
    },
    "ar": {
        "common": {
            "scope": "النطاق"
        }
    },
    "es": {
        "common": {
            "scope": "Alcance"
        }
    },
    "tr": {
        "common": {
            "scope": "Kapsam"
        }
    },
    "no": {
        "common": {
            "scope": "Omfang"
        }
    }
}

def update_translations_file(file_path, translations):
    """Update translations in a JSON file"""
    try:
        # Read existing translations
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Merge common translations (this will update existing keys and add new ones)
        if 'common' in data:
            data['common'].update(translations['common'])
        else:
            data['common'] = translations['common']
        
        # Write back to file
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Updated {file_path}")
        
    except Exception as e:
        print(f"❌ Error updating {file_path}: {e}")

def main():
    """Add common.scope translation to all locale files"""
    print("Adding common.scope translation to locale files...")
    
    locales_dir = "frontend/src/locales"
    
    for lang_code, translations in scope_translations.items():
        file_path = os.path.join(locales_dir, f"{lang_code}.json")
        if os.path.exists(file_path):
            update_translations_file(file_path, translations)
        else:
            print(f"⚠️  Locale file not found: {file_path}")
    
    print("\n🎉 common.scope translation added successfully!")
    print("\nTranslations added:")
    print("- English: Scope")
    print("- Greek: Εμβέλεια")
    print("- Arabic: النطاق")
    print("- Spanish: Alcance")
    print("- Turkish: Kapsam")
    print("- Norwegian: Omfang")

if __name__ == "__main__":
    main()