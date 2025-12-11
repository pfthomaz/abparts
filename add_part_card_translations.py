#!/usr/bin/env python3
import json

# Translation keys to add
translations = {
    "en": {
        "partCard": {
            "partNumber": "Part #",
            "description": "Description",
            "unit": "Unit",
            "manufacturer": "Manufacturer",
            "partCode": "Part Code",
            "serialNumber": "Serial #",
            "mfgPartNumber": "Mfg Part #",
            "images": "Images",
            "totalStock": "Total Stock",
            "low": "LOW",
            "byWarehouse": "By Warehouse",
            "noInventoryData": "No inventory data available"
        }
    },
    "el": {
        "partCard": {
            "partNumber": "Αρ. Ανταλλακτικού",
            "description": "Περιγραφή",
            "unit": "Μονάδα",
            "manufacturer": "Κατασκευαστής",
            "partCode": "Κωδικός Ανταλλακτικού",
            "serialNumber": "Σειριακός Αρ.",
            "mfgPartNumber": "Αρ. Κατασκευαστή",
            "images": "Εικόνες",
            "totalStock": "Συνολικό Απόθεμα",
            "low": "ΧΑΜΗΛΟ",
            "byWarehouse": "Ανά Αποθήκη",
            "noInventoryData": "Δεν υπάρχουν διαθέσιμα δεδομένα αποθέματος"
        }
    },
    "ar": {
        "partCard": {
            "partNumber": "رقم القطعة",
            "description": "الوصف",
            "unit": "الوحدة",
            "manufacturer": "الشركة المصنعة",
            "partCode": "كود القطعة",
            "serialNumber": "الرقم التسلسلي",
            "mfgPartNumber": "رقم الشركة المصنعة",
            "images": "الصور",
            "totalStock": "إجمالي المخزون",
            "low": "منخفض",
            "byWarehouse": "حسب المستودع",
            "noInventoryData": "لا توجد بيانات مخزون متاحة"
        }
    },
    "es": {
        "partCard": {
            "partNumber": "N° de Pieza",
            "description": "Descripción",
            "unit": "Unidad",
            "manufacturer": "Fabricante",
            "partCode": "Código de Pieza",
            "serialNumber": "N° de Serie",
            "mfgPartNumber": "N° de Fab.",
            "images": "Imágenes",
            "totalStock": "Stock Total",
            "low": "BAJO",
            "byWarehouse": "Por Almacén",
            "noInventoryData": "No hay datos de inventario disponibles"
        }
    },
    "tr": {
        "partCard": {
            "partNumber": "Parça No",
            "description": "Açıklama",
            "unit": "Birim",
            "manufacturer": "Üretici",
            "partCode": "Parça Kodu",
            "serialNumber": "Seri No",
            "mfgPartNumber": "Üretici Parça No",
            "images": "Resimler",
            "totalStock": "Toplam Stok",
            "low": "DÜŞÜK",
            "byWarehouse": "Depoya Göre",
            "noInventoryData": "Envanter verisi mevcut değil"
        }
    },
    "no": {
        "partCard": {
            "partNumber": "Delnr.",
            "description": "Beskrivelse",
            "unit": "Enhet",
            "manufacturer": "Produsent",
            "partCode": "Delkode",
            "serialNumber": "Serienr.",
            "mfgPartNumber": "Prod. Delnr.",
            "images": "Bilder",
            "totalStock": "Totalt Lager",
            "low": "LAV",
            "byWarehouse": "Etter Lager",
            "noInventoryData": "Ingen lagerdata tilgjengelig"
        }
    }
}

def deep_merge(base, updates):
    """Recursively merge updates into base dictionary"""
    for key, value in updates.items():
        if key in base and isinstance(base[key], dict) and isinstance(value, dict):
            deep_merge(base[key], value)
        else:
            base[key] = value
    return base

# Update each language file
for lang, new_translations in translations.items():
    filename = f'frontend/src/locales/{lang}.json'
    
    # Read existing translations
    with open(filename, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Merge new translations
    data = deep_merge(data, new_translations)
    
    # Write back with proper formatting
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write('\n')
    
    print(f"✓ Updated {filename}")

print("\n✅ All translation files updated successfully!")
print("\nNew keys added for PartCard component")
