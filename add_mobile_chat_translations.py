#!/usr/bin/env python3
"""
Add mobile-specific chat widget translations to all locale files.
"""

import json
import os

# Translation mappings for each language
translations = {
    'ar': {
        'fullScreen': 'ملء الشاشة',
        'exitFullScreen': 'الخروج من ملء الشاشة'
    },
    'el': {
        'fullScreen': 'Πλήρης οθόνη',
        'exitFullScreen': 'Έξοδος από πλήρη οθόνη'
    },
    'es': {
        'fullScreen': 'Pantalla completa',
        'exitFullScreen': 'Salir de pantalla completa'
    },
    'no': {
        'fullScreen': 'Fullskjerm',
        'exitFullScreen': 'Avslutt fullskjerm'
    },
    'tr': {
        'fullScreen': 'Tam ekran',
        'exitFullScreen': 'Tam ekrandan çık'
    }
}

def add_translations():
    """Add mobile chat translations to all locale files."""
    locale_dir = 'frontend/src/locales'
    
    for lang_code, trans in translations.items():
        file_path = os.path.join(locale_dir, f'{lang_code}.json')
        
        if not os.path.exists(file_path):
            print(f"⚠️  File not found: {file_path}")
            continue
        
        try:
            # Read existing translations
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Add new translations to aiAssistant.chatWidget
            if 'aiAssistant' in data and 'chatWidget' in data['aiAssistant']:
                # Add after 'maximize' key
                chat_widget = data['aiAssistant']['chatWidget']
                
                # Create new ordered dict with fullScreen keys inserted after maximize
                new_chat_widget = {}
                for key, value in chat_widget.items():
                    new_chat_widget[key] = value
                    if key == 'maximize':
                        new_chat_widget['fullScreen'] = trans['fullScreen']
                        new_chat_widget['exitFullScreen'] = trans['exitFullScreen']
                
                data['aiAssistant']['chatWidget'] = new_chat_widget
                
                # Write back to file
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                
                print(f"✅ Updated {lang_code}.json")
            else:
                print(f"⚠️  aiAssistant.chatWidget not found in {lang_code}.json")
        
        except Exception as e:
            print(f"❌ Error processing {lang_code}.json: {e}")

if __name__ == '__main__':
    print("Adding mobile chat widget translations...")
    add_translations()
    print("\n✨ Translation update complete!")
