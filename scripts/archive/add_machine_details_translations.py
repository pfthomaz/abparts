#!/usr/bin/env python3
import json

# Translation keys to add
translations = {
    "en": {
        "machineDetails": {
            "machineHoursLog": "Machine Hours Log",
            "dateTime": "Date & Time",
            "hoursValue": "Hours Value",
            "totalRecords": "Total Records",
            "totalAccumulated": "Total Accumulated",
            "addMaintenanceRecord": "Add Maintenance Record",
            "noMaintenanceRecords": "No maintenance records found",
            "duration": "Duration",
            "cost": "Cost",
            "usageChart": "Usage Chart",
            "machineNotFound": "Machine not found",
            "addMaintenance": "Add Maintenance",
            "machineInformation": "Machine Information",
            "purchaseDate": "Purchase Date",
            "warrantyExpiry": "Warranty Expiry",
            "nextMaintenance": "Next Maintenance",
            "quickStats": "Quick Stats",
            "maintenanceRecords": "Maintenance Records",
            "partsUsed": "Parts Used",
            "compatibleParts": "Compatible Parts",
            "warrantyActive": "Active",
            "warrantyExpired": "Expired",
            "warrantyStatus": "Warranty Status",
            "performanceAnalytics": "Machine Performance Analytics",
            "maintenanceFrequency": "Maintenance Frequency",
            "days": "days",
            "averageBetweenMaintenance": "Average between maintenance",
            "partsConsumption": "Parts Consumption",
            "totalPartsConsumed": "Total parts consumed",
            "maintenanceCost": "Maintenance Cost",
            "totalMaintenanceCost": "Total maintenance cost",
            "uptime": "Uptime",
            "estimatedUptime": "Estimated uptime",
            "failedToFetchData": "Failed to fetch machine data",
            "tabs": {
                "overview": "Overview",
                "machineHours": "Machine Hours",
                "maintenanceHistory": "Maintenance History",
                "partsUsage": "Parts Usage",
                "performance": "Performance",
                "maintenanceSchedule": "Maintenance Schedule"
            }
        },
        "common": {
            "na": "N/A",
            "close": "Close"
        }
    },
    "el": {
        "machineDetails": {
            "machineHoursLog": "Αρχείο Ωρών Μηχανήματος",
            "dateTime": "Ημερομηνία & Ώρα",
            "hoursValue": "Τιμή Ωρών",
            "totalRecords": "Σύνολο Εγγραφών",
            "totalAccumulated": "Συνολική Συσσώρευση",
            "addMaintenanceRecord": "Προσθήκη Εγγραφής Συντήρησης",
            "noMaintenanceRecords": "Δεν βρέθηκαν εγγραφές συντήρησης",
            "duration": "Διάρκεια",
            "cost": "Κόστος",
            "usageChart": "Γράφημα Χρήσης",
            "machineNotFound": "Το μηχάνημα δεν βρέθηκε",
            "addMaintenance": "Προσθήκη Συντήρησης",
            "machineInformation": "Πληροφορίες Μηχανήματος",
            "purchaseDate": "Ημερομηνία Αγοράς",
            "warrantyExpiry": "Λήξη Εγγύησης",
            "nextMaintenance": "Επόμενη Συντήρηση",
            "quickStats": "Γρήγορα Στατιστικά",
            "maintenanceRecords": "Εγγραφές Συντήρησης",
            "partsUsed": "Ανταλλακτικά που Χρησιμοποιήθηκαν",
            "compatibleParts": "Συμβατά Ανταλλακτικά",
            "warrantyActive": "Ενεργή",
            "warrantyExpired": "Έληξε",
            "warrantyStatus": "Κατάσταση Εγγύησης",
            "performanceAnalytics": "Αναλυτικά Απόδοσης Μηχανήματος",
            "maintenanceFrequency": "Συχνότητα Συντήρησης",
            "days": "ημέρες",
            "averageBetweenMaintenance": "Μέσος όρος μεταξύ συντηρήσεων",
            "partsConsumption": "Κατανάλωση Ανταλλακτικών",
            "totalPartsConsumed": "Σύνολο ανταλλακτικών που καταναλώθηκαν",
            "maintenanceCost": "Κόστος Συντήρησης",
            "totalMaintenanceCost": "Συνολικό κόστος συντήρησης",
            "uptime": "Χρόνος Λειτουργίας",
            "estimatedUptime": "Εκτιμώμενος χρόνος λειτουργίας",
            "failedToFetchData": "Αποτυχία φόρτωσης δεδομένων μηχανήματος",
            "tabs": {
                "overview": "Επισκόπηση",
                "machineHours": "Ώρες Μηχανήματος",
                "maintenanceHistory": "Ιστορικό Συντήρησης",
                "partsUsage": "Χρήση Ανταλλακτικών",
                "performance": "Απόδοση",
                "maintenanceSchedule": "Πρόγραμμα Συντήρησης"
            }
        },
        "common": {
            "na": "Μ/Δ",
            "close": "Κλείσιμο"
        }
    },
    "ar": {
        "machineDetails": {
            "machineHoursLog": "سجل ساعات الآلة",
            "dateTime": "التاريخ والوقت",
            "hoursValue": "قيمة الساعات",
            "totalRecords": "إجمالي السجلات",
            "totalAccumulated": "الإجمالي المتراكم",
            "addMaintenanceRecord": "إضافة سجل صيانة",
            "noMaintenanceRecords": "لم يتم العثور على سجلات صيانة",
            "duration": "المدة",
            "cost": "التكلفة",
            "usageChart": "مخطط الاستخدام",
            "machineNotFound": "لم يتم العثور على الآلة",
            "addMaintenance": "إضافة صيانة",
            "machineInformation": "معلومات الآلة",
            "purchaseDate": "تاريخ الشراء",
            "warrantyExpiry": "انتهاء الضمان",
            "nextMaintenance": "الصيانة التالية",
            "quickStats": "إحصائيات سريعة",
            "maintenanceRecords": "سجلات الصيانة",
            "partsUsed": "القطع المستخدمة",
            "compatibleParts": "القطع المتوافقة",
            "warrantyActive": "نشط",
            "warrantyExpired": "منتهي",
            "warrantyStatus": "حالة الضمان",
            "performanceAnalytics": "تحليلات أداء الآلة",
            "maintenanceFrequency": "تكرار الصيانة",
            "days": "أيام",
            "averageBetweenMaintenance": "المتوسط بين الصيانات",
            "partsConsumption": "استهلاك القطع",
            "totalPartsConsumed": "إجمالي القطع المستهلكة",
            "maintenanceCost": "تكلفة الصيانة",
            "totalMaintenanceCost": "إجمالي تكلفة الصيانة",
            "uptime": "وقت التشغيل",
            "estimatedUptime": "وقت التشغيل المقدر",
            "failedToFetchData": "فشل في جلب بيانات الآلة",
            "tabs": {
                "overview": "نظرة عامة",
                "machineHours": "ساعات الآلة",
                "maintenanceHistory": "سجل الصيانة",
                "partsUsage": "استخدام القطع",
                "performance": "الأداء",
                "maintenanceSchedule": "جدول الصيانة"
            }
        },
        "common": {
            "na": "غير متاح",
            "close": "إغلاق"
        }
    },
    "es": {
        "machineDetails": {
            "machineHoursLog": "Registro de Horas de Máquina",
            "dateTime": "Fecha y Hora",
            "hoursValue": "Valor de Horas",
            "totalRecords": "Total de Registros",
            "totalAccumulated": "Total Acumulado",
            "addMaintenanceRecord": "Agregar Registro de Mantenimiento",
            "noMaintenanceRecords": "No se encontraron registros de mantenimiento",
            "duration": "Duración",
            "cost": "Costo",
            "usageChart": "Gráfico de Uso",
            "machineNotFound": "Máquina no encontrada",
            "addMaintenance": "Agregar Mantenimiento",
            "machineInformation": "Información de la Máquina",
            "purchaseDate": "Fecha de Compra",
            "warrantyExpiry": "Vencimiento de Garantía",
            "nextMaintenance": "Próximo Mantenimiento",
            "quickStats": "Estadísticas Rápidas",
            "maintenanceRecords": "Registros de Mantenimiento",
            "partsUsed": "Piezas Utilizadas",
            "compatibleParts": "Piezas Compatibles",
            "warrantyActive": "Activa",
            "warrantyExpired": "Vencida",
            "warrantyStatus": "Estado de Garantía",
            "performanceAnalytics": "Análisis de Rendimiento de Máquina",
            "maintenanceFrequency": "Frecuencia de Mantenimiento",
            "days": "días",
            "averageBetweenMaintenance": "Promedio entre mantenimientos",
            "partsConsumption": "Consumo de Piezas",
            "totalPartsConsumed": "Total de piezas consumidas",
            "maintenanceCost": "Costo de Mantenimiento",
            "totalMaintenanceCost": "Costo total de mantenimiento",
            "uptime": "Tiempo de Actividad",
            "estimatedUptime": "Tiempo de actividad estimado",
            "failedToFetchData": "Error al obtener datos de la máquina",
            "tabs": {
                "overview": "Resumen",
                "machineHours": "Horas de Máquina",
                "maintenanceHistory": "Historial de Mantenimiento",
                "partsUsage": "Uso de Piezas",
                "performance": "Rendimiento",
                "maintenanceSchedule": "Programa de Mantenimiento"
            }
        },
        "common": {
            "na": "N/D",
            "close": "Cerrar"
        }
    },
    "tr": {
        "machineDetails": {
            "machineHoursLog": "Makine Saatleri Kaydı",
            "dateTime": "Tarih ve Saat",
            "hoursValue": "Saat Değeri",
            "totalRecords": "Toplam Kayıt",
            "totalAccumulated": "Toplam Birikmiş",
            "addMaintenanceRecord": "Bakım Kaydı Ekle",
            "noMaintenanceRecords": "Bakım kaydı bulunamadı",
            "duration": "Süre",
            "cost": "Maliyet",
            "usageChart": "Kullanım Grafiği",
            "machineNotFound": "Makine bulunamadı",
            "addMaintenance": "Bakım Ekle",
            "machineInformation": "Makine Bilgileri",
            "purchaseDate": "Satın Alma Tarihi",
            "warrantyExpiry": "Garanti Sonu",
            "nextMaintenance": "Sonraki Bakım",
            "quickStats": "Hızlı İstatistikler",
            "maintenanceRecords": "Bakım Kayıtları",
            "partsUsed": "Kullanılan Parçalar",
            "compatibleParts": "Uyumlu Parçalar",
            "warrantyActive": "Aktif",
            "warrantyExpired": "Süresi Dolmuş",
            "warrantyStatus": "Garanti Durumu",
            "performanceAnalytics": "Makine Performans Analitiği",
            "maintenanceFrequency": "Bakım Sıklığı",
            "days": "gün",
            "averageBetweenMaintenance": "Bakımlar arası ortalama",
            "partsConsumption": "Parça Tüketimi",
            "totalPartsConsumed": "Toplam tüketilen parça",
            "maintenanceCost": "Bakım Maliyeti",
            "totalMaintenanceCost": "Toplam bakım maliyeti",
            "uptime": "Çalışma Süresi",
            "estimatedUptime": "Tahmini çalışma süresi",
            "failedToFetchData": "Makine verileri alınamadı",
            "tabs": {
                "overview": "Genel Bakış",
                "machineHours": "Makine Saatleri",
                "maintenanceHistory": "Bakım Geçmişi",
                "partsUsage": "Parça Kullanımı",
                "performance": "Performans",
                "maintenanceSchedule": "Bakım Programı"
            }
        },
        "common": {
            "na": "Yok",
            "close": "Kapat"
        }
    },
    "no": {
        "machineDetails": {
            "machineHoursLog": "Maskintimer Logg",
            "dateTime": "Dato og Tid",
            "hoursValue": "Timeverdi",
            "totalRecords": "Totalt Antall Poster",
            "totalAccumulated": "Totalt Akkumulert",
            "addMaintenanceRecord": "Legg til Vedlikeholdspost",
            "noMaintenanceRecords": "Ingen vedlikeholdsposter funnet",
            "duration": "Varighet",
            "cost": "Kostnad",
            "usageChart": "Bruksdiagram",
            "machineNotFound": "Maskin ikke funnet",
            "addMaintenance": "Legg til Vedlikehold",
            "machineInformation": "Maskininformasjon",
            "purchaseDate": "Kjøpsdato",
            "warrantyExpiry": "Garantiutløp",
            "nextMaintenance": "Neste Vedlikehold",
            "quickStats": "Rask Statistikk",
            "maintenanceRecords": "Vedlikeholdsposter",
            "partsUsed": "Deler Brukt",
            "compatibleParts": "Kompatible Deler",
            "warrantyActive": "Aktiv",
            "warrantyExpired": "Utløpt",
            "warrantyStatus": "Garantistatus",
            "performanceAnalytics": "Maskinytelsesanalyse",
            "maintenanceFrequency": "Vedlikeholdsfrekvens",
            "days": "dager",
            "averageBetweenMaintenance": "Gjennomsnitt mellom vedlikehold",
            "partsConsumption": "Delforbruk",
            "totalPartsConsumed": "Totalt forbrukte deler",
            "maintenanceCost": "Vedlikeholdskostnad",
            "totalMaintenanceCost": "Total vedlikeholdskostnad",
            "uptime": "Oppetid",
            "estimatedUptime": "Estimert oppetid",
            "failedToFetchData": "Kunne ikke hente maskindata",
            "tabs": {
                "overview": "Oversikt",
                "machineHours": "Maskintimer",
                "maintenanceHistory": "Vedlikeholdshistorikk",
                "partsUsage": "Delbruk",
                "performance": "Ytelse",
                "maintenanceSchedule": "Vedlikeholdsplan"
            }
        },
        "common": {
            "na": "I/T",
            "close": "Lukk"
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
print("\nNew keys added for MachineDetails component with all 6 tabs")
