#!/usr/bin/env python3
import json

# Maintenance Executions translations
translations = {
    'en': {
        'title': 'Maintenance Executions',
        'newExecution': 'New Execution',
        'executionHistory': 'Execution History',
        'startNewMaintenance': 'Start New Maintenance',
        'selectMachine': 'Select Machine',
        'selectMachinePlaceholder': '-- Select a machine --',
        'selectProtocol': 'Select Protocol',
        'selectProtocolPlaceholder': '-- Select a protocol --',
        'pleaseSelectMachine': 'Please select a machine',
        'pleaseSelectProtocol': 'Please select a protocol',
        'type': 'Type',
        'duration': 'Duration',
        'frequency': 'Frequency',
        'every': 'Every',
        'hours': 'hours',
        'min': 'min',
        'startMaintenance': 'Start Maintenance'
    },
    'el': {
        'title': 'Εκτελέσεις Συντήρησης',
        'newExecution': 'Νέα Εκτέλεση',
        'executionHistory': 'Ιστορικό Εκτελέσεων',
        'startNewMaintenance': 'Έναρξη Νέας Συντήρησης',
        'selectMachine': 'Επιλογή Μηχανήματος',
        'selectMachinePlaceholder': '-- Επιλέξτε μηχάνημα --',
        'selectProtocol': 'Επιλογή Πρωτοκόλλου',
        'selectProtocolPlaceholder': '-- Επιλέξτε πρωτόκολλο --',
        'pleaseSelectMachine': 'Παρακαλώ επιλέξτε ένα μηχάνημα',
        'pleaseSelectProtocol': 'Παρακαλώ επιλέξτε ένα πρωτόκολλο',
        'type': 'Τύπος',
        'duration': 'Διάρκεια',
        'frequency': 'Συχνότητα',
        'every': 'Κάθε',
        'hours': 'ώρες',
        'min': 'λεπτά',
        'startMaintenance': 'Έναρξη Συντήρησης'
    },
    'ar': {
        'title': 'تنفيذات الصيانة',
        'newExecution': 'تنفيذ جديد',
        'executionHistory': 'سجل التنفيذ',
        'startNewMaintenance': 'بدء صيانة جديدة',
        'selectMachine': 'اختر الآلة',
        'selectMachinePlaceholder': '-- اختر آلة --',
        'selectProtocol': 'اختر البروتوكول',
        'selectProtocolPlaceholder': '-- اختر بروتوكول --',
        'pleaseSelectMachine': 'يرجى اختيار آلة',
        'pleaseSelectProtocol': 'يرجى اختيار بروتوكول',
        'type': 'النوع',
        'duration': 'المدة',
        'frequency': 'التكرار',
        'every': 'كل',
        'hours': 'ساعات',
        'min': 'دقيقة',
        'startMaintenance': 'بدء الصيانة'
    },
    'es': {
        'title': 'Ejecuciones de Mantenimiento',
        'newExecution': 'Nueva Ejecución',
        'executionHistory': 'Historial de Ejecuciones',
        'startNewMaintenance': 'Iniciar Nuevo Mantenimiento',
        'selectMachine': 'Seleccionar Máquina',
        'selectMachinePlaceholder': '-- Seleccione una máquina --',
        'selectProtocol': 'Seleccionar Protocolo',
        'selectProtocolPlaceholder': '-- Seleccione un protocolo --',
        'pleaseSelectMachine': 'Por favor seleccione una máquina',
        'pleaseSelectProtocol': 'Por favor seleccione un protocolo',
        'type': 'Tipo',
        'duration': 'Duración',
        'frequency': 'Frecuencia',
        'every': 'Cada',
        'hours': 'horas',
        'min': 'min',
        'startMaintenance': 'Iniciar Mantenimiento'
    },
    'tr': {
        'title': 'Bakım Uygulamaları',
        'newExecution': 'Yeni Uygulama',
        'executionHistory': 'Uygulama Geçmişi',
        'startNewMaintenance': 'Yeni Bakım Başlat',
        'selectMachine': 'Makine Seç',
        'selectMachinePlaceholder': '-- Bir makine seçin --',
        'selectProtocol': 'Protokol Seç',
        'selectProtocolPlaceholder': '-- Bir protokol seçin --',
        'pleaseSelectMachine': 'Lütfen bir makine seçin',
        'pleaseSelectProtocol': 'Lütfen bir protokol seçin',
        'type': 'Tür',
        'duration': 'Süre',
        'frequency': 'Sıklık',
        'every': 'Her',
        'hours': 'saat',
        'min': 'dk',
        'startMaintenance': 'Bakımı Başlat'
    },
    'no': {
        'title': 'Vedlikeholdsutførelser',
        'newExecution': 'Ny Utførelse',
        'executionHistory': 'Utførelseshistorikk',
        'startNewMaintenance': 'Start Nytt Vedlikehold',
        'selectMachine': 'Velg Maskin',
        'selectMachinePlaceholder': '-- Velg en maskin --',
        'selectProtocol': 'Velg Protokoll',
        'selectProtocolPlaceholder': '-- Velg en protokoll --',
        'pleaseSelectMachine': 'Vennligst velg en maskin',
        'pleaseSelectProtocol': 'Vennligst velg en protokoll',
        'type': 'Type',
        'duration': 'Varighet',
        'frequency': 'Frekvens',
        'every': 'Hver',
        'hours': 'timer',
        'min': 'min',
        'startMaintenance': 'Start Vedlikehold'
    }
}

# Add to each language file
for lang_code, maintenance_translations in translations.items():
    file_path = f'frontend/src/locales/{lang_code}.json'
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Add maintenance section
        data['maintenance'] = maintenance_translations
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f'✓ Added Maintenance Executions translations to {lang_code}.json')
    
    except Exception as e:
        print(f'✗ Error processing {lang_code}.json: {e}')

print('\n✅ Maintenance Executions translations added successfully!')
