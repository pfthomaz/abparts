# Tomorrow: Inventory Management & Transaction Integrity

## Priority 1: Fix Receiving Warehouse Display

### Task 1.1: Verify Backend Returns Warehouse Name
- [x] Added `receiving_warehouse_name` to `CustomerOrderResponse` schema
- [ ] Restart API and verify field appears in `/customer_orders/` response
- [ ] Test with order ID: `f732cf73-48e3-449c-9107-e1e00d623cd8`

### Task 1.2: Display in List View
- [x] Added warehouse display in Orders.js line ~550
- [ ] Verify it shows: "Warehouse: [name]" for Received/Delivered orders
- [ ] Format suggestion: Show in order header as "Order for Company (Warehouse)"

### Task 1.3: Display in Calendar View
- [x] Added warehouse display in OrderCalendarView.js
- [ ] Verify format: "#ORDER_ID - CUSTOMER → WAREHOUSE"
- [ ] Check modal detail view includes warehouse

## Priority 2: Verify Order Receipt Inventory Updates

### Task 2.1: Test Current Implementation
```bash
# Check if inventory was updated when order was received
SELECT i.id, i.current_stock, w.name as warehouse, p.part_number, p.name as part_name
FROM inventory i
JOIN warehouses w ON i.warehouse_id = w.id
JOIN parts p ON i.part_id = p.id
WHERE w.id = 'ac0f825a-94c1-4581-a868-17172e79c5ff'
ORDER BY i.last_updated DESC;
```

### Task 2.2: Verify Transaction Creation
- [ ] Check transactions table has `customer_order_id` populated
- [ ] Verify `to_warehouse_id` matches selected warehouse
- [ ] Confirm `current_stock` increased by order quantity

### Task 2.3: Edge Cases
- [ ] Test receiving order with parts not yet in inventory (creates new record)
- [ ] Test receiving order with parts already in inventory (updates existing)
- [ ] Test decimal quantities (e.g., 2.5 liters)

## Priority 3: Order Editing & Deletion with Inventory Impact

### Task 3.1: Design Considerations
**When editing a received order:**
- If warehouse changes: reverse old transaction, create new one
- If quantities change: adjust inventory accordingly
- If order is "unreceived": reverse all inventory changes

**When deleting a received order:**
- Reverse all inventory transactions
- Delete or mark transactions as void
- Prevent deletion if parts have been used from that stock

### Task 3.2: Implementation
```python
# backend/app/routers/customer_orders.py

@router.put("/{order_id}/unreceive")
def unreceive_order(order_id: str, db: Session):
    """Reverse inventory changes when unreceiving an order"""
    # Find all transactions for this order
    # Reverse inventory changes
    # Update order status back to 'Shipped'
    pass

@router.delete("/{order_id}")
def delete_order(order_id: str, db: Session):
    """Delete order and reverse inventory if received"""
    # Check if order was received
    # If yes, reverse inventory changes
    # Delete transactions
    # Delete order
    pass
```

### Task 3.3: Frontend UI
- [ ] Add "Edit Order" button (only for non-received orders)
- [ ] Add "Unreceive Order" button (for received orders)
- [ ] Add "Delete Order" button with confirmation
- [ ] Show warning if deleting will affect inventory

## Priority 4: Stock Reset Functionality

### Task 4.1: Simple UI Design
**Warehouse Stock Reset Page:**
```
┌─────────────────────────────────────────┐
│ Reset Stock for: [Warehouse Dropdown]  │
│                                         │
│ ⚠️  WARNING: This will set all parts   │
│    in this warehouse to specified      │
│    quantities. Use for initialization  │
│    or corrections only.                │
│                                         │
│ [Upload CSV] or [Manual Entry]         │
│                                         │
│ Part Number | Current | New Quantity   │
│ ─────────────────────────────────────  │
│ WHC-005     | 10.000  | [____]         │
│ ESE-011     | 5.000   | [____]         │
│                                         │
│ Reason: [Dropdown: Initial Stock /     │
│          Stocktake Correction /        │
│          System Reset]                 │
│                                         │
│ Notes: [________________]              │
│                                         │
│ [Cancel] [Reset Stock]                 │
└─────────────────────────────────────────┘
```

### Task 4.2: Backend Implementation
```python
@router.post("/warehouses/{warehouse_id}/reset-stock")
def reset_warehouse_stock(
    warehouse_id: str,
    reset_data: StockResetRequest,
    db: Session
):
    """Reset all stock in a warehouse to specified quantities"""
    # For each part in reset_data:
    #   - Calculate difference from current stock
    #   - Create adjustment transaction
    #   - Update inventory.current_stock
    #   - Log in audit trail
    pass
```

### Task 4.3: CSV Import Format
```csv
part_number,quantity
WHC-005,10.000
ESE-011,5.000
WHC-007,25.000
```

## Priority 5: Warehouse-to-Warehouse Transfers

### Task 5.1: Verify Current Transfer Logic
- [ ] Check if transfers create two transactions (from + to)
- [ ] Verify inventory decreases in source warehouse
- [ ] Verify inventory increases in destination warehouse

### Task 5.2: Edit Transfer Functionality
```python
@router.put("/transactions/{transaction_id}/transfer")
def edit_transfer(transaction_id: str, edit_data: TransferEditRequest, db: Session):
    """Edit a warehouse transfer and update inventories"""
    # Find original transfer transactions (from + to)
    # Reverse original inventory changes
    # Apply new transfer with updated data
    # Create new transactions
    pass
```

### Task 5.3: Delete Transfer Functionality
- [ ] Find both transactions (from + to)
- [ ] Reverse inventory changes
- [ ] Mark transactions as deleted or remove them
- [ ] Update audit trail

## Priority 6: Part Usage Records Management

### Task 6.1: Current Part Usage Flow
- [ ] Verify part usage decreases warehouse inventory
- [ ] Check transaction is created with `machine_id`
- [ ] Confirm `from_warehouse_id` is set correctly

### Task 6.2: Edit Part Usage
```python
@router.put("/part-usage/{usage_id}")
def edit_part_usage(usage_id: str, edit_data: PartUsageEditRequest, db: Session):
    """Edit part usage record and adjust inventory"""
    # Get original usage record
    # Reverse original inventory decrease
    # Apply new usage with updated quantity
    # Update transaction
    pass
```

### Task 6.3: Delete Part Usage
- [ ] Reverse inventory decrease (add parts back to warehouse)
- [ ] Delete or void transaction
- [ ] Delete part usage record
- [ ] Update machine maintenance history if applicable

## Testing Checklist

### Scenario 1: Order Receipt
1. Create order with 3 parts
2. Ship order
3. Receive order, select warehouse
4. ✓ Verify inventory increased
5. ✓ Verify transaction created with customer_order_id
6. ✓ Verify warehouse name shows in list and calendar

### Scenario 2: Order Unreceive
1. Take a received order
2. Click "Unreceive"
3. ✓ Verify inventory decreased back
4. ✓ Verify order status changed to 'Shipped'
5. ✓ Verify transactions marked as reversed

### Scenario 3: Stock Reset
1. Go to warehouse stock reset page
2. Enter new quantities for all parts
3. Submit with reason "Initial Stock Entry"
4. ✓ Verify all inventories updated
5. ✓ Verify adjustment transactions created
6. ✓ Verify audit trail logged

### Scenario 4: Warehouse Transfer
1. Transfer 5 units of part from Warehouse A to B
2. ✓ Verify A decreased by 5
3. ✓ Verify B increased by 5
4. Edit transfer to 3 units
5. ✓ Verify A now has 2 more units
6. ✓ Verify B now has 2 fewer units

### Scenario 5: Part Usage
1. Record part usage on machine
2. ✓ Verify warehouse inventory decreased
3. Edit usage to different quantity
4. ✓ Verify inventory adjusted correctly
5. Delete usage record
6. ✓ Verify inventory restored

## Database Queries for Verification

```sql
-- Check inventory changes for a warehouse
SELECT 
    p.part_number,
    p.name,
    i.current_stock,
    i.last_updated
FROM inventory i
JOIN parts p ON i.part_id = p.id
WHERE i.warehouse_id = 'WAREHOUSE_ID'
ORDER BY i.last_updated DESC;

-- Check transactions for an order
SELECT 
    t.id,
    t.transaction_type,
    t.quantity,
    t.customer_order_id,
    w.name as to_warehouse
FROM transactions t
LEFT JOIN warehouses w ON t.to_warehouse_id = w.id
WHERE t.customer_order_id = 'ORDER_ID';

-- Check all transactions for a part
SELECT 
    t.transaction_type,
    t.quantity,
    t.transaction_date,
    wf.name as from_warehouse,
    wt.name as to_warehouse,
    m.serial_number as machine
FROM transactions t
LEFT JOIN warehouses wf ON t.from_warehouse_id = wf.id
LEFT JOIN warehouses wt ON t.to_warehouse_id = wt.id
LEFT JOIN machines m ON t.machine_id = m.id
WHERE t.part_id = 'PART_ID'
ORDER BY t.transaction_date DESC;
```

## Notes

- All inventory changes MUST create transactions for audit trail
- Transactions should never be truly deleted, only marked as void/reversed
- Always validate that source warehouse has sufficient stock before transfers/usage
- Consider adding inventory snapshots for major operations (stock resets)
- UI should clearly show impact before confirming destructive operations
