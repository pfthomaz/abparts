#!/usr/bin/env python3
"""
Add missing translations: orders.expectedDelivery and common.remove
"""

import json

# Translation data for all languages
translations = {
    "en": {
        "orders": {
            "expectedDelivery": "Expected Delivery"
        },
        "common": {
            "remove": "Remove"
        }
    },
    "el": {
        "orders": {
            "expectedDelivery": "Αναμενόμενη Παράδοση"
        },
        "common": {
            "remove": "Αφαίρεση"
        }
    },
    "ar": {
        "orders": {
            "expectedDelivery": "التسليم المتوقع"
        },
        "common": {
            "remove": "إزالة"
        }
    },
    "es": {
        "orders": {
            "expectedDelivery": "Entrega Esperada"
        },
        "common": {
            "remove": "Eliminar"
        }
    },
    "tr": {
        "orders": {
            "expectedDelivery": "Beklenen Teslimat"
        },
        "common": {
            "remove": "Kaldır"
        }
    },
    "no": {
        "orders": {
            "expectedDelivery": "Forventet Levering"
        },
        "common": {
            "remove": "Fjern"
        }
    }
}

def update_locale_file(lang_code, new_translations):
    """Update a locale file with new translations"""
    file_path = f"frontend/src/locales/{lang_code}.json"
    
    # Read existing translations
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Update orders section
    if 'orders' not in data:
        data['orders'] = {}
    data['orders']['expectedDelivery'] = new_translations['orders']['expectedDelivery']
    
    # Update common section
    if 'common' not in data:
        data['common'] = {}
    data['common']['remove'] = new_translations['common']['remove']
    
    # Write back
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"✓ Updated {file_path}")

def main():
    for lang_code, trans in translations.items():
        update_locale_file(lang_code, trans)
    
    print("\n✅ Missing translations added to all languages!")

if __name__ == "__main__":
    main()
