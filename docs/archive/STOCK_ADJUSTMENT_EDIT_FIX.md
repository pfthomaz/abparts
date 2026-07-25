# Stock Adjustment Edit Fix - Complete

## Issues Fixed

### 1. 500 Error When Editing Stock Adjustments
**Problem:** Backend was trying to access `adjustment_date` field that doesn't exist in `StockAdjustmentCreate` schema.

**Solution:**
- Removed `adjustment_date` assignment from update endpoint (it's auto-generated)
- Added `quantity_before` as optional field to `StockAdjustmentItemCreate` schema
- Updated backend to use provided `quantity_before` or calculate it if not provided
- Updated frontend to send `quantity_before` when in edit mode
- Fixed `quantity_change` calculation in update endpoint

### 2. Integer Display for Consumables
**Problem:** All quantity inputs showed decimals (step="0.01") even for consumable parts that should use integers.

**Solution:**
- Added `unit_of_measure` to item data structure in CreateStockAdjustmentModal
- Updated quantity input to use `step="1"` for consumables (unit_of_measure === 'units')
- Updated quantity input to use `step="0.01"` for liquids
- Backend now returns `unit_of_measure` in stock adjustment item details

## Files Modified

### Backend
1. **backend/app/schemas.py**
   - Added `quantity_before` as optional field to `StockAdjustmentItemCreate`

2. **backend/app/routers/stock_adjustments.py**
   - Removed invalid `adjustment_date` assignment
   - Added `quantity_change` calculation
   - Added logic to use provided `quantity_before` or calculate it
   - Fixed `reason` field mapping for items

3. **backend/app/crud/stock_adjustments.py**
   - Added `unit_of_measure` to item response in `get_stock_adjustment_by_id`

### Frontend
1. **frontend/src/components/CreateStockAdjustmentModal.js**
   - Added `unit_of_measure` to item data structure
   - Updated quantity input step based on unit_of_measure
   - Updated submit to send `quantity_before` in edit mode
   - Fixed reason field mapping

## Additional Fixes

### 3. Integer Display Formatting
**Problem:** Even with step="1", consumables were displaying with thousand separators (e.g., "1,000") making them look like decimals.

**Solution:**
- Updated `formatNumber` utility to accept `unitOfMeasure` parameter
- For consumables (units), format as integers with no decimal places
- For liquids, format with up to 2 decimal places
- Updated all quantity displays to pass unit_of_measure to formatNumber
- Added integer enforcement in onChange handler for consumable inputs

## Testing Checklist
- [x] Edit existing stock adjustment without 500 error
- [x] Verify consumables show integer inputs (step="1")
- [x] Verify liquids show decimal inputs (step="0.01")
- [x] Verify consumables display without decimal places (e.g., "1,000" not "1,000.00")
- [x] Verify quantity changes are calculated correctly
- [x] Verify item reasons are preserved on edit

## Notes
- The fix ensures consumables use integer inputs AND display as integers throughout the application
- Edit mode now properly sends quantity_before to maintain accurate change tracking
- Backend gracefully handles both create (calculates quantity_before) and update (uses provided quantity_before)
- formatNumber utility now intelligently formats based on unit_of_measure
