# Deploy Net Cleaning Offline Fix - READY NOW

## Status: ✅ ALL FIXES COMMITTED AND PUSHED + DEBUG LOGGING ADDED

All code changes have been committed to GitHub (latest commit: 409deac).

## What Was Fixed

### Problem
When trying to record net cleaning offline:
1. Farm sites dropdown was empty
2. Build errors: `'userContext' is not defined` in farmSitesService.js and netsService.js

### Root Cause
- `STORES.FARM_SITES` and `STORES.NETS` were undefined in cached JavaScript
- Search/getById functions were using `userContext` but didn't have it as a parameter

### Solution Applied
1. **farmSitesService.js**:
   - Replaced all `STORES.FARM_SITES` with `'farmSites'` string literal
   - Added `userContext` parameter to all functions
   - Added `userContext` parameter to `getFarmSite()` function
   - **NEW**: Added debug console logging to track cache retrieval

2. **netsService.js**:
   - Replaced all `STORES.NETS` with `'nets'` string literal
   - Added `userContext` parameter to all functions
   - Added `userContext` parameter to `getNet()` function

3. **NetCleaningRecords.js**:
   - Updated to pass userContext to all service calls

4. **Debug Tools**:
   - Added `debug_farm_sites_cache.js` script to inspect IndexedDB
   - Added console logging to farmSitesService for troubleshooting

## Deployment Steps

### On Production Server (ubuntu-8gb-hel1-2)

```bash
# 1. Navigate to project directory
cd /root/abparts

# 2. Pull latest code
git pull origin main

# 3. Rebuild and restart containers
docker compose -f docker-compose.prod.yml down
docker compose -f docker-compose.prod.yml build --no-cache web
docker compose -f docker-compose.prod.yml up -d

# 4. Verify containers are running
docker compose -f docker-compose.prod.yml ps
```

### On Client Browser

**CRITICAL**: Clear browser cache to remove old cached JavaScript:

1. Open browser DevTools (F12)
2. Go to Application tab → Storage
3. Click "Clear site data"
4. Hard refresh: Cmd+Shift+R (Mac) or Ctrl+Shift+R (Windows/Linux)

## Troubleshooting

### Check Console Logs

After deployment, open browser console and look for:

```
[FarmSitesService] Using cached data, userContext: {...}
[FarmSitesService] Retrieved from cache: X farm sites
[FarmSitesService] After active filter: X farm sites
[FarmSitesService] After pagination: X farm sites
```

### Run Debug Script

If dropdown is still empty, run the debug script:

1. Open DevTools Console
2. Copy contents of `debug_farm_sites_cache.js`
3. Paste and press Enter
4. Check output for issues

### Common Issues

**If "Retrieved from cache: 0":**
- Data was never cached
- Logout and login again to trigger data preload
- Check for "Data preload completed" message

**If "SECURITY WARNING: Reading cache without user context":**
- Code bug - should be fixed in latest commit
- Verify you pulled latest code

**If data exists but dropdown empty:**
- Check organization filtering
- See `TROUBLESHOOT_FARM_SITES_DROPDOWN.md` for detailed steps

## Testing Offline Net Cleaning

1. **Login** to the application
2. **Wait for data preload** to complete (check console for "Data preload completed")
3. **Go offline** (DevTools → Network tab → Throttling → Offline)
4. **Navigate to Net Cleaning Records** page
5. **Click "Record Cleaning"**
6. **Verify**:
   - Farm sites dropdown is populated
   - Nets dropdown is populated after selecting farm site
   - Machines dropdown is populated
   - Can create cleaning record offline

## Commits Included

- `6a19438` - Replace STORES constants with string literals in farmSites and nets services
- `665f2ef` - Add userContext parameter to search functions
- `830cfee` - Add userContext parameter to getFarmSite and getNet functions
- `409deac` - Add debug logging to farmSitesService for troubleshooting

## Files Changed

- `frontend/src/services/farmSitesService.js`
- `frontend/src/services/netsService.js`
- `frontend/src/pages/NetCleaningRecords.js`
- `debug_farm_sites_cache.js` (new)

## Expected Behavior After Deployment

✅ Farm sites dropdown populated offline
✅ Nets dropdown populated offline
✅ Machines dropdown populated offline
✅ Can create net cleaning records offline
✅ Records sync when back online
✅ No build errors
✅ No console errors
✅ Debug logs show cache retrieval details

---

**Ready to deploy!** All code is committed and pushed to GitHub.

**If issues persist after deployment**, see `TROUBLESHOOT_FARM_SITES_DROPDOWN.md` for detailed troubleshooting steps.
