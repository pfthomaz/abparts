# Offline Maintenance - Status Sync Issue

**Date**: February 7, 2026  
**Status**: SYNC WORKING BUT STATUS NOT UPDATING

## Current Situation

✅ **What's Working:**
- Offline maintenance execution saves to IndexedDB
- Sync creates the execution in the database
- Execution appears in the list

❌ **What's NOT Working:**
- Execution shows as "Ongoing" instead of "Completed"
- Status remains "in_progress" even though user finished it offline
- The completion step is failing silently

## Root Cause

In `syncSingleMaintenanceExecution()` in `syncProcessor.js`:

1. Execution is created with status from offline data
2. Checklist completions are synced
3. **IF status is 'completed'**, code tries to call `/complete` endpoint
4. The `/complete` endpoint call is failing (500 error or silent failure)

## The Problem

The offline execution has:
```javascript
{
  status: 'completed',  // Set when user clicked "Finish"
  checklist_completions: [...],  // All the completed items
  ...
}
```

But when syncing:
1. `checklist_completions` is removed from the data sent to create execution
2. Execution is created with `status: 'in_progress'` (default)
3. Checklist completions are synced separately
4. Complete endpoint is called but fails

## Solution

We need to include the status when creating the execution, so it's created as "completed" from the start.

### Option 1: Send Status in Create (RECOMMENDED)
Modify the sync to include status when creating:

```javascript
// In syncSingleMaintenanceExecution
const { tempId, synced, timestamp, protocol, machine, checklist_completions, ...apiData } = execution;

// apiData now includes: status, protocol_id, machine_id, machine_hours_at_service, etc.
```

This way, if the execution was completed offline, it's created as completed.

### Option 2: Fix the Complete Endpoint Call
The current code tries to complete after creation, but it's failing. Need to check why.

## Immediate Fix

The simplest fix is to NOT remove `status` from the data sent to the backend. The backend schema accepts it:

```python
class MaintenanceExecutionCreate(BaseModel):
    machine_id: uuid.UUID
    protocol_id: Optional[uuid.UUID] = None
    ...
    status: Optional[MaintenanceExecutionStatusEnum] = MaintenanceExecutionStatusEnum.IN_PROGRESS
    ...
```

So we can send `status: 'completed'` and it will be created as completed.

## Files to Modify

1. `frontend/src/services/syncProcessor.js` - Line ~260
   - Change what fields are removed from execution data
   - Keep `status` field in the data sent to backend

## Testing Steps

1. Clear IndexedDB (remove old test executions)
2. Go offline
3. Start maintenance
4. Complete all items
5. Finish maintenance (status becomes 'completed')
6. Go online
7. Wait for sync
8. Check execution list - should show as "Completed" not "Ongoing"

## Next Steps

I'll create the fix now...
