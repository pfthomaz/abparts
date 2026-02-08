# Deploy IndexedDB Fix - RIGHT NOW

## What I Fixed
Incremented IndexedDB version from 2 to 3 to force schema upgrade and create the missing `protocols` store.

## Deploy to Production (Run These Commands)

```bash
# On production server
cd ~/abparts
git pull origin main
docker compose -f docker-compose.prod.yml build --no-cache web
docker compose -f docker-compose.prod.yml up -d web
```

## In Your Browser (CRITICAL STEP)

**You MUST delete the old database:**

1. Open https://abparts.oraseas.com
2. Press **F12** (DevTools)
3. Go to: **Application** tab > **Storage** > **IndexedDB**
4. Right-click on **"ABPartsOfflineDB"**
5. Click **"Delete database"**
6. Press **Cmd+Shift+R** (hard refresh)
7. **Login**

## Verify It Works

Check the console - you should see:
```
[OfflinePreloader] Starting data preload for offline mode...
[OfflinePreloader] ✓ Cached 18 machines
[OfflinePreloader] ✓ Cached X protocols  ← THIS SHOULD APPEAR NOW!
[OfflinePreloader] ✓ Cached 24 users
[OfflinePreloader] ✓ Cached X farm sites
[OfflinePreloader] ✓ Cached X nets
[OfflinePreloader] Preload complete: 5/5 successful
```

Check IndexedDB:
- F12 > Application > IndexedDB > ABPartsOfflineDB > **protocols** ← Should have data!

---

**Why this works:** The old database (version 2) didn't have the protocols store. By incrementing to version 3, the browser will run the upgrade function and create all missing stores including protocols.
