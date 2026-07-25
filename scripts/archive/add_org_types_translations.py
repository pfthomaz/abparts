#!/usr/bin/env python3
"""Add Organization Types translations to all locale files."""

import json

# Translation mappings for all languages
translations = {
    "en": {
        "oraseaseLabel": "Oraseas EE",
        "oraseaseDesc": "App owner and primary distributor",
        "bossaquaLabel": "BossAqua",
        "bossaquaDesc": "Manufacturer of AutoBoss machines",
        "customerLabel": "Customer",
        "customerDesc": "Organizations that purchase machines",
        "supplierLabel": "Supplier",
        "supplierDesc": "Third-party parts suppliers"
    },
    "el": {  # Greek
        "oraseaseLabel": "Oraseas EE",
        "oraseaseDesc": "Κάτοχος εφαρμογής και κύριος διανομέας",
        "bossaquaLabel": "BossAqua",
        "bossaquaDesc": "Κατασκευαστής μηχανημάτων AutoBoss",
        "customerLabel": "Πελάτης",
        "customerDesc": "Οργανισμοί που αγοράζουν μηχανήματα",
        "supplierLabel": "Προμηθευτής",
        "supplierDesc": "Προμηθευτές ανταλλακτικών τρίτων"
    },
    "ar": {  # Arabic
        "oraseaseLabel": "Oraseas EE",
        "oraseaseDesc": "مالك التطبيق والموزع الرئيسي",
        "bossaquaLabel": "BossAqua",
        "bossaquaDesc": "مصنع آلات AutoBoss",
        "customerLabel": "عميل",
        "customerDesc": "المنظمات التي تشتري الآلات",
        "supplierLabel": "مورد",
        "supplierDesc": "موردو قطع الغيار من طرف ثالث"
    },
    "es": {  # Spanish
        "oraseaseLabel": "Oraseas EE",
        "oraseaseDesc": "Propietario de la aplicación y distribuidor principal",
        "bossaquaLabel": "BossAqua",
        "bossaquaDesc": "Fabricante de máquinas AutoBoss",
        "customerLabel": "Cliente",
        "customerDesc": "Organizaciones que compran máquinas",
        "supplierLabel": "Proveedor",
        "supplierDesc": "Proveedores de piezas de terceros"
    },
    "tr": {  # Turkish
        "oraseaseLabel": "Oraseas EE",
        "oraseaseDesc": "Uygulama sahibi ve ana distribütör",
        "bossaquaLabel": "BossAqua",
        "bossaquaDesc": "AutoBoss makinelerinin üreticisi",
        "customerLabel": "Müşteri",
        "customerDesc": "Makine satın alan organizasyonlar",
        "supplierLabel": "Tedarikçi",
        "supplierDesc": "Üçüncü taraf parça tedarikçileri"
    },
    "no": {  # Norwegian
        "oraseaseLabel": "Oraseas EE",
        "oraseaseDesc": "Appeier og hoveddistributør",
        "bossaquaLabel": "BossAqua",
        "bossaquaDesc": "Produsent av AutoBoss-maskiner",
        "customerLabel": "Kunde",
        "customerDesc": "Organisasjoner som kjøper maskiner",
        "supplierLabel": "Leverandør",
        "supplierDesc": "Tredjepartsleverandører av deler"
    }
}

def add_translations_to_file(lang_code, translations_dict):
    """Add translations to a specific language file."""
    file_path = f"frontend/src/locales/{lang_code}.json"
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Add organizationTypes section
        data["organizationTypes"] = translations_dict
        
        # Write back
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ Updated {lang_code}.json with {len(translations_dict)} keys")
        
    except Exception as e:
        print(f"❌ Error updating {lang_code}.json: {e}")

# Process all languages
for lang_code, trans in translations.items():
    add_translations_to_file(lang_code, trans)

print("\n✅ All Organization Types translations added successfully!")
print(f"📊 Total keys per language: {len(translations['en'])}")
