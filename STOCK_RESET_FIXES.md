# Stock Reset and Inventory Display Fixes

## Issues Fixed

### 1. Stock Doubling Bug in Stock Reset
**Problem:** When adding a new part to stock reset, the system was doubling the quantity because it was fetching inventory from the wrong endpoint, getting data from ALL warehouses instead of just the specific warehouse.

**Root Cause:** 
1. The `handleAddPart` function was using `/inventory/?warehouse_id=${warehouse.id}` which doesn't actually filter by warehouse
2. The general `/inventory/` endpoint doesn't accept warehouse_id as a query parameter
3. This caused it to fetch inventory from ALL warehouses in the organization, potentially getting the wrong quantity

**Solution:** 
1. Changed to use the correct warehouse-specific endpoint: `/inventory/warehouse/${warehouse.id}`
2. Updated both the initial data fetch and the `handleAddPart` function to use this endpoint
3. Added `limit=1000` to ensure all inventory items are fetched

**Files Changed:**
- `frontend/src/components/StockResetTab.js`

**Code Changes:**
```javascript
// WRONG: Using general inventory endpoint (doesn't filter by warehouse!)
const inventoryResponse = await api.get(`/inventory/?warehouse_id=${warehouse.id}`);
// ❌ This returns ALL inventory from ALL warehouses in the organization

// CORRECT: Using warehouse-specific endpoint
const inventoryResponse = await api.get(`/inventory/warehouse/${warehouse.id}?limit=1000`);
// ✅ This returns ONLY inventory from the specified warehouse

// Then find the specific part
const partInventory = inventory.find(item => item.part_id === partId);
const currentStock = partInventory ? parseFloat(partInventory.current_stock || 0) : 0;
```

**Key Insight:** The `/inventory/` endpoint doesn't support query parameters for filtering. Always use `/inventory/warehouse/{warehouse_id}` for warehouse-specific inventory.

### 2. Inventory Tab Not Refreshing After Stock Reset
**Problem:** After applying a stock reset, the "Current Inventory" tab didn't show the updated inventory or newly added parts.

**Root Cause:** The refresh mechanism wasn't properly triggering a re-fetch of inventory data when switching back to the inventory tab.

**Solution:** 
1. Added a `refreshTrigger` state to force re-render of the inventory component
2. Stored the inventory refresh function in a ref for direct access
3. Called the refresh function and incremented the trigger when stock reset succeeds

**Files Changed:**
- `frontend/src/components/WarehouseDetailedView.js`

**Code Changes:**
```javascript
// Added state and ref for refresh management
const [refreshTrigger, setRefreshTrigger] = useState(0);
const inventoryRefreshFnRef = React.useRef(null);

// Store refresh function in ref
const handleRefreshCallback = useCallback((refreshFn) => {
  inventoryRefreshFnRef.current = refreshFn;
  // ...
}, [onInventoryRefresh]);

// Trigger refresh on stock reset success
onSuccess={() => {
  if (inventoryRefreshFnRef.current) {
    inventoryRefreshFnRef.current();  // Call refresh
  }
  setRefreshTrigger(prev => prev + 1);  // Force re-render
  setActiveTab('inventory');
}}

// Add key to force component remount
<WarehouseInventoryView
  key={`inventory-${refreshTrigger}`}
  // ...
/>
```

### 3. Inventory Tab Limited to 100 Items
**Problem:** The "Current Inventory" tab was only showing 100 inventory items even if the warehouse had more parts.

**Root Cause:** The `getWarehouseInventory` function wasn't passing a `limit` parameter, so the backend used its default limit of 100.

**Solution:** Added `limit=1000` parameter to the inventory API call to fetch up to 1000 items (the backend's maximum).

**Files Changed:**
- `frontend/src/services/inventoryService.js`

**Code Change:**
```javascript
const getWarehouseInventory = (warehouseId, filters = {}) => {
  const queryParams = new URLSearchParams();
  queryParams.append('_t', Date.now().toString());
  queryParams.append('limit', '1000');  // ✅ Fetch up to 1000 items
  // ...
};
```

## Testing Checklist

- [x] Add a part with existing stock to stock reset - verify current quantity shows correctly
- [x] Apply stock reset with new parts - verify inventory tab updates immediately
- [x] Check inventory tab shows all parts (not limited to 100)
- [x] Verify stock quantities are correct after reset (no doubling)
- [x] Test with parts that have 0 stock initially
- [x] Test with parts that have existing stock

## Related Files

### Frontend
- `frontend/src/components/StockResetTab.js` - Stock reset UI and logic
- `frontend/src/components/WarehouseDetailedView.js` - Tab management and refresh coordination
- `frontend/src/components/WarehouseInventoryView.js` - Inventory display
- `frontend/src/services/inventoryService.js` - Inventory API calls

### Backend
- `backend/app/routers/warehouses.py` - Stock reset endpoint
- `backend/app/routers/inventory.py` - Inventory endpoints

## Notes

- The backend maximum limit for inventory items is 1000 per request
- If a warehouse has more than 1000 inventory items in the future, consider implementing pagination
- The stock reset feature creates adjustment transactions for audit trail
- All changes are logged with reason and notes for compliance
