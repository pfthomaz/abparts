#!/usr/bin/env python3
"""
Add execution delete translations to all language files
"""

import json
import os

# Translation keys to add
translations = {
    'en': {
        'confirmDeleteExecution': 'Are you sure you want to delete this maintenance execution? This action cannot be undone.',
        'executionDeletedSuccessfully': 'Maintenance execution deleted successfully',
        'failedToDeleteExecution': 'Failed to delete maintenance execution'
    },
    'el': {
        'confirmDeleteExecution': 'Είστε σίγουροι ότι θέλετε να διαγράψετε αυτήν την εκτέλεση συντήρησης; Αυτή η ενέργεια δεν μπορεί να αναιρεθεί.',
        'executionDeletedSuccessfully': 'Η εκτέλεση συντήρησης διαγράφηκε με επιτυχία',
        'failedToDeleteExecution': 'Αποτυχία διαγραφής εκτέλεσης συντήρησης'
    },
    'es': {
        'confirmDeleteExecution': '¿Está seguro de que desea eliminar esta ejecución de mantenimiento? Esta acción no se puede deshacer.',
        'executionDeletedSuccessfully': 'Ejecución de mantenimiento eliminada con éxito',
        'failedToDeleteExecution': 'Error al eliminar la ejecución de mantenimiento'
    },
    'no': {
        'confirmDeleteExecution': 'Er du sikker på at du vil slette denne vedlikeholdsutførelsen? Denne handlingen kan ikke angres.',
        'executionDeletedSuccessfully': 'Vedlikeholdsutførelse slettet',
        'failedToDeleteExecution': 'Kunne ikke slette vedlikeholdsutførelse'
    },
    'tr': {
        'confirmDeleteExecution': 'Bu bakım yürütmesini silmek istediğinizden emin misiniz? Bu işlem geri alınamaz.',
        'executionDeletedSuccessfully': 'Bakım yürütmesi başarıyla silindi',
        'failedToDeleteExecution': 'Bakım yürütmesi silinemedi'
    },
    'ar': {
        'confirmDeleteExecution': 'هل أنت متأكد من أنك تريد حذف تنفيذ الصيانة هذا؟ لا يمكن التراجع عن هذا الإجراء.',
        'executionDeletedSuccessfully': 'تم حذف تنفيذ الصيانة بنجاح',
        'failedToDeleteExecution': 'فشل في حذف تنفيذ الصيانة'
    }
}

def add_translations():
    """Add translations to all language files"""
    
    for lang_code, new_keys in translations.items():
        file_path = f'frontend/src/locales/{lang_code}.json'
        
        if not os.path.exists(file_path):
            print(f"⚠️  File not found: {file_path}")
            continue
        
        # Read existing translations
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Add new keys to maintenance section
        if 'maintenance' not in data:
            data['maintenance'] = {}
        
        # Add the new keys
        for key, value in new_keys.items():
            data['maintenance'][key] = value
            print(f"✅ Added {lang_code}.maintenance.{key}")
        
        # Write back to file
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ Updated {file_path}")

if __name__ == '__main__':
    print("Adding execution delete translations...")
    add_translations()
    print("\n✅ All translations added successfully!")
