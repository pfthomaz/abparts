#!/usr/bin/env python3
"""Add Organization Management page translations to all locale files."""

import json

# Translation mappings for all languages
translations = {
    "en": {
        "title": "Organization Management",
        "subtitle": "Manage organizations, suppliers, and warehouses with enhanced UI components",
        "selected": "Selected",
        "organizationHierarchy": "Organization Hierarchy",
        "supplierManagement": "Supplier Management",
        "warehouseManagement": "Warehouse Management",
        "noOrganizationSelected": "No organization selected",
        "selectOrgForSuppliers": "Select an organization from the hierarchy to manage its suppliers.",
        "selectOrgForWarehouses": "Select an organization from the hierarchy to manage its warehouses.",
        "limitedAccess": "Limited Access",
        "limitedAccessMessage": "Some organization management features may be limited based on your role. Contact your administrator for additional permissions."
    },
    "el": {  # Greek
        "title": "Διαχείριση Οργανισμών",
        "subtitle": "Διαχειριστείτε οργανισμούς, προμηθευτές και αποθήκες με βελτιωμένα στοιχεία UI",
        "selected": "Επιλεγμένο",
        "organizationHierarchy": "Ιεραρχία Οργανισμών",
        "supplierManagement": "Διαχείριση Προμηθευτών",
        "warehouseManagement": "Διαχείριση Αποθηκών",
        "noOrganizationSelected": "Δεν έχει επιλεγεί οργανισμός",
        "selectOrgForSuppliers": "Επιλέξτε έναν οργανισμό από την ιεραρχία για να διαχειριστείτε τους προμηθευτές του.",
        "selectOrgForWarehouses": "Επιλέξτε έναν οργανισμό από την ιεραρχία για να διαχειριστείτε τις αποθήκες του.",
        "limitedAccess": "Περιορισμένη Πρόσβαση",
        "limitedAccessMessage": "Ορισμένες λειτουργίες διαχείρισης οργανισμών ενδέχεται να είναι περιορισμένες με βάση τον ρόλο σας. Επικοινωνήστε με τον διαχειριστή σας για πρόσθετα δικαιώματα."
    },
    "ar": {  # Arabic
        "title": "إدارة المنظمات",
        "subtitle": "إدارة المنظمات والموردين والمستودعات باستخدام مكونات واجهة مستخدم محسّنة",
        "selected": "المحدد",
        "organizationHierarchy": "التسلسل الهرمي للمنظمات",
        "supplierManagement": "إدارة الموردين",
        "warehouseManagement": "إدارة المستودعات",
        "noOrganizationSelected": "لم يتم تحديد منظمة",
        "selectOrgForSuppliers": "حدد منظمة من التسلسل الهرمي لإدارة مورديها.",
        "selectOrgForWarehouses": "حدد منظمة من التسلسل الهرمي لإدارة مستودعاتها.",
        "limitedAccess": "وصول محدود",
        "limitedAccessMessage": "قد تكون بعض ميزات إدارة المنظمات محدودة بناءً على دورك. اتصل بالمسؤول للحصول على أذونات إضافية."
    },
    "es": {  # Spanish
        "title": "Gestión de Organizaciones",
        "subtitle": "Gestione organizaciones, proveedores y almacenes con componentes de interfaz mejorados",
        "selected": "Seleccionado",
        "organizationHierarchy": "Jerarquía de Organizaciones",
        "supplierManagement": "Gestión de Proveedores",
        "warehouseManagement": "Gestión de Almacenes",
        "noOrganizationSelected": "No hay organización seleccionada",
        "selectOrgForSuppliers": "Seleccione una organización de la jerarquía para gestionar sus proveedores.",
        "selectOrgForWarehouses": "Seleccione una organización de la jerarquía para gestionar sus almacenes.",
        "limitedAccess": "Acceso Limitado",
        "limitedAccessMessage": "Algunas funciones de gestión de organizaciones pueden estar limitadas según su rol. Contacte a su administrador para obtener permisos adicionales."
    },
    "tr": {  # Turkish
        "title": "Organizasyon Yönetimi",
        "subtitle": "Gelişmiş UI bileşenleriyle organizasyonları, tedarikçileri ve depoları yönetin",
        "selected": "Seçili",
        "organizationHierarchy": "Organizasyon Hiyerarşisi",
        "supplierManagement": "Tedarikçi Yönetimi",
        "warehouseManagement": "Depo Yönetimi",
        "noOrganizationSelected": "Organizasyon seçilmedi",
        "selectOrgForSuppliers": "Tedarikçilerini yönetmek için hiyerarşiden bir organizasyon seçin.",
        "selectOrgForWarehouses": "Depolarını yönetmek için hiyerarşiden bir organizasyon seçin.",
        "limitedAccess": "Sınırlı Erişim",
        "limitedAccessMessage": "Bazı organizasyon yönetimi özellikleri rolünüze göre sınırlı olabilir. Ek izinler için yöneticinizle iletişime geçin."
    },
    "no": {  # Norwegian
        "title": "Organisasjonsstyring",
        "subtitle": "Administrer organisasjoner, leverandører og lagre med forbedrede UI-komponenter",
        "selected": "Valgt",
        "organizationHierarchy": "Organisasjonshierarki",
        "supplierManagement": "Leverandørstyring",
        "warehouseManagement": "Lagerstyring",
        "noOrganizationSelected": "Ingen organisasjon valgt",
        "selectOrgForSuppliers": "Velg en organisasjon fra hierarkiet for å administrere leverandørene.",
        "selectOrgForWarehouses": "Velg en organisasjon fra hierarkiet for å administrere lagrene.",
        "limitedAccess": "Begrenset Tilgang",
        "limitedAccessMessage": "Noen organisasjonsstyringsfunksjoner kan være begrenset basert på din rolle. Kontakt administratoren for ytterligere tillatelser."
    }
}

def add_translations_to_file(lang_code, translations_dict):
    """Add translations to a specific language file."""
    file_path = f"frontend/src/locales/{lang_code}.json"
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Add organizationManagement section
        data["organizationManagement"] = translations_dict
        
        # Write back
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ Updated {lang_code}.json with {len(translations_dict)} keys")
        
    except Exception as e:
        print(f"❌ Error updating {lang_code}.json: {e}")

# Process all languages
for lang_code, trans in translations.items():
    add_translations_to_file(lang_code, trans)

print("\n✅ All Organization Management page translations added successfully!")
print(f"📊 Total keys per language: {len(translations['en'])}")
