#!/usr/bin/env python3
"""
Add detailed tour step content translations to all locale files
"""

import json
import os

# Define the detailed tour step content translations
tour_step_translations = {
    "en": {
        "tour": {
            "partsOrdering": {
                "steps": {
                    "welcomeTitle": "📦 Parts Ordering Tutorial",
                    "welcome": "Welcome! Let's learn how to order parts step-by-step.",
                    "findOrders": "First, hover over the navigation menu to find \"Orders\".",
                    "createOrder": "Click \"New Order\" button to start creating an order.",
                    "selectType": "Choose order type: Customer Order (buying parts) or Supplier Order (selling parts).",
                    "searchParts": "Search for parts by name, number, or description.",
                    "setQuantities": "Enter quantities needed and review stock levels.",
                    "submitTrack": "Add delivery details and submit your order. You can then track its status!"
                }
            },
            "partsUsage": {
                "steps": {
                    "welcomeTitle": "🔧 Parts Usage Recording",
                    "welcome": "Let's learn how to record parts consumed during machine operation.",
                    "goToMachines": "Navigate to \"Machines\" in the Operations menu.",
                    "selectMachine": "Select the specific machine where parts were used.",
                    "recordUsage": "Click \"Record Usage\" to log consumed parts.",
                    "findPart": "Search and select the part that was used.",
                    "enterQuantity": "Enter quantity used - inventory updates automatically!"
                }
            },
            "dailyOperations": {
                "steps": {
                    "welcomeTitle": "📋 Daily Operations",
                    "welcome": "Daily reporting helps track machine performance and maintenance.",
                    "navigate": "Find \"Daily Operations\" in the Operations menu.",
                    "chooseDateMachine": "Select the date and machine for your report.",
                    "enterMetrics": "Enter operational metrics: hours, cycles, performance data.",
                    "completeChecklist": "Complete daily checklist items and add notes.",
                    "submitReport": "Submit report to track machine health trends."
                }
            },
            "scheduledMaintenance": {
                "steps": {
                    "welcomeTitle": "⚙️ Scheduled Maintenance",
                    "welcome": "Execute scheduled maintenance protocols systematically.",
                    "findMaintenance": "Go to \"Maintenance Executions\" in Operations.",
                    "chooseProtocol": "Select the maintenance protocol to execute.",
                    "assignResources": "Assign machine and technician for the maintenance.",
                    "executeChecklist": "Work through checklist items systematically.",
                    "documentWork": "Record parts used and add photos/notes.",
                    "completeSchedule": "Complete protocol to generate reports and schedule next service."
                }
            }
        }
    },
    "el": {
        "tour": {
            "partsOrdering": {
                "steps": {
                    "welcomeTitle": "📦 Εκμάθηση Παραγγελιών Ανταλλακτικών",
                    "welcome": "Καλώς ήρθατε! Ας μάθουμε πώς να παραγγείλουμε ανταλλακτικά βήμα προς βήμα.",
                    "findOrders": "Πρώτα, περάστε το ποντίκι πάνω από το μενού πλοήγησης για να βρείτε τις \"Παραγγελίες\".",
                    "createOrder": "Κάντε κλικ στο κουμπί \"Νέα Παραγγελία\" για να ξεκινήσετε τη δημιουργία παραγγελίας.",
                    "selectType": "Επιλέξτε τύπο παραγγελίας: Παραγγελία Πελάτη (αγορά ανταλλακτικών) ή Παραγγελία Προμηθευτή (πώληση ανταλλακτικών).",
                    "searchParts": "Αναζητήστε ανταλλακτικά με όνομα, αριθμό ή περιγραφή.",
                    "setQuantities": "Εισάγετε τις απαιτούμενες ποσότητες και ελέγξτε τα επίπεδα αποθέματος.",
                    "submitTrack": "Προσθέστε λεπτομέρειες παράδοσης και υποβάλετε την παραγγελία σας. Μπορείτε στη συνέχεια να παρακολουθήσετε την κατάστασή της!"
                }
            },
            "partsUsage": {
                "steps": {
                    "welcomeTitle": "🔧 Καταγραφή Χρήσης Ανταλλακτικών",
                    "welcome": "Ας μάθουμε πώς να καταγράφουμε τα ανταλλακτικά που καταναλώνονται κατά τη λειτουργία μηχανημάτων.",
                    "goToMachines": "Πλοηγηθείτε στα \"Μηχανήματα\" στο μενού Λειτουργιών.",
                    "selectMachine": "Επιλέξτε το συγκεκριμένο μηχάνημα όπου χρησιμοποιήθηκαν ανταλλακτικά.",
                    "recordUsage": "Κάντε κλικ στο \"Καταγραφή Χρήσης\" για να καταγράψετε τα καταναλωμένα ανταλλακτικά.",
                    "findPart": "Αναζητήστε και επιλέξτε το ανταλλακτικό που χρησιμοποιήθηκε.",
                    "enterQuantity": "Εισάγετε την ποσότητα που χρησιμοποιήθηκε - το απόθεμα ενημερώνεται αυτόματα!"
                }
            },
            "dailyOperations": {
                "steps": {
                    "welcomeTitle": "📋 Ημερήσιες Λειτουργίες",
                    "welcome": "Η ημερήσια αναφορά βοηθά στην παρακολούθηση της απόδοσης και συντήρησης μηχανημάτων.",
                    "navigate": "Βρείτε τις \"Ημερήσιες Λειτουργίες\" στο μενού Λειτουργιών.",
                    "chooseDateMachine": "Επιλέξτε την ημερομηνία και το μηχάνημα για την αναφορά σας.",
                    "enterMetrics": "Εισάγετε λειτουργικές μετρήσεις: ώρες, κύκλους, δεδομένα απόδοσης.",
                    "completeChecklist": "Ολοκληρώστε τα στοιχεία της ημερήσιας λίστας ελέγχου και προσθέστε σημειώσεις.",
                    "submitReport": "Υποβάλετε την αναφορά για να παρακολουθήσετε τις τάσεις υγείας του μηχανήματος."
                }
            },
            "scheduledMaintenance": {
                "steps": {
                    "welcomeTitle": "⚙️ Προγραμματισμένη Συντήρηση",
                    "welcome": "Εκτελέστε συστηματικά τα πρωτόκολλα προγραμματισμένης συντήρησης.",
                    "findMaintenance": "Πηγαίνετε στις \"Εκτελέσεις Συντήρησης\" στις Λειτουργίες.",
                    "chooseProtocol": "Επιλέξτε το πρωτόκολλο συντήρησης προς εκτέλεση.",
                    "assignResources": "Αναθέστε μηχάνημα και τεχνικό για τη συντήρηση.",
                    "executeChecklist": "Εργαστείτε συστηματικά μέσω των στοιχείων της λίστας ελέγχου.",
                    "documentWork": "Καταγράψτε τα χρησιμοποιημένα ανταλλακτικά και προσθέστε φωτογραφίες/σημειώσεις.",
                    "completeSchedule": "Ολοκληρώστε το πρωτόκολλο για να δημιουργήσετε αναφορές και να προγραμματίσετε την επόμενη υπηρεσία."
                }
            }
        }
    },
    "ar": {
        "tour": {
            "partsOrdering": {
                "steps": {
                    "welcomeTitle": "📦 دليل طلب قطع الغيار",
                    "welcome": "مرحباً! دعنا نتعلم كيفية طلب قطع الغيار خطوة بخطوة.",
                    "findOrders": "أولاً، مرر الماوس فوق قائمة التنقل للعثور على \"الطلبات\".",
                    "createOrder": "انقر على زر \"طلب جديد\" لبدء إنشاء طلب.",
                    "selectType": "اختر نوع الطلب: طلب العميل (شراء قطع الغيار) أو طلب المورد (بيع قطع الغيار).",
                    "searchParts": "ابحث عن قطع الغيار بالاسم أو الرقم أو الوصف.",
                    "setQuantities": "أدخل الكميات المطلوبة وراجع مستويات المخزون.",
                    "submitTrack": "أضف تفاصيل التسليم وأرسل طلبك. يمكنك بعد ذلك تتبع حالته!"
                }
            },
            "partsUsage": {
                "steps": {
                    "welcomeTitle": "🔧 تسجيل استخدام قطع الغيار",
                    "welcome": "دعنا نتعلم كيفية تسجيل قطع الغيار المستهلكة أثناء تشغيل الآلات.",
                    "goToMachines": "انتقل إلى \"الآلات\" في قائمة العمليات.",
                    "selectMachine": "حدد الآلة المحددة التي تم استخدام قطع الغيار فيها.",
                    "recordUsage": "انقر على \"تسجيل الاستخدام\" لتسجيل قطع الغيار المستهلكة.",
                    "findPart": "ابحث واختر قطعة الغيار التي تم استخدامها.",
                    "enterQuantity": "أدخل الكمية المستخدمة - يتم تحديث المخزون تلقائياً!"
                }
            },
            "dailyOperations": {
                "steps": {
                    "welcomeTitle": "📋 العمليات اليومية",
                    "welcome": "التقارير اليومية تساعد في تتبع أداء الآلات والصيانة.",
                    "navigate": "ابحث عن \"العمليات اليومية\" في قائمة العمليات.",
                    "chooseDateMachine": "حدد التاريخ والآلة لتقريرك.",
                    "enterMetrics": "أدخل المقاييس التشغيلية: الساعات، الدورات، بيانات الأداء.",
                    "completeChecklist": "أكمل عناصر قائمة التحقق اليومية وأضف الملاحظات.",
                    "submitReport": "أرسل التقرير لتتبع اتجاهات صحة الآلة."
                }
            },
            "scheduledMaintenance": {
                "steps": {
                    "welcomeTitle": "⚙️ الصيانة المجدولة",
                    "welcome": "نفذ بروتوكولات الصيانة المجدولة بشكل منهجي.",
                    "findMaintenance": "اذهب إلى \"تنفيذ الصيانة\" في العمليات.",
                    "chooseProtocol": "حدد بروتوكول الصيانة المراد تنفيذه.",
                    "assignResources": "عين الآلة والفني للصيانة.",
                    "executeChecklist": "اعمل من خلال عناصر قائمة التحقق بشكل منهجي.",
                    "documentWork": "سجل قطع الغيار المستخدمة وأضف الصور/الملاحظات.",
                    "completeSchedule": "أكمل البروتوكول لإنشاء التقارير وجدولة الخدمة التالية."
                }
            }
        }
    },
    "es": {
        "tour": {
            "partsOrdering": {
                "steps": {
                    "welcomeTitle": "📦 Tutorial de Pedidos de Repuestos",
                    "welcome": "¡Bienvenido! Aprendamos cómo pedir repuestos paso a paso.",
                    "findOrders": "Primero, pasa el cursor sobre el menú de navegación para encontrar \"Pedidos\".",
                    "createOrder": "Haz clic en el botón \"Nuevo Pedido\" para comenzar a crear un pedido.",
                    "selectType": "Elige el tipo de pedido: Pedido de Cliente (comprar repuestos) o Pedido de Proveedor (vender repuestos).",
                    "searchParts": "Busca repuestos por nombre, número o descripción.",
                    "setQuantities": "Ingresa las cantidades necesarias y revisa los niveles de stock.",
                    "submitTrack": "Agrega detalles de entrega y envía tu pedido. ¡Luego puedes rastrear su estado!"
                }
            },
            "partsUsage": {
                "steps": {
                    "welcomeTitle": "🔧 Registro de Uso de Repuestos",
                    "welcome": "Aprendamos cómo registrar repuestos consumidos durante la operación de máquinas.",
                    "goToMachines": "Navega a \"Máquinas\" en el menú de Operaciones.",
                    "selectMachine": "Selecciona la máquina específica donde se usaron repuestos.",
                    "recordUsage": "Haz clic en \"Registrar Uso\" para registrar repuestos consumidos.",
                    "findPart": "Busca y selecciona el repuesto que se usó.",
                    "enterQuantity": "Ingresa la cantidad usada - ¡el inventario se actualiza automáticamente!"
                }
            },
            "dailyOperations": {
                "steps": {
                    "welcomeTitle": "📋 Operaciones Diarias",
                    "welcome": "Los informes diarios ayudan a rastrear el rendimiento y mantenimiento de máquinas.",
                    "navigate": "Encuentra \"Operaciones Diarias\" en el menú de Operaciones.",
                    "chooseDateMachine": "Selecciona la fecha y máquina para tu informe.",
                    "enterMetrics": "Ingresa métricas operacionales: horas, ciclos, datos de rendimiento.",
                    "completeChecklist": "Completa los elementos de la lista de verificación diaria y agrega notas.",
                    "submitReport": "Envía el informe para rastrear tendencias de salud de la máquina."
                }
            },
            "scheduledMaintenance": {
                "steps": {
                    "welcomeTitle": "⚙️ Mantenimiento Programado",
                    "welcome": "Ejecuta protocolos de mantenimiento programado sistemáticamente.",
                    "findMaintenance": "Ve a \"Ejecuciones de Mantenimiento\" en Operaciones.",
                    "chooseProtocol": "Selecciona el protocolo de mantenimiento a ejecutar.",
                    "assignResources": "Asigna máquina y técnico para el mantenimiento.",
                    "executeChecklist": "Trabaja a través de elementos de lista de verificación sistemáticamente.",
                    "documentWork": "Registra repuestos usados y agrega fotos/notas.",
                    "completeSchedule": "Completa el protocolo para generar informes y programar el próximo servicio."
                }
            }
        }
    },
    "tr": {
        "tour": {
            "partsOrdering": {
                "steps": {
                    "welcomeTitle": "📦 Parça Sipariş Eğitimi",
                    "welcome": "Hoş geldiniz! Adım adım parça siparişi vermeyi öğrenelim.",
                    "findOrders": "İlk olarak, \"Siparişler\"i bulmak için gezinme menüsünün üzerine gelin.",
                    "createOrder": "Sipariş oluşturmaya başlamak için \"Yeni Sipariş\" düğmesine tıklayın.",
                    "selectType": "Sipariş türünü seçin: Müşteri Siparişi (parça satın alma) veya Tedarikçi Siparişi (parça satma).",
                    "searchParts": "Parçaları ad, numara veya açıklama ile arayın.",
                    "setQuantities": "Gerekli miktarları girin ve stok seviyelerini gözden geçirin.",
                    "submitTrack": "Teslimat detaylarını ekleyin ve siparişinizi gönderin. Daha sonra durumunu takip edebilirsiniz!"
                }
            },
            "partsUsage": {
                "steps": {
                    "welcomeTitle": "🔧 Parça Kullanım Kaydı",
                    "welcome": "Makine işletimi sırasında tüketilen parçaları kaydetmeyi öğrenelim.",
                    "goToMachines": "İşlemler menüsünde \"Makineler\"e gidin.",
                    "selectMachine": "Parçaların kullanıldığı belirli makineyi seçin.",
                    "recordUsage": "Tüketilen parçaları kaydetmek için \"Kullanımı Kaydet\"e tıklayın.",
                    "findPart": "Kullanılan parçayı arayın ve seçin.",
                    "enterQuantity": "Kullanılan miktarı girin - envanter otomatik olarak güncellenir!"
                }
            },
            "dailyOperations": {
                "steps": {
                    "welcomeTitle": "📋 Günlük İşlemler",
                    "welcome": "Günlük raporlama makine performansını ve bakımını takip etmeye yardımcı olur.",
                    "navigate": "İşlemler menüsünde \"Günlük İşlemler\"i bulun.",
                    "chooseDateMachine": "Raporunuz için tarihi ve makineyi seçin.",
                    "enterMetrics": "İşletme metriklerini girin: saatler, döngüler, performans verileri.",
                    "completeChecklist": "Günlük kontrol listesi öğelerini tamamlayın ve notlar ekleyin.",
                    "submitReport": "Makine sağlığı eğilimlerini takip etmek için raporu gönderin."
                }
            },
            "scheduledMaintenance": {
                "steps": {
                    "welcomeTitle": "⚙️ Planlı Bakım",
                    "welcome": "Planlı bakım protokollerini sistematik olarak yürütün.",
                    "findMaintenance": "İşlemler'de \"Bakım Yürütmeleri\"ne gidin.",
                    "chooseProtocol": "Yürütülecek bakım protokolünü seçin.",
                    "assignResources": "Bakım için makine ve teknisyen atayın.",
                    "executeChecklist": "Kontrol listesi öğelerini sistematik olarak işleyin.",
                    "documentWork": "Kullanılan parçaları kaydedin ve fotoğraf/notlar ekleyin.",
                    "completeSchedule": "Raporlar oluşturmak ve bir sonraki hizmeti planlamak için protokolü tamamlayın."
                }
            }
        }
    },
    "no": {
        "tour": {
            "partsOrdering": {
                "steps": {
                    "welcomeTitle": "📦 Delebestilling Opplæring",
                    "welcome": "Velkommen! La oss lære hvordan vi bestiller deler steg for steg.",
                    "findOrders": "Først, hold musepekeren over navigasjonsmenyen for å finne \"Bestillinger\".",
                    "createOrder": "Klikk på \"Ny Bestilling\" knappen for å begynne å opprette en bestilling.",
                    "selectType": "Velg bestillingstype: Kundebestilling (kjøpe deler) eller Leverandørbestilling (selge deler).",
                    "searchParts": "Søk etter deler etter navn, nummer eller beskrivelse.",
                    "setQuantities": "Angi nødvendige mengder og gjennomgå lagernivåer.",
                    "submitTrack": "Legg til leveringsdetaljer og send inn bestillingen din. Du kan deretter spore statusen!"
                }
            },
            "partsUsage": {
                "steps": {
                    "welcomeTitle": "🔧 Delbruk Registrering",
                    "welcome": "La oss lære hvordan vi registrerer deler som forbrukes under maskindrift.",
                    "goToMachines": "Naviger til \"Maskiner\" i Operasjoner-menyen.",
                    "selectMachine": "Velg den spesifikke maskinen hvor deler ble brukt.",
                    "recordUsage": "Klikk på \"Registrer Bruk\" for å logge forbrukte deler.",
                    "findPart": "Søk og velg delen som ble brukt.",
                    "enterQuantity": "Angi mengde brukt - lageret oppdateres automatisk!"
                }
            },
            "dailyOperations": {
                "steps": {
                    "welcomeTitle": "📋 Daglige Operasjoner",
                    "welcome": "Daglig rapportering hjelper med å spore maskinytelse og vedlikehold.",
                    "navigate": "Finn \"Daglige Operasjoner\" i Operasjoner-menyen.",
                    "chooseDateMachine": "Velg dato og maskin for rapporten din.",
                    "enterMetrics": "Angi driftsmetrikker: timer, sykluser, ytelsesdata.",
                    "completeChecklist": "Fullfør daglige sjekkliste-elementer og legg til notater.",
                    "submitReport": "Send inn rapport for å spore maskinhelsetrender."
                }
            },
            "scheduledMaintenance": {
                "steps": {
                    "welcomeTitle": "⚙️ Planlagt Vedlikehold",
                    "welcome": "Utfør planlagte vedlikeholdsprotokoller systematisk.",
                    "findMaintenance": "Gå til \"Vedlikeholdsutførelser\" i Operasjoner.",
                    "chooseProtocol": "Velg vedlikeholdsprotokollen som skal utføres.",
                    "assignResources": "Tildel maskin og tekniker for vedlikeholdet.",
                    "executeChecklist": "Arbeid gjennom sjekkliste-elementer systematisk.",
                    "documentWork": "Registrer brukte deler og legg til bilder/notater.",
                    "completeSchedule": "Fullfør protokoll for å generere rapporter og planlegge neste service."
                }
            }
        }
    }
}

def update_translations_file(file_path, translations):
    """Update translations in a JSON file"""
    try:
        # Read existing translations
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Deep merge tour step translations
        if 'tour' in data:
            # Merge partsOrdering steps
            if 'partsOrdering' in data['tour']:
                if 'steps' in translations['tour']['partsOrdering']:
                    if 'steps' not in data['tour']['partsOrdering']:
                        data['tour']['partsOrdering']['steps'] = {}
                    data['tour']['partsOrdering']['steps'].update(translations['tour']['partsOrdering']['steps'])
            
            # Merge partsUsage steps
            if 'partsUsage' in data['tour']:
                if 'steps' in translations['tour']['partsUsage']:
                    if 'steps' not in data['tour']['partsUsage']:
                        data['tour']['partsUsage']['steps'] = {}
                    data['tour']['partsUsage']['steps'].update(translations['tour']['partsUsage']['steps'])
            
            # Merge dailyOperations steps
            if 'dailyOperations' in data['tour']:
                if 'steps' in translations['tour']['dailyOperations']:
                    if 'steps' not in data['tour']['dailyOperations']:
                        data['tour']['dailyOperations']['steps'] = {}
                    data['tour']['dailyOperations']['steps'].update(translations['tour']['dailyOperations']['steps'])
            
            # Merge scheduledMaintenance steps
            if 'scheduledMaintenance' in data['tour']:
                if 'steps' in translations['tour']['scheduledMaintenance']:
                    if 'steps' not in data['tour']['scheduledMaintenance']:
                        data['tour']['scheduledMaintenance']['steps'] = {}
                    data['tour']['scheduledMaintenance']['steps'].update(translations['tour']['scheduledMaintenance']['steps'])
        
        # Write back to file
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Updated {file_path}")
        
    except Exception as e:
        print(f"❌ Error updating {file_path}: {e}")

def main():
    """Add detailed tour step content translations to all locale files"""
    print("Adding detailed tour step content translations to locale files...")
    
    locales_dir = "frontend/src/locales"
    
    for lang_code, translations in tour_step_translations.items():
        file_path = os.path.join(locales_dir, f"{lang_code}.json")
        if os.path.exists(file_path):
            update_translations_file(file_path, translations)
        else:
            print(f"⚠️  Locale file not found: {file_path}")
    
    print("\n🎉 Detailed tour step content translations added successfully!")
    print("\nStep content now localized for:")
    print("- Parts Ordering workflow (7 steps)")
    print("- Parts Usage workflow (6 steps)")  
    print("- Daily Operations workflow (6 steps)")
    print("- Scheduled Maintenance workflow (7 steps)")
    print("- All 6 languages fully supported")

if __name__ == "__main__":
    main()