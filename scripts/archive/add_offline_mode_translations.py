#!/usr/bin/env python3
"""
Add offline mode translations to all language files.
Includes translations for:
- Offline indicator
- Sync status page
- Net cleaning offline mode
- Photo handling
"""

import json
import os

# Translation keys for offline mode
OFFLINE_TRANSLATIONS = {
    "en": {
        # Offline Indicator
        "offline": {
            "title": "Offline Mode",
            "message": "You are currently offline",
            "pendingOperations": "{count} operations pending sync",
            "syncing": "Syncing...",
            "syncComplete": "Sync complete",
            "backOnline": "Back online",
            "duration": "Offline for {duration}"
        },
        
        # Sync Status Page
        "syncStatus": {
            "title": "Sync Status",
            "syncNow": "Sync Now",
            "syncing": "Syncing...",
            "connectionStatus": "Connection Status",
            "online": "Online",
            "offline": "Offline",
            "pendingOperations": "Pending Operations",
            "lastSync": "Last Sync",
            "never": "Never",
            "storageUsage": "Storage Usage",
            "used": "Used",
            "quota": "Quota",
            "syncError": "Sync Error",
            "queueStatistics": "Queue Statistics",
            "total": "Total",
            "pending": "Pending",
            "failed": "Failed",
            "failedOperations": "Failed Operations",
            "attempts": "Attempts",
            "retry": "Retry",
            "remove": "Remove",
            "confirmRemove": "Are you sure you want to remove this operation?",
            "type": "Type",
            "status": "Status",
            "priority": "Priority",
            "created": "Created",
            "offlineRecords": "Offline Records",
            "offlineRecordsHelp": "These records were created offline and are waiting to sync",
            "netCleaningRecord": "Net Cleaning Record",
            "operator": "Operator",
            "mode": "Mode",
            "waitingSync": "Waiting to sync",
            "allSynced": "All Synced!",
            "allSyncedHelp": "All offline data has been synchronized",
            "types": {
                "netCleaningRecord": "Net Cleaning Record",
                "netCleaningPhoto": "Photo",
                "maintenanceExecution": "Maintenance Execution",
                "machineHours": "Machine Hours",
                "stockAdjustment": "Stock Adjustment"
            },
            "statuses": {
                "pending": "Pending",
                "syncing": "Syncing",
                "completed": "Completed",
                "failed": "Failed"
            }
        },
        
        # Net Cleaning Offline Mode
        "netCleaning": {
            "records": {
                "photos": "Photos",
                "photosHelp": "Take photos of the cleaning process",
                "photosOfflineHelp": "Photos will be stored offline and synced when connection is restored",
                "offlineMode": "Offline Mode",
                "offlineModeHelp": "This record will be saved offline and synced automatically when you're back online",
                "savedOffline": "Record saved offline. It will sync when connection is restored.",
                "pendingSync": "Pending Sync",
                "waitingSync": "Waiting to sync"
            }
        }
    },
    
    "es": {
        # Offline Indicator
        "offline": {
            "title": "Modo Sin Conexión",
            "message": "Actualmente estás sin conexión",
            "pendingOperations": "{count} operaciones pendientes de sincronización",
            "syncing": "Sincronizando...",
            "syncComplete": "Sincronización completa",
            "backOnline": "De vuelta en línea",
            "duration": "Sin conexión durante {duration}"
        },
        
        # Sync Status Page
        "syncStatus": {
            "title": "Estado de Sincronización",
            "syncNow": "Sincronizar Ahora",
            "syncing": "Sincronizando...",
            "connectionStatus": "Estado de Conexión",
            "online": "En Línea",
            "offline": "Sin Conexión",
            "pendingOperations": "Operaciones Pendientes",
            "lastSync": "Última Sincronización",
            "never": "Nunca",
            "storageUsage": "Uso de Almacenamiento",
            "used": "Usado",
            "quota": "Cuota",
            "syncError": "Error de Sincronización",
            "queueStatistics": "Estadísticas de Cola",
            "total": "Total",
            "pending": "Pendiente",
            "failed": "Fallido",
            "failedOperations": "Operaciones Fallidas",
            "attempts": "Intentos",
            "retry": "Reintentar",
            "remove": "Eliminar",
            "confirmRemove": "¿Está seguro de que desea eliminar esta operación?",
            "type": "Tipo",
            "status": "Estado",
            "priority": "Prioridad",
            "created": "Creado",
            "offlineRecords": "Registros Sin Conexión",
            "offlineRecordsHelp": "Estos registros se crearon sin conexión y están esperando sincronizarse",
            "netCleaningRecord": "Registro de Limpieza de Red",
            "operator": "Operador",
            "mode": "Modo",
            "waitingSync": "Esperando sincronización",
            "allSynced": "¡Todo Sincronizado!",
            "allSyncedHelp": "Todos los datos sin conexión se han sincronizado",
            "types": {
                "netCleaningRecord": "Registro de Limpieza de Red",
                "netCleaningPhoto": "Foto",
                "maintenanceExecution": "Ejecución de Mantenimiento",
                "machineHours": "Horas de Máquina",
                "stockAdjustment": "Ajuste de Inventario"
            },
            "statuses": {
                "pending": "Pendiente",
                "syncing": "Sincronizando",
                "completed": "Completado",
                "failed": "Fallido"
            }
        },
        
        # Net Cleaning Offline Mode
        "netCleaning": {
            "records": {
                "photos": "Fotos",
                "photosHelp": "Tome fotos del proceso de limpieza",
                "photosOfflineHelp": "Las fotos se almacenarán sin conexión y se sincronizarán cuando se restablezca la conexión",
                "offlineMode": "Modo Sin Conexión",
                "offlineModeHelp": "Este registro se guardará sin conexión y se sincronizará automáticamente cuando vuelva a estar en línea",
                "savedOffline": "Registro guardado sin conexión. Se sincronizará cuando se restablezca la conexión.",
                "pendingSync": "Sincronización Pendiente",
                "waitingSync": "Esperando sincronización"
            }
        }
    },
    
    "tr": {
        # Offline Indicator
        "offline": {
            "title": "Çevrimdışı Mod",
            "message": "Şu anda çevrimdışısınız",
            "pendingOperations": "{count} işlem senkronizasyon bekliyor",
            "syncing": "Senkronize ediliyor...",
            "syncComplete": "Senkronizasyon tamamlandı",
            "backOnline": "Tekrar çevrimiçi",
            "duration": "{duration} çevrimdışı"
        },
        
        # Sync Status Page
        "syncStatus": {
            "title": "Senkronizasyon Durumu",
            "syncNow": "Şimdi Senkronize Et",
            "syncing": "Senkronize ediliyor...",
            "connectionStatus": "Bağlantı Durumu",
            "online": "Çevrimiçi",
            "offline": "Çevrimdışı",
            "pendingOperations": "Bekleyen İşlemler",
            "lastSync": "Son Senkronizasyon",
            "never": "Hiçbir zaman",
            "storageUsage": "Depolama Kullanımı",
            "used": "Kullanılan",
            "quota": "Kota",
            "syncError": "Senkronizasyon Hatası",
            "queueStatistics": "Kuyruk İstatistikleri",
            "total": "Toplam",
            "pending": "Beklemede",
            "failed": "Başarısız",
            "failedOperations": "Başarısız İşlemler",
            "attempts": "Denemeler",
            "retry": "Yeniden Dene",
            "remove": "Kaldır",
            "confirmRemove": "Bu işlemi kaldırmak istediğinizden emin misiniz?",
            "type": "Tür",
            "status": "Durum",
            "priority": "Öncelik",
            "created": "Oluşturuldu",
            "offlineRecords": "Çevrimdışı Kayıtlar",
            "offlineRecordsHelp": "Bu kayıtlar çevrimdışı oluşturuldu ve senkronize edilmeyi bekliyor",
            "netCleaningRecord": "Ağ Temizleme Kaydı",
            "operator": "Operatör",
            "mode": "Mod",
            "waitingSync": "Senkronizasyon bekleniyor",
            "allSynced": "Hepsi Senkronize Edildi!",
            "allSyncedHelp": "Tüm çevrimdışı veriler senkronize edildi",
            "types": {
                "netCleaningRecord": "Ağ Temizleme Kaydı",
                "netCleaningPhoto": "Fotoğraf",
                "maintenanceExecution": "Bakım Yürütme",
                "machineHours": "Makine Saatleri",
                "stockAdjustment": "Stok Ayarlaması"
            },
            "statuses": {
                "pending": "Beklemede",
                "syncing": "Senkronize ediliyor",
                "completed": "Tamamlandı",
                "failed": "Başarısız"
            }
        },
        
        # Net Cleaning Offline Mode
        "netCleaning": {
            "records": {
                "photos": "Fotoğraflar",
                "photosHelp": "Temizleme sürecinin fotoğraflarını çekin",
                "photosOfflineHelp": "Fotoğraflar çevrimdışı saklanacak ve bağlantı geri geldiğinde senkronize edilecek",
                "offlineMode": "Çevrimdışı Mod",
                "offlineModeHelp": "Bu kayıt çevrimdışı kaydedilecek ve tekrar çevrimiçi olduğunuzda otomatik olarak senkronize edilecek",
                "savedOffline": "Kayıt çevrimdışı kaydedildi. Bağlantı geri geldiğinde senkronize edilecek.",
                "pendingSync": "Senkronizasyon Bekliyor",
                "waitingSync": "Senkronizasyon bekleniyor"
            }
        }
    },
    
    "no": {
        # Offline Indicator
        "offline": {
            "title": "Frakoblet Modus",
            "message": "Du er for øyeblikket frakoblet",
            "pendingOperations": "{count} operasjoner venter på synkronisering",
            "syncing": "Synkroniserer...",
            "syncComplete": "Synkronisering fullført",
            "backOnline": "Tilbake på nett",
            "duration": "Frakoblet i {duration}"
        },
        
        # Sync Status Page
        "syncStatus": {
            "title": "Synkroniseringsstatus",
            "syncNow": "Synkroniser Nå",
            "syncing": "Synkroniserer...",
            "connectionStatus": "Tilkoblingsstatus",
            "online": "Tilkoblet",
            "offline": "Frakoblet",
            "pendingOperations": "Ventende Operasjoner",
            "lastSync": "Siste Synkronisering",
            "never": "Aldri",
            "storageUsage": "Lagringsbruk",
            "used": "Brukt",
            "quota": "Kvote",
            "syncError": "Synkroniseringsfeil",
            "queueStatistics": "Køstatistikk",
            "total": "Totalt",
            "pending": "Ventende",
            "failed": "Mislyktes",
            "failedOperations": "Mislykkede Operasjoner",
            "attempts": "Forsøk",
            "retry": "Prøv Igjen",
            "remove": "Fjern",
            "confirmRemove": "Er du sikker på at du vil fjerne denne operasjonen?",
            "type": "Type",
            "status": "Status",
            "priority": "Prioritet",
            "created": "Opprettet",
            "offlineRecords": "Frakoblede Poster",
            "offlineRecordsHelp": "Disse postene ble opprettet frakoblet og venter på synkronisering",
            "netCleaningRecord": "Notrensingspost",
            "operator": "Operatør",
            "mode": "Modus",
            "waitingSync": "Venter på synkronisering",
            "allSynced": "Alt Synkronisert!",
            "allSyncedHelp": "Alle frakoblede data er synkronisert",
            "types": {
                "netCleaningRecord": "Notrensingspost",
                "netCleaningPhoto": "Bilde",
                "maintenanceExecution": "Vedlikeholdsutførelse",
                "machineHours": "Maskintimer",
                "stockAdjustment": "Lagerjustering"
            },
            "statuses": {
                "pending": "Ventende",
                "syncing": "Synkroniserer",
                "completed": "Fullført",
                "failed": "Mislyktes"
            }
        },
        
        # Net Cleaning Offline Mode
        "netCleaning": {
            "records": {
                "photos": "Bilder",
                "photosHelp": "Ta bilder av renseprosessen",
                "photosOfflineHelp": "Bilder vil bli lagret frakoblet og synkronisert når tilkoblingen gjenopprettes",
                "offlineMode": "Frakoblet Modus",
                "offlineModeHelp": "Denne posten vil bli lagret frakoblet og synkronisert automatisk når du er tilbake på nett",
                "savedOffline": "Post lagret frakoblet. Den vil synkroniseres når tilkoblingen gjenopprettes.",
                "pendingSync": "Venter på Synkronisering",
                "waitingSync": "Venter på synkronisering"
            }
        }
    },
    
    "el": {
        # Offline Indicator
        "offline": {
            "title": "Λειτουργία Εκτός Σύνδεσης",
            "message": "Αυτή τη στιγμή είστε εκτός σύνδεσης",
            "pendingOperations": "{count} λειτουργίες σε αναμονή συγχρονισμού",
            "syncing": "Συγχρονισμός...",
            "syncComplete": "Ο συγχρονισμός ολοκληρώθηκε",
            "backOnline": "Επιστροφή σε σύνδεση",
            "duration": "Εκτός σύνδεσης για {duration}"
        },
        
        # Sync Status Page
        "syncStatus": {
            "title": "Κατάσταση Συγχρονισμού",
            "syncNow": "Συγχρονισμός Τώρα",
            "syncing": "Συγχρονισμός...",
            "connectionStatus": "Κατάσταση Σύνδεσης",
            "online": "Σε Σύνδεση",
            "offline": "Εκτός Σύνδεσης",
            "pendingOperations": "Λειτουργίες σε Αναμονή",
            "lastSync": "Τελευταίος Συγχρονισμός",
            "never": "Ποτέ",
            "storageUsage": "Χρήση Αποθήκευσης",
            "used": "Χρησιμοποιείται",
            "quota": "Όριο",
            "syncError": "Σφάλμα Συγχρονισμού",
            "queueStatistics": "Στατιστικά Ουράς",
            "total": "Σύνολο",
            "pending": "Σε Αναμονή",
            "failed": "Απέτυχε",
            "failedOperations": "Αποτυχημένες Λειτουργίες",
            "attempts": "Προσπάθειες",
            "retry": "Επανάληψη",
            "remove": "Αφαίρεση",
            "confirmRemove": "Είστε βέβαιοι ότι θέλετε να αφαιρέσετε αυτή τη λειτουργία;",
            "type": "Τύπος",
            "status": "Κατάσταση",
            "priority": "Προτεραιότητα",
            "created": "Δημιουργήθηκε",
            "offlineRecords": "Εγγραφές Εκτός Σύνδεσης",
            "offlineRecordsHelp": "Αυτές οι εγγραφές δημιουργήθηκαν εκτός σύνδεσης και περιμένουν συγχρονισμό",
            "netCleaningRecord": "Εγγραφή Καθαρισμού Δικτύου",
            "operator": "Χειριστής",
            "mode": "Λειτουργία",
            "waitingSync": "Αναμονή συγχρονισμού",
            "allSynced": "Όλα Συγχρονισμένα!",
            "allSyncedHelp": "Όλα τα δεδομένα εκτός σύνδεσης έχουν συγχρονιστεί",
            "types": {
                "netCleaningRecord": "Εγγραφή Καθαρισμού Δικτύου",
                "netCleaningPhoto": "Φωτογραφία",
                "maintenanceExecution": "Εκτέλεση Συντήρησης",
                "machineHours": "Ώρες Μηχανής",
                "stockAdjustment": "Προσαρμογή Αποθέματος"
            },
            "statuses": {
                "pending": "Σε Αναμονή",
                "syncing": "Συγχρονισμός",
                "completed": "Ολοκληρώθηκε",
                "failed": "Απέτυχε"
            }
        },
        
        # Net Cleaning Offline Mode
        "netCleaning": {
            "records": {
                "photos": "Φωτογραφίες",
                "photosHelp": "Τραβήξτε φωτογραφίες της διαδικασίας καθαρισμού",
                "photosOfflineHelp": "Οι φωτογραφίες θα αποθηκευτούν εκτός σύνδεσης και θα συγχρονιστούν όταν αποκατασταθεί η σύνδεση",
                "offlineMode": "Λειτουργία Εκτός Σύνδεσης",
                "offlineModeHelp": "Αυτή η εγγραφή θα αποθηκευτεί εκτός σύνδεσης και θα συγχρονιστεί αυτόματα όταν επιστρέψετε σε σύνδεση",
                "savedOffline": "Η εγγραφή αποθηκεύτηκε εκτός σύνδεσης. Θα συγχρονιστεί όταν αποκατασταθεί η σύνδεση.",
                "pendingSync": "Αναμονή Συγχρονισμού",
                "waitingSync": "Αναμονή συγχρονισμού"
            }
        }
    },
    
    "ar": {
        # Offline Indicator
        "offline": {
            "title": "وضع عدم الاتصال",
            "message": "أنت حاليًا غير متصل",
            "pendingOperations": "{count} عمليات في انتظار المزامنة",
            "syncing": "جارٍ المزامنة...",
            "syncComplete": "اكتملت المزامنة",
            "backOnline": "العودة إلى الاتصال",
            "duration": "غير متصل لمدة {duration}"
        },
        
        # Sync Status Page
        "syncStatus": {
            "title": "حالة المزامنة",
            "syncNow": "مزامنة الآن",
            "syncing": "جارٍ المزامنة...",
            "connectionStatus": "حالة الاتصال",
            "online": "متصل",
            "offline": "غير متصل",
            "pendingOperations": "العمليات المعلقة",
            "lastSync": "آخر مزامنة",
            "never": "أبدًا",
            "storageUsage": "استخدام التخزين",
            "used": "مستخدم",
            "quota": "الحصة",
            "syncError": "خطأ في المزامنة",
            "queueStatistics": "إحصائيات قائمة الانتظار",
            "total": "المجموع",
            "pending": "معلق",
            "failed": "فشل",
            "failedOperations": "العمليات الفاشلة",
            "attempts": "المحاولات",
            "retry": "إعادة المحاولة",
            "remove": "إزالة",
            "confirmRemove": "هل أنت متأكد من أنك تريد إزالة هذه العملية؟",
            "type": "النوع",
            "status": "الحالة",
            "priority": "الأولوية",
            "created": "تم الإنشاء",
            "offlineRecords": "السجلات غير المتصلة",
            "offlineRecordsHelp": "تم إنشاء هذه السجلات في وضع عدم الاتصال وهي في انتظار المزامنة",
            "netCleaningRecord": "سجل تنظيف الشبكة",
            "operator": "المشغل",
            "mode": "الوضع",
            "waitingSync": "في انتظار المزامنة",
            "allSynced": "تمت المزامنة بالكامل!",
            "allSyncedHelp": "تمت مزامنة جميع البيانات غير المتصلة",
            "types": {
                "netCleaningRecord": "سجل تنظيف الشبكة",
                "netCleaningPhoto": "صورة",
                "maintenanceExecution": "تنفيذ الصيانة",
                "machineHours": "ساعات الآلة",
                "stockAdjustment": "تعديل المخزون"
            },
            "statuses": {
                "pending": "معلق",
                "syncing": "جارٍ المزامنة",
                "completed": "مكتمل",
                "failed": "فشل"
            }
        },
        
        # Net Cleaning Offline Mode
        "netCleaning": {
            "records": {
                "photos": "الصور",
                "photosHelp": "التقط صورًا لعملية التنظيف",
                "photosOfflineHelp": "سيتم تخزين الصور في وضع عدم الاتصال ومزامنتها عند استعادة الاتصال",
                "offlineMode": "وضع عدم الاتصال",
                "offlineModeHelp": "سيتم حفظ هذا السجل في وضع عدم الاتصال ومزامنته تلقائيًا عند العودة إلى الاتصال",
                "savedOffline": "تم حفظ السجل في وضع عدم الاتصال. سيتم مزامنته عند استعادة الاتصال.",
                "pendingSync": "في انتظار المزامنة",
                "waitingSync": "في انتظار المزامنة"
            }
        }
    }
}


def deep_merge(base, updates):
    """Deep merge updates into base dictionary"""
    for key, value in updates.items():
        if key in base and isinstance(base[key], dict) and isinstance(value, dict):
            deep_merge(base[key], value)
        else:
            base[key] = value


def add_translations():
    """Add offline mode translations to all language files"""
    locales_dir = "frontend/src/locales"
    
    if not os.path.exists(locales_dir):
        print(f"Error: {locales_dir} directory not found")
        return
    
    for lang_code, translations in OFFLINE_TRANSLATIONS.items():
        file_path = os.path.join(locales_dir, f"{lang_code}.json")
        
        if not os.path.exists(file_path):
            print(f"Warning: {file_path} not found, skipping...")
            continue
        
        # Read existing translations
        with open(file_path, 'r', encoding='utf-8') as f:
            existing = json.load(f)
        
        # Merge new translations
        deep_merge(existing, translations)
        
        # Write back
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(existing, f, ensure_ascii=False, indent=2)
        
        print(f"✓ Updated {lang_code}.json with offline mode translations")
    
    print("\n✅ All translation files updated successfully!")
    print("\nAdded translations for:")
    print("  - Offline indicator")
    print("  - Sync status page")
    print("  - Net cleaning offline mode")
    print("  - Photo handling")


if __name__ == "__main__":
    add_translations()
