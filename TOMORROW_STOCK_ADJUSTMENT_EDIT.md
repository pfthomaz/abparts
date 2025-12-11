# Stock Adjustment Edit Feature - Implementation Plan

## Current Status
✅ Backend update endpoint exists (`PUT /stock-adjustments/{id}`)
✅ Frontend service method exists (`stockAdjustmentsService.update()`)
✅ Delete functionality working
✅ Edit button visible in UI (shows alert placeholder)

## What Needs to Be Done

### Option 1: Reuse CreateStockAdjustmentModal (Recommended)
Modify the existing create modal to support edit mode.

**Pros:**
- Less code duplication
- Consistent UI/UX
- Easier to maintain

**Implementation:**
1. Add `editMode` and `initialData` props to CreateStockAdjustmentModal
2. Pre-fill form fields when in edit mode
3. Change title and button text based on mode
4. Call update service instead of create when editing

### Option 2: Create Separate EditStockAdjustmentModal
Create a new modal specifically for editing.

**Pros:**
- Cleaner separation of concerns
- No risk of breaking create functionality

**Cons:**
- Code duplication
- More maintenance

## Recommended Implementation (Option 1)

### Step 1: Update CreateStockAdjustmentModal Component

```javascript
// Add new props
const CreateStockAdjustmentModal = ({ 
  isOpen, 
  onClose, 
  onSubmit, 
  warehouses,
  editMode = false,           // NEW
  initialData = null          // NEW
}) => {

  // Initialize form with initial data if editing
  useEffect(() => {
    if (editMode && initialData) {
      setFormData({
        warehouse_id: initialData.warehouse_id,
        adjustment_type: initialData.adjustment_type,
        adjustment_date: initialData.adjustment_date.split('T')[0],
        reason: initialData.reason || '',
        notes: initialData.notes || '',
        reference_number: initialData.reference_number || '',
        items: initialData.items.map(item => ({
          part_id: item.part_id,
          quantity_before: item.quantity_before,
          quantity_after: item.quantity_after,
          notes: item.notes || ''
        }))
      });
    }
  }, [editMode, initialData]);

  // Update modal title
  const title = editMode ? 'Edit Stock Adjustment' : 'Create Stock Adjustment';
  
  // Update button text
  const submitButtonText = editMode ? 'Update Adjustment' : 'Create Adjustment';
```

### Step 2: Update StockAdjustments Page

```javascript
// Add state for editing
const [editingAdjustment, setEditingAdjustment] = useState(null);

// Update handleEdit
const handleEdit = async (adjustment) => {
  try {
    // Fetch full details
    const details = await stockAdjustmentsService.getById(adjustment.id);
    setEditingAdjustment(details);
  } catch (err) {
    alert('Failed to load adjustment details: ' + err.message);
  }
};

// Update handleCreateAdjustment to handle both create and edit
const handleSaveAdjustment = async (adjustmentData) => {
  try {
    if (editingAdjustment) {
      // Update existing
      await stockAdjustmentsService.update(editingAdjustment.id, adjustmentData);
      setEditingAdjustment(null);
    } else {
      // Create new
      await stockAdjustmentsService.create(adjustmentData);
      setShowCreateModal(false);
    }
    loadData();
  } catch (err) {
    throw err;
  }
};

// Render modal for both create and edit
{(showCreateModal || editingAdjustment) && (
  <CreateStockAdjustmentModal
    isOpen={true}
    onClose={() => {
      setShowCreateModal(false);
      setEditingAdjustment(null);
    }}
    onSubmit={handleSaveAdjustment}
    warehouses={warehouses}
    editMode={!!editingAdjustment}
    initialData={editingAdjustment}
  />
)}
```

### Step 3: Handle Edge Cases

1. **Validation**: Ensure edited data is valid
2. **Loading state**: Show loading while fetching adjustment details
3. **Error handling**: Clear error messages
4. **Permissions**: Backend already checks admin permissions
5. **Inventory impact**: Backend handles recalculation automatically

## Files to Modify

1. `frontend/src/components/CreateStockAdjustmentModal.js` - Add edit mode support
2. `frontend/src/pages/StockAdjustments.js` - Update handlers and modal rendering

## Testing Checklist

- [ ] Edit button loads adjustment details
- [ ] Modal opens with pre-filled data
- [ ] All fields are editable
- [ ] Items list is editable (add/remove/modify)
- [ ] Update saves successfully
- [ ] Inventory recalculates correctly
- [ ] Page refreshes with updated data
- [ ] Error handling works
- [ ] Cancel closes modal without saving
- [ ] Non-admins cannot edit (backend check)

## Estimated Time
30-45 minutes to implement and test

## Alternative Quick Solution
If you want something simpler for now, keep the current alert and add a note:
"Full edit functionality coming soon. For now, delete and recreate the adjustment."

This is acceptable for MVP and can be enhanced later.
