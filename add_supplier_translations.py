#!/usr/bin/env python3
import json

# Supplier-specific translations
supplier_translations = {
    'en': {
        'partsSortedNoteSupplier': 'Parts sorted by order frequency for this supplier'
    },
    'el': {
        'partsSortedNoteSupplier': 'Ανταλλακτικά ταξινομημένα κατά συχνότητα παραγγελίας για αυτόν τον προμηθευτή'
    },
    'ar': {
        'partsSortedNoteSupplier': 'القطع مرتبة حسب تكرار الطلب لهذا المورد'
    },
    'es': {
        'partsSortedNoteSupplier': 'Piezas ordenadas por frecuencia de pedido para este proveedor'
    },
    'tr': {
        'partsSortedNoteSupplier': 'Bu tedarikçi için sipariş sıklığına göre sıralanmış parçalar'
    },
    'no': {
        'partsSortedNoteSupplier': 'Deler sortert etter bestillingsfrekvens for denne leverandøren'
    }
}

# Process each language file
for lang_code, translations in supplier_translations.items():
    file_path = f'frontend/src/locales/{lang_code}.json'
    
    try:
        # Read existing translations
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Add translations to orders section
        if 'orders' not in data:
            data['orders'] = {}
        
        # Add each translation
        for key, value in translations.items():
            data['orders'][key] = value
        
        # Write back to file
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f'✓ Added supplier translations to {lang_code}.json')
    
    except Exception as e:
        print(f'✗ Error processing {lang_code}.json: {e}')

print('\nSupplier translations added successfully!')
