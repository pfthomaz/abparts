# Order Edit & Delete - Bug Fixes

## Issues Fixed

### 1. Syntax Error in Backend
**Problem:** `@router.delete` decorator was split across two lines causing Python syntax error.

**Fix:** Combined decorator onto single line in `backend/app/routers/customer_orders.py`

### 2. Edit Button Error - "Cannot read properties of undefined (reading 'name')"
**Problem:** When editing an order, the form tried to access `item.part.name` but the API returns items with a different structure than what the form expects.

**Root Cause:** 
- Form expects: `item.part.name`, `item.part.part_number`, etc.
- API returns: `item.part_name`, `item.part_number`, etc. (flat structure)

**Fix:** Added item normalization in both `CustomerOrderForm.js` and `SupplierOrderForm.js`:
- When `initialData` contains items, normalize them to match the form's expected structure
- Map API response fields to nested `part` object
- Provide fallback values for missing fields

### 3. Delete Button Not Showing
**Status:** Need to verify user role in browser console

**Possible Causes:**
1. User role might not be 'admin' or 'super_admin'
2. Order status might not be 'Requested' or 'Pending'

**To Debug:**
```javascript
// In browser console on Orders page:
console.log('User:', user);
console.log('User role:', user?.role);
console.log('Order status:', order.status);
```

## Files Modified

### Backend
- `backend/app/routers/customer_orders.py` - Fixed decorator syntax

### Frontend
- `frontend/src/components/CustomerOrderForm.js` - Added item normalization for edit mode
- `frontend/src/components/SupplierOrderForm.js` - Added item normalization for edit mode

## Testing

### Edit Functionality
- [x] Fixed syntax error
- [x] Fixed item.part.name error
- [ ] Test editing customer order
- [ ] Test editing supplier order
- [ ] Verify items display correctly in edit mode
- [ ] Verify form submission works

### Delete Functionality
- [ ] Verify delete button shows for admin users
- [ ] Verify delete button only shows for Requested/Pending orders
- [ ] Test delete confirmation modal
- [ ] Test successful deletion
- [ ] Verify order list refreshes after delete

## Next Steps

1. Test edit functionality with actual order data
2. Debug why delete button isn't showing (check user role)
3. Verify all permissions work correctly
4. Test with different order statuses
