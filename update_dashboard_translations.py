#!/usr/bin/env python3
"""Add dashboard translations"""

import json

# Greek dashboard translations
greek_dashboard = {
    "welcomeBack": "Καλώς ήρθες πίσω, {{name}}",
    "quickActions": "Γρήγορες Ενέργειες",
    "systemStatus": "Κατάσταση Συστήματος",
    "allSystemsOperational": "Όλα τα συστήματα λειτουργούν",
    "activeUsers": "Ενεργοί Χρήστες",
    "onlineNow": "Συνδεδεμένοι τώρα",
    "lowStock": "Χαμηλό Απόθεμα",
    "needsAttention": "Χρειάζεται προσοχή",
    "allGood": "Όλα καλά",
    "outOfStock": "Εξαντλημένο Απόθεμα",
    "critical": "Κρίσιμο",
    "allStocked": "Όλα σε απόθεμα",
    "pendingOrders": "Εκκρεμείς Παραγγελίες",
    "inProgress": "Σε εξέλιξη",
    "noPending": "Καμία εκκρεμής",
    "recentActivity": "Πρόσφατη Δραστηριότητα",
    "last24h": "Τελευταίες 24ω",
    "warehouses": "Αποθήκες",
    "activeLocations": "Ενεργές τοποθεσίες",
    "attentionRequired": "Απαιτείται Προσοχή",
    "criticalStockAlert": "Κρίσιμη Ειδοποίηση Αποθέματος",
    "lowStockWarning": "Προειδοποίηση Χαμηλού Αποθέματος",
    "pendingInvitations": "Εκκρεμείς Προσκλήσεις",
    "pendingOrdersOverview": "Επισκόπηση Εκκρεμών Παραγγελιών",
    "lowStockByOrganization": "Χαμηλό Απόθεμα ανά Οργανισμό",
    "currentStatus": "Τρέχουσα κατάσταση",
    "errorLoading": "Σφάλμα φόρτωσης πίνακα ελέγχου"
}

# Arabic dashboard translations
arabic_dashboard = {
    "welcomeBack": "مرحبًا بعودتك، {{name}}",
    "quickActions": "إجراءات سريعة",
    "systemStatus": "حالة النظام",
    "allSystemsOperational": "جميع الأنظمة تعمل",
    "activeUsers": "المستخدمون النشطون",
    "onlineNow": "متصل الآن",
    "lowStock": "مخزون منخفض",
    "needsAttention": "يحتاج إلى اهتمام",
    "allGood": "كل شيء على ما يرام",
    "outOfStock": "نفاد المخزون",
    "critical": "حرج",
    "allStocked": "كل شيء في المخزون",
    "pendingOrders": "الطلبات المعلقة",
    "inProgress": "قيد التنفيذ",
    "noPending": "لا يوجد معلق",
    "recentActivity": "النشاط الأخير",
    "last24h": "آخر 24 ساعة",
    "warehouses": "المستودعات",
    "activeLocations": "المواقع النشطة",
    "attentionRequired": "مطلوب الانتباه",
    "criticalStockAlert": "تنبيه مخزون حرج",
    "lowStockWarning": "تحذير مخزون منخفض",
    "pendingInvitations": "الدعوات المعلقة",
    "pendingOrdersOverview": "نظرة عامة على الطلبات المعلقة",
    "lowStockByOrganization": "المخزون المنخفض حسب المنظمة",
    "currentStatus": "الحالة الحالية",
    "errorLoading": "خطأ في تحميل لوحة التحكم"
}

# Update Greek file
with open('frontend/src/locales/el.json', 'r', encoding='utf-8') as f:
    el_data = json.load(f)

el_data['dashboard'] = greek_dashboard

with open('frontend/src/locales/el.json', 'w', encoding='utf-8') as f:
    json.dump(el_data, f, ensure_ascii=False, indent=2)

print("✅ Updated Greek dashboard translations")

# Update Arabic file
with open('frontend/src/locales/ar.json', 'r', encoding='utf-8') as f:
    ar_data = json.load(f)

ar_data['dashboard'] = arabic_dashboard

with open('frontend/src/locales/ar.json', 'w', encoding='utf-8') as f:
    json.dump(ar_data, f, ensure_ascii=False, indent=2)

print("✅ Updated Arabic dashboard translations")
print("✅ All dashboard translations updated!")
