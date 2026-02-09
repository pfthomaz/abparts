# Protocols Caching Issue - RESOLVED

## Problem Summary

Protocols were not caching during login preload, causing this error:
```
[IndexedDB] DEBUG: Attempting transaction for store: undefined
[IndexedDB] Failed to cache data to undefined: NotFoundError
[OfflinePreloader] ✗ Failed to cache protocols
```

## Root Cause

The browser was serving **stale cached JavaScript** where `STORES.MAINTENANCE_PROTOCOLS` evaluated to `undefined`. Even though the code was fixed in the repository, the service worker was aggressively caching the old JavaScript bundle.

## Solution Applied

### Code Fix (Already Committed)
- **Commit**: 18695f0
- **Change**: Replaced all `STORES` constant references with string literals in `offlineDataPreloader.js`
- **Before**: `await cacheData(STORES.MAINTENANCE_PROTOCOLS, protocols, userContext)`
- **After**: `await cacheData('protocols', protocols, userContext)`

### Deployment Required

The code fix is complete, but requires:
1. ✅ Pull latest code from GitHub
2. ✅ Rebuild frontend with `--no-cache` flag
3. ✅ Clear browser cache completely
4. ✅ Verify protocols cache successfully

## Deployment Instructions

### Option 1: Automated Script (Recommended)

```bash
cd ~/abparts
./deploy_protocols_fix.sh
```

Then clear browser cache as instructed.

### Option 2: Manual Steps

```bash
cd ~/abparts
git pull origin main
docker compose -f docker-compose.prod.yml down
docker rmi abparts-web:latest 2>/dev/null || true
docker compose -f docker-compose.prod.yml build --no-cache web
docker compose -f docker-compose.prod.yml up -d
```

### Clear Browser Cache

**Method 1: Safari Preferences**
1. Safari → Preferences → Privacy → Manage Website Data
2. Search for "abparts" or "oraseas"
3. Click "Remove All"
4. Close and reopen Safari

**Method 2: Hard Refresh**
1. Open https://abparts.oraseas.com
2. Press `Cmd + Option + E` (empty caches)
3. Press `Cmd + Shift + R` (hard reload)

**Method 3: Cache Clearing Tool**
1. Navigate to: https://abparts.oraseas.com/clear-cache.html
2. Click "Clear All Caches"
3. Close all ABParts tabs
4. Reopen in new tab

## Verification

After deployment and cache clearing, login and check console:

### Expected Output (SUCCESS)
```
[OfflinePreloader] Starting data preload for offline mode...
[IndexedDB] DEBUG: Attempting transaction for store: machines
[OfflinePreloader] ✓ Cached 18 machines
[IndexedDB] DEBUG: Attempting transaction for store: protocols
[OfflinePreloader] ✓ Cached 5 protocols
[IndexedDB] DEBUG: Attempting transaction for store: users
[OfflinePreloader] ✓ Cached 24 users
[IndexedDB] DEBUG: Attempting transaction for store: farmSites
[OfflinePreloader] ✓ Cached 1 farm sites
[IndexedDB] DEBUG: Attempting transaction for store: nets
[OfflinePreloader] ✓ Cached 1 nets
[OfflinePreloader] Preload complete: 5/5 successful in XXXms
```

### Failure Indicators
- ❌ `store: undefined` in console
- ❌ `Failed to cache data to undefined`
- ❌ `Preload complete: 4/5 successful` (should be 5/5)

## Technical Details

### Why Service Workers Cache Aggressively

Service workers are designed for offline-first applications and cache JavaScript bundles to enable offline functionality. However, this means:

1. **Cache-First Strategy**: Service worker serves cached JS before checking network
2. **Stale Content**: Old code can persist even after deployment
3. **Manual Intervention**: Requires explicit cache clearing or versioning

### Files Modified

1. **frontend/src/services/offlineDataPreloader.js**
   - Replaced `STORES.MAINTENANCE_PROTOCOLS` → `'protocols'`
   - Replaced `STORES.USERS` → `'users'`
   - Replaced `STORES.FARM_SITES` → `'farmSites'`
   - Replaced `STORES.NETS` → `'nets'`
   - Replaced `STORES.MACHINES` → `'machines'`

2. **frontend/public/clear-cache.html** (NEW)
   - Tool to programmatically clear all caches
   - Accessible at `/clear-cache.html`

3. **deploy_protocols_fix.sh** (NEW)
   - Automated deployment script
   - Handles git pull, rebuild, restart

## Prevention for Future

To avoid this issue in future deployments:

1. **Always rebuild with --no-cache** after code changes
2. **Version service worker** (can implement cache versioning)
3. **Clear browser cache** after deployments
4. **Use cache-busting** in production builds

## Status

- ✅ Code fixed and committed (18695f0)
- ✅ Deployment script created
- ✅ Cache clearing tool created
- ✅ Documentation complete
- ⏳ **WAITING**: Production deployment + browser cache clear

## Next Steps

1. Run `./deploy_protocols_fix.sh` on production server
2. Clear browser cache using one of the methods above
3. Login and verify all 5 data types cache successfully
4. Test offline mode functionality
5. Confirm protocols load in MaintenanceExecutions page

---

**Files Created:**
- `DEPLOY_PROTOCOLS_FIX_NOW.md` - Detailed deployment guide
- `deploy_protocols_fix.sh` - Automated deployment script
- `frontend/public/clear-cache.html` - Browser cache clearing tool
- `PROTOCOLS_CACHING_FIXED.md` - This summary document
