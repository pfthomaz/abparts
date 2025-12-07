#!/usr/bin/env python3
import json

# Translation keys to add
translations = {
    "en": {
        "transactionHistory": {
            "title": "Transaction History",
            "filters": "Filters",
            "transactionType": "Transaction Type",
            "allTypes": "All Types",
            "part": "Part",
            "allParts": "All Parts",
            "fromWarehouse": "From Warehouse",
            "toWarehouse": "To Warehouse",
            "allWarehouses": "All Warehouses",
            "startDate": "Start Date",
            "endDate": "End Date",
            "referenceNumber": "Reference Number",
            "referenceNumberPlaceholder": "Enter reference number",
            "clearFilters": "Clear Filters",
            "search": "Search",
            "loading": "Loading transactions...",
            "noTransactionsFound": "No transactions found.",
            "loadingMore": "Loading more transactions...",
            "loadMore": "Load More",
            "tableHeaders": {
                "date": "Date",
                "type": "Type",
                "part": "Part",
                "quantity": "Quantity",
                "from": "From",
                "to": "To",
                "performedBy": "Performed By",
                "reference": "Reference"
            },
            "types": {
                "creation": "Creation",
                "transfer": "Transfer",
                "consumption": "Consumption",
                "adjustment": "Adjustment"
            },
            "machine": "Machine"
        }
    },
    "el": {
        "transactionHistory": {
            "title": "Ιστορικό Συναλλαγών",
            "filters": "Φίλτρα",
            "transactionType": "Τύπος Συναλλαγής",
            "allTypes": "Όλοι οι Τύποι",
            "part": "Ανταλλακτικό",
            "allParts": "Όλα τα Ανταλλακτικά",
            "fromWarehouse": "Από Αποθήκη",
            "toWarehouse": "Προς Αποθήκη",
            "allWarehouses": "Όλες οι Αποθήκες",
            "startDate": "Ημερομηνία Έναρξης",
            "endDate": "Ημερομηνία Λήξης",
            "referenceNumber": "Αριθμός Αναφοράς",
            "referenceNumberPlaceholder": "Εισάγετε αριθμό αναφοράς",
            "clearFilters": "Εκκαθάριση Φίλτρων",
            "search": "Αναζήτηση",
            "loading": "Φόρτωση συναλλαγών...",
            "noTransactionsFound": "Δεν βρέθηκαν συναλλαγές.",
            "loadingMore": "Φόρτωση περισσότερων συναλλαγών...",
            "loadMore": "Φόρτωση Περισσότερων",
            "tableHeaders": {
                "date": "Ημερομηνία",
                "type": "Τύπος",
                "part": "Ανταλλακτικό",
                "quantity": "Ποσότητα",
                "from": "Από",
                "to": "Προς",
                "performedBy": "Εκτελέστηκε Από",
                "reference": "Αναφορά"
            },
            "types": {
                "creation": "Δημιουργία",
                "transfer": "Μεταφορά",
                "consumption": "Κατανάλωση",
                "adjustment": "Προσαρμογή"
            },
            "machine": "Μηχάνημα"
        }
    },
    "ar": {
        "transactionHistory": {
            "title": "سجل المعاملات",
            "filters": "الفلاتر",
            "transactionType": "نوع المعاملة",
            "allTypes": "جميع الأنواع",
            "part": "القطعة",
            "allParts": "جميع القطع",
            "fromWarehouse": "من المستودع",
            "toWarehouse": "إلى المستودع",
            "allWarehouses": "جميع المستودعات",
            "startDate": "تاريخ البدء",
            "endDate": "تاريخ الانتهاء",
            "referenceNumber": "الرقم المرجعي",
            "referenceNumberPlaceholder": "أدخل الرقم المرجعي",
            "clearFilters": "مسح الفلاتر",
            "search": "بحث",
            "loading": "جاري تحميل المعاملات...",
            "noTransactionsFound": "لم يتم العثور على معاملات.",
            "loadingMore": "جاري تحميل المزيد من المعاملات...",
            "loadMore": "تحميل المزيد",
            "tableHeaders": {
                "date": "التاريخ",
                "type": "النوع",
                "part": "القطعة",
                "quantity": "الكمية",
                "from": "من",
                "to": "إلى",
                "performedBy": "نفذ بواسطة",
                "reference": "المرجع"
            },
            "types": {
                "creation": "إنشاء",
                "transfer": "نقل",
                "consumption": "استهلاك",
                "adjustment": "تعديل"
            },
            "machine": "الآلة"
        }
    },
    "es": {
        "transactionHistory": {
            "title": "Historial de Transacciones",
            "filters": "Filtros",
            "transactionType": "Tipo de Transacción",
            "allTypes": "Todos los Tipos",
            "part": "Pieza",
            "allParts": "Todas las Piezas",
            "fromWarehouse": "Desde Almacén",
            "toWarehouse": "Hacia Almacén",
            "allWarehouses": "Todos los Almacenes",
            "startDate": "Fecha de Inicio",
            "endDate": "Fecha de Fin",
            "referenceNumber": "Número de Referencia",
            "referenceNumberPlaceholder": "Ingrese número de referencia",
            "clearFilters": "Limpiar Filtros",
            "search": "Buscar",
            "loading": "Cargando transacciones...",
            "noTransactionsFound": "No se encontraron transacciones.",
            "loadingMore": "Cargando más transacciones...",
            "loadMore": "Cargar Más",
            "tableHeaders": {
                "date": "Fecha",
                "type": "Tipo",
                "part": "Pieza",
                "quantity": "Cantidad",
                "from": "Desde",
                "to": "Hacia",
                "performedBy": "Realizado Por",
                "reference": "Referencia"
            },
            "types": {
                "creation": "Creación",
                "transfer": "Transferencia",
                "consumption": "Consumo",
                "adjustment": "Ajuste"
            },
            "machine": "Máquina"
        }
    },
    "tr": {
        "transactionHistory": {
            "title": "İşlem Geçmişi",
            "filters": "Filtreler",
            "transactionType": "İşlem Türü",
            "allTypes": "Tüm Türler",
            "part": "Parça",
            "allParts": "Tüm Parçalar",
            "fromWarehouse": "Depodan",
            "toWarehouse": "Depoya",
            "allWarehouses": "Tüm Depolar",
            "startDate": "Başlangıç Tarihi",
            "endDate": "Bitiş Tarihi",
            "referenceNumber": "Referans Numarası",
            "referenceNumberPlaceholder": "Referans numarası girin",
            "clearFilters": "Filtreleri Temizle",
            "search": "Ara",
            "loading": "İşlemler yükleniyor...",
            "noTransactionsFound": "İşlem bulunamadı.",
            "loadingMore": "Daha fazla işlem yükleniyor...",
            "loadMore": "Daha Fazla Yükle",
            "tableHeaders": {
                "date": "Tarih",
                "type": "Tür",
                "part": "Parça",
                "quantity": "Miktar",
                "from": "Nereden",
                "to": "Nereye",
                "performedBy": "Gerçekleştiren",
                "reference": "Referans"
            },
            "types": {
                "creation": "Oluşturma",
                "transfer": "Transfer",
                "consumption": "Tüketim",
                "adjustment": "Ayarlama"
            },
            "machine": "Makine"
        }
    },
    "no": {
        "transactionHistory": {
            "title": "Transaksjonshistorikk",
            "filters": "Filtre",
            "transactionType": "Transaksjonstype",
            "allTypes": "Alle Typer",
            "part": "Del",
            "allParts": "Alle Deler",
            "fromWarehouse": "Fra Lager",
            "toWarehouse": "Til Lager",
            "allWarehouses": "Alle Lagre",
            "startDate": "Startdato",
            "endDate": "Sluttdato",
            "referenceNumber": "Referansenummer",
            "referenceNumberPlaceholder": "Skriv inn referansenummer",
            "clearFilters": "Fjern Filtre",
            "search": "Søk",
            "loading": "Laster transaksjoner...",
            "noTransactionsFound": "Ingen transaksjoner funnet.",
            "loadingMore": "Laster flere transaksjoner...",
            "loadMore": "Last Mer",
            "tableHeaders": {
                "date": "Dato",
                "type": "Type",
                "part": "Del",
                "quantity": "Mengde",
                "from": "Fra",
                "to": "Til",
                "performedBy": "Utført Av",
                "reference": "Referanse"
            },
            "types": {
                "creation": "Opprettelse",
                "transfer": "Overføring",
                "consumption": "Forbruk",
                "adjustment": "Justering"
            },
            "machine": "Maskin"
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
print("\nNew keys added for TransactionHistory component")
