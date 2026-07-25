#!/usr/bin/env python3
import json

# Translation keys to add
translations = {
    "en": {
        "transactions": {
            "title": "Transaction Management",
            "subtitle": "Manage and track all inventory transactions across your organization",
            "createOrder": "Create Order",
            "recordUsage": "Record Usage",
            "createTransaction": "Create Transaction",
            "createNewTransaction": "Create New Transaction",
            "tabs": {
                "history": "Transaction History",
                "historyDesc": "View and search transaction records",
                "auditTrail": "Audit Trail",
                "auditTrailDesc": "Detailed transaction audit log with filters",
                "analytics": "Analytics & Reports",
                "analyticsDesc": "Transaction analytics and reporting",
                "approvals": "Approvals",
                "approvalsDesc": "Manage transaction approvals",
                "reversals": "Reversals & Corrections",
                "reversalsDesc": "Reverse or correct transactions"
            }
        },
        "common": {
            "admin": "Admin"
        }
    },
    "el": {
        "transactions": {
            "title": "Διαχείριση Συναλλαγών",
            "subtitle": "Διαχειριστείτε και παρακολουθήστε όλες τις συναλλαγές αποθέματος στον οργανισμό σας",
            "createOrder": "Δημιουργία Παραγγελίας",
            "recordUsage": "Καταγραφή Χρήσης",
            "createTransaction": "Δημιουργία Συναλλαγής",
            "createNewTransaction": "Δημιουργία Νέας Συναλλαγής",
            "tabs": {
                "history": "Ιστορικό Συναλλαγών",
                "historyDesc": "Προβολή και αναζήτηση εγγραφών συναλλαγών",
                "auditTrail": "Ίχνος Ελέγχου",
                "auditTrailDesc": "Λεπτομερές αρχείο ελέγχου συναλλαγών με φίλτρα",
                "analytics": "Αναλυτικά & Αναφορές",
                "analyticsDesc": "Αναλυτικά και αναφορές συναλλαγών",
                "approvals": "Εγκρίσεις",
                "approvalsDesc": "Διαχείριση εγκρίσεων συναλλαγών",
                "reversals": "Αναστροφές & Διορθώσεις",
                "reversalsDesc": "Αναστροφή ή διόρθωση συναλλαγών"
            }
        },
        "common": {
            "admin": "Διαχειριστής"
        }
    },
    "ar": {
        "transactions": {
            "title": "إدارة المعاملات",
            "subtitle": "إدارة وتتبع جميع معاملات المخزون عبر مؤسستك",
            "createOrder": "إنشاء طلب",
            "recordUsage": "تسجيل الاستخدام",
            "createTransaction": "إنشاء معاملة",
            "createNewTransaction": "إنشاء معاملة جديدة",
            "tabs": {
                "history": "سجل المعاملات",
                "historyDesc": "عرض والبحث في سجلات المعاملات",
                "auditTrail": "مسار التدقيق",
                "auditTrailDesc": "سجل تدقيق مفصل للمعاملات مع الفلاتر",
                "analytics": "التحليلات والتقارير",
                "analyticsDesc": "تحليلات وتقارير المعاملات",
                "approvals": "الموافقات",
                "approvalsDesc": "إدارة موافقات المعاملات",
                "reversals": "العكس والتصحيحات",
                "reversalsDesc": "عكس أو تصحيح المعاملات"
            }
        },
        "common": {
            "admin": "مسؤول"
        }
    },
    "es": {
        "transactions": {
            "title": "Gestión de Transacciones",
            "subtitle": "Gestione y rastree todas las transacciones de inventario en su organización",
            "createOrder": "Crear Pedido",
            "recordUsage": "Registrar Uso",
            "createTransaction": "Crear Transacción",
            "createNewTransaction": "Crear Nueva Transacción",
            "tabs": {
                "history": "Historial de Transacciones",
                "historyDesc": "Ver y buscar registros de transacciones",
                "auditTrail": "Pista de Auditoría",
                "auditTrailDesc": "Registro detallado de auditoría de transacciones con filtros",
                "analytics": "Análisis e Informes",
                "analyticsDesc": "Análisis e informes de transacciones",
                "approvals": "Aprobaciones",
                "approvalsDesc": "Gestionar aprobaciones de transacciones",
                "reversals": "Reversiones y Correcciones",
                "reversalsDesc": "Revertir o corregir transacciones"
            }
        },
        "common": {
            "admin": "Administrador"
        }
    },
    "tr": {
        "transactions": {
            "title": "İşlem Yönetimi",
            "subtitle": "Kuruluşunuzdaki tüm envanter işlemlerini yönetin ve takip edin",
            "createOrder": "Sipariş Oluştur",
            "recordUsage": "Kullanım Kaydet",
            "createTransaction": "İşlem Oluştur",
            "createNewTransaction": "Yeni İşlem Oluştur",
            "tabs": {
                "history": "İşlem Geçmişi",
                "historyDesc": "İşlem kayıtlarını görüntüleyin ve arayın",
                "auditTrail": "Denetim İzi",
                "auditTrailDesc": "Filtreli detaylı işlem denetim kaydı",
                "analytics": "Analitik ve Raporlar",
                "analyticsDesc": "İşlem analitiği ve raporlama",
                "approvals": "Onaylar",
                "approvalsDesc": "İşlem onaylarını yönetin",
                "reversals": "Geri Almalar ve Düzeltmeler",
                "reversalsDesc": "İşlemleri geri alın veya düzeltin"
            }
        },
        "common": {
            "admin": "Yönetici"
        }
    },
    "no": {
        "transactions": {
            "title": "Transaksjonsstyring",
            "subtitle": "Administrer og spor alle lagertransaksjoner på tvers av organisasjonen din",
            "createOrder": "Opprett Bestilling",
            "recordUsage": "Registrer Bruk",
            "createTransaction": "Opprett Transaksjon",
            "createNewTransaction": "Opprett Ny Transaksjon",
            "tabs": {
                "history": "Transaksjonshistorikk",
                "historyDesc": "Vis og søk i transaksjonsposter",
                "auditTrail": "Revisjonsspor",
                "auditTrailDesc": "Detaljert transaksjonsrevisjonslogg med filtre",
                "analytics": "Analyse og Rapporter",
                "analyticsDesc": "Transaksjonsanalyse og rapportering",
                "approvals": "Godkjenninger",
                "approvalsDesc": "Administrer transaksjonsgodkjenninger",
                "reversals": "Reverseringer og Korrigeringer",
                "reversalsDesc": "Reverser eller korriger transaksjoner"
            }
        },
        "common": {
            "admin": "Administrator"
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
print("\nNew keys added for Transactions page")
