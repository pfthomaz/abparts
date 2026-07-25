# How to See Translations Working

## ✅ Your Language is Set to Greek!

The system has saved your preferred language as Greek (`el`), but you're still seeing English because the existing components haven't been migrated to use translations yet.

## 🎯 See It Working RIGHT NOW!

### Step 1: Visit the Translation Demo

Go to this URL in your browser:
```
http://localhost:3000/translation-demo
```

### Step 2: What You'll See

The demo page shows:
- ✅ All buttons in Greek (Αποθήκευση, Ακύρωση, Διαγραφή, etc.)
- ✅ Navigation items in Greek (Πίνακας Ελέγχου, Οργανισμοί, Χρήστες, etc.)
- ✅ Validation messages in Greek
- ✅ Error messages in Greek
- ✅ You can switch languages and see text change instantly!

## 📝 Why the Rest of the App is Still in English

The translation **infrastructure is complete**, but each component needs to be migrated to use it. Here's the difference:

### ❌ Current Code (Hardcoded English):
```javascript
<button>Save</button>
<h1>Dashboard</h1>
```

### ✅ Translated Code:
```javascript
import { useTranslation } from '../hooks/useTranslation';

function MyComponent() {
  const { t } = useTranslation();
  return (
    <>
      <button>{t('common.save')}</button>
      <h1>{t('navigation.dashboard')}</h1>
    </>
  );
}
```

## 🔄 How to Migrate Components

### Example: Migrate a Button

**Before:**
```javascript
<button className="...">Save Changes</button>
```

**After:**
```javascript
import { useTranslation } from '../hooks/useTranslation';

function MyComponent() {
  const { t } = useTranslation();
  
  return (
    <button className="...">{t('common.save')}</button>
  );
}
```

### Example: Migrate Page Title

**Before:**
```javascript
<h1>Dashboard</h1>
```

**After:**
```javascript
import { useTranslation } from '../hooks/useTranslation';

function Dashboard() {
  const { t } = useTranslation();
  
  return (
    <h1>{t('navigation.dashboard')}</h1>
  );
}
```

## 📚 Available Translation Keys

All keys are in `frontend/src/locales/*.json`:

### Common UI Elements
- `t('common.save')` → Αποθήκευση
- `t('common.cancel')` → Ακύρωση
- `t('common.delete')` → Διαγραφή
- `t('common.edit')` → Επεξεργασία
- `t('common.add')` → Προσθήκη

### Navigation
- `t('navigation.dashboard')` → Πίνακας Ελέγχου
- `t('navigation.organizations')` → Οργανισμοί
- `t('navigation.users')` → Χρήστες
- `t('navigation.parts')` → Ανταλλακτικά
- `t('navigation.warehouses')` → Αποθήκες
- `t('navigation.machines')` → Μηχανήματα
- `t('navigation.orders')` → Παραγγελίες

### Users
- `t('users.addUser')` → Προσθήκη Χρήστη
- `t('users.editUser')` → Επεξεργασία Χρήστη
- `t('users.username')` → Όνομα Χρήστη
- `t('users.email')` → Email
- `t('users.preferredLanguage')` → Προτιμώμενη Γλώσσα

### Validation
- `t('validation.required')` → Αυτό το πεδίο είναι υποχρεωτικό
- `t('validation.invalidEmail')` → Μη έγκυρη διεύθυνση email

## 🎯 Quick Win: Migrate One Component

Let's migrate the Dashboard title as an example:

1. Open `frontend/src/pages/Dashboard.js`
2. Add at the top:
   ```javascript
   import { useTranslation } from '../hooks/useTranslation';
   ```
3. Inside the component:
   ```javascript
   const { t } = useTranslation();
   ```
4. Replace any hardcoded text:
   ```javascript
   <h1>{t('navigation.dashboard')}</h1>
   ```

## 🚀 Gradual Migration Strategy

You don't need to migrate everything at once! Do it gradually:

1. **Start with high-traffic pages**: Dashboard, Orders, Parts
2. **Then navigation menus**: Layout, MobileNavigation
3. **Then forms**: UserForm, OrganizationForm, PartForm
4. **Finally everything else**

## ✅ Current Status

- ✅ Translation system fully working
- ✅ 4 languages supported (English, Greek, Arabic, Spanish)
- ✅ User language preference saved in database
- ✅ Demo page shows it working
- 🔄 Components need migration (gradual process)

## 📖 Full Documentation

- **Developer Guide**: `docs/LOCALIZATION_GUIDE.md`
- **Implementation Details**: `LOCALIZATION_IMPLEMENTATION_COMPLETE.md`
- **Quick Reference**: `LOCALIZATION_QUICK_START.md`

## 🎉 Next Steps

1. **Visit `/translation-demo`** to see it working
2. **Pick a component** to migrate (start small!)
3. **Replace hardcoded strings** with `t()` calls
4. **Test in Greek** to verify
5. **Repeat** for other components

The infrastructure is complete - now it's just a matter of replacing hardcoded strings with translation keys!
