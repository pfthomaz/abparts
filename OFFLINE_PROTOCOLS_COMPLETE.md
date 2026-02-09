# Offline Protocols - COMPLETE ✅

## Issues Fixed

### Issue 1: Protocols Not Caching
**Problem:** `STORES.PROTOCOLS` was `undefined` in cached JavaScript, causing protocols to fail caching during login.

**Solution:** Replaced all `STORES` constant references with string literals in `offlineDataPreloader.js`:
- `STORES.MAINTENANCE_PROTOCOLS` → `'protocols'`
- `STORES.USERS` → `'users'`
- `STORES.FARM_SITES` → `'farmSites'`
- `STORES.NETS` → `'nets'`
- `STORES.MACHINES` → `'machines'`

**Commit:** 18695f0

### Issue 2: Protocols Not Loading in Offline Mode
**Problem:** When offline, `getCachedData()` was called without `userContext`, triggering security warning and returning empty array.

**Solution:** Updated protocol service functions to accept and pass `userContext`:
1. `listProtocols(filters, forceRefresh, userContext)` - now accepts userContext
2. `getLocalizedProtocols(filters, userLanguage, forceRefresh, userContext)` - passes userContext through
3. `MaintenanceExecutions.js` - passes userContext when calling `getLocalizedProtocols()`

**Commit:** e8c4baf

## Files Modified

1. `frontend/src/services/offlineDataPreloader.js` - Use string literals instead of STORES constants
2. `frontend/src/services/maintenanceProtocolsService.js` - Accept and pass userContext
3. `frontend/src/pages/MaintenanceExecutions.js` - Pass userContext to protocol functions

## Deploy to Production

```bash
cd /path/to/abparts
git pull origin main
docker compose -f docker-compose.prod.yml down
docker compose -f docker-compose.prod.yml build --no-cache web
docker compose -f docker-compose.prod.yml up -d
```

## Clear Browser Cache (REQUIRED!)

After deploying, clear browser cache completely:

```javascript
(async function() {
  const regs = await navigator.serviceWorker.getRegistrations();
  for (let reg of regs) await reg.unregister();
  const names = await caches.keys();
  for (let name of names) await caches.delete(name);
  indexedDB.deleteDatabase('ABPartsOfflineDB');
  setTimeout(() => location.reload(true), 2000);
})();
```

## Expected Result

**On Login (Online):**
```
[OfflinePreloader] Starting data preload for offline mode...
[OfflinePreloader] ✓ Cached 18 machines
[OfflinePreloader] ✓ Cached X protocols  ✅
[OfflinePreloader] ✓ Cached 24 users
[OfflinePreloader] ✓ Cached 1 farm sites
[OfflinePreloader] ✓ Cached 1 nets
[OfflinePreloader] Preload complete: 5/5 successful
```

**In Offline Mode:**
- Protocols load from IndexedDB cache
- No security warnings
- Maintenance Executions page works offline

## Verify

```javascript
// Check protocols in IndexedDB
const request = indexedDB.open('ABPartsOfflineDB', 3);
request.onsuccess = function(event) {
  const db = event.target.result;
  const tx = db.transaction('protocols', 'readonly');
  const store = tx.objectStore('protocols');
  const countRequest = store.count();
  countRequest.onsuccess = function() {
    console.log('✅ Protocols in IndexedDB:', countRequest.result);
  };
};
```

## How It Works

1. **On Login:** `offlineDataPreloader.js` fetches protocols from API and caches them with user context
2. **Online Mode:** `listProtocols()` fetches from API, falls back to cache if API fails
3. **Offline Mode:** `listProtocols()` reads from IndexedDB cache using user context for security
4. **Security:** All cache operations require user context to prevent cross-user data leakage

## Security Features

- User-scoped caching: Each user only sees their organization's protocols
- Super admins see all protocols
- Cache operations without user context are blocked with security warnings
- Data is filtered by organization_id before being returned

