#!/usr/bin/env python3

import json
import os

def add_maintenance_protocols_translations():
    """Add comprehensive maintenance protocols translations to all locale files"""
    
    # Maintenance protocols translations
    protocols_translations = {
        "en": {
            "maintenanceProtocols": {
                "title": "Maintenance Protocols",
                "subtitle": "Manage maintenance protocol templates for machines",
                "createNew": "Create New Protocol",
                "noProtocols": "No protocols found. Create your first protocol to get started.",
                "loading": "Loading protocols...",
                "confirmDelete": "Are you sure you want to delete this protocol?",
                "deleteFailed": "Failed to delete protocol",
                "filters": {
                    "protocolType": "Protocol Type",
                    "allTypes": "All Types",
                    "machineModel": "Machine Model",
                    "allModels": "All Models",
                    "universal": "Universal (All Models)",
                    "status": "Status",
                    "activeOnly": "Active Only",
                    "all": "All",
                    "search": "Search",
                    "searchPlaceholder": "Search protocols..."
                },
                "types": {
                    "daily": "Daily",
                    "weekly": "Weekly",
                    "scheduled": "Scheduled",
                    "custom": "Custom"
                },
                "card": {
                    "serviceInterval": "Service Interval",
                    "hours": "h",
                    "checklistItems": "checklist items",
                    "manageChecklist": "Manage Checklist",
                    "edit": "Edit",
                    "delete": "Delete",
                    "inactive": "Inactive"
                }
            },
            "protocolForm": {
                "editTitle": "Edit Protocol",
                "createTitle": "Create New Protocol",
                "fields": {
                    "name": "Protocol Name",
                    "namePlaceholder": "e.g., Daily Start of Day",
                    "type": "Protocol Type",
                    "serviceHours": "Service Hours",
                    "serviceHoursPlaceholder": "e.g., 50 or 250",
                    "serviceHoursHelp": "Number of operating hours for this service",
                    "isRecurring": "Recurring service (repeat every {hours} hours)",
                    "recurringHelp": "Uncheck for one-time services (e.g., 50h initial service). Check for recurring services (e.g., every 250h).",
                    "machineModel": "Machine Model",
                    "allModelsUniversal": "All Models (Universal)",
                    "machineModelHelp": "Leave empty to apply to all machine models",
                    "description": "Description",
                    "descriptionPlaceholder": "Brief description of this protocol...",
                    "displayOrder": "Display Order",
                    "displayOrderHelp": "Lower numbers appear first",
                    "isActive": "Active (protocol is available for use)"
                },
                "typeOptions": {
                    "daily": "Daily",
                    "weekly": "Weekly",
                    "scheduled": "Scheduled (Hours-based)",
                    "custom": "Custom"
                },
                "actions": {
                    "saving": "Saving...",
                    "update": "Update Protocol",
                    "create": "Create Protocol",
                    "cancel": "Cancel"
                }
            }
        },
        "el": {
            "maintenanceProtocols": {
                "title": "Πρωτόκολλα Συντήρησης",
                "subtitle": "Διαχείριση προτύπων πρωτοκόλλων συντήρησης για μηχανήματα",
                "createNew": "Δημιουργία Νέου Πρωτοκόλλου",
                "noProtocols": "Δεν βρέθηκαν πρωτόκολλα. Δημιουργήστε το πρώτο σας πρωτόκολλο για να ξεκινήσετε.",
                "loading": "Φόρτωση πρωτοκόλλων...",
                "confirmDelete": "Είστε σίγουροι ότι θέλετε να διαγράψετε αυτό το πρωτόκολλο;",
                "deleteFailed": "Αποτυχία διαγραφής πρωτοκόλλου",
                "filters": {
                    "protocolType": "Τύπος Πρωτοκόλλου",
                    "allTypes": "Όλοι οι Τύποι",
                    "machineModel": "Μοντέλο Μηχανήματος",
                    "allModels": "Όλα τα Μοντέλα",
                    "universal": "Καθολικό (Όλα τα Μοντέλα)",
                    "status": "Κατάσταση",
                    "activeOnly": "Μόνο Ενεργά",
                    "all": "Όλα",
                    "search": "Αναζήτηση",
                    "searchPlaceholder": "Αναζήτηση πρωτοκόλλων..."
                },
                "types": {
                    "daily": "Ημερήσιο",
                    "weekly": "Εβδομαδιαίο",
                    "scheduled": "Προγραμματισμένο",
                    "custom": "Προσαρμοσμένο"
                },
                "card": {
                    "serviceInterval": "Διάστημα Συντήρησης",
                    "hours": "ώ",
                    "checklistItems": "στοιχεία ελέγχου",
                    "manageChecklist": "Διαχείριση Λίστας Ελέγχου",
                    "edit": "Επεξεργασία",
                    "delete": "Διαγραφή",
                    "inactive": "Ανενεργό"
                }
            },
            "protocolForm": {
                "editTitle": "Επεξεργασία Πρωτοκόλλου",
                "createTitle": "Δημιουργία Νέου Πρωτοκόλλου",
                "fields": {
                    "name": "Όνομα Πρωτοκόλλου",
                    "namePlaceholder": "π.χ., Ημερήσια Έναρξη Ημέρας",
                    "type": "Τύπος Πρωτοκόλλου",
                    "serviceHours": "Ώρες Συντήρησης",
                    "serviceHoursPlaceholder": "π.χ., 50 ή 250",
                    "serviceHoursHelp": "Αριθμός ωρών λειτουργίας για αυτή τη συντήρηση",
                    "isRecurring": "Επαναλαμβανόμενη συντήρηση (επανάληψη κάθε {hours} ώρες)",
                    "recurringHelp": "Αποεπιλέξτε για μία φορά συντηρήσεις (π.χ., αρχική συντήρηση 50ώ). Επιλέξτε για επαναλαμβανόμενες συντηρήσεις (π.χ., κάθε 250ώ).",
                    "machineModel": "Μοντέλο Μηχανήματος",
                    "allModelsUniversal": "Όλα τα Μοντέλα (Καθολικό)",
                    "machineModelHelp": "Αφήστε κενό για εφαρμογή σε όλα τα μοντέλα μηχανημάτων",
                    "description": "Περιγραφή",
                    "descriptionPlaceholder": "Σύντομη περιγραφή αυτού του πρωτοκόλλου...",
                    "displayOrder": "Σειρά Εμφάνισης",
                    "displayOrderHelp": "Μικρότεροι αριθμοί εμφανίζονται πρώτοι",
                    "isActive": "Ενεργό (το πρωτόκολλο είναι διαθέσιμο για χρήση)"
                },
                "typeOptions": {
                    "daily": "Ημερήσιο",
                    "weekly": "Εβδομαδιαίο",
                    "scheduled": "Προγραμματισμένο (Βάσει Ωρών)",
                    "custom": "Προσαρμοσμένο"
                },
                "actions": {
                    "saving": "Αποθήκευση...",
                    "update": "Ενημέρωση Πρωτοκόλλου",
                    "create": "Δημιουργία Πρωτοκόλλου",
                    "cancel": "Ακύρωση"
                }
            }
        },
        "ar": {
            "maintenanceProtocols": {
                "title": "بروتوكولات الصيانة",
                "subtitle": "إدارة قوالب بروتوكولات الصيانة للآلات",
                "createNew": "إنشاء بروتوكول جديد",
                "noProtocols": "لم يتم العثور على بروتوكولات. أنشئ بروتوكولك الأول للبدء.",
                "loading": "تحميل البروتوكولات...",
                "confirmDelete": "هل أنت متأكد من أنك تريد حذف هذا البروتوكول؟",
                "deleteFailed": "فشل في حذف البروتوكول",
                "filters": {
                    "protocolType": "نوع البروتوكول",
                    "allTypes": "جميع الأنواع",
                    "machineModel": "طراز الآلة",
                    "allModels": "جميع الطرازات",
                    "universal": "عالمي (جميع الطرازات)",
                    "status": "الحالة",
                    "activeOnly": "النشطة فقط",
                    "all": "الكل",
                    "search": "بحث",
                    "searchPlaceholder": "البحث في البروتوكولات..."
                },
                "types": {
                    "daily": "يومي",
                    "weekly": "أسبوعي",
                    "scheduled": "مجدول",
                    "custom": "مخصص"
                },
                "card": {
                    "serviceInterval": "فترة الخدمة",
                    "hours": "س",
                    "checklistItems": "عناصر قائمة التحقق",
                    "manageChecklist": "إدارة قائمة التحقق",
                    "edit": "تحرير",
                    "delete": "حذف",
                    "inactive": "غير نشط"
                }
            },
            "protocolForm": {
                "editTitle": "تحرير البروتوكول",
                "createTitle": "إنشاء بروتوكول جديد",
                "fields": {
                    "name": "اسم البروتوكول",
                    "namePlaceholder": "مثال: بداية اليوم اليومية",
                    "type": "نوع البروتوكول",
                    "serviceHours": "ساعات الخدمة",
                    "serviceHoursPlaceholder": "مثال: 50 أو 250",
                    "serviceHoursHelp": "عدد ساعات التشغيل لهذه الخدمة",
                    "isRecurring": "خدمة متكررة (تكرار كل {hours} ساعة)",
                    "recurringHelp": "ألغِ التحديد للخدمات لمرة واحدة (مثل خدمة أولية 50س). حدد للخدمات المتكررة (مثل كل 250س).",
                    "machineModel": "طراز الآلة",
                    "allModelsUniversal": "جميع الطرازات (عالمي)",
                    "machineModelHelp": "اتركه فارغاً للتطبيق على جميع طرازات الآلات",
                    "description": "الوصف",
                    "descriptionPlaceholder": "وصف موجز لهذا البروتوكول...",
                    "displayOrder": "ترتيب العرض",
                    "displayOrderHelp": "الأرقام الأقل تظهر أولاً",
                    "isActive": "نشط (البروتوكول متاح للاستخدام)"
                },
                "typeOptions": {
                    "daily": "يومي",
                    "weekly": "أسبوعي",
                    "scheduled": "مجدول (على أساس الساعات)",
                    "custom": "مخصص"
                },
                "actions": {
                    "saving": "جاري الحفظ...",
                    "update": "تحديث البروتوكول",
                    "create": "إنشاء البروتوكول",
                    "cancel": "إلغاء"
                }
            }
        },
        "es": {
            "maintenanceProtocols": {
                "title": "Protocolos de Mantenimiento",
                "subtitle": "Gestionar plantillas de protocolos de mantenimiento para máquinas",
                "createNew": "Crear Nuevo Protocolo",
                "noProtocols": "No se encontraron protocolos. Crea tu primer protocolo para comenzar.",
                "loading": "Cargando protocolos...",
                "confirmDelete": "¿Estás seguro de que quieres eliminar este protocolo?",
                "deleteFailed": "Error al eliminar el protocolo",
                "filters": {
                    "protocolType": "Tipo de Protocolo",
                    "allTypes": "Todos los Tipos",
                    "machineModel": "Modelo de Máquina",
                    "allModels": "Todos los Modelos",
                    "universal": "Universal (Todos los Modelos)",
                    "status": "Estado",
                    "activeOnly": "Solo Activos",
                    "all": "Todos",
                    "search": "Buscar",
                    "searchPlaceholder": "Buscar protocolos..."
                },
                "types": {
                    "daily": "Diario",
                    "weekly": "Semanal",
                    "scheduled": "Programado",
                    "custom": "Personalizado"
                },
                "card": {
                    "serviceInterval": "Intervalo de Servicio",
                    "hours": "h",
                    "checklistItems": "elementos de lista de verificación",
                    "manageChecklist": "Gestionar Lista de Verificación",
                    "edit": "Editar",
                    "delete": "Eliminar",
                    "inactive": "Inactivo"
                }
            },
            "protocolForm": {
                "editTitle": "Editar Protocolo",
                "createTitle": "Crear Nuevo Protocolo",
                "fields": {
                    "name": "Nombre del Protocolo",
                    "namePlaceholder": "ej., Inicio Diario del Día",
                    "type": "Tipo de Protocolo",
                    "serviceHours": "Horas de Servicio",
                    "serviceHoursPlaceholder": "ej., 50 o 250",
                    "serviceHoursHelp": "Número de horas de operación para este servicio",
                    "isRecurring": "Servicio recurrente (repetir cada {hours} horas)",
                    "recurringHelp": "Desmarcar para servicios únicos (ej., servicio inicial de 50h). Marcar para servicios recurrentes (ej., cada 250h).",
                    "machineModel": "Modelo de Máquina",
                    "allModelsUniversal": "Todos los Modelos (Universal)",
                    "machineModelHelp": "Dejar vacío para aplicar a todos los modelos de máquinas",
                    "description": "Descripción",
                    "descriptionPlaceholder": "Breve descripción de este protocolo...",
                    "displayOrder": "Orden de Visualización",
                    "displayOrderHelp": "Los números más bajos aparecen primero",
                    "isActive": "Activo (el protocolo está disponible para uso)"
                },
                "typeOptions": {
                    "daily": "Diario",
                    "weekly": "Semanal",
                    "scheduled": "Programado (Basado en Horas)",
                    "custom": "Personalizado"
                },
                "actions": {
                    "saving": "Guardando...",
                    "update": "Actualizar Protocolo",
                    "create": "Crear Protocolo",
                    "cancel": "Cancelar"
                }
            }
        },
        "tr": {
            "maintenanceProtocols": {
                "title": "Bakım Protokolleri",
                "subtitle": "Makineler için bakım protokolü şablonlarını yönetin",
                "createNew": "Yeni Protokol Oluştur",
                "noProtocols": "Protokol bulunamadı. Başlamak için ilk protokolünüzü oluşturun.",
                "loading": "Protokoller yükleniyor...",
                "confirmDelete": "Bu protokolü silmek istediğinizden emin misiniz?",
                "deleteFailed": "Protokol silme başarısız",
                "filters": {
                    "protocolType": "Protokol Türü",
                    "allTypes": "Tüm Türler",
                    "machineModel": "Makine Modeli",
                    "allModels": "Tüm Modeller",
                    "universal": "Evrensel (Tüm Modeller)",
                    "status": "Durum",
                    "activeOnly": "Sadece Aktif",
                    "all": "Tümü",
                    "search": "Ara",
                    "searchPlaceholder": "Protokollerde ara..."
                },
                "types": {
                    "daily": "Günlük",
                    "weekly": "Haftalık",
                    "scheduled": "Planlanmış",
                    "custom": "Özel"
                },
                "card": {
                    "serviceInterval": "Servis Aralığı",
                    "hours": "s",
                    "checklistItems": "kontrol listesi öğeleri",
                    "manageChecklist": "Kontrol Listesini Yönet",
                    "edit": "Düzenle",
                    "delete": "Sil",
                    "inactive": "Pasif"
                }
            },
            "protocolForm": {
                "editTitle": "Protokolü Düzenle",
                "createTitle": "Yeni Protokol Oluştur",
                "fields": {
                    "name": "Protokol Adı",
                    "namePlaceholder": "örn., Günlük Gün Başlangıcı",
                    "type": "Protokol Türü",
                    "serviceHours": "Servis Saatleri",
                    "serviceHoursPlaceholder": "örn., 50 veya 250",
                    "serviceHoursHelp": "Bu servis için çalışma saati sayısı",
                    "isRecurring": "Tekrarlayan servis (her {hours} saatte tekrarla)",
                    "recurringHelp": "Tek seferlik servisler için işareti kaldırın (örn., 50s ilk servis). Tekrarlayan servisler için işaretleyin (örn., her 250s).",
                    "machineModel": "Makine Modeli",
                    "allModelsUniversal": "Tüm Modeller (Evrensel)",
                    "machineModelHelp": "Tüm makine modellerine uygulamak için boş bırakın",
                    "description": "Açıklama",
                    "descriptionPlaceholder": "Bu protokolün kısa açıklaması...",
                    "displayOrder": "Görüntüleme Sırası",
                    "displayOrderHelp": "Düşük sayılar önce görünür",
                    "isActive": "Aktif (protokol kullanım için mevcut)"
                },
                "typeOptions": {
                    "daily": "Günlük",
                    "weekly": "Haftalık",
                    "scheduled": "Planlanmış (Saat Bazlı)",
                    "custom": "Özel"
                },
                "actions": {
                    "saving": "Kaydediliyor...",
                    "update": "Protokolü Güncelle",
                    "create": "Protokol Oluştur",
                    "cancel": "İptal"
                }
            }
        },
        "no": {
            "maintenanceProtocols": {
                "title": "Vedlikeholdsprotokoll",
                "subtitle": "Administrer vedlikeholdsprotokollmaler for maskiner",
                "createNew": "Opprett Ny Protokoll",
                "noProtocols": "Ingen protokoller funnet. Opprett din første protokoll for å komme i gang.",
                "loading": "Laster protokoller...",
                "confirmDelete": "Er du sikker på at du vil slette denne protokollen?",
                "deleteFailed": "Kunne ikke slette protokoll",
                "filters": {
                    "protocolType": "Protokolltype",
                    "allTypes": "Alle Typer",
                    "machineModel": "Maskinmodell",
                    "allModels": "Alle Modeller",
                    "universal": "Universell (Alle Modeller)",
                    "status": "Status",
                    "activeOnly": "Kun Aktive",
                    "all": "Alle",
                    "search": "Søk",
                    "searchPlaceholder": "Søk protokoller..."
                },
                "types": {
                    "daily": "Daglig",
                    "weekly": "Ukentlig",
                    "scheduled": "Planlagt",
                    "custom": "Tilpasset"
                },
                "card": {
                    "serviceInterval": "Serviceintervall",
                    "hours": "t",
                    "checklistItems": "sjekkliste elementer",
                    "manageChecklist": "Administrer Sjekkliste",
                    "edit": "Rediger",
                    "delete": "Slett",
                    "inactive": "Inaktiv"
                }
            },
            "protocolForm": {
                "editTitle": "Rediger Protokoll",
                "createTitle": "Opprett Ny Protokoll",
                "fields": {
                    "name": "Protokollnavn",
                    "namePlaceholder": "f.eks., Daglig Oppstart",
                    "type": "Protokolltype",
                    "serviceHours": "Servicetimer",
                    "serviceHoursPlaceholder": "f.eks., 50 eller 250",
                    "serviceHoursHelp": "Antall driftstimer for denne tjenesten",
                    "isRecurring": "Gjentakende service (gjenta hver {hours} time)",
                    "recurringHelp": "Fjern avkrysning for engangsservice (f.eks., 50t første service). Kryss av for gjentakende service (f.eks., hver 250t).",
                    "machineModel": "Maskinmodell",
                    "allModelsUniversal": "Alle Modeller (Universell)",
                    "machineModelHelp": "La stå tom for å gjelde alle maskinmodeller",
                    "description": "Beskrivelse",
                    "descriptionPlaceholder": "Kort beskrivelse av denne protokollen...",
                    "displayOrder": "Visningsrekkefølge",
                    "displayOrderHelp": "Lavere tall vises først",
                    "isActive": "Aktiv (protokoll er tilgjengelig for bruk)"
                },
                "typeOptions": {
                    "daily": "Daglig",
                    "weekly": "Ukentlig",
                    "scheduled": "Planlagt (Timebasert)",
                    "custom": "Tilpasset"
                },
                "actions": {
                    "saving": "Lagrer...",
                    "update": "Oppdater Protokoll",
                    "create": "Opprett Protokoll",
                    "cancel": "Avbryt"
                }
            }
        }
    }
    
    # Process each locale file
    locale_dir = "frontend/src/locales"
    for lang_code, translations in protocols_translations.items():
        file_path = os.path.join(locale_dir, f"{lang_code}.json")
        
        if not os.path.exists(file_path):
            print(f"⚠️  Locale file not found: {file_path}")
            continue
            
        print(f"Adding maintenance protocols translations to {file_path}...")
        
        # Load existing translations
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Add maintenance protocols translations
        data.update(translations)
        
        # Write back to file
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ Added maintenance protocols translations to {lang_code}.json")
    
    print("\n🎉 Maintenance protocols translations added successfully!")
    print("The MaintenanceProtocols page and ProtocolForm component can now be localized.")

if __name__ == "__main__":
    add_maintenance_protocols_translations()