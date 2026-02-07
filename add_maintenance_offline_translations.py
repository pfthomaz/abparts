#!/usr/bin/env python3
"""
Add offline maintenance translations to all language files
"""

import json
import os

# Translation data for all languages
translations = {
    'en': {
        'maintenance': {
            'offlineMode': 'Offline Mode',
            'offlineModeHelp': 'You are offline. Maintenance will be saved locally and synced when connection is restored.',
            'savedOffline': 'Maintenance saved offline. Will sync when connection restored.',
            'pendingSync': '{count} maintenance execution(s) pending sync',
            'pendingSyncMessage': 'These maintenance executions were recorded offline and will sync when connection is restored.',
            'waitingSync': 'Waiting to sync',
            'syncingExecution': 'Syncing maintenance execution...',
        }
    },
    'es': {
        'maintenance': {
            'offlineMode': 'Modo Sin Conexión',
            'offlineModeHelp': 'Estás sin conexión. El mantenimiento se guardará localmente y se sincronizará cuando se restablezca la conexión.',
            'savedOffline': 'Mantenimiento guardado sin conexión. Se sincronizará cuando se restablezca la conexión.',
            'pendingSync': '{count} ejecución(es) de mantenimiento pendiente(s) de sincronización',
            'pendingSyncMessage': 'Estas ejecuciones de mantenimiento se registraron sin conexión y se sincronizarán cuando se restablezca la conexión.',
            'waitingSync': 'Esperando sincronización',
            'syncingExecution': 'Sincronizando ejecución de mantenimiento...',
        }
    },
    'tr': {
        'maintenance': {
            'offlineMode': 'Çevrimdışı Mod',
            'offlineModeHelp': 'Çevrimdışısınız. Bakım yerel olarak kaydedilecek ve bağlantı geri geldiğinde senkronize edilecektir.',
            'savedOffline': 'Bakım çevrimdışı kaydedildi. Bağlantı geri geldiğinde senkronize edilecek.',
            'pendingSync': '{count} bakım yürütmesi senkronizasyon bekliyor',
            'pendingSyncMessage': 'Bu bakım yürütmeleri çevrimdışı kaydedildi ve bağlantı geri geldiğinde senkronize edilecek.',
            'waitingSync': 'Senkronizasyon bekleniyor',
            'syncingExecution': 'Bakım yürütmesi senkronize ediliyor...',
        }
    },
    'no': {
        'maintenance': {
            'offlineMode': 'Frakoblet Modus',
            'offlineModeHelp': 'Du er frakoblet. Vedlikehold vil bli lagret lokalt og synkronisert når tilkoblingen er gjenopprettet.',
            'savedOffline': 'Vedlikehold lagret frakoblet. Vil synkronisere når tilkoblingen er gjenopprettet.',
            'pendingSync': '{count} vedlikeholdsutførelse(r) venter på synkronisering',
            'pendingSyncMessage': 'Disse vedlikeholdsutførelsene ble registrert frakoblet og vil synkronisere når tilkoblingen er gjenopprettet.',
            'waitingSync': 'Venter på synkronisering',
            'syncingExecution': 'Synkroniserer vedlikeholdsutførelse...',
        }
    },
    'el': {
        'maintenance': {
            'offlineMode': 'Λειτουργία Εκτός Σύνδεσης',
            'offlineModeHelp': 'Είστε εκτός σύνδεσης. Η συντήρηση θα αποθηκευτεί τοπικά και θα συγχρονιστεί όταν αποκατασταθεί η σύνδεση.',
            'savedOffline': 'Η συντήρηση αποθηκεύτηκε εκτός σύνδεσης. Θα συγχρονιστεί όταν αποκατασταθεί η σύνδεση.',
            'pendingSync': '{count} εκτέλεση(-εις) συντήρησης σε αναμονή συγχρονισμού',
            'pendingSyncMessage': 'Αυτές οι εκτελέσεις συντήρησης καταγράφηκαν εκτός σύνδεσης και θα συγχρονιστούν όταν αποκατασταθεί η σύνδεση.',
            'waitingSync': 'Αναμονή συγχρονισμού',
            'syncingExecution': 'Συγχρονισμός εκτέλεσης συντήρησης...',
        }
    },
    'ar': {
        'maintenance': {
            'offlineMode': 'وضع عدم الاتصال',
            'offlineModeHelp': 'أنت غير متصل. سيتم حفظ الصيانة محليًا ومزامنتها عند استعادة الاتصال.',
            'savedOffline': 'تم حفظ الصيانة دون اتصال. ستتم المزامنة عند استعادة الاتصال.',
            'pendingSync': '{count} تنفيذ صيانة في انتظار المزامنة',
            'pendingSyncMessage': 'تم تسجيل عمليات تنفيذ الصيانة هذه دون اتصال وستتم مزامنتها عند استعادة الاتصال.',
            'waitingSync': 'في انتظار المزامنة',
            'syncingExecution': 'مزامنة تنفيذ الصيانة...',
        }
    }
}

def deep_merge(base, update):
    """Deep merge two dictionaries"""
    for key, value in update.items():
        if key in base and isinstance(base[key], dict) and isinstance(value, dict):
            deep_merge(base[key], value)
        else:
            base[key] = value
    return base

def update_translation_file(lang_code, new_translations):
    """Update a translation file with new translations"""
    file_path = f'frontend/src/locales/{lang_code}.json'
    
    # Read existing translations
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            existing = json.load(f)
    except FileNotFoundError:
        print(f"Warning: {file_path} not found, skipping...")
        return False
    
    # Merge translations
    merged = deep_merge(existing, new_translations)
    
    # Write back
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(merged, f, ensure_ascii=False, indent=2)
    
    print(f"✓ Updated {file_path}")
    return True

def main():
    """Main function"""
    print("Adding offline maintenance translations...")
    print()
    
    success_count = 0
    for lang_code, trans in translations.items():
        if update_translation_file(lang_code, trans):
            success_count += 1
    
    print()
    print(f"✓ Successfully updated {success_count}/{len(translations)} translation files")
    print()
    print("Offline maintenance translations added!")

if __name__ == '__main__':
    main()
