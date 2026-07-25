#!/usr/bin/env python3
"""
Add enhanced tour translation keys including button labels and detailed step content
"""

import json
import os

# Define the enhanced tour translations
enhanced_tour_translations = {
    "en": {
        "tour": {
            "helpButton": "Need help? Click for guided tours",
            "menuTitle": "Guided Tours",
            "menuDescription": "Learn how to use ABParts with step-by-step guides",
            "menuFooter": "Choose Quick Guide for overview or Interactive for hands-on experience",
            "back": "Back",
            "close": "Close",
            "finish": "Finish",
            "next": "Next",
            "skip": "Skip",
            "quickGuide": "Quick Guide",
            "interactive": "Interactive",
            "partsOrdering": {
                "title": "How to Order Parts",
                "description": "Learn to place orders, track them, and receive parts into your warehouse",
                "step1": "Find Orders",
                "step2": "Create New Order",
                "step3": "Select Order Type",
                "step4": "Search Parts",
                "step5": "Set Quantities",
                "step6": "Submit & Track"
            },
            "partsUsage": {
                "title": "How to Record Part Usage",
                "description": "Track parts consumed during machine operation and maintenance",
                "step1": "Go to Machines",
                "step2": "Select Machine",
                "step3": "Record Usage",
                "step4": "Find Part",
                "step5": "Enter Quantity"
            },
            "dailyOperations": {
                "title": "How to Record Daily Services",
                "description": "Log daily machine operations, metrics, and maintenance checks",
                "step1": "Navigate Here",
                "step2": "Choose Date & Machine",
                "step3": "Enter Metrics",
                "step4": "Complete Checklist",
                "step5": "Submit Report"
            },
            "scheduledMaintenance": {
                "title": "How to Record Scheduled Services",
                "description": "Execute maintenance protocols and track service completion",
                "step1": "Find Maintenance",
                "step2": "Choose Protocol",
                "step3": "Assign Resources",
                "step4": "Execute Checklist",
                "step5": "Document Work",
                "step6": "Complete & Schedule"
            }
        }
    },
    "el": {
        "tour": {
            "helpButton": "Χρειάζεστε βοήθεια; Κάντε κλικ για οδηγούς",
            "menuTitle": "Οδηγοί Εκμάθησης",
            "menuDescription": "Μάθετε πώς να χρησιμοποιείτε το ABParts με βήμα προς βήμα οδηγίες",
            "menuFooter": "Επιλέξτε Γρήγορο Οδηγό για επισκόπηση ή Διαδραστικό για πρακτική εμπειρία",
            "back": "Πίσω",
            "close": "Κλείσιμο",
            "finish": "Τέλος",
            "next": "Επόμενο",
            "skip": "Παράλειψη",
            "quickGuide": "Γρήγορος Οδηγός",
            "interactive": "Διαδραστικό",
            "partsOrdering": {
                "title": "Πώς να Παραγγείλετε Ανταλλακτικά",
                "description": "Μάθετε να κάνετε παραγγελίες, να τις παρακολουθείτε και να παραλαμβάνετε ανταλλακτικά",
                "step1": "Βρείτε Παραγγελίες",
                "step2": "Δημιουργήστε Νέα Παραγγελία",
                "step3": "Επιλέξτε Τύπο Παραγγελίας",
                "step4": "Αναζητήστε Ανταλλακτικά",
                "step5": "Ορίστε Ποσότητες",
                "step6": "Υποβάλετε & Παρακολουθήστε"
            },
            "partsUsage": {
                "title": "Πώς να Καταγράψετε Χρήση Ανταλλακτικών",
                "description": "Παρακολουθήστε τα ανταλλακτικά που καταναλώνονται κατά τη λειτουργία μηχανημάτων",
                "step1": "Πηγαίνετε στα Μηχανήματα",
                "step2": "Επιλέξτε Μηχάνημα",
                "step3": "Καταγράψτε Χρήση",
                "step4": "Βρείτε Ανταλλακτικό",
                "step5": "Εισάγετε Ποσότητα"
            },
            "dailyOperations": {
                "title": "Πώς να Καταγράψετε Ημερήσιες Υπηρεσίες",
                "description": "Καταγράψτε ημερήσιες λειτουργίες μηχανημάτων και ελέγχους συντήρησης",
                "step1": "Πλοηγηθείτε Εδώ",
                "step2": "Επιλέξτε Ημερομηνία & Μηχάνημα",
                "step3": "Εισάγετε Μετρήσεις",
                "step4": "Ολοκληρώστε τη Λίστα Ελέγχου",
                "step5": "Υποβάλετε Αναφορά"
            },
            "scheduledMaintenance": {
                "title": "Πώς να Καταγράψετε Προγραμματισμένες Υπηρεσίες",
                "description": "Εκτελέστε πρωτόκολλα συντήρησης και παρακολουθήστε την ολοκλήρωση",
                "step1": "Βρείτε Συντήρηση",
                "step2": "Επιλέξτε Πρωτόκολλο",
                "step3": "Αναθέστε Πόρους",
                "step4": "Εκτελέστε Λίστα Ελέγχου",
                "step5": "Τεκμηριώστε Εργασία",
                "step6": "Ολοκληρώστε & Προγραμματίστε"
            }
        }
    },
    "ar": {
        "tour": {
            "helpButton": "تحتاج مساعدة؟ انقر للحصول على جولات إرشادية",
            "menuTitle": "الجولات الإرشادية",
            "menuDescription": "تعلم كيفية استخدام ABParts مع أدلة خطوة بخطوة",
            "menuFooter": "اختر الدليل السريع للنظرة العامة أو التفاعلي للتجربة العملية",
            "back": "السابق",
            "close": "إغلاق",
            "finish": "إنهاء",
            "next": "التالي",
            "skip": "تخطي",
            "quickGuide": "دليل سريع",
            "interactive": "تفاعلي",
            "partsOrdering": {
                "title": "كيفية طلب قطع الغيار",
                "description": "تعلم كيفية تقديم الطلبات وتتبعها واستلام قطع الغيار في المستودع",
                "step1": "العثور على الطلبات",
                "step2": "إنشاء طلب جديد",
                "step3": "اختيار نوع الطلب",
                "step4": "البحث عن القطع",
                "step5": "تحديد الكميات",
                "step6": "الإرسال والتتبع"
            },
            "partsUsage": {
                "title": "كيفية تسجيل استخدام قطع الغيار",
                "description": "تتبع قطع الغيار المستهلكة أثناء تشغيل الآلات والصيانة",
                "step1": "الذهاب إلى الآلات",
                "step2": "اختيار الآلة",
                "step3": "تسجيل الاستخدام",
                "step4": "العثور على القطعة",
                "step5": "إدخال الكمية"
            },
            "dailyOperations": {
                "title": "كيفية تسجيل الخدمات اليومية",
                "description": "سجل العمليات اليومية للآلات والمقاييس وفحوصات الصيانة",
                "step1": "التنقل هنا",
                "step2": "اختيار التاريخ والآلة",
                "step3": "إدخال المقاييس",
                "step4": "إكمال قائمة التحقق",
                "step5": "إرسال التقرير"
            },
            "scheduledMaintenance": {
                "title": "كيفية تسجيل الخدمات المجدولة",
                "description": "تنفيذ بروتوكولات الصيانة وتتبع إنجاز الخدمة",
                "step1": "العثور على الصيانة",
                "step2": "اختيار البروتوكول",
                "step3": "تخصيص الموارد",
                "step4": "تنفيذ قائمة التحقق",
                "step5": "توثيق العمل",
                "step6": "الإكمال والجدولة"
            }
        }
    },
    "es": {
        "tour": {
            "helpButton": "¿Necesitas ayuda? Haz clic para tours guiados",
            "menuTitle": "Tours Guiados",
            "menuDescription": "Aprende a usar ABParts con guías paso a paso",
            "menuFooter": "Elige Guía Rápida para resumen o Interactivo para experiencia práctica",
            "back": "Atrás",
            "close": "Cerrar",
            "finish": "Finalizar",
            "next": "Siguiente",
            "skip": "Omitir",
            "quickGuide": "Guía Rápida",
            "interactive": "Interactivo",
            "partsOrdering": {
                "title": "Cómo Pedir Repuestos",
                "description": "Aprende a hacer pedidos, rastrearlos y recibir repuestos en tu almacén",
                "step1": "Encontrar Pedidos",
                "step2": "Crear Nuevo Pedido",
                "step3": "Seleccionar Tipo de Pedido",
                "step4": "Buscar Repuestos",
                "step5": "Establecer Cantidades",
                "step6": "Enviar y Rastrear"
            },
            "partsUsage": {
                "title": "Cómo Registrar Uso de Repuestos",
                "description": "Rastrea repuestos consumidos durante operación y mantenimiento de máquinas",
                "step1": "Ir a Máquinas",
                "step2": "Seleccionar Máquina",
                "step3": "Registrar Uso",
                "step4": "Encontrar Repuesto",
                "step5": "Ingresar Cantidad"
            },
            "dailyOperations": {
                "title": "Cómo Registrar Servicios Diarios",
                "description": "Registra operaciones diarias de máquinas, métricas y verificaciones de mantenimiento",
                "step1": "Navegar Aquí",
                "step2": "Elegir Fecha y Máquina",
                "step3": "Ingresar Métricas",
                "step4": "Completar Lista de Verificación",
                "step5": "Enviar Reporte"
            },
            "scheduledMaintenance": {
                "title": "Cómo Registrar Servicios Programados",
                "description": "Ejecuta protocolos de mantenimiento y rastrea la finalización del servicio",
                "step1": "Encontrar Mantenimiento",
                "step2": "Elegir Protocolo",
                "step3": "Asignar Recursos",
                "step4": "Ejecutar Lista de Verificación",
                "step5": "Documentar Trabajo",
                "step6": "Completar y Programar"
            }
        }
    },
    "tr": {
        "tour": {
            "helpButton": "Yardıma mı ihtiyacınız var? Rehberli turlar için tıklayın",
            "menuTitle": "Rehberli Turlar",
            "menuDescription": "Adım adım kılavuzlarla ABParts'ı nasıl kullanacağınızı öğrenin",
            "menuFooter": "Genel bakış için Hızlı Kılavuz'u veya uygulamalı deneyim için Etkileşimli'yi seçin",
            "back": "Geri",
            "close": "Kapat",
            "finish": "Bitir",
            "next": "İleri",
            "skip": "Atla",
            "quickGuide": "Hızlı Kılavuz",
            "interactive": "Etkileşimli",
            "partsOrdering": {
                "title": "Parça Nasıl Sipariş Edilir",
                "description": "Sipariş vermeyi, takip etmeyi ve parçaları deponuza almayı öğrenin",
                "step1": "Siparişleri Bul",
                "step2": "Yeni Sipariş Oluştur",
                "step3": "Sipariş Türünü Seç",
                "step4": "Parça Ara",
                "step5": "Miktarları Belirle",
                "step6": "Gönder ve Takip Et"
            },
            "partsUsage": {
                "title": "Parça Kullanımı Nasıl Kaydedilir",
                "description": "Makine işletimi ve bakımı sırasında tüketilen parçaları takip edin",
                "step1": "Makinelere Git",
                "step2": "Makine Seç",
                "step3": "Kullanımı Kaydet",
                "step4": "Parçayı Bul",
                "step5": "Miktarı Gir"
            },
            "dailyOperations": {
                "title": "Günlük Hizmetler Nasıl Kaydedilir",
                "description": "Günlük makine işlemlerini, metrikleri ve bakım kontrollerini kaydedin",
                "step1": "Buraya Git",
                "step2": "Tarih ve Makine Seç",
                "step3": "Metrikleri Gir",
                "step4": "Kontrol Listesini Tamamla",
                "step5": "Raporu Gönder"
            },
            "scheduledMaintenance": {
                "title": "Planlı Hizmetler Nasıl Kaydedilir",
                "description": "Bakım protokollerini yürütün ve hizmet tamamlanmasını takip edin",
                "step1": "Bakımı Bul",
                "step2": "Protokol Seç",
                "step3": "Kaynakları Ata",
                "step4": "Kontrol Listesini Yürüt",
                "step5": "Çalışmayı Belgele",
                "step6": "Tamamla ve Planla"
            }
        }
    },
    "no": {
        "tour": {
            "helpButton": "Trenger du hjelp? Klikk for guidede turer",
            "menuTitle": "Guidede Turer",
            "menuDescription": "Lær hvordan du bruker ABParts med steg-for-steg guider",
            "menuFooter": "Velg Hurtigguide for oversikt eller Interaktiv for praktisk erfaring",
            "back": "Tilbake",
            "close": "Lukk",
            "finish": "Fullfør",
            "next": "Neste",
            "skip": "Hopp over",
            "quickGuide": "Hurtigguide",
            "interactive": "Interaktiv",
            "partsOrdering": {
                "title": "Hvordan Bestille Deler",
                "description": "Lær å legge inn bestillinger, spore dem og motta deler til lageret ditt",
                "step1": "Finn Bestillinger",
                "step2": "Opprett Ny Bestilling",
                "step3": "Velg Bestillingstype",
                "step4": "Søk Deler",
                "step5": "Angi Mengder",
                "step6": "Send inn og Spor"
            },
            "partsUsage": {
                "title": "Hvordan Registrere Delbruk",
                "description": "Spor deler som forbrukes under maskindrift og vedlikehold",
                "step1": "Gå til Maskiner",
                "step2": "Velg Maskin",
                "step3": "Registrer Bruk",
                "step4": "Finn Del",
                "step5": "Angi Mengde"
            },
            "dailyOperations": {
                "title": "Hvordan Registrere Daglige Tjenester",
                "description": "Logg daglige maskinoperasjoner, målinger og vedlikeholdskontroller",
                "step1": "Naviger Hit",
                "step2": "Velg Dato og Maskin",
                "step3": "Angi Målinger",
                "step4": "Fullfør Sjekkliste",
                "step5": "Send inn Rapport"
            },
            "scheduledMaintenance": {
                "title": "Hvordan Registrere Planlagte Tjenester",
                "description": "Utfør vedlikeholdsprotokoller og spor tjenestens fullføring",
                "step1": "Finn Vedlikehold",
                "step2": "Velg Protokoll",
                "step3": "Tildel Ressurser",
                "step4": "Utfør Sjekkliste",
                "step5": "Dokumenter Arbeid",
                "step6": "Fullfør og Planlegg"
            }
        }
    }
}

def update_translations_file(file_path, translations):
    """Update translations in a JSON file"""
    try:
        # Read existing translations
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Merge tour translations (this will update existing keys and add new ones)
        if 'tour' in data:
            data['tour'].update(translations['tour'])
        else:
            data['tour'] = translations['tour']
        
        # Write back to file
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Updated {file_path}")
        
    except Exception as e:
        print(f"❌ Error updating {file_path}: {e}")

def main():
    """Add enhanced tour translations to all locale files"""
    print("Adding enhanced tour translations to locale files...")
    
    locales_dir = "frontend/src/locales"
    
    for lang_code, translations in enhanced_tour_translations.items():
        file_path = os.path.join(locales_dir, f"{lang_code}.json")
        if os.path.exists(file_path):
            update_translations_file(file_path, translations)
        else:
            print(f"⚠️  Locale file not found: {file_path}")
    
    print("\n🎉 Enhanced tour translations added successfully!")
    print("\nNew features added:")
    print("- Button labels (Quick Guide, Interactive)")
    print("- Enhanced menu footer text")
    print("- Step-by-step labels for each workflow")
    print("- All 6 languages fully supported")

if __name__ == "__main__":
    main()