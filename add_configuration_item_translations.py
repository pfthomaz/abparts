#!/usr/bin/env python3

import json
import os

def add_configuration_translations():
    """Add comprehensive configuration item translations to all locale files"""
    
    # Configuration key translations and descriptions
    config_translations = {
        "en": {
            "configKeys": {
                "org.default_country": "Default Country",
                "org.auto_create_warehouse": "Auto-Create Warehouse", 
                "org.max_suppliers_per_organization": "Max Suppliers per Organization",
                "parts.max_photos_per_part": "Max Photos per Part",
                "parts.photo_max_size_mb": "Max Photo Size (MB)",
                "parts.supported_photo_formats": "Supported Photo Formats",
                "user.password_min_length": "Minimum Password Length",
                "user.session_timeout_minutes": "Session Timeout (Minutes)",
                "user.max_failed_login_attempts": "Max Failed Login Attempts",
                "locale.supported_languages": "Supported Languages",
                "locale.supported_countries": "Supported Countries", 
                "locale.default_language": "Default Language",
                "test.config": "Test Configuration",
                "test_update_value": "Test Update Value"
            },
            "configDescriptions": {
                "org.default_country": "Default country for new organizations",
                "org.auto_create_warehouse": "Automatically create default warehouse for new organizations",
                "org.max_suppliers_per_organization": "Maximum number of suppliers per organization",
                "parts.max_photos_per_part": "Maximum number of photos per part",
                "parts.photo_max_size_mb": "Maximum photo size in MB",
                "parts.supported_photo_formats": "Supported photo formats for parts",
                "user.password_min_length": "Minimum password length",
                "user.session_timeout_minutes": "Session timeout in minutes",
                "user.max_failed_login_attempts": "Maximum failed login attempts before lockout",
                "locale.supported_languages": "Supported languages",
                "locale.supported_countries": "Supported countries",
                "locale.default_language": "Default language for new users",
                "test.config": "Test configuration",
                "test_update_value": "Test update value"
            },
            "validationRules": {
                "allowed_values": "Allowed Values",
                "min": "Minimum",
                "max": "Maximum",
                "min_length": "Minimum Length",
                "max_length": "Maximum Length"
            }
        },
        "el": {
            "configKeys": {
                "org.default_country": "Προεπιλεγμένη Χώρα",
                "org.auto_create_warehouse": "Αυτόματη Δημιουργία Αποθήκης",
                "org.max_suppliers_per_organization": "Μέγιστοι Προμηθευτές ανά Οργανισμό",
                "parts.max_photos_per_part": "Μέγιστες Φωτογραφίες ανά Εξάρτημα",
                "parts.photo_max_size_mb": "Μέγιστο Μέγεθος Φωτογραφίας (MB)",
                "parts.supported_photo_formats": "Υποστηριζόμενες Μορφές Φωτογραφιών",
                "user.password_min_length": "Ελάχιστο Μήκος Κωδικού Πρόσβασης",
                "user.session_timeout_minutes": "Χρονικό Όριο Συνεδρίας (Λεπτά)",
                "user.max_failed_login_attempts": "Μέγιστες Αποτυχημένες Προσπάθειες Σύνδεσης",
                "locale.supported_languages": "Υποστηριζόμενες Γλώσσες",
                "locale.supported_countries": "Υποστηριζόμενες Χώρες",
                "locale.default_language": "Προεπιλεγμένη Γλώσσα",
                "test.config": "Διαμόρφωση Δοκιμής",
                "test_update_value": "Τιμή Ενημέρωσης Δοκιμής"
            },
            "configDescriptions": {
                "org.default_country": "Προεπιλεγμένη χώρα για νέους οργανισμούς",
                "org.auto_create_warehouse": "Αυτόματη δημιουργία προεπιλεγμένης αποθήκης για νέους οργανισμούς",
                "org.max_suppliers_per_organization": "Μέγιστος αριθμός προμηθευτών ανά οργανισμό",
                "parts.max_photos_per_part": "Μέγιστος αριθμός φωτογραφιών ανά εξάρτημα",
                "parts.photo_max_size_mb": "Μέγιστο μέγεθος φωτογραφίας σε MB",
                "parts.supported_photo_formats": "Υποστηριζόμενες μορφές φωτογραφιών για εξαρτήματα",
                "user.password_min_length": "Ελάχιστο μήκος κωδικού πρόσβασης",
                "user.session_timeout_minutes": "Χρονικό όριο συνεδρίας σε λεπτά",
                "user.max_failed_login_attempts": "Μέγιστες αποτυχημένες προσπάθειες σύνδεσης πριν το κλείδωμα",
                "locale.supported_languages": "Υποστηριζόμενες γλώσσες",
                "locale.supported_countries": "Υποστηριζόμενες χώρες",
                "locale.default_language": "Προεπιλεγμένη γλώσσα για νέους χρήστες",
                "test.config": "Διαμόρφωση δοκιμής",
                "test_update_value": "Τιμή ενημέρωσης δοκιμής"
            },
            "validationRules": {
                "allowed_values": "Επιτρεπόμενες Τιμές",
                "min": "Ελάχιστο",
                "max": "Μέγιστο",
                "min_length": "Ελάχιστο Μήκος",
                "max_length": "Μέγιστο Μήκος"
            }
        },
        "ar": {
            "configKeys": {
                "org.default_country": "البلد الافتراضي",
                "org.auto_create_warehouse": "إنشاء المستودع تلقائياً",
                "org.max_suppliers_per_organization": "الحد الأقصى للموردين لكل منظمة",
                "parts.max_photos_per_part": "الحد الأقصى للصور لكل قطعة",
                "parts.photo_max_size_mb": "الحد الأقصى لحجم الصورة (ميجابايت)",
                "parts.supported_photo_formats": "تنسيقات الصور المدعومة",
                "user.password_min_length": "الحد الأدنى لطول كلمة المرور",
                "user.session_timeout_minutes": "انتهاء مهلة الجلسة (دقائق)",
                "user.max_failed_login_attempts": "الحد الأقصى لمحاولات تسجيل الدخول الفاشلة",
                "locale.supported_languages": "اللغات المدعومة",
                "locale.supported_countries": "البلدان المدعومة",
                "locale.default_language": "اللغة الافتراضية",
                "test.config": "تكوين الاختبار",
                "test_update_value": "قيمة تحديث الاختبار"
            },
            "configDescriptions": {
                "org.default_country": "البلد الافتراضي للمنظمات الجديدة",
                "org.auto_create_warehouse": "إنشاء مستودع افتراضي تلقائياً للمنظمات الجديدة",
                "org.max_suppliers_per_organization": "الحد الأقصى لعدد الموردين لكل منظمة",
                "parts.max_photos_per_part": "الحد الأقصى لعدد الصور لكل قطعة",
                "parts.photo_max_size_mb": "الحد الأقصى لحجم الصورة بالميجابايت",
                "parts.supported_photo_formats": "تنسيقات الصور المدعومة للقطع",
                "user.password_min_length": "الحد الأدنى لطول كلمة المرور",
                "user.session_timeout_minutes": "انتهاء مهلة الجلسة بالدقائق",
                "user.max_failed_login_attempts": "الحد الأقصى لمحاولات تسجيل الدخول الفاشلة قبل الحظر",
                "locale.supported_languages": "اللغات المدعومة",
                "locale.supported_countries": "البلدان المدعومة",
                "locale.default_language": "اللغة الافتراضية للمستخدمين الجدد",
                "test.config": "تكوين الاختبار",
                "test_update_value": "قيمة تحديث الاختبار"
            },
            "validationRules": {
                "allowed_values": "القيم المسموحة",
                "min": "الحد الأدنى",
                "max": "الحد الأقصى",
                "min_length": "الحد الأدنى للطول",
                "max_length": "الحد الأقصى للطول"
            }
        },
        "es": {
            "configKeys": {
                "org.default_country": "País Predeterminado",
                "org.auto_create_warehouse": "Crear Almacén Automáticamente",
                "org.max_suppliers_per_organization": "Máx. Proveedores por Organización",
                "parts.max_photos_per_part": "Máx. Fotos por Pieza",
                "parts.photo_max_size_mb": "Tamaño Máx. de Foto (MB)",
                "parts.supported_photo_formats": "Formatos de Foto Soportados",
                "user.password_min_length": "Longitud Mín. de Contraseña",
                "user.session_timeout_minutes": "Tiempo de Espera de Sesión (Minutos)",
                "user.max_failed_login_attempts": "Máx. Intentos de Inicio Fallidos",
                "locale.supported_languages": "Idiomas Soportados",
                "locale.supported_countries": "Países Soportados",
                "locale.default_language": "Idioma Predeterminado",
                "test.config": "Configuración de Prueba",
                "test_update_value": "Valor de Actualización de Prueba"
            },
            "configDescriptions": {
                "org.default_country": "País predeterminado para nuevas organizaciones",
                "org.auto_create_warehouse": "Crear automáticamente almacén predeterminado para nuevas organizaciones",
                "org.max_suppliers_per_organization": "Número máximo de proveedores por organización",
                "parts.max_photos_per_part": "Número máximo de fotos por pieza",
                "parts.photo_max_size_mb": "Tamaño máximo de foto en MB",
                "parts.supported_photo_formats": "Formatos de foto soportados para piezas",
                "user.password_min_length": "Longitud mínima de contraseña",
                "user.session_timeout_minutes": "Tiempo de espera de sesión en minutos",
                "user.max_failed_login_attempts": "Máximo de intentos de inicio fallidos antes del bloqueo",
                "locale.supported_languages": "Idiomas soportados",
                "locale.supported_countries": "Países soportados",
                "locale.default_language": "Idioma predeterminado para nuevos usuarios",
                "test.config": "Configuración de prueba",
                "test_update_value": "Valor de actualización de prueba"
            },
            "validationRules": {
                "allowed_values": "Valores Permitidos",
                "min": "Mínimo",
                "max": "Máximo",
                "min_length": "Longitud Mínima",
                "max_length": "Longitud Máxima"
            }
        },
        "tr": {
            "configKeys": {
                "org.default_country": "Varsayılan Ülke",
                "org.auto_create_warehouse": "Otomatik Depo Oluştur",
                "org.max_suppliers_per_organization": "Organizasyon Başına Maks. Tedarikçi",
                "parts.max_photos_per_part": "Parça Başına Maks. Fotoğraf",
                "parts.photo_max_size_mb": "Maks. Fotoğraf Boyutu (MB)",
                "parts.supported_photo_formats": "Desteklenen Fotoğraf Formatları",
                "user.password_min_length": "Min. Şifre Uzunluğu",
                "user.session_timeout_minutes": "Oturum Zaman Aşımı (Dakika)",
                "user.max_failed_login_attempts": "Maks. Başarısız Giriş Denemesi",
                "locale.supported_languages": "Desteklenen Diller",
                "locale.supported_countries": "Desteklenen Ülkeler",
                "locale.default_language": "Varsayılan Dil",
                "test.config": "Test Yapılandırması",
                "test_update_value": "Test Güncelleme Değeri"
            },
            "configDescriptions": {
                "org.default_country": "Yeni organizasyonlar için varsayılan ülke",
                "org.auto_create_warehouse": "Yeni organizasyonlar için otomatik varsayılan depo oluştur",
                "org.max_suppliers_per_organization": "Organizasyon başına maksimum tedarikçi sayısı",
                "parts.max_photos_per_part": "Parça başına maksimum fotoğraf sayısı",
                "parts.photo_max_size_mb": "MB cinsinden maksimum fotoğraf boyutu",
                "parts.supported_photo_formats": "Parçalar için desteklenen fotoğraf formatları",
                "user.password_min_length": "Minimum şifre uzunluğu",
                "user.session_timeout_minutes": "Dakika cinsinden oturum zaman aşımı",
                "user.max_failed_login_attempts": "Kilitleme öncesi maksimum başarısız giriş denemesi",
                "locale.supported_languages": "Desteklenen diller",
                "locale.supported_countries": "Desteklenen ülkeler",
                "locale.default_language": "Yeni kullanıcılar için varsayılan dil",
                "test.config": "Test yapılandırması",
                "test_update_value": "Test güncelleme değeri"
            },
            "validationRules": {
                "allowed_values": "İzin Verilen Değerler",
                "min": "Minimum",
                "max": "Maksimum",
                "min_length": "Minimum Uzunluk",
                "max_length": "Maksimum Uzunluk"
            }
        },
        "no": {
            "configKeys": {
                "org.default_country": "Standard Land",
                "org.auto_create_warehouse": "Opprett Lager Automatisk",
                "org.max_suppliers_per_organization": "Maks. Leverandører per Organisasjon",
                "parts.max_photos_per_part": "Maks. Bilder per Del",
                "parts.photo_max_size_mb": "Maks. Bildestørrelse (MB)",
                "parts.supported_photo_formats": "Støttede Bildeformater",
                "user.password_min_length": "Min. Passordlengde",
                "user.session_timeout_minutes": "Økt Tidsavbrudd (Minutter)",
                "user.max_failed_login_attempts": "Maks. Mislykkede Påloggingsforsøk",
                "locale.supported_languages": "Støttede Språk",
                "locale.supported_countries": "Støttede Land",
                "locale.default_language": "Standard Språk",
                "test.config": "Testkonfigurasjon",
                "test_update_value": "Test Oppdateringsverdi"
            },
            "configDescriptions": {
                "org.default_country": "Standard land for nye organisasjoner",
                "org.auto_create_warehouse": "Opprett automatisk standardlager for nye organisasjoner",
                "org.max_suppliers_per_organization": "Maksimalt antall leverandører per organisasjon",
                "parts.max_photos_per_part": "Maksimalt antall bilder per del",
                "parts.photo_max_size_mb": "Maksimal bildestørrelse i MB",
                "parts.supported_photo_formats": "Støttede bildeformater for deler",
                "user.password_min_length": "Minimum passordlengde",
                "user.session_timeout_minutes": "Økt tidsavbrudd i minutter",
                "user.max_failed_login_attempts": "Maksimale mislykkede påloggingsforsøk før låsing",
                "locale.supported_languages": "Støttede språk",
                "locale.supported_countries": "Støttede land",
                "locale.default_language": "Standard språk for nye brukere",
                "test.config": "Testkonfigurasjon",
                "test_update_value": "Test oppdateringsverdi"
            },
            "validationRules": {
                "allowed_values": "Tillatte Verdier",
                "min": "Minimum",
                "max": "Maksimum",
                "min_length": "Minimum Lengde",
                "max_length": "Maksimum Lengde"
            }
        }
    }
    
    # Process each locale file
    locale_dir = "frontend/src/locales"
    for lang_code, translations in config_translations.items():
        file_path = os.path.join(locale_dir, f"{lang_code}.json")
        
        if not os.path.exists(file_path):
            print(f"⚠️  Locale file not found: {file_path}")
            continue
            
        print(f"Adding configuration translations to {file_path}...")
        
        # Load existing translations
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Add configuration translations to the configuration section
        if 'configuration' not in data:
            data['configuration'] = {}
            
        # Add the new translation sections
        data['configuration']['configKeys'] = translations['configKeys']
        data['configuration']['configDescriptions'] = translations['configDescriptions']
        data['configuration']['validationRules'] = translations['validationRules']
        
        # Write back to file
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ Added configuration translations to {lang_code}.json")
    
    print("\n🎉 Configuration item translations added successfully!")
    print("The ConfigurationItem component can now translate configuration keys and descriptions.")

if __name__ == "__main__":
    add_configuration_translations()