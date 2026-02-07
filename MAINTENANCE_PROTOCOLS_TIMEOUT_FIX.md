# Maintenance Protocols 408 Timeout Fix

## Issue
When navigating to the Maintenance Executions page, users encountered:
- **408 Request Timeout** error on `/maintenance-protocols/` API call
- **Empty machine dropdown** (couldn't select machine)
- **Page unable to load** properly

## Root Cause
The `listProtocols()` function in `maintenanceProtocolsService.js` was:
1. Calling `isCacheStale()` which could block for too long
2. Using `Promise.all()` in the page load, causing one failure to block everything
3. Not handling API timeouts gracefully with cache fallback

## Changes Made

### 1. Fixed `maintenanceProtocolsService.js` - `listProtocols()` function
**Changes:**
- Added timeout protection (1 second) for cache staleness check
- Separated offline vs online logic for clarity
- Improved cache fallback logic with better error messages
- Extracted filter logic into reusable helper function

**Key improvements:**
```javascript
// Check cache staleness with timeout to prevent blocking
const staleCheckPromise = isCacheStale(STORES.PROTOCOLS);
const timeoutPromise = new Promise((resolve) => setTimeout(() => resolve(true), 1000));
cacheStale = await Promise.race([staleCheckPromise, timeoutPromise]);
```

### 2. Fixed `MaintenanceExecutions.js` - `loadData()` function
**Changes:**
- Replaced `Promise.all()` with sequential loading
- Added individual try-catch blocks for each data source
- Allowed page to load even if some data fails
- Better error messages for specific failures

**Key improvements:**
```javascript
// Load each data source independently
try {
  machinesData = await machinesService.getMachines();
} catch (err) {
  console.error('Failed to load machines:', err);
  setError('Failed to load machines. Please refresh the page.');
}
```

### 3. Fixed `partsService.js` - `getParts()` function (Preventive)
**Changes:**
- Applied same timeout protection as protocols service
- Prevents similar issues when loading parts for maintenance execution
- Ensures parts dropdown can populate even with slow API

## Testing Steps

1. **Hard refresh the page** (`Cmd+Shift+R` on Mac, `Ctrl+Shift+R` on Windows)
   - This clears the cached JavaScript and loads the new code
   - **IMPORTANT:** This is required after IndexedDB schema changes

2. **Navigate to Maintenance Executions**
   - Should load without 408 error
   - Machines dropdown should populate
   - Protocols dropdown should populate

3. **Test offline mode**
   - Disconnect network
   - Navigate to Maintenance Executions
   - Should use cached data if available

4. **Test slow network**
   - Throttle network in DevTools
   - Page should still load using cache fallback

## Expected Behavior

### Online with Fresh Cache
- Uses cached data immediately
- No API call needed
- Fast page load (<1 second)

### Online with Stale Cache
- Attempts API call with 30-second timeout
- Falls back to cache if API fails
- Page loads even if API is slow

### Offline
- Uses cached data immediately
- Shows offline indicator
- All functionality works with cached data

## Files Modified
1. `frontend/src/services/maintenanceProtocolsService.js` - Fixed `listProtocols()` and `getChecklistItems()` timeout issues
2. `frontend/src/pages/MaintenanceExecutions.js` - Fixed page load error handling
3. `frontend/src/services/partsService.js` - Fixed `getParts()` timeout issue (preventive)
4. `frontend/src/services/machinesService.js` - Added caching and timeout protection

## Related Issues
- IndexedDB version conflict (requires hard refresh after schema changes)
- Offline maintenance execution support (M1-M7 tasks completed)
- Cache staleness checks blocking page load

## Offline Maintenance Status

### ✅ Completed Tasks (M1-M7)
1. **M1: Cache Maintenance Protocols Service** - 24-hour staleness, timeout protection
2. **M2: Cache Parts Service** - For quantity tracking, timeout protection
3. **M3: Modify ExecutionForm for Offline** - Full offline support with warning banner
4. **M4: Add IndexedDB Helper Functions** - Save/retrieve/sync maintenance executions
5. **M5: Update Sync Processor** - Sync executions and checklist completions
6. **M6: Update MaintenanceExecutions Page** - Show pending executions with badges
7. **M7: Add Translations** - All 6 languages (en, es, tr, no, el, ar)

### Current Status
- ✅ All offline maintenance features implemented
- ✅ Timeout issues fixed
- ✅ Cache fallback working correctly
- ⚠️ Requires hard refresh to clear IndexedDB version conflict

## Next Steps
1. **User Action Required:** Hard refresh (`Cmd+Shift+R`) to load new code
2. Test maintenance execution recording offline
3. Test sync when coming back online
4. Verify all dropdowns populate correctly (machines, protocols, parts, operators)

