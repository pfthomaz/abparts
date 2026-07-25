# Checklist Items Caching Fix

## Issue
When clicking "Start Maintenance", the execution form failed with:
```
API Error (/maintenance-protocols/{id}/checklist-items): TypeError: Failed to fetch
Error initializing execution: TypeError: Failed to fetch
```

## Root Cause
The `getChecklistItems()` function was not cached, so when the backend was slow or offline, the execution form couldn't load the checklist items needed to start maintenance.

## Fix Applied

### Updated `getChecklistItems()` function
Added caching support with offline fallback:

```javascript
export const getChecklistItems = async (protocolId) => {
  const online = isOnline();
  
  // Try to get from cached protocol first
  if (!online) {
    const cachedProtocol = await getCachedItem(STORES.PROTOCOLS, protocolId);
    if (cachedProtocol && cachedProtocol.checklist_items) {
      return cachedProtocol.checklist_items;
    }
  }
  
  // Fetch from API
  try {
    const items = await api.get(`/maintenance-protocols/${protocolId}/checklist-items`);
    
    // Update the cached protocol with checklist items
    const cachedProtocol = await getCachedItem(STORES.PROTOCOLS, protocolId);
    if (cachedProtocol) {
      cachedProtocol.checklist_items = items;
      await cacheData(STORES.PROTOCOLS, cachedProtocol);
    }
    
    return items;
  } catch (error) {
    // Fallback to cached protocol
    const cachedProtocol = await getCachedItem(STORES.PROTOCOLS, protocolId);
    if (cachedProtocol && cachedProtocol.checklist_items) {
      return cachedProtocol.checklist_items;
    }
    throw error;
  }
};
```

## How It Works

1. **Offline Mode:** Uses cached checklist items from the protocol object
2. **Online Mode:** Fetches from API and updates cache
3. **Error Fallback:** Falls back to cache if API fails

## Testing Steps

1. **Hard refresh** (`Cmd+Shift+R` or `Ctrl+Shift+R`)
2. Navigate to Maintenance Executions
3. Select a machine and protocol
4. Click "Start Maintenance"
5. Should load checklist items without error

## Expected Behavior

### First Load (Populating Cache)
- Fetches checklist items from API
- Stores them in the cached protocol
- Console: `[MaintenanceService] Cached checklist items: X`

### Subsequent Loads (Using Cache)
- Uses cached checklist items
- No API call needed
- Fast execution form load

### Offline Mode
- Uses cached checklist items immediately
- Console: `[MaintenanceService] Using cached checklist items (offline): X`

### API Failure (Fallback)
- Attempts API call
- Falls back to cache on error
- Console: `[MaintenanceService] Using cached checklist items (fallback): X`

## Files Modified
- `frontend/src/services/maintenanceProtocolsService.js` - Added caching to `getChecklistItems()`

## Related Fixes
This completes the offline maintenance caching implementation:
- ✅ M1: Cache Maintenance Protocols
- ✅ M2: Cache Parts
- ✅ M3: Offline ExecutionForm
- ✅ M4: IndexedDB Helpers
- ✅ M5: Sync Processor
- ✅ M6: Pending Executions Display
- ✅ M7: Translations
- ✅ **NEW: Cache Checklist Items**

## Next Steps
After hard refresh, you should be able to:
1. Start maintenance execution
2. Complete checklist items
3. Record maintenance offline
4. Sync when back online
