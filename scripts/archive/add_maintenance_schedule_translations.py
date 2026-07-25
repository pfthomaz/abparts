#!/usr/bin/env python3
import json

# Translation keys to add
translations = {
    "en": {
        "maintenanceSchedule": {
            "scheduleOverview": "Maintenance Schedule Overview",
            "overdue": "Overdue",
            "dueSoon": "Due Soon",
            "scheduled": "Scheduled",
            "upcomingMaintenance": "Upcoming Maintenance",
            "scheduleMaintenance": "Schedule Maintenance",
            "dueDate": "Due Date",
            "schedule": "Schedule",
            "complete": "Complete",
            "recentHistory": "Recent Maintenance History",
            "noHistoryAvailable": "No maintenance history available",
            "maintenance": "MAINTENANCE",
            "viewAllRecords": "View all {{count}} records",
            "overdueBy": "Overdue by {{days}} days",
            "dueIn": "Due in {{days}} days",
            "overdueLabel": "OVERDUE",
            "dueSoonLabel": "DUE SOON",
            "scheduledLabel": "SCHEDULED",
            "maintenanceTips": "Maintenance Tips",
            "descriptions": {
                "routine": "Basic cleaning, lubrication, and visual inspection",
                "preventive": "Comprehensive system check, filter replacement, calibration",
                "inspection": "Detailed safety and performance inspection",
                "deepClean": "Complete disassembly, deep cleaning, and component replacement",
                "standard": "Standard maintenance procedure"
            },
            "tips": {
                "regularCleaning": "Regular cleaning prevents buildup and extends machine life",
                "checkFilters": "Check filters monthly and replace when dirty",
                "monitorNoises": "Monitor unusual noises or vibrations during operation",
                "keepLogs": "Keep maintenance logs for warranty and troubleshooting",
                "useApprovedParts": "Use only approved parts and cleaning solutions"
            }
        }
    },
    "el": {
        "maintenanceSchedule": {
            "scheduleOverview": "Επισκόπηση Προγράμματος Συντήρησης",
            "overdue": "Καθυστερημένα",
            "dueSoon": "Σύντομα",
            "scheduled": "Προγραμματισμένα",
            "upcomingMaintenance": "Επερχόμενη Συντήρηση",
            "scheduleMaintenance": "Προγραμματισμός Συντήρησης",
            "dueDate": "Ημερομηνία Λήξης",
            "schedule": "Προγραμματισμός",
            "complete": "Ολοκλήρωση",
            "recentHistory": "Πρόσφατο Ιστορικό Συντήρησης",
            "noHistoryAvailable": "Δεν υπάρχει διαθέσιμο ιστορικό συντήρησης",
            "maintenance": "ΣΥΝΤΗΡΗΣΗ",
            "viewAllRecords": "Προβολή όλων των {{count}} εγγραφών",
            "overdueBy": "Καθυστέρηση {{days}} ημερών",
            "dueIn": "Λήγει σε {{days}} ημέρες",
            "overdueLabel": "ΚΑΘΥΣΤΕΡΗΜΕΝΟ",
            "dueSoonLabel": "ΛΗΓΕΙ ΣΥΝΤΟΜΑ",
            "scheduledLabel": "ΠΡΟΓΡΑΜΜΑΤΙΣΜΕΝΟ",
            "maintenanceTips": "Συμβουλές Συντήρησης",
            "descriptions": {
                "routine": "Βασικός καθαρισμός, λίπανση και οπτική επιθεώρηση",
                "preventive": "Ολοκληρωμένος έλεγχος συστήματος, αντικατάσταση φίλτρων, βαθμονόμηση",
                "inspection": "Λεπτομερής επιθεώρηση ασφάλειας και απόδοσης",
                "deepClean": "Πλήρης αποσυναρμολόγηση, βαθύς καθαρισμός και αντικατάσταση εξαρτημάτων",
                "standard": "Τυπική διαδικασία συντήρησης"
            },
            "tips": {
                "regularCleaning": "Ο τακτικός καθαρισμός αποτρέπει τη συσσώρευση και παρατείνει τη ζωή του μηχανήματος",
                "checkFilters": "Ελέγχετε τα φίλτρα μηνιαίως και αντικαταστήστε τα όταν είναι βρώμικα",
                "monitorNoises": "Παρακολουθήστε ασυνήθιστους θορύβους ή δονήσεις κατά τη λειτουργία",
                "keepLogs": "Διατηρήστε αρχεία συντήρησης για εγγύηση και αντιμετώπιση προβλημάτων",
                "useApprovedParts": "Χρησιμοποιείτε μόνο εγκεκριμένα ανταλλακτικά και διαλύματα καθαρισμού"
            }
        }
    },
    "ar": {
        "maintenanceSchedule": {
            "scheduleOverview": "نظرة عامة على جدول الصيانة",
            "overdue": "متأخر",
            "dueSoon": "قريباً",
            "scheduled": "مجدول",
            "upcomingMaintenance": "الصيانة القادمة",
            "scheduleMaintenance": "جدولة الصيانة",
            "dueDate": "تاريخ الاستحقاق",
            "schedule": "جدولة",
            "complete": "إكمال",
            "recentHistory": "سجل الصيانة الأخير",
            "noHistoryAvailable": "لا يوجد سجل صيانة متاح",
            "maintenance": "صيانة",
            "viewAllRecords": "عرض جميع السجلات {{count}}",
            "overdueBy": "متأخر بـ {{days}} أيام",
            "dueIn": "مستحق خلال {{days}} أيام",
            "overdueLabel": "متأخر",
            "dueSoonLabel": "مستحق قريباً",
            "scheduledLabel": "مجدول",
            "maintenanceTips": "نصائح الصيانة",
            "descriptions": {
                "routine": "التنظيف الأساسي والتشحيم والفحص البصري",
                "preventive": "فحص شامل للنظام واستبدال الفلاتر والمعايرة",
                "inspection": "فحص تفصيلي للسلامة والأداء",
                "deepClean": "التفكيك الكامل والتنظيف العميق واستبدال المكونات",
                "standard": "إجراء صيانة قياسي"
            },
            "tips": {
                "regularCleaning": "التنظيف المنتظم يمنع التراكم ويطيل عمر الآلة",
                "checkFilters": "افحص الفلاتر شهرياً واستبدلها عند اتساخها",
                "monitorNoises": "راقب الأصوات أو الاهتزازات غير العادية أثناء التشغيل",
                "keepLogs": "احتفظ بسجلات الصيانة للضمان واستكشاف الأخطاء",
                "useApprovedParts": "استخدم فقط القطع ومحاليل التن��يف المعتمدة"
            }
        }
    },
    "es": {
        "maintenanceSchedule": {
            "scheduleOverview": "Resumen del Programa de Mantenimiento",
            "overdue": "Vencido",
            "dueSoon": "Próximo",
            "scheduled": "Programado",
            "upcomingMaintenance": "Mantenimiento Próximo",
            "scheduleMaintenance": "Programar Mantenimiento",
            "dueDate": "Fecha de Vencimiento",
            "schedule": "Programar",
            "complete": "Completar",
            "recentHistory": "Historial Reciente de Mantenimiento",
            "noHistoryAvailable": "No hay historial de mantenimiento disponible",
            "maintenance": "MANTENIMIENTO",
            "viewAllRecords": "Ver todos los {{count}} registros",
            "overdueBy": "Vencido por {{days}} días",
            "dueIn": "Vence en {{days}} días",
            "overdueLabel": "VENCIDO",
            "dueSoonLabel": "PRÓXIMO",
            "scheduledLabel": "PROGRAMADO",
            "maintenanceTips": "Consejos de Mantenimiento",
            "descriptions": {
                "routine": "Limpieza básica, lubricación e inspección visual",
                "preventive": "Revisión completa del sistema, reemplazo de filtros, calibración",
                "inspection": "Inspección detallada de seguridad y rendimiento",
                "deepClean": "Desmontaje completo, limpieza profunda y reemplazo de componentes",
                "standard": "Procedimiento de mantenimiento estándar"
            },
            "tips": {
                "regularCleaning": "La limpieza regular previene la acumulación y prolonga la vida de la máquina",
                "checkFilters": "Revise los filtros mensualmente y reemplácelos cuando estén sucios",
                "monitorNoises": "Monitoree ruidos o vibraciones inusuales durante la operación",
                "keepLogs": "Mantenga registros de mantenimiento para garantía y solución de problemas",
                "useApprovedParts": "Use solo piezas y soluciones de limpieza aprobadas"
            }
        }
    },
    "tr": {
        "maintenanceSchedule": {
            "scheduleOverview": "Bakım Programı Genel Bakış",
            "overdue": "Gecikmiş",
            "dueSoon": "Yakında",
            "scheduled": "Planlanmış",
            "upcomingMaintenance": "Yaklaşan Bakım",
            "scheduleMaintenance": "Bakım Planla",
            "dueDate": "Son Tarih",
            "schedule": "Planla",
            "complete": "Tamamla",
            "recentHistory": "Son Bakım Geçmişi",
            "noHistoryAvailable": "Bakım geçmişi mevcut değil",
            "maintenance": "BAKIM",
            "viewAllRecords": "Tüm {{count}} kaydı görüntüle",
            "overdueBy": "{{days}} gün gecikmiş",
            "dueIn": "{{days}} gün içinde",
            "overdueLabel": "GECİKMİŞ",
            "dueSoonLabel": "YAKINDA",
            "scheduledLabel": "PLANLANMIŞ",
            "maintenanceTips": "Bakım İpuçları",
            "descriptions": {
                "routine": "Temel temizlik, yağlama ve görsel muayene",
                "preventive": "Kapsamlı sistem kontrolü, filtre değişimi, kalibrasyon",
                "inspection": "Detaylı güvenlik ve performans muayenesi",
                "deepClean": "Tam sökme, derin temizlik ve bileşen değişimi",
                "standard": "Standart bakım prosedürü"
            },
            "tips": {
                "regularCleaning": "Düzenli temizlik birikim önler ve makine ömrünü uzatır",
                "checkFilters": "Filtreleri aylık kontrol edin ve kirlendiğinde değiştirin",
                "monitorNoises": "Çalışma sırasında olağandışı sesler veya titreşimleri izleyin",
                "keepLogs": "Garanti ve sorun giderme için bakım kayıtları tutun",
                "useApprovedParts": "Sadece onaylı parçalar ve temizlik solüsyonları kullanın"
            }
        }
    },
    "no": {
        "maintenanceSchedule": {
            "scheduleOverview": "Oversikt over Vedlikeholdsplan",
            "overdue": "Forfalt",
            "dueSoon": "Snart",
            "scheduled": "Planlagt",
            "upcomingMaintenance": "Kommende Vedlikehold",
            "scheduleMaintenance": "Planlegg Vedlikehold",
            "dueDate": "Forfallsdato",
            "schedule": "Planlegg",
            "complete": "Fullfør",
            "recentHistory": "Nylig Vedlikeholdshistorikk",
            "noHistoryAvailable": "Ingen vedlikeholdshistorikk tilgjengelig",
            "maintenance": "VEDLIKEHOLD",
            "viewAllRecords": "Vis alle {{count}} poster",
            "overdueBy": "Forfalt med {{days}} dager",
            "dueIn": "Forfaller om {{days}} dager",
            "overdueLabel": "FORFALT",
            "dueSoonLabel": "FORFALLER SNART",
            "scheduledLabel": "PLANLAGT",
            "maintenanceTips": "Vedlikeholdstips",
            "descriptions": {
                "routine": "Grunnleggende rengjøring, smøring og visuell inspeksjon",
                "preventive": "Omfattende systemsjekk, filterbytte, kalibrering",
                "inspection": "Detaljert sikkerhets- og ytelsesinspeksjon",
                "deepClean": "Fullstendig demontering, dyprengjøring og komponentutskifting",
                "standard": "Standard vedlikeholdsprosedyre"
            },
            "tips": {
                "regularCleaning": "Regelmessig rengjøring forhindrer opphopning og forlenger maskinens levetid",
                "checkFilters": "Sjekk filtre månedlig og bytt når de er skitne",
                "monitorNoises": "Overvåk uvanlige lyder eller vibrasjoner under drift",
                "keepLogs": "Oppbevar vedlikeholdslogger for garanti og feilsøking",
                "useApprovedParts": "Bruk kun godkjente deler og rengjøringsløsninger"
            }
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
print("\nNew keys added for MaintenanceSchedule component")
