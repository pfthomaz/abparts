# Customer Order Workflow Analysis

## Current Status

Based on the previous session's work, the system now correctly filters customer orders:
- **Oraseas EE users** see orders placed TO them (where `oraseas_organization_id` matches)
- **Customer organizations** see orders placed BY them (where `customer_organization_id` matches)

## Order Status Workflow

### Current Status Values
The system uses these status values:
- `Requested` - Initial state when customer places order
- `Pending` - Order approved by Oraseas EE admin
- `Shipped` - Oraseas EE marks order as shipped
- `Received` - Customer confirms receipt
- `Delivered` - Final state (currently same as Received)
- `Cancelled` - Order cancelled

### Current Date Fields in CustomerOrder Model
```python
order_date                  # When order was placed
expected_delivery_date      # Expected delivery date
actual_delivery_date        # When order was actually delivered/received
```

## Workflow Analysis

### 1. Customer Places Order
**Who:** Customer organization user  
**Action:** Creates customer order with status `Requested`  
**Current Implementation:** ✅ Working via CustomerOrderForm

### 2. Oraseas EE Views Incoming Orders
**Who:** Oraseas EE admin/user  
**Action:** Views orders placed TO them  
**Current Implementation:** ✅ Fixed in previous session - filters by `oraseas_organization_id`

### 3. Oraseas EE Ships Order
**Who:** Oraseas EE admin  
**Action:** Marks order as `Shipped`  
**Current Implementation:** ⚠️ Partially implemented

**Current Issues:**
- The "Fulfill Order" button changes status to `Received` (skips `Shipped`)
- No dedicated "Mark as Shipped" action for Oraseas EE
- No shipping date tracking (uses `actual_delivery_date` for fulfillment)

**What's Needed:**
- Add "Mark as Shipped" button for Oraseas EE users
- Add `shipped_date` field to track when Oraseas EE ships
- Keep `actual_delivery_date` for when customer receives

### 4. Customer Records Arrival
**Who:** Customer organization user  
**Action:** Confirms receipt and records arrival date  
**Current Implementation:** ❌ Not implemented

**What's Needed:**
- Customer users should see a "Confirm Receipt" button on shipped orders
- This should update status to `Received` and set `actual_delivery_date`

## Recommended Implementation

### Database Changes

#### Option A: Add shipped_date field (Recommended)
```python
# In CustomerOrder model
shipped_date = Column(DateTime(timezone=True), nullable=True)  # When Oraseas EE ships
actual_delivery_date = Column(DateTime(timezone=True), nullable=True)  # When customer receives
```

This provides clear separation:
- `shipped_date` = Oraseas EE action
- `actual_delivery_date` = Customer action

#### Option B: Use existing fields differently
Keep current structure but clarify usage:
- `expected_delivery_date` = Estimated delivery
- `actual_delivery_date` = When customer receives (set by customer)
- Add notes field to track shipping date

**Recommendation:** Option A is cleaner and more explicit.

### UI Changes

#### For Oraseas EE Users (viewing orders TO them)

**Order Card Actions:**
```javascript
// Status: Requested or Pending
- [Approve] button (changes to Pending)
- [Mark as Shipped] button (changes to Shipped, sets shipped_date)

// Status: Shipped
- [View Details] button
- Show "Waiting for customer confirmation"

// Status: Received
- [View Details] button
- Show shipped_date and actual_delivery_date
```

#### For Customer Users (viewing orders BY them)

**Order Card Actions:**
```javascript
// Status: Requested or Pending
- [View Details] button
- Show "Awaiting approval/shipment"

// Status: Shipped
- [Confirm Receipt] button (changes to Received, sets actual_delivery_date)
- Show shipped_date

// Status: Received
- [View Details] button
- Show complete timeline
```

### Backend Changes

#### 1. Add Migration for shipped_date
```python
# alembic/versions/xxx_add_shipped_date.py
def upgrade():
    op.add_column('customer_orders', 
        sa.Column('shipped_date', sa.DateTime(timezone=True), nullable=True))

def downgrade():
    op.drop_column('customer_orders', 'shipped_date')
```

#### 2. Update Schema
```python
# backend/app/schemas.py
class CustomerOrderBase(BaseModel):
    # ... existing fields ...
    shipped_date: Optional[datetime] = None
    actual_delivery_date: Optional[datetime] = None
```

#### 3. Add Endpoint for Shipping
```python
# backend/app/routers/customer_orders.py
@router.patch("/{order_id}/ship")
async def ship_customer_order(
    order_id: uuid.UUID,
    shipped_date: datetime,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mark order as shipped (Oraseas EE only)"""
    # Verify user is from Oraseas EE
    # Update order status to 'Shipped'
    # Set shipped_date
    # Return updated order
```

#### 4. Add Endpoint for Customer Receipt
```python
# backend/app/routers/customer_orders.py
@router.patch("/{order_id}/confirm-receipt")
async def confirm_order_receipt(
    order_id: uuid.UUID,
    actual_delivery_date: datetime,
    notes: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Confirm order receipt (Customer only)"""
    # Verify user is from customer organization that placed order
    # Update order status to 'Received'
    # Set actual_delivery_date
    # Return updated order
```

### Frontend Changes

#### 1. Update Orders.js

Add role-based action buttons:
```javascript
const canShipOrder = (order) => {
  // Oraseas EE users can ship Pending orders
  return user && 
    (user.organization_name?.includes('Oraseas') || user.organization_name?.includes('BossServ')) &&
    (user.role === 'admin' || user.role === 'super_admin') &&
    order.status === 'Pending';
};

const canConfirmReceipt = (order) => {
  // Customer users can confirm receipt of Shipped orders
  return user && 
    order.customer_organization_id === user.organization_id &&
    order.status === 'Shipped';
};
```

#### 2. Add Ship Order Modal
```javascript
const ShipOrderForm = ({ order, onSubmit, onClose }) => {
  const [formData, setFormData] = useState({
    shipped_date: new Date().toISOString().split('T')[0],
    tracking_number: '',
    notes: ''
  });
  // ... form implementation
};
```

#### 3. Add Confirm Receipt Modal
```javascript
const ConfirmReceiptForm = ({ order, onSubmit, onClose }) => {
  const [formData, setFormData] = useState({
    actual_delivery_date: new Date().toISOString().split('T')[0],
    receiving_warehouse_id: '',
    notes: ''
  });
  // ... form implementation
};
```

## Complete Workflow Example

### Scenario: Customer orders parts from Oraseas EE

1. **Customer User (e.g., BossServ Cyprus admin):**
   - Goes to Orders page
   - Clicks "Add Customer Order"
   - Selects parts and quantities
   - Submits order
   - Order created with status `Requested`

2. **Oraseas EE Admin:**
   - Goes to Orders page
   - Sees order in "Customer Orders (Received)" section
   - Reviews order details
   - Clicks "Approve" → Status changes to `Pending`
   - Prepares shipment
   - Clicks "Mark as Shipped" → Status changes to `Shipped`, `shipped_date` set
   - System could send email notification to customer

3. **Customer User:**
   - Sees order status changed to `Shipped` on Orders page
   - Sees `shipped_date` displayed
   - Receives physical shipment
   - Clicks "Confirm Receipt"
   - Selects receiving warehouse
   - Sets actual delivery date
   - Submits → Status changes to `Received`, `actual_delivery_date` set
   - Inventory automatically updated in selected warehouse

## Permission Matrix

| Action | Super Admin | Oraseas EE Admin | Customer Admin | Customer User |
|--------|-------------|------------------|----------------|---------------|
| Create customer order | ✅ | ✅ | ✅ | ✅ |
| View all orders | ✅ | ❌ | ❌ | ❌ |
| View org's orders | ✅ | ✅ | ✅ | ✅ |
| Approve order | ✅ | ✅ (own org) | ❌ | ❌ |
| Mark as shipped | ✅ | ✅ (own org) | ❌ | ❌ |
| Confirm receipt | ✅ | ❌ | ✅ (own org) | ✅ (own org) |
| Cancel order | ✅ | ✅ (before shipped) | ✅ (before shipped) | ❌ |

## Next Steps

### Phase 1: Database & Backend (Priority: High)
1. Create migration to add `shipped_date` field
2. Update CustomerOrder model
3. Update schemas
4. Add `/ship` endpoint
5. Add `/confirm-receipt` endpoint
6. Update CRUD functions with proper permissions

### Phase 2: Frontend (Priority: High)
1. Add "Mark as Shipped" button for Oraseas EE
2. Add "Confirm Receipt" button for customers
3. Create ShipOrderForm component
4. Create ConfirmReceiptForm component
5. Update order card to show shipped_date
6. Update order timeline display

### Phase 3: Enhancements (Priority: Medium)
1. Add email notifications on status changes
2. Add tracking number field
3. Add order history/audit trail
4. Add automatic inventory updates on receipt
5. Add shipping carrier information
6. Add estimated delivery date calculation

### Phase 4: Analytics (Priority: Low)
1. Track average shipping times
2. Track delivery performance
3. Generate shipping reports
4. Customer satisfaction metrics

## Testing Checklist

- [ ] Customer can create order
- [ ] Oraseas EE sees order in their list
- [ ] Oraseas EE can approve order
- [ ] Oraseas EE can mark as shipped
- [ ] Customer sees shipped status
- [ ] Customer can confirm receipt
- [ ] Dates are recorded correctly
- [ ] Permissions are enforced
- [ ] Status transitions are valid
- [ ] Order history is complete
