#!/usr/bin/env python3
import json

# Translation keys to add
translations = {
    "en": {
        "maintenance": {
            "backToHistory": "Back to History",
            "executionDetails": "Execution Details",
            "protocol": "Protocol",
            "performedBy": "Performed By",
            "hours": "hours",
            "checklistItems": "Checklist Items",
            "quantityUsedValue": "Quantity used: {{quantity}}",
            "by": "By",
            "viewDetails": "View Details",
            "executionHistory": "Execution History",
            "allStatus": "All Status",
            "noExecutionsFound": "No executions found",
            "status": {
                "scheduled": "Scheduled",
                "in_progress": "In Progress",
                "completed": "Completed",
                "cancelled": "Cancelled",
                "skipped": "Skipped"
            }
        },
        "common": {
            "unknown": "Unknown",
            "date": "Date",
            "status": "Status",
            "refresh": "Refresh"
        }
    },
    "el": {
        "maintenance": {
            "backToHistory": "Επιστροφή στο Ιστορικό",
            "executionDetails": "Λεπτομέρειες Εκτέλεσης",
            "protocol": "Πρωτόκολλο",
            "performedBy": "Εκτελέστηκε Από",
            "hours": "ώρες",
            "checklistItems": "Στοιχεία Λίστας Ελέγχου",
            "quantityUsedValue": "Ποσότητα που χρησιμοποιήθηκε: {{quantity}}",
            "by": "Από",
            "viewDetails": "Προβολή Λεπτομερειών",
            "executionHistory": "Ιστορικό Εκτελέσεων",
            "allStatus": "Όλες οι Καταστάσεις",
            "noExecutionsFound": "Δεν βρέθηκαν εκτελέσεις",
            "status": {
                "scheduled": "Προγραμματισμένο",
                "in_progress": "Σε Εξέλιξη",
                "completed": "Ολοκληρώθηκε",
                "cancelled": "Ακυρώθηκε",
                "skipped": "Παραλείφθηκε"
            }
        },
        "common": {
            "unknown": "Άγνωστο",
            "date": "Ημερομηνία",
            "status": "Κατάσταση",
            "refresh": "Ανανέωση"
        }
    },
    "ar": {
        "maintenance": {
            "backToHistory": "العودة إلى السجل",
            "executionDetails": "تفاصيل التنفيذ",
            "protocol": "البروتوكول",
            "performedBy": "نفذ بواسطة",
            "hours": "ساعات",
            "checklistItems": "عناصر قائمة التحقق",
            "quantityUsedValue": "الكمية المستخدمة: {{quantity}}",
            "by": "بواسطة",
            "viewDetails": "عرض التفاصيل",
            "executionHistory": "سجل التنفيذ",
            "allStatus": "جميع الحالات",
            "noExecutionsFound": "لم يتم العثور على تنفيذات",
            "status": {
                "scheduled": "مجدول",
                "in_progress": "قيد التنفيذ",
                "completed": "مكتمل",
                "cancelled": "ملغى",
                "skipped": "متخطى"
            }
        },
        "common": {
            "unknown": "غير معروف",
            "date": "التاريخ",
            "status": "الحالة",
            "refresh": "تحديث"
        }
    },
    "es": {
        "maintenance": {
            "backToHistory": "Volver al Historial",
            "executionDetails": "Detalles de Ejecución",
            "protocol": "Protocolo",
            "performedBy": "Realizado Por",
            "hours": "horas",
            "checklistItems": "Elementos de Lista de Verificación",
            "quantityUsedValue": "Cantidad utilizada: {{quantity}}",
            "by": "Por",
            "viewDetails": "Ver Detalles",
            "executionHistory": "Historial de Ejecuciones",
            "allStatus": "Todos los Estados",
            "noExecutionsFound": "No se encontraron ejecuciones",
            "status": {
                "scheduled": "Programado",
                "in_progress": "En Progreso",
                "completed": "Completado",
                "cancelled": "Cancelado",
                "skipped": "Omitido"
            }
        },
        "common": {
            "unknown": "Desconocido",
            "date": "Fecha",
            "status": "Estado",
            "refresh": "Actualizar"
        }
    },
    "tr": {
        "maintenance": {
            "backToHistory": "Geçmişe Dön",
            "executionDetails": "Uygulama Detayları",
            "protocol": "Protokol",
            "performedBy": "Gerçekleştiren",
            "hours": "saat",
            "checklistItems": "Kontrol Listesi Öğeleri",
            "quantityUsedValue": "Kullanılan miktar: {{quantity}}",
            "by": "Tarafından",
            "viewDetails": "Detayları Görüntüle",
            "executionHistory": "Uygulama Geçmişi",
            "allStatus": "Tüm Durumlar",
            "noExecutionsFound": "Uygulama bulunamadı",
            "status": {
                "scheduled": "Planlandı",
                "in_progress": "Devam Ediyor",
                "completed": "Tamamlandı",
                "cancelled": "İptal Edildi",
                "skipped": "Atlandı"
            }
        },
        "common": {
            "unknown": "Bilinmiyor",
            "date": "Tarih",
            "status": "Durum",
            "refresh": "Yenile"
        }
    },
    "no": {
        "maintenance": {
            "backToHistory": "Tilbake til Historikk",
            "executionDetails": "Utførelsesdetaljer",
            "protocol": "Protokoll",
            "performedBy": "Utført Av",
            "hours": "timer",
            "checklistItems": "Sjekklisteelementer",
            "quantityUsedValue": "Mengde brukt: {{quantity}}",
            "by": "Av",
            "viewDetails": "Vis Detaljer",
            "executionHistory": "Utførelseshistorikk",
            "allStatus": "Alle Statuser",
            "noExecutionsFound": "Ingen utførelser funnet",
            "status": {
                "scheduled": "Planlagt",
                "in_progress": "Pågår",
                "completed": "Fullført",
                "cancelled": "Kansellert",
                "skipped": "Hoppet Over"
            }
        },
        "common": {
            "unknown": "Ukjent",
            "date": "Dato",
            "status": "Status",
            "refresh": "Oppdater"
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
print("- maintenance.backToHistory")
print("- maintenance.executionDetails")
print("- maintenance.protocol")
print("- maintenance.performedBy")
print("- maintenance.hours")
print("- maintenance.checklistItems")
print("- maintenance.quantityUsedValue")
print("- maintenance.by")
print("- maintenance.viewDetails")
print("- maintenance.executionHistory")
print("- maintenance.allStatus")
print("- maintenance.noExecutionsFound")
print("- maintenance.status.scheduled")
print("- maintenance.status.in_progress")
print("- maintenance.status.completed")
print("- maintenance.status.cancelled")
print("- maintenance.status.skipped")
print("- common.unknown")
print("- common.date")
print("- common.status")
print("- common.refresh")
