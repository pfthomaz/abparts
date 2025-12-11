#!/usr/bin/env python3

import json
import os

def add_protocol_translations_page_strings():
    """Add Protocol Translations page strings to all language files"""
    
    # Protocol Translations page strings
    translation_strings = {
        "translations": {
            "totalProtocols": "Total Protocols",
            "fullyTranslated": "Fully Translated",
            "partiallyTranslated": "Partially Translated",
            "untranslated": "Untranslated",
            "allProtocols": "All Protocols",
            "languages": "Languages",
            "checklistItems": "checklist items",
            "startTranslating": "Start Translating",
            "noProtocolsFound": "No protocols found",
            "noProtocolsYet": "No protocols available yet",
            "tryDifferentSearch": "Try adjusting your search or filter criteria",
            "createProtocolsFirst": "Create maintenance protocols first to enable translations"
        },
        "navigation": {
            "protocolTranslations": "Protocol Translations",
            "protocolTranslationsDescription": "Manage multi-language protocol translations"
        }
    }

    # Language-specific translations
    language_translations = {
        "el": {
            "translations": {
                "totalProtocols": "Συνολικά Πρωτόκολλα",
                "fullyTranslated": "Πλήρως Μεταφρασμένα",
                "partiallyTranslated": "Μερικώς Μεταφρασμένα",
                "untranslated": "Αμετάφραστα",
                "allProtocols": "Όλα τα Πρωτόκολλα",
                "languages": "Γλώσσες",
                "checklistItems": "στοιχεία λίστας ελέγχου",
                "startTranslating": "Έναρξη Μετάφρασης",
                "noProtocolsFound": "Δεν βρέθηκαν πρωτόκολλα",
                "noProtocolsYet": "Δεν υπάρχουν ακόμη πρωτόκολλα",
                "tryDifferentSearch": "Δοκιμάστε να προσαρμόσετε τα κριτήρια αναζήτησης ή φίλτρου",
                "createProtocolsFirst": "Δημιουργήστε πρώτα πρωτόκολλα συντήρησης για να ενεργοποιήσετε τις μεταφράσεις"
            },
            "navigation": {
                "protocolTranslations": "Μεταφράσεις Πρωτοκόλλων",
                "protocolTranslationsDescription": "Διαχείριση μεταφράσεων πρωτοκόλλων σε πολλές γλώσσες"
            }
        },
        "ar": {
            "translations": {
                "totalProtocols": "إجمالي البروتوكولات",
                "fullyTranslated": "مترجم بالكامل",
                "partiallyTranslated": "مترجم جزئياً",
                "untranslated": "غير مترجم",
                "allProtocols": "جميع البروتوكولات",
                "languages": "اللغات",
                "checklistItems": "عناصر قائمة التحقق",
                "startTranslating": "بدء الترجمة",
                "noProtocolsFound": "لم يتم العثور على بروتوكولات",
                "noProtocolsYet": "لا توجد بروتوكولات متاحة بعد",
                "tryDifferentSearch": "جرب تعديل معايير البحث أو التصفية",
                "createProtocolsFirst": "أنشئ بروتوكولات الصيانة أولاً لتمكين الترجمات"
            },
            "navigation": {
                "protocolTranslations": "ترجمات البروتوكولات",
                "protocolTranslationsDescription": "إدارة ترجمات البروتوكولات متعددة اللغات"
            }
        },
        "es": {
            "translations": {
                "totalProtocols": "Total de Protocolos",
                "fullyTranslated": "Completamente Traducido",
                "partiallyTranslated": "Parcialmente Traducido",
                "untranslated": "Sin Traducir",
                "allProtocols": "Todos los Protocolos",
                "languages": "Idiomas",
                "checklistItems": "elementos de lista de verificación",
                "startTranslating": "Comenzar Traducción",
                "noProtocolsFound": "No se encontraron protocolos",
                "noProtocolsYet": "Aún no hay protocolos disponibles",
                "tryDifferentSearch": "Intenta ajustar tus criterios de búsqueda o filtro",
                "createProtocolsFirst": "Crea primero protocolos de mantenimiento para habilitar traducciones"
            },
            "navigation": {
                "protocolTranslations": "Traducciones de Protocolos",
                "protocolTranslationsDescription": "Gestionar traducciones de protocolos en múltiples idiomas"
            }
        },
        "tr": {
            "translations": {
                "totalProtocols": "Toplam Protokoller",
                "fullyTranslated": "Tamamen Çevrildi",
                "partiallyTranslated": "Kısmen Çevrildi",
                "untranslated": "Çevrilmedi",
                "allProtocols": "Tüm Protokoller",
                "languages": "Diller",
                "checklistItems": "kontrol listesi öğeleri",
                "startTranslating": "Çeviriye Başla",
                "noProtocolsFound": "Protokol bulunamadı",
                "noProtocolsYet": "Henüz mevcut protokol yok",
                "tryDifferentSearch": "Arama veya filtre kriterlerinizi ayarlamayı deneyin",
                "createProtocolsFirst": "Çevirileri etkinleştirmek için önce bakım protokolleri oluşturun"
            },
            "navigation": {
                "protocolTranslations": "Protokol Çevirileri",
                "protocolTranslationsDescription": "Çok dilli protokol çevirilerini yönet"
            }
        },
        "no": {
            "translations": {
                "totalProtocols": "Totalt Protokoller",
                "fullyTranslated": "Fullstendig Oversatt",
                "partiallyTranslated": "Delvis Oversatt",
                "untranslated": "Ikke Oversatt",
                "allProtocols": "Alle Protokoller",
                "languages": "Språk",
                "checklistItems": "sjekkliste-elementer",
                "startTranslating": "Start Oversettelse",
                "noProtocolsFound": "Ingen protokoller funnet",
                "noProtocolsYet": "Ingen protokoller tilgjengelig ennå",
                "tryDifferentSearch": "Prøv å justere søke- eller filterkriteriene dine",
                "createProtocolsFirst": "Opprett vedlikeholdsprotokoller først for å aktivere oversettelser"
            },
            "navigation": {
                "protocolTranslations": "Protokolloversettelser",
                "protocolTranslationsDescription": "Administrer flerspråklige protokolloversettelser"
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
            
            # Merge translations (deep merge for nested objects)
            for key, value in new_strings.items():
                if key in existing_translations and isinstance(existing_translations[key], dict) and isinstance(value, dict):
                    existing_translations[key].update(value)
                else:
                    existing_translations[key] = value
            
            # Write back to file
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(existing_translations, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Updated {lang_code}.json with Protocol Translations page strings")
            success_count += 1
            
        except Exception as e:
            print(f"❌ Failed to update {lang_code}.json: {e}")
    
    print(f"\n🎉 Successfully updated {success_count}/6 language files with Protocol Translations page strings!")
    return success_count == 6

if __name__ == "__main__":
    add_protocol_translations_page_strings()