#!/usr/bin/env python3

import json
import os

def add_organization_scope_translations():
    """Add organization scope indicator translations to all locale files"""
    
    # Organization scope translations
    scope_translations = {
        "en": {
            "organizationScope": {
                "globalAccess": "Global Access",
                "organizationAccess": "Organization Access",
                "viewing": "Viewing",
                "allOrganizations": "All Organizations",
                "limitedTo": "Limited to",
                "yourOrganization": "Your Organization",
                "switchOrganization": "Switch Organization",
                "switch": "Switch",
                "dataAccess": "Data Access",
                "unrestricted": "Unrestricted",
                "organizationScoped": "Organization-scoped",
                "userManagement": "User Management",
                "ownOrganization": "Own Organization",
                "reporting": "Reporting",
                "globalReports": "Global Reports",
                "organizationReports": "Organization Reports",
                "accessLevels": {
                    "global": "global",
                    "organization": "organization"
                }
            }
        },
        "el": {
            "organizationScope": {
                "globalAccess": "Καθολική Πρόσβαση",
                "organizationAccess": "Πρόσβαση Οργανισμού",
                "viewing": "Προβολή",
                "allOrganizations": "Όλοι οι Οργανισμοί",
                "limitedTo": "Περιορισμένο σε",
                "yourOrganization": "Ο Οργανισμός σας",
                "switchOrganization": "Αλλαγή Οργανισμού",
                "switch": "Αλλαγή",
                "dataAccess": "Πρόσβαση Δεδομένων",
                "unrestricted": "Απεριόριστη",
                "organizationScoped": "Περιορισμένη σε Οργανισμό",
                "userManagement": "Διαχείριση Χρηστών",
                "ownOrganization": "Δικός Οργανισμός",
                "reporting": "Αναφορές",
                "globalReports": "Καθολικές Αναφορές",
                "organizationReports": "Αναφορές Οργανισμού",
                "accessLevels": {
                    "global": "καθολικό",
                    "organization": "οργανισμός"
                }
            }
        },
        "ar": {
            "organizationScope": {
                "globalAccess": "الوصول العالمي",
                "organizationAccess": "وصول المنظمة",
                "viewing": "عرض",
                "allOrganizations": "جميع المنظمات",
                "limitedTo": "مقيد بـ",
                "yourOrganization": "منظمتك",
                "switchOrganization": "تبديل المنظمة",
                "switch": "تبديل",
                "dataAccess": "الوصول للبيانات",
                "unrestricted": "غير مقيد",
                "organizationScoped": "مقيد بالمنظمة",
                "userManagement": "إدارة المستخدمين",
                "ownOrganization": "المنظمة الخاصة",
                "reporting": "التقارير",
                "globalReports": "التقارير العالمية",
                "organizationReports": "تقارير المنظمة",
                "accessLevels": {
                    "global": "عالمي",
                    "organization": "منظمة"
                }
            }
        },
        "es": {
            "organizationScope": {
                "globalAccess": "Acceso Global",
                "organizationAccess": "Acceso de Organización",
                "viewing": "Viendo",
                "allOrganizations": "Todas las Organizaciones",
                "limitedTo": "Limitado a",
                "yourOrganization": "Tu Organización",
                "switchOrganization": "Cambiar Organización",
                "switch": "Cambiar",
                "dataAccess": "Acceso a Datos",
                "unrestricted": "Sin Restricciones",
                "organizationScoped": "Limitado a Organización",
                "userManagement": "Gestión de Usuarios",
                "ownOrganization": "Propia Organización",
                "reporting": "Informes",
                "globalReports": "Informes Globales",
                "organizationReports": "Informes de Organización",
                "accessLevels": {
                    "global": "global",
                    "organization": "organización"
                }
            }
        },
        "tr": {
            "organizationScope": {
                "globalAccess": "Küresel Erişim",
                "organizationAccess": "Organizasyon Erişimi",
                "viewing": "Görüntüleme",
                "allOrganizations": "Tüm Organizasyonlar",
                "limitedTo": "Sınırlı",
                "yourOrganization": "Organizasyonunuz",
                "switchOrganization": "Organizasyon Değiştir",
                "switch": "Değiştir",
                "dataAccess": "Veri Erişimi",
                "unrestricted": "Sınırsız",
                "organizationScoped": "Organizasyon Kapsamlı",
                "userManagement": "Kullanıcı Yönetimi",
                "ownOrganization": "Kendi Organizasyon",
                "reporting": "Raporlama",
                "globalReports": "Küresel Raporlar",
                "organizationReports": "Organizasyon Raporları",
                "accessLevels": {
                    "global": "küresel",
                    "organization": "organizasyon"
                }
            }
        },
        "no": {
            "organizationScope": {
                "globalAccess": "Global Tilgang",
                "organizationAccess": "Organisasjonstilgang",
                "viewing": "Viser",
                "allOrganizations": "Alle Organisasjoner",
                "limitedTo": "Begrenset til",
                "yourOrganization": "Din Organisasjon",
                "switchOrganization": "Bytt Organisasjon",
                "switch": "Bytt",
                "dataAccess": "Datatilgang",
                "unrestricted": "Ubegrenset",
                "organizationScoped": "Organisasjonsbegrenset",
                "userManagement": "Brukerbehandling",
                "ownOrganization": "Egen Organisasjon",
                "reporting": "Rapportering",
                "globalReports": "Globale Rapporter",
                "organizationReports": "Organisasjonsrapporter",
                "accessLevels": {
                    "global": "global",
                    "organization": "organisasjon"
                }
            }
        }
    }
    
    # Process each locale file
    locale_dir = "frontend/src/locales"
    for lang_code, translations in scope_translations.items():
        file_path = os.path.join(locale_dir, f"{lang_code}.json")
        
        if not os.path.exists(file_path):
            print(f"⚠️  Locale file not found: {file_path}")
            continue
            
        print(f"Adding organization scope translations to {file_path}...")
        
        # Load existing translations
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Add organization scope translations
        data.update(translations)
        
        # Write back to file
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ Added organization scope translations to {lang_code}.json")
    
    print("\n🎉 Organization scope translations added successfully!")
    print("The OrganizationScopeIndicator component can now be localized.")

if __name__ == "__main__":
    add_organization_scope_translations()