# Deploy Protocols Caching Fix - IMMEDIATE ACTION REQUIRED

## Problem Identified

The browser is using **OLD cached JavaScript** where `STORES.MAINTENANCE_PROTOCOLS` is `undefined`. Even though we fixed the code, the service worker is serving stale JavaScript bundles.

## Root Cause

```
[IndexedDB] DEBUG: Attempting transaction for store: undefined
```

This means the JavaScript variable `STORES.MAINTENANCE_PROTOCOLS` evaluates to `undefined` in the cached bundle.

## Solution: Force Complete Cache Clear

### Step 1: Pull Latest Code on Production

```bash
cd ~/abparts
git pull origin main
```

### Step 2: Rebuild Frontend with Cache Busting

```bash
# Stop containers
docker compose -f docker-compose.prod.yml down

# Remove old frontend image to force rebuild
docker rmi abparts-web:latest 2>/dev/null || true

# Rebuild with no cache
docker compose -f docker-compose.prod.yml build --no-cache web

# Start containers
docker compose -f docker-compose.prod.yml up -d
```

### Step 3: Clear Browser Cache (CRITICAL!)

**In Safari:**
1. Open Safari menu → Preferences → Privacy
2. Click "Manage Website Data"
3. Search for "abparts" or "oraseas"
4. Click "Remove All" or select and "Remove"
5. Close and reopen Safari

**Alternative - Hard Refresh:**
1. Open https://abparts.oraseas.com
2. Press **Cmd + Option + E** (to empty caches)
3. Then press **Cmd + Shift + R** (hard reload)

**Alternative - Developer Tools:**
1. Open Safari → Develop → Show Web Inspector
2. Go to Storage tab
3. Right-click on "Service Workers" → Unregister
4. Right-click on "Cache Storage" → Delete
5. Right-click on "IndexedDB" → Delete "ABPartsDB"
6. Close inspector and hard refresh (Cmd + Shift + R)

### Step 4: Verify Fix

After clearing cache, login and check console:

**Expected (GOOD):**
```
[OfflinePreloader] Starting data preload for offline mode...
[IndexedDB] DEBUG: Attempting transaction for store: protocols
[OfflinePreloader] ✓ Cached 5 protocols
```

**Not Expected (BAD):**
```
[IndexedDB] DEBUG: Attempting transaction for store: undefined
[IndexedDB] Failed to cache data to undefined
```

## Why This Happened

1. Service worker caches JavaScript bundles aggressively
2. Even after deploying new code, browser serves old cached JS
3. The old JS has `STORES.MAINTENANCE_PROTOCOLS = undefined`
4. IndexedDB tries to open transaction on store named `undefined` → fails

## Prevention

After any code deployment that changes service files:
1. Always rebuild with `--no-cache`
2. Always clear browser cache
3. Consider versioning service worker (we can implement this)

## Current Status

- ✅ Code is fixed in repository (commit 18695f0)
- ✅ String literals used instead of STORES constants
- ⏳ **WAITING**: Production deployment + browser cache clear

## Next Steps

1. Deploy using steps above
2. Clear browser cache completely
3. Test in fresh Safari window
4. Verify protocols cache successfully
5. Test offline mode works

---

**IMPORTANT**: The fix is already in the code. The only issue is stale cached JavaScript in the browser. Once you clear the cache, it will work immediately.
