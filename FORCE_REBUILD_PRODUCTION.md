# Force Complete Rebuild - Clear All Caches

The issue is that the production build has stale/cached JavaScript. We need to force a complete rebuild.

## On Production Server - Run These Commands

```bash
cd ~/abparts

# 1. Pull latest code
git pull origin main

# 2. Stop all containers
docker compose -f docker-compose.prod.yml down

# 3. Remove the web image completely
docker rmi abparts-web || true

# 4. Remove node_modules volume if it exists
docker volume rm abparts_node_modules || true

# 5. Build with NO cache
docker compose -f docker-compose.prod.yml build --no-cache --pull web

# 6. Start containers
docker compose -f docker-compose.prod.yml up -d

# 7. Check logs
docker compose -f docker-compose.prod.yml logs -f web
```

## In Browser

1. Open https://abparts.oraseas.com
2. Press **Ctrl+Shift+Delete** (or Cmd+Shift+Delete on Mac)
3. Select "Cached images and files"
4. Click "Clear data"
5. Close browser completely
6. Reopen browser
7. Go to https://abparts.oraseas.com
8. Press F12 (DevTools)
9. Go to Console tab
10. Hard refresh: **Cmd+Shift+R** (Mac) or **Ctrl+Shift+R** (Windows)
11. Login

## What to Look For

You should see these logs appear IN ORDER:

```
[OfflinePreloader] Module loaded, STORES = {FARM_SITES: 'farmSites', NETS: 'nets', ...}
[OfflinePreloader] STORES.PROTOCOLS = protocols
[Auth] ✓ Cleared stale cache on login
[OfflinePreloader] Starting data preload for offline mode...
[IndexedDB] DEBUG: Attempting transaction for store: machines
[OfflinePreloader] ✓ Cached 18 machines
[OfflinePreloader] ========== PROTOCOLS SECTION START ==========
[OfflinePreloader] DEBUG: Starting protocols fetch, STORES.PROTOCOLS = protocols
[OfflinePreloader] DEBUG: typeof STORES.PROTOCOLS = string
[OfflinePreloader] DEBUG: STORES = {FARM_SITES: 'farmSites', ...}
```

If you see `store: undefined` BEFORE the "PROTOCOLS SECTION START" line, then something else is calling cacheData incorrectly.

## If It Still Fails

Check the browser console for the FULL error stack trace and paste it here. We need to see exactly which file and line is calling `cacheData` with `undefined`.
