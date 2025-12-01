# Stock Adjustments Issue - Analysis and Fix

## Problem

Stock adjustments made through the Warehouses page don't appear in the Adjustment History.

## Root Cause Analysis

### Database Tables (Confusion)

There are **TWO tables** for adjustments:

1. **`inventory_adjustments`** (LEGACY - NOT USED)
   - Empty table
   - No model in `models.py`
   - Referenced in old `inventory_workflow` code
   - Should be deprecated/removed

2. **`stock_adjustments`** (CURRENT - SHOULD BE USED)
   - Has model: `StockAdjustment` in `models.py`
   - Linked to `Inventory` table via `inventory_id`
   - Has 3 old records from September
   - This is the correct table to use

### Code Paths

There are **TWO different endpoints** for creating adjustments:

**Path 1: Warehouse-specific adjustments** (CORRECT)
- Frontend: `inventoryService.createWarehouseStockAdjustment()`
- API: `POST /inventory/warehouse/{warehouse_id}/adjustment`
- Backend: `backend/app/routers/inventory.py` line 978
- Creates: `StockAdjustment` records ✅
- Used by: Warehouses page

**Path 2: Inventory workflow adjustments** (LEGACY)
- Frontend: `inventoryWorkflowService.createInventoryAdjustment()`
- API: `POST /inventory-workflows/adjustments`
- Backend: `backend/app/routers/inventory_workflow.py` line 308
- Creates: `InventoryAdjustment` records (table exists but no model!) ❌
- Used by: InventoryWorkflows page

### The Bug

When you make a stock adjustment from the Warehouses page:
1. ✅ Frontend calls the correct endpoint
2. ✅ Backend code tries to create `StockAdjustment` record
3. ❌ **BUT** the record is not being created (transaction might be failing silently)
4. ❌ Adjustment History shows nothing

## Investigation Steps

Run this on the server to check what's happening:

```bash
# Check stock_adjustments table
sudo docker exec -it abparts_db_prod psql -U abparts_user -d abparts_prod -c "SELECT * FROM stock_adjustments ORDER BY created_at DESC LIMIT 5;"

# Check if there are any recent adjustments
sudo docker exec -it abparts_db_prod psql -U abparts_user -d abparts_prod -c "SELECT COUNT(*) FROM stock_adjustments;"

# Check the API logs for errors during adjustment creation
sudo docker compose -f docker-compose.prod.yml logs api | grep -i "stock adjustment" | tail -20
```

## Likely Issues

1. **Transaction rollback** - The adjustment creation might be failing but error is not surfaced
2. **Permission issue** - User might not have permission to create adjustments
3. **Foreign key constraint** - `inventory_id` or `user_id` might be invalid
4. **Schema mismatch** - The request data might not match what the backend expects

## The Fix

We need to:

1. **Debug why StockAdjustment records aren't being created**
2. **Remove/deprecate the legacy `inventory_adjustments` table**
3. **Consolidate to use only `stock_adjustments` table**
4. **Ensure all adjustment creation goes through the correct endpoint**

## Recommended Approach

### Step 1: Check the actual error

Add better error logging to the adjustment creation endpoint:

```python
# In backend/app/routers/inventory.py around line 1010
try:
    db_adjustment = models.StockAdjustment(...)
    db.add(db_adjustment)
    # ... rest of code
    db.commit()
except Exception as e:
    logger.error(f"FAILED to create StockAdjustment: {str(e)}")
    logger.error(f"Traceback: {traceback.format_exc()}")
    db.rollback()
    raise
```

### Step 2: Test the adjustment creation

Make a test adjustment and check the logs immediately.

### Step 3: Fix the root cause

Once we see the actual error, we can fix it properly.

## Next Steps

1. Check the API logs for recent adjustment attempts
2. Try creating an adjustment and immediately check logs
3. Verify the database constraints and foreign keys
4. Fix the actual issue preventing record creation
