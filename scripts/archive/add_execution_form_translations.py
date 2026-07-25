#!/usr/bin/env python3
import json

# Translation keys to add
translations = {
    "en": {
        "maintenance": {
            "quantityUsed": "Quantity Used",
            "estimatedQuantity": "Estimated: {{quantity}}",
            "notes": "Notes",
            "addObservationsPlaceholder": "Add any observations or notes",
            "completeAllCriticalItems": "Please complete all critical items before finishing ({{count}} remaining)",
            "saveAllItemsBeforeFinishing": "Please save all checklist items before finishing",
            "confirmFinishExecution": "Are you sure you want to finish this maintenance execution?",
            "executionCompletedSuccessfully": "Maintenance execution completed successfully!",
            "failedToCompleteExecution": "Failed to complete execution: {{error}}",
            "errorInitializingExecution": "Error initializing execution",
            "machine": "Machine",
            "progress": "Progress",
            "completed": "✓ Completed",
            "markAsCompleted": "Mark as completed",
            "saved": "Saved",
            "critical": "Critical",
            "failedToSaveItem": "Failed to save item: {{error}}",
            "finishMaintenance": "Finish Maintenance"
        },
        "common": {
            "goBack": "Go Back"
        }
    },
    "el": {
        "maintenance": {
            "quantityUsed": "Ποσότητα που Χρησιμοποιήθηκε",
            "estimatedQuantity": "Εκτιμώμενη: {{quantity}}",
            "notes": "Σημειώσεις",
            "addObservationsPlaceholder": "Προσθέστε παρατηρήσεις ή σημειώσεις",
            "completeAllCriticalItems": "Παρακαλώ ολοκληρώστε όλα τα κρίσιμα στοιχεία πριν την ολοκλήρωση ({{count}} απομένουν)",
            "saveAllItemsBeforeFinishing": "Παρακαλώ αποθηκεύστε όλα τα στοιχεία της λίστας πριν την ολοκλήρωση",
            "confirmFinishExecution": "Είστε σίγουροι ότι θέλετε να ολοκληρώσετε αυτή την εκτέλεση συντήρησης;",
            "executionCompletedSuccessfully": "Η εκτέλεση συντήρησης ολοκληρώθηκε με επιτυχία!",
            "failedToCompleteExecution": "Αποτυχία ολοκλήρωσης εκτέλεσης: {{error}}",
            "errorInitializingExecution": "Σφάλμα κατά την αρχικοποίηση της εκτέλεσης",
            "machine": "Μηχάνημα",
            "progress": "Πρόοδος",
            "completed": "✓ Ολοκληρώθηκε",
            "markAsCompleted": "Σημείωση ως ολοκληρωμένο",
            "saved": "Αποθηκεύτηκε",
            "critical": "Κρίσιμο",
            "failedToSaveItem": "Αποτυχία αποθήκευσης στοιχείου: {{error}}",
            "finishMaintenance": "Ολοκλήρωση Συντήρησης"
        },
        "common": {
            "goBack": "Επιστροφή"
        }
    },
    "ar": {
        "maintenance": {
            "quantityUsed": "الكمية المستخدمة",
            "estimatedQuantity": "المقدرة: {{quantity}}",
            "notes": "ملاحظات",
            "addObservationsPlaceholder": "أضف أي ملاحظات أو تعليقات",
            "completeAllCriticalItems": "يرجى إكمال جميع العناصر الحرجة قبل الإنهاء ({{count}} متبقية)",
            "saveAllItemsBeforeFinishing": "يرجى حفظ جميع عناصر القائمة قبل الإنهاء",
            "confirmFinishExecution": "هل أنت متأكد من أنك تريد إنهاء تنفيذ الصيانة هذا؟",
            "executionCompletedSuccessfully": "تم إكمال تنفيذ الصيانة بنجاح!",
            "failedToCompleteExecution": "فشل في إكمال التنفيذ: {{error}}",
            "errorInitializingExecution": "خطأ في تهيئة التنفيذ",
            "machine": "الآلة",
            "progress": "التقدم",
            "completed": "✓ مكتمل",
            "markAsCompleted": "وضع علامة كمكتمل",
            "saved": "محفوظ",
            "critical": "حرج",
            "failedToSaveItem": "فشل في حفظ العنصر: {{error}}",
            "finishMaintenance": "إنهاء الصيانة"
        },
        "common": {
            "goBack": "العودة"
        }
    },
    "es": {
        "maintenance": {
            "quantityUsed": "Cantidad Utilizada",
            "estimatedQuantity": "Estimada: {{quantity}}",
            "notes": "Notas",
            "addObservationsPlaceholder": "Añadir observaciones o notas",
            "completeAllCriticalItems": "Por favor complete todos los elementos críticos antes de finalizar ({{count}} restantes)",
            "saveAllItemsBeforeFinishing": "Por favor guarde todos los elementos de la lista antes de finalizar",
            "confirmFinishExecution": "¿Está seguro de que desea finalizar esta ejecución de mantenimiento?",
            "executionCompletedSuccessfully": "¡Ejecución de mantenimiento completada con éxito!",
            "failedToCompleteExecution": "Error al completar la ejecución: {{error}}",
            "errorInitializingExecution": "Error al inicializar la ejecución",
            "machine": "Máquina",
            "progress": "Progreso",
            "completed": "✓ Completado",
            "markAsCompleted": "Marcar como completado",
            "saved": "Guardado",
            "critical": "Crítico",
            "failedToSaveItem": "Error al guardar el elemento: {{error}}",
            "finishMaintenance": "Finalizar Mantenimiento"
        },
        "common": {
            "goBack": "Volver"
        }
    },
    "tr": {
        "maintenance": {
            "quantityUsed": "Kullanılan Miktar",
            "estimatedQuantity": "Tahmini: {{quantity}}",
            "notes": "Notlar",
            "addObservationsPlaceholder": "Gözlem veya not ekleyin",
            "completeAllCriticalItems": "Lütfen bitirmeden önce tüm kritik öğeleri tamamlayın ({{count}} kaldı)",
            "saveAllItemsBeforeFinishing": "Lütfen bitirmeden önce tüm kontrol listesi öğelerini kaydedin",
            "confirmFinishExecution": "Bu bakım uygulamasını bitirmek istediğinizden emin misiniz?",
            "executionCompletedSuccessfully": "Bakım uygulaması başarıyla tamamlandı!",
            "failedToCompleteExecution": "Uygulama tamamlanamadı: {{error}}",
            "errorInitializingExecution": "Uygulama başlatma hatası",
            "machine": "Makine",
            "progress": "İlerleme",
            "completed": "✓ Tamamlandı",
            "markAsCompleted": "Tamamlandı olarak işaretle",
            "saved": "Kaydedildi",
            "critical": "Kritik",
            "failedToSaveItem": "Öğe kaydedilemedi: {{error}}",
            "finishMaintenance": "Bakımı Bitir"
        },
        "common": {
            "goBack": "Geri Dön"
        }
    },
    "no": {
        "maintenance": {
            "quantityUsed": "Brukt Mengde",
            "estimatedQuantity": "Estimert: {{quantity}}",
            "notes": "Notater",
            "addObservationsPlaceholder": "Legg til observasjoner eller notater",
            "completeAllCriticalItems": "Vennligst fullfør alle kritiske elementer før avslutning ({{count}} gjenstår)",
            "saveAllItemsBeforeFinishing": "Vennligst lagre alle sjekklisteelementer før avslutning",
            "confirmFinishExecution": "Er du sikker på at du vil fullføre denne vedlikeholdsutførelsen?",
            "executionCompletedSuccessfully": "Vedlikeholdsutførelse fullført!",
            "failedToCompleteExecution": "Kunne ikke fullføre utførelse: {{error}}",
            "errorInitializingExecution": "Feil ved initialisering av utførelse",
            "machine": "Maskin",
            "progress": "Fremdrift",
            "completed": "✓ Fullført",
            "markAsCompleted": "Merk som fullført",
            "saved": "Lagret",
            "critical": "Kritisk",
            "failedToSaveItem": "Kunne ikke lagre element: {{error}}",
            "finishMaintenance": "Fullfør Vedlikehold"
        },
        "common": {
            "goBack": "Gå Tilbake"
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
print("\nNew keys added:")
print("- maintenance.quantityUsed")
print("- maintenance.estimatedQuantity")
print("- maintenance.notes")
print("- maintenance.addObservationsPlaceholder")
print("- maintenance.completeAllCriticalItems")
print("- maintenance.saveAllItemsBeforeFinishing")
print("- maintenance.confirmFinishExecution")
print("- maintenance.executionCompletedSuccessfully")
print("- maintenance.failedToCompleteExecution")
print("- maintenance.errorInitializingExecution")
print("- maintenance.machine")
print("- maintenance.progress")
print("- maintenance.completed")
print("- maintenance.markAsCompleted")
print("- maintenance.saved")
print("- maintenance.critical")
print("- maintenance.failedToSaveItem")
print("- maintenance.finishMaintenance")
print("- common.goBack")
