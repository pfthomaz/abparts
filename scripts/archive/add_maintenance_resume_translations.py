#!/usr/bin/env python3
"""Add maintenance resume and ongoing protocol translations to all locale files."""

import json
import sys

# Translations for each language
TRANSLATIONS = {
    'no': {  # Norwegian
        'maintenance': {
            'resume': 'Gjenoppta',
            'resumeExecution': 'Gjenoppta Utførelse',
            'resuming': 'Gjenopptar',
            'continuingIncompleteExecution': 'Fortsetter pågående utførelse',
            'incomplete': 'Pågående',
            'resumeNow': 'Gjenoppta Nå',
            'incompleteDailyProtocols': 'Pågående Daglige Protokoller',
            'incompleteDailyProtocolsMessage': 'Du har pågående daglige vedlikeholdsprotokoller som må fullføres:',
            'ongoing': 'Pågående',
            'confirmFinishWithIncompleteCritical': '{{count}} kritiske elementer er ikke fullført. Er du sikker på at du vil fullføre?',
            'complete': 'fullført'
        },
        'dailyOperations': {
            'continueOngoing': 'Fortsett Pågående'
        }
    },
    'tr': {  # Turkish
        'maintenance': {
            'resume': 'Devam Et',
            'resumeExecution': 'Yürütmeye Devam Et',
            'resuming': 'Devam Ediyor',
            'continuingIncompleteExecution': 'Devam eden yürütmeye devam ediliyor',
            'incomplete': 'Devam Ediyor',
            'resumeNow': 'Şimdi Devam Et',
            'incompleteDailyProtocols': 'Devam Eden Günlük Protokoller',
            'incompleteDailyProtocolsMessage': 'Tamamlanması gereken devam eden günlük bakım protokolleriniz var:',
            'ongoing': 'Devam Ediyor',
            'confirmFinishWithIncompleteCritical': '{{count}} kritik öğe tamamlanmadı. Bitirmek istediğinizden emin misiniz?',
            'complete': 'tamamlandı'
        },
        'dailyOperations': {
            'continueOngoing': 'Devam Edene Devam Et'
        }
    },
    'ar': {  # Arabic
        'maintenance': {
            'resume': 'استئناف',
            'resumeExecution': 'استئناف التنفيذ',
            'resuming': 'جاري الاستئناف',
            'continuingIncompleteExecution': 'متابعة التنفيذ الجاري',
            'incomplete': 'جاري',
            'resumeNow': 'استئناف الآن',
            'incompleteDailyProtocols': 'البروتوكولات اليومية الجارية',
            'incompleteDailyProtocolsMessage': 'لديك بروتوكولات صيانة يومية جارية يجب إكمالها:',
            'ongoing': 'جاري',
            'confirmFinishWithIncompleteCritical': '{{count}} عناصر حرجة غير مكتملة. هل أنت متأكد من أنك تريد الإنهاء؟',
            'complete': 'مكتمل'
        },
        'dailyOperations': {
            'continueOngoing': 'متابعة الجاري'
        }
    }
}

def add_translations_to_file(filepath, lang_code):
    """Add translations to a locale file."""
    try:
        # Read existing file
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        translations = TRANSLATIONS.get(lang_code)
        if not translations:
            print(f"No translations defined for {lang_code}")
            return False
        
        # Add maintenance translations
        if 'maintenance' in data and 'maintenance' in translations:
            for key, value in translations['maintenance'].items():
                data['maintenance'][key] = value
            print(f"✓ Added {len(translations['maintenance'])} maintenance keys to {lang_code}")
        
        # Add dailyOperations translations
        if 'dailyOperations' in data and 'dailyOperations' in translations:
            for key, value in translations['dailyOperations'].items():
                data['dailyOperations'][key] = value
            print(f"✓ Added {len(translations['dailyOperations'])} dailyOperations keys to {lang_code}")
        
        # Write back to file
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"✓ Successfully updated {filepath}")
        return True
        
    except Exception as e:
        print(f"✗ Error processing {filepath}: {e}")
        return False

def main():
    """Main function."""
    files_to_update = [
        ('frontend/src/locales/no.json', 'no'),
        ('frontend/src/locales/tr.json', 'tr'),
        ('frontend/src/locales/ar.json', 'ar')
    ]
    
    success_count = 0
    for filepath, lang_code in files_to_update:
        if add_translations_to_file(filepath, lang_code):
            success_count += 1
    
    print(f"\n{'='*50}")
    print(f"Updated {success_count}/{len(files_to_update)} files successfully")
    print(f"{'='*50}")
    
    return 0 if success_count == len(files_to_update) else 1

if __name__ == '__main__':
    sys.exit(main())
