#!/usr/bin/env python3
"""
Add tour/wizard translation keys to all locale files
"""

import json
import os

# Define the tour translations
tour_translations = {
    "en": {
        "tour": {
            "helpButton": "Need help? Click for guided tours",
            "menuTitle": "Guided Tours",
            "menuDescription": "Learn how to use ABParts with step-by-step guides",
            "menuFooter": "Click any tour to get started",
            "back": "Back",
            "close": "Close",
            "finish": "Finish",
            "next": "Next",
            "skip": "Skip",
            "partsOrdering": {
                "title": "How to Order Parts",
                "description": "Learn to place orders, track them, and receive parts into your warehouse"
            },
            "partsUsage": {
                "title": "How to Record Part Usage",
                "description": "Track parts consumed during machine operation and maintenance"
            },
            "dailyOperations": {
                "title": "How to Record Daily Services",
                "description": "Log daily machine operations, metrics, and maintenance checks"
            },
            "scheduledMaintenance": {
                "title": "How to Record Scheduled Services",
                "description": "Execute maintenance protocols and track service completion"
            }
        }
    },
    "el": {
        "tour": {
            "helpButton": "Χρειάζεστε βοήθεια; Κάντε κλικ για οδηγούς",
            "menuTitle": "Οδηγοί Εκμάθησης",
            "menuDescription": "Μάθετε πώς να χρησιμοποιείτε το ABParts με βήμα προς βήμα οδηγίες",
            "menuFooter": "Κάντε κλικ σε οποιονδήποτε οδηγό για να ξεκινήσετε",
            "back": "Πίσω",
            "close": "Κλείσιμο",
            "finish": "Τέλος",
            "next": "Επόμενο",
            "skip": "Παράλειψη",
            "partsOrdering": {
                "title": "Πώς να Παραγγείλετε Ανταλλακτικά",
                "description": "Μάθετε να κάνετε παραγγελίες, να τις παρακολουθείτε και να παραλαμβάνετε ανταλλακτικά"
            },
            "partsUsage": {
                "title": "Πώς να Καταγράψετε Χρήση Ανταλλακτικών",
                "description": "Παρακολουθήστε τα ανταλλακτικά που καταναλώνονται κατά τη λειτουργία μηχανημάτων"
            },
            "dailyOperations": {
                "title": "Πώς να Καταγράψετε Ημερήσιες Υπηρεσίες",
                "description": "Καταγράψτε ημερήσιες λειτουργίες μηχανημάτων και ελέγχους συντήρησης"
            },
            "scheduledMaintenance": {
                "title": "Πώς να Καταγράψετε Προγραμματισμένες Υπηρεσίες",
                "description": "Εκτελέστε πρωτόκολλα συντήρησης και παρακολουθήστε την ολοκλήρωση"
            }
        }
    },
    "ar": {
        "tour": {
            "helpButton": "تحتاج مساعدة؟ انقر للحصول على جولات إرشادية",
            "menuTitle": "الجولات الإرشادية",
            "menuDescription": "تعلم كيفية استخدام ABParts مع أدلة خطوة بخطوة",
            "menuFooter": "انقر على أي جولة للبدء",
            "back": "السابق",
            "close": "إغلاق",
            "finish": "إنهاء",
            "next": "التالي",
            "skip": "تخطي",
            "partsOrdering": {
                "title": "كيفية طلب قطع الغيار",
                "description": "تعلم كيفية تقديم الطلبات وتتبعها واستلام قطع الغيار في المستودع"
            },
            "partsUsage": {
                "title": "كيفية تسجيل استخدام قطع الغيار",
                "description": "تتبع قطع الغيار المستهلكة أثناء تشغيل الآلات والصيانة"
            },
            "dailyOperations": {
                "title": "كيفية تسجيل الخدمات اليومية",
                "description": "سجل العمليات اليومية للآلات والمقاييس وفحوصات الصيانة"
            },
            "scheduledMaintenance": {
                "title": "كيفية تسجيل الخدمات المجدولة",
                "description": "تنفيذ بروتوكولات الصيانة وتتبع إنجاز الخدمة"
            }
        }
    },
    "es": {
        "tour": {
            "helpButton": "¿Necesitas ayuda? Haz clic para tours guiados",
            "menuTitle": "Tours Guiados",
            "menuDescription": "Aprende a usar ABParts con guías paso a paso",
            "menuFooter": "Haz clic en cualquier tour para comenzar",
            "back": "Atrás",
            "close": "Cerrar",
            "finish": "Finalizar",
            "next": "Siguiente",
            "skip": "Omitir",
            "partsOrdering": {
                "title": "Cómo Pedir Repuestos",
                "description": "Aprende a hacer pedidos, rastrearlos y recibir repuestos en tu almacén"
            },
            "partsUsage": {
                "title": "Cómo Registrar Uso de Repuestos",
                "description": "Rastrea repuestos consumidos durante operación y mantenimiento de máquinas"
            },
            "dailyOperations": {
                "title": "Cómo Registrar Servicios Diarios",
                "description": "Registra operaciones diarias de máquinas, métricas y verificaciones de mantenimiento"
            },
            "scheduledMaintenance": {
                "title": "Cómo Registrar Servicios Programados",
                "description": "Ejecuta protocolos de mantenimiento y rastrea la finalización del servicio"
            }
        }
    },
    "tr": {
        "tour": {
            "helpButton": "Yardıma mı ihtiyacınız var? Rehberli turlar için tıklayın",
            "menuTitle": "Rehberli Turlar",
            "menuDescription": "Adım adım kılavuzlarla ABParts'ı nasıl kullanacağınızı öğrenin",
            "menuFooter": "Başlamak için herhangi bir tura tıklayın",
            "back": "Geri",
            "close": "Kapat",
            "finish": "Bitir",
            "next": "İleri",
            "skip": "Atla",
            "partsOrdering": {
                "title": "Parça Nasıl Sipariş Edilir",
                "description": "Sipariş vermeyi, takip etmeyi ve parçaları deponuza almayı öğrenin"
            },
            "partsUsage": {
                "title": "Parça Kullanımı Nasıl Kaydedilir",
                "description": "Makine işletimi ve bakımı sırasında tüketilen parçaları takip edin"
            },
            "dailyOperations": {
                "title": "Günlük Hizmetler Nasıl Kaydedilir",
                "description": "Günlük makine işlemlerini, metrikleri ve bakım kontrollerini kaydedin"
            },
            "scheduledMaintenance": {
                "title": "Planlı Hizmetler Nasıl Kaydedilir",
                "description": "Bakım protokollerini yürütün ve hizmet tamamlanmasını takip edin"
            }
        }
    },
    "no": {
        "tour": {
            "helpButton": "Trenger du hjelp? Klikk for guidede turer",
            "menuTitle": "Guidede Turer",
            "menuDescription": "Lær hvordan du bruker ABParts med steg-for-steg guider",
            "menuFooter": "Klikk på hvilken som helst tur for å komme i gang",
            "back": "Tilbake",
            "close": "Lukk",
            "finish": "Fullfør",
            "next": "Neste",
            "skip": "Hopp over",
            "partsOrdering": {
                "title": "Hvordan Bestille Deler",
                "description": "Lær å legge inn bestillinger, spore dem og motta deler til lageret ditt"
            },
            "partsUsage": {
                "title": "Hvordan Registrere Delbruk",
                "description": "Spor deler som forbrukes under maskindrift og vedlikehold"
            },
            "dailyOperations": {
                "title": "Hvordan Registrere Daglige Tjenester",
                "description": "Logg daglige maskinoperasjoner, målinger og vedlikeholdskontroller"
            },
            "scheduledMaintenance": {
                "title": "Hvordan Registrere Planlagte Tjenester",
                "description": "Utfør vedlikeholdsprotokoller og spor tjenestens fullføring"
            }
        }
    }
}

def add_translations_to_file(file_path, translations):
    """Add translations to a JSON file"""
    try:
        # Read existing translations
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Add tour translations
        data.update(translations)
        
        # Write back to file
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Updated {file_path}")
        
    except Exception as e:
        print(f"❌ Error updating {file_path}: {e}")

def main():
    """Add tour translations to all locale files"""
    print("Adding tour translations to locale files...")
    
    locales_dir = "frontend/src/locales"
    
    for lang_code, translations in tour_translations.items():
        file_path = os.path.join(locales_dir, f"{lang_code}.json")
        if os.path.exists(file_path):
            add_translations_to_file(file_path, translations)
        else:
            print(f"⚠️  Locale file not found: {file_path}")
    
    print("\n🎉 Tour translations added successfully!")
    print("\nNext steps:")
    print("1. Install React Joyride: npm install react-joyride")
    print("2. Add TourProvider to App.js")
    print("3. Add TourButton to Layout.js")
    print("4. Add data-tour attributes to UI elements")

if __name__ == "__main__":
    main()