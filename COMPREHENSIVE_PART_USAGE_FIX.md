# Comprehensive Part Usage Fix

## Root Cause Analysis

After thorough investigation, the issue is:

1. **Backend IS calculating correctly** - `calculate_current_stock()` works
2. **Transaction updates ARE saving** - Database is updated
3. **Frontend IS NOT refreshing** - The UI doesn't refetch after edit

The problem is **NOT** in the calculation, but in the **UI refresh flow**.

## The Real Issue

When you edit a part usage:
1. ✓ Frontend sends update request
2. ✓ Backend updates transaction
3. ✓ Backend calculates new inventory correctly
4. ✗ **Frontend doesn't refetch inventory**
5. ✗ **UI still shows old cached value**

## Why the Event System Isn't Working

The `inventoryUpdated` event is dispatched, but:
- The `WarehouseInventoryView` component might not be mounted
- The event might not be reaching the right component
- The component might not be in the same page/context

## The Correct Fix

### 1. Make the callback actually refresh inventory

In `MachineDetails.js`, the `onUsageDeleted` callback calls `fetchMachineData()`, which refreshes machine data but **NOT inventory**.

We need to:
- Pass a callback that refreshes BOTH machine data AND inventory
- Or dispatch a global event that ALL inventory components listen for
- Or force a full page refresh after edit

### 2. Add updated_at columns (for audit trail)

This doesn't fix the display issue, but it's good practice:
- Track when records are modified
- Enable audit trails
- Support conflict detection

### 3. Keep part_usage_items in sync

When updating a transaction, also update the linked part_usage_item.

## Implementation Plan

### Phase 1: Fix the UI Refresh (CRITICAL)

**Option A: Force inventory refetch in callback**
```javascript
// In MachineDetails.js
const handleUsageUpdate = async () => {
  await fetchMachineData();  // Refresh machine data
  // Dispatch event for inventory components
  window.dispatchEvent(new CustomEvent('inventoryUpdated', {
    detail: { action: 'usage_updated' }
  }));
};
```

**Option B: Reload the page after edit**
```javascript
// In PartUsageHistory.js after successful update
window.location.reload();
```

**Option C: Pass inventory refresh function down**
```javascript
// Pass from parent that has inventory state
<PartUsageHistory 
  machineId={machineId}
  onUsageUpdated={handleUsageAndInventoryRefresh}
/>
```

### Phase 2: Add updated_at columns

Run the migration to add `updated_at` to all tables.

### Phase 3: Sync part_usage_items

Update the transaction update endpoint to also update linked part_usage_items.

## Quick Fix (Immediate)

The fastest fix is to reload the page after editing:

```javascript
// In PartUsageHistory.js, after successful update:
await transactionService.updateTransaction(editingUsage.id, updatePayload);
window.location.reload();  // Force full refresh
```

This ensures:
- All data is refetched
- All calculations are re-run
- All displays are updated

## Proper Fix (Better UX)

1. Create a global inventory refresh function
2. Store it in a context or event bus
3. Call it after any inventory-affecting operation
4. All inventory displays subscribe to updates

## Testing

After applying the fix:

1. Open machine details
2. Edit a part usage quantity
3. **Expected**: Inventory updates immediately (or page reloads)
4. Verify in database that transaction was updated
5. Verify inventory calculation is correct

## Files to Modify

1. `frontend/src/components/PartUsageHistory.js` - Add reload or better refresh
2. `frontend/src/components/MachineDetails.js` - Pass inventory refresh callback
3. `backend/app/models.py` - Add updated_at to Transaction model
4. `backend/alembic/versions/add_updated_at_columns.py` - Migration
5. `backend/app/routers/transactions.py` - Sync part_usage_items on update
