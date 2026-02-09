# Deploy IndexedDB Protocols Fix - COMPLETE SOLUTION

## THE PROBLEM

The service worker is caching OLD JavaScript files. Even though we've rebuilt production multiple times, the browser is serving cached JavaScript that doesn't have our fixes.

**Evidence:**
- Error shows `store: undefined` (old code)
- Module-level debug logs NEVER appear (should show `[OfflinePreloader] Module loaded, STORES = ...`)
- Console shows: `[Service Worker] Serving from cache: https://abparts.oraseas.com/static/js/754.9a5ad9e4.chunk.js`

## THE SOLUTION - 3 STEPS

### STEP 1: Force Service Worker to Update (On Production Server)

The service worker needs to be updated so it stops serving old cached files.

**Option A: Increment Cache Version (RECOMMENDED)**

```bash
# SSH to production server
ssh diogo@ubuntu-8gb-hel1-2

# Navigate to project
cd /path/to/abparts

# Edit service worker to force cache invalidation
nano frontend/public/service-worker.js
```

Change line 5 from:
```javascript
const CACHE_VERSION = 'abparts-offline-v1';
```

To:
```javascript
const CACHE_VERSION = 'abparts-offline-v2';  // <-- INCREMENT THIS
```

**Option B: Disable Service Worker Temporarily**

```bash
# Rename service worker to disable it
cd /path/to/abparts
mv frontend/public/service-worker.js frontend/public/service-worker.js.disabled
```

### STEP 2: Rebuild Frontend Container

```bash
# Stop containers
docker compose -f docker-compose.prod.yml down

# Rebuild web container with NO CACHE
docker compose -f docker-compose.prod.yml build --no-cache web

# Start containers
docker compose -f docker-compose.prod.yml up -d

# Verify build
docker compose -f docker-compose.prod.yml logs web | tail -20
```

### STEP 3: Clear Browser Cache (CRITICAL!)

**In Browser Console - Run This JavaScript:**

```javascript
// 1. Unregister ALL service workers
navigator.serviceWorker.getRegistrations().then(function(registrations) {
  for(let registration of registrations) {
    registration.unregister();
    console.log('✓ Unregistered:', registration.scope);
  }
  console.log('✓ All service workers unregistered!');
});

// 2. Clear all caches
caches.keys().then(function(names) {
  for (let name of names) {
    caches.delete(name);
    console.log('✓ Deleted cache:', name);
  }
  console.log('✓ All caches cleared!');
});

// 3. Clear IndexedDB
indexedDB.deleteDatabase('ABPartsOfflineDB').onsuccess = function() {
  console.log('✓ IndexedDB cleared!');
};

// 4. Reload after 2 seconds
setTimeout(() => {
  console.log('✓ Reloading page with fresh cache...');
  location.reload(true);
}, 2000);
```

**OR Manually:**

1. Open DevTools (F12)
2. Go to **Application** tab
3. **Service Workers** → Click **Unregister**
4. **Cache Storage** → Right-click each cache → **Delete**
5. **IndexedDB** → Right-click ABPartsOfflineDB → **Delete**
6. **Storage** → Click **Clear site data**
7. Close browser COMPLETELY
8. Reopen browser
9. Go to https://abparts.oraseas.com
10. Hard refresh: **Cmd+Shift+R** (Mac) or **Ctrl+Shift+R** (Windows)

## VERIFICATION

After completing all 3 steps, you should see these logs in console:

```
[OfflinePreloader] Module loaded, STORES = {FARM_SITES: 'farmSites', NETS: 'nets', MACHINES: 'machines', PROTOCOLS: 'protocols', ...}
[OfflinePreloader] STORES.PROTOCOLS = protocols
[OfflinePreloader] Starting data preload for offline mode...
[OfflinePreloader] ========== PROTOCOLS SECTION START ==========
[OfflinePreloader] DEBUG: Starting protocols fetch, STORES.PROTOCOLS = protocols
[OfflinePreloader] ✓ Cached 18 machines
[OfflinePreloader] ✓ Cached X protocols  <-- THIS SHOULD WORK NOW!
[OfflinePreloader] ✓ Cached 24 users
[OfflinePreloader] ✓ Cached 1 farm sites
[OfflinePreloader] ✓ Cached 1 nets
[OfflinePreloader] Preload complete: 5/5 successful in XXXms
```

**Check IndexedDB:**

```javascript
// Run in console to verify protocols are cached
indexedDB.databases().then(dbs => console.log('Databases:', dbs));

// Open database and check protocols store
const request = indexedDB.open('ABPartsOfflineDB', 3);
request.onsuccess = function(event) {
  const db = event.target.result;
  console.log('Database version:', db.version);
  console.log('Object stores:', Array.from(db.objectStoreNames));
  
  // Check protocols count
  const tx = db.transaction('protocols', 'readonly');
  const store = tx.objectStore('protocols');
  const countRequest = store.count();
  countRequest.onsuccess = function() {
    console.log('Protocols in IndexedDB:', countRequest.result);
  };
};
```

## WHY THIS HAPPENS

Service workers are VERY aggressive about caching. They cache JavaScript files to enable offline functionality, but this means:

1. When you rebuild the frontend, new JavaScript is generated
2. But the service worker serves the OLD cached JavaScript
3. The browser never sees the new code
4. Even hard refresh doesn't help because service worker intercepts the request

**The fix:** Increment the cache version in service-worker.js, which forces the service worker to delete old caches and fetch fresh files.

## IF IT STILL DOESN'T WORK

If protocols still don't cache after all 3 steps:

1. Check if service worker is registered:
```javascript
navigator.serviceWorker.getRegistrations().then(r => console.log('Registrations:', r));
```

2. Check if there are any console errors during preload

3. Verify the API returns protocols:
```javascript
fetch('/api/maintenance-protocols/', {
  headers: {
    'Authorization': `Bearer ${localStorage.getItem('token')}`
  }
}).then(r => r.json()).then(d => console.log('Protocols from API:', d));
```

4. Check if there's a CDN or nginx cache in front of the application that's also caching old files

## ALTERNATIVE: Disable Service Worker Completely

If you want to disable offline functionality temporarily to fix this:

```bash
# On production server
cd /path/to/abparts
mv frontend/public/service-worker.js frontend/public/service-worker.js.disabled

# Rebuild
docker compose -f docker-compose.prod.yml build --no-cache web
docker compose -f docker-compose.prod.yml up -d
```

Then in browser, unregister service worker and clear all caches as shown above.

