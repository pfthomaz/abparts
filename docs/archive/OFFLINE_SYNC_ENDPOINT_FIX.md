# Offline Sync Endpoint Fix

## Issue
Offline maintenance executions were being recorded successfully, but sync was failing with:
```
POST http://localhost:8000/maintenance-executions
Status Code: 404 Not Found
```

Error messages:
- `[SyncProcessor] Failed to sync maintenance execution: Error: Not Found`
- `Internal server error`
- All 4 sync operations failed

## Root Cause
The sync queue was using the wrong endpoint:
- **Wrong:** `/maintenance-executions`
- **Correct:** `/maintenance-protocols/executions`

The backend API endpoint for creating maintenance executions is `/maintenance-protocols/executions`, not `/maintenance-executions`.

## Fix Applied

### Updated `syncQueueManager.js`
Changed the endpoint in `queueMaintenanceExecution()` function:

```javascript
// BEFORE (Wrong)
endpoint: '/maintenance-executions',

// AFTER (Correct)
endpoint: '/maintenance-protocols/executions',
```

## How to Test

### 1. Hard Refresh (REQUIRED!)
**Mac:** `Cmd + Shift + R`
**Windows:** `Ctrl + Shift + R`

### 2. Clear Existing Failed Operations
The old failed operations are still in the sync queue with the wrong endpoint. You need to clear them:

**Option A: Clear IndexedDB (Recommended)**
1. Open DevTools (F12)
2. Go to Application > Storage > IndexedDB
3. Expand `ABPartsOfflineDB`
4. Right-click on `syncQueue` store
5. Click "Clear"
6. Right-click on `maintenanceExecutions` store
7. Click "Clear"
8. Refresh the page

**Option B: Let them fail and retry**
The old operations will continue to fail, but new ones will work.

### 3. Test Offline Recording
1. Go to Maintenance Executions
2. Select machine and protocol
3. Click "Start Maintenance"
4. Complete some checklist items
5. Click "Finish"
6. Should see "Saved offline" message

### 4. Test Sync
1. Check browser console
2. Should see: `[SyncQueue] Queued maintenance execution: X`
3. When online, sync should succeed
4. Should see: `[SyncProcessor] Sync complete: {total: X, succeeded: X, failed: 0}`

## Expected Behavior

### Offline Recording
- ✅ Can start maintenance execution
- ✅ Can complete checklist items
- ✅ Can finish execution
- ✅ Saved to IndexedDB
- ✅ Queued for sync with correct endpoint

### Online Sync
- ✅ Sync processor picks up queued operations
- ✅ POSTs to `/maintenance-protocols/executions`
- ✅ Backend creates execution record
- ✅ Marks as synced in IndexedDB
- ✅ Removes from sync queue
- ✅ Page refreshes to show synced data

## Files Modified
- `frontend/src/services/syncQueueManager.js` - Fixed endpoint URL

## Related Issues
- ✅ M1-M9: All offline maintenance tasks complete
- ✅ Caching fixes applied
- ✅ Checklist items caching added
- ✅ **NEW: Sync endpoint fixed**

## Verification

After hard refresh and clearing old operations, you should see:

**Console logs when recording offline:**
```
[IndexedDB] Saved offline maintenance execution: temp_xxx
[SyncQueue] Queued maintenance execution: 1
```

**Console logs when syncing:**
```
[SyncProcessor] Processing sync queue...
[SyncProcessor] Syncing maintenance execution: temp_xxx
[SyncProcessor] Sync complete: {total: 1, succeeded: 1, failed: 0}
```

**Network tab:**
```
POST /maintenance-protocols/executions
Status: 201 Created
```

## Next Steps
1. Hard refresh browser
2. Clear old failed operations from IndexedDB
3. Test offline recording
4. Test sync when back online
5. Verify execution appears in history
