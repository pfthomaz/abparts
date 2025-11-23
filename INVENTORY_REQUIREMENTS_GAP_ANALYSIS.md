# Inventory Requirements - Gap Analysis

## Requirements vs Implementation

### ✅ ALREADY IMPLEMENTED

#### 1. Multiple Warehouses per Organization
**Status:** ✅ WORKING
- Organizations can have unlimited warehouses
- Unique constraint: `(organization_id, name)`
- Active/inactive status supported
- Location and description fields available

#### 2. Inventory Increases
**Status:** ✅ PARTIALLY WORKING

**From Supplier Orders:**
- ✅ Supplier order system exists
- ✅ Orders can be marked as "Delivered"
- ⚠️ **MISSING:** Automatic inventory creation when order delivered
- **Current:** Manual process required

**From Warehouse Transfers:**
- ✅ Transfer endpoint exists: `POST /inventory/transfer`
- ✅ Automatic stock updates via database triggers
- ✅ Validates sufficient stock
- ✅ Creates transaction audit trail
- ✅ Works perfectly

#### 3. Inventory Decreases
**Status:** ✅ WORKING

**Part Usage in Machines:**
- ✅ Part usage recording exists
- ✅ Creates CONSUMPTION transaction
- ✅ Decreases warehouse stock automatically
- ✅ Links to specific machine
- ✅ Records user who performed action

**Warehouse Transfers:**
- ✅ Decreases source warehouse automatically
- ✅ Works perfectly

#### 4. Stock Adjustments
**Status:** ✅ WORKING
- ✅ Stock adjustment model exists
- ✅ Reason codes defined (STOCKTAKE_DISCREPANCY, etc.)
- ✅ Supports positive/negative adjustments
- ✅ Records user and notes
- ⚠️ **UI MAY NEED IMPROVEMENT** for bulk operations

---

## ❌ CRITICAL ISSUES TO FIX

### Issue #1: Decimal Precision for Consumables
**Problem:** ALL parts currently support 3 decimal places
**Required:** 
- CONSUMABLE parts → Integer only (no decimals)
- BULK_MATERIAL parts → Decimals allowed (e.g., 10.5 liters)

**Impact Areas:**

#### Database Schema
```sql
-- Current (WRONG for consumables)
current_stock DECIMAL(10, 3)  -- Allows 1234567.123

-- Should validate based on part_type
```

#### Backend Models
**File:** `backend/app/models.py`
- `Inventory.current_stock` - DECIMAL(10, 3)
- `Transaction.quantity` - DECIMAL(10, 3)
- `PartUsage.quantity` - DECIMAL(10, 3)
- `StockAdjustment.quantity_adjusted` - DECIMAL(10, 3)
- `SupplierOrderItem.quantity` - DECIMAL(10, 3)
- `CustomerOrderItem.quantity` - DECIMAL(10, 3)

**Fix Required:** Add validation logic, not schema change

#### Backend Validation
**Files to Update:**
- `backend/app/schemas.py` - Add validators
- `backend/app/crud/inventory.py` - Validate on create/update
- `backend/app/routers/inventory.py` - Validate transfers
- `backend/app/routers/part_usage.py` - Validate consumption
- `backend/app/routers/stock_adjustments.py` - Validate adjustments

#### Frontend Components
**Files to Update:**
- `frontend/src/components/PartUsageRecorder.js` - Integer input for consumables
- `frontend/src/components/StockAdjustmentForm.js` - Integer input for consumables
- `frontend/src/pages/Orders.js` - Order quantity inputs
- Any inventory transfer forms
- Initial stock entry forms

**HTML Input Changes:**
```javascript
// Current (WRONG for consumables)
<input type="number" step="0.001" />

// Should be (for consumables)
<input type="number" step="1" min="0" />

// For bulk materials
<input type="number" step="0.1" min="0" />
```

---

## ⚠️ MISSING FEATURES

### Feature #1: Initial Inventory Entry (Bulk)
**Status:** ❌ NOT IMPLEMENTED
**Priority:** HIGH

**Requirement:**
- Set initial stock for ALL parts in a warehouse
- Must be practical for many parts (100+ parts)
- One-time operation per warehouse

**Suggested Implementation:**
1. **Spreadsheet-like UI** with all parts listed
2. Input fields for each part's initial quantity
3. Save all at once (batch operation)
4. Creates INITIAL_STOCK_ENTRY adjustments

**UI Mockup:**
```
Initial Inventory Entry - [Warehouse Name]
┌─────────────────────────────────────────────────────────┐
│ Part Number │ Part Name        │ Type       │ Quantity │
├─────────────────────────────────────────────────────────┤
│ AB-001      │ Filter Cartridge │ Consumable │ [  50  ] │
│ AB-002      │ O-Ring Set       │ Consumable │ [ 100  ] │
│ AB-003      │ Hydraulic Oil    │ Bulk       │ [ 25.5 ] │
│ AB-004      │ Cleaning Agent   │ Bulk       │ [ 10.0 ] │
│ ...         │ ...              │ ...        │ [      ] │
└─────────────────────────────────────────────────────────┘
[Cancel] [Save All]
```

**Backend Endpoint Needed:**
```
POST /inventory/bulk-initialize
{
  "warehouse_id": "uuid",
  "items": [
    {"part_id": "uuid", "quantity": 50},
    {"part_id": "uuid", "quantity": 100},
    ...
  ]
}
```

### Feature #2: Physical Count / Stocktake UI
**Status:** ❌ PARTIALLY IMPLEMENTED
**Priority:** HIGH

**Current State:**
- ✅ Backend: Stocktake worksheet endpoint exists
- ✅ Backend: Stock adjustment model exists
- ❌ Frontend: No practical UI for bulk adjustments

**Requirement:**
- Generate worksheet with current system quantities
- Allow entering physical count for each part
- Calculate discrepancies automatically
- Create adjustments in batch

**Suggested Implementation:**
```
Physical Stocktake - [Warehouse Name]
┌──────────────────────────────────────────────────────────────────┐
│ Part      │ Part Name    │ System │ Physical │ Diff │ Reason    │
├──────────────────────────────────────────────────────────────────┤
│ AB-001    │ Filter       │   50   │ [  48  ] │  -2  │ [Damaged] │
│ AB-002    │ O-Ring       │  100   │ [ 105  ] │  +5  │ [Found]   │
│ AB-003    │ Oil (L)      │  25.5  │ [ 24.0 ] │ -1.5 │ [Used]    │
└──────────────────────────────────────────────────────────────────┘
[Export to Excel] [Import from Excel] [Save Adjustments]
```

**Backend Endpoint Needed:**
```
POST /inventory/bulk-adjust
{
  "warehouse_id": "uuid",
  "adjustments": [
    {
      "inventory_id": "uuid",
      "physical_count": 48,
      "reason_code": "DAMAGED_GOODS",
      "notes": "2 filters damaged during storage"
    },
    ...
  ]
}
```

### Feature #3: Automatic Inventory from Supplier Orders
**Status:** ❌ NOT IMPLEMENTED
**Priority:** MEDIUM

**Current State:**
- Supplier orders can be created
- Orders can be marked as "Delivered"
- **BUT:** No automatic inventory creation

**Required:**
When supplier order status changes to "Delivered":
1. For each order item (part + quantity)
2. Find or create inventory record in receiving warehouse
3. Create CREATION transaction
4. Increase stock automatically

**Implementation:**
- Add `receiving_warehouse_id` to `SupplierOrder` model
- Add endpoint: `POST /supplier-orders/{id}/receive`
- Automatically create transactions and update inventory

---

## 📋 IMPLEMENTATION PLAN

### Phase 1: Fix Decimal Precision (CRITICAL)
**Priority:** URGENT - This is a data integrity issue

1. **Backend Validation**
   - Add Pydantic validators to check part_type
   - Reject decimals for CONSUMABLE parts
   - Allow decimals for BULK_MATERIAL parts

2. **Frontend Input Controls**
   - Fetch part details before showing quantity input
   - Set `step="1"` for consumables
   - Set `step="0.1"` for bulk materials
   - Add visual indicator of part type

3. **Data Cleanup**
   - Audit existing data for consumables with decimals
   - Round to nearest integer if found
   - Log discrepancies

**Files to Modify:**
```
Backend:
- backend/app/schemas.py (add validators)
- backend/app/crud/inventory.py (validate quantities)
- backend/app/routers/inventory.py (validate transfers)
- backend/app/routers/part_usage.py (validate usage)
- backend/app/routers/stock_adjustments.py (validate adjustments)

Frontend:
- frontend/src/components/PartUsageRecorder.js
- frontend/src/components/StockAdjustmentForm.js (if exists)
- frontend/src/pages/Orders.js
- Create: frontend/src/utils/partQuantityValidation.js
```

### Phase 2: Initial Inventory Entry UI
**Priority:** HIGH - Needed for onboarding

1. Create bulk entry component
2. Spreadsheet-like interface
3. Batch save endpoint
4. Validation and error handling

**New Files:**
```
Frontend:
- frontend/src/components/InitialInventoryEntry.js
- frontend/src/pages/WarehouseSetup.js

Backend:
- backend/app/routers/inventory.py (add bulk-initialize endpoint)
```

### Phase 3: Physical Stocktake UI
**Priority:** HIGH - Needed for operations

1. Generate worksheet from existing endpoint
2. Bulk adjustment interface
3. Excel import/export
4. Batch adjustment endpoint

**New Files:**
```
Frontend:
- frontend/src/components/PhysicalStocktake.js
- frontend/src/pages/Stocktake.js

Backend:
- backend/app/routers/inventory.py (add bulk-adjust endpoint)
```

### Phase 4: Supplier Order → Inventory
**Priority:** MEDIUM - Nice to have

1. Add receiving warehouse to orders
2. Create receive endpoint
3. Automatic transaction creation
4. UI for receiving process

---

## 🎯 IMMEDIATE ACTION ITEMS

### Tomorrow's Work Priority:

1. **FIX DECIMAL PRECISION** (2-3 hours)
   - Most critical issue
   - Affects data integrity
   - Relatively quick fix

2. **CREATE INITIAL INVENTORY UI** (3-4 hours)
   - High business value
   - Needed for new warehouse setup
   - Moderate complexity

3. **IMPROVE STOCKTAKE WORKFLOW** (2-3 hours)
   - High operational value
   - Backend mostly ready
   - Focus on UI/UX

**Total Estimated Time:** 7-10 hours

---

## Summary

### What Works Now ✅
- Multiple warehouses per organization
- Warehouse-to-warehouse transfers
- Part usage (consumption) tracking
- Stock adjustment infrastructure
- Transaction audit trail

### Critical Issues ❌
- Decimal precision for consumables (MUST FIX)
- No bulk initial inventory entry
- No practical stocktake UI

### Missing Features ⚠️
- Automatic inventory from supplier orders
- Batch operations for efficiency
- Excel import/export for stocktakes

The foundation is solid, but the **decimal precision issue is critical** and should be fixed first. Then focus on the bulk entry UIs which are essential for practical operations.
