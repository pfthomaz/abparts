# Apply Translations to All Screens - Quick Guide

## ✅ You've Seen It Working!

The translation demo at `/translation-demo` proves the system works perfectly. Now let's apply it everywhere.

## 🚀 Fastest Way: Use AI to Migrate

Since you have many components, the fastest way is to ask me (Kiro) to migrate specific components. Here's how:

### Just ask me:
```
"Migrate the Dashboard page to use Greek translations"
"Add translations to the Layout navigation menu"
"Translate all buttons in the UserForm component"
```

I'll do the migration for you automatically!

## 📝 Manual Migration (If You Prefer)

### Step 1: Add the Hook

At the top of any component file, add:
```javascript
import { useTranslation } from '../hooks/useTranslation';
```

Inside the component function, add:
```javascript
const { t } = useTranslation();
```

### Step 2: Replace Strings

Replace hardcoded English with translation keys:

```javascript
// Before
<button>Save</button>
<h1>Dashboard</h1>
<label>Username</label>

// After
<button>{t('common.save')}</button>
<h1>{t('navigation.dashboard')}</h1>
<label>{t('users.username')}</label>
```

## 🎯 Priority Components to Migrate

### High Priority (Most Visible):
1. **Layout.js** - Navigation menu, user menu
2. **Dashboard.js** - Main dashboard page
3. **LoginForm.js** - Login page
4. **UserForm.js** - User creation/editing
5. **OrganizationForm.js** - Organization management

### Medium Priority:
6. **Parts.js** - Parts management
7. **Orders.js** - Orders page
8. **Warehouses.js** - Warehouses page
9. **Machines.js** - Machines page
10. **UserProfile.js** - User profile page

### Lower Priority:
- All other pages and components
- Modal dialogs
- Form validation messages

## 📚 Complete Translation Key Reference

### Common UI (common.*)
```javascript
t('common.save')          // Αποθήκευση
t('common.cancel')        // Ακύρωση
t('common.delete')        // Διαγραφή
t('common.edit')          // Επεξεργασία
t('common.add')           // Προσθήκη
t('common.create')        // Δημιουργία
t('common.update')        // Ενημέρωση
t('common.search')        // Αναζήτηση
t('common.filter')        // Φίλτρο
t('common.loading')       // Φόρτωση...
t('common.yes')           // Ναι
t('common.no')            // Όχι
t('common.close')         // Κλείσιμο
t('common.submit')        // Υποβολή
t('common.reset')         // Επαναφορά
t('common.active')        // Ενεργό
t('common.inactive')      // Ανενεργό
t('common.status')        // Κατάσταση
t('common.actions')       // Ενέργειες
```

### Navigation (navigation.*)
```javascript
t('navigation.dashboard')        // Πίνακας Ελέγχου
t('navigation.organizations')    // Οργανισμοί
t('navigation.users')            // Χρήστες
t('navigation.parts')            // Ανταλλακτικά
t('navigation.inventory')        // Απόθεμα
t('navigation.warehouses')       // Αποθήκες
t('navigation.machines')         // Μηχανήματα
t('navigation.orders')           // Παραγγελίες
t('navigation.stockAdjustments') // Προσαρμογές Αποθέματος
t('navigation.maintenance')      // Συντήρηση
t('navigation.reports')          // Αναφορές
t('navigation.settings')         // Ρυθμίσεις
t('navigation.profile')          // Προφίλ
t('navigation.logout')           // Αποσύνδεση
t('navigation.dailyOperations')  // Καθημερινές Λειτουργίες
```

### Users (users.*)
```javascript
t('users.title')            // Χρήστες
t('users.addUser')          // Προσθήκη Χρήστη
t('users.editUser')         // Επεξεργασία Χρήστη
t('users.deleteUser')       // Διαγραφή Χρήστη
t('users.username')         // Όνομα Χρήστη
t('users.email')            // Email
t('users.name')             // Όνομα
t('users.role')             // Ρόλος
t('users.organization')     // Οργανισμός
t('users.isActive')         // Ενεργός
t('users.preferredLanguage') // Προτιμώμενη Γλώσσα
```

### Organizations (organizations.*)
```javascript
t('organizations.title')            // Οργανισμοί
t('organizations.addOrganization')  // Προσθήκη Οργανισμού
t('organizations.editOrganization') // Επεξεργασία Οργανισμού
t('organizations.name')             // Όνομα
t('organizations.type')             // Τύπος
t('organizations.country')          // Χώρα
t('organizations.address')          // Διεύθυνση
t('organizations.contactInfo')      // Στοιχεία Επικοινωνίας
```

### Parts (parts.*)
```javascript
t('parts.title')        // Ανταλλακτικά
t('parts.addPart')      // Προσθήκη Ανταλλακτικού
t('parts.editPart')     // Επεξεργασία Ανταλλακτικού
t('parts.partNumber')   // Κωδικός Ανταλλακτικού
t('parts.description')  // Περιγραφή
t('parts.category')     // Κατηγορία
t('parts.price')        // Τιμή
t('parts.stock')        // Απόθεμα
```

### Validation (validation.*)
```javascript
t('validation.required')      // Αυτό το πεδίο είναι υποχρεωτικό
t('validation.invalidEmail')  // Μη έγκυρη διεύθυνση email
t('validation.minLength', { min: 8 })  // Το ελάχιστο μήκος είναι 8 χαρακτήρες
```

### Errors (errors.*)
```javascript
t('errors.generic')       // Παρουσιάστηκε σφάλμα
t('errors.unauthorized')  // Δεν έχετε εξουσιοδότηση
t('errors.networkError')  // Σφάλμα δικτύου
t('errors.serverError')   // Σφάλμα διακομιστή
```

## 🤖 Let Me Do It For You!

The easiest way: Just tell me which components you want translated, and I'll migrate them for you!

Examples:
- "Translate the Dashboard page"
- "Add Greek translations to the navigation menu"
- "Migrate all user management forms"
- "Translate the entire Layout component"

I'll handle all the code changes automatically!

## ✅ Testing After Migration

After migrating a component:
1. Refresh the page
2. Check that Greek text appears
3. Try switching languages in the demo
4. Verify all buttons and labels are translated

## 📖 Full Documentation

- Translation keys: `frontend/src/locales/el.json`
- Developer guide: `docs/LOCALIZATION_GUIDE.md`
- How it works: `HOW_TO_SEE_TRANSLATIONS.md`

## 🎉 Ready to Go!

Just tell me which components to migrate, and I'll do it for you!
