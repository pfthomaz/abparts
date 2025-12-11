#!/usr/bin/env python3
import json

# Missing Stock Reset translations
translations = {
    'en': {
        'addPartToList': 'Add Part to Adjustment List',
        'searchPlaceholder': 'Search by part number, name, or description...',
        'noPartsLoaded': 'No parts loaded. Check console for errors.',
        'partsAvailable': 'parts available for search',
        'stockAdjustments': 'Stock Adjustments',
        'parts': 'parts',
        'partNumber': 'Part Number',
        'partName': 'Part Name',
        'current': 'Current',
        'newQuantity': 'New Quantity',
        'actions': 'Actions',
        'noPartsInList': 'No parts in adjustment list. Use the search above to add parts.',
        'reason': 'Reason',
        'notes': 'Notes',
        'notesPlaceholder': 'Optional notes...',
        'summary': 'Summary',
        'partsToAdjust': 'Parts to adjust',
        'totalIncrease': 'Total increase',
        'totalDecrease': 'Total decrease',
        'units': 'units',
        'previewChanges': 'Preview Changes',
        'applying': 'Applying...',
        'applyStockReset': 'Apply Stock Reset',
        'confirmStockReset': 'Confirm Stock Reset',
        'aboutToAdjust': 'You are about to adjust',
        'in': 'in',
        'thisActionWill': 'This action will',
        'createAdjustmentTransactions': 'Create adjustment transactions for audit trail',
        'updateInventoryQuantities': 'Update inventory quantities',
        'logChanges': 'Log changes with reason and notes',
        'confirmReset': 'Confirm Reset',
        'reasons': {
            'initialStockEntry': 'Initial Stock Entry',
            'physicalStocktake': 'Physical Stocktake Correction',
            'systemReconciliation': 'System Reconciliation',
            'damagedGoods': 'Damaged Goods Write-off',
            'foundStock': 'Found Stock',
            'other': 'Other'
        }
    },
    'el': {
        'addPartToList': 'Προσθήκη Ανταλλακτικού στη Λίστα Προσαρμογών',
        'searchPlaceholder': 'Αναζήτηση με αριθμό, όνομα ή περιγραφή ανταλλακτικού...',
        'noPartsLoaded': 'Δεν φορτώθηκαν ανταλλακτικά. Ελέγξτε την κονσόλα για σφάλματα.',
        'partsAvailable': 'ανταλλακτικά διαθέσιμα για αναζήτηση',
        'stockAdjustments': 'Προσαρμογές Αποθέματος',
        'parts': 'ανταλλακτικά',
        'partNumber': 'Αριθμός Ανταλλακτικού',
        'partName': 'Όνομα Ανταλλακτικού',
        'current': 'Τρέχον',
        'newQuantity': 'Νέα Ποσότητα',
        'actions': 'Ενέργειες',
        'noPartsInList': 'Δεν υπάρχουν ανταλλακτικά στη λίστα προσαρμογών. Χρησιμοποιήστε την αναζήτηση παραπάνω για να προσθέσετε ανταλλακτικά.',
        'reason': 'Αιτία',
        'notes': 'Σημειώσεις',
        'notesPlaceholder': 'Προαιρετικές σημειώσεις...',
        'summary': 'Περίληψη',
        'partsToAdjust': 'Ανταλλακτικά προς προσαρμογή',
        'totalIncrease': 'Συνολική αύξηση',
        'totalDecrease': 'Συνολική μείωση',
        'units': 'μονάδες',
        'previewChanges': 'Προεπισκόπηση Αλλαγών',
        'applying': 'Εφαρμογή...',
        'applyStockReset': 'Εφαρμογή Επαναφοράς Αποθέματος',
        'confirmStockReset': 'Επιβεβαίωση Επαναφοράς Αποθέματος',
        'aboutToAdjust': 'Πρόκειται να προσαρμόσετε',
        'in': 'στο',
        'thisActionWill': 'Αυτή η ενέργεια θα',
        'createAdjustmentTransactions': 'Δημιουργήσει συναλλαγές προσαρμογής για έλεγχο',
        'updateInventoryQuantities': 'Ενημερώσει τις ποσότητες αποθέματος',
        'logChanges': 'Καταγράψει τις αλλαγές με αιτία και σημειώσεις',
        'confirmReset': 'Επιβεβαίωση Επαναφοράς',
        'reasons': {
            'initialStockEntry': 'Αρχική Καταχώριση Αποθέματος',
            'physicalStocktake': 'Διόρθωση Φυσικής Απογραφής',
            'systemReconciliation': 'Συμφωνία Συστήματος',
            'damagedGoods': 'Διαγραφή Κατεστραμμένων Προϊόντων',
            'foundStock': 'Βρεθέν Απόθεμα',
            'other': 'Άλλο'
        }
    },
    'ar': {
        'addPartToList': 'إضافة قطعة إلى قائمة التعديلات',
        'searchPlaceholder': 'البحث برقم أو اسم أو وصف القطعة...',
        'noPartsLoaded': 'لم يتم تحميل القطع. تحقق من وحدة التحكم للأخطاء.',
        'partsAvailable': 'قطع متاحة للبحث',
        'stockAdjustments': 'تعديلات المخزون',
        'parts': 'قطع',
        'partNumber': 'رقم القطعة',
        'partName': 'اسم القطعة',
        'current': 'الحالي',
        'newQuantity': 'الكمية الجديدة',
        'actions': 'الإجراءات',
        'noPartsInList': 'لا توجد قطع في قائمة التعديلات. استخدم البحث أعلاه لإضافة القطع.',
        'reason': 'السبب',
        'notes': 'ملاحظات',
        'notesPlaceholder': 'ملاحظات اختيارية...',
        'summary': 'ملخص',
        'partsToAdjust': 'القطع المراد تعديلها',
        'totalIncrease': 'إجمالي الزيادة',
        'totalDecrease': 'إجمالي النقصان',
        'units': 'وحدات',
        'previewChanges': 'معاينة التغييرات',
        'applying': 'جاري التطبيق...',
        'applyStockReset': 'تطبيق إعادة تعيين المخزون',
        'confirmStockReset': 'تأكيد إعادة تعيين المخزون',
        'aboutToAdjust': 'أنت على وشك تعديل',
        'in': 'في',
        'thisActionWill': 'سيقوم هذا الإجراء بـ',
        'createAdjustmentTransactions': 'إنشاء معاملات التعديل لسجل التدقيق',
        'updateInventoryQuantities': 'تحديث كميات المخزون',
        'logChanges': 'تسجيل التغييرات مع السبب والملاحظات',
        'confirmReset': 'تأكيد الإعادة',
        'reasons': {
            'initialStockEntry': 'إدخال المخزون الأولي',
            'physicalStocktake': 'تصحيح الجرد الفعلي',
            'systemReconciliation': 'تسوية النظام',
            'damagedGoods': 'شطب البضائع التالفة',
            'foundStock': 'مخزون تم العثور عليه',
            'other': 'أخرى'
        }
    },
    'es': {
        'addPartToList': 'Agregar Pieza a la Lista de Ajustes',
        'searchPlaceholder': 'Buscar por número, nombre o descripción de pieza...',
        'noPartsLoaded': 'No se cargaron piezas. Verifique la consola para errores.',
        'partsAvailable': 'piezas disponibles para búsqueda',
        'stockAdjustments': 'Ajustes de Stock',
        'parts': 'piezas',
        'partNumber': 'Número de Pieza',
        'partName': 'Nombre de Pieza',
        'current': 'Actual',
        'newQuantity': 'Nueva Cantidad',
        'actions': 'Acciones',
        'noPartsInList': 'No hay piezas en la lista de ajustes. Use la búsqueda arriba para agregar piezas.',
        'reason': 'Razón',
        'notes': 'Notas',
        'notesPlaceholder': 'Notas opcionales...',
        'summary': 'Resumen',
        'partsToAdjust': 'Piezas a ajustar',
        'totalIncrease': 'Aumento total',
        'totalDecrease': 'Disminución total',
        'units': 'unidades',
        'previewChanges': 'Vista Previa de Cambios',
        'applying': 'Aplicando...',
        'applyStockReset': 'Aplicar Reinicio de Stock',
        'confirmStockReset': 'Confirmar Reinicio de Stock',
        'aboutToAdjust': 'Está a punto de ajustar',
        'in': 'en',
        'thisActionWill': 'Esta acción',
        'createAdjustmentTransactions': 'Creará transacciones de ajuste para auditoría',
        'updateInventoryQuantities': 'Actualizará las cantidades de inventario',
        'logChanges': 'Registrará cambios con razón y notas',
        'confirmReset': 'Confirmar Reinicio',
        'reasons': {
            'initialStockEntry': 'Entrada de Stock Inicial',
            'physicalStocktake': 'Corrección de Inventario Físico',
            'systemReconciliation': 'Reconciliación del Sistema',
            'damagedGoods': 'Baja de Mercancías Dañadas',
            'foundStock': 'Stock Encontrado',
            'other': 'Otro'
        }
    },
    'tr': {
        'addPartToList': 'Ayarlama Listesine Parça Ekle',
        'searchPlaceholder': 'Parça numarası, adı veya açıklamasıyla ara...',
        'noPartsLoaded': 'Parçalar yüklenmedi. Hatalar için konsolu kontrol edin.',
        'partsAvailable': 'arama için mevcut parça',
        'stockAdjustments': 'Stok Ayarlamaları',
        'parts': 'parça',
        'partNumber': 'Parça Numarası',
        'partName': 'Parça Adı',
        'current': 'Mevcut',
        'newQuantity': 'Yeni Miktar',
        'actions': 'İşlemler',
        'noPartsInList': 'Ayarlama listesinde parça yok. Parça eklemek için yukarıdaki aramayı kullanın.',
        'reason': 'Sebep',
        'notes': 'Notlar',
        'notesPlaceholder': 'İsteğe bağlı notlar...',
        'summary': 'Özet',
        'partsToAdjust': 'Ayarlanacak parçalar',
        'totalIncrease': 'Toplam artış',
        'totalDecrease': 'Toplam azalış',
        'units': 'birim',
        'previewChanges': 'Değişiklikleri Önizle',
        'applying': 'Uygulanıyor...',
        'applyStockReset': 'Stok Sıfırlamayı Uygula',
        'confirmStockReset': 'Stok Sıfırlamayı Onayla',
        'aboutToAdjust': 'Ayarlamak üzeresiniz',
        'in': 'içinde',
        'thisActionWill': 'Bu işlem',
        'createAdjustmentTransactions': 'Denetim kaydı için ayarlama işlemleri oluşturacak',
        'updateInventoryQuantities': 'Envanter miktarlarını güncelleyecek',
        'logChanges': 'Değişiklikleri sebep ve notlarla kaydedecek',
        'confirmReset': 'Sıfırlamayı Onayla',
        'reasons': {
            'initialStockEntry': 'İlk Stok Girişi',
            'physicalStocktake': 'Fiziksel Stok Sayımı Düzeltmesi',
            'systemReconciliation': 'Sistem Mutabakatı',
            'damagedGoods': 'Hasarlı Mal Silme',
            'foundStock': 'Bulunan Stok',
            'other': 'Diğer'
        }
    },
    'no': {
        'addPartToList': 'Legg til Del i Justeringsliste',
        'searchPlaceholder': 'Søk etter delenummer, navn eller beskrivelse...',
        'noPartsLoaded': 'Ingen deler lastet. Sjekk konsollen for feil.',
        'partsAvailable': 'deler tilgjengelig for søk',
        'stockAdjustments': 'Lagerjusteringer',
        'parts': 'deler',
        'partNumber': 'Delenummer',
        'partName': 'Delenavn',
        'current': 'Nåværende',
        'newQuantity': 'Ny Mengde',
        'actions': 'Handlinger',
        'noPartsInList': 'Ingen deler i justeringslisten. Bruk søket ovenfor for å legge til deler.',
        'reason': 'Årsak',
        'notes': 'Notater',
        'notesPlaceholder': 'Valgfrie notater...',
        'summary': 'Sammendrag',
        'partsToAdjust': 'Deler å justere',
        'totalIncrease': 'Total økning',
        'totalDecrease': 'Total reduksjon',
        'units': 'enheter',
        'previewChanges': 'Forhåndsvis Endringer',
        'applying': 'Bruker...',
        'applyStockReset': 'Bruk Lagertilbakestilling',
        'confirmStockReset': 'Bekreft Lagertilbakestilling',
        'aboutToAdjust': 'Du er i ferd med å justere',
        'in': 'i',
        'thisActionWill': 'Denne handlingen vil',
        'createAdjustmentTransactions': 'Opprette justeringstransaksjoner for revisjonsspor',
        'updateInventoryQuantities': 'Oppdatere lagermengder',
        'logChanges': 'Logge endringer med årsak og notater',
        'confirmReset': 'Bekreft Tilbakestilling',
        'reasons': {
            'initialStockEntry': 'Innledende Lagerregistrering',
            'physicalStocktake': 'Fysisk Varetelling Korreksjon',
            'systemReconciliation': 'Systemavstemmelse',
            'damagedGoods': 'Avskrivning av Skadede Varer',
            'foundStock': 'Funnet Lager',
            'other': 'Annet'
        }
    }
}

# Add to each language file under warehouses.stockReset
for lang_code, reset_translations in translations.items():
    file_path = f'frontend/src/locales/{lang_code}.json'
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Ensure warehouses section exists
        if 'warehouses' not in data:
            data['warehouses'] = {}
        
        # Add stockReset section
        data['warehouses']['stockReset'] = reset_translations
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f'✓ Added Stock Reset translations to {lang_code}.json')
    
    except Exception as e:
        print(f'✗ Error processing {lang_code}.json: {e}')

print('\n✅ Stock Reset missing translations added successfully!')
