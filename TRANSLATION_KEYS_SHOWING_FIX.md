# Translation Keys Showing Instead of Values - Fix Guide

## Problem

In production, the AI Assistant is showing translation keys like `aiAssistant.messages.machineSelected` instead of the actual translated text like "Selected machine: AutoBoss 1 (V3.1B)".

## Root Cause

The production frontend hasn't been rebuilt with the latest translation files. The translation keys exist and are correct, but the build is outdated.

## Solution

Rebuild the frontend in production to load the updated translation files.

## Quick Fix (On Production Server)

```bash
cd ~/abparts
./fix_production_translations.sh
```

This script will:
1. Verify translation files exist
2. Check the machineSelected key is present
3. Rebuild the frontend (2-3 minutes)
4. Restart the web container
5. Verify the container is running

**Time: ~3-5 minutes**

## Manual Fix (If Script Fails)

```bash
# 1. Check translation files exist
docker compose exec web ls /app/src/locales/en.json

# 2. Rebuild frontend
docker compose exec web npm run build

# 3. Restart web container
docker compose restart web

# 4. Wait for container to start
sleep 5

# 5. Check status
docker compose ps web
```

## Diagnostic Tool

If you want to investigate the issue first:

```bash
./diagnose_translation_issue.sh
```

This will check:
- Translation files exist
- Keys are present in files
- Build directory status
- Build timestamp
- Container logs

## What Should Happen After Fix

### Before Fix
```
aiAssistant.messages.machineSelected
```

### After Fix
```
Selected machine: AutoBoss 1 (V3.1B)
```

## Testing After Fix

1. **Open AI Assistant** - Click the chat icon
2. **Select a machine** - Choose any machine from the dropdown
3. **Check the message** - Should show:
   - ✓ "Selected machine: [name] ([model])"
   - ✗ NOT "aiAssistant.messages.machineSelected"

4. **Test other translations**:
   - Step numbers: "Step 1" (not "Step {{number}}")
   - Time estimates: "5 min" (not "{{minutes}} min")
   - Success rates: "85% success rate" (not "{{rate}}% success rate")

5. **Test in Greek** (if applicable):
   - Switch language to Ελληνικά
   - Verify translations work
   - Switch back to English

## Browser Cache Issue

If translations still show as keys after the fix:

1. **Hard refresh the page**:
   - Chrome/Firefox: `Ctrl + Shift + R`
   - Mac: `Cmd + Shift + R`

2. **Clear browser cache**:
   - Chrome: Settings → Privacy → Clear browsing data
   - Firefox: Settings → Privacy → Clear Data

3. **Try incognito/private window**:
   - This bypasses cache completely

## Why This Happened

The translation files were updated in development with the correct `{{param}}` syntax, but the production frontend wasn't rebuilt. React bundles all translation files into the JavaScript build, so changes to JSON files require a rebuild.

## Prevention

Always rebuild the frontend after translation changes:

```bash
# After updating translation files
docker compose exec web npm run build
docker compose restart web
```

## Related Files

- `frontend/src/locales/en.json` - English translations
- `frontend/src/locales/el.json` - Greek translations
- `frontend/src/locales/ar.json` - Arabic translations
- `frontend/src/locales/es.json` - Spanish translations
- `frontend/src/locales/tr.json` - Turkish translations
- `frontend/src/locales/no.json` - Norwegian translations
- `frontend/src/hooks/useTranslation.js` - Translation hook
- `frontend/src/contexts/LocalizationContext.js` - Language context

## Translation Key Structure

The AI Assistant uses nested translation keys:

```json
{
  "aiAssistant": {
    "messages": {
      "machineSelected": "Selected machine: {{machineName}} ({{modelType}})",
      "machineCleared": "Machine selection cleared. Providing general assistance."
    },
    "troubleshooting": {
      "stepNumber": "Step {{number}}",
      "estimatedTime": "{{minutes}} min",
      "successRate": "{{rate}}% success rate"
    }
  }
}
```

Parameters are replaced using `{{paramName}}` syntax.

## Support

If the issue persists after running the fix:

1. Check logs: `docker compose logs web`
2. Check build: `docker compose exec web ls -lh /app/build/`
3. Verify files: `docker compose exec web grep "machineSelected" /app/src/locales/en.json`
4. Check container: `docker compose ps web`

## Summary

The fix is simple: rebuild the frontend. The translation system is working correctly, it just needs the latest build to include the updated translation files.

```bash
cd ~/abparts
./fix_production_translations.sh
```

Then test by selecting a machine in the AI Assistant chat.
