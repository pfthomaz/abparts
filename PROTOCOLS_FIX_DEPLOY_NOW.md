# Deploy Protocols Caching Fix - FINAL

## The Fix

Changed `frontend/src/services/offlineDataPreloader.js` to use **string literals** instead of `STORES` constants to avoid undefined errors in cached JavaScript.

## Deploy to Production (Run on Production Server)

```bash
# SSH to production
ssh diogo@ubuntu-8gb-hel1-2

# Navigate to project
cd /path/to/abparts

# Pull latest changes
git pull origin main

# Stop containers
docker compose -f docker-compose.prod.yml down

# Rebuild web container with NO CACHE (critical!)
docker compose -f docker-compose.prod.yml build --no-cache web

# Start containers
docker compose -f docker-compose.prod.yml up -d

# Check logs
docker compose -f docker-compose.prod.yml logs web | tail -30
```

## After Deployment - Clear Browser Cache

**CRITICAL:** You MUST clear browser cache completely, even in Safari:

### Option 1: JavaScript in Console

```javascript
// Run this in browser console at https://abparts.oraseas.com
(async function() {
  // Unregister service workers
  const regs = await navigator.serviceWorker.getRegistrations();
  for (let reg of regs) await reg.unregister();
  
  // Clear caches
  const names = await caches.keys();
  for (let name of names) await caches.delete(name);
  
  // Clear IndexedDB
  indexedDB.deleteDatabase('ABPartsOfflineDB');
  
  // Reload
  setTimeout(() => location.reload(true), 2000);
})();
```

### Option 2: Manual (Safari)

1. Safari → Settings → Privacy → Manage Website Data
2. Find `abparts.oraseas.com`
3. Click "Remove"
4. Close Safari COMPLETELY (Cmd+Q)
5. Reopen Safari
6. Go to https://abparts.oraseas.com
7. Login

### Option 3: Developer Tools (Safari)

1. Open Developer Tools (Cmd+Option+I)
2. Go to Storage tab
3. Right-click on domain → Clear
4. Close browser completely
5. Reopen and test

## Expected Result

After clearing cache, you should see in console:

```
[OfflinePreloader] Starting data preload for offline mode...
[OfflinePreloader] ========== PROTOCOLS SECTION START ==========
[OfflinePreloader] DEBUG: Fetched protocols from API, count = X
[OfflinePreloader] ✓ Cached X protocols          <-- THIS SHOULD WORK!
[OfflinePreloader] ✓ Cached 18 machines
[OfflinePreloader] ✓ Cached 24 users
[OfflinePreloader] ✓ Cached 1 farm sites
[OfflinePreloader] ✓ Cached 1 nets
[OfflinePreloader] Preload complete: 5/5 successful in XXXms
```

## Verify Protocols in IndexedDB

Run in console:

```javascript
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

## If Still Not Working

If you still see `store: undefined` error after all steps:

1. **Check git commit on production:**
   ```bash
   cd /path/to/abparts
   git log --oneline -1
   # Should show: "fix protocols offline mode" or similar
   ```

2. **Verify the file was updated:**
   ```bash
   grep "await cacheData('protocols'" frontend/src/services/offlineDataPreloader.js
   # Should show the line with string literal 'protocols'
   ```

3. **Check build output:**
   ```bash
   docker compose -f docker-compose.prod.yml logs web | grep -i "webpack\|compiled"
   ```

4. **Try incognito/private browsing mode** - this ensures NO cached files

5. **Check if there's a CDN or proxy caching** - nginx might be caching static files

## Why This Fixes It

The old code used `STORES.PROTOCOLS` which was `undefined` in cached JavaScript bundles. By using the string literal `'protocols'` directly, we bypass any import/constant resolution issues and directly reference the IndexedDB store name.

