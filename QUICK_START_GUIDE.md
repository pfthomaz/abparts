# Customer Order Workflow - Quick Start Guide

## For Oraseas EE Users

### Viewing Customer Orders
1. Login to ABParts
2. Go to **Orders** page
3. Scroll to **"Customer Orders (Received)"** section
4. You'll see orders placed TO your organization by customers

### Shipping an Order
1. Find an order with status **"Pending"**
2. Click the **"Mark as Shipped"** button (purple)
3. Fill in the form:
   - **Shipped Date:** When you shipped it (defaults to today)
   - **Tracking Number:** Optional tracking number
   - **Notes:** Any shipping notes
4. Click **"Mark as Shipped"**
5. Order status changes to **"Shipped"**

## For Customer Users

### Viewing Your Orders
1. Login to ABParts
2. Go to **Orders** page
3. Scroll to **"Customer Orders (Placed)"** section
4. You'll see orders you placed TO Oraseas EE

### Confirming Receipt
1. Find an order with status **"Shipped"**
2. Click the **"Confirm Receipt"** button (green)
3. Fill in the form:
   - **Delivery Date:** When you received it (defaults to today)
   - **Receiving Warehouse:** Select your warehouse
   - **Notes:** Any delivery notes
4. Click **"Confirm Receipt"**
5. Order status changes to **"Received"**

## Order Status Flow

```
Requested → Pending → Shipped → Received
   ↓          ↓         ↓          ↓
Customer   Oraseas   Oraseas   Customer
 places     EE        EE       confirms
 order    approves   ships    receipt
```

## Button Colors

- 🔵 **Blue "Approve"** - Oraseas EE approves order
- 🟣 **Purple "Mark as Shipped"** - Oraseas EE ships order
- 🟢 **Green "Confirm Receipt"** - Customer confirms delivery

## Dates Explained

- **Order Date:** When customer placed the order
- **Expected Delivery:** Estimated delivery date
- **Shipped Date:** When Oraseas EE shipped it ✨ NEW
- **Received Date:** When customer received it ✨ NEW

## Troubleshooting

**Q: I don't see the "Mark as Shipped" button**
- Make sure you're logged in as Oraseas EE admin
- Order must be in "Pending" status
- You need admin or super_admin role

**Q: I don't see the "Confirm Receipt" button**
- Make sure you're logged in as the customer who placed the order
- Order must be in "Shipped" status
- Any user in your organization can confirm receipt

**Q: I don't see any warehouses in the dropdown**
- Your organization needs at least one warehouse
- Contact your admin to create a warehouse
- Go to Warehouses page → Add Warehouse

**Q: The button is grayed out**
- Check the order status - buttons only appear for specific statuses
- Check your permissions - you may not have the right role
- Refresh the page to see latest status

## Tips

✅ **DO:**
- Ship orders promptly after approval
- Include tracking numbers when available
- Add notes about any special handling
- Confirm receipt as soon as you receive the shipment
- Select the correct warehouse for inventory tracking

❌ **DON'T:**
- Don't mark as shipped before actually shipping
- Don't confirm receipt before actually receiving
- Don't skip the warehouse selection
- Don't forget to add notes if there are issues

## Need Help?

Contact your system administrator or refer to:
- `CUSTOMER_ORDER_WORKFLOW_ANALYSIS.md` - Detailed analysis
- `CUSTOMER_ORDER_WORKFLOW_IMPLEMENTATION.md` - Technical details
- `IMPLEMENTATION_COMPLETE.md` - Complete implementation summary
