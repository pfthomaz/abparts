# Diagnose Warehouse Name Issue

## Step 1: Restart the API
The schema was updated yesterday, so we need to ensure the API is running with the latest code:

```bash
docker-compose restart api
# Wait 5 seconds for it to start
sleep 5
docker-compose logs api --tail 20
```

## Step 2: Check the API Response
Open your browser's Developer Tools (F12), go to the Network tab, then:

1. Go to the Orders page in your app
2. Find the request to `GET /customer_orders/`
3. Click on it and go to the "Response" tab
4. Look for an order with status "Received" or "Delivered"
5. Check if it has a `receiving_warehouse_name` field

Example of what you should see:
```json
{
  "id": "f732cf73-48e3-449c-9107-e1e00d623cd8",
  "status": "Received",
  "customer_organization_name": "Kefalonia Fisheries SA",
  "receiving_warehouse_name": "Sparfish",  <-- THIS SHOULD BE HERE
  ...
}
```

## Step 3: If receiving_warehouse_name is NULL or missing

### Check if transaction exists:
```sql
SELECT 
    t.id,
    t.customer_order_id,
    t.to_warehouse_id,
    w.name as warehouse_name
FROM transactions t
LEFT JOIN warehouses w ON t.to_warehouse_id = w.id
WHERE t.customer_order_id = 'f732cf73-48e3-449c-9107-e1e00d623cd8';
```

If this returns a row with a warehouse_name, then the backend query isn't working.

### Check backend logs for errors:
```bash
docker-compose logs api | grep -i "error getting warehouse"
```

## Step 4: If field is completely missing from response

This means Pydantic is filtering it out. Check:

1. Is the API restarted? (schemas are loaded at startup)
2. Is there a typo in the schema field name?
3. Is FastAPI using a different response model?

## Step 5: Manual Test

Create a simple test endpoint to verify the query works:

```python
# Add to backend/app/routers/customer_orders.py

@router.get("/debug/{order_id}")
def debug_warehouse(order_id: str, db: Session = Depends(get_db)):
    order = db.query(models.CustomerOrder).filter(
        models.CustomerOrder.id == order_id
    ).first()
    
    if not order:
        return {"error": "Order not found"}
    
    txn = db.query(models.Transaction).filter(
        models.Transaction.customer_order_id == order.id,
        models.Transaction.to_warehouse_id.isnot(None)
    ).first()
    
    if not txn:
        return {
            "order_id": str(order.id),
            "status": order.status,
            "has_transaction": False
        }
    
    warehouse = db.query(models.Warehouse).filter(
        models.Warehouse.id == txn.to_warehouse_id
    ).first()
    
    return {
        "order_id": str(order.id),
        "status": order.status,
        "has_transaction": True,
        "transaction_id": str(txn.id),
        "to_warehouse_id": str(txn.to_warehouse_id),
        "warehouse_name": warehouse.name if warehouse else None
    }
```

Then visit: `http://localhost:8000/customer_orders/debug/f732cf73-48e3-449c-9107-e1e00d623cd8`

## Expected Results

✅ **Success**: You should see `receiving_warehouse_name` in the API response for Received orders
✅ **Frontend**: The warehouse name should appear in Orders list and Calendar view
✅ **Database**: Transactions table has `customer_order_id` populated

## If Still Not Working

The issue could be:
1. **API not restarted** - Old code still running
2. **Schema mismatch** - Pydantic filtering the field
3. **Query not finding transaction** - customer_order_id not set correctly
4. **Frontend caching** - Hard refresh the page (Ctrl+Shift+R)
