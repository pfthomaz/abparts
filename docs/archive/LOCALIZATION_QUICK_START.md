# Localization Quick Start Guide

## 🚀 Setup (One-time)

```bash
# Run the migration
./run_language_migration.sh
```

## 👤 Set User Language

1. Go to **Users** page
2. Click **Add User** or **Edit** existing user
3. Select **Preferred Language** from dropdown:
   - 🇬🇧 English
   - 🇬🇷 Ελληνικά (Greek)
   - 🇸🇦 العربية (Arabic)
   - 🇪🇸 Español (Spanish)
4. Click **Save**

## 💻 Use in Components

```javascript
import { useTranslation } from '../hooks/useTranslation';

function MyComponent() {
  const { t } = useTranslation();
  
  return (
    <div>
      <h1>{t('navigation.dashboard')}</h1>
      <button>{t('common.save')}</button>
      <button>{t('common.cancel')}</button>
    </div>
  );
}
```

## 📝 Common Translation Keys

```javascript
// Buttons
t('common.save')          // Save
t('common.cancel')        // Cancel
t('common.delete')        // Delete
t('common.edit')          // Edit
t('common.add')           // Add
t('common.create')        // Create
t('common.update')        // Update
t('common.submit')        // Submit

// Navigation
t('navigation.dashboard')        // Dashboard
t('navigation.organizations')    // Organizations
t('navigation.users')            // Users
t('navigation.parts')            // Parts
t('navigation.warehouses')       // Warehouses
t('navigation.machines')         // Machines
t('navigation.orders')           // Orders
t('navigation.maintenance')      // Maintenance

// Validation
t('validation.required')         // This field is required
t('validation.invalidEmail')     // Invalid email address

// Errors
t('errors.generic')              // An error occurred
t('errors.unauthorized')         // Not authorized
```

## 🌍 Supported Languages

| Language | Code | RTL |
|----------|------|-----|
| English  | `en` | No  |
| Greek    | `el` | No  |
| Arabic   | `ar` | Yes |
| Spanish  | `es` | No  |

## 📚 Full Documentation

See `docs/LOCALIZATION_GUIDE.md` for complete documentation.
