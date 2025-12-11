# Inventory Refresh Fix

## Problem
When updating or deleting a transaction in the Part Usage History, the transaction was being updated successfully in the database, but the inventory display wasn't refreshing to show the new calculated values.

## Root Cause
The `PartUsageHistory` component was calling `onUsageDeleted` callback after updates, but this only refreshed the machine data, not the inventory display. The inventory calculation system works correctly on the backend (it recalculates from transactions), but the frontend wasn't fetching the updated values.

## Solution
Added event dispatching to notify inventory components when transactions are updated or deleted:

1. **PartUsageHistory.js** - Now dispatches `inventoryUpdated` custom events after:
   - Transaction updates (edit)
   - Transaction deletes

2. **WarehouseInventoryView.js** - Already has a listener for `inventoryUpdated` events that automatically refreshes inventory when the event is received.

## Changes Made

### frontend/src/components/PartUsageHistory.js

Added event dispatching in two places:

1. After transaction update (in `handleEditSave`):
```javascript
// Dispatch a custom event to notify other components that inventory needs refresh
window.dispatchEvent(new CustomEvent('inventoryUpdated', {
  detail: {
    warehouseId: editingUsage.from_warehouse_id,
    partId: editingUsage.part_id,
    action: 'transaction_updated'
  }
}));
```

2. After transaction delete (in `handleDeleteConfirm`):
```javascript
// Dispatch a custom event to notify other components that inventory needs refresh
window.dispatchEvent(new CustomEvent('inventoryUpdated', {
  detail: {
    warehouseId: deleteConfirm.from_warehouse_id,
    partId: deleteConfirm.part_id,
    action: 'transaction_deleted'
  }
}));
```

## How It Works

1. User edits or deletes a part usage transaction
2. Transaction is updated/deleted in the database
3. Backend automatically recalculates inventory (using the calculated inventory system)
4. Frontend dispatches `inventoryUpdated` event
5. `WarehouseInventoryView` component (and any other listening components) receives the event
6. Inventory is automatically refetched and display updates

## Testing

To test the fix:

1. Rebuild the frontend:
   ```bash
   docker-compose build web
   docker-compose up -d web
   ```

2. Open a machine details page with part usage history
3. Edit a part usage quantity
4. Check that the inventory display updates immediately
5. Delete a part usage record
6. Check that the inventory display updates immediately

## Benefits

- Inventory display now stays in sync with transaction changes
- No manual refresh needed
- Works across all components that listen for `inventoryUpdated` events
- Leverages existing event system already in place
