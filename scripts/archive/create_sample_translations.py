#!/usr/bin/env python3

"""
Create sample translations for existing maintenance protocols
This script will add Greek, Arabic, Spanish, Turkish, and Norwegian translations
"""

import requests
import json
import time

# Configuration
BASE_URL = "http://localhost:8000"
TEST_USERNAME = "test_admin"  # Test super admin user
TEST_PASSWORD = "test123"  # Test password

# Sample translations for common maintenance protocols
SAMPLE_TRANSLATIONS = {
    # Daily Start of Day Protocol
    "Start of the day": {
        "el": {
            "name": "Ημερήσια Έναρξη Ημέρας",
            "description": "Ολοκληρώστε αυτές τις εργασίες στην αρχή κάθε ημέρας για να διασφαλίσετε την ασφαλή και αποδοτική λειτουργία του μηχανήματος"
        },
        "ar": {
            "name": "بداية اليوم اليومية",
            "description": "أكمل هذه المهام في بداية كل يوم لضمان التشغيل الآمن والفعال للآلة"
        },
        "es": {
            "name": "Inicio Diario del Día",
            "description": "Complete estas tareas al inicio de cada día para asegurar el funcionamiento seguro y eficiente de la máquina"
        },
        "tr": {
            "name": "Günlük Gün Başlangıcı",
            "description": "Makinenin güvenli ve verimli çalışmasını sağlamak için her gün başında bu görevleri tamamlayın"
        },
        "no": {
            "name": "Daglig Oppstart",
            "description": "Fullfør disse oppgavene ved starten av hver dag for å sikre trygg og effektiv drift av maskinen"
        }
    },
    
    # End of day maintenance Protocol
    "End of day maintenance": {
        "el": {
            "name": "Συντήρηση Τέλους Ημέρας",
            "description": "Εργασίες συντήρησης που πρέπει να εκτελούνται στο τέλος κάθε ημέρας εργασίας"
        },
        "ar": {
            "name": "صيانة نهاية اليوم",
            "description": "مهام الصيانة التي يجب تنفيذها في نهاية كل يوم عمل"
        },
        "es": {
            "name": "Mantenimiento de Fin de Día",
            "description": "Tareas de mantenimiento que deben realizarse al final de cada día de trabajo"
        },
        "tr": {
            "name": "Gün Sonu Bakımı",
            "description": "Her iş günü sonunda yapılması gereken bakım görevleri"
        },
        "no": {
            "name": "Slutt-av-dag Vedlikehold",
            "description": "Vedlikeholdsoppgaver som må utføres på slutten av hver arbeidsdag"
        }
    },
    
    # 50 Hour Service
    "50h service": {
        "el": {
            "name": "Συντήρηση 50 Ωρών",
            "description": "Αρχική συντήρηση μετά από 50 ώρες λειτουργίας - κρίσιμη για τη μακροπρόθεσμη αξιοπιστία"
        },
        "ar": {
            "name": "خدمة 50 ساعة",
            "description": "الصيانة الأولية بعد 50 ساعة تشغيل - حاسمة للموثوقية طويلة المدى"
        },
        "es": {
            "name": "Servicio de 50 Horas",
            "description": "Mantenimiento inicial después de 50 horas de operación - crítico para la confiabilidad a largo plazo"
        },
        "tr": {
            "name": "50 Saat Servisi",
            "description": "50 saat çalışma sonrası ilk bakım - uzun vadeli güvenilirlik için kritik"
        },
        "no": {
            "name": "50 Timers Service",
            "description": "Innledende vedlikehold etter 50 timer drift - kritisk for langsiktig pålitelighet"
        }
    }
}

# Sample checklist item translations
CHECKLIST_TRANSLATIONS = {
    "Check oil level": {
        "el": "Έλεγχος στάθμης λαδιού",
        "ar": "فحص مستوى الزيت",
        "es": "Verificar nivel de aceite",
        "tr": "Yağ seviyesini kontrol et",
        "no": "Sjekk oljenivå"
    },
    "Inspect filters": {
        "el": "Επιθεώρηση φίλτρων",
        "ar": "فحص المرشحات",
        "es": "Inspeccionar filtros",
        "tr": "Filtreleri incele",
        "no": "Inspiser filtre"
    },
    "Test emergency stop": {
        "el": "Δοκιμή διακόπτη έκτακτης ανάγκης",
        "ar": "اختبار إيقاف الطوارئ",
        "es": "Probar parada de emergencia",
        "tr": "Acil durdurma testini yap",
        "no": "Test nødstopp"
    },
    "Clean exterior surfaces": {
        "el": "Καθαρισμός εξωτερικών επιφανειών",
        "ar": "تنظيف الأسطح الخارجية",
        "es": "Limpiar superficies exteriores",
        "tr": "Dış yüzeyleri temizle",
        "no": "Rengjør utvendige overflater"
    },
    "Check alarm functions": {
        "el": "Έλεγχος λειτουργιών συναγερμού",
        "ar": "فحص وظائف الإنذار",
        "es": "Verificar funciones de alarma",
        "tr": "Alarm fonksiyonlarını kontrol et",
        "no": "Sjekk alarmfunksjoner"
    },
    "Lubricate moving parts": {
        "el": "Λίπανση κινούμενων μερών",
        "ar": "تشحيم الأجزاء المتحركة",
        "es": "Lubricar partes móviles",
        "tr": "Hareketli parçaları yağla",
        "no": "Smør bevegelige deler"
    },
    "Replace air filter": {
        "el": "Αντικατάσταση φίλτρου αέρα",
        "ar": "استبدال مرشح الهواء",
        "es": "Reemplazar filtro de aire",
        "tr": "Hava filtresini değiştir",
        "no": "Skift luftfilter"
    },
    "Check hydraulic fluid": {
        "el": "Έλεγχος υδραυλικού υγρού",
        "ar": "فحص السائل الهيدروليكي",
        "es": "Verificar fluido hidráulico",
        "tr": "Hidrolik sıvıyı kontrol et",
        "no": "Sjekk hydraulikkvæske"
    },
    "Lift the power pack and check for oil leaks": {
        "el": "Ανυψώστε το πακέτο ισχύος και ελέγξτε για διαρροές λαδιού",
        "ar": "ارفع حزمة الطاقة وتحقق من تسريبات الزيت",
        "es": "Levante el paquete de energía y verifique fugas de aceite",
        "tr": "Güç paketini kaldırın ve yağ sızıntılarını kontrol edin",
        "no": "Løft kraftpakken og sjekk for oljelekkasjer"
    },
    "Check belt tension": {
        "el": "Έλεγχος τάσης ιμάντα",
        "ar": "فحص شد الحزام",
        "es": "Verificar tensión de la correa",
        "tr": "Kayış gerginliğini kontrol et",
        "no": "Sjekk beltespenning"
    },
    "Run the Boss with freshwater": {
        "el": "Λειτουργήστε το Boss με γλυκό νερό",
        "ar": "تشغيل البوس بالمياه العذبة",
        "es": "Ejecutar el Boss con agua dulce",
        "tr": "Boss'u tatlı su ile çalıştırın",
        "no": "Kjør Boss med ferskvann"
    },
    "Grease all rotary unions": {
        "el": "Λιπάνετε όλες τις περιστροφικές ενώσεις",
        "ar": "تشحيم جميع الوصلات الدوارة",
        "es": "Engrasar todas las uniones rotativas",
        "tr": "Tüm döner bağlantıları yağlayın",
        "no": "Smør alle roterende koblinger"
    },
    "Clean bag filter": {
        "el": "Καθαρισμός φίλτρου σάκου",
        "ar": "تنظيف مرشح الكيس",
        "es": "Limpiar filtro de bolsa",
        "tr": "Torba filtresini temizle",
        "no": "Rengjør posefilter"
    }
}

class TranslationCreator:
    def __init__(self):
        self.token = None
        self.headers = {}
        
    def authenticate(self):
        """Authenticate and get access token"""
        print("🔐 Authenticating...")
        
        auth_data = {
            "username": TEST_USERNAME,
            "password": TEST_PASSWORD
        }
        
        response = requests.post(f"{BASE_URL}/token", data=auth_data)
        
        if response.status_code == 200:
            token_data = response.json()
            self.token = token_data["access_token"]
            self.headers = {"Authorization": f"Bearer {self.token}"}
            print("✅ Authentication successful")
            return True
        else:
            print(f"❌ Authentication failed: {response.status_code}")
            print(response.text)
            return False
    
    def get_protocols(self):
        """Get all existing protocols"""
        print("📋 Fetching existing protocols...")
        
        response = requests.get(
            f"{BASE_URL}/maintenance-protocols",
            headers=self.headers
        )
        
        if response.status_code == 200:
            protocols = response.json()
            print(f"✅ Found {len(protocols)} protocols")
            return protocols
        else:
            print(f"❌ Failed to get protocols: {response.status_code}")
            return []
    
    def create_protocol_translations(self, protocol):
        """Create translations for a protocol"""
        protocol_name = protocol["name"]
        protocol_id = protocol["id"]
        
        print(f"🌍 Creating translations for: {protocol_name}")
        
        # Find matching translation template
        translation_template = None
        for template_name, translations in SAMPLE_TRANSLATIONS.items():
            if template_name.lower() in protocol_name.lower():
                translation_template = translations
                break
        
        if not translation_template:
            print(f"⚠️  No translation template found for: {protocol_name}")
            return
        
        created_count = 0
        
        for language, translation_data in translation_template.items():
            try:
                response = requests.post(
                    f"{BASE_URL}/translations/protocols/{protocol_id}/translations",
                    headers=self.headers,
                    json={
                        "language_code": language,
                        "name": translation_data["name"],
                        "description": translation_data["description"]
                    }
                )
                
                if response.status_code == 200:
                    print(f"  ✅ Created {language} translation: {translation_data['name']}")
                    created_count += 1
                else:
                    print(f"  ❌ Failed to create {language} translation: {response.status_code}")
                    
            except Exception as e:
                print(f"  💥 Error creating {language} translation: {str(e)}")
        
        print(f"  📊 Created {created_count} translations for {protocol_name}")
        return created_count
    
    def get_checklist_items(self, protocol_id):
        """Get checklist items for a protocol"""
        response = requests.get(
            f"{BASE_URL}/maintenance-protocols/{protocol_id}/checklist-items",
            headers=self.headers
        )
        
        if response.status_code == 200:
            return response.json()
        return []
    
    def create_checklist_item_translations(self, protocol):
        """Create translations for checklist items"""
        protocol_id = protocol["id"]
        items = self.get_checklist_items(protocol_id)
        
        if not items:
            print(f"  ⚠️  No checklist items found for {protocol['name']}")
            return 0
        
        print(f"📝 Creating checklist item translations for {len(items)} items...")
        
        total_created = 0
        
        for item in items:
            item_description = item["item_description"]
            item_id = item["id"]
            
            # Find matching translation
            translation_template = None
            for template_desc, translations in CHECKLIST_TRANSLATIONS.items():
                if template_desc.lower() in item_description.lower():
                    translation_template = translations
                    break
            
            if not translation_template:
                print(f"    ⚠️  No translation found for: {item_description}")
                continue
            
            created_count = 0
            
            for language, translated_description in translation_template.items():
                try:
                    response = requests.post(
                        f"{BASE_URL}/translations/checklist-items/{item_id}/translations",
                        headers=self.headers,
                        json={
                            "language_code": language,
                            "item_description": translated_description,
                            "notes": None,
                            "item_category": None
                        }
                    )
                    
                    if response.status_code == 200:
                        created_count += 1
                    
                except Exception as e:
                    print(f"    💥 Error creating {language} translation: {str(e)}")
            
            if created_count > 0:
                print(f"    ✅ Created {created_count} translations for: {item_description}")
                total_created += created_count
        
        return total_created
    
    def create_all_translations(self):
        """Create translations for all protocols and their checklist items"""
        print("🚀 Starting Sample Translation Creation")
        print("=" * 50)
        
        if not self.authenticate():
            return False
        
        protocols = self.get_protocols()
        if not protocols:
            print("❌ No protocols found")
            return False
        
        total_protocol_translations = 0
        total_item_translations = 0
        
        for protocol in protocols:
            print(f"\n🔧 Processing: {protocol['name']}")
            
            # Create protocol translations
            protocol_count = self.create_protocol_translations(protocol)
            if protocol_count:
                total_protocol_translations += protocol_count
            
            # Create checklist item translations
            item_count = self.create_checklist_item_translations(protocol)
            total_item_translations += item_count
            
            # Small delay to avoid overwhelming the API
            time.sleep(0.5)
        
        print(f"\n📊 Translation Creation Summary:")
        print(f"   Protocol translations: {total_protocol_translations}")
        print(f"   Checklist item translations: {total_item_translations}")
        print(f"   Total translations: {total_protocol_translations + total_item_translations}")
        
        if total_protocol_translations > 0 or total_item_translations > 0:
            print("\n🎉 Sample translations created successfully!")
            print("\nNext steps:")
            print("1. Test the translation API endpoints")
            print("2. Build the frontend translation management interface")
            print("3. Test language-aware protocol display")
        else:
            print("\n⚠️  No translations were created. Check the protocol names and templates.")
        
        return True


if __name__ == "__main__":
    creator = TranslationCreator()
    creator.create_all_translations()