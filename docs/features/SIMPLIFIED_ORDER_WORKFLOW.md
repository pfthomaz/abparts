# Simplified Customer Order Workflow

## Overview

The order workflow has been simplified to remove the "Approve" step. Orders now go directly from creation to shipping.

## Updated Workflow

### Step 1: Customer Creates Order
**Who:** Customer organization (any user)  
**Action:** Creates a customer order  
**Status:** `Requested`  
**UI:** "Add Customer Order" button

### Step 2: Receiver Ships Order
**Who:** Receiver organization (Oraseas EE, BossServe, BossAqua) - Admin only  
**Action:** Marks order as shipped and records shipping date  
**Status:** `Requested` → `Shipped`  
**Data Set:** `shipped_date`, optional tracking number  
**UI:** "Mark as Shipped" button (purple)  
**Permission:** User's organization must match `oraseas_organization_id`

### Step 3: Customer Confirms Receipt
**Who:** Customer organization (any user)  
**Action:** Confirms order received and records delivery date  
**Status:** `Shipped` → `Received`  
**Data Set:** `actual_delivery_date`, receiving warehouse  
**UI:** "Confirm Receipt" button (green)  
**Permission:** User's organization must match `customer_organization_id`

## Key Changes from Previous Version

### ❌ Removed
- "Approve" button
- "Pending" status step
- Approval workflow

### ✅ Simplified
- Direct path: `Requested` → `Shipped` → `Received`
- Receiver can ship immediately upon seeing the order
- No intermediate approval needed

## Use Cases

### Use Case 1: Customer Orders from Oraseas EE
1. **Customer** (e.g., BossServe Cyprus) creates order → Status: `Requested`
2. **Oraseas EE** sees order, ships it → Status: `Shipped` (with `shipped_date`)
3. **Customer** receives shipment, confirms → Status: `Received` (with `actual_delivery_date`)

### Use Case 2: Oraseas Orders from BossAqua
1. **Oraseas EE** creates order to BossAqua → Status: `Requested`
2. **BossAqua** sees order, ships it → Status: `Shipped` (with `shipped_date`)
3. **Oraseas EE** receives shipment, confirms → Status: `Received` (with `actual_delivery_date`)

### Use Case 3: Oraseas Orders from BossServe
1. **Oraseas EE** creates order to BossServe → Status: `Requested`
2. **BossServe** sees order, ships it → Status: `Shipped` (with `shipped_date`)
3. **Oraseas EE** receives shipment, confirms → Status: `Received` (with `actual_delivery_date`)

## Permission Matrix

| Action | Customer User | Customer Admin | Receiver Admin | Super Admin |
|--------|---------------|----------------|----------------|-------------|
| Create order | ✅ | ✅ | ✅ | ✅ |
| View order | ✅ (own org) | ✅ (own org) | ✅ (own org) | ✅ (all) |
| Ship order | ❌ | ❌ | ✅ (if receiver) | ✅ |
| Confirm receipt | ✅ (if customer) | ✅ (if customer) | ❌ | ✅ |

## Button Visibility Logic

### "Mark as Shipped" Button (Purple)
**Shows when:**
- User is admin or super_admin
- User's organization ID matches `oraseas_organization_id` (receiver)
- Order status is `Requested`

### "Confirm Receipt" Button (Green)
**Shows when:**
- User's organization ID matches `customer_organization_id` (customer)
- Order status is `Shipped`

## Status Flow

```
┌─────────────┐
│  Requested  │ ← Customer creates order
└──────┬──────┘
       │
       │ Receiver ships (sets shipped_date)
       ↓
┌─────────────┐
│   Shipped   │
└──────┬──────┘
       │
       │ Customer confirms (sets actual_delivery_date)
       ↓
┌─────────────┐
│  Received   │ ← Final state
└─────────────┘
```

## Files Changed

### Frontend
- `frontend/src/pages/Orders.js`
  - Removed `canApproveOrder()` function
  - Updated `canShipOrder()` to check `oraseas_organization_id` and work on `Requested` status
  - Updated `canConfirmReceipt()` to check `customer_organization_id`
  - Removed "Approve" button from UI

### Backend
- `backend/app/routers/customer_orders.py`
  - Updated permission check in `update_customer_order()` to allow both customer and receiver organizations

## Testing Checklist

- [ ] Customer can create order (status: Requested)
- [ ] Receiver sees order in their list
- [ ] Receiver can click "Mark as Shipped" on Requested orders
- [ ] Customer sees order status change to Shipped
- [ ] Customer can click "Confirm Receipt" on Shipped orders
- [ ] Order status changes to Received
- [ ] Dates are recorded correctly (shipped_date and actual_delivery_date)
- [ ] Permissions are enforced (only receiver can ship, only customer can confirm)

## Benefits of Simplified Workflow

1. **Faster Processing:** No approval bottleneck
2. **Clearer Roles:** Receiver ships, customer confirms
3. **Better Tracking:** Direct timestamps for shipping and receipt
4. **Flexible:** Works for any organization pair (Oraseas↔Customer, Oraseas↔BossAqua, etc.)
5. **Intuitive:** Matches real-world shipping process

## Next Steps

1. Test the workflow with real orders
2. Verify permissions work correctly
3. Consider adding email notifications for status changes
4. Add tracking number display in order details
