#!/usr/bin/env python3
import json

# Calendar View translations
translations = {
    'en': {
        'previous30Days': 'Previous 30 Days',
        'today': 'Today',
        'next30Days': 'Next 30 Days',
        'showing': 'Showing',
        'noOrdersInRange': 'No orders in this date range',
        'showingCount': 'Showing {{visible}} of {{total}} orders',
        'orderInformation': 'Order Information',
        'orderItems': 'Order Items',
        'unknownPart': 'Unknown Part',
        'partNumber': 'Part #',
        'units': 'units',
        'each': 'each',
        'subtotal': 'Subtotal',
        'orderTotal': 'Order Total',
        'noItemsInOrder': 'No items in this order'
    },
    'el': {
        'previous30Days': 'Προηγούμενες 30 Ημέρες',
        'today': 'Σήμερα',
        'next30Days': 'Επόμενες 30 Ημέρες',
        'showing': 'Εμφάνιση',
        'noOrdersInRange': 'Δεν υπάρχουν παραγγελίες σε αυτό το χρονικό διάστημα',
        'showingCount': 'Εμφάνιση {{visible}} από {{total}} παραγγελίες',
        'orderInformation': 'Πληροφορίες Παραγγελίας',
        'orderItems': 'Αντικείμενα Παραγγελίας',
        'unknownPart': 'Άγνωστο Ανταλλακτικό',
        'partNumber': 'Αρ. Ανταλλακτικού',
        'units': 'μονάδες',
        'each': 'έκαστο',
        'subtotal': 'Υποσύνολο',
        'orderTotal': 'Σύνολο Παραγγελίας',
        'noItemsInOrder': 'Δεν υπάρχουν αντικείμενα σε αυτήν την παραγγελία'
    },
    'ar': {
        'previous30Days': 'الـ 30 يومًا السابقة',
        'today': 'اليوم',
        'next30Days': 'الـ 30 يومًا التالية',
        'showing': 'عرض',
        'noOrdersInRange': 'لا توجد طلبات في هذا النطاق الزمني',
        'showingCount': 'عرض {{visible}} من {{total}} طلبات',
        'orderInformation': 'معلومات الطلب',
        'orderItems': 'عناصر الطلب',
        'unknownPart': 'قطعة غير معروفة',
        'partNumber': 'رقم القطعة',
        'units': 'وحدات',
        'each': 'لكل واحدة',
        'subtotal': 'المجموع الفرعي',
        'orderTotal': 'إجمالي الطلب',
        'noItemsInOrder': 'لا توجد عناصر في هذا الطلب'
    },
    'es': {
        'previous30Days': '30 Días Anteriores',
        'today': 'Hoy',
        'next30Days': 'Próximos 30 Días',
        'showing': 'Mostrando',
        'noOrdersInRange': 'No hay pedidos en este rango de fechas',
        'showingCount': 'Mostrando {{visible}} de {{total}} pedidos',
        'orderInformation': 'Información del Pedido',
        'orderItems': 'Artículos del Pedido',
        'unknownPart': 'Pieza Desconocida',
        'partNumber': 'N.º de Pieza',
        'units': 'unidades',
        'each': 'cada uno',
        'subtotal': 'Subtotal',
        'orderTotal': 'Total del Pedido',
        'noItemsInOrder': 'No hay artículos en este pedido'
    },
    'tr': {
        'previous30Days': 'Önceki 30 Gün',
        'today': 'Bugün',
        'next30Days': 'Sonraki 30 Gün',
        'showing': 'Gösteriliyor',
        'noOrdersInRange': 'Bu tarih aralığında sipariş yok',
        'showingCount': '{{total}} siparişten {{visible}} gösteriliyor',
        'orderInformation': 'Sipariş Bilgileri',
        'orderItems': 'Sipariş Öğeleri',
        'unknownPart': 'Bilinmeyen Parça',
        'partNumber': 'Parça No',
        'units': 'birim',
        'each': 'adet',
        'subtotal': 'Ara Toplam',
        'orderTotal': 'Sipariş Toplamı',
        'noItemsInOrder': 'Bu siparişte öğe yok'
    },
    'no': {
        'previous30Days': 'Forrige 30 Dager',
        'today': 'I dag',
        'next30Days': 'Neste 30 Dager',
        'showing': 'Viser',
        'noOrdersInRange': 'Ingen bestillinger i dette datoområdet',
        'showingCount': 'Viser {{visible}} av {{total}} bestillinger',
        'orderInformation': 'Bestillingsinformasjon',
        'orderItems': 'Bestillingsvarer',
        'unknownPart': 'Ukjent Del',
        'partNumber': 'Delenr.',
        'units': 'enheter',
        'each': 'hver',
        'subtotal': 'Delsum',
        'orderTotal': 'Bestillingstotal',
        'noItemsInOrder': 'Ingen varer i denne bestillingen'
    }
}

# Add to each language file under orders.calendar
for lang_code, calendar_translations in translations.items():
    file_path = f'frontend/src/locales/{lang_code}.json'
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Ensure orders section exists
        if 'orders' not in data:
            data['orders'] = {}
        
        # Add calendar section
        data['orders']['calendar'] = calendar_translations
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f'✓ Added Calendar View translations to {lang_code}.json')
    
    except Exception as e:
        print(f'✗ Error processing {lang_code}.json: {e}')

print('\n✅ Calendar View translations added successfully!')
