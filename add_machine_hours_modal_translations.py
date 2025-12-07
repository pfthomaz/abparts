#!/usr/bin/env python3
import json

# Machine Hours Reminder Modal translations
translations = {
    'en': {
        'hoursReminder': 'Machine Hours Reminder',
        'hoursReminderMessage': "The following machines haven't had hours recorded in the last 2 weeks",
        'recordedViaReminder': 'Recorded via reminder',
        'failedToSaveHours': 'Failed to save machine hours',
        'successfullySavedHours': 'Successfully saved hours for {{count}} machine(s)!',
        'model': 'Model',
        'serial': 'Serial',
        'lastRecorded': 'Last recorded',
        'hrs': 'hrs',
        'noHoursRecorded': 'No hours ever recorded',
        'currentHours': 'Current Hours',
        'enterHoursPlaceholder': 'Enter hours...',
        'allMachinesUpToDate': 'All machines are up to date!',
        'allMachinesUpToDateMessage': 'All machines have hours recorded within the last 2 weeks.',
        'machinesNeedUpdating': '{{count}} machine(s) need updating',
        'skipForNow': 'Skip for Now',
        'saving': 'Saving...',
        'saveHours': 'Save Hours'
    },
    'el': {
        'hoursReminder': 'Υπενθύμιση Ωρών Μηχανήματος',
        'hoursReminderMessage': 'Τα παρακάτω μηχανήματα δεν έχουν καταγραφή ωρών τις τελευταίες 2 εβδομάδες',
        'recordedViaReminder': 'Καταγράφηκε μέσω υπενθύμισης',
        'failedToSaveHours': 'Αποτυχία αποθήκευσης ωρών μηχανήματος',
        'successfullySavedHours': 'Επιτυχής αποθήκευση ωρών για {{count}} μηχάνημα(τα)!',
        'model': 'Μοντέλο',
        'serial': 'Σειριακός',
        'lastRecorded': 'Τελευταία καταγραφή',
        'hrs': 'ώρες',
        'noHoursRecorded': 'Δεν έχουν καταγραφεί ποτέ ώρες',
        'currentHours': 'Τρέχουσες Ώρες',
        'enterHoursPlaceholder': 'Εισάγετε ώρες...',
        'allMachinesUpToDate': 'Όλα τα μηχανήματα είναι ενημερωμένα!',
        'allMachinesUpToDateMessage': 'Όλα τα μηχανήματα έχουν καταγραφή ωρών τις τελευταίες 2 εβδομάδες.',
        'machinesNeedUpdating': '{{count}} μηχάνημα(τα) χρειάζονται ενημέρωση',
        'skipForNow': 'Παράλειψη Προς το Παρόν',
        'saving': 'Αποθήκευση...',
        'saveHours': 'Αποθήκευση Ωρών'
    },
    'ar': {
        'hoursReminder': 'تذكير ساعات الآلة',
        'hoursReminderMessage': 'الآلات التالية لم يتم تسجيل ساعاتها في آخر أسبوعين',
        'recordedViaReminder': 'تم التسجيل عبر التذكير',
        'failedToSaveHours': 'فشل حفظ ساعات الآلة',
        'successfullySavedHours': 'تم حفظ الساعات بنجاح لـ {{count}} آلة!',
        'model': 'الطراز',
        'serial': 'الرقم التسلسلي',
        'lastRecorded': 'آخر تسجيل',
        'hrs': 'ساعات',
        'noHoursRecorded': 'لم يتم تسجيل ساعات مطلقًا',
        'currentHours': 'الساعات الحالية',
        'enterHoursPlaceholder': 'أدخل الساعات...',
        'allMachinesUpToDate': 'جميع الآلات محدثة!',
        'allMachinesUpToDateMessage': 'جميع الآلات لديها ساعات مسجلة خلال آخر أسبوعين.',
        'machinesNeedUpdating': '{{count}} آلة تحتاج إلى تحديث',
        'skipForNow': 'تخطي الآن',
        'saving': 'جاري الحفظ...',
        'saveHours': 'حفظ الساعات'
    },
    'es': {
        'hoursReminder': 'Recordatorio de Horas de Máquina',
        'hoursReminderMessage': 'Las siguientes máquinas no han tenido horas registradas en las últimas 2 semanas',
        'recordedViaReminder': 'Registrado mediante recordatorio',
        'failedToSaveHours': 'Error al guardar horas de máquina',
        'successfullySavedHours': '¡Horas guardadas exitosamente para {{count}} máquina(s)!',
        'model': 'Modelo',
        'serial': 'Serie',
        'lastRecorded': 'Último registro',
        'hrs': 'hrs',
        'noHoursRecorded': 'Nunca se han registrado horas',
        'currentHours': 'Horas Actuales',
        'enterHoursPlaceholder': 'Ingrese horas...',
        'allMachinesUpToDate': '¡Todas las máquinas están actualizadas!',
        'allMachinesUpToDateMessage': 'Todas las máquinas tienen horas registradas en las últimas 2 semanas.',
        'machinesNeedUpdating': '{{count}} máquina(s) necesitan actualización',
        'skipForNow': 'Omitir por Ahora',
        'saving': 'Guardando...',
        'saveHours': 'Guardar Horas'
    },
    'tr': {
        'hoursReminder': 'Makine Saatleri Hatırlatıcısı',
        'hoursReminderMessage': 'Aşağıdaki makinelerin son 2 haftada saat kaydı yapılmamış',
        'recordedViaReminder': 'Hatırlatıcı ile kaydedildi',
        'failedToSaveHours': 'Makine saatleri kaydedilemedi',
        'successfullySavedHours': '{{count}} makine için saatler başarıyla kaydedildi!',
        'model': 'Model',
        'serial': 'Seri',
        'lastRecorded': 'Son kayıt',
        'hrs': 'saat',
        'noHoursRecorded': 'Hiç saat kaydedilmemiş',
        'currentHours': 'Mevcut Saatler',
        'enterHoursPlaceholder': 'Saat girin...',
        'allMachinesUpToDate': 'Tüm makineler güncel!',
        'allMachinesUpToDateMessage': 'Tüm makinelerin son 2 hafta içinde saat kaydı var.',
        'machinesNeedUpdating': '{{count}} makine güncelleme gerektiriyor',
        'skipForNow': 'Şimdilik Atla',
        'saving': 'Kaydediliyor...',
        'saveHours': 'Saatleri Kaydet'
    },
    'no': {
        'hoursReminder': 'Maskinetimepåminnelse',
        'hoursReminderMessage': 'Følgende maskiner har ikke hatt timer registrert de siste 2 ukene',
        'recordedViaReminder': 'Registrert via påminnelse',
        'failedToSaveHours': 'Kunne ikke lagre maskintimer',
        'successfullySavedHours': 'Timer lagret for {{count}} maskin(er)!',
        'model': 'Modell',
        'serial': 'Serienummer',
        'lastRecorded': 'Sist registrert',
        'hrs': 'timer',
        'noHoursRecorded': 'Ingen timer noensinne registrert',
        'currentHours': 'Nåværende Timer',
        'enterHoursPlaceholder': 'Skriv inn timer...',
        'allMachinesUpToDate': 'Alle maskiner er oppdaterte!',
        'allMachinesUpToDateMessage': 'Alle maskiner har timer registrert innen de siste 2 ukene.',
        'machinesNeedUpdating': '{{count}} maskin(er) trenger oppdatering',
        'skipForNow': 'Hopp Over Nå',
        'saving': 'Lagrer...',
        'saveHours': 'Lagre Timer'
    }
}

# Add to each language file under machines section
for lang_code, modal_translations in translations.items():
    file_path = f'frontend/src/locales/{lang_code}.json'
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Ensure machines section exists
        if 'machines' not in data:
            data['machines'] = {}
        
        # Add the translations
        data['machines'].update(modal_translations)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f'✓ Added Machine Hours Modal translations to {lang_code}.json')
    
    except Exception as e:
        print(f'✗ Error processing {lang_code}.json: {e}')

print('\n✅ Machine Hours Modal translations added successfully!')
