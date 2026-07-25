#!/usr/bin/env python3
import json
import os

# Status translations for all languages
status_translations = {
    'en': {
        'requested': 'Requested',
        'pending': 'Pending',
        'shipped': 'Shipped',
        'received': 'Received',
        'delivered': 'Delivered',
        'cancelled': 'Cancelled'
    },
    'el': {
        'requested': 'Ζητήθηκε',
        'pending': 'Εκκρεμεί',
        'shipped': 'Απεστάλη',
        'received': 'Παραλήφθηκε',
        'delivered': 'Παραδόθηκε',
        'cancelled': 'Ακυρώθηκε'
    },
    'ar': {
        'requested': 'مطلوب',
        'pending': 'قيد الانتظار',
        'shipped': 'تم الشحن',
        'received': 'تم الاستلام',
        'delivered': 'تم التسليم',
        'cancelled': 'ملغى'
    },
    'es': {
        'requested': 'Solicitado',
        'pending': 'Pendiente',
        'shipped': 'Enviado',
        'received': 'Recibido',
        'delivered': 'Entregado',
        'cancelled': 'Cancelado'
    },
    'tr': {
        'requested': 'Talep Edildi',
        'pending': 'Beklemede',
        'shipped': 'Gönderildi',
        'received': 'Alındı',
        'delivered': 'Teslim Edildi',
        'cancelled': 'İptal Edildi'
    },
    'no': {
        'requested': 'Forespurt',
        'pending': 'Venter',
        'shipped': 'Sendt',
        'received': 'Mottatt',
        'delivered': 'Levert',
        'cancelled': 'Kansellert'
    }
}

# Process each language file
for lang_code, translations in status_translations.items():
    file_path = f'frontend/src/locales/{lang_code}.json'
    
    try:
        # Read existing translations
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Add status translations to orders section
        if 'orders' not in data:
            data['orders'] = {}
        
        # Add each status translation
        for key, value in translations.items():
            data['orders'][key] = value
        
        # Write back to file
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f'✓ Added status translations to {lang_code}.json')
    
    except Exception as e:
        print(f'✗ Error processing {lang_code}.json: {e}')

print('\nStatus translations added successfully!')
