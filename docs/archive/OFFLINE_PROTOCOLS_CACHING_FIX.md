# Offline Protocols Caching Fix - Deployment Guide

## Problem Summary

Protocols were not being cached in IndexedDB during offline data preload, causing the following errors:

```
[IndexedDB] SECURITY WARNING: Caching without user context - data will not be cached
[IndexedDB] Failed to cache data to undefined: NotFoundError
[OfflinePreloader] ✗ Failed to cache protocols: NotFoundError
```

## Root Cause

The `listProtocols()` function in `maintenanceProtocolsService.js` was calling `cacheData(STORES.PROTOCOLS, data)` without passing the required `userContext` parameter. The `cacheData()` function requires user context for security (to prevent cross-user data leakage).

## Solution Applied

Modified `offlineDataPreloader.js` to fetch protocols directly from the API with proper authentication and user context, bypassing the problematic `listProtocols()` function:

```javascript
// Fetch protocols directly from API
const response = await fetch(`${process.env.REACT_APP_API_BASE_URL || ''}/api/maintenance-protocols/`, {
  headers: {
    'Authorization': `Bearer ${localStorage.getItem('token')}`,
    'Content-Type': 'application/json'
  }
});

const protocols = await response.json();

// Cache protocols with user context
await cacheData(STORES.PROTOCOLS, protocols, userContext);
```

## Deployment Steps

### On Production Server

Run the deployment script:

```bash
cd ~/abparts
./deploy_offline_protocols_fix.sh
```

Or manually:

```bash
# 1. Pull latest code
cd ~/abparts
git pull origin main

# 2. Rebuild web container (no cache)
docker compose -f docker-compose.prod.yml build --no-cache web

# 3. Restart web container
docker compose -f docker-compose.prod.yml up -d web
```

### In Browser

1. Open https://abparts.oraseas.com
2. Open DevTools (F12) > Application > Storage > IndexedDB
3. **Delete the 'ABPartsOfflineDB' database** (right-click > Delete)
4. Hard refresh the page (Cmd+Shift+R on Mac, Ctrl+Shift+R on Windows)
5. Login with your credentials
6. Check DevTools Console for preload messages

## Verification

### Expected Console Output

```
[Auth] ✓ Cleared stale cache on login
[OfflinePreloader] Starting data preload for offline mode...
[OfflinePreloader] ✓ Cached 18 machines
[OfflinePreloader] ✓ Cached X protocols  <-- Should see this now!
[OfflinePreloader] ✓ Cached 24 users
[OfflinePreloader] ✓ Cached X farm sites
[OfflinePreloader] ✓ Cached X nets
[OfflinePreloader] Preload complete: 5/5 successful in XXXms
```

### Check IndexedDB

1. Open DevTools > Application > Storage > IndexedDB
2. Expand 'ABPartsOfflineDB'
3. Click on 'protocols' store
4. You should see all protocols listed with their data

### Test Offline Mode

1. After successful preload, open DevTools > Network tab
2. Check "Offline" checkbox to simulate offline mode
3. Navigate to Maintenance > Protocols
4. Protocols should load from IndexedDB cache
5. You should be able to view protocol details offline

## Files Modified

- `frontend/src/services/offlineDataPreloader.js` - Fixed protocols caching with proper user context
- `frontend/src/services/maintenanceProtocolsService.js` - No changes needed (kept for reference)
- `frontend/src/db/indexedDB.js` - No changes needed (security checks working as intended)

## Technical Details

### User Context Security

The IndexedDB caching system requires user context for all cache operations to prevent cross-user data leakage:

```javascript
const userContext = {
  userId: user.id,
  organizationId: user.organization_id,
  isSuperAdmin: user.role === 'super_admin'
};
```

This ensures:
- Regular users only see their organization's data
- Super admins can see all data
- No data leakage between users/organizations

### Cache Stores

The following data is preloaded for offline use:
- **machines** - All machines (filtered by organization)
- **protocols** - All maintenance protocols (filtered by organization)
- **users** - All users (for operator dropdowns)
- **farmSites** - All farm sites (for net cleaning)
- **nets** - All nets (for net cleaning)

## Troubleshooting

### If protocols still don't cache:

1. **Check browser console for errors** - Look for any red error messages
2. **Verify API response** - Check Network tab, should see 200 OK for `/api/maintenance-protocols/`
3. **Check user context** - Console should show user ID and organization ID
4. **Clear all browser data** - Settings > Privacy > Clear browsing data > Cached images and files
5. **Try incognito mode** - Rules out browser extension interference

### If you see "SECURITY WARNING: Caching without user context":

This means the user object is missing or incomplete. Check:
- User is properly logged in
- `localStorage.getItem('token')` returns a valid token
- User object has `id`, `organization_id`, and `role` properties

## Status

✅ **Code changes committed to repository**  
⏳ **Awaiting deployment to production server**  
⏳ **Awaiting verification in production**

## Next Steps

1. Deploy to production using the script above
2. Clear IndexedDB in browser
3. Login and verify protocols are cached
4. Test offline mode functionality
5. Confirm with user that issue is resolved
