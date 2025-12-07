#!/usr/bin/env python3
"""
Add part category translations to all locale files
"""

import json
import os

# Translation data for all languages
translations = {
    "en": {
        "partForm": {
            "partNumber": "Part Number",
            "partNameMultilingual": "Part Name (Multilingual)",
            "enterPartName": "Enter part name...",
            "description": "Description",
            "partCategory": "Part Category",
            "unitOfMeasure": "Unit of Measure",
            "manufacturerPartNumber": "Manufacturer Part Number",
            "proprietary": "Proprietary Part (BossAqua)",
            "manufacturerDeliveryTime": "Manufacturer Delivery Time (days)",
            "localSupplierDeliveryTime": "Local Supplier Delivery Time (days)",
            "submitting": "Submitting...",
            "createPart": "Create Part",
            "updatePart": "Update Part",
            "units": {
                "pieces": "Pieces",
                "liters": "Liters",
                "kilograms": "Kilograms",
                "meters": "Meters",
                "gallons": "Gallons",
                "pounds": "Pounds",
                "feet": "Feet",
                "boxes": "Boxes",
                "sets": "Sets"
            },
            "categories": {
                "consumable": "Consumable",
                "consumableShort": "CONS",
                "consumableDesc": "Whole units (pieces, sets, boxes)",
                "bulkMaterial": "Bulk Material",
                "bulkMaterialShort": "BULK",
                "bulkMaterialDesc": "Measurable quantities (liters, kg, meters)",
                "bossAqua": "BossAqua",
                "allTypes": "All Types"
            }
        }
    },
    "el": {
        "partForm": {
            "partNumber": "Αριθμός Ανταλλακτικού",
            "partNameMultilingual": "Όνομα Ανταλλακτικού (Πολυγλωσσικό)",
            "enterPartName": "Εισάγετε όνομα ανταλλακτικού...",
            "description": "Περιγραφή",
            "partCategory": "Κατηγορία Ανταλλακτικού",
            "unitOfMeasure": "Μονάδα Μέτρησης",
            "manufacturerPartNumber": "Αριθμός Κατασκευαστή",
            "proprietary": "Ιδιόκτητο Ανταλλακτικό (BossAqua)",
            "manufacturerDeliveryTime": "Χρόνος Παράδοσης Κατασκευαστή (ημέρες)",
            "localSupplierDeliveryTime": "Χρόνος Παράδοσης Τοπικού Προμηθευτή (ημέρες)",
            "submitting": "Υποβολή...",
            "createPart": "Δημιουργία Ανταλλακτικού",
            "updatePart": "Ενημέρωση Ανταλλακτικού",
            "units": {
                "pieces": "Τεμάχια",
                "liters": "Λίτρα",
                "kilograms": "Κιλά",
                "meters": "Μέτρα",
                "gallons": "Γαλόνια",
                "pounds": "Λίβρες",
                "feet": "Πόδια",
                "boxes": "Κουτιά",
                "sets": "Σετ"
            },
            "categories": {
                "consumable": "Αναλώσιμο",
                "consumableShort": "ΑΝΑΛ",
                "consumableDesc": "Ολόκληρες μονάδες (τεμάχια, σετ, κουτιά)",
                "bulkMaterial": "Χύδην Υλικό",
                "bulkMaterialShort": "ΧΥΔΗΝ",
                "bulkMaterialDesc": "Μετρήσιμες ποσότητες (λίτρα, κιλά, μέτρα)",
                "bossAqua": "BossAqua",
                "allTypes": "Όλοι οι Τύποι"
            }
        }
    },
    "ar": {
        "partForm": {
            "partNumber": "رقم القطعة",
            "partNameMultilingual": "اسم القطعة (متعدد اللغات)",
            "enterPartName": "أدخل اسم القطعة...",
            "description": "الوصف",
            "partCategory": "فئة القطعة",
            "unitOfMeasure": "وحدة القياس",
            "manufacturerPartNumber": "رقم قطعة الشركة المصنعة",
            "proprietary": "قطعة خاصة (BossAqua)",
            "manufacturerDeliveryTime": "وقت التسليم من الشركة المصنعة (أيام)",
            "localSupplierDeliveryTime": "وقت التسليم من المورد المحلي (أيام)",
            "submitting": "جاري الإرسال...",
            "createPart": "إنشاء قطعة",
            "updatePart": "تحديث القطعة",
            "units": {
                "pieces": "قطع",
                "liters": "لترات",
                "kilograms": "كيلوغرامات",
                "meters": "أمتار",
                "gallons": "جالونات",
                "pounds": "أرطال",
                "feet": "أقدام",
                "boxes": "صناديق",
                "sets": "مجموعات"
            },
            "categories": {
                "consumable": "مستهلكة",
                "consumableShort": "مستهلك",
                "consumableDesc": "وحدات كاملة (قطع، مجموعات، صناديق)",
                "bulkMaterial": "مواد سائبة",
                "bulkMaterialShort": "سائب",
                "bulkMaterialDesc": "كميات قابلة للقياس (لترات، كيلوغرامات، أمتار)",
                "bossAqua": "BossAqua",
                "allTypes": "جميع الأنواع"
            }
        }
    },
    "es": {
        "partForm": {
            "partNumber": "Número de Pieza",
            "partNameMultilingual": "Nombre de Pieza (Multilingüe)",
            "enterPartName": "Ingrese nombre de pieza...",
            "description": "Descripción",
            "partCategory": "Categoría de Pieza",
            "unitOfMeasure": "Unidad de Medida",
            "manufacturerPartNumber": "Número de Pieza del Fabricante",
            "proprietary": "Pieza Propietaria (BossAqua)",
            "manufacturerDeliveryTime": "Tiempo de Entrega del Fabricante (días)",
            "localSupplierDeliveryTime": "Tiempo de Entrega del Proveedor Local (días)",
            "submitting": "Enviando...",
            "createPart": "Crear Pieza",
            "updatePart": "Actualizar Pieza",
            "units": {
                "pieces": "Piezas",
                "liters": "Litros",
                "kilograms": "Kilogramos",
                "meters": "Metros",
                "gallons": "Galones",
                "pounds": "Libras",
                "feet": "Pies",
                "boxes": "Cajas",
                "sets": "Conjuntos"
            },
            "categories": {
                "consumable": "Consumible",
                "consumableShort": "CONS",
                "consumableDesc": "Unidades completas (piezas, conjuntos, cajas)",
                "bulkMaterial": "Material a Granel",
                "bulkMaterialShort": "GRANEL",
                "bulkMaterialDesc": "Cantidades medibles (litros, kg, metros)",
                "bossAqua": "BossAqua",
                "allTypes": "Todos los Tipos"
            }
        }
    },
    "tr": {
        "partForm": {
            "partNumber": "Parça Numarası",
            "partNameMultilingual": "Parça Adı (Çok Dilli)",
            "enterPartName": "Parça adını girin...",
            "description": "Açıklama",
            "partCategory": "Parça Kategorisi",
            "unitOfMeasure": "Ölçü Birimi",
            "manufacturerPartNumber": "Üretici Parça Numarası",
            "proprietary": "Özel Parça (BossAqua)",
            "manufacturerDeliveryTime": "Üretici Teslimat Süresi (gün)",
            "localSupplierDeliveryTime": "Yerel Tedarikçi Teslimat Süresi (gün)",
            "submitting": "Gönderiliyor...",
            "createPart": "Parça Oluştur",
            "updatePart": "Parçayı Güncelle",
            "units": {
                "pieces": "Adet",
                "liters": "Litre",
                "kilograms": "Kilogram",
                "meters": "Metre",
                "gallons": "Galon",
                "pounds": "Pound",
                "feet": "Fit",
                "boxes": "Kutu",
                "sets": "Set"
            },
            "categories": {
                "consumable": "Sarf Malzemesi",
                "consumableShort": "SARF",
                "consumableDesc": "Tam birimler (adet, set, kutu)",
                "bulkMaterial": "Dökme Malzeme",
                "bulkMaterialShort": "DÖKME",
                "bulkMaterialDesc": "Ölçülebilir miktarlar (litre, kg, metre)",
                "bossAqua": "BossAqua",
                "allTypes": "Tüm Tipler"
            }
        }
    },
    "no": {
        "partForm": {
            "partNumber": "Delenummer",
            "partNameMultilingual": "Delenavn (Flerspråklig)",
            "enterPartName": "Skriv inn delenavn...",
            "description": "Beskrivelse",
            "partCategory": "Delkategori",
            "unitOfMeasure": "Måleenhet",
            "manufacturerPartNumber": "Produsentens Delenummer",
            "proprietary": "Proprietær Del (BossAqua)",
            "manufacturerDeliveryTime": "Produsentens Leveringstid (dager)",
            "localSupplierDeliveryTime": "Lokal Leverandørs Leveringstid (dager)",
            "submitting": "Sender inn...",
            "createPart": "Opprett Del",
            "updatePart": "Oppdater Del",
            "units": {
                "pieces": "Stykker",
                "liters": "Liter",
                "kilograms": "Kilogram",
                "meters": "Meter",
                "gallons": "Gallons",
                "pounds": "Pund",
                "feet": "Fot",
                "boxes": "Bokser",
                "sets": "Sett"
            },
            "categories": {
                "consumable": "Forbruksvare",
                "consumableShort": "FORBR",
                "consumableDesc": "Hele enheter (stykker, sett, bokser)",
                "bulkMaterial": "Bulkmateriale",
                "bulkMaterialShort": "BULK",
                "bulkMaterialDesc": "Målbare mengder (liter, kg, meter)",
                "bossAqua": "BossAqua",
                "allTypes": "Alle Typer"
            }
        }
    }
}

def update_locale_file(lang_code, new_translations):
    """Update a locale file with new translations"""
    file_path = f"frontend/src/locales/{lang_code}.json"
    
    # Read existing translations
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Update with new translations
    data['partForm'] = new_translations['partForm']
    
    # Write back
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"✓ Updated {file_path}")

def main():
    for lang_code, trans in translations.items():
        update_locale_file(lang_code, trans)
    
    print("\n✅ Part category translations added to all languages!")

if __name__ == "__main__":
    main()
