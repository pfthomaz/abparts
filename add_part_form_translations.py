#!/usr/bin/env python3
import json

translations = {
    "en": {
        "partForm": {
            "partNumber": "Part Number",
            "partNameMultilingual": "Part Name (Multilingual)",
            "enterPartName": "Enter part name",
            "description": "Description",
            "partCategory": "Part Category",
            "unitOfMeasure": "Unit of Measure",
            "manufacturerPartNumber": "Manufacturer Part Number",
            "proprietary": "Proprietary (BossAqua exclusive part)",
            "manufacturerDeliveryTime": "Manufacturer Delivery Time (Days)",
            "localSupplierDeliveryTime": "Local Supplier Delivery Time (Days)",
            "submitting": "Submitting...",
            "updatePart": "Update Part",
            "createPart": "Create Part",
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
            }
        }
    },
    "el": {
        "partForm": {
            "partNumber": "Αριθμός Ανταλλακτικού",
            "partNameMultilingual": "Όνομα Ανταλλακτικού (Πολύγλωσσο)",
            "enterPartName": "Εισάγετε όνομα ανταλλακτικού",
            "description": "Περιγραφή",
            "partCategory": "Κατηγορία Ανταλλακτικού",
            "unitOfMeasure": "Μονάδα Μέτρησης",
            "manufacturerPartNumber": "Αριθμός Ανταλλακτικού Κατασκευαστή",
            "proprietary": "Ιδιόκτητο (Αποκλειστικό ανταλλακτικό BossAqua)",
            "manufacturerDeliveryTime": "Χρόνος Παράδοσης Κατασκευαστή (Ημέρες)",
            "localSupplierDeliveryTime": "Χρόνος Παράδοσης Τοπικού Προμηθευτή (Ημέρες)",
            "submitting": "Υποβολή...",
            "updatePart": "Ενημέρωση Ανταλλακτικού",
            "createPart": "Δημιουργία Ανταλλακτικού",
            "units": {
                "pieces": "Τεμάχια",
                "liters": "Λίτρα",
                "kilograms": "Χιλιόγραμμα",
                "meters": "Μέτρα",
                "gallons": "Γαλόνια",
                "pounds": "Λίβρες",
                "feet": "Πόδια",
                "boxes": "Κουτιά",
                "sets": "Σετ"
            }
        }
    },
    "ar": {
        "partForm": {
            "partNumber": "رقم القطعة",
            "partNameMultilingual": "اسم القطعة (متعدد اللغات)",
            "enterPartName": "أدخل اسم القطعة",
            "description": "الوصف",
            "partCategory": "فئة القطعة",
            "unitOfMeasure": "وحدة القياس",
            "manufacturerPartNumber": "رقم قطعة الشركة المصنعة",
            "proprietary": "خاص (قطعة حصرية من BossAqua)",
            "manufacturerDeliveryTime": "وقت تسليم الشركة المصنعة (أيام)",
            "localSupplierDeliveryTime": "وقت تسليم المورد المحلي (أيام)",
            "submitting": "جاري الإرسال...",
            "updatePart": "تحديث القطعة",
            "createPart": "إنشاء قطعة",
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
            }
        }
    },
    "es": {
        "partForm": {
            "partNumber": "Número de Pieza",
            "partNameMultilingual": "Nombre de Pieza (Multilingüe)",
            "enterPartName": "Ingrese nombre de pieza",
            "description": "Descripción",
            "partCategory": "Categoría de Pieza",
            "unitOfMeasure": "Unidad de Medida",
            "manufacturerPartNumber": "Número de Pieza del Fabricante",
            "proprietary": "Propietario (Pieza exclusiva de BossAqua)",
            "manufacturerDeliveryTime": "Tiempo de Entrega del Fabricante (Días)",
            "localSupplierDeliveryTime": "Tiempo de Entrega del Proveedor Local (Días)",
            "submitting": "Enviando...",
            "updatePart": "Actualizar Pieza",
            "createPart": "Crear Pieza",
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
            }
        }
    },
    "tr": {
        "partForm": {
            "partNumber": "Parça Numarası",
            "partNameMultilingual": "Parça Adı (Çok Dilli)",
            "enterPartName": "Parça adı girin",
            "description": "Açıklama",
            "partCategory": "Parça Kategorisi",
            "unitOfMeasure": "Ölçü Birimi",
            "manufacturerPartNumber": "Üretici Parça Numarası",
            "proprietary": "Özel (BossAqua özel parçası)",
            "manufacturerDeliveryTime": "Üretici Teslimat Süresi (Gün)",
            "localSupplierDeliveryTime": "Yerel Tedarikçi Teslimat Süresi (Gün)",
            "submitting": "Gönderiliyor...",
            "updatePart": "Parçayı Güncelle",
            "createPart": "Parça Oluştur",
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
            }
        }
    },
    "no": {
        "partForm": {
            "partNumber": "Delnummer",
            "partNameMultilingual": "Delnavn (Flerspråklig)",
            "enterPartName": "Skriv inn delnavn",
            "description": "Beskrivelse",
            "partCategory": "Delkategori",
            "unitOfMeasure": "Måleenhet",
            "manufacturerPartNumber": "Produsentens Delnummer",
            "proprietary": "Proprietær (BossAqua eksklusiv del)",
            "manufacturerDeliveryTime": "Produsent Leveringstid (Dager)",
            "localSupplierDeliveryTime": "Lokal Leverandør Leveringstid (Dager)",
            "submitting": "Sender inn...",
            "updatePart": "Oppdater Del",
            "createPart": "Opprett Del",
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
            }
        }
    }
}

def deep_merge(base, updates):
    for key, value in updates.items():
        if key in base and isinstance(base[key], dict) and isinstance(value, dict):
            deep_merge(base[key], value)
        else:
            base[key] = value
    return base

for lang, new_translations in translations.items():
    filename = f'frontend/src/locales/{lang}.json'
    with open(filename, 'r', encoding='utf-8') as f:
        data = json.load(f)
    data = deep_merge(data, new_translations)
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write('\n')
    print(f"✓ Updated {filename}")

print("\n✅ PartForm translations added!")
