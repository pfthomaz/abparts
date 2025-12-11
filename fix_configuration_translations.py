#!/usr/bin/env python3

import json
import os

def convert_flat_to_nested(flat_dict):
    """Convert flat dot-notation keys to nested objects"""
    nested = {}
    
    for key, value in flat_dict.items():
        if '.' in key and key.startswith('configuration.'):
            # Split the key and create nested structure
            parts = key.split('.')
            current = nested
            
            # Navigate/create the nested structure
            for part in parts[:-1]:
                if part not in current:
                    current[part] = {}
                current = current[part]
            
            # Set the final value
            current[parts[-1]] = value
        else:
            # Keep non-configuration keys as they are
            nested[key] = value
    
    return nested

def fix_locale_file(file_path):
    """Fix a single locale file"""
    print(f"Fixing {file_path}...")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Convert flat configuration keys to nested
    fixed_data = convert_flat_to_nested(data)
    
    # Write back to file
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(fixed_data, f, ensure_ascii=False, indent=2)
    
    print(f"✅ Fixed {file_path}")

def main():
    """Fix all locale files"""
    locale_dir = "frontend/src/locales"
    locale_files = [
        "en.json",
        "el.json", 
        "ar.json",
        "es.json",
        "tr.json",
        "no.json"
    ]
    
    for locale_file in locale_files:
        file_path = os.path.join(locale_dir, locale_file)
        if os.path.exists(file_path):
            fix_locale_file(file_path)
        else:
            print(f"⚠️  File not found: {file_path}")
    
    print("\n🎉 All configuration translations fixed!")
    print("The translation keys are now properly nested and should work correctly.")

if __name__ == "__main__":
    main()