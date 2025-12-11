#!/usr/bin/env python3

import json
import os

def add_translation_ui_strings():
    """Add translation management UI strings to all language files"""
    
    # Translation UI strings
    translation_strings = {
        "translations": {
            "manageTranslations": "Manage Translations",
            "manageTranslationsDescription": "Translate maintenance protocols and checklist items into different languages",
            "overview": "Overview",
            "noStatus": "No translation status available",
            "baseLanguage": "Base Language",
            "totalItems": "Total Items",
            "completedLanguages": "Completed Languages",
            "progress": "Progress",
            "edit": "Edit",
            "start": "Start",
            "checklist": "Checklist",
            "quickActions": "Quick Actions",
            "exportTranslations": "Export Translations",
            "importTranslations": "Import Translations",
            "bulkTranslate": "Bulk Translate",
            "editTranslation": "Edit Translation",
            "createTranslation": "Create Translation",
            "translateProtocolTo": "Translate protocol to",
            "originalContent": "Original Content",
            "translationContent": "Translation Content",
            "enterTranslation": "Enter translation...",
            "translationTips": "Translation Tips",
            "tip1": "Keep the meaning and context of the original text",
            "tip2": "Use appropriate technical terminology for your language",
            "tip3": "Consider cultural differences when translating",
            "tip4": "Maintain consistency across all translations",
            "translateChecklist": "Translate Checklist Items",
            "translateTo": "Translate to",
            "translationProgress": "Translation Progress",
            "checklistItem": "Checklist Item",
            "step": "Step",
            "translated": "Translated",
            "pending": "Pending",
            "completed": "Completed",
            "saveAllTranslations": "Save all translations",
            "saveAll": "Save All",
            "saving": "Saving...",
            "errors": {
                "nameRequired": "Protocol name is required",
                "descriptionRequired": "Description is required",
                "saveFailed": "Failed to save translation"
            }
        }
    }

    # Language-specific translations
    language_translations = {
        "el": {
            "translations": {
                "manageTranslations": "Διαχείριση Μεταφράσεων",
                "manageTranslationsDescription": "Μετάφραση πρωτοκόλλων συντήρησης και στοιχείων ελέγχου σε διαφορετικές γλώσσες",
                "overview": "Επισκόπηση",
                "noStatus": "Δεν υπάρχει διαθέσιμη κατάσταση μετάφρασης",
                "baseLanguage": "Βασική Γλώσσα",
                "totalItems": "Συνολικά Στοιχεία",
                "completedLanguages": "Ολοκληρωμένες Γλώσσες",
                "progress": "Πρόοδος",
                "edit": "Επεξεργασία",
                "start": "Έναρξη",
                "checklist": "Λίστα Ελέγχου",
                "quickActions": "Γρήγορες Ενέργειες",
                "exportTranslations": "Εξαγωγή Μεταφράσεων",
                "importTranslations": "Εισαγωγή Μεταφράσεων",
                "bulkTranslate": "Μαζική Μετάφραση",
                "editTranslation": "Επεξεργασία Μετάφρασης",
                "createTranslation": "Δημιουργία Μετάφρασης",
                "translateProtocolTo": "Μετάφραση πρωτοκόλλου σε",
                "originalContent": "Αρχικό Περιεχόμενο",
                "translationContent": "Περιεχόμενο Μετάφρασης",
                "enterTranslation": "Εισάγετε μετάφραση...",
                "translationTips": "Συμβουλές Μετάφρασης",
                "tip1": "Διατηρήστε το νόημα και το πλαίσιο του αρχικού κειμένου",
                "tip2": "Χρησιμοποιήστε κατάλληλη τεχνική ορολογία για τη γλώσσα σας",
                "tip3": "Λάβετε υπόψη τις πολιτισμικές διαφορές κατά τη μετάφραση",
                "tip4": "Διατηρήστε συνέπεια σε όλες τις μεταφράσεις",
                "translateChecklist": "Μετάφραση Στοιχείων Λίστας Ελέγχου",
                "translateTo": "Μετάφραση σε",
                "translationProgress": "Πρόοδος Μετάφρασης",
                "checklistItem": "Στοιχείο Λίστας Ελέγχου",
                "step": "Βήμα",
                "translated": "Μεταφρασμένο",
                "pending": "Εκκρεμεί",
                "completed": "Ολοκληρωμένο",
                "saveAllTranslations": "Αποθήκευση όλων των μεταφράσεων",
                "saveAll": "Αποθήκευση Όλων",
                "saving": "Αποθήκευση...",
                "errors": {
                    "nameRequired": "Το όνομα του πρωτοκόλλου είναι υποχρεωτικό",
                    "descriptionRequired": "Η περιγραφή είναι υποχρεωτική",
                    "saveFailed": "Αποτυχία αποθήκευσης μετάφρασης"
                }
            }
        },
        "ar": {
            "translations": {
                "manageTranslations": "إدارة الترجمات",
                "manageTranslationsDescription": "ترجمة بروتوكولات الصيانة وعناصر قائمة التحقق إلى لغات مختلفة",
                "overview": "نظرة عامة",
                "noStatus": "لا توجد حالة ترجمة متاحة",
                "baseLanguage": "اللغة الأساسية",
                "totalItems": "إجمالي العناصر",
                "completedLanguages": "اللغات المكتملة",
                "progress": "التقدم",
                "edit": "تحرير",
                "start": "بدء",
                "checklist": "قائمة التحقق",
                "quickActions": "إجراءات سريعة",
                "exportTranslations": "تصدير الترجمات",
                "importTranslations": "استيراد الترجمات",
                "bulkTranslate": "ترجمة مجمعة",
                "editTranslation": "تحرير الترجمة",
                "createTranslation": "إنشاء ترجمة",
                "translateProtocolTo": "ترجمة البروتوكول إلى",
                "originalContent": "المحتوى الأصلي",
                "translationContent": "محتوى الترجمة",
                "enterTranslation": "أدخل الترجمة...",
                "translationTips": "نصائح الترجمة",
                "tip1": "احتفظ بمعنى وسياق النص الأصلي",
                "tip2": "استخدم المصطلحات التقنية المناسبة للغتك",
                "tip3": "اعتبر الاختلافات الثقافية عند الترجمة",
                "tip4": "حافظ على الاتساق عبر جميع الترجمات",
                "translateChecklist": "ترجمة عناصر قائمة التحقق",
                "translateTo": "ترجمة إلى",
                "translationProgress": "تقدم الترجمة",
                "checklistItem": "عنصر قائمة التحقق",
                "step": "خطوة",
                "translated": "مترجم",
                "pending": "معلق",
                "completed": "مكتمل",
                "saveAllTranslations": "حفظ جميع الترجمات",
                "saveAll": "حفظ الكل",
                "saving": "جاري الحفظ...",
                "errors": {
                    "nameRequired": "اسم البروتوكول مطلوب",
                    "descriptionRequired": "الوصف مطلوب",
                    "saveFailed": "فشل في حفظ الترجمة"
                }
            }
        },
        "es": {
            "translations": {
                "manageTranslations": "Gestionar Traducciones",
                "manageTranslationsDescription": "Traducir protocolos de mantenimiento y elementos de lista de verificación a diferentes idiomas",
                "overview": "Resumen",
                "noStatus": "No hay estado de traducción disponible",
                "baseLanguage": "Idioma Base",
                "totalItems": "Total de Elementos",
                "completedLanguages": "Idiomas Completados",
                "progress": "Progreso",
                "edit": "Editar",
                "start": "Iniciar",
                "checklist": "Lista de Verificación",
                "quickActions": "Acciones Rápidas",
                "exportTranslations": "Exportar Traducciones",
                "importTranslations": "Importar Traducciones",
                "bulkTranslate": "Traducción Masiva",
                "editTranslation": "Editar Traducción",
                "createTranslation": "Crear Traducción",
                "translateProtocolTo": "Traducir protocolo a",
                "originalContent": "Contenido Original",
                "translationContent": "Contenido de Traducción",
                "enterTranslation": "Ingrese traducción...",
                "translationTips": "Consejos de Traducción",
                "tip1": "Mantenga el significado y contexto del texto original",
                "tip2": "Use terminología técnica apropiada para su idioma",
                "tip3": "Considere las diferencias culturales al traducir",
                "tip4": "Mantenga consistencia en todas las traducciones",
                "translateChecklist": "Traducir Elementos de Lista de Verificación",
                "translateTo": "Traducir a",
                "translationProgress": "Progreso de Traducción",
                "checklistItem": "Elemento de Lista de Verificación",
                "step": "Paso",
                "translated": "Traducido",
                "pending": "Pendiente",
                "completed": "Completado",
                "saveAllTranslations": "Guardar todas las traducciones",
                "saveAll": "Guardar Todo",
                "saving": "Guardando...",
                "errors": {
                    "nameRequired": "El nombre del protocolo es requerido",
                    "descriptionRequired": "La descripción es requerida",
                    "saveFailed": "Error al guardar la traducción"
                }
            }
        },
        "tr": {
            "translations": {
                "manageTranslations": "Çevirileri Yönet",
                "manageTranslationsDescription": "Bakım protokollerini ve kontrol listesi öğelerini farklı dillere çevirin",
                "overview": "Genel Bakış",
                "noStatus": "Kullanılabilir çeviri durumu yok",
                "baseLanguage": "Temel Dil",
                "totalItems": "Toplam Öğeler",
                "completedLanguages": "Tamamlanan Diller",
                "progress": "İlerleme",
                "edit": "Düzenle",
                "start": "Başla",
                "checklist": "Kontrol Listesi",
                "quickActions": "Hızlı İşlemler",
                "exportTranslations": "Çevirileri Dışa Aktar",
                "importTranslations": "Çevirileri İçe Aktar",
                "bulkTranslate": "Toplu Çeviri",
                "editTranslation": "Çeviriyi Düzenle",
                "createTranslation": "Çeviri Oluştur",
                "translateProtocolTo": "Protokolü şuna çevir",
                "originalContent": "Orijinal İçerik",
                "translationContent": "Çeviri İçeriği",
                "enterTranslation": "Çeviri girin...",
                "translationTips": "Çeviri İpuçları",
                "tip1": "Orijinal metnin anlamını ve bağlamını koruyun",
                "tip2": "Diliniz için uygun teknik terminoloji kullanın",
                "tip3": "Çeviri yaparken kültürel farklılıkları göz önünde bulundurun",
                "tip4": "Tüm çevirilerde tutarlılığı koruyun",
                "translateChecklist": "Kontrol Listesi Öğelerini Çevir",
                "translateTo": "Şuna çevir",
                "translationProgress": "Çeviri İlerlemesi",
                "checklistItem": "Kontrol Listesi Öğesi",
                "step": "Adım",
                "translated": "Çevrildi",
                "pending": "Beklemede",
                "completed": "Tamamlandı",
                "saveAllTranslations": "Tüm çevirileri kaydet",
                "saveAll": "Tümünü Kaydet",
                "saving": "Kaydediliyor...",
                "errors": {
                    "nameRequired": "Protokol adı gereklidir",
                    "descriptionRequired": "Açıklama gereklidir",
                    "saveFailed": "Çeviri kaydedilemedi"
                }
            }
        },
        "no": {
            "translations": {
                "manageTranslations": "Administrer Oversettelser",
                "manageTranslationsDescription": "Oversett vedlikeholdsprotokoller og sjekkliste-elementer til forskjellige språk",
                "overview": "Oversikt",
                "noStatus": "Ingen oversettelsestatus tilgjengelig",
                "baseLanguage": "Grunnspråk",
                "totalItems": "Totalt Elementer",
                "completedLanguages": "Fullførte Språk",
                "progress": "Fremgang",
                "edit": "Rediger",
                "start": "Start",
                "checklist": "Sjekkliste",
                "quickActions": "Hurtighandlinger",
                "exportTranslations": "Eksporter Oversettelser",
                "importTranslations": "Importer Oversettelser",
                "bulkTranslate": "Masseoversetelse",
                "editTranslation": "Rediger Oversettelse",
                "createTranslation": "Opprett Oversettelse",
                "translateProtocolTo": "Oversett protokoll til",
                "originalContent": "Originalt Innhold",
                "translationContent": "Oversettelsesinnhold",
                "enterTranslation": "Skriv inn oversettelse...",
                "translationTips": "Oversettelsetips",
                "tip1": "Behold betydningen og konteksten til den opprinnelige teksten",
                "tip2": "Bruk passende teknisk terminologi for ditt språk",
                "tip3": "Vurder kulturelle forskjeller når du oversetter",
                "tip4": "Oppretthold konsistens på tvers av alle oversettelser",
                "translateChecklist": "Oversett Sjekkliste-elementer",
                "translateTo": "Oversett til",
                "translationProgress": "Oversettelsesframgang",
                "checklistItem": "Sjekkliste-element",
                "step": "Trinn",
                "translated": "Oversatt",
                "pending": "Venter",
                "completed": "Fullført",
                "saveAllTranslations": "Lagre alle oversettelser",
                "saveAll": "Lagre Alle",
                "saving": "Lagrer...",
                "errors": {
                    "nameRequired": "Protokollnavn er påkrevd",
                    "descriptionRequired": "Beskrivelse er påkrevd",
                    "saveFailed": "Kunne ikke lagre oversettelse"
                }
            }
        }
    }

    # Get the frontend locales directory
    locales_dir = "frontend/src/locales"
    
    if not os.path.exists(locales_dir):
        print(f"❌ Locales directory not found: {locales_dir}")
        return False

    success_count = 0
    
    # Process each language file
    for lang_code in ["en", "el", "ar", "es", "tr", "no"]:
        file_path = os.path.join(locales_dir, f"{lang_code}.json")
        
        try:
            # Load existing translations
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    existing_translations = json.load(f)
            else:
                existing_translations = {}
            
            # Use language-specific translations if available, otherwise use English
            if lang_code in language_translations:
                new_strings = language_translations[lang_code]
            else:
                new_strings = translation_strings
            
            # Merge translations
            existing_translations.update(new_strings)
            
            # Write back to file
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(existing_translations, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Updated {lang_code}.json with translation UI strings")
            success_count += 1
            
        except Exception as e:
            print(f"❌ Failed to update {lang_code}.json: {e}")
    
    print(f"\n🎉 Successfully updated {success_count}/6 language files with translation UI strings!")
    return success_count == 6

if __name__ == "__main__":
    add_translation_ui_strings()