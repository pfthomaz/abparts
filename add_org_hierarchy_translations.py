#!/usr/bin/env python3
"""Add Organization Hierarchy component translations to all locale files."""

import json

# Translation mappings for all languages
translations = {
    "en": {
        "title": "Organization Hierarchy",
        "subtitle": "Visual representation of organization structure",
        "refresh": "Refresh",
        "includeInactive": "Include inactive organizations",
        "expandAll": "Expand All",
        "collapseAll": "Collapse All",
        "inactive": "Inactive",
        "child": "child",
        "children": "children",
        "noOrganizations": "No organizations found. Create your first organization to get started.",
        "organizationTypes": "Organization Types",
        "failedToLoad": "Failed to load organization hierarchy. Please try again."
    },
    "el": {  # Greek
        "title": "Ιεραρχία Οργανισμών",
        "subtitle": "Οπτική αναπαράσταση της δομής του οργανισμού",
        "refresh": "Ανανέωση",
        "includeInactive": "Συμπερίληψη ανενεργών οργανισμών",
        "expandAll": "Ανάπτυξη Όλων",
        "collapseAll": "Σύμπτυξη Όλων",
        "inactive": "Ανενεργός",
        "child": "παιδί",
        "children": "παιδιά",
        "noOrganizations": "Δεν βρέθηκαν οργανισμοί. Δημιουργήστε τον πρώτο σας οργανισμό για να ξεκινήσετε.",
        "organizationTypes": "Τύποι Οργανισμών",
        "failedToLoad": "Αποτυχία φόρτωσης ιεραρχίας οργανισμών. Παρακαλώ δοκιμάστε ξανά."
    },
    "ar": {  # Arabic
        "title": "التسلسل الهرمي للمنظمات",
        "subtitle": "تمثيل مرئي لهيكل المنظمة",
        "refresh": "تحديث",
        "includeInactive": "تضمين المنظمات غير النشطة",
        "expandAll": "توسيع الكل",
        "collapseAll": "طي الكل",
        "inactive": "غير نشط",
        "child": "فرع",
        "children": "فروع",
        "noOrganizations": "لم يتم العثور على منظمات. أنشئ منظمتك الأولى للبدء.",
        "organizationTypes": "أنواع المنظمات",
        "failedToLoad": "فشل تحميل التسلسل الهرمي للمنظمات. يرجى المحاولة مرة أخرى."
    },
    "es": {  # Spanish
        "title": "Jerarquía de Organizaciones",
        "subtitle": "Representación visual de la estructura organizacional",
        "refresh": "Actualizar",
        "includeInactive": "Incluir organizaciones inactivas",
        "expandAll": "Expandir Todo",
        "collapseAll": "Contraer Todo",
        "inactive": "Inactivo",
        "child": "hijo",
        "children": "hijos",
        "noOrganizations": "No se encontraron organizaciones. Crea tu primera organización para comenzar.",
        "organizationTypes": "Tipos de Organizaciones",
        "failedToLoad": "Error al cargar la jerarquía de organizaciones. Por favor, inténtalo de nuevo."
    },
    "tr": {  # Turkish
        "title": "Organizasyon Hiyerarşisi",
        "subtitle": "Organizasyon yapısının görsel temsili",
        "refresh": "Yenile",
        "includeInactive": "Pasif organizasyonları dahil et",
        "expandAll": "Tümünü Genişlet",
        "collapseAll": "Tümünü Daralt",
        "inactive": "Pasif",
        "child": "alt",
        "children": "alt",
        "noOrganizations": "Organizasyon bulunamadı. Başlamak için ilk organizasyonunuzu oluşturun.",
        "organizationTypes": "Organizasyon Türleri",
        "failedToLoad": "Organizasyon hiyerarşisi yüklenemedi. Lütfen tekrar deneyin."
    },
    "no": {  # Norwegian
        "title": "Organisasjonshierarki",
        "subtitle": "Visuell representasjon av organisasjonsstruktur",
        "refresh": "Oppdater",
        "includeInactive": "Inkluder inaktive organisasjoner",
        "expandAll": "Utvid Alle",
        "collapseAll": "Skjul Alle",
        "inactive": "Inaktiv",
        "child": "barn",
        "children": "barn",
        "noOrganizations": "Ingen organisasjoner funnet. Opprett din første organisasjon for å komme i gang.",
        "organizationTypes": "Organisasjonstyper",
        "failedToLoad": "Kunne ikke laste organisasjonshierarki. Vennligst prøv igjen."
    }
}

def add_translations_to_file(lang_code, translations_dict):
    """Add translations to a specific language file."""
    file_path = f"frontend/src/locales/{lang_code}.json"
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Add organizationHierarchy section
        data["organizationHierarchy"] = translations_dict
        
        # Write back
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ Updated {lang_code}.json with {len(translations_dict)} keys")
        
    except Exception as e:
        print(f"❌ Error updating {lang_code}.json: {e}")

# Process all languages
for lang_code, trans in translations.items():
    add_translations_to_file(lang_code, trans)

print("\n✅ All Organization Hierarchy translations added successfully!")
print(f"📊 Total keys per language: {len(translations['en'])}")
