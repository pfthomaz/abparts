# 🌍 Quick Language Reference

## Available Languages

| Flag | Language | Code | Native Name |
|------|----------|------|-------------|
| 🇬🇧 | English | `en` | English |
| 🇬🇷 | Greek | `el` | Ελληνικά |
| 🇸🇦 | Arabic | `ar` | العربية |
| 🇪🇸 | Spanish | `es` | Español |
| 🇹🇷 | Turkish | `tr` | Türkçe |
| 🇳🇴 | Norwegian | `no` | Norsk |

## How to Change Language

### In the App (User Interface)
1. Click your profile picture (top right)
2. Select "Profile" / "Προφίλ" / "الملف الشخصي" / "Perfil" / "Profil"
3. Find "Language Settings" section
4. Choose your preferred language
5. App updates immediately

### Via Database (Admin)
```sql
-- Set user language to Turkish
UPDATE users SET preferred_language = 'tr' WHERE username = 'username';

-- Set user language to Norwegian
UPDATE users SET preferred_language = 'no' WHERE username = 'username';
```

### Via Python Script
```bash
# Set language to Turkish
python3 set_user_language.py username tr

# Set language to Norwegian
python3 set_user_language.py username no
```

## Common Phrases in All Languages

### "Save"
- 🇬🇧 Save
- 🇬🇷 Αποθήκευση
- 🇸🇦 حفظ
- 🇪🇸 Guardar
- 🇹🇷 Kaydet
- 🇳🇴 Lagre

### "Cancel"
- 🇬🇧 Cancel
- 🇬🇷 Ακύρωση
- 🇸🇦 إلغاء
- 🇪🇸 Cancelar
- 🇹🇷 İptal
- 🇳🇴 Avbryt

### "Dashboard"
- 🇬🇧 Dashboard
- 🇬🇷 Πίνακας Ελέγχου
- 🇸🇦 لوحة التحكم
- 🇪🇸 Panel de Control
- 🇹🇷 Kontrol Paneli
- 🇳🇴 Dashbord

### "Parts"
- 🇬🇧 Parts
- 🇬🇷 Ανταλλακτικά
- 🇸🇦 القطع
- 🇪🇸 Piezas
- 🇹🇷 Parçalar
- 🇳🇴 Deler

### "Orders"
- 🇬🇧 Orders
- 🇬🇷 Παραγγελίες
- 🇸🇦 الطلبات
- 🇪🇸 Pedidos
- 🇹🇷 Siparişler
- 🇳🇴 Bestillinger

### "Machines"
- 🇬🇧 Machines
- 🇬🇷 Μηχανήματα
- 🇸🇦 الأجهزة
- 🇪🇸 Máquinas
- 🇹🇷 Makineler
- 🇳🇴 Maskiner

### "Users"
- 🇬🇧 Users
- 🇬🇷 Χρήστες
- 🇸🇦 المستخدمون
- 🇪🇸 Usuarios
- 🇹🇷 Kullanıcılar
- 🇳🇴 Brukere

### "Logout"
- 🇬🇧 Logout
- 🇬🇷 Αποσύνδεση
- 🇸🇦 تسجيل الخروج
- 🇪🇸 Cerrar Sesión
- 🇹🇷 Çıkış
- 🇳🇴 Logg ut

## For Developers

### Use Translation in Component
```javascript
import { useTranslation } from '../hooks/useTranslation';

const MyComponent = () => {
  const { t } = useTranslation();
  
  return <button>{t('common.save')}</button>;
};
```

### With Parameters
```javascript
<p>{t('dashboard.welcomeBack', { name: user.name })}</p>
// English: "Welcome back, John"
// Greek: "Καλώς ήρθες πίσω, John"
// Turkish: "Tekrar hoş geldiniz, John"
```

### Check Current Language
```javascript
import { useLocalization } from '../contexts/LocalizationContext';

const MyComponent = () => {
  const { currentLanguage } = useLocalization();
  
  console.log('Current language:', currentLanguage); // 'en', 'el', 'tr', etc.
};
```

## Translation Files Location

```
frontend/src/locales/
├── en.json  - English
├── el.json  - Greek
├── ar.json  - Arabic
├── es.json  - Spanish
├── tr.json  - Turkish
└── no.json  - Norwegian
```

## Adding New Translations

1. Find the English key in `en.json`
2. Add the same key to all other language files
3. Translate the value appropriately
4. Test in the app

Example:
```json
// en.json
{
  "myFeature": {
    "title": "My Feature"
  }
}

// tr.json
{
  "myFeature": {
    "title": "Özelliğim"
  }
}

// no.json
{
  "myFeature": {
    "title": "Min Funksjon"
  }
}
```

## Troubleshooting

### Translation not showing?
1. Check if key exists in translation file
2. Verify JSON syntax is valid
3. Check browser console for warnings
4. Refresh the page

### Wrong language displaying?
1. Check user's `preferred_language` in database
2. Clear browser localStorage
3. Check LocalizationContext console logs

### Missing translation?
- Falls back to English automatically
- Check console for warning: "Translation key not found: xxx"

## Quick Test Commands

```bash
# Validate JSON files
python3 -m json.tool frontend/src/locales/tr.json > /dev/null && echo "✅ Valid"
python3 -m json.tool frontend/src/locales/no.json > /dev/null && echo "✅ Valid"

# Check translation exists
python3 -c "import json; print(json.load(open('frontend/src/locales/tr.json'))['navigation']['dashboard'])"

# Count translations
wc -l frontend/src/locales/*.json
```

## Support

For questions or issues with translations:
1. Check this guide
2. Review `LANGUAGES_SUMMARY.md`
3. Check `LOCALIZATION_WORKING.md`
4. Review translation files in `frontend/src/locales/`
