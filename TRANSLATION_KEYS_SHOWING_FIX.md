# Translation Keys Fixed - Machine Selected Label

## Issue
The Greek language (and potentially other non-English languages) were showing the translation key `aiAssistant.messages.machineSelected` instead of the translated value when a machine was selected in the AI Assistant.

## Root Cause
The `machineSelected` key was missing from the `aiAssistant.messages` section in several translation files:
- Greek (el.json) ❌
- Arabic (ar.json) ❌  
- Turkish (tr.json) ❌
- Norwegian (no.json) ❌

English and Spanish already had the key.

## Solution Applied
Added the missing translation keys to all affected language files:

### Greek (el.json)
```json
"machineSelected": "Επιλεγμένο μηχάνημα: {{machineName}} ({{modelType}})"
```

### Arabic (ar.json)
```json
"machineSelected": "الآلة المحددة: {{machineName}} ({{modelType}})"
```

### Turkish (tr.json)
```json
"machineSelected": "Seçilen makine: {{machineName}} ({{modelType}})"
```

### Norwegian (no.json)
```json
"machineSelected": "Valgt maskin: {{machineName}} ({{modelType}})"
```

Also added related missing keys:
- `machineCleared` - Message when machine selection is cleared
- `escalationCreated` - Message when support ticket is created
- `expertContact` - Expert contact information format
- `escalationError` - Error message for failed escalation

## Files Modified
- `frontend/src/locales/el.json`
- `frontend/src/locales/ar.json`
- `frontend/src/locales/tr.json`
- `frontend/src/locales/no.json`

## Deployment
Web container restarted to apply changes:
```bash
docker compose restart web
```

## Testing Instructions
1. **Hard refresh your browser** to clear cached JavaScript:
   - Chrome/Edge: `Ctrl+Shift+R` (Windows) or `Cmd+Shift+R` (Mac)
   - Firefox: `Ctrl+F5` (Windows) or `Cmd+Shift+R` (Mac)

2. Change language to Greek (or any other affected language)

3. Open AI Assistant

4. Select a machine from the dropdown

5. Verify the label shows: "Επιλεγμένο μηχάνημα: [Machine Name] ([Model])" instead of the translation key

## Status
✅ **COMPLETE** - All translation keys added and web container restarted.

The issue should now be resolved for all languages after a hard browser refresh.
