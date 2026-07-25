# Debug Translation Keys Issue

## Run Diagnostics First

On production server:
```bash
./check_production_build.sh
```

This will show:
- If the build is recent
- If translations are in the JavaScript bundles
- If source files have the correct keys

## Browser Console Check

1. Open your browser
2. Press `F12` to open Developer Tools
3. Go to **Console** tab
4. Look for errors related to:
   - `Translation key not found`
   - `useTranslation`
   - `LocalizationContext`
   - Failed to load modules

## Common Issues

### Issue 1: Browser Cache
**Symptom**: Old JavaScript still loading

**Fix**:
```bash
# Hard refresh
Ctrl + Shift + R (Windows/Linux)
Cmd + Shift + R (Mac)

# Or clear all cache
Browser Settings → Privacy → Clear browsing data → Cached images and files
```

### Issue 2: Build Didn't Include Translations
**Symptom**: `machineSelected` not found in JavaScript bundles (Check 4 in diagnostics)

**Fix**:
```bash
# On production server
cd ~/abparts

# Verify translation files exist
cat frontend/src/locales/en.json | grep machineSelected

# If missing, pull latest code
git pull origin main

# Rebuild
./rebuild_frontend_production.sh
```

### Issue 3: LocalizationContext Not Loading
**Symptom**: Console shows "Cannot read property 'currentLanguage' of undefined"

**Check**:
1. Is `LocalizationContext.js` in the source?
2. Is `useTranslation.js` importing it correctly?
3. Is `App.js` wrapping components with `LocalizationProvider`?

### Issue 4: Translation Files Not Imported
**Symptom**: `machineSelected` in bundles but still showing as key

**Check `useTranslation.js`**:
```javascript
// Should have these imports
import enTranslations from '../locales/en.json';
import elTranslations from '../locales/el.json';
// ... etc

const translations = {
  en: enTranslations,
  el: elTranslations,
  // ... etc
};
```

## Manual Verification Steps

### Step 1: Check Source Files
```bash
# On production server
cd ~/abparts

# Check translation file exists
ls -la frontend/src/locales/en.json

# Check key exists
grep "machineSelected" frontend/src/locales/en.json

# Should show:
# "machineSelected": "Selected machine: {{machineName}} ({{modelType}})",
```

### Step 2: Check Build Output
```bash
# Check if build directory exists
docker compose exec web ls /usr/share/nginx/html/

# Check JavaScript bundles
docker compose exec web find /usr/share/nginx/html/static/js -name "*.js"

# Search for translation in bundles
docker compose exec web grep -r "machineSelected" /usr/share/nginx/html/static/js/
```

### Step 3: Check Container Logs
```bash
# Check for build errors
docker compose logs web --tail=100

# Look for:
# - npm build errors
# - Module not found errors
# - Syntax errors
```

### Step 4: Test in Incognito
1. Open incognito/private window
2. Go to your site
3. Test AI Assistant
4. If it works in incognito → Browser cache issue
5. If still broken → Build issue

## Nuclear Option: Complete Rebuild

If nothing else works:

```bash
cd ~/abparts

# Pull latest code
git pull origin main

# Stop everything
docker compose down

# Remove web image
docker rmi abparts-web

# Rebuild from scratch
docker compose build --no-cache --pull web

# Start
docker compose up -d web

# Wait 10 seconds
sleep 10

# Check status
docker compose ps web
```

Then:
1. Clear browser cache completely
2. Close browser
3. Reopen browser
4. Go to site
5. Test

## Check Network Tab

1. Open browser DevTools (F12)
2. Go to **Network** tab
3. Reload page
4. Look for JavaScript files being loaded
5. Check their timestamps
6. If timestamps are old → Browser cache issue

## Verify Translation Hook

Check browser console:
```javascript
// Type this in console
localStorage.getItem('preferredLanguage')

// Should show: "en" or "el" etc.
```

## Contact Info

If still not working, provide:
1. Output of `./check_production_build.sh`
2. Browser console errors (screenshot)
3. Network tab showing JS file timestamps
4. Output of `docker compose logs web --tail=50`
