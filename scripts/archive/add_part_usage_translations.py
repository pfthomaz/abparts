#!/usr/bin/env python3
import json

# Translation keys to add
translations = {
    "en": {
        "partUsage": {
            "title": "Record Part Usage",
            "failedToLoadData": "Failed to load form data. Please try again.",
            "organizationMismatchWarning": "Selected machine and warehouse belong to different organizations. Please ensure you have proper authorization.",
            "pleaseSelectMachine": "Please select a machine",
            "pleaseSelectPart": "Please select a part",
            "pleaseSelectWarehouse": "Please select a warehouse",
            "pleaseEnterValidQuantity": "Please enter a valid quantity",
            "insufficientInventory": "Insufficient inventory. Available: {{available}}",
            "recordedSuccessfully": "Part usage recorded successfully",
            "failedToRecord": "Failed to record part usage",
            "step1FromWarehouse": "1. From Warehouse",
            "step2Part": "2. Part",
            "step3ToMachine": "3. To Machine",
            "selectWarehouseFirst": "Select warehouse first",
            "selectWarehouseHelp": "Select the warehouse where the part is stored",
            "selectAPart": "Select a part",
            "noPartsAvailable": "No parts available in this warehouse",
            "available": "available",
            "availableInStock": "Available in stock",
            "preSelected": "(Pre-selected)",
            "selectPartFirst": "Select part first",
            "selectDestinationMachine": "Select destination machine",
            "machinePreSelectedHelp": "Machine pre-selected from Machines page and cannot be changed",
            "selectMachineHelp": "Select the machine where the part will be used",
            "availableInventory": "Available Inventory",
            "noStockAvailable": "(No stock available)",
            "quantityUsed": "Quantity Used",
            "wholeUnits": "Whole units",
            "decimalAllowed": "Decimal quantities allowed",
            "usageDate": "Usage Date",
            "referenceNumber": "Reference Number",
            "referenceNumberPlaceholder": "Work order, service ticket, etc.",
            "notes": "Notes",
            "notesPlaceholder": "Additional details about this part usage",
            "usageSummary": "Usage Summary",
            "machine": "Machine",
            "part": "Part",
            "quantity": "Quantity",
            "from": "From",
            "date": "Date",
            "recording": "Recording...",
            "recordUsage": "Record Usage"
        },
        "common": {
            "success": "Success",
            "warning": "Warning"
        }
    },
    "el": {
        "partUsage": {
            "title": "Καταγραφή Χρήσης Ανταλλακτικού",
            "failedToLoadData": "Αποτυχία φόρτωσης δεδομένων φόρμας. Παρακαλώ δοκιμάστε ξανά.",
            "organizationMismatchWarning": "Το επιλεγμένο μηχάνημα και η αποθήκη ανήκουν σε διαφορετικούς οργανισμούς. Βεβαιωθείτε ότι έχετε την κατάλληλη εξουσιοδότηση.",
            "pleaseSelectMachine": "Παρακαλώ επιλέξτε μηχάνημα",
            "pleaseSelectPart": "Παρακαλώ επιλέξτε ανταλλακτικό",
            "pleaseSelectWarehouse": "Παρακαλώ επιλέξτε αποθήκη",
            "pleaseEnterValidQuantity": "Παρακαλώ εισάγετε έγκυρη ποσότητα",
            "insufficientInventory": "Ανεπαρκές απόθεμα. Διαθέσιμο: {{available}}",
            "recordedSuccessfully": "Η χρήση ανταλλακτικού καταγράφηκε με επιτυχία",
            "failedToRecord": "Αποτυχία καταγραφής χρήσης ανταλλακτικού",
            "step1FromWarehouse": "1. Από Αποθήκη",
            "step2Part": "2. Ανταλλακτικό",
            "step3ToMachine": "3. Σε Μηχάνημα",
            "selectWarehouseFirst": "Επιλέξτε πρώτα αποθήκη",
            "selectWarehouseHelp": "Επιλέξτε την αποθήκη όπου αποθηκεύεται το ανταλλακτικό",
            "selectAPart": "Επιλέξτε ανταλλακτικό",
            "noPartsAvailable": "Δεν υπάρχουν διαθέσιμα ανταλλακτικά σε αυτή την αποθήκη",
            "available": "διαθέσιμα",
            "availableInStock": "Διαθέσιμο σε απόθεμα",
            "preSelected": "(Προεπιλεγμένο)",
            "selectPartFirst": "Επιλέξτε πρώτα ανταλλακτικό",
            "selectDestinationMachine": "Επιλέξτε μηχάνημα προορισμού",
            "machinePreSelectedHelp": "Το μηχάνημα προεπιλέχθηκε από τη σελίδα Μηχανημάτων και δεν μπορεί να αλλάξει",
            "selectMachineHelp": "Επιλέξτε το μηχάνημα όπου θα χρησιμοποιηθεί το ανταλλακτικό",
            "availableInventory": "Διαθέσιμο Απόθεμα",
            "noStockAvailable": "(Δεν υπάρχει διαθέσιμο απόθεμα)",
            "quantityUsed": "Ποσότητα που Χρησιμοποιήθηκε",
            "wholeUnits": "Ολόκληρες μονάδες",
            "decimalAllowed": "Επιτρέπονται δεκαδικές ποσότητες",
            "usageDate": "Ημερομηνία Χρήσης",
            "referenceNumber": "Αριθμός Αναφοράς",
            "referenceNumberPlaceholder": "Εντολή εργασίας, δελτίο εξυπηρέτησης κ.λπ.",
            "notes": "Σημειώσεις",
            "notesPlaceholder": "Πρόσθετες λεπτομέρειες για αυτή τη χρήση ανταλλακτικού",
            "usageSummary": "Περίληψη Χρήσης",
            "machine": "Μηχάνημα",
            "part": "Ανταλλακτικό",
            "quantity": "Ποσότητα",
            "from": "Από",
            "date": "Ημερομηνία",
            "recording": "Καταγραφή...",
            "recordUsage": "Καταγραφή Χρήσης"
        },
        "common": {
            "success": "Επιτυχία",
            "warning": "Προειδοποίηση"
        }
    },
    "ar": {
        "partUsage": {
            "title": "تسجيل استخدام القطعة",
            "failedToLoadData": "فشل في تحميل بيانات النموذج. يرجى المحاولة مرة أخرى.",
            "organizationMismatchWarning": "الآلة والمستودع المحددان ينتميان إلى منظمات مختلفة. يرجى التأكد من حصولك على التفويض المناسب.",
            "pleaseSelectMachine": "يرجى اختيار آلة",
            "pleaseSelectPart": "يرجى اختيار قطعة",
            "pleaseSelectWarehouse": "يرجى اختيار مستودع",
            "pleaseEnterValidQuantity": "يرجى إدخال كمية صالحة",
            "insufficientInventory": "مخزون غير كافٍ. المتاح: {{available}}",
            "recordedSuccessfully": "تم تسجيل استخدام القطعة بنجاح",
            "failedToRecord": "فشل في تسجيل استخدام القطعة",
            "step1FromWarehouse": "1. من المستودع",
            "step2Part": "2. القطعة",
            "step3ToMachine": "3. إلى الآلة",
            "selectWarehouseFirst": "اختر المستودع أولاً",
            "selectWarehouseHelp": "اختر المستودع حيث يتم تخزين القطعة",
            "selectAPart": "اختر قطعة",
            "noPartsAvailable": "لا توجد قطع متاحة في هذا المستودع",
            "available": "متاح",
            "availableInStock": "متاح في المخزون",
            "preSelected": "(محدد مسبقاً)",
            "selectPartFirst": "اختر القطعة أولاً",
            "selectDestinationMachine": "اختر آلة الوجهة",
            "machinePreSelectedHelp": "تم تحديد الآلة مسبقاً من صفحة الآلات ولا يمكن تغييرها",
            "selectMachineHelp": "اختر الآلة التي سيتم استخدام القطعة فيها",
            "availableInventory": "المخزون المتاح",
            "noStockAvailable": "(لا يوجد مخزون متاح)",
            "quantityUsed": "الكمية المستخدمة",
            "wholeUnits": "وحدات كاملة",
            "decimalAllowed": "الكميات العشرية مسموح بها",
            "usageDate": "تاريخ الاستخدام",
            "referenceNumber": "الرقم المرجعي",
            "referenceNumberPlaceholder": "أمر عمل، تذكرة خدمة، إلخ.",
            "notes": "ملاحظات",
            "notesPlaceholder": "تفاصيل إضافية حول استخدام هذه القطعة",
            "usageSummary": "ملخص الاستخدام",
            "machine": "الآلة",
            "part": "القطعة",
            "quantity": "الكمية",
            "from": "من",
            "date": "التاريخ",
            "recording": "جاري التسجيل...",
            "recordUsage": "تسجيل الاستخدام"
        },
        "common": {
            "success": "نجاح",
            "warning": "تحذير"
        }
    },
    "es": {
        "partUsage": {
            "title": "Registrar Uso de Pieza",
            "failedToLoadData": "Error al cargar datos del formulario. Por favor, inténtelo de nuevo.",
            "organizationMismatchWarning": "La máquina y el almacén seleccionados pertenecen a diferentes organizaciones. Asegúrese de tener la autorización adecuada.",
            "pleaseSelectMachine": "Por favor seleccione una máquina",
            "pleaseSelectPart": "Por favor seleccione una pieza",
            "pleaseSelectWarehouse": "Por favor seleccione un almacén",
            "pleaseEnterValidQuantity": "Por favor ingrese una cantidad válida",
            "insufficientInventory": "Inventario insuficiente. Disponible: {{available}}",
            "recordedSuccessfully": "Uso de pieza registrado exitosamente",
            "failedToRecord": "Error al registrar el uso de pieza",
            "step1FromWarehouse": "1. Desde Almacén",
            "step2Part": "2. Pieza",
            "step3ToMachine": "3. A Máquina",
            "selectWarehouseFirst": "Seleccione primero el almacén",
            "selectWarehouseHelp": "Seleccione el almacén donde se almacena la pieza",
            "selectAPart": "Seleccione una pieza",
            "noPartsAvailable": "No hay piezas disponibles en este almacén",
            "available": "disponible",
            "availableInStock": "Disponible en stock",
            "preSelected": "(Preseleccionado)",
            "selectPartFirst": "Seleccione primero la pieza",
            "selectDestinationMachine": "Seleccione máquina de destino",
            "machinePreSelectedHelp": "Máquina preseleccionada desde la página de Máquinas y no se puede cambiar",
            "selectMachineHelp": "Seleccione la máquina donde se usará la pieza",
            "availableInventory": "Inventario Disponible",
            "noStockAvailable": "(Sin stock disponible)",
            "quantityUsed": "Cantidad Utilizada",
            "wholeUnits": "Unidades enteras",
            "decimalAllowed": "Cantidades decimales permitidas",
            "usageDate": "Fecha de Uso",
            "referenceNumber": "Número de Referencia",
            "referenceNumberPlaceholder": "Orden de trabajo, ticket de servicio, etc.",
            "notes": "Notas",
            "notesPlaceholder": "Detalles adicionales sobre este uso de pieza",
            "usageSummary": "Resumen de Uso",
            "machine": "Máquina",
            "part": "Pieza",
            "quantity": "Cantidad",
            "from": "Desde",
            "date": "Fecha",
            "recording": "Registrando...",
            "recordUsage": "Registrar Uso"
        },
        "common": {
            "success": "Éxito",
            "warning": "Advertencia"
        }
    },
    "tr": {
        "partUsage": {
            "title": "Parça Kullanımını Kaydet",
            "failedToLoadData": "Form verileri yüklenemedi. Lütfen tekrar deneyin.",
            "organizationMismatchWarning": "Seçilen makine ve depo farklı kuruluşlara ait. Uygun yetkiniz olduğundan emin olun.",
            "pleaseSelectMachine": "Lütfen bir makine seçin",
            "pleaseSelectPart": "Lütfen bir parça seçin",
            "pleaseSelectWarehouse": "Lütfen bir depo seçin",
            "pleaseEnterValidQuantity": "Lütfen geçerli bir miktar girin",
            "insufficientInventory": "Yetersiz envanter. Mevcut: {{available}}",
            "recordedSuccessfully": "Parça kullanımı başarıyla kaydedildi",
            "failedToRecord": "Parça kullanımı kaydedilemedi",
            "step1FromWarehouse": "1. Depodan",
            "step2Part": "2. Parça",
            "step3ToMachine": "3. Makineye",
            "selectWarehouseFirst": "Önce depo seçin",
            "selectWarehouseHelp": "Parçanın saklandığı depoyu seçin",
            "selectAPart": "Bir parça seçin",
            "noPartsAvailable": "Bu depoda parça yok",
            "available": "mevcut",
            "availableInStock": "Stokta mevcut",
            "preSelected": "(Önceden seçilmiş)",
            "selectPartFirst": "Önce parça seçin",
            "selectDestinationMachine": "Hedef makineyi seçin",
            "machinePreSelectedHelp": "Makine, Makineler sayfasından önceden seçilmiş ve değiştirilemez",
            "selectMachineHelp": "Parçanın kullanılacağı makineyi seçin",
            "availableInventory": "Mevcut Envanter",
            "noStockAvailable": "(Stok yok)",
            "quantityUsed": "Kullanılan Miktar",
            "wholeUnits": "Tam birimler",
            "decimalAllowed": "Ondalık miktarlara izin verilir",
            "usageDate": "Kullanım Tarihi",
            "referenceNumber": "Referans Numarası",
            "referenceNumberPlaceholder": "İş emri, servis bileti, vb.",
            "notes": "Notlar",
            "notesPlaceholder": "Bu parça kullanımı hakkında ek ayrıntılar",
            "usageSummary": "Kullanım Özeti",
            "machine": "Makine",
            "part": "Parça",
            "quantity": "Miktar",
            "from": "Nereden",
            "date": "Tarih",
            "recording": "Kaydediliyor...",
            "recordUsage": "Kullanımı Kaydet"
        },
        "common": {
            "success": "Başarılı",
            "warning": "Uyarı"
        }
    },
    "no": {
        "partUsage": {
            "title": "Registrer Delbruk",
            "failedToLoadData": "Kunne ikke laste skjemadata. Vennligst prøv igjen.",
            "organizationMismatchWarning": "Valgt maskin og lager tilhører forskjellige organisasjoner. Sørg for at du har riktig autorisasjon.",
            "pleaseSelectMachine": "Vennligst velg en maskin",
            "pleaseSelectPart": "Vennligst velg en del",
            "pleaseSelectWarehouse": "Vennligst velg et lager",
            "pleaseEnterValidQuantity": "Vennligst angi en gyldig mengde",
            "insufficientInventory": "Utilstrekkelig lager. Tilgjengelig: {{available}}",
            "recordedSuccessfully": "Delbruk registrert",
            "failedToRecord": "Kunne ikke registrere delbruk",
            "step1FromWarehouse": "1. Fra Lager",
            "step2Part": "2. Del",
            "step3ToMachine": "3. Til Maskin",
            "selectWarehouseFirst": "Velg lager først",
            "selectWarehouseHelp": "Velg lageret der delen er lagret",
            "selectAPart": "Velg en del",
            "noPartsAvailable": "Ingen deler tilgjengelig i dette lageret",
            "available": "tilgjengelig",
            "availableInStock": "Tilgjengelig på lager",
            "preSelected": "(Forhåndsvalgt)",
            "selectPartFirst": "Velg del først",
            "selectDestinationMachine": "Velg destinasjonsmaskin",
            "machinePreSelectedHelp": "Maskin forhåndsvalgt fra Maskiner-siden og kan ikke endres",
            "selectMachineHelp": "Velg maskinen der delen skal brukes",
            "availableInventory": "Tilgjengelig Lager",
            "noStockAvailable": "(Ingen lager tilgjengelig)",
            "quantityUsed": "Mengde Brukt",
            "wholeUnits": "Hele enheter",
            "decimalAllowed": "Desimalmengder tillatt",
            "usageDate": "Bruksdato",
            "referenceNumber": "Referansenummer",
            "referenceNumberPlaceholder": "Arbeidsordre, servicebillett, etc.",
            "notes": "Notater",
            "notesPlaceholder": "Ytterligere detaljer om denne delbruken",
            "usageSummary": "Brukssammendrag",
            "machine": "Maskin",
            "part": "Del",
            "quantity": "Mengde",
            "from": "Fra",
            "date": "Dato",
            "recording": "Registrerer...",
            "recordUsage": "Registrer Bruk"
        },
        "common": {
            "success": "Suksess",
            "warning": "Advarsel"
        }
    }
}

def deep_merge(base, updates):
    """Recursively merge updates into base dictionary"""
    for key, value in updates.items():
        if key in base and isinstance(base[key], dict) and isinstance(value, dict):
            deep_merge(base[key], value)
        else:
            base[key] = value
    return base

# Update each language file
for lang, new_translations in translations.items():
    filename = f'frontend/src/locales/{lang}.json'
    
    # Read existing translations
    with open(filename, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Merge new translations
    data = deep_merge(data, new_translations)
    
    # Write back with proper formatting
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write('\n')
    
    print(f"✓ Updated {filename}")

print("\n✅ All translation files updated successfully!")
print("\nNew keys added for PartUsageRecorder component")
