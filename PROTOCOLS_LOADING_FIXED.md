# Protocols Loading Issue - FULLY RESOLVED

## Problem Summary

Protocols were failing to load in MaintenanceExecutions page with error:
```
[MaintenanceExecutions] Failed to load protocols: Error: No cached data available offline
```

## Root Causes (2 Issues Found)

### Issue 1: Undefined STORES Constant ✅ FIXED
- **Symptom**: `[IndexedDB] DEBUG: Attempting transaction for store: undefined`
- **Cause**: Service worker cached old JavaScript where `STORES.MAINTENANCE_PROTOCOLS` was undefined
- **Fix**: Replaced all STORES constant references with string literals
- **Commits**: 18695f0, e8c4baf

### Issue 2: Incorrect Organization Filtering ✅ FIXED
- **Symptom**: `Error: No cached data available offline` when loading protocols
- **Cause**: `getCachedData()` was filtering ALL stores by `organization_id`, but `MaintenanceProtocol` model has NO `organization_id` field (protocols are global/shared across organizations)
- **Fix**: Added `GLOBAL_STORES` list to identify stores that aren't organization-scoped
- **Commit**: 88df42f

## Technical Details

### The Organization Filtering Problem

**Before (BROKEN):**
```javascript
// getCachedData filtered EVERYTHING by organization_id
const filteredData = userContext.isSuperAdmin 
  ? data 
  : data.filter(item => item.organization_id === userContext.organizationId);
```

**Problem:**
- Protocols cached successfully: `[OfflinePreloader] ✓ Cached 5 protocols`
- But when loading: `getCachedData('protocols', userContext)` returned `[]`
- Why? Because protocols don't have `organization_id` field!
- Filter: `protocols.filter(p => p.organization_id === userContext.organizationId)` → empty array

**After (FIXED):**
```javascript
// Define stores that are GLOBAL (not organization-scoped)
const GLOBAL_STORES = ['protocols', 'users'];

let filteredData;
if (GLOBAL_STORES.includes(storeName)) {
  // Global stores - return all data
  filteredData = data;
} else {
  // Organization-scoped stores - filter by organization
  filteredData = userContext.isSuperAdmin 
    ? data 
    : data.filter(item => item.organization_id === userContext.organizationId);
}
```

### Store Classification

**Global Stores (No Organization Filtering):**
- `protocols` - Maintenance protocols are shared across all organizations
- `users` - User list needed for dropdowns (already filtered by backend)

**Organization-Scoped Stores (Filtered by Organization):**
- `machines` - Each machine belongs to one organization
- `farmSites` - Each farm site belongs to one organization
- `nets` - Each net belongs to one organization
- `parts` - Parts can be organization-specific
- `maintenanceExecutions` - Executions are organization-scoped

## Deployment Instructions

### Step 1: Deploy on Production

```bash
cd ~/abparts
./deploy_protocols_fix.sh
```

### Step 2: Clear Browser Cache

Use one of these methods:
- Safari Preferences → Privacy → Manage Website Data → Remove All
- Navigate to `/clear-cache.html` and click "Clear All Caches"
- Hard refresh: `Cmd + Option + E` then `Cmd + Shift + R`

### Step 3: Verify

After login, check console:
```
[OfflinePreloader] ✓ Cached 5 protocols
[OfflinePreloader] Preload complete: 5/5 successful
```

Navigate to Maintenance Executions - protocols should load without errors.

## Files Modified

1. **frontend/src/services/offlineDataPreloader.js**
   - Replaced STORES constants with string literals
   - Ensures protocols cache correctly

2. **frontend/src/services/maintenanceProtocolsService.js**
   - Added userContext parameter to protocol functions
   - Passes userContext through to caching layer

3. **frontend/src/db/indexedDB.js**
   - Added GLOBAL_STORES list
   - Fixed getCachedData to not filter global stores by organization

## Security Considerations

The fix maintains security:
- User context is still required for all cache operations
- Organization-scoped data (machines, nets, etc.) still filtered correctly
- Global data (protocols) is intentionally shared across organizations
- Super admins still see all data as expected

## Status

- ✅ Issue 1 fixed: STORES constant undefined
- ✅ Issue 2 fixed: Protocols organization filtering
- ✅ Code committed and pushed (commits 88df42f, 05b703e)
- ✅ Documentation updated
- ⏳ **WAITING**: Production deployment + browser cache clear

## Next Steps

1. Run `./deploy_protocols_fix.sh` on production server
2. Clear browser cache completely
3. Login and verify protocols cache successfully
4. Navigate to Maintenance Executions page
5. Confirm protocols load without errors

---

**Summary**: Two issues fixed - stale JavaScript cache and incorrect organization filtering. Both fixes are in the repository and ready to deploy.
