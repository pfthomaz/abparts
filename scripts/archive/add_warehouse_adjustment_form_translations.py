#!/usr/bin/env python3
import json

# Warehouse Stock Adjustment Form translations
translations = {
    'en': {
        'failedToFetchParts': 'Failed to fetch parts',
        'quantityMustBeValid': 'Quantity change must be a valid number',
        'cannotReduceStock': 'Cannot reduce stock by {{quantity}}. Current stock: {{currentStock}}',
        'failedToCreateAdjustment': 'Failed to create adjustment',
        'unknownWarehouse': 'Unknown Warehouse',
        'stockAdjustmentForm': {
            'title': 'Stock Adjustment',
            'searchParts': 'Search Parts',
            'searchPlaceholder': 'Search by part number or name...',
            'part': 'Part',
            'selectPart': 'Select a part',
            'current': 'Current',
            'currentStock': 'Current Stock',
            'quantityChange': 'Quantity Change',
            'quantityPlaceholder': 'Enter positive for increase, negative for decrease',
            'quantityHint': 'Use positive numbers to increase inventory, negative numbers to decrease',
            'newStockLevel': 'New stock level will be',
            'reason': 'Reason',
            'selectReason': 'Select a reason',
            'notes': 'Notes',
            'notesPlaceholder': 'Optional additional details about this adjustment...',
            'creatingAdjustment': 'Creating Adjustment...',
            'createAdjustment': 'Create Adjustment',
            'reasons': {
                'stocktakeAdjustment': 'Stocktake adjustment',
                'damagedGoods': 'Damaged goods',
                'expiredItems': 'Expired items',
                'foundItems': 'Found items',
                'lostItems': 'Lost items',
                'transferCorrection': 'Transfer correction',
                'systemErrorCorrection': 'System error correction',
                'initialStockEntry': 'Initial stock entry',
                'returnToVendor': 'Return to vendor',
                'customerReturnResalable': 'Customer return - resalable',
                'customerReturnDamaged': 'Customer return - damaged',
                'other': 'Other'
            }
        }
    },
    'el': {
        'failedToFetchParts': 'Αποτυχία φόρτωσης ανταλλακτικών',
        'quantityMustBeValid': 'Η αλλαγή ποσότητας πρέπει να είναι έγκυρος αριθμός',
        'cannotReduceStock': 'Δεν είναι δυνατή η μείωση του αποθέματος κατά {{quantity}}. Τρέχον απόθεμα: {{currentStock}}',
        'failedToCreateAdjustment': 'Αποτυχία δημιουργίας προσαρμογής',
        'unknownWarehouse': 'Άγνωστη Αποθήκη',
        'stockAdjustmentForm': {
            'title': 'Προσαρμογή Αποθέματος',
            'searchParts': 'Αναζήτηση Ανταλλακτικών',
            'searchPlaceholder': 'Αναζήτηση με αριθμό ή όνομα ανταλλακτικού...',
            'part': 'Ανταλλακτικό',
            'selectPart': 'Επιλέξτε ανταλλακτικό',
            'current': 'Τρέχον',
            'currentStock': 'Τρέχον Απόθεμα',
            'quantityChange': 'Αλλαγή Ποσότητας',
            'quantityPlaceholder': 'Εισάγετε θετικό για αύξηση, αρνητικό για μείωση',
            'quantityHint': 'Χρησιμοποιήστε θετικούς αριθμούς για αύξηση αποθέματος, αρνητικούς για μείωση',
            'newStockLevel': 'Το νέο επίπεδο αποθέματος θα είναι',
            'reason': 'Αιτία',
            'selectReason': 'Επιλέξτε αιτία',
            'notes': 'Σημειώσεις',
            'notesPlaceholder': 'Προαιρετικές πρόσθετες λεπτομέρειες για αυτήν την προσαρμογή...',
            'creatingAdjustment': 'Δημιουργία Προσαρμογής...',
            'createAdjustment': 'Δημιουργία Προσαρμογής',
            'reasons': {
                'stocktakeAdjustment': 'Προσαρμογή απογραφής',
                'damagedGoods': 'Κατεστραμμένα προϊόντα',
                'expiredItems': 'Ληγμένα προϊόντα',
                'foundItems': 'Βρεθέντα προϊόντα',
                'lostItems': 'Χαμένα προϊόντα',
                'transferCorrection': 'Διόρθωση μεταφοράς',
                'systemErrorCorrection': 'Διόρθωση σφάλματος συστήματος',
                'initialStockEntry': 'Αρχική καταχώριση αποθέματος',
                'returnToVendor': 'Επιστροφή στον προμηθευτή',
                'customerReturnResalable': 'Επιστροφή πελάτη - επαναπωλήσιμο',
                'customerReturnDamaged': 'Επιστροφή πελάτη - κατεστραμμένο',
                'other': 'Άλλο'
            }
        }
    },
    'ar': {
        'failedToFetchParts': 'فشل تحميل القطع',
        'quantityMustBeValid': 'يجب أن يكون تغيير الكمية رقمًا صالحًا',
        'cannotReduceStock': 'لا يمكن تقليل المخزون بمقدار {{quantity}}. المخزون الحالي: {{currentStock}}',
        'failedToCreateAdjustment': 'فشل إنشاء التعديل',
        'unknownWarehouse': 'مستودع غير معروف',
        'stockAdjustmentForm': {
            'title': 'تعديل المخزون',
            'searchParts': 'البحث عن القطع',
            'searchPlaceholder': 'البحث برقم أو اسم القطعة...',
            'part': 'القطعة',
            'selectPart': 'اختر قطعة',
            'current': 'الحالي',
            'currentStock': 'المخزون الحالي',
            'quantityChange': 'تغيير الكمية',
            'quantityPlaceholder': 'أدخل رقمًا موجبًا للزيادة، سالبًا للنقصان',
            'quantityHint': 'استخدم أرقامًا موجبة لزيادة المخزون، وأرقامًا سالبة للنقصان',
            'newStockLevel': 'سيكون مستوى المخزون الجديد',
            'reason': 'السبب',
            'selectReason': 'اختر سببًا',
            'notes': 'ملاحظات',
            'notesPlaceholder': 'تفاصيل إضافية اختيارية حول هذا التعديل...',
            'creatingAdjustment': 'جاري إنشاء التعديل...',
            'createAdjustment': 'إنشاء التعديل',
            'reasons': {
                'stocktakeAdjustment': 'تعديل الجرد',
                'damagedGoods': 'بضائع تالفة',
                'expiredItems': 'عناصر منتهية الصلاحية',
                'foundItems': 'عناصر تم العثور عليها',
                'lostItems': 'عناصر مفقودة',
                'transferCorrection': 'تصحيح النقل',
                'systemErrorCorrection': 'تصحيح خطأ النظام',
                'initialStockEntry': 'إدخال المخزون الأولي',
                'returnToVendor': 'إرجاع إلى المورد',
                'customerReturnResalable': 'إرجاع العميل - قابل لإعادة البيع',
                'customerReturnDamaged': 'إرجاع العميل - تالف',
                'other': 'أخرى'
            }
        }
    },
    'es': {
        'failedToFetchParts': 'Error al cargar piezas',
        'quantityMustBeValid': 'El cambio de cantidad debe ser un número válido',
        'cannotReduceStock': 'No se puede reducir el stock en {{quantity}}. Stock actual: {{currentStock}}',
        'failedToCreateAdjustment': 'Error al crear ajuste',
        'unknownWarehouse': 'Almacén Desconocido',
        'stockAdjustmentForm': {
            'title': 'Ajuste de Stock',
            'searchParts': 'Buscar Piezas',
            'searchPlaceholder': 'Buscar por número o nombre de pieza...',
            'part': 'Pieza',
            'selectPart': 'Seleccionar una pieza',
            'current': 'Actual',
            'currentStock': 'Stock Actual',
            'quantityChange': 'Cambio de Cantidad',
            'quantityPlaceholder': 'Ingrese positivo para aumentar, negativo para disminuir',
            'quantityHint': 'Use números positivos para aumentar el inventario, negativos para disminuir',
            'newStockLevel': 'El nuevo nivel de stock será',
            'reason': 'Razón',
            'selectReason': 'Seleccionar una razón',
            'notes': 'Notas',
            'notesPlaceholder': 'Detalles adicionales opcionales sobre este ajuste...',
            'creatingAdjustment': 'Creando Ajuste...',
            'createAdjustment': 'Crear Ajuste',
            'reasons': {
                'stocktakeAdjustment': 'Ajuste de inventario',
                'damagedGoods': 'Mercancías dañadas',
                'expiredItems': 'Artículos vencidos',
                'foundItems': 'Artículos encontrados',
                'lostItems': 'Artículos perdidos',
                'transferCorrection': 'Corrección de transferencia',
                'systemErrorCorrection': 'Corrección de error del sistema',
                'initialStockEntry': 'Entrada de stock inicial',
                'returnToVendor': 'Devolución al proveedor',
                'customerReturnResalable': 'Devolución del cliente - revendible',
                'customerReturnDamaged': 'Devolución del cliente - dañado',
                'other': 'Otro'
            }
        }
    },
    'tr': {
        'failedToFetchParts': 'Parçalar yüklenemedi',
        'quantityMustBeValid': 'Miktar değişikliği geçerli bir sayı olmalıdır',
        'cannotReduceStock': 'Stok {{quantity}} kadar azaltılamaz. Mevcut stok: {{currentStock}}',
        'failedToCreateAdjustment': 'Ayarlama oluşturulamadı',
        'unknownWarehouse': 'Bilinmeyen Depo',
        'stockAdjustmentForm': {
            'title': 'Stok Ayarlaması',
            'searchParts': 'Parça Ara',
            'searchPlaceholder': 'Parça numarası veya adıyla ara...',
            'part': 'Parça',
            'selectPart': 'Bir parça seçin',
            'current': 'Mevcut',
            'currentStock': 'Mevcut Stok',
            'quantityChange': 'Miktar Değişikliği',
            'quantityPlaceholder': 'Artış için pozitif, azalış için negatif girin',
            'quantityHint': 'Envanteri artırmak için pozitif, azaltmak için negatif sayılar kullanın',
            'newStockLevel': 'Yeni stok seviyesi olacak',
            'reason': 'Sebep',
            'selectReason': 'Bir sebep seçin',
            'notes': 'Notlar',
            'notesPlaceholder': 'Bu ayarlama hakkında isteğe bağlı ek ayrıntılar...',
            'creatingAdjustment': 'Ayarlama Oluşturuluyor...',
            'createAdjustment': 'Ayarlama Oluştur',
            'reasons': {
                'stocktakeAdjustment': 'Stok sayımı ayarlaması',
                'damagedGoods': 'Hasarlı mallar',
                'expiredItems': 'Süresi dolmuş ürünler',
                'foundItems': 'Bulunan ürünler',
                'lostItems': 'Kayıp ürünler',
                'transferCorrection': 'Transfer düzeltmesi',
                'systemErrorCorrection': 'Sistem hatası düzeltmesi',
                'initialStockEntry': 'İlk stok girişi',
                'returnToVendor': 'Satıcıya iade',
                'customerReturnResalable': 'Müşteri iadesi - yeniden satılabilir',
                'customerReturnDamaged': 'Müşteri iadesi - hasarlı',
                'other': 'Diğer'
            }
        }
    },
    'no': {
        'failedToFetchParts': 'Kunne ikke laste deler',
        'quantityMustBeValid': 'Mengdeendring må være et gyldig tall',
        'cannotReduceStock': 'Kan ikke redusere lager med {{quantity}}. Nåværende lager: {{currentStock}}',
        'failedToCreateAdjustment': 'Kunne ikke opprette justering',
        'unknownWarehouse': 'Ukjent Lager',
        'stockAdjustmentForm': {
            'title': 'Lagerjustering',
            'searchParts': 'Søk Deler',
            'searchPlaceholder': 'Søk etter delenummer eller navn...',
            'part': 'Del',
            'selectPart': 'Velg en del',
            'current': 'Nåværende',
            'currentStock': 'Nåværende Lager',
            'quantityChange': 'Mengdeendring',
            'quantityPlaceholder': 'Skriv inn positivt for økning, negativt for reduksjon',
            'quantityHint': 'Bruk positive tall for å øke beholdning, negative for å redusere',
            'newStockLevel': 'Nytt lagernivå vil være',
            'reason': 'Årsak',
            'selectReason': 'Velg en årsak',
            'notes': 'Notater',
            'notesPlaceholder': 'Valgfrie tilleggsdetaljer om denne justeringen...',
            'creatingAdjustment': 'Oppretter Justering...',
            'createAdjustment': 'Opprett Justering',
            'reasons': {
                'stocktakeAdjustment': 'Varetelling justering',
                'damagedGoods': 'Skadede varer',
                'expiredItems': 'Utgåtte varer',
                'foundItems': 'Funnet varer',
                'lostItems': 'Tapte varer',
                'transferCorrection': 'Overføringskorreksjon',
                'systemErrorCorrection': 'Systemfeilkorreksjon',
                'initialStockEntry': 'Innledende lagerregistrering',
                'returnToVendor': 'Retur til leverandør',
                'customerReturnResalable': 'Kunderetur - videresalgbar',
                'customerReturnDamaged': 'Kunderetur - skadet',
                'other': 'Annet'
            }
        }
    }
}

# Add to each language file
for lang_code, form_translations in translations.items():
    file_path = f'frontend/src/locales/{lang_code}.json'
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Add to warehouses section
        if 'warehouses' not in data:
            data['warehouses'] = {}
        
        # Merge the new translations
        data['warehouses'].update(form_translations)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f'✓ Added Warehouse Stock Adjustment Form translations to {lang_code}.json')
    
    except Exception as e:
        print(f'✗ Error processing {lang_code}.json: {e}')

print('\n✅ Warehouse Stock Adjustment Form translations added successfully!')
