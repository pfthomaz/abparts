# Stock Adjustments - Manual Verification Steps

## Backend Verification

### 1. Check API is Running
Open in browser: http://localhost:8000/docs

You should see the FastAPI documentation with `/stock-adjustments` endpoints.

### 2. Test Authentication
In the API docs:
1. Click on `/token` endpoint
2. Click "Try it out"
3. Enter credentials (try these):
   - Username: `admin@oraseas.com`
   - Password: `admin123`
4. Click "Execute"
5. Copy the `access_token` from the response

### 3. Test List Endpoint
1. Click on `GET /stock-adjustments`
2. Click "Try it out"
3. Click "Authorize" button at top and paste your token
4. Click "Execute"
5. Should return an array of adjustments (may be empty)

### 4. Check Database
```bash
docker-compose exec db psql -U abparts_user -d abparts_dev -c "SELECT COUNT(*) FROM stock_adjustments;"
docker-compose exec db psql -U abparts_user -d abparts_dev -c "SELECT COUNT(*) FROM stock_adjustment_items;"
```

## Frontend Verification

### 1. Check Frontend is Running
Open in browser: http://localhost:3000

### 2. Login
Use admin credentials (same as above)

### 3. Find Stock Adjustments
Look for navigation menu:
- Should see "Inventory" dropdown in the top menu
- Click on it
- Should see "Stock Adjustments" option
- Click to navigate to the page

### 4. Test the Page
- Should see "Stock Adjustments" heading
- Should see "+ New Adjustment" button
- Should see filters (Warehouse, Type, Date range)
- Should see a table or "No stock adjustments found" message

### 5. Create Test Adjustment
1. Click "+ New Adjustment"
2. Modal should open
3. Select a warehouse
4. Select adjustment type (e.g., "Stock Take")
5. Search and add a part
6. Set quantity (e.g., 100)
7. Click "Create Adjustment"
8. Should see success and adjustment appears in list

## Troubleshooting

### If navigation item doesn't appear:
- Check user role (must be admin or super_admin)
- Check browser console for errors
- Verify permissions in user profile

### If API returns 401 Unauthorized:
- Token may have expired
- Re-authenticate and get new token

### If API returns 403 Forbidden:
- User doesn't have ADJUST_INVENTORY permission
- Check user role in database

### If parts don't load in modal:
- Check parts exist in database
- Check API endpoint: http://localhost:8000/docs#/Parts/list_parts_parts_get

### If warehouses don't load:
- Check warehouses exist in database
- Check API endpoint: http://localhost:8000/docs#/Warehouses/list_warehouses_warehouses_get

## Database Queries for Debugging

```sql
-- Check if tables exist
SELECT table_name FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_name LIKE 'stock_adjustment%';

-- Check stock adjustments
SELECT id, warehouse_id, adjustment_type, adjustment_date, total_items_adjusted 
FROM stock_adjustments 
ORDER BY created_at DESC 
LIMIT 5;

-- Check stock adjustment items
SELECT sa.adjustment_type, sai.part_id, sai.quantity_before, sai.quantity_after, sai.quantity_change
FROM stock_adjustment_items sai
JOIN stock_adjustments sa ON sai.stock_adjustment_id = sa.id
ORDER BY sai.created_at DESC
LIMIT 10;

-- Check user permissions
SELECT email, role, organization_id 
FROM users 
WHERE role IN ('admin', 'super_admin');
```

## Expected Behavior

### Creating an Adjustment:
1. User selects warehouse and type
2. User adds one or more parts
3. User sets new quantity for each part
4. System calculates quantity change
5. System updates inventory
6. System creates transaction records
7. Adjustment appears in list

### Viewing Details:
1. Click "View Details" on any adjustment
2. Modal shows:
   - Warehouse, type, date, user
   - Reason and notes (if provided)
   - Table of items with before/after quantities
   - Color-coded changes (green=increase, red=decrease)

## Success Criteria

✅ Backend API endpoints respond correctly
✅ Frontend page loads without errors
✅ Navigation item appears for admin users
✅ Can create new adjustments
✅ Can view adjustment details
✅ Inventory quantities update correctly
✅ Transaction records created
