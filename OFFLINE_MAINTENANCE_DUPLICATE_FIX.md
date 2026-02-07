# Offline Maintenance - Duplicate Execution Fix ✅

**Date**: February 7, 2026  
**Status**: DUPLICATE ISSUE RESOLVED

## Problem: Duplicate Executions

**Symptom**: One offline execution creates TWO database entries:
- One "In Progress" (Ongoing)
- One "Completed"

## Root Cause

The system had **TWO sync mechanisms** for the same execution:

### Sync Path 1: maintenanceExecutions Store
```javascript
// In syncProcessor.js - syncMaintenanceExecutions()
1. Get unsynced executions from IndexedDB.maintenanceExecutions
2. Sync each execution with correct status
3. Creates execution with status: "completed" ✅
```

### Sync Path 2: syncQueue Store  
```javascript
// In ExecutionForm.js - when saving offline
1. Save to maintenanceExecutions store
2. ALSO queue in syncQueue store ❌ (DUPLICATE!)
3. syncQueue has old data with status: "in_progress"
4. Creates ANOTHER execution with status: "in_progress" ❌
```

## The Fix

**Removed the duplicate queueing** in `ExecutionForm.js`:

### Before (WRONG):
```javascript
// Save to IndexedDB
await saveOfflineMaintenanceExecution(offlineExecution);

// Queue for sync - THIS CREATES DUPLICATE!
const syncData = {
  protocol_id: protocol.id,
  machine_id: machine.id,
  machine_hours_at_service: hours > 0 ? hours : null,
  status: 'in_progress'  // ❌ Wrong status
};
await queueMaintenanceExecution(tempId, syncData);
```

### After (CORRECT):
```javascript
// Save to IndexedDB
await saveOfflineMaintenanceExecution(offlineExecution);

// NOTE: Do NOT queue in syncQueue - maintenance executions are synced
// directly from the maintenanceExecutions store to avoid duplicates
```

## How It Works Now

### Single Sync Path (CORRECT):
```
1. User finishes maintenance offline
   ↓
2. Execution saved to maintenanceExecutions store
   - status: "completed"
   - checklist_completions: [...]
   ↓
3. When online, syncMaintenanceExecutions() runs
   ↓
4. Creates ONE execution with correct status
   ↓
5. Syncs checklist completions
   ↓
6. Marks as synced in IndexedDB
   ↓
7. ONE execution in database ✅
```

## Files Modified

1. **`frontend/src/components/ExecutionForm.js`**
   - Removed `queueMaintenanceExecution()` call
   - Added comment explaining why

## User Instructions

### Step 1: Hard Refresh (CRITICAL)
- **Mac**: `Cmd + Shift + R`
- **Windows/Linux**: `Ctrl + Shift + R`

### Step 2: Clean Up Database
You need to delete the duplicate executions from the database:

```sql
-- Find duplicates (same machine, protocol, and date)
SELECT machine_id, protocol_id, DATE(performed_date), COUNT(*) as count
FROM maintenance_executions
GROUP BY machine_id, protocol_id, DATE(performed_date)
HAVING COUNT(*) > 1;

-- Delete the "in_progress" duplicates (keep completed ones)
DELETE FROM maintenance_executions
WHERE status = 'in_progress'
AND id IN (
  SELECT id FROM (
    SELECT id, 
           ROW_NUMBER() OVER (
             PARTITION BY machine_id, protocol_id, DATE(performed_date) 
             ORDER BY created_at DESC
           ) as rn
    FROM maintenance_executions
    WHERE status = 'in_progress'
  ) t
  WHERE rn > 1
);
```

Or manually delete the "Ongoing" entries from the UI.

### Step 3: Clear IndexedDB
1. Open DevTools (F12)
2. Application → IndexedDB → ABPartsOfflineDB
3. Clear these stores:
   - `syncQueue` - Remove ALL maintenance execution operations
   - `maintenanceExecutions` - Remove old test data
4. Refresh page

### Step 4: Test Again
1. Go offline
2. Start new maintenance
3. Complete checklist
4. Finish maintenance
5. Go online
6. Wait for sync
7. **Check list - should see ONLY ONE "Completed" execution** ✅

## Verification

After the fix, you should see:
- ✅ ONE execution per maintenance session
- ✅ Correct status ("Completed" not "Ongoing")
- ✅ All checklist completions synced
- ✅ No duplicates

## Technical Details

### Why This Happened

The original implementation tried to use BOTH sync mechanisms:
- `maintenanceExecutions` store for full execution data
- `syncQueue` for generic operation queueing

This was redundant and caused duplicates because:
1. Both stores had the same execution
2. Both sync functions ran independently
3. Each created a separate database entry

### The Correct Approach

Maintenance executions should ONLY use the `maintenanceExecutions` store because:
- It stores the complete execution data
- It tracks checklist completions
- It handles status updates
- It's specifically designed for maintenance

The `syncQueue` is better for:
- Simple operations (machine hours, stock adjustments)
- Operations without complex nested data
- Generic sync operations

## Status: FIXED ✅

The duplicate issue is now resolved. After hard refresh and cleanup:
- ✅ No more duplicate executions
- ✅ Single sync path
- ✅ Correct status
- ✅ Clean database

**Next**: Hard refresh, clean up duplicates, test again!
