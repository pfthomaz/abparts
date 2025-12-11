#!/usr/bin/env python3
"""Add Organization Form translations to all locale files."""

import json

# Translation mappings for all languages
translations = {
    "en": {
        "organizationLogo": "Organization Logo",
        "organizationName": "Organization Name",
        "organizationNamePlaceholder": "Enter organization name",
        "organizationType": "Organization Type",
        "singletonWarning": "⚠️ Only one {{type}} organization is allowed",
        "country": "Country",
        "selectCountry": "Select country...",
        "parentOrganization": "Parent Organization",
        "selectParentOrganization": "Select parent organization...",
        "loadingParentOrganizations": "Loading parent organizations...",
        "addressPlaceholder": "Enter organization address",
        "contactInformation": "Contact Information",
        "contactPlaceholder": "Enter contact information (phone, email, etc.)",
        "organizationIsActive": "Organization is active",
        "updating": "Updating...",
        "creating": "Creating...",
        "updateOrganization": "Update Organization",
        "createOrganization": "Create Organization",
        "validationFailed": "Validation failed. Please check your input.",
        "unexpectedError": "An unexpected error occurred."
    },
    "el": {  # Greek
        "organizationLogo": "Λογότυπο Οργανισμού",
        "organizationName": "Όνομα Οργανισμού",
        "organizationNamePlaceholder": "Εισάγετε όνομα οργανισμού",
        "organizationType": "Τύπος Οργανισμού",
        "singletonWarning": "⚠️ Επιτρέπεται μόνο ένας οργανισμός {{type}}",
        "country": "Χώρα",
        "selectCountry": "Επιλέξτε χώρα...",
        "parentOrganization": "Γονικός Οργανισμός",
        "selectParentOrganization": "Επιλέξτε γονικό οργανισμό...",
        "loadingParentOrganizations": "Φόρτωση γονικών οργανισμών...",
        "addressPlaceholder": "Εισάγετε διεύθυνση οργανισμού",
        "contactInformation": "Στοιχεία Επικοινωνίας",
        "contactPlaceholder": "Εισάγετε στοιχεία επικοινωνίας (τηλέφωνο, email, κλπ.)",
        "organizationIsActive": "Ο οργανισμός είναι ενεργός",
        "updating": "Ενημέρωση...",
        "creating": "Δημιουργία...",
        "updateOrganization": "Ενημέρωση Οργανισμού",
        "createOrganization": "Δημιουργία Οργανισμού",
        "validationFailed": "Η επικύρωση απέτυχε. Ελέγξτε την εισαγωγή σας.",
        "unexpectedError": "Προέκυψε ένα απροσδόκητο σφάλμα."
    },
    "ar": {  # Arabic
        "organizationLogo": "شعار المنظمة",
        "organizationName": "اسم المنظمة",
        "organizationNamePlaceholder": "أدخل اسم المنظمة",
        "organizationType": "نوع المنظمة",
        "singletonWarning": "⚠️ يُسمح بمنظمة {{type}} واحدة فقط",
        "country": "البلد",
        "selectCountry": "اختر البلد...",
        "parentOrganization": "المنظمة الأم",
        "selectParentOrganization": "اختر المنظمة الأم...",
        "loadingParentOrganizations": "جارٍ تحميل المنظمات الأم...",
        "addressPlaceholder": "أدخل عنوان المنظمة",
        "contactInformation": "معلومات الاتصال",
        "contactPlaceholder": "أدخل معلومات الاتصال (الهاتف، البريد الإلكتروني، إلخ.)",
        "organizationIsActive": "المنظمة نشطة",
        "updating": "جارٍ التحديث...",
        "creating": "جارٍ الإنشاء...",
        "updateOrganization": "تحديث المنظمة",
        "createOrganization": "إنشاء منظمة",
        "validationFailed": "فشل التحقق. يرجى التحقق من إدخالك.",
        "unexpectedError": "حدث خطأ غير متوقع."
    },
    "es": {  # Spanish
        "organizationLogo": "Logo de la Organización",
        "organizationName": "Nombre de la Organización",
        "organizationNamePlaceholder": "Ingrese el nombre de la organización",
        "organizationType": "Tipo de Organización",
        "singletonWarning": "⚠️ Solo se permite una organización {{type}}",
        "country": "País",
        "selectCountry": "Seleccionar país...",
        "parentOrganization": "Organización Padre",
        "selectParentOrganization": "Seleccionar organización padre...",
        "loadingParentOrganizations": "Cargando organizaciones padre...",
        "addressPlaceholder": "Ingrese la dirección de la organización",
        "contactInformation": "Información de Contacto",
        "contactPlaceholder": "Ingrese información de contacto (teléfono, correo, etc.)",
        "organizationIsActive": "La organización está activa",
        "updating": "Actualizando...",
        "creating": "Creando...",
        "updateOrganization": "Actualizar Organización",
        "createOrganization": "Crear Organización",
        "validationFailed": "Validación fallida. Por favor revise su entrada.",
        "unexpectedError": "Ocurrió un error inesperado."
    },
    "tr": {  # Turkish
        "organizationLogo": "Organizasyon Logosu",
        "organizationName": "Organizasyon Adı",
        "organizationNamePlaceholder": "Organizasyon adını girin",
        "organizationType": "Organizasyon Türü",
        "singletonWarning": "⚠️ Yalnızca bir {{type}} organizasyonuna izin verilir",
        "country": "Ülke",
        "selectCountry": "Ülke seçin...",
        "parentOrganization": "Üst Organizasyon",
        "selectParentOrganization": "Üst organizasyon seçin...",
        "loadingParentOrganizations": "Üst organizasyonlar yükleniyor...",
        "addressPlaceholder": "Organizasyon adresini girin",
        "contactInformation": "İletişim Bilgileri",
        "contactPlaceholder": "İletişim bilgilerini girin (telefon, e-posta, vb.)",
        "organizationIsActive": "Organizasyon aktif",
        "updating": "Güncelleniyor...",
        "creating": "Oluşturuluyor...",
        "updateOrganization": "Organizasyonu Güncelle",
        "createOrganization": "Organizasyon Oluştur",
        "validationFailed": "Doğrulama başarısız. Lütfen girişinizi kontrol edin.",
        "unexpectedError": "Beklenmeyen bir hata oluştu."
    },
    "no": {  # Norwegian
        "organizationLogo": "Organisasjonslogo",
        "organizationName": "Organisasjonsnavn",
        "organizationNamePlaceholder": "Skriv inn organisasjonsnavn",
        "organizationType": "Organisasjonstype",
        "singletonWarning": "⚠️ Bare én {{type}} organisasjon er tillatt",
        "country": "Land",
        "selectCountry": "Velg land...",
        "parentOrganization": "Overordnet Organisasjon",
        "selectParentOrganization": "Velg overordnet organisasjon...",
        "loadingParentOrganizations": "Laster overordnede organisasjoner...",
        "addressPlaceholder": "Skriv inn organisasjonsadresse",
        "contactInformation": "Kontaktinformasjon",
        "contactPlaceholder": "Skriv inn kontaktinformasjon (telefon, e-post, osv.)",
        "organizationIsActive": "Organisasjonen er aktiv",
        "updating": "Oppdaterer...",
        "creating": "Oppretter...",
        "updateOrganization": "Oppdater Organisasjon",
        "createOrganization": "Opprett Organisasjon",
        "validationFailed": "Validering mislyktes. Vennligst sjekk inndataene dine.",
        "unexpectedError": "En uventet feil oppstod."
    }
}

def add_translations_to_file(lang_code, translations_dict):
    """Add translations to a specific language file."""
    file_path = f"frontend/src/locales/{lang_code}.json"
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Add organizationForm section
        data["organizationForm"] = translations_dict
        
        # Write back
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ Updated {lang_code}.json with {len(translations_dict)} keys")
        
    except Exception as e:
        print(f"❌ Error updating {lang_code}.json: {e}")

# Process all languages
for lang_code, trans in translations.items():
    add_translations_to_file(lang_code, trans)

print("\n✅ All Organization Form translations added successfully!")
print(f"📊 Total keys per language: {len(translations['en'])}")
