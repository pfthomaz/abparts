# Fix Protocols Caching - Quick Start

## The Problem

Safari is showing this error:
```
[IndexedDB] DEBUG: Attempting transaction for store: undefined
[OfflinePreloader] ✗ Failed to cache protocols
```

This means the browser is using **old cached JavaScript** where the variable is undefined.

## The Solution (3 Steps)

### Step 1: Deploy on Production Server

SSH to production and run:

```bash
cd ~/abparts
./deploy_protocols_fix.sh
```

This will:
- Pull latest code
- Rebuild frontend with no cache
- Restart containers

### Step 2: Clear Browser Cache

**Option A - Safari Preferences:**
1. Safari → Preferences → Privacy
2. Click "Manage Website Data"
3. Search for "abparts"
4. Click "Remove All"
5. Close Safari completely
6. Reopen Safari

**Option B - Use Clear Cache Tool:**
1. Open: https://abparts.oraseas.com/clear-cache.html
2. Click "Clear All Caches"
3. Close all ABParts tabs
4. Reopen in new tab

**Option C - Hard Refresh:**
1. Open https://abparts.oraseas.com
2. Press `Cmd + Option + E` (empty caches)
3. Press `Cmd + Shift + R` (hard reload)

### Step 3: Verify It Works

Login and check console. You should see:

```
[OfflinePreloader] Starting data preload for offline mode...
[OfflinePreloader] ✓ Cached 18 machines
[OfflinePreloader] ✓ Cached 5 protocols    ← This should appear now!
[OfflinePreloader] ✓ Cached 24 users
[OfflinePreloader] ✓ Cached 1 farm sites
[OfflinePreloader] ✓ Cached 1 nets
[OfflinePreloader] Preload complete: 5/5 successful
```

## Why This Happened

The service worker cached old JavaScript where `STORES.MAINTENANCE_PROTOCOLS` was undefined. Even though we fixed the code, the browser kept serving the old cached version.

## Files to Help You

- `DEPLOY_PROTOCOLS_FIX_NOW.md` - Detailed explanation
- `PROTOCOLS_CACHING_FIXED.md` - Complete technical summary
- `deploy_protocols_fix.sh` - Automated deployment script
- `frontend/public/clear-cache.html` - Browser cache clearing tool

---

**TL;DR**: Run `./deploy_protocols_fix.sh` on server, then clear Safari cache. Done!
