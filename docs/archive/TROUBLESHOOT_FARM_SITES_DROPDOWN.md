# Troubleshoot Farm Sites Dropdown Empty

## Problem
Farm sites dropdown is empty when trying to record net cleaning offline, even though data is in IndexedDB.

## Diagnostic Steps

### Step 1: Check Browser Console Logs

After deploying the latest code (commit 409deac), open browser console and look for these logs:

```
[FarmSitesService] Using cached data, userContext: {userId: "...", organizationId: "...", isSuperAdmin: false}
[FarmSitesService] Retrieved from cache: X farm sites
[FarmSitesService] After active filter: X farm sites
[FarmSitesService] After pagination: X farm sites
```

**What to look for:**
- If "Retrieved from cache: 0" → Data was never cached (go to Step 2)
- If "After active filter: 0" → All farm sites are inactive (check database)
- If "After pagination: X" but dropdown still empty → Frontend rendering issue (go to Step 3)

### Step 2: Check IndexedDB Data

Run the debug script in browser console:

1. Open DevTools (F12)
2. Go to Console tab
3. Copy and paste the contents of `debug_farm_sites_cache.js`
4. Press Enter

**What to look for:**
- "❌ farmSites store does NOT exist!" → Database schema issue, need to clear IndexedDB
- "⚠️ No farm sites in cache!" → Data preload failed
- "❌ X farm sites missing organization_id" → Backend data issue

### Step 3: Check Data Preload

Look for these console logs during login:

```
[OfflineDataPreloader] Starting data preload...
[OfflineDataPreloader] Preloading farm sites...
[OfflineDataPreloader] Cached X farm sites
[OfflineDataPreloader] Data preload completed successfully
```

**If preload failed:**
- Check if user is logged in
- Check if API is accessible
- Check network tab for failed requests

### Step 4: Check User Context

The farm sites service requires userContext with:
- `userId`: User's ID
- `organizationId`: User's organization ID
- `isSuperAdmin`: Whether user is super admin

**Verify in console:**
```javascript
// Check current user
const user = JSON.parse(localStorage.getItem('user'));
console.log('User:', user);
console.log('Organization ID:', user.organization_id);
```

## Common Issues and Solutions

### Issue 1: No Data in Cache

**Symptoms:**
- Console shows "Retrieved from cache: 0 farm sites"
- Debug script shows "No farm sites in cache"

**Solution:**
1. Go online
2. Logout and login again (triggers data preload)
3. Wait for "Data preload completed" message
4. Go offline and try again

### Issue 2: User Context Missing

**Symptoms:**
- Console shows "SECURITY WARNING: Reading cache without user context"
- Returns empty array

**Solution:**
- This is a code bug - userContext should always be passed
- Check that NetCleaningRecords page is passing userContext to farmSitesService
- Latest code (commit 409deac) should have this fixed

### Issue 3: Organization Filtering

**Symptoms:**
- Data exists in IndexedDB
- But filtered to 0 results

**Possible causes:**
1. Farm sites belong to different organization than logged-in user
2. User's organization_id doesn't match farm sites' organization_id

**Check in console:**
```javascript
// Get all farm sites from IndexedDB
const request = indexedDB.open('ABPartsOfflineDB', 3);
request.onsuccess = (e) => {
  const db = e.target.result;
  const tx = db.transaction(['farmSites'], 'readonly');
  const store = tx.objectStore('farmSites');
  store.getAll().onsuccess = (e) => {
    const sites = e.target.result;
    console.log('All farm sites:', sites);
    console.log('Organization IDs:', sites.map(s => s.organization_id));
  };
};

// Compare with user's organization
const user = JSON.parse(localStorage.getItem('user'));
console.log('User organization ID:', user.organization_id);
```

### Issue 4: IndexedDB Version Conflict

**Symptoms:**
- Console shows database errors
- Stores don't exist

**Solution:**
1. Close all browser tabs with the app
2. Open DevTools → Application → Storage
3. Click "Clear site data"
4. Refresh page
5. Login again

## Deployment Steps

```bash
# On production server
cd /root/abparts
git pull origin main
docker compose -f docker-compose.prod.yml down
docker compose -f docker-compose.prod.yml build --no-cache web
docker compose -f docker-compose.prod.yml up -d

# On client browser
# Clear cache: DevTools → Application → Clear site data
# Hard refresh: Cmd+Shift+R
```

## Expected Console Output (Working)

```
[OfflineDataPreloader] Starting data preload...
[OfflineDataPreloader] Preloading farm sites...
[OfflineDataPreloader] Cached 5 farm sites
[OfflineDataPreloader] Data preload completed successfully

[FarmSitesService] Using cached data, userContext: {userId: "abc123", organizationId: "org456", isSuperAdmin: false}
[FarmSitesService] Retrieved from cache: 5 farm sites
[FarmSitesService] After active filter: 5 farm sites
[FarmSitesService] After pagination: 5 farm sites
```

## Next Steps

After deploying and checking console logs, report back with:
1. What console logs you see
2. Results from debug script
3. Any error messages

This will help identify the exact issue.
