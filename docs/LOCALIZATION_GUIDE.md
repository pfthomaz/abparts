# ABParts Localization Guide

## Overview

ABParts now supports full internationalization (i18n) with support for:
- **English (en)** - Default language
- **Greek (el)** - Ελληνικά
- **Arabic (ar)** - العربية (with RTL support)
- **Spanish (es)** - Español

## User Language Preference

Each user can set their preferred language in their user profile. The system will:
1. Use the user's `preferred_language` field from the database
2. Fall back to localStorage preferences if no user preference is set
3. Fall back to organization country's default language
4. Finally fall back to English

## For Developers

### Using Translations in Components

```javascript
import { useTranslation } from '../hooks/useTranslation';

function MyComponent() {
  const { t } = useTranslation();
  
  return (
    <div>
      <h1>{t('navigation.dashboard')}</h1>
      <button>{t('common.save')}</button>
      <p>{t('validation.minLength', { min: 8 })}</p>
    </div>
  );
}
```

### Translation Keys Structure

Translations are organized by namespace in JSON files located in `frontend/src/locales/`:

```
common.*          - Common UI elements (save, cancel, delete, etc.)
navigation.*      - Navigation menu items
auth.*            - Authentication related
users.*           - User management
organizations.*   - Organization management
parts.*           - Parts management
warehouses.*      - Warehouse management
machines.*        - Machine management
orders.*          - Order management
maintenance.*     - Maintenance features
dashboard.*       - Dashboard
validation.*      - Form validation messages
errors.*          - Error messages
```

### Adding New Translations

1. Add the key to all language files (`en.json`, `el.json`, `ar.json`, `es.json`)
2. Use the key in your component with `t('namespace.key')`

Example:
```json
// en.json
{
  "myFeature": {
    "title": "My Feature",
    "description": "This is my feature"
  }
}

// el.json
{
  "myFeature": {
    "title": "Το Χαρακτηριστικό μου",
    "description": "Αυτό είναι το χαρακτηριστικό μου"
  }
}
```

### Using Parameters in Translations

```javascript
// Translation file
{
  "validation": {
    "minLength": "Minimum length is {{min}} characters"
  }
}

// Component
t('validation.minLength', { min: 8 })
// Output: "Minimum length is 8 characters"
```

### RTL Support

Arabic language automatically enables RTL (Right-to-Left) layout. The LocalizationContext provides utilities:

```javascript
import { useLocalization } from '../contexts/LocalizationContext';

function MyComponent() {
  const { isRTL, getTextDirection, getDirectionClass } = useLocalization();
  
  return (
    <div dir={getTextDirection()}>
      {/* Content automatically adjusts for RTL */}
    </div>
  );
}
```

### Formatting Utilities

```javascript
import { useLocalization } from '../contexts/LocalizationContext';

function MyComponent() {
  const { formatDate, formatNumber, formatCurrency } = useLocalization();
  
  return (
    <div>
      <p>{formatDate(new Date())}</p>
      <p>{formatNumber(1234.56)}</p>
      <p>{formatCurrency(99.99)}</p>
    </div>
  );
}
```

## Backend Setup

### Database Migration

Run the migration to add the `preferred_language` field:

```bash
docker-compose exec api alembic upgrade head
```

### User Schema

The `preferred_language` field is now part of:
- `UserBase` schema
- `UserUpdate` schema
- `UserResponse` schema

Accepted values: `en`, `el`, `ar`, `es`

## User Interface

### Setting Language Preference

1. **During User Creation**: Admins can set the preferred language when creating a new user
2. **User Profile**: Users can update their language preference in their profile settings
3. **Add User Form**: The language dropdown appears in the user creation/edit form

### Language Selection Options

- 🇬🇧 English
- 🇬🇷 Ελληνικά (Greek)
- 🇸🇦 العربية (Arabic)
- 🇪🇸 Español (Spanish)

## Migration Path

To migrate existing components to use translations:

1. Import the `useTranslation` hook
2. Replace hardcoded strings with `t('key')` calls
3. Add missing translation keys to all language files
4. Test in all supported languages

### Example Migration

**Before:**
```javascript
function MyComponent() {
  return <button>Save</button>;
}
```

**After:**
```javascript
import { useTranslation } from '../hooks/useTranslation';

function MyComponent() {
  const { t } = useTranslation();
  return <button>{t('common.save')}</button>;
}
```

## Best Practices

1. **Always add translations to all language files** - Don't leave any language incomplete
2. **Use descriptive keys** - `users.addUser` is better than `btn1`
3. **Group related translations** - Keep translations organized by feature/namespace
4. **Test RTL layout** - Always test Arabic to ensure layout works correctly
5. **Use parameters for dynamic content** - Don't concatenate strings
6. **Keep translations short** - UI space is limited, especially in buttons
7. **Be consistent** - Use the same terminology across the application

## Testing

To test different languages:
1. Create a user with different `preferred_language` values
2. Login as that user
3. Verify all UI elements are translated correctly
4. For Arabic, verify RTL layout works properly

## Future Enhancements

- Language switcher in user profile
- More languages (Turkish, Norwegian, etc.)
- Translation management UI
- Automatic translation suggestions
- Pluralization support
- Date/time format customization per user
