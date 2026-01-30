#!/usr/bin/env python3
"""Add Field Operations Dashboard translations to all languages."""

import json
import os

# Translation data for all languages
translations = {
    'en': {
        'fab': {
            'washNets': 'Wash Nets',
            'dailyService': 'Daily Service',
            'orderParts': 'Order Parts',
            'close': 'Close',
            'quickActions': 'Quick Actions'
        },
        'fieldOps': {
            'washNets': 'Wash Nets',
            'washNetsDesc': 'Record net cleaning',
            'dailyService': 'Daily Service',
            'dailyServiceDesc': 'Perform maintenance',
            'orderParts': 'Order Parts',
            'orderPartsDesc': 'Request supplies',
            'netsToday': 'Nets Today',
            'servicesToday': 'Services Today',
            'todaysActivity': "Today's Activity",
            'noActivityYet': 'No activity yet today',
            'startYourDay': 'Start your day by recording a cleaning or service',
            'completedToday': 'Completed today: {{count}}',
            'viewFarms': 'View Farms',
            'viewMachines': 'View Machines'
        }
    },
    'es': {
        'fab': {
            'washNets': 'Lavar Redes',
            'dailyService': 'Servicio Diario',
            'orderParts': 'Pedir Piezas',
            'close': 'Cerrar',
            'quickActions': 'Acciones Rápidas'
        },
        'fieldOps': {
            'washNets': 'Lavar Redes',
            'washNetsDesc': 'Registrar limpieza de redes',
            'dailyService': 'Servicio Diario',
            'dailyServiceDesc': 'Realizar mantenimiento',
            'orderParts': 'Pedir Piezas',
            'orderPartsDesc': 'Solicitar suministros',
            'netsToday': 'Redes Hoy',
            'servicesToday': 'Servicios Hoy',
            'todaysActivity': 'Actividad de Hoy',
            'noActivityYet': 'Sin actividad hoy',
            'startYourDay': 'Comienza tu día registrando una limpieza o servicio',
            'completedToday': 'Completado hoy: {{count}}',
            'viewFarms': 'Ver Granjas',
            'viewMachines': 'Ver Máquinas'
        }
    },
    'ar': {
        'fab': {
            'washNets': 'غسل الشباك',
            'dailyService': 'الخدمة اليومية',
            'orderParts': 'طلب قطع الغيار',
            'close': 'إغلاق',
            'quickActions': 'إجراءات سريعة'
        },
        'fieldOps': {
            'washNets': 'غسل الشباك',
            'washNetsDesc': 'تسجيل تنظيف الشباك',
            'dailyService': 'الخدمة اليومية',
            'dailyServiceDesc': 'إجراء الصيانة',
            'orderParts': 'طلب قطع الغيار',
            'orderPartsDesc': 'طلب الإمدادات',
            'netsToday': 'الشباك اليوم',
            'servicesToday': 'الخدمات اليوم',
            'todaysActivity': 'نشاط اليوم',
            'noActivityYet': 'لا يوجد نشاط اليوم',
            'startYourDay': 'ابدأ يومك بتسجيل تنظيف أو خدمة',
            'completedToday': 'مكتمل اليوم: {{count}}',
            'viewFarms': 'عرض المزارع',
            'viewMachines': 'عرض الآلات'
        }
    },
    'el': {
        'fab': {
            'washNets': 'Πλύσιμο Διχτυών',
            'dailyService': 'Ημερήσια Υπηρεσία',
            'orderParts': 'Παραγγελία Ανταλλακτικών',
            'close': 'Κλείσιμο',
            'quickActions': 'Γρήγορες Ενέργειες'
        },
        'fieldOps': {
            'washNets': 'Πλύσιμο Διχτυών',
            'washNetsDesc': 'Καταγραφή καθαρισμού διχτυών',
            'dailyService': 'Ημερήσια Υπηρεσία',
            'dailyServiceDesc': 'Εκτέλεση συντήρησης',
            'orderParts': 'Παραγγελία Ανταλλακτικών',
            'orderPartsDesc': 'Αίτημα προμηθειών',
            'netsToday': 'Δίχτυα Σήμερα',
            'servicesToday': 'Υπηρεσίες Σήμερα',
            'todaysActivity': 'Δραστηριότητα Σήμερα',
            'noActivityYet': 'Καμία δραστηριότητα σήμερα',
            'startYourDay': 'Ξεκινήστε τη μέρα σας καταγράφοντας έναν καθαρισμό ή υπηρεσία',
            'completedToday': 'Ολοκληρώθηκε σήμερα: {{count}}',
            'viewFarms': 'Προβολή Φάρμων',
            'viewMachines': 'Προβολή Μηχανών'
        }
    },
    'no': {
        'fab': {
            'washNets': 'Vask Nett',
            'dailyService': 'Daglig Service',
            'orderParts': 'Bestill Deler',
            'close': 'Lukk',
            'quickActions': 'Hurtighandlinger'
        },
        'fieldOps': {
            'washNets': 'Vask Nett',
            'washNetsDesc': 'Registrer nettvask',
            'dailyService': 'Daglig Service',
            'dailyServiceDesc': 'Utfør vedlikehold',
            'orderParts': 'Bestill Deler',
            'orderPartsDesc': 'Be om forsyninger',
            'netsToday': 'Nett I Dag',
            'servicesToday': 'Tjenester I Dag',
            'todaysActivity': 'Dagens Aktivitet',
            'noActivityYet': 'Ingen aktivitet i dag',
            'startYourDay': 'Start dagen din ved å registrere en vask eller service',
            'completedToday': 'Fullført i dag: {{count}}',
            'viewFarms': 'Vis Gårder',
            'viewMachines': 'Vis Maskiner'
        }
    },
    'tr': {
        'fab': {
            'washNets': 'Ağları Yıka',
            'dailyService': 'Günlük Servis',
            'orderParts': 'Parça Sipariş Et',
            'close': 'Kapat',
            'quickActions': 'Hızlı İşlemler'
        },
        'fieldOps': {
            'washNets': 'Ağları Yıka',
            'washNetsDesc': 'Ağ temizliğini kaydet',
            'dailyService': 'Günlük Servis',
            'dailyServiceDesc': 'Bakım yap',
            'orderParts': 'Parça Sipariş Et',
            'orderPartsDesc': 'Malzeme talep et',
            'netsToday': 'Bugün Ağlar',
            'servicesToday': 'Bugün Servisler',
            'todaysActivity': 'Bugünün Aktivitesi',
            'noActivityYet': 'Bugün henüz aktivite yok',
            'startYourDay': 'Bir temizlik veya servis kaydederek güne başlayın',
            'completedToday': 'Bugün tamamlanan: {{count}}',
            'viewFarms': 'Çiftlikleri Görüntüle',
            'viewMachines': 'Makineleri Görüntüle'
        }
    }
}

def add_translations():
    """Add translations to all language files."""
    base_path = 'frontend/src/locales'
    
    for lang_code, trans_data in translations.items():
        file_path = os.path.join(base_path, f'{lang_code}.json')
        
        # Read existing translations
        with open(file_path, 'r', encoding='utf-8') as f:
            existing = json.load(f)
        
        # Add new translations
        existing.update(trans_data)
        
        # Write back
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(existing, f, ensure_ascii=False, indent=2)
        
        print(f'✓ Updated {lang_code}.json')

if __name__ == '__main__':
    add_translations()
    print('\n✅ All translations added successfully!')
