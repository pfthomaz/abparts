#!/usr/bin/env python3
"""
Add Dashboard and Net Cleaning enhancements translations for all 6 supported languages.
"""

import json
import os

# Define translations for all 6 languages
TRANSLATIONS = {
    "en": {
        "dashboard": {
            "recordNetCleaning": "Record Net Cleaning",
            "recordNetCleaningDesc": "Log a new net cleaning operation",
            "farms": "Farms",
            "farmsSubtitle": "Aquaculture farm sites",
            "cages": "Cages",
            "cagesSubtitle": "Nets and cages in operation"
        },
        "netCleaning": {
            "farmSites": {
                "addCage": "Add Cage"
            },
            "nets": {
                "selectMaterial": "Select material",
                "materials": {
                    "polyester": "Polyester",
                    "polypropylene": "Polypropylene",
                    "polyethylene": "Polyethylene",
                    "galvanizedSteel": "Galvanized steel",
                    "spectra": "Spectra",
                    "copper": "Copper",
                    "thornD": "Thorn d",
                    "dyneema": "Dyneema",
                    "other": "Other"
                }
            },
            "records": {
                "selectOperator": "Select operator"
            }
        }
    },
    "el": {
        "dashboard": {
            "recordNetCleaning": "Καταγραφή Καθαρισμού Διχτυού",
            "recordNetCleaningDesc": "Καταγράψτε μια νέα λειτουργία καθαρισμού διχτυού",
            "farms": "Μονάδες",
            "farmsSubtitle": "Μονάδες υδατοκαλλιέργειας",
            "cages": "Κλωβοί",
            "cagesSubtitle": "Δίχτυα και κλωβοί σε λειτουργία"
        },
        "netCleaning": {
            "farmSites": {
                "addCage": "Προσθήκη Κλωβού"
            },
            "nets": {
                "selectMaterial": "Επιλέξτε υλικό",
                "materials": {
                    "polyester": "Πολυεστέρας",
                    "polypropylene": "Πολυπροπυλένιο",
                    "polyethylene": "Πολυαιθυλένιο",
                    "galvanizedSteel": "Γαλβανισμένος χάλυβας",
                    "spectra": "Spectra",
                    "copper": "Χαλκός",
                    "thornD": "Thorn d",
                    "dyneema": "Dyneema",
                    "other": "Άλλο"
                }
            },
            "records": {
                "selectOperator": "Επιλέξτε χειριστή"
            }
        }
    },
    "ar": {
        "dashboard": {
            "recordNetCleaning": "تسجيل تنظيف الشبكة",
            "recordNetCleaningDesc": "تسجيل عملية تنظيف شبكة جديدة",
            "farms": "المزارع",
            "farmsSubtitle": "مواقع مزارع الاستزراع المائي",
            "cages": "الأقفاص",
            "cagesSubtitle": "الشباك والأقفاص قيد التشغيل"
        },
        "netCleaning": {
            "farmSites": {
                "addCage": "إضافة قفص"
            },
            "nets": {
                "selectMaterial": "اختر المادة",
                "materials": {
                    "polyester": "بوليستر",
                    "polypropylene": "بولي بروبيلين",
                    "polyethylene": "بولي إيثيلين",
                    "galvanizedSteel": "فولاذ مجلفن",
                    "spectra": "سبكترا",
                    "copper": "نحاس",
                    "thornD": "ثورن دي",
                    "dyneema": "داينيما",
                    "other": "أخرى"
                }
            },
            "records": {
                "selectOperator": "اختر المشغل"
            }
        }
    },
    "es": {
        "dashboard": {
            "recordNetCleaning": "Registrar Limpieza de Red",
            "recordNetCleaningDesc": "Registrar una nueva operación de limpieza de red",
            "farms": "Granjas",
            "farmsSubtitle": "Sitios de granjas acuícolas",
            "cages": "Jaulas",
            "cagesSubtitle": "Redes y jaulas en operación"
        },
        "netCleaning": {
            "farmSites": {
                "addCage": "Agregar Jaula"
            },
            "nets": {
                "selectMaterial": "Seleccionar material",
                "materials": {
                    "polyester": "Poliéster",
                    "polypropylene": "Polipropileno",
                    "polyethylene": "Polietileno",
                    "galvanizedSteel": "Acero galvanizado",
                    "spectra": "Spectra",
                    "copper": "Cobre",
                    "thornD": "Thorn d",
                    "dyneema": "Dyneema",
                    "other": "Otro"
                }
            },
            "records": {
                "selectOperator": "Seleccionar operador"
            }
        }
    },
    "no": {
        "dashboard": {
            "recordNetCleaning": "Registrer Notrengjøring",
            "recordNetCleaningDesc": "Logg en ny notrengjøringsoperasjon",
            "farms": "Anlegg",
            "farmsSubtitle": "Oppdrettsanlegg",
            "cages": "Merder",
            "cagesSubtitle": "Nøter og merder i drift"
        },
        "netCleaning": {
            "farmSites": {
                "addCage": "Legg til Merd"
            },
            "nets": {
                "selectMaterial": "Velg materiale",
                "materials": {
                    "polyester": "Polyester",
                    "polypropylene": "Polypropylen",
                    "polyethylene": "Polyetylen",
                    "galvanizedSteel": "Galvanisert stål",
                    "spectra": "Spectra",
                    "copper": "Kobber",
                    "thornD": "Thorn d",
                    "dyneema": "Dyneema",
                    "other": "Annet"
                }
            },
            "records": {
                "selectOperator": "Velg operatør"
            }
        }
    },
    "tr": {
        "dashboard": {
            "recordNetCleaning": "Ağ Temizliği Kaydet",
            "recordNetCleaningDesc": "Yeni bir ağ temizleme işlemi kaydet",
            "farms": "Çiftlikler",
            "farmsSubtitle": "Su ürünleri çiftlik sahaları",
            "cages": "Kafesler",
            "cagesSubtitle": "Çalışan ağlar ve kafesler"
        },
        "netCleaning": {
            "farmSites": {
                "addCage": "Kafes Ekle"
            },
            "nets": {
                "selectMaterial": "Malzeme seç",
                "materials": {
                    "polyester": "Polyester",
                    "polypropylene": "Polipropilen",
                    "polyethylene": "Polietilen",
                    "galvanizedSteel": "Galvanizli çelik",
                    "spectra": "Spectra",
                    "copper": "Bakır",
                    "thornD": "Thorn d",
                    "dyneema": "Dyneema",
                    "other": "Diğer"
                }
            },
            "records": {
                "selectOperator": "Operatör seç"
            }
        }
    }
}

def add_translations():
    """Add dashboard and net cleaning enhancement translations to all language files."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    locales_dir = os.path.join(script_dir, 'frontend', 'src', 'locales')
    
    if not os.path.exists(locales_dir):
        print(f"Error: Locales directory not found at {locales_dir}")
        return False
    
    success_count = 0
    for lang_code, translations in TRANSLATIONS.items():
        file_path = os.path.join(locales_dir, f'{lang_code}.json')
        
        try:
            # Read existing translations
            with open(file_path, 'r', encoding='utf-8') as f:
                existing = json.load(f)
            
            # Update dashboard translations
            if 'dashboard' not in existing:
                existing['dashboard'] = {}
            existing['dashboard'].update(translations['dashboard'])
            
            # Update netCleaning translations (deep merge)
            if 'netCleaning' not in existing:
                existing['netCleaning'] = {}
            
            for section, content in translations['netCleaning'].items():
                if section not in existing['netCleaning']:
                    existing['netCleaning'][section] = {}
                existing['netCleaning'][section].update(content)
            
            # Write back with proper formatting
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(existing, f, ensure_ascii=False, indent=2)
            
            print(f"✓ Added dashboard and net cleaning translations to {lang_code}.json")
            success_count += 1
            
        except FileNotFoundError:
            print(f"✗ File not found: {file_path}")
        except json.JSONDecodeError as e:
            print(f"✗ JSON decode error in {file_path}: {e}")
        except Exception as e:
            print(f"✗ Error processing {file_path}: {e}")
    
    print(f"\nCompleted: {success_count}/{len(TRANSLATIONS)} language files updated")
    return success_count == len(TRANSLATIONS)

if __name__ == '__main__':
    print("Adding Dashboard and Net Cleaning Enhancement translations...")
    print("=" * 60)
    success = add_translations()
    print("=" * 60)
    if success:
        print("✓ All translations added successfully!")
    else:
        print("✗ Some translations failed. Please check the errors above.")
    exit(0 if success else 1)
