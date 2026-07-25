# Deploy Farm Sites Cache Fix - Service Worker Update

## Problem Summary
Farm sites dropdown is empty when offline because the browser is serving OLD cached JavaScript code that doesn't pass `userContext` to cache operations. This causes security warnings and prevents data from being cached.

## Root Cause
Service worker is caching JavaScript files aggressively. Even though we fixed the code in commits 81f4e7a and 7a5fc93, the browser continues serving the old cached version.

**Evidence from console logs:**
```
farmSitesService.js:55  [IndexedDB] SECURITY WARNING: Caching without user context
netsService.js:62       [IndexedDB] SECURITY WARNING: Caching without user context
```

These line numbers (55, 62) are from the OLD code BEFORE the fix. The NEW code has these calls on different lines with userContext parameter.

## Solution Applied
✅ Bumped service worker cache version from `'abparts-offline-v1'` to `'abparts-offline-v2'`

This forces the browser to:
1. Delete old cached JavaScript files
2. Download and cache NEW JavaScript files with the fixes
3. Run the corrected code that passes userContext

## Deployment Steps

### 1. Commit and Push Changes
```bash
git add frontend/public/service-worker.js
git commit -m "Bump service worker cache version to v2 - force browser to load fixed farm sites code"
git push origin main
```

### 2. Pull on Production Server
```bash
ssh diogo@ubuntu-8gb-hel1-2
cd /root/abparts
git pull origin main
```

### 3. Rebuild Web Container
```bash
docker compose -f docker-compose.prod.yml build web
docker compose -f docker-compose.prod.yml up -d web
```

### 4. Clear Browser Cache (CRITICAL!)
On your browser:
1. Open DevTools (F12)
2. Go to **Application** tab
3. Click **Clear site data** (left sidebar)
4. Check ALL boxes:
   - ✅ Unregister service workers
   - ✅ Local and session storage
   - ✅ IndexedDB
   - ✅ Cache storage
5. Click **Clear site data** button
6. Close DevTools

### 5. Hard Refresh Browser
```
Cmd + Shift + R (Mac)
Ctrl + Shift + R (Windows/Linux)
```

### 6. Login Again
1. Login to trigger data preload
2. Open DevTools Console
3. **Verify NO security warnings:**
   ```
   ✅ Should see: [OfflinePreloader] ✓ Cached 1 farm sites
   ❌ Should NOT see: [IndexedDB] SECURITY WARNING: Caching without user context
   ```

### 7. Test Offline Net Cleaning
1. Go to **Net Cleaning Records** page
2. Click **Add Record** button
3. **Verify farm sites dropdown is populated**
4. Go offline (DevTools → Network → Offline)
5. Refresh page
6. Click **Add Record** again
7. **Verify farm sites dropdown STILL populated**

## Expected Console Output (After Fix)
```
[OfflinePreloader] Starting data preload for offline mode...
[OfflinePreloader] ✓ Cached 18 machines
[OfflinePreloader] ✓ Cached 6 protocols
[OfflinePreloader] ✓ Cached 24 users
[OfflinePreloader] ✓ Cached 1 farm sites    ← NO security warning!
[OfflinePreloader] ✓ Cached 1 nets          ← NO security warning!
[OfflinePreloader] Preload complete: 5/5 successful in 650ms

[FarmSitesService] Using cached data, userContext: {userId: '...', organizationId: '...', isSuperAdmin: true}
[FarmSitesService] Retrieved from cache: 1 farm sites
[FarmSitesService] After active filter: 1 farm sites
[FarmSitesService] After pagination: 1 farm sites

[NetCleaningRecordForm] Received props: {farmSitesCount: 1, farmSites: Array(1), ...}  ← Count = 1!
```

## What Changed
**File:** `frontend/public/service-worker.js`
- Line 4: `CACHE_VERSION = 'abparts-offline-v1'` → `'abparts-offline-v2'`

This single change forces the browser to invalidate ALL cached JavaScript and download fresh copies.

## Why This Works
1. Service worker sees new cache version
2. Activates and deletes old `abparts-offline-v1-*` caches
3. Creates new `abparts-offline-v2-*` caches
4. Downloads fresh JavaScript files with the fixes
5. Browser runs NEW code that passes userContext
6. Data caches successfully without security warnings
7. Farm sites dropdown works offline

## Troubleshooting
If farm sites dropdown is still empty after deployment:

1. **Check service worker version:**
   - DevTools → Application → Service Workers
   - Should show "waiting to activate" or "activated"
   - Click "Unregister" if stuck

2. **Verify cache version in console:**
   ```javascript
   caches.keys().then(console.log)
   // Should show: ["abparts-offline-v2-static", "abparts-offline-v2-dynamic", ...]
   ```

3. **Check for security warnings:**
   - If you still see "SECURITY WARNING: Caching without user context"
   - Browser is STILL serving old code
   - Try incognito/private window
   - Or bump version to v3

4. **Verify IndexedDB has data:**
   - DevTools → Application → IndexedDB → ABPartsOfflineDB → farmSites
   - Should see 1 record with your farm site data

## Files Modified
- ✅ `frontend/public/service-worker.js` - Bumped cache version to v2

## Related Commits
- 81f4e7a - Pass userContext to getFarmSites() and getNets() in offlineDataPreloader
- 7a5fc93 - Pass userContext to cacheData() in farmSitesService and netsService
- (This commit) - Bump service worker cache version to force browser update

---
**Status:** Ready to deploy
**Risk:** Low - only changes cache version number
**Rollback:** Change version back to v1 if issues occur
