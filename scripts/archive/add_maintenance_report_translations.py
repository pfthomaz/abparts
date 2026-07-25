#!/usr/bin/env python3
"""
Add maintenance report download translations to all supported languages
"""

import json
import os

# Define translations for all languages
translations = {
    'ar': {
        'downloadDocxReport': 'تنزيل تقرير DOCX مع رؤى الذكاء الاصطناعي',
        'downloadPdfReport': 'تنزيل تقرير PDF مع رؤى الذكاء الاصطناعي',
        'generatingReport': 'جاري إنشاء التقرير...',
        'reportGenerated': 'تم إنشاء التقرير بنجاح'
    },
    'el': {
        'downloadDocxReport': 'Λήψη αναφοράς DOCX με πληροφορίες AI',
        'downloadPdfReport': 'Λήψη αναφοράς PDF με πληροφορίες AI',
        'generatingReport': 'Δημιουργία αναφοράς...',
        'reportGenerated': 'Η αναφορά δημιουργήθηκε με επιτυχία'
    },
    'es': {
        'downloadDocxReport': 'Descargar informe DOCX con información de IA',
        'downloadPdfReport': 'Descargar informe PDF con información de IA',
        'generatingReport': 'Generando informe...',
        'reportGenerated': 'Informe generado exitosamente'
    },
    'no': {
        'downloadDocxReport': 'Last ned DOCX-rapport med AI-innsikt',
        'downloadPdfReport': 'Last ned PDF-rapport med AI-innsikt',
        'generatingReport': 'Genererer rapport...',
        'reportGenerated': 'Rapport generert vellykket'
    },
    'tr': {
        'downloadDocxReport': 'AI Öngörüleri ile DOCX Raporu İndir',
        'downloadPdfReport': 'AI Öngörüleri ile PDF Raporu İndir',
        'generatingReport': 'Rapor oluşturuluyor...',
        'reportGenerated': 'Rapor başarıyla oluşturuldu'
    }
}

def add_translations():
    """Add maintenance report translations to all language files"""
    
    locales_dir = 'frontend/src/locales'
    
    for lang_code, new_translations in translations.items():
        file_path = os.path.join(locales_dir, f'{lang_code}.json')
        
        print(f"\nProcessing {lang_code}.json...")
        
        # Read existing translations
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Check if maintenance section exists
        if 'maintenance' not in data:
            print(f"  Warning: 'maintenance' section not found in {lang_code}.json")
            continue
        
        # Add new translations
        added = []
        for key, value in new_translations.items():
            if key not in data['maintenance']:
                data['maintenance'][key] = value
                added.append(key)
            else:
                print(f"  Skipping {key} (already exists)")
        
        if added:
            # Write back to file with proper formatting
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            print(f"  ✓ Added {len(added)} translations: {', '.join(added)}")
        else:
            print(f"  ✓ All translations already exist")

if __name__ == '__main__':
    print("Adding maintenance report translations to all languages...")
    add_translations()
    print("\n✓ Translation update complete!")
