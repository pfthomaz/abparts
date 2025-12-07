#!/usr/bin/env python3
"""Update navigation translations in all language files"""

import json

# Greek translations
greek_nav = {
    "dashboard": "Πίνακας Ελέγχου",
    "dashboardDescription": "Επισκόπηση μετρήσεων και κατάστασης συστήματος",
    "organizations": "Οργανισμοί",
    "organizationsDescription": "Διαχείριση ιεραρχίας και σχέσεων οργανισμών",
    "organizationManagement": "Διαχείριση Οργανισμού",
    "organizationManagementDescription": "Βελτιωμένη διαχείριση οργανισμού, προμηθευτών και αποθηκών",
    "parts": "Ανταλλακτικά",
    "partsDescription": "Περιήγηση και διαχείριση καταλόγου ανταλλακτικών",
    "orders": "Παραγγελίες",
    "ordersDescription": "Δημιουργία και παρακολούθηση παραγγελιών ανταλλακτικών",
    "stocktake": "Απογραφή",
    "stocktakeDescription": "Εκτέλεση προσαρμογών και απογραφών αποθέματος",
    "stockAdjustments": "Προσαρμογές Αποθέματος",
    "stockAdjustmentsDescription": "Καταγραφή και παρακολούθηση προσαρμογών αποθέματος",
    "maintenanceProtocols": "Πρωτόκολλα Συντήρησης",
    "maintenanceProtocolsDescription": "Διαχείριση προτύπων πρωτοκόλλων συντήρησης",
    "maintenance": "Συντήρηση",
    "maintenanceDescription": "Εκτέλεση και παρακολούθηση συντήρησης",
    "machines": "Μηχανήματα",
    "machinesDescription": "Προβολή και διαχείριση μηχανημάτων AutoBoss",
    "users": "Χρήστες",
    "usersDescription": "Διαχείριση χρηστών και δικαιωμάτων",
    "warehouses": "Αποθήκες",
    "warehousesDescription": "Διαχείριση τοποθεσιών και ρυθμίσεων αποθηκών",
    "transactions": "Συναλλαγές",
    "transactionsDescription": "Προβολή και διαχείριση ιστορικού συναλλαγών",
    "configuration": "Ρυθμίσεις",
    "configurationDescription": "Πίνακας διαχειριστικών ρυθμίσεων",
    "inventory": "Απόθεμα",
    "reports": "Αναφορές",
    "settings": "Ρυθμίσεις",
    "profile": "Προφίλ",
    "security": "Κέντρο Ασφαλείας",
    "logout": "Αποσύνδεση",
    "dailyOperations": "Καθημερινές Λειτουργίες",
    "categories": {
        "core": "Βασικά",
        "inventory": "Απόθεμα",
        "operations": "Λειτουργίες",
        "administration": "Διαχείριση"
    }
}

# Arabic translations
arabic_nav = {
    "dashboard": "لوحة التحكم",
    "dashboardDescription": "نظرة عامة على مقاييس النظام والحالة",
    "organizations": "المنظمات",
    "organizationsDescription": "إدارة التسلسل الهرمي والعلاقات التنظيمية",
    "organizationManagement": "إدارة المنظمة",
    "organizationManagementDescription": "إدارة محسّنة للمنظمة والموردين والمستودعات",
    "parts": "القطع",
    "partsDescription": "تصفح وإدارة كتالوج القطع",
    "orders": "الطلبات",
    "ordersDescription": "إنشاء وتتبع طلبات القطع",
    "stocktake": "الجرد",
    "stocktakeDescription": "إجراء تعديلات وجرد المخزون",
    "stockAdjustments": "تعديلات المخزون",
    "stockAdjustmentsDescription": "تسجيل وتتبع تعديلات المخزون",
    "maintenanceProtocols": "بروتوكولات الصيانة",
    "maintenanceProtocolsDescription": "إدارة قوالب بروتوكولات الصيانة",
    "maintenance": "الصيانة",
    "maintenanceDescription": "تنفيذ وتتبع الصيانة",
    "machines": "الأجهزة",
    "machinesDescription": "عرض وإدارة أجهزة AutoBoss",
    "users": "المستخدمون",
    "usersDescription": "إدارة المستخدمين والأذونات",
    "warehouses": "المستودعات",
    "warehousesDescription": "إدارة مواقع وإعدادات المستودعات",
    "transactions": "المعاملات",
    "transactionsDescription": "عرض وإدارة سجل المعاملات",
    "configuration": "التكوين",
    "configurationDescription": "لوحة التكوين الإدارية",
    "inventory": "المخزون",
    "reports": "التقارير",
    "settings": "الإعدادات",
    "profile": "الملف الشخصي",
    "security": "مركز الأمان",
    "logout": "تسجيل الخروج",
    "dailyOperations": "العمليات اليومية",
    "categories": {
        "core": "الأساسية",
        "inventory": "المخزون",
        "operations": "العمليات",
        "administration": "الإدارة"
    }
}

# Update Greek file
with open('frontend/src/locales/el.json', 'r', encoding='utf-8') as f:
    el_data = json.load(f)

el_data['navigation'] = greek_nav

with open('frontend/src/locales/el.json', 'w', encoding='utf-8') as f:
    json.dump(el_data, f, ensure_ascii=False, indent=2)

print("✅ Updated Greek translations")

# Update Arabic file
with open('frontend/src/locales/ar.json', 'r', encoding='utf-8') as f:
    ar_data = json.load(f)

ar_data['navigation'] = arabic_nav

with open('frontend/src/locales/ar.json', 'w', encoding='utf-8') as f:
    json.dump(ar_data, f, ensure_ascii=False, indent=2)

print("✅ Updated Arabic translations")
print("✅ All navigation translations updated!")
