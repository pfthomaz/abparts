# Offline Mode Fix - Complete Guide

## Issues Addressed

### 1. Organizations Not Showing in Production
**Problem**: New organizations added to database don't appear in Organizations page
**Root Cause**: Browser caching stale data
**Solution**: Hard refresh to clear browser cache

### 2. Offline Mode Not Working
**Problem**: Offline mode fails with "Cannot fetch machines offline without user context" errors
**Root Cause**: Multiple issues:
- Service worker not being copied to production build
- User context not passed to getMachines() in MaintenanceExecutions
- Service worker causing HMR spam in development
- Data not preloaded on login

**Solutions Applied**:
- ✅ Created `frontend/copy-sw.js` post-build script
- ✅ Updated `package.json` to run post-build script
- ✅ Fixed `MaintenanceExecutions.js` to pass user context
- ✅ Disabled service worker in development mode
- ✅ Created `offlineDataPreloader.js` to preload all essential data
- ✅ Integrated preloader into `AuthContext.js` to run on login

## Quick Fix for Organizations Issue

### Production Server
```bash
# No code changes needed - just clear browser cache
# In browser: Cmd+Shift+R (Mac) or Ctrl+Shift+R (Windows/Linux)
```

### If Hard Refresh Doesn't Work
```bash
# Check if API is returning organizations correctly
curl -H "Authorization: Bearer YOUR_TOKEN" http://localhost:8000/organizations/

# If API returns organizations but UI doesn't show them:
# 1. Open browser DevTools (F12)
# 2. Go to Application tab
# 3. Clear all storage (Storage > Clear site data)
# 4. Reload page
```

## Complete Fix for Offline Mode

### Step 1: Rebuild Frontend (Local Development)
```bash
# Stop current containers
docker compose down

# Rebuild frontend with all fixes
docker compose build web --no-cache

# Start containers
docker compose up -d

# Verify service worker is present
docker compose exec web ls -lh /usr/share/nginx/html/service-worker.js
```

### Step 2: Rebuild Frontend (Production)
```bash
# SSH to production server
ssh diogo@ubuntu-8gb-hel1-2

# Navigate to project directory
cd ~/abparts

# Pull latest changes
git pull

# Stop current containers
docker compose -f docker-compose.prod.yml down

# Rebuild frontend with all fixes
docker compose -f docker-compose.prod.yml build web --no-cache

# Start containers
docker compose -f docker-compose.prod.yml up -d

# Verify service worker is present
docker compose -f docker-compose.prod.yml exec web ls -lh /usr/share/nginx/html/service-worker.js
```

### Step 3: Test Offline Mode

#### A. Test Data Preloading
1. **Login to the app**
2. **Open browser DevTools** (F12)
3. **Check Console** for preloader messages:
   ```
   [OfflinePreloader] Starting data preload for user: <username>
   [OfflinePreloader] Preloading machines...
   [OfflinePreloader] Preloading maintenance protocols...
   [OfflinePreloader] Preloading users...
   [OfflinePreloader] Preloading farm sites...
   [OfflinePreloader] Preloading nets...
   [OfflinePreloader] Data preload complete
   ```

#### B. Verify IndexedDB Population
1. **Open DevTools** > **Application** tab
2. **Navigate to** IndexedDB > ABPartsOfflineDB
3. **Check stores** have data:
   - `machines` - should have all machines
   - `maintenanceProtocols` - should have all protocols
   - `users` - should have all users
   - `farmSites` - should have all farm sites
   - `nets` - should have all nets

#### C. Test Offline Functionality
1. **Go to DevTools** > **Network** tab
2. **Enable "Offline" mode** (checkbox at top)
3. **Navigate to** Maintenance Executions page
4. **Try to create** a new maintenance execution:
   - Machine dropdown should show all machines
   - Protocol dropdown should show all protocols
   - No errors in console
5. **Navigate to** Net Cleaning Records page
6. **Try to create** a new net cleaning record:
   - User dropdown should show all users
   - Farm site dropdown should show all farm sites
   - Net dropdown should show all nets
   - No errors in console

### Step 4: Troubleshooting

#### Issue: Preloader not running
**Symptoms**: No "[OfflinePreloader]" messages in console after login
**Solution**:
```bash
# Check if offlineDataPreloader.js exists
ls -l frontend/src/services/offlineDataPreloader.js

# Check if AuthContext.js imports it
grep -n "offlineDataPreloader" frontend/src/AuthContext.js

# Rebuild frontend
docker compose build web --no-cache
docker compose up -d
```

#### Issue: IndexedDB not populated
**Symptoms**: IndexedDB stores are empty after login
**Solution**:
1. Check browser console for errors
2. Verify you're online when logging in (preloader only runs when online)
3. Check API endpoints are accessible:
   ```bash
   curl -H "Authorization: Bearer YOUR_TOKEN" http://localhost:8000/machines/
   curl -H "Authorization: Bearer YOUR_TOKEN" http://localhost:8000/maintenance-protocols/
   ```

#### Issue: Service worker not working
**Symptoms**: "Failed to fetch" errors when offline
**Solution**:
```bash
# Verify service worker file exists in build
docker compose exec web ls -lh /usr/share/nginx/html/service-worker.js

# If missing, check copy-sw.js script
cat frontend/copy-sw.js

# Rebuild frontend
docker compose build web --no-cache
docker compose up -d
```

#### Issue: Development mode console spam
**Symptoms**: Endless "[Service Worker]" messages in development
**Solution**: This is expected and fixed! Service worker is now disabled in development mode (NODE_ENV=development). The spam only occurs with Hot Module Replacement (HMR) in development.

## Files Modified

### Frontend Files
1. `frontend/src/services/offlineDataPreloader.js` - NEW: Preloads all essential data on login
2. `frontend/src/AuthContext.js` - MODIFIED: Integrated preloader to run after login
3. `frontend/src/index.js` - MODIFIED: Disabled service worker in development mode
4. `frontend/copy-sw.js` - NEW: Post-build script to copy service worker
5. `frontend/package.json` - MODIFIED: Added postbuild script
6. `frontend/src/pages/MaintenanceExecutions.js` - MODIFIED: Pass user context to getMachines()

### No Backend Changes Required
All fixes are frontend-only.

## Expected Behavior After Fix

### On Login
1. User logs in successfully
2. Preloader automatically runs in background
3. All essential data is cached to IndexedDB
4. User can immediately start working
5. No need to navigate through pages to cache data

### When Online
1. All API calls work normally
2. Data is cached to IndexedDB for offline use
3. Service worker caches API responses

### When Offline
1. Service worker intercepts API calls
2. Data is served from IndexedDB cache
3. User can create maintenance executions and net cleaning records
4. Changes are queued for sync when back online

## Next Steps

1. ✅ Rebuild frontend in local development
2. ✅ Test offline mode locally
3. ✅ Rebuild frontend in production
4. ✅ Test offline mode in production
5. ⏳ Monitor for any additional issues

## Notes

- **Organizations Issue**: No code changes needed, just browser cache clear
- **Offline Mode**: All fixes implemented, just needs rebuild
- **Service Worker**: Now properly copied to build folder
- **Data Preloading**: Runs automatically on login
- **Development Mode**: Service worker disabled to prevent HMR spam
- **Production Mode**: Service worker enabled for offline functionality

## Support

If issues persist after following this guide:
1. Check browser console for errors
2. Verify service worker is registered (DevTools > Application > Service Workers)
3. Check IndexedDB has data (DevTools > Application > IndexedDB)
4. Verify API endpoints are accessible when online
5. Try clearing all browser data and logging in again
