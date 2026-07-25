#!/usr/bin/env python3

import json
import os

def add_skip_translation():
    """Add 'skip' translation key to common section in all locale files"""
    
    # Define translations for each language
    translations = {
        'en.json': 'Skip',
        'el.json': 'Παράλειψη',
        'ar.json': 'تخطي',
        'es.json': 'Omitir',
        'tr.json': 'Atla',
        'no.json': 'Hopp over'
    }
    
    locales_dir = 'frontend/src/locales'
    
    for filename, translation in translations.items():
        filepath = os.path.join(locales_dir, filename)
        
        try:
            # Read existing file
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Add skip to common section if it doesn't exist
            if 'common' in data:
                if 'skip' not in data['common']:
                    data['common']['skip'] = translation
                    print(f"Added 'skip': '{translation}' to {filename}")
                else:
                    print(f"'skip' already exists in {filename}")
            else:
                print(f"Warning: 'common' section not found in {filename}")
                continue
            
            # Write back to file with proper formatting
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            print(f"Error processing {filename}: {e}")

if __name__ == '__main__':
    add_skip_translation()
    print("Skip translation keys added to all locale files!")