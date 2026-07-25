#!/usr/bin/env python3
"""
Add mobile navigation translations to all language files
"""

import json
import os

# Translation data for all languages
translations = {
    'en': {
        "home": "Home",
        "stock": "Stock",
        "actions": "Actions",
        "orders": "Orders",
        "machines": "Machines",
        "quickActions": "Quick Actions",
        "allFeatures": "All Features",
        "orderParts": "Order Parts",
        "recordHours": "Record Hours",
        "checkStock": "Check Stock",
        "useParts": "Use Parts"
    },
    'es': {
        "home": "Inicio",
        "stock": "Stock",
        "actions": "Acciones",
        "orders": "Pedidos",
        "machines": "Máquinas",
        "quickActions": "Acciones Rápidas",
        "allFeatures": "Todas las Funciones",
        "orderParts": "Pedir Piezas",
        "recordHours": "Registrar Horas",
        "checkStock": "Verificar Stock",
        "useParts": "Usar Piezas"
    },
    'ar': {
        "home": "الرئيسية",
        "stock": "المخزون",
        "actions": "الإجراءات",
        "orders": "الطلبات",
        "machines": "الآلات",
        "quickActions": "إجراءات سريعة",
        "allFeatures": "جميع الميزات",
        "orderParts": "طلب قطع",
        "recordHours": "تسجيل الساعات",
        "checkStock": "التحقق من المخزون",
        "useParts": "استخدام القطع"
    },
    'el': {
        "home": "Αρχική",
        "stock": "Απόθεμα",
        "actions": "Ενέργειες",
        "orders": "Παραγγελίες",
        "machines": "Μηχανές",
        "quickActions": "Γρήγορες Ενέργειες",
        "allFeatures": "Όλες οι Λειτουργίες",
        "orderParts": "Παραγγελία Ανταλλακτικών",
        "recordHours": "Καταγραφή Ωρών",
        "checkStock": "Έλεγχος Αποθέματος",
        "useParts": "Χρήση Ανταλλακτικών"
    },
    'no': {
        "home": "Hjem",
        "stock": "Lager",
        "actions": "Handlinger",
        "orders": "Bestillinger",
        "machines": "Maskiner",
        "quickActions": "Hurtighandlinger",
        "allFeatures": "Alle Funksjoner",
        "orderParts": "Bestill Deler",
        "recordHours": "Registrer Timer",
        "checkStock": "Sjekk Lager",
        "useParts": "Bruk Deler"
    },
    'tr': {
        "home": "Ana Sayfa",
        "stock": "Stok",
        "actions": "İşlemler",
        "orders": "Siparişler",
        "machines": "Makineler",
        "quickActions": "Hızlı İşlemler",
        "allFeatures": "Tüm Özellikler",
        "orderParts": "Parça Sipariş Et",
        "recordHours": "Saat Kaydet",
        "checkStock": "Stok Kontrol",
        "useParts": "Parça Kullan"
    }
}

def add_translations():
    """Add mobile navigation translations to all language files"""
    
    locales_dir = 'frontend/src/locales'
    
    for lang_code, trans_data in translations.items():
        file_path = os.path.join(locales_dir, f'{lang_code}.json')
        
        print(f"\nProcessing {lang_code}.json...")
        
        try:
            # Read existing translations
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Add mobileNav section if it doesn't exist
            if 'mobileNav' not in data:
                data['mobileNav'] = {}
            
            # Add/update translations
            for key, value in trans_data.items():
                data['mobileNav'][key] = value
                print(f"  Added: mobileNav.{key} = {value}")
            
            # Write back to file
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            print(f"✓ Successfully updated {lang_code}.json")
            
        except FileNotFoundError:
            print(f"✗ File not found: {file_path}")
        except json.JSONDecodeError as e:
            print(f"✗ JSON decode error in {file_path}: {e}")
        except Exception as e:
            print(f"✗ Error processing {file_path}: {e}")

if __name__ == '__main__':
    print("Adding mobile navigation translations...")
    print("=" * 60)
    add_translations()
    print("\n" + "=" * 60)
    print("✓ Mobile navigation translations added to all language files!")
    print("\nTranslation keys added:")
    print("  - mobileNav.home")
    print("  - mobileNav.stock")
    print("  - mobileNav.actions")
    print("  - mobileNav.orders")
    print("  - mobileNav.machines")
    print("  - mobileNav.quickActions")
    print("  - mobileNav.allFeatures")
    print("  - mobileNav.orderParts")
    print("  - mobileNav.recordHours")
    print("  - mobileNav.checkStock")
    print("  - mobileNav.useParts")
