# Stock Reset Doubling Issue - FIXED

## Root Cause

The stock reset was creating **adjustment transactions** that were being **processed twice**:

1. Stock reset sets `inventory.current_stock = 10` ✅
2. Stock reset creates adjustment transaction with `quantity = 10` 
3. Transaction processor sees the transaction and does `current_stock += 10` ❌
4. Result: `current_stock = 20` (DOUBLED!)

## The Fix

### 1. Added New Transaction Type

**File:** `backend/app/models.py`

Added `STOCK_RESET` to the `TransactionType` enum:

```python
class TransactionType(enum.Enum):
    CREATION = "creation"
    TRANSFER = "transfer"
    CONSUMPTION = "consumption"
    ADJUSTMENT = "adjustment"
    STOCK_RESET = "stock_reset"  # NEW: For stock reset operations
```

### 2. Updated Stock Reset Endpoint

**File:** `backend/app/routers/warehouses.py`

Changed the transaction type from `"adjustment"` to `"stock_reset"`:

```python
transaction = models.Transaction(
    transaction_type="stock_reset",  # Changed from "adjustment"
    # ... rest of transaction
)
```

## Why This Works

- **Stock reset transactions** are now type `"stock_reset"` instead of `"adjustment"`
- **Transaction processor** only processes specific types (transfer, consumption, etc.)
- **Stock reset transactions** are NOT processed by transaction processor
- **Inventory is updated directly** with absolute values
- **Audit trail is maintained** (transactions are still recorded)

## IMPORTANT: Restart Required

**You MUST restart the backend Docker container** for the enum change to take effect:

```bash
docker-compose restart api
```

Or rebuild if restart doesn't work:

```bash
docker-compose down
docker-compose up -d
```

## How Stock Reset Now Works

1. User enters new stock quantities in Stock Reset tab
2. Frontend sends absolute values to backend
3. Backend:
   - Creates `stock_reset` transaction for audit (NOT processed)
   - **Directly sets** `inventory.current_stock = new_quantity`
   - Commits changes
4. Inventory shows correct values (no doubling)

## Inventory Calculation Formula

```
Current Stock = Last Stock Reset Value 
              + Purchases (from orders)
              + Transfers In (from other warehouses)
              - Transfers Out (to other warehouses)
              - Part Usages (consumption in machines)
```

Stock reset transactions are NOT included in this calculation because they set absolute values.

## Testing After Restart

1. Restart backend: `docker-compose restart api`
2. Go to Warehouses page
3. Select a warehouse
4. Click "View Inventory"
5. Go to "Stock Reset" tab
6. Add a part with existing stock (e.g., current stock = 10)
7. Change quantity to 15
8. Click "Apply Stock Reset"
9. Check "Current Inventory" tab
10. **Expected:** Stock should be 15 (not 25 or 30)

## Files Modified

1. `backend/app/models.py` - Added STOCK_RESET to TransactionType enum
2. `backend/app/routers/warehouses.py` - Changed transaction type to "stock_reset"
3. `frontend/src/components/StockResetTab.js` - Added console logging for debugging

## Rollback Plan

If issues persist, you can temporarily disable transaction creation in stock reset:

```python
# In backend/app/routers/warehouses.py, comment out transaction creation:
# if difference != 0:
#     transaction = models.Transaction(...)
#     db.add(transaction)
```

This will still update inventory correctly but won't create audit transactions.
