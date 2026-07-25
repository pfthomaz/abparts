#!/usr/bin/env python3

import json
import os

def add_checklist_items_translations():
    """Add comprehensive checklist items translations to all locale files"""
    
    # Checklist items translations
    checklist_translations = {
        "en": {
            "checklistManager": {
                "title": "Manage Checklist Items",
                "backToProtocols": "Back to Protocols",
                "protocol": "Protocol",
                "addItem": "Add Checklist Item",
                "loading": "Loading checklist items...",
                "noItems": "No checklist items yet. Add your first item to get started.",
                "dragTip": "Drag and drop items to reorder them",
                "confirmDelete": "Are you sure you want to delete this checklist item?",
                "deleteFailed": "Failed to delete item",
                "reorderFailed": "Failed to reorder items",
                "critical": "Critical",
                "minutes": "min",
                "edit": "Edit",
                "delete": "Delete",
                "itemTypes": {
                    "check": "Check",
                    "service": "Service", 
                    "replacement": "Replacement"
                }
            },
            "checklistItemForm": {
                "editTitle": "Edit Checklist Item",
                "addTitle": "Add Checklist Item",
                "fields": {
                    "description": "Description",
                    "descriptionPlaceholder": "e.g., Check oil level and top up if needed",
                    "descriptionRequired": "Description is required",
                    "itemType": "Item Type",
                    "category": "Category",
                    "categoryPlaceholder": "e.g., Electrical, Mechanical",
                    "estimatedDuration": "Estimated Duration (minutes)",
                    "durationPlaceholder": "e.g., 15",
                    "estimatedQuantity": "Estimated Quantity",
                    "quantityPlaceholder": "e.g., 2.5",
                    "isCritical": "Mark as Critical (must be completed)",
                    "notes": "Notes",
                    "notesPlaceholder": "Additional instructions or information"
                },
                "typeOptions": {
                    "check": "Check",
                    "service": "Service",
                    "replacement": "Replacement"
                },
                "actions": {
                    "cancel": "Cancel",
                    "saving": "Saving...",
                    "updateItem": "Update Item",
                    "addItem": "Add Item",
                    "saveFailed": "Failed to save checklist item"
                }
            }
        },
        "el": {
            "checklistManager": {
                "title": "Διαχείριση Στοιχείων Λίστας Ελέγχου",
                "backToProtocols": "Επιστροφή στα Πρωτόκολλα",
                "protocol": "Πρωτόκολλο",
                "addItem": "Προσθήκη Στοιχείου Λίστας Ελέγχου",
                "loading": "Φόρτωση στοιχείων λίστας ελέγχου...",
                "noItems": "Δεν υπάρχουν ακόμη στοιχεία λίστας ελέγχου. Προσθέστε το πρώτο σας στοιχείο για να ξεκινήσετε.",
                "dragTip": "Σύρετε και αφήστε στοιχεία για να τα αναδιατάξετε",
                "confirmDelete": "Είστε σίγουροι ότι θέλετε να διαγράψετε αυτό το στοιχείο λίστας ελέγχου;",
                "deleteFailed": "Αποτυχία διαγραφής στοιχείου",
                "reorderFailed": "Αποτυχία αναδιάταξης στοιχείων",
                "critical": "Κρίσιμο",
                "minutes": "λεπ",
                "edit": "Επεξεργασία",
                "delete": "Διαγραφή",
                "itemTypes": {
                    "check": "Έλεγχος",
                    "service": "Συντήρηση",
                    "replacement": "Αντικατάσταση"
                }
            },
            "checklistItemForm": {
                "editTitle": "Επεξεργασία Στοιχείου Λίστας Ελέγχου",
                "addTitle": "Προσθήκη Στοιχείου Λίστας Ελέγχου",
                "fields": {
                    "description": "Περιγραφή",
                    "descriptionPlaceholder": "π.χ., Έλεγχος στάθμης λαδιού και συμπλήρωση εάν χρειάζεται",
                    "descriptionRequired": "Η περιγραφή είναι υποχρεωτική",
                    "itemType": "Τύπος Στοιχείου",
                    "category": "Κατηγορία",
                    "categoryPlaceholder": "π.χ., Ηλεκτρικά, Μηχανικά",
                    "estimatedDuration": "Εκτιμώμενη Διάρκεια (λεπτά)",
                    "durationPlaceholder": "π.χ., 15",
                    "estimatedQuantity": "Εκτιμώμενη Ποσότητα",
                    "quantityPlaceholder": "π.χ., 2.5",
                    "isCritical": "Σήμανση ως Κρίσιμο (πρέπει να ολοκληρωθεί)",
                    "notes": "Σημειώσεις",
                    "notesPlaceholder": "Πρόσθετες οδηγίες ή πληροφορίες"
                },
                "typeOptions": {
                    "check": "Έλεγχος",
                    "service": "Συντήρηση",
                    "replacement": "Αντικατάσταση"
                },
                "actions": {
                    "cancel": "Ακύρωση",
                    "saving": "Αποθήκευση...",
                    "updateItem": "Ενημέρωση Στοιχείου",
                    "addItem": "Προσθήκη Στοιχείου",
                    "saveFailed": "Αποτυχία αποθήκευσης στοιχείου λίστας ελέγχου"
                }
            }
        },
        "ar": {
            "checklistManager": {
                "title": "إدارة عناصر قائمة التحقق",
                "backToProtocols": "العودة إلى البروتوكولات",
                "protocol": "البروتوكول",
                "addItem": "إضافة عنصر قائمة التحقق",
                "loading": "تحميل عناصر قائمة التحقق...",
                "noItems": "لا توجد عناصر قائمة تحقق بعد. أضف عنصرك الأول للبدء.",
                "dragTip": "اسحب وأفلت العناصر لإعادة ترتيبها",
                "confirmDelete": "هل أنت متأكد من أنك تريد حذف عنصر قائمة التحقق هذا؟",
                "deleteFailed": "فشل في حذف العنصر",
                "reorderFailed": "فشل في إعادة ترتيب العناصر",
                "critical": "حرج",
                "minutes": "دق",
                "edit": "تحرير",
                "delete": "حذف",
                "itemTypes": {
                    "check": "فحص",
                    "service": "خدمة",
                    "replacement": "استبدال"
                }
            },
            "checklistItemForm": {
                "editTitle": "تحرير عنصر قائمة التحقق",
                "addTitle": "إضافة عنصر قائمة التحقق",
                "fields": {
                    "description": "الوصف",
                    "descriptionPlaceholder": "مثال: فحص مستوى الزيت وإضافة المزيد إذا لزم الأمر",
                    "descriptionRequired": "الوصف مطلوب",
                    "itemType": "نوع العنصر",
                    "category": "الفئة",
                    "categoryPlaceholder": "مثال: كهربائي، ميكانيكي",
                    "estimatedDuration": "المدة المقدرة (دقائق)",
                    "durationPlaceholder": "مثال: 15",
                    "estimatedQuantity": "الكمية المقدرة",
                    "quantityPlaceholder": "مثال: 2.5",
                    "isCritical": "تحديد كحرج (يجب إكماله)",
                    "notes": "ملاحظات",
                    "notesPlaceholder": "تعليمات أو معلومات إضافية"
                },
                "typeOptions": {
                    "check": "فحص",
                    "service": "خدمة",
                    "replacement": "استبدال"
                },
                "actions": {
                    "cancel": "إلغاء",
                    "saving": "جاري الحفظ...",
                    "updateItem": "تحديث العنصر",
                    "addItem": "إضافة العنصر",
                    "saveFailed": "فشل في حفظ عنصر قائمة التحقق"
                }
            }
        },
        "es": {
            "checklistManager": {
                "title": "Gestionar Elementos de Lista de Verificación",
                "backToProtocols": "Volver a Protocolos",
                "protocol": "Protocolo",
                "addItem": "Agregar Elemento de Lista de Verificación",
                "loading": "Cargando elementos de lista de verificación...",
                "noItems": "Aún no hay elementos de lista de verificación. Agrega tu primer elemento para comenzar.",
                "dragTip": "Arrastra y suelta elementos para reordenarlos",
                "confirmDelete": "¿Estás seguro de que quieres eliminar este elemento de lista de verificación?",
                "deleteFailed": "Error al eliminar elemento",
                "reorderFailed": "Error al reordenar elementos",
                "critical": "Crítico",
                "minutes": "min",
                "edit": "Editar",
                "delete": "Eliminar",
                "itemTypes": {
                    "check": "Verificación",
                    "service": "Servicio",
                    "replacement": "Reemplazo"
                }
            },
            "checklistItemForm": {
                "editTitle": "Editar Elemento de Lista de Verificación",
                "addTitle": "Agregar Elemento de Lista de Verificación",
                "fields": {
                    "description": "Descripción",
                    "descriptionPlaceholder": "ej., Verificar nivel de aceite y rellenar si es necesario",
                    "descriptionRequired": "La descripción es requerida",
                    "itemType": "Tipo de Elemento",
                    "category": "Categoría",
                    "categoryPlaceholder": "ej., Eléctrico, Mecánico",
                    "estimatedDuration": "Duración Estimada (minutos)",
                    "durationPlaceholder": "ej., 15",
                    "estimatedQuantity": "Cantidad Estimada",
                    "quantityPlaceholder": "ej., 2.5",
                    "isCritical": "Marcar como Crítico (debe completarse)",
                    "notes": "Notas",
                    "notesPlaceholder": "Instrucciones o información adicional"
                },
                "typeOptions": {
                    "check": "Verificación",
                    "service": "Servicio",
                    "replacement": "Reemplazo"
                },
                "actions": {
                    "cancel": "Cancelar",
                    "saving": "Guardando...",
                    "updateItem": "Actualizar Elemento",
                    "addItem": "Agregar Elemento",
                    "saveFailed": "Error al guardar elemento de lista de verificación"
                }
            }
        },
        "tr": {
            "checklistManager": {
                "title": "Kontrol Listesi Öğelerini Yönet",
                "backToProtocols": "Protokollere Dön",
                "protocol": "Protokol",
                "addItem": "Kontrol Listesi Öğesi Ekle",
                "loading": "Kontrol listesi öğeleri yükleniyor...",
                "noItems": "Henüz kontrol listesi öğesi yok. Başlamak için ilk öğenizi ekleyin.",
                "dragTip": "Öğeleri yeniden sıralamak için sürükleyip bırakın",
                "confirmDelete": "Bu kontrol listesi öğesini silmek istediğinizden emin misiniz?",
                "deleteFailed": "Öğe silme başarısız",
                "reorderFailed": "Öğeleri yeniden sıralama başarısız",
                "critical": "Kritik",
                "minutes": "dk",
                "edit": "Düzenle",
                "delete": "Sil",
                "itemTypes": {
                    "check": "Kontrol",
                    "service": "Servis",
                    "replacement": "Değiştirme"
                }
            },
            "checklistItemForm": {
                "editTitle": "Kontrol Listesi Öğesini Düzenle",
                "addTitle": "Kontrol Listesi Öğesi Ekle",
                "fields": {
                    "description": "Açıklama",
                    "descriptionPlaceholder": "örn., Yağ seviyesini kontrol edin ve gerekirse ekleyin",
                    "descriptionRequired": "Açıklama gerekli",
                    "itemType": "Öğe Türü",
                    "category": "Kategori",
                    "categoryPlaceholder": "örn., Elektrik, Mekanik",
                    "estimatedDuration": "Tahmini Süre (dakika)",
                    "durationPlaceholder": "örn., 15",
                    "estimatedQuantity": "Tahmini Miktar",
                    "quantityPlaceholder": "örn., 2.5",
                    "isCritical": "Kritik olarak işaretle (tamamlanması gerekir)",
                    "notes": "Notlar",
                    "notesPlaceholder": "Ek talimatlar veya bilgiler"
                },
                "typeOptions": {
                    "check": "Kontrol",
                    "service": "Servis",
                    "replacement": "Değiştirme"
                },
                "actions": {
                    "cancel": "İptal",
                    "saving": "Kaydediliyor...",
                    "updateItem": "Öğeyi Güncelle",
                    "addItem": "Öğe Ekle",
                    "saveFailed": "Kontrol listesi öğesi kaydetme başarısız"
                }
            }
        },
        "no": {
            "checklistManager": {
                "title": "Administrer Sjekkliste Elementer",
                "backToProtocols": "Tilbake til Protokoller",
                "protocol": "Protokoll",
                "addItem": "Legg til Sjekkliste Element",
                "loading": "Laster sjekkliste elementer...",
                "noItems": "Ingen sjekkliste elementer ennå. Legg til ditt første element for å komme i gang.",
                "dragTip": "Dra og slipp elementer for å endre rekkefølge",
                "confirmDelete": "Er du sikker på at du vil slette dette sjekkliste elementet?",
                "deleteFailed": "Kunne ikke slette element",
                "reorderFailed": "Kunne ikke endre rekkefølge på elementer",
                "critical": "Kritisk",
                "minutes": "min",
                "edit": "Rediger",
                "delete": "Slett",
                "itemTypes": {
                    "check": "Sjekk",
                    "service": "Service",
                    "replacement": "Utskifting"
                }
            },
            "checklistItemForm": {
                "editTitle": "Rediger Sjekkliste Element",
                "addTitle": "Legg til Sjekkliste Element",
                "fields": {
                    "description": "Beskrivelse",
                    "descriptionPlaceholder": "f.eks., Sjekk oljenivå og fyll på om nødvendig",
                    "descriptionRequired": "Beskrivelse er påkrevd",
                    "itemType": "Elementtype",
                    "category": "Kategori",
                    "categoryPlaceholder": "f.eks., Elektrisk, Mekanisk",
                    "estimatedDuration": "Estimert Varighet (minutter)",
                    "durationPlaceholder": "f.eks., 15",
                    "estimatedQuantity": "Estimert Mengde",
                    "quantityPlaceholder": "f.eks., 2.5",
                    "isCritical": "Merk som Kritisk (må fullføres)",
                    "notes": "Notater",
                    "notesPlaceholder": "Tilleggsinstruksjoner eller informasjon"
                },
                "typeOptions": {
                    "check": "Sjekk",
                    "service": "Service",
                    "replacement": "Utskifting"
                },
                "actions": {
                    "cancel": "Avbryt",
                    "saving": "Lagrer...",
                    "updateItem": "Oppdater Element",
                    "addItem": "Legg til Element",
                    "saveFailed": "Kunne ikke lagre sjekkliste element"
                }
            }
        }
    }
    
    # Process each locale file
    locale_dir = "frontend/src/locales"
    for lang_code, translations in checklist_translations.items():
        file_path = os.path.join(locale_dir, f"{lang_code}.json")
        
        if not os.path.exists(file_path):
            print(f"⚠️  Locale file not found: {file_path}")
            continue
            
        print(f"Adding checklist items translations to {file_path}...")
        
        # Load existing translations
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Add checklist items translations
        data.update(translations)
        
        # Write back to file
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ Added checklist items translations to {lang_code}.json")
    
    print("\n🎉 Checklist items translations added successfully!")
    print("The ChecklistItemManager and ChecklistItemForm components can now be localized.")

if __name__ == "__main__":
    add_checklist_items_translations()