# Part Usage Recorder - Issues & Fixes

## Issues Identified

### Issue #1: Parts dropdown showing only 1 of 2 parts
**Problem:** When fetching warehouse inventory, the code uses `getInventory()` with filters instead of the dedicated `getWarehouseInventory()` method.

**Current Code (Line 115):**
```javascript
const inventory = await inventoryService.getInventory({
  warehouse_id: formData.from_warehouse_id
});
```

**Issue:** The `/inventory?warehouse_id=xxx` endpoint doesn't exist. Should use `/inventory/warehouse/{id}`.

**Fix:** Use the correct method:
```javascript
const inventory = await inventoryService.getWarehouseInventory(formData.from_warehouse_id);
```

---

### Issue #2: Machine dropdown allows selecting any machine
**Problem:** When opened from Machines page with `initialMachineId`, the machine dropdown should be:
- Pre-selected with that machine
- Disabled (not changeable)

**Current Behavior:** Machine dropdown is enabled and shows all machines.

**Fix:** 
1. Disable machine dropdown when `initialMachineId` is provided
2. Add visual indicator that machine is pre-selected

---

### Issue #3: Superadmin sees all parts instead of warehouse-specific
**Problem:** Same as Issue #1 - using wrong endpoint.

**Additional Issue:** When no warehouse is selected, it might be fetching all parts globally.

**Fix:** Ensure parts are ONLY shown after warehouse selection, and only parts in that warehouse.

---

## Implementation

### Fix #1: Use correct inventory endpoint
**File:** `frontend/src/components/PartUsageRecorder.js`
**Line:** ~115

Change:
```javascript
const inventory = await inventoryService.getInventory({
  warehouse_id: formData.from_warehouse_id
});
```

To:
```javascript
const inventory = await inventoryService.getWarehouseInventory(
  formData.from_warehouse_id
);
```

### Fix #2: Disable machine selection when pre-selected
**File:** `frontend/src/components/PartUsageRecorder.js`
**Line:** ~420 (machine select element)

Change:
```javascript
<select
  id="machine_id"
  name="machine_id"
  value={formData.machine_id}
  onChange={handleChange}
  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
  disabled={loading || !formData.part_id}
  required
>
```

To:
```javascript
<select
  id="machine_id"
  name="machine_id"
  value={formData.machine_id}
  onChange={handleChange}
  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
  disabled={loading || !formData.part_id || initialMachineId}
  required
>
```

Add helper text after the select:
```javascript
{initialMachineId && (
  <p className="text-xs text-blue-600 mt-1">
    Machine pre-selected from Machines page
  </p>
)}
```

### Fix #3: Better inventory response handling
**File:** `frontend/src/components/PartUsageRecorder.js`
**Line:** ~120-135

The response handling looks correct, but let's add better logging:
```javascript
console.log('Fetching inventory for warehouse:', formData.from_warehouse_id);
const inventory = await inventoryService.getWarehouseInventory(
  formData.from_warehouse_id
);

console.log('Raw inventory response:', inventory);
console.log('Response type:', typeof inventory);
console.log('Is array?', Array.isArray(inventory));
```

---

## Testing Checklist

After fixes:

### From Machines Page (with initialMachineId)
- [ ] Click "Use Part" on a machine
- [ ] Warehouse dropdown shows correct warehouse
- [ ] Parts dropdown shows ONLY parts in that warehouse with stock > 0
- [ ] Machine dropdown is pre-selected and DISABLED
- [ ] Can record usage successfully

### From Transactions Page (no initialMachineId)
- [ ] Click "Record Usage"
- [ ] Select warehouse first
- [ ] Parts dropdown shows ONLY parts in selected warehouse
- [ ] Machine dropdown shows all machines in organization
- [ ] Can select any machine
- [ ] Can record usage successfully

### As Superadmin
- [ ] Can see all warehouses
- [ ] Parts filtered by selected warehouse (not all parts)
- [ ] Can see all machines
- [ ] Organizational boundary validation works

---

## Root Cause

The main issue is using the wrong API endpoint:
- ❌ `GET /inventory?warehouse_id=xxx` - Doesn't filter properly
- ✅ `GET /inventory/warehouse/{warehouse_id}` - Returns warehouse-specific inventory

The backend has the correct endpoint, but the frontend wasn't using it.
