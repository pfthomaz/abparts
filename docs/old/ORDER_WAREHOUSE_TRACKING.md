# Order Warehouse Tracking Implementation

## Summary

Added `customer_order_id` field to the `transactions` table to link order receipts with their destination warehouses. This enables proper audit trails and allows the calendar view to display which warehouse received each order.

## Database Changes

### New Column
- **Table:** `transactions`
- **Column:** `customer_order_id` (UUID, nullable, foreign key to `customer_orders.id`)
- **Index:** `ix_transactions_customer_order_id` for query performance

### Migration
Manual column addition completed. Migration file created at:
`backend/alembic/versions/20251124_add_customer_order_id_to_transactions.py`

## Backend Changes

### Models (`backend/app/models.py`)
1. Added `customer_order_id` field to `Transaction` model
2. Added relationship: `Transaction.customer_order` → `CustomerOrder`
3. Added reverse relationship: `CustomerOrder.transactions` → `Transaction[]`

### API (`backend/app/routers/customer_orders.py`)

#### Order Receipt Endpoint
When a customer confirms order receipt (`POST /customer_orders/{order_id}/receive`):
1. Creates transaction records for each order item with `customer_order_id` populated
2. Updates inventory in the receiving warehouse
3. Links transactions to the order for audit trail

#### Order List Endpoint
When fetching orders (`GET /customer_orders/`):
1. Eagerly loads transactions and their warehouses
2. Extracts `receiving_warehouse_name` from linked transactions
3. Includes warehouse name in API response

## Frontend Changes

### Auto-Select Warehouse (`frontend/src/pages/Orders.js`)

#### ConfirmReceiptForm (Customer users)
- Auto-selects warehouse if organization has only one warehouse
- Warehouse selection is mandatory (required field)
- Only shows warehouses belonging to the customer organization

#### OrderFulfillmentForm (Oraseas users)
- Auto-selects warehouse if customer organization has only one warehouse
- Warehouse selection is mandatory (required field)
- Only shows warehouses belonging to the customer organization
- Shows warning if no warehouses exist

### Calendar View (`frontend/src/components/OrderCalendarView.js`)
- Displays warehouse name for Received/Delivered orders
- Shows format: `#ORDER_ID - CUSTOMER_NAME → WAREHOUSE_NAME`
- Includes warehouse in order detail modal

## Benefits

1. **Audit Trail:** Every order receipt is linked to specific transactions
2. **Traceability:** Can track which warehouse received which order
3. **Error Correction:** If wrong warehouse is recorded, can update the transaction
4. **Calendar Visibility:** Users can see at a glance where orders were delivered
5. **User Experience:** Auto-selects warehouse for single-warehouse organizations

## Testing

After restarting the API:
1. Create a new customer order
2. Ship the order (Oraseas user)
3. Receive the order and select a warehouse (Customer user)
4. Check calendar view - warehouse name should appear
5. Verify transactions table has `customer_order_id` populated
6. Verify inventory was updated in the correct warehouse

## Future Enhancements

- Allow editing warehouse on received orders (updates transaction)
- Show warehouse history if order was moved between warehouses
- Add warehouse filter to calendar view
- Generate warehouse-specific receiving reports
