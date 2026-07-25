#!/usr/bin/env python3
"""Add warehouse QR location translations to all non-English locale files."""
import json
import os

LOCALES_DIR = "/Users/diogothomaz/dev/abparts/frontend/src/locales"

# Define all translations per language
TRANSLATIONS = {}

# Greek (el)
TRANSLATIONS["el"] = {
    "mobileNav_scan": "Σάρωση",
    "warehouseLocations": {
        "title": "Τοποθεσίες Αποθήκης",
        "subtitle": "Διαχείριση θέσεων ραφιών και αντιστοιχίσεων ανταλλακτικών",
        "backToWarehouses": "Πίσω στις Αποθήκες",
        "addLocation": "Προσθήκη Τοποθεσίας",
        "editLocation": "Επεξεργασία Τοποθεσίας",
        "deleteLocation": "Διαγραφή Τοποθεσίας",
        "locationCode": "Κωδικός Τοποθεσίας",
        "description": "Περιγραφή",
        "descriptionPlaceholder": "Προαιρετική περιγραφή για αυτή τη θέση...",
        "locationCodeRequired": "Ο κωδικός τοποθεσίας είναι υποχρεωτικός",
        "totalLocations": "Σύνολο Τοποθεσιών",
        "occupied": "Κατειλημμένες",
        "empty": "Κενές",
        "noLocations": "Χωρίς Τοποθεσίες",
        "noLocationsDescription": "Δεν έχουν οριστεί τοποθεσίες για αυτή την αποθήκη.",
        "parts": "Ανταλλακτικά",
        "noDescription": "Χωρίς περιγραφή",
        "deleteConfirmation": "Είστε βέβαιοι ότι θέλετε να διαγράψετε αυτή τη θέση;",
        "deleteWarningHasParts": "Αυτή η θέση έχει ανταλλακτικά. Θα αποσυνδεθούν.",
        "printLabels": "Εκτύπωση Ετικετών",
        "printSelected": "Εκτύπωση Επιλεγμένων",
        "printAll": "Εκτύπωση Όλων",
        "selectAll": "Επιλογή Όλων",
        "selected": "επιλεγμένα",
        "generating": "Δημιουργία...",
        "whereIsThis": "Πού είναι αυτό;",
        "noLocationAssigned": "Δεν έχει αντιστοιχιστεί θέση",
        "currentLocations": "Τρέχουσες Τοποθεσίες",
        "assignToLocation": "Αντιστοίχιση σε Θέση",
        "selectLocation": "Επιλογή Θέσης",
        "noLocationsAvailable": "Δεν υπάρχουν διαθέσιμες θέσεις",
        "assign": "Αντιστοίχιση",
        "assignAll": "Αντιστοίχιση Όλων",
        "removeLocation": "Αφαίρεση Θέσης",
        "bulkAssignTitle": "Μαζική Αντιστοίχιση σε Θέση",
        "bulkAssignDescription": "Αντιστοίχιση επιλεγμένων ανταλλακτικών σε θέση",
        "bulkAssignSuccess": "Τα ανταλλακτικά αντιστοιχίστηκαν επιτυχώς",
        "noPartsSelected": "Δεν επιλέχθηκαν ανταλλακτικά",
        "partsSelected": "ανταλλακτικά επιλεγμένα",
        "errorLoadingLocations": "Σφάλμα φόρτωσης τοποθεσιών",
        "errorAssigning": "Σφάλμα αντιστοίχισης ανταλλακτικού",
        "errorUnassigning": "Σφάλμα αφαίρεσης ανταλλακτικού",
        "errorBulkAssign": "Σφάλμα μαζικής αντιστοίχισης"
    },
    "qrScanner": {
        "title": "Σαρωτής QR",
        "scanTitle": "Σάρωση Κωδικού QR",
        "comingSoon": "Σύντομα Διαθέσιμο",
        "permissionDenied": "Η πρόσβαση στην κάμερα απορρίφθηκε",
        "noCameraFound": "Δεν βρέθηκε κάμερα",
        "initError": "Σφάλμα εκκίνησης σαρωτή",
        "cameraBlocked": "Η πρόσβαση στην κάμερα είναι αποκλεισμένη",
        "tryAgain": "Δοκιμάστε Ξανά",
        "scannerError": "Σφάλμα σαρωτή",
        "initializing": "Εκκίνηση κάμερας...",
        "allowCamera": "Επιτρέψτε πρόσβαση στην κάμερα για σάρωση κωδικών QR",
        "scanHint": "Στρέψτε την κάμερα σε κωδικό QR τοποθεσίας",
        "invalidQr": "Μη έγκυρος κωδικός QR",
        "lastScanned": "Τελευταία σάρωση",
        "orManualEntry": "Ή εισάγετε χειροκίνητα",
        "warehouseId": "ID Αποθήκης",
        "warehouseIdPlaceholder": "Εισάγετε ID αποθήκης...",
        "locationCode": "Κωδικός Τοποθεσίας",
        "locationCodePlaceholder": "Εισάγετε κωδικό τοποθεσίας...",
        "goToLocation": "Μετάβαση στη Θέση",
        "enterWarehouseId": "Εισάγετε ID αποθήκης",
        "cameraPlaceholder": "Η προεπισκόπηση κάμερας θα εμφανιστεί εδώ"
    },
    "locationDetail": {
        "title": "Λεπτομέρειες Τοποθεσίας",
        "notFound": "Η Τοποθεσία Δεν Βρέθηκε",
        "error": "Σφάλμα",
        "notFoundDescription": "Αυτή η τοποθεσία δεν υπάρχει ή έχει αφαιρεθεί.",
        "errorDescription": "Παρουσιάστηκε σφάλμα κατά τη φόρτωση.",
        "scanAnother": "Σάρωση Άλλου",
        "locationCode": "Κωδικός Τοποθεσίας",
        "partsHere": "Ανταλλακτικά σε αυτή τη θέση",
        "part": "ανταλλακτικό",
        "parts": "ανταλλακτικά",
        "qty": "Ποσ.",
        "noParts": "Χωρίς Ανταλλακτικά",
        "noPartsDescription": "Δεν υπάρχουν ανταλλακτικά σε αυτή τη θέση."
    },
    "pickList": {
        "title": "Λίστα Συλλογής",
        "startPicking": "Έναρξη Συλλογής",
        "progress": "Πρόοδος",
        "itemsPicked": "αντικείμενα συλλέχθηκαν",
        "allPicked": "Όλα τα αντικείμενα συλλέχθηκαν!",
        "orderReady": "Η παραγγελία είναι έτοιμη για συσκευασία",
        "done": "Ολοκλήρωση",
        "noItems": "Δεν υπάρχουν αντικείμενα",
        "noLocation": "\u2014",
        "loadingLocations": "Φόρτωση τοποθεσιών...",
        "markPicked": "Σημείωση ως συλλεγμένο",
        "unmarkPicked": "Αναίρεση σημείωσης"
    }
}

print("Greek translations defined")

# Arabic (ar)
TRANSLATIONS["ar"] = {
    "mobileNav_scan": "مسح",
    "warehouseLocations": {
        "title": "مواقع المستودع",
        "subtitle": "إدارة مواقع الرفوف وتعيينات القطع",
        "backToWarehouses": "العودة إلى المستودعات",
        "addLocation": "إضافة موقع",
        "editLocation": "تعديل الموقع",
        "deleteLocation": "حذف الموقع",
        "locationCode": "رمز الموقع",
        "description": "الوصف",
        "descriptionPlaceholder": "وصف اختياري لهذا الموقع...",
        "locationCodeRequired": "رمز الموقع مطلوب",
        "totalLocations": "إجمالي المواقع",
        "occupied": "مشغولة",
        "empty": "فارغة",
        "noLocations": "لا توجد مواقع",
        "noLocationsDescription": "لم يتم تحديد مواقع لهذا المستودع بعد.",
        "parts": "القطع",
        "noDescription": "بدون وصف",
        "deleteConfirmation": "هل أنت متأكد من حذف هذا الموقع؟",
        "deleteWarningHasParts": "هذا الموقع يحتوي على قطع. سيتم إلغاء تعيينها.",
        "printLabels": "طباعة الملصقات",
        "printSelected": "طباعة المحدد",
        "printAll": "طباعة الكل",
        "selectAll": "تحديد الكل",
        "selected": "محدد",
        "generating": "جارٍ الإنشاء...",
        "whereIsThis": "أين هذا؟",
        "noLocationAssigned": "لم يتم تعيين موقع",
        "currentLocations": "المواقع الحالية",
        "assignToLocation": "تعيين إلى موقع",
        "selectLocation": "اختر الموقع",
        "noLocationsAvailable": "لا توجد مواقع متاحة",
        "assign": "تعيين",
        "assignAll": "تعيين الكل",
        "removeLocation": "إزالة الموقع",
        "bulkAssignTitle": "تعيين جماعي إلى موقع",
        "bulkAssignDescription": "تعيين القطع المحددة إلى موقع",
        "bulkAssignSuccess": "تم تعيين القطع بنجاح",
        "noPartsSelected": "لم يتم تحديد قطع",
        "partsSelected": "قطع محددة",
        "errorLoadingLocations": "خطأ في تحميل المواقع",
        "errorAssigning": "خطأ في تعيين القطعة",
        "errorUnassigning": "خطأ في إزالة القطعة",
        "errorBulkAssign": "خطأ في التعيين الجماعي"
    },
    "qrScanner": {
        "title": "ماسح QR",
        "scanTitle": "مسح رمز QR",
        "comingSoon": "قريباً",
        "permissionDenied": "تم رفض إذن الكاميرا",
        "noCameraFound": "لم يتم العثور على كاميرا",
        "initError": "خطأ في تهيئة الماسح",
        "cameraBlocked": "الوصول إلى الكاميرا محظور",
        "tryAgain": "حاول مرة أخرى",
        "scannerError": "خطأ في الماسح",
        "initializing": "جارٍ تهيئة الكاميرا...",
        "allowCamera": "يرجى السماح بالوصول إلى الكاميرا لمسح رموز QR",
        "scanHint": "وجّه الكاميرا نحو رمز QR الموقع",
        "invalidQr": "رمز QR غير صالح",
        "lastScanned": "آخر مسح",
        "orManualEntry": "أو أدخل يدوياً",
        "warehouseId": "معرف المستودع",
        "warehouseIdPlaceholder": "أدخل معرف المستودع...",
        "locationCode": "رمز الموقع",
        "locationCodePlaceholder": "أدخل رمز الموقع...",
        "goToLocation": "الذهاب إلى الموقع",
        "enterWarehouseId": "أدخل معرف المستودع",
        "cameraPlaceholder": "ستظهر معاينة الكاميرا هنا"
    },
    "locationDetail": {
        "title": "تفاصيل الموقع",
        "notFound": "الموقع غير موجود",
        "error": "خطأ",
        "notFoundDescription": "هذا الموقع غير موجود أو تمت إزالته.",
        "errorDescription": "حدث خطأ أثناء تحميل التفاصيل.",
        "scanAnother": "مسح آخر",
        "locationCode": "رمز الموقع",
        "partsHere": "القطع في هذا الموقع",
        "part": "قطعة",
        "parts": "قطع",
        "qty": "الكمية",
        "noParts": "لا توجد قطع",
        "noPartsDescription": "لا توجد قطع معينة لهذا الموقع حالياً."
    },
    "pickList": {
        "title": "قائمة الجمع",
        "startPicking": "بدء الجمع",
        "progress": "التقدم",
        "itemsPicked": "عناصر تم جمعها",
        "allPicked": "تم جمع جميع العناصر!",
        "orderReady": "الطلب جاهز للتغليف",
        "done": "تم",
        "noItems": "لا توجد عناصر للجمع",
        "noLocation": "\u2014",
        "loadingLocations": "جارٍ تحميل المواقع...",
        "markPicked": "تحديد كمجموع",
        "unmarkPicked": "إلغاء التحديد"
    }
}

print("Arabic translations defined")

# Spanish (es)
TRANSLATIONS["es"] = {
    "mobileNav_scan": "Escanear",
    "warehouseLocations": {
        "title": "Ubicaciones del Almacén",
        "subtitle": "Gestionar ubicaciones de estantes y asignaciones de piezas",
        "backToWarehouses": "Volver a Almacenes",
        "addLocation": "Agregar Ubicación",
        "editLocation": "Editar Ubicación",
        "deleteLocation": "Eliminar Ubicación",
        "locationCode": "Código de Ubicación",
        "description": "Descripción",
        "descriptionPlaceholder": "Descripción opcional para esta ubicación...",
        "locationCodeRequired": "El código de ubicación es obligatorio",
        "totalLocations": "Total de Ubicaciones",
        "occupied": "Ocupadas",
        "empty": "Vacías",
        "noLocations": "Sin Ubicaciones",
        "noLocationsDescription": "No se han definido ubicaciones para este almacén.",
        "parts": "Piezas",
        "noDescription": "Sin descripción",
        "deleteConfirmation": "¿Está seguro de que desea eliminar esta ubicación?",
        "deleteWarningHasParts": "Esta ubicación tiene piezas asignadas. Serán desasignadas.",
        "printLabels": "Imprimir Etiquetas",
        "printSelected": "Imprimir Seleccionadas",
        "printAll": "Imprimir Todas",
        "selectAll": "Seleccionar Todo",
        "selected": "seleccionadas",
        "generating": "Generando...",
        "whereIsThis": "¿Dónde está esto?",
        "noLocationAssigned": "Sin ubicación asignada",
        "currentLocations": "Ubicaciones Actuales",
        "assignToLocation": "Asignar a Ubicación",
        "selectLocation": "Seleccionar Ubicación",
        "noLocationsAvailable": "No hay ubicaciones disponibles",
        "assign": "Asignar",
        "assignAll": "Asignar Todo",
        "removeLocation": "Quitar Ubicación",
        "bulkAssignTitle": "Asignación Masiva a Ubicación",
        "bulkAssignDescription": "Asignar piezas seleccionadas a una ubicación",
        "bulkAssignSuccess": "Piezas asignadas exitosamente",
        "noPartsSelected": "No hay piezas seleccionadas",
        "partsSelected": "piezas seleccionadas",
        "errorLoadingLocations": "Error al cargar ubicaciones",
        "errorAssigning": "Error al asignar pieza",
        "errorUnassigning": "Error al quitar pieza",
        "errorBulkAssign": "Error en asignación masiva"
    },
    "qrScanner": {
        "title": "Escáner QR",
        "scanTitle": "Escanear Código QR",
        "comingSoon": "Próximamente",
        "permissionDenied": "Permiso de cámara denegado",
        "noCameraFound": "No se encontró cámara",
        "initError": "Error al inicializar el escáner",
        "cameraBlocked": "El acceso a la cámara está bloqueado",
        "tryAgain": "Intentar de Nuevo",
        "scannerError": "Error del escáner",
        "initializing": "Inicializando cámara...",
        "allowCamera": "Permita el acceso a la cámara para escanear códigos QR",
        "scanHint": "Apunte la cámara a un código QR de ubicación",
        "invalidQr": "Código QR no válido",
        "lastScanned": "Último escaneo",
        "orManualEntry": "O ingrese manualmente",
        "warehouseId": "ID del Almacén",
        "warehouseIdPlaceholder": "Ingrese ID del almacén...",
        "locationCode": "Código de Ubicación",
        "locationCodePlaceholder": "Ingrese código de ubicación...",
        "goToLocation": "Ir a Ubicación",
        "enterWarehouseId": "Ingrese ID del almacén",
        "cameraPlaceholder": "La vista previa de la cámara aparecerá aquí"
    },
    "locationDetail": {
        "title": "Detalle de Ubicación",
        "notFound": "Ubicación No Encontrada",
        "error": "Error",
        "notFoundDescription": "Esta ubicación no existe o ha sido eliminada.",
        "errorDescription": "Ocurrió un error al cargar los detalles.",
        "scanAnother": "Escanear Otro",
        "locationCode": "Código de Ubicación",
        "partsHere": "Piezas en esta ubicación",
        "part": "pieza",
        "parts": "piezas",
        "qty": "Cant.",
        "noParts": "Sin Piezas",
        "noPartsDescription": "No hay piezas asignadas a esta ubicación actualmente."
    },
    "pickList": {
        "title": "Lista de Recolección",
        "startPicking": "Iniciar Recolección",
        "progress": "Progreso",
        "itemsPicked": "artículos recolectados",
        "allPicked": "¡Todos los artículos recolectados!",
        "orderReady": "El pedido está listo para empacar",
        "done": "Listo",
        "noItems": "No hay artículos para recolectar",
        "noLocation": "\u2014",
        "loadingLocations": "Cargando ubicaciones...",
        "markPicked": "Marcar como recolectado",
        "unmarkPicked": "Desmarcar"
    }
}

print("Spanish translations defined")

# Norwegian (no)
TRANSLATIONS["no"] = {
    "mobileNav_scan": "Skann",
    "warehouseLocations": {
        "title": "Lagerlokasjon",
        "subtitle": "Administrer hylleplasseringer og deler",
        "backToWarehouses": "Tilbake til Lagre",
        "addLocation": "Legg til Lokasjon",
        "editLocation": "Rediger Lokasjon",
        "deleteLocation": "Slett Lokasjon",
        "locationCode": "Lokasjonskode",
        "description": "Beskrivelse",
        "descriptionPlaceholder": "Valgfri beskrivelse for denne lokasjonen...",
        "locationCodeRequired": "Lokasjonskode er påkrevd",
        "totalLocations": "Totalt Lokasjoner",
        "occupied": "Opptatt",
        "empty": "Ledig",
        "noLocations": "Ingen Lokasjoner",
        "noLocationsDescription": "Ingen lokasjoner er definert for dette lageret ennå.",
        "parts": "Deler",
        "noDescription": "Ingen beskrivelse",
        "deleteConfirmation": "Er du sikker på at du vil slette denne lokasjonen?",
        "deleteWarningHasParts": "Denne lokasjonen har deler tilordnet. De vil bli fjernet.",
        "printLabels": "Skriv ut Etiketter",
        "printSelected": "Skriv ut Valgte",
        "printAll": "Skriv ut Alle",
        "selectAll": "Velg Alle",
        "selected": "valgt",
        "generating": "Genererer...",
        "whereIsThis": "Hvor er dette?",
        "noLocationAssigned": "Ingen lokasjon tilordnet",
        "currentLocations": "Nåværende Lokasjoner",
        "assignToLocation": "Tilordne til Lokasjon",
        "selectLocation": "Velg Lokasjon",
        "noLocationsAvailable": "Ingen lokasjoner tilgjengelig",
        "assign": "Tilordne",
        "assignAll": "Tilordne Alle",
        "removeLocation": "Fjern Lokasjon",
        "bulkAssignTitle": "Massetilordning til Lokasjon",
        "bulkAssignDescription": "Tilordne valgte deler til en lokasjon",
        "bulkAssignSuccess": "Deler tilordnet",
        "noPartsSelected": "Ingen deler valgt",
        "partsSelected": "deler valgt",
        "errorLoadingLocations": "Feil ved lasting av lokasjoner",
        "errorAssigning": "Feil ved tilordning av del",
        "errorUnassigning": "Feil ved fjerning av del",
        "errorBulkAssign": "Feil ved massetilordning"
    },
    "qrScanner": {
        "title": "QR-skanner",
        "scanTitle": "Skann QR-kode",
        "comingSoon": "Kommer Snart",
        "permissionDenied": "Kameratilgang nektet",
        "noCameraFound": "Ingen kamera funnet",
        "initError": "Feil ved initialisering av skanner",
        "cameraBlocked": "Kameratilgang er blokkert",
        "tryAgain": "Prøv Igjen",
        "scannerError": "Skannerfeil",
        "initializing": "Initialiserer kamera...",
        "allowCamera": "Tillat kameratilgang for å skanne QR-koder",
        "scanHint": "Pek kameraet mot en lokasjons-QR-kode",
        "invalidQr": "Ugyldig QR-kode",
        "lastScanned": "Sist skannet",
        "orManualEntry": "Eller skriv inn manuelt",
        "warehouseId": "Lager-ID",
        "warehouseIdPlaceholder": "Skriv inn lager-ID...",
        "locationCode": "Lokasjonskode",
        "locationCodePlaceholder": "Skriv inn lokasjonskode...",
        "goToLocation": "Gå til Lokasjon",
        "enterWarehouseId": "Skriv inn lager-ID",
        "cameraPlaceholder": "Kameraforhåndsvisning vises her"
    },
    "locationDetail": {
        "title": "Lokasjonsdetaljer",
        "notFound": "Lokasjon Ikke Funnet",
        "error": "Feil",
        "notFoundDescription": "Denne lokasjonen eksisterer ikke eller er fjernet.",
        "errorDescription": "En feil oppstod under lasting av detaljer.",
        "scanAnother": "Skann En Annen",
        "locationCode": "Lokasjonskode",
        "partsHere": "Deler på denne lokasjonen",
        "part": "del",
        "parts": "deler",
        "qty": "Ant.",
        "noParts": "Ingen Deler",
        "noPartsDescription": "Ingen deler er tilordnet denne lokasjonen."
    },
    "pickList": {
        "title": "Plukkliste",
        "startPicking": "Start Plukking",
        "progress": "Fremdrift",
        "itemsPicked": "artikler plukket",
        "allPicked": "Alle artikler plukket!",
        "orderReady": "Bestillingen er klar for pakking",
        "done": "Ferdig",
        "noItems": "Ingen artikler å plukke",
        "noLocation": "\u2014",
        "loadingLocations": "Laster lokasjoner...",
        "markPicked": "Merk som plukket",
        "unmarkPicked": "Fjern merking"
    }
}

print("Norwegian translations defined")

# Turkish (tr)
TRANSLATIONS["tr"] = {
    "mobileNav_scan": "Tara",
    "warehouseLocations": {
        "title": "Depo Konumları",
        "subtitle": "Raf konumlarını ve parça atamalarını yönet",
        "backToWarehouses": "Depolara Dön",
        "addLocation": "Konum Ekle",
        "editLocation": "Konumu Düzenle",
        "deleteLocation": "Konumu Sil",
        "locationCode": "Konum Kodu",
        "description": "Açıklama",
        "descriptionPlaceholder": "Bu konum için isteğe bağlı açıklama...",
        "locationCodeRequired": "Konum kodu gereklidir",
        "totalLocations": "Toplam Konum",
        "occupied": "Dolu",
        "empty": "Boş",
        "noLocations": "Konum Yok",
        "noLocationsDescription": "Bu depo için henüz konum tanımlanmamış.",
        "parts": "Parçalar",
        "noDescription": "Açıklama yok",
        "deleteConfirmation": "Bu konumu silmek istediğinizden emin misiniz?",
        "deleteWarningHasParts": "Bu konumda parçalar var. Atamaları kaldırılacak.",
        "printLabels": "Etiket Yazdır",
        "printSelected": "Seçilenleri Yazdır",
        "printAll": "Tümünü Yazdır",
        "selectAll": "Tümünü Seç",
        "selected": "seçili",
        "generating": "Oluşturuluyor...",
        "whereIsThis": "Bu nerede?",
        "noLocationAssigned": "Konum atanmamış",
        "currentLocations": "Mevcut Konumlar",
        "assignToLocation": "Konuma Ata",
        "selectLocation": "Konum Seç",
        "noLocationsAvailable": "Kullanılabilir konum yok",
        "assign": "Ata",
        "assignAll": "Tümünü Ata",
        "removeLocation": "Konumu Kaldır",
        "bulkAssignTitle": "Toplu Konum Atama",
        "bulkAssignDescription": "Seçili parçaları bir konuma ata",
        "bulkAssignSuccess": "Parçalar başarıyla atandı",
        "noPartsSelected": "Parça seçilmedi",
        "partsSelected": "parça seçili",
        "errorLoadingLocations": "Konumlar yüklenirken hata",
        "errorAssigning": "Parça atanırken hata",
        "errorUnassigning": "Parça kaldırılırken hata",
        "errorBulkAssign": "Toplu atama hatası"
    },
    "qrScanner": {
        "title": "QR Tarayıcı",
        "scanTitle": "QR Kod Tara",
        "comingSoon": "Yakında",
        "permissionDenied": "Kamera izni reddedildi",
        "noCameraFound": "Kamera bulunamadı",
        "initError": "Tarayıcı başlatma hatası",
        "cameraBlocked": "Kamera erişimi engellendi",
        "tryAgain": "Tekrar Dene",
        "scannerError": "Tarayıcı hatası",
        "initializing": "Kamera başlatılıyor...",
        "allowCamera": "QR kodları taramak için kamera erişimine izin verin",
        "scanHint": "Kamerayı bir konum QR koduna yöneltin",
        "invalidQr": "Geçersiz QR kodu",
        "lastScanned": "Son taranan",
        "orManualEntry": "Veya manuel girin",
        "warehouseId": "Depo ID",
        "warehouseIdPlaceholder": "Depo ID girin...",
        "locationCode": "Konum Kodu",
        "locationCodePlaceholder": "Konum kodu girin...",
        "goToLocation": "Konuma Git",
        "enterWarehouseId": "Depo ID girin",
        "cameraPlaceholder": "Kamera önizlemesi burada görünecek"
    },
    "locationDetail": {
        "title": "Konum Detayı",
        "notFound": "Konum Bulunamadı",
        "error": "Hata",
        "notFoundDescription": "Bu konum mevcut değil veya kaldırılmış.",
        "errorDescription": "Detaylar yüklenirken bir hata oluştu.",
        "scanAnother": "Başka Tara",
        "locationCode": "Konum Kodu",
        "partsHere": "Bu konumdaki parçalar",
        "part": "parça",
        "parts": "parça",
        "qty": "Adet",
        "noParts": "Parça Yok",
        "noPartsDescription": "Bu konuma atanmış parça bulunmuyor."
    },
    "pickList": {
        "title": "Toplama Listesi",
        "startPicking": "Toplamaya Başla",
        "progress": "İlerleme",
        "itemsPicked": "öğe toplandı",
        "allPicked": "Tüm öğeler toplandı!",
        "orderReady": "Sipariş paketlemeye hazır",
        "done": "Bitti",
        "noItems": "Toplanacak öğe yok",
        "noLocation": "\u2014",
        "loadingLocations": "Konumlar yükleniyor...",
        "markPicked": "Toplandı olarak işaretle",
        "unmarkPicked": "İşareti kaldır"
    }
}

print("Turkish translations defined")

# Main execution - update each locale file
def update_locale(lang):
    filepath = os.path.join(LOCALES_DIR, f"{lang}.json")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    trans = TRANSLATIONS[lang]
    
    # 1. Add "scan" to mobileNav
    if "mobileNav" in data:
        data["mobileNav"]["scan"] = trans["mobileNav_scan"]
    else:
        data["mobileNav"] = {"scan": trans["mobileNav_scan"]}
    
    # 2. Add warehouseLocations
    data["warehouseLocations"] = trans["warehouseLocations"]
    
    # 3. Add qrScanner
    data["qrScanner"] = trans["qrScanner"]
    
    # 4. Add locationDetail
    data["locationDetail"] = trans["locationDetail"]
    
    # 5. Replace/add pickList
    data["pickList"] = trans["pickList"]
    
    # Write back
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write('\n')
    
    print(f"Updated {filepath}")

# Process all 5 non-English locales
for lang in ["el", "ar", "es", "no", "tr"]:
    update_locale(lang)

print("\nAll locale files updated successfully!")
