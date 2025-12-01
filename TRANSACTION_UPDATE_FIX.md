# Transaction Update Fix

## Problem Identified

When editing a part usage transaction quantity, the changes were not properly reflected in inventory because:

1. **Dual Tracking System**: The system tracks part usage in TWO places:
   - `transactions` table (affects inventory calculations)
   - `part_usage_items` table (detailed usage records)

2. **Incomplete Update**: The update endpoint only updated the `transactions` table, leaving `part_usage_items` out of sync

3. **Missing updated_at**: The `Transaction` model doesn't have an `updated_at` field to track when records are modified

## Solution Implemented

### 1. Enhanced Transaction Update Endpoint

Modified `backend/app/routers/transactions.py` to:
- Update the transaction record (as before)
- **Also update the corresponding `part_usage_item`** if it exists
- Match part_usage_items by: machine_id, part_id, old quantity, and time window

### 2. How It Works

```python
# When updating a consumption transaction:
1. Update the transaction record
2. Find the linked part_usage_item by:
   - Same machine_id
   - Same part_id  
   - Same old quantity
   - Within 5-minute time window of transaction_date
3. Update the part_usage_item quantity to match
4. Commit both changes together
```

### 3. Inventory Calculation

The inventory calculation system (`inventory_calculator.py`) already works correctly:
- It sums all transactions (not part_usage_items)
- Consumption transactions subtract from inventory (from_warehouse_id)
- When a transaction is updated, inventory automatically recalculates

## Files Modified

### backend/app/routers/transactions.py
- Enhanced `update_transaction()` endpoint
- Added logic to find and update linked `part_usage_item`
- Maintains data consistency between both tables

### frontend/src/components/PartUsageHistory.js  
- Added `inventoryUpdated` event dispatch after updates
- Added `inventoryUpdated` event dispatch after deletes
- Triggers automatic inventory refresh in listening components

## Testing

To test the fix:

1. **Restart the API**:
   ```bash
   docker-compose restart api
   ```

2. **Rebuild Frontend** (for event dispatch fix):
   ```bash
   docker-compose build web
   docker-compose up -d web
   ```

3. **Test Transaction Update**:
   - Open a machine details page
   - Go to "Parts Usage" tab
   - Edit a part usage quantity
   - Verify:
     - Transaction is updated ✓
     - Part_usage_item is updated ✓
     - Inventory display refreshes ✓
     - Calculated inventory is correct ✓

## Database Schema Notes

### Transactions Table
```sql
- id (UUID)
- transaction_type (consumption, transfer, etc.)
- part_id
- from_warehouse_id
- quantity  ← Updated by edit
- transaction_date
- machine_id
- notes
- created_at
- NO updated_at field (could be added in future)
```

### Part_Usage_Items Table
```sql
- id (UUID)
- usage_record_id (FK to part_usage_records)
- part_id
- quantity  ← Also updated by edit now
- notes
- created_at
- updated_at  ← Tracks modifications
```

## Why This Matters

1. **Data Consistency**: Both tracking systems stay in sync
2. **Accurate Reporting**: Reports using either table show same data
3. **Audit Trail**: Part usage history matches transaction history
4. **Inventory Accuracy**: Calculated inventory reflects actual usage

## Future Improvements

1. **Add updated_at to Transaction**: Track when transactions are modified
2. **Link Transaction to PartUsageItem**: Add foreign key for direct relationship
3. **Cascade Updates**: Use database triggers or ORM events for automatic sync
4. **Audit Log**: Track who changed what and when
