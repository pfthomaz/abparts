# Parts Usage System Architecture

## How Part Usage is Recorded

### Current System (Dual Tracking)

When a part is used in a machine, the system creates records in **TWO places**:

#### 1. Part Usage Records (Detailed Tracking)
```
part_usage_records (parent record)
  ├── id
  ├── machine_id
  ├── from_warehouse_id
  ├── usage_date
  ├── service_type
  ├── machine_hours
  └── performed_by_user_id

part_usage_items (child records - one per part)
  ├── id
  ├── usage_record_id (FK to part_usage_records)
  ├── part_id
  ├── quantity  ← THE QUANTITY USED
  └── notes
```

#### 2. Transactions (Inventory Impact)
```
transactions
  ├── id
  ├── transaction_type = 'consumption'
  ├── part_id
  ├── from_warehouse_id  ← Parts come FROM warehouse
  ├── to_warehouse_id = NULL (consumed, not transferred)
  ├── machine_id
  ├── quantity  ← THE QUANTITY USED
  ├── transaction_date
  └── performed_by_user_id
```

### The Role of the Transactions Table

The `transactions` table is the **SINGLE SOURCE OF TRUTH** for inventory calculations:

1. **Inventory Calculation**: 
   - Start with baseline (from stock_adjustments)
   - Add/subtract ALL transactions
   - `to_warehouse_id` = ADD to inventory
   - `from_warehouse_id` = SUBTRACT from inventory

2. **Transaction Types**:
   - `creation`: New parts added (to_warehouse_id)
   - `transfer`: Move between warehouses (from → to)
   - `consumption`: Parts used in machines (from_warehouse_id, machine_id)
   - `adjustment`: Stock corrections

3. **Audit Trail**: Complete history of all parts movements

### The Problem

When you edit a part usage through the UI:
- ✓ Transaction is updated
- ✗ Part_usage_item is NOT updated
- ✓ Inventory calculation uses transactions (correct)
- ✗ But part_usage_items shows old quantity (inconsistent)

**Result**: The two tracking systems are out of sync!

## Why Two Systems?

1. **part_usage_records/items**: Rich context about the service event
   - What service was performed
   - Machine hours at time of service
   - Multiple parts used in one service event
   - Service-specific notes

2. **transactions**: Simple, consistent inventory tracking
   - Every parts movement is a transaction
   - Easy to calculate inventory
   - Uniform structure for all movement types

## The Correct Solution

### Option A: Make Transactions Primary (Recommended)
- Store part usage details in transactions
- Eliminate part_usage_records/items
- Simpler, single source of truth

### Option B: Keep Both, But Link Them
- Add `transaction_id` FK to part_usage_items
- When updating transaction, find linked part_usage_item
- Update both together

### Option C: Make Part Usage Primary
- Calculate inventory from part_usage_items + other sources
- More complex, multiple sources of truth

## Current Implementation Issues

1. **No updated_at on transactions**: Can't track when edited
2. **No link between tables**: Hard to find matching records
3. **Manual sync required**: Update endpoint must update both
4. **Inconsistent data**: Two tables can show different quantities

## Recommended Fix

1. Add `updated_at` to all tables
2. Add `transaction_id` FK to part_usage_items
3. Update both records together
4. Consider consolidating to single system long-term
