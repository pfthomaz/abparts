#!/usr/bin/env python3
import json

# Translation keys to add
translations = {
    "en": {
        "machines": {
            "title": "Machines",
            "registerMachine": "Register Machine",
            "loading": "Loading machines...",
            "confirmDelete": "Are you sure you want to delete this machine?",
            "failedToDelete": "Failed to delete machine.",
            "noMachinesFound": "No Machines Found",
            "tryAdjustingFilters": "Try adjusting your search or filter criteria.",
            "noMachinesYet": "There are no machines in the system yet.",
            "searchMachine": "Search Machine",
            "searchPlaceholder": "Name, model, or serial...",
            "filterByOwner": "Filter by Owner",
            "allOwners": "All Owners",
            "model": "Model",
            "serial": "Serial",
            "owner": "Owner",
            "latestHours": "Latest Hours",
            "hrs": "hrs",
            "recorded": "Recorded",
            "at": "at",
            "noHoursRecorded": "No hours recorded yet",
            "lastMaintenance": "Last Maintenance",
            "editMachine": "Edit Machine",
            "registerNewMachine": "Register New Machine",
            "machineDetails": "Machine Details",
            "transferMachine": "Transfer Machine",
            "viewDetails": "View Details",
            "recordPartUsage": "Record part usage for this machine",
            "usePart": "Use Part",
            "transfer": "Transfer",
            "status": {
                "active": "Active",
                "inactive": "Inactive",
                "maintenance": "Under Maintenance",
                "decommissioned": "Decommissioned"
            }
        },
        "common": {
            "error": "Error",
            "edit": "Edit",
            "delete": "Delete"
        }
    },
    "el": {
        "machines": {
            "title": "Μηχανήματα",
            "registerMachine": "Καταχώριση Μηχανήματος",
            "loading": "Φόρτωση μηχανημάτων...",
            "confirmDelete": "Είστε σίγουροι ότι θέλετε να διαγράψετε αυτό το μηχάνημα;",
            "failedToDelete": "Αποτυχία διαγραφής μηχανήματος.",
            "noMachinesFound": "Δεν Βρέθηκαν Μηχανήματα",
            "tryAdjustingFilters": "Δοκιμάστε να προσαρμόσετε τα κριτήρια αναζήτησης ή φιλτραρίσματος.",
            "noMachinesYet": "Δεν υπάρχουν ακόμα μηχανήματα στο σύστημα.",
            "searchMachine": "Αναζήτηση Μηχανήματος",
            "searchPlaceholder": "Όνομα, μοντέλο ή σειριακός...",
            "filterByOwner": "Φιλτράρισμα κατά Ιδιοκτήτη",
            "allOwners": "Όλοι οι Ιδιοκτήτες",
            "model": "Μοντέλο",
            "serial": "Σειριακός",
            "owner": "Ιδιοκτήτης",
            "latestHours": "Τελευταίες Ώρες",
            "hrs": "ώρες",
            "recorded": "Καταγράφηκε",
            "at": "στις",
            "noHoursRecorded": "Δεν έχουν καταγραφεί ώρες ακόμα",
            "lastMaintenance": "Τελευταία Συντήρηση",
            "editMachine": "Επεξεργασία Μηχανήματος",
            "registerNewMachine": "Καταχώριση Νέου Μηχανήματος",
            "machineDetails": "Λεπτομέρειες Μηχανήματος",
            "transferMachine": "Μεταφορά Μηχανήματος",
            "viewDetails": "Προβολή Λεπτομερειών",
            "recordPartUsage": "Καταγραφή χρήσης ανταλλακτικού για αυτό το μηχάνημα",
            "usePart": "Χρήση Ανταλλακτικού",
            "transfer": "Μεταφορά",
            "status": {
                "active": "Ενεργό",
                "inactive": "Ανενεργό",
                "maintenance": "Υπό Συντήρηση",
                "decommissioned": "Παροπλισμένο"
            }
        },
        "common": {
            "error": "Σφάλμα",
            "edit": "Επεξεργασία",
            "delete": "Διαγραφή"
        }
    },
    "ar": {
        "machines": {
            "title": "الآلات",
            "registerMachine": "تسجيل آلة",
            "loading": "جاري تحميل الآلات...",
            "confirmDelete": "هل أنت متأكد من أنك تريد حذف هذه الآلة؟",
            "failedToDelete": "فشل في حذف الآلة.",
            "noMachinesFound": "لم يتم العثور على آلات",
            "tryAdjustingFilters": "حاول تعديل معايير البحث أو التصفية.",
            "noMachinesYet": "لا توجد آلات في النظام بعد.",
            "searchMachine": "البحث عن آلة",
            "searchPlaceholder": "الاسم أو الطراز أو الرقم التسلسلي...",
            "filterByOwner": "تصفية حسب المالك",
            "allOwners": "جميع المالكين",
            "model": "الطراز",
            "serial": "الرقم التسلسلي",
            "owner": "المالك",
            "latestHours": "أحدث الساعات",
            "hrs": "ساعات",
            "recorded": "مسجل",
            "at": "في",
            "noHoursRecorded": "لم يتم تسجيل ساعات بعد",
            "lastMaintenance": "آخر صيانة",
            "editMachine": "تعديل الآلة",
            "registerNewMachine": "تسجيل آلة جديدة",
            "machineDetails": "تفاصيل الآلة",
            "transferMachine": "نقل الآلة",
            "viewDetails": "عرض التفاصيل",
            "recordPartUsage": "تسجيل استخدام قطعة لهذه الآلة",
            "usePart": "استخدام قطعة",
            "transfer": "نقل",
            "status": {
                "active": "نشط",
                "inactive": "غير نشط",
                "maintenance": "تحت الصيانة",
                "decommissioned": "خارج الخدمة"
            }
        },
        "common": {
            "error": "خطأ",
            "edit": "تعديل",
            "delete": "حذف"
        }
    },
    "es": {
        "machines": {
            "title": "Máquinas",
            "registerMachine": "Registrar Máquina",
            "loading": "Cargando máquinas...",
            "confirmDelete": "¿Está seguro de que desea eliminar esta máquina?",
            "failedToDelete": "Error al eliminar la máquina.",
            "noMachinesFound": "No se Encontraron Máquinas",
            "tryAdjustingFilters": "Intente ajustar sus criterios de búsqueda o filtro.",
            "noMachinesYet": "Aún no hay máquinas en el sistema.",
            "searchMachine": "Buscar Máquina",
            "searchPlaceholder": "Nombre, modelo o serial...",
            "filterByOwner": "Filtrar por Propietario",
            "allOwners": "Todos los Propietarios",
            "model": "Modelo",
            "serial": "Serial",
            "owner": "Propietario",
            "latestHours": "Últimas Horas",
            "hrs": "hrs",
            "recorded": "Registrado",
            "at": "a las",
            "noHoursRecorded": "No se han registrado horas aún",
            "lastMaintenance": "Último Mantenimiento",
            "editMachine": "Editar Máquina",
            "registerNewMachine": "Registrar Nueva Máquina",
            "machineDetails": "Detalles de la Máquina",
            "transferMachine": "Transferir Máquina",
            "viewDetails": "Ver Detalles",
            "recordPartUsage": "Registrar uso de pieza para esta máquina",
            "usePart": "Usar Pieza",
            "transfer": "Transferir",
            "status": {
                "active": "Activo",
                "inactive": "Inactivo",
                "maintenance": "En Mantenimiento",
                "decommissioned": "Fuera de Servicio"
            }
        },
        "common": {
            "error": "Error",
            "edit": "Editar",
            "delete": "Eliminar"
        }
    },
    "tr": {
        "machines": {
            "title": "Makineler",
            "registerMachine": "Makine Kaydet",
            "loading": "Makineler yükleniyor...",
            "confirmDelete": "Bu makineyi silmek istediğinizden emin misiniz?",
            "failedToDelete": "Makine silinemedi.",
            "noMachinesFound": "Makine Bulunamadı",
            "tryAdjustingFilters": "Arama veya filtre kriterlerinizi ayarlamayı deneyin.",
            "noMachinesYet": "Sistemde henüz makine yok.",
            "searchMachine": "Makine Ara",
            "searchPlaceholder": "İsim, model veya seri...",
            "filterByOwner": "Sahibine Göre Filtrele",
            "allOwners": "Tüm Sahipler",
            "model": "Model",
            "serial": "Seri",
            "owner": "Sahip",
            "latestHours": "Son Saatler",
            "hrs": "saat",
            "recorded": "Kaydedildi",
            "at": "saat",
            "noHoursRecorded": "Henüz saat kaydedilmedi",
            "lastMaintenance": "Son Bakım",
            "editMachine": "Makineyi Düzenle",
            "registerNewMachine": "Yeni Makine Kaydet",
            "machineDetails": "Makine Detayları",
            "transferMachine": "Makineyi Transfer Et",
            "viewDetails": "Detayları Görüntüle",
            "recordPartUsage": "Bu makine için parça kullanımını kaydet",
            "usePart": "Parça Kullan",
            "transfer": "Transfer",
            "status": {
                "active": "Aktif",
                "inactive": "Pasif",
                "maintenance": "Bakımda",
                "decommissioned": "Hizmet Dışı"
            }
        },
        "common": {
            "error": "Hata",
            "edit": "Düzenle",
            "delete": "Sil"
        }
    },
    "no": {
        "machines": {
            "title": "Maskiner",
            "registerMachine": "Registrer Maskin",
            "loading": "Laster maskiner...",
            "confirmDelete": "Er du sikker på at du vil slette denne maskinen?",
            "failedToDelete": "Kunne ikke slette maskin.",
            "noMachinesFound": "Ingen Maskiner Funnet",
            "tryAdjustingFilters": "Prøv å justere søke- eller filterkriteriene.",
            "noMachinesYet": "Det er ingen maskiner i systemet ennå.",
            "searchMachine": "Søk Maskin",
            "searchPlaceholder": "Navn, modell eller serienummer...",
            "filterByOwner": "Filtrer etter Eier",
            "allOwners": "Alle Eiere",
            "model": "Modell",
            "serial": "Serienummer",
            "owner": "Eier",
            "latestHours": "Siste Timer",
            "hrs": "timer",
            "recorded": "Registrert",
            "at": "kl",
            "noHoursRecorded": "Ingen timer registrert ennå",
            "lastMaintenance": "Siste Vedlikehold",
            "editMachine": "Rediger Maskin",
            "registerNewMachine": "Registrer Ny Maskin",
            "machineDetails": "Maskindetaljer",
            "transferMachine": "Overfør Maskin",
            "viewDetails": "Vis Detaljer",
            "recordPartUsage": "Registrer delbruk for denne maskinen",
            "usePart": "Bruk Del",
            "transfer": "Overfør",
            "status": {
                "active": "Aktiv",
                "inactive": "Inaktiv",
                "maintenance": "Under Vedlikehold",
                "decommissioned": "Utfaset"
            }
        },
        "common": {
            "error": "Feil",
            "edit": "Rediger",
            "delete": "Slett"
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
print("\nNew keys added for Machines page")
