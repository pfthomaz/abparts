#!/usr/bin/env python3
"""Add Organizations page translations to all locale files."""

import json

# Translation mappings for all languages
translations = {
    "en": {
        "title": "Organizations",
        "subtitle": "Manage organization hierarchy and relationships",
        "cards": "Cards",
        "hierarchy": "Hierarchy",
        "addOrganization": "Add Organization",
        "loadingOrganizations": "Loading organizations...",
        "searchByName": "Search by Name",
        "searchPlaceholder": "Search organizations...",
        "filterByType": "Filter by Type",
        "allTypes": "All Types",
        "noOrganizationsFound": "No Organizations Found",
        "adjustSearchCriteria": "Try adjusting your search or filter criteria.",
        "noOrganizationsYet": "There are no organizations in the system yet.",
        "parent": "Parent",
        "address": "Address",
        "contact": "Contact",
        "warehouses": "Warehouses",
        "loadingHierarchy": "Loading hierarchy...",
        "noHierarchyData": "No Hierarchy Data",
        "unableToLoadHierarchy": "Unable to load organization hierarchy.",
        "editOrganization": "Edit Organization",
        "addNewOrganization": "Add New Organization",
        "deleteConfirm": "Are you sure you want to delete this organization? This action cannot be undone.",
        "failedToFetch": "Failed to fetch organizations.",
        "failedToDelete": "Failed to delete organization.",
        "noLogo": "No Logo"
    },
    "el": {  # Greek
        "title": "Οργανισμοί",
        "subtitle": "Διαχείριση ιεραρχίας και σχέσεων οργανισμών",
        "cards": "Κάρτες",
        "hierarchy": "Ιεραρχία",
        "addOrganization": "Προσθήκη Οργανισμού",
        "loadingOrganizations": "Φόρτωση οργανισμών...",
        "searchByName": "Αναζήτηση με Όνομα",
        "searchPlaceholder": "Αναζήτηση οργανισμών...",
        "filterByType": "Φιλτράρισμα με Τύπο",
        "allTypes": "Όλοι οι Τύποι",
        "noOrganizationsFound": "Δεν Βρέθηκαν Οργανισμοί",
        "adjustSearchCriteria": "Δοκιμάστε να προσαρμόσετε τα κριτήρια αναζήτησης ή φιλτραρίσματος.",
        "noOrganizationsYet": "Δεν υπάρχουν ακόμα οργανισμοί στο σύστημα.",
        "parent": "Γονικός",
        "address": "Διεύθυνση",
        "contact": "Επικοινωνία",
        "warehouses": "Αποθήκες",
        "loadingHierarchy": "Φόρτωση ιεραρχίας...",
        "noHierarchyData": "Δεν Υπάρχουν Δεδομένα Ιεραρχίας",
        "unableToLoadHierarchy": "Αδυναμία φόρτωσης ιεραρχίας οργανισμών.",
        "editOrganization": "Επεξεργασία Οργανισμού",
        "addNewOrganization": "Προσθήκη Νέου Οργανισμού",
        "deleteConfirm": "Είστε σίγουροι ότι θέλετε να διαγράψετε αυτόν τον οργανισμό; Αυτή η ενέργεια δεν μπορεί να αναιρεθεί.",
        "failedToFetch": "Αποτυχία φόρτωσης οργανισμών.",
        "failedToDelete": "Αποτυχία διαγραφής οργανισμού.",
        "noLogo": "Χωρίς Λογότυπο"
    },
    "ar": {  # Arabic
        "title": "المنظمات",
        "subtitle": "إدارة التسلسل الهرمي والعلاقات بين المنظمات",
        "cards": "البطاقات",
        "hierarchy": "التسلسل الهرمي",
        "addOrganization": "إضافة منظمة",
        "loadingOrganizations": "جارٍ تحميل المنظمات...",
        "searchByName": "البحث بالاسم",
        "searchPlaceholder": "البحث عن المنظمات...",
        "filterByType": "التصفية حسب النوع",
        "allTypes": "جميع الأنواع",
        "noOrganizationsFound": "لم يتم العثور على منظمات",
        "adjustSearchCriteria": "حاول تعديل معايير البحث أو التصفية.",
        "noOrganizationsYet": "لا توجد منظمات في النظام بعد.",
        "parent": "الأصل",
        "address": "العنوان",
        "contact": "جهة الاتصال",
        "warehouses": "المستودعات",
        "loadingHierarchy": "جارٍ تحميل التسلسل الهرمي...",
        "noHierarchyData": "لا توجد بيانات تسلسل هرمي",
        "unableToLoadHierarchy": "تعذر تحميل التسلسل الهرمي للمنظمات.",
        "editOrganization": "تعديل المنظمة",
        "addNewOrganization": "إضافة منظمة جديدة",
        "deleteConfirm": "هل أنت متأكد من رغبتك في حذف هذه المنظمة؟ لا يمكن التراجع عن هذا الإجراء.",
        "failedToFetch": "فشل تحميل المنظمات.",
        "failedToDelete": "فشل حذف المنظمة.",
        "noLogo": "لا يوجد شعار"
    },
    "es": {  # Spanish
        "title": "Organizaciones",
        "subtitle": "Gestionar jerarquía y relaciones de organizaciones",
        "cards": "Tarjetas",
        "hierarchy": "Jerarquía",
        "addOrganization": "Agregar Organización",
        "loadingOrganizations": "Cargando organizaciones...",
        "searchByName": "Buscar por Nombre",
        "searchPlaceholder": "Buscar organizaciones...",
        "filterByType": "Filtrar por Tipo",
        "allTypes": "Todos los Tipos",
        "noOrganizationsFound": "No se Encontraron Organizaciones",
        "adjustSearchCriteria": "Intenta ajustar tus criterios de búsqueda o filtro.",
        "noOrganizationsYet": "Aún no hay organizaciones en el sistema.",
        "parent": "Padre",
        "address": "Dirección",
        "contact": "Contacto",
        "warehouses": "Almacenes",
        "loadingHierarchy": "Cargando jerarquía...",
        "noHierarchyData": "Sin Datos de Jerarquía",
        "unableToLoadHierarchy": "No se pudo cargar la jerarquía de organizaciones.",
        "editOrganization": "Editar Organización",
        "addNewOrganization": "Agregar Nueva Organización",
        "deleteConfirm": "¿Estás seguro de que quieres eliminar esta organización? Esta acción no se puede deshacer.",
        "failedToFetch": "Error al cargar organizaciones.",
        "failedToDelete": "Error al eliminar organización.",
        "noLogo": "Sin Logo"
    },
    "tr": {  # Turkish
        "title": "Organizasyonlar",
        "subtitle": "Organizasyon hiyerarşisini ve ilişkilerini yönetin",
        "cards": "Kartlar",
        "hierarchy": "Hiyerarşi",
        "addOrganization": "Organizasyon Ekle",
        "loadingOrganizations": "Organizasyonlar yükleniyor...",
        "searchByName": "İsme Göre Ara",
        "searchPlaceholder": "Organizasyonları ara...",
        "filterByType": "Türe Göre Filtrele",
        "allTypes": "Tüm Türler",
        "noOrganizationsFound": "Organizasyon Bulunamadı",
        "adjustSearchCriteria": "Arama veya filtre kriterlerinizi ayarlamayı deneyin.",
        "noOrganizationsYet": "Sistemde henüz organizasyon yok.",
        "parent": "Üst",
        "address": "Adres",
        "contact": "İletişim",
        "warehouses": "Depolar",
        "loadingHierarchy": "Hiyerarşi yükleniyor...",
        "noHierarchyData": "Hiyerarşi Verisi Yok",
        "unableToLoadHierarchy": "Organizasyon hiyerarşisi yüklenemedi.",
        "editOrganization": "Organizasyonu Düzenle",
        "addNewOrganization": "Yeni Organizasyon Ekle",
        "deleteConfirm": "Bu organizasyonu silmek istediğinizden emin misiniz? Bu işlem geri alınamaz.",
        "failedToFetch": "Organizasyonlar yüklenemedi.",
        "failedToDelete": "Organizasyon silinemedi.",
        "noLogo": "Logo Yok"
    },
    "no": {  # Norwegian
        "title": "Organisasjoner",
        "subtitle": "Administrer organisasjonshierarki og relasjoner",
        "cards": "Kort",
        "hierarchy": "Hierarki",
        "addOrganization": "Legg til Organisasjon",
        "loadingOrganizations": "Laster organisasjoner...",
        "searchByName": "Søk etter Navn",
        "searchPlaceholder": "Søk organisasjoner...",
        "filterByType": "Filtrer etter Type",
        "allTypes": "Alle Typer",
        "noOrganizationsFound": "Ingen Organisasjoner Funnet",
        "adjustSearchCriteria": "Prøv å justere søke- eller filterkriteriene.",
        "noOrganizationsYet": "Det er ingen organisasjoner i systemet ennå.",
        "parent": "Overordnet",
        "address": "Adresse",
        "contact": "Kontakt",
        "warehouses": "Lagre",
        "loadingHierarchy": "Laster hierarki...",
        "noHierarchyData": "Ingen Hierarkidata",
        "unableToLoadHierarchy": "Kunne ikke laste organisasjonshierarki.",
        "editOrganization": "Rediger Organisasjon",
        "addNewOrganization": "Legg til Ny Organisasjon",
        "deleteConfirm": "Er du sikker på at du vil slette denne organisasjonen? Denne handlingen kan ikke angres.",
        "failedToFetch": "Kunne ikke laste organisasjoner.",
        "failedToDelete": "Kunne ikke slette organisasjon.",
        "noLogo": "Ingen Logo"
    }
}

def add_translations_to_file(lang_code, translations_dict):
    """Add translations to a specific language file."""
    file_path = f"frontend/src/locales/{lang_code}.json"
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Add organizations section
        data["organizations"] = translations_dict
        
        # Write back
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ Updated {lang_code}.json with {len(translations_dict)} keys")
        
    except Exception as e:
        print(f"❌ Error updating {lang_code}.json: {e}")

# Process all languages
for lang_code, trans in translations.items():
    add_translations_to_file(lang_code, trans)

print("\n✅ All Organizations page translations added successfully!")
print(f"📊 Total keys per language: {len(translations['en'])}")
