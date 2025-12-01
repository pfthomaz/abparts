# Calculated Inventory Implementation

## Overview
Inventory quantities are now **calculated** from transactions and adjustments, not stored as hardcoded values. This ensures accuracy and makes the system auditable.

## How It Works

### Single Source of Truth
Stock levels are calculated by:
1. Finding the last stock adjustment (if any) as the baseline
2. Adding all transactions after that adjustment:
   - **Incoming** (to_warehouse_id matches): +quantity
   - **Outgoing** (from_warehouse_id matches): -quantity

### Formula
```
Current Stock = Last Adjustment Quantity + Sum of Transactions
```

## Updated Functions

### Backend (Python)

#### Core Calculator (`backend/app/crud/inventory_calculator.py`)
- `calculate_current_stock()` - Calculate stock for one part in one warehouse
- `calculate_all_warehouse_stock()` - Calculate stock for all parts in a warehouse
- `refresh_inventory_cache()` - Update cached values (optional)
- `get_inventory_with_calculated_stock()` - Get inventory with calculated values

#### Updated CRUD Functions (`backend/app/crud/inventory.py`)
- ✅ `get_inventory_by_warehouse()` - Now uses calculated stock
- ✅ `get_inventory_aggregation_by_organization()` - Now uses calculated stock

#### Updated Transaction Handling (`backend/app/crud/transaction.py`)
- ✅ `update_inventory()` - No longer updates current_stock, just ensures record exists
- ✅ `create_transaction()` - Creates transaction records only

#### Updated Stock Adjustments (`backend/app/crud/stock_adjustments.py`)
- ✅ `create_stock_adjustment()` - Uses calculated stock for quantity_before
- ✅ No longer updates inventory.current_stock directly

### API Endpoints

#### New Endpoints (`/inventory/calculated/`)
- `GET /{warehouse_id}/{part_id}` - Get calculated stock for specific part
- `GET /{warehouse_id}` - Get all calculated stock for warehouse
- `GET /` - Get all inventory with calculated values
- `POST /refresh-cache` - Refresh cached values

#### Updated Endpoints
- ✅ `GET /inventory/warehouse/{warehouse_id}` - Returns calculated stock
- ✅ `GET /inventory/organization/{organization_id}/aggregated` - Returns calculated totals

## Benefits

### 1. Accuracy
- No drift between transactions and inventory
- Always correct, even if cache is stale

### 2. Auditability
- Full transaction history
- Can calculate stock "as of" any date
- Easy to trace discrepancies

### 3. Flexibility
- Can delete/edit transactions without breaking inventory
- Can recalculate at any time
- Easy to add new transaction types

### 4. Data Integrity
- Transactions are immutable records
- Balance is derived, not stored
- Like a bank account ledger

## Database Changes

### Removed
- ❌ Database trigger `trigger_update_inventory_on_transaction` (was causing double updates)
- ❌ Database function `update_inventory_on_transaction()`

### Kept
- ✅ `inventory.current_stock` field (now used as optional cache)
- ✅ All transaction records
- ✅ All stock adjustment records

## Migration Notes

### For Development
1. Remove the trigger: `./remove_duplicate_inventory_trigger.sh`
2. Restart API: `docker compose restart api`
3. Clear browser cache

### For Production
1. Run the same trigger removal script on production
2. Optionally refresh cache: `POST /inventory/calculated/refresh-cache`
3. Restart API

## Performance Considerations

### Calculation Cost
- Calculating stock requires querying transactions and adjustments
- For high-volume systems, consider:
  - Caching calculated values in `current_stock`
  - Running periodic cache refresh jobs
  - Adding database indexes on transaction dates

### Current Implementation
- Calculates on-demand for accuracy
- Cache field available but not required
- Suitable for systems with <10,000 transactions/day

### Optimization Options
1. **Cache refresh job**: Run hourly/daily to update `current_stock`
2. **Materialized views**: Create database views for common queries
3. **Redis caching**: Cache calculated values with TTL

## Testing

### Verify Calculated Values
```bash
# Check what API returns
./test_inventory_api.sh

# Compare calculated vs cached
curl http://localhost:8000/inventory/calculated/
```

### Refresh Cache
```bash
curl -X POST http://localhost:8000/inventory/calculated/refresh-cache
```

## Troubleshooting

### Stock values don't match
1. Check if browser is caching: Hard refresh (Ctrl+Shift+R)
2. Verify API is returning calculated values: Check network tab
3. Refresh cache: `POST /inventory/calculated/refresh-cache`

### Performance issues
1. Add indexes on transaction_date and warehouse_id
2. Enable cache refresh job
3. Consider materialized views for reports

### Discrepancies in history
1. Check stock adjustment records
2. Verify transaction records are complete
3. Use calculated endpoint to see actual values

## Future Enhancements

### Planned
- [ ] Scheduled cache refresh job
- [ ] Historical stock calculation (as-of date)
- [ ] Stock movement reports
- [ ] Inventory reconciliation tools

### Possible
- [ ] Real-time stock updates via WebSocket
- [ ] Predictive stock levels
- [ ] Automated reorder suggestions
- [ ] Multi-currency support for valuations
