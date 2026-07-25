# Stock Adjustments Edit/Delete Feature

## Backend Endpoints Needed

Add these endpoints to `backend/app/routers/stock_adjustments.py`:

### Delete Endpoint
```python
@router.delete("/{adjustment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_stock_adjustment(
    adjustment_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)
):
    """Delete a stock adjustment. Only admins can delete."""
    from ..permissions import permission_checker
    
    if not permission_checker.is_admin(current_user):
        raise HTTPException(status_code=403, detail="Only admins can delete stock adjustments")
    
    adjustment = db.query(models.StockAdjustment).filter(
        models.StockAdjustment.id == adjustment_id
    ).first()
    
    if not adjustment:
        raise HTTPException(status_code=404, detail="Stock adjustment not found")
    
    if not permission_checker.is_super_admin(current_user):
        if adjustment.warehouse.organization_id != current_user.organization_id:
            raise HTTPException(status_code=403, detail="Not authorized")
    
    db.delete(adjustment)
    db.commit()
    return None
```

### Update Endpoint
```python
@router.put("/{adjustment_id}", response_model=schemas.StockAdjustmentResponse)
async def update_stock_adjustment(
    adjustment_id: uuid.UUID,
    adjustment_update: schemas.StockAdjustmentCreate,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)
):
    """Update a stock adjustment. Only admins can update."""
    from ..permissions import permission_checker
    
    if not permission_checker.is_admin(current_user):
        raise HTTPException(status_code=403, detail="Only admins can update stock adjustments")
    
    adjustment = db.query(models.StockAdjustment).filter(
        models.StockAdjustment.id == adjustment_id
    ).first()
    
    if not adjustment:
        raise HTTPException(status_code=404, detail="Stock adjustment not found")
    
    if not permission_checker.is_super_admin(current_user):
        if adjustment.warehouse.organization_id != current_user.organization_id:
            raise HTTPException(status_code=403, detail="Not authorized")
    
    # Update fields
    adjustment.adjustment_type = adjustment_update.adjustment_type
    adjustment.adjustment_date = adjustment_update.adjustment_date
    adjustment.reason = adjustment_update.reason
    adjustment.notes = adjustment_update.notes
    
    # Update items (delete old, add new)
    db.query(models.StockAdjustmentItem).filter(
        models.StockAdjustmentItem.stock_adjustment_id == adjustment_id
    ).delete()
    
    for item in adjustment_update.items:
        db_item = models.StockAdjustmentItem(
            stock_adjustment_id=adjustment_id,
            part_id=item.part_id,
            quantity_before=item.quantity_before,
            quantity_after=item.quantity_after,
            notes=item.notes
        )
        db.add(db_item)
    
    db.commit()
    return crud.get_stock_adjustment_by_id(db, adjustment_id)
```

## Frontend Service Methods

Add to `frontend/src/services/stockAdjustmentsService.js`:

```javascript
const deleteStockAdjustment = async (adjustmentId) => {
  return api.delete(`/stock-adjustments/${adjustmentId}`);
};

const updateStockAdjustment = async (adjustmentId, adjustmentData) => {
  return api.put(`/stock-adjustments/${adjustmentId}`, adjustmentData);
};

// Add to exports
export const stockAdjustmentsService = {
  // ... existing methods
  deleteStockAdjustment,
  updateStockAdjustment
};
```

## Implementation Steps

1. Add backend endpoints to `backend/app/routers/stock_adjustments.py`
2. Add service methods to `frontend/src/services/stockAdjustmentsService.js`
3. Update `StockAdjustmentsList.js` to add Edit/Delete buttons
4. Add edit modal (reuse CreateStockAdjustmentModal with edit mode)
5. Add delete confirmation modal
6. Restart API and rebuild frontend

## Quick Implementation

Run this to add the backend endpoints:
```bash
# Copy the endpoints from add_stock_adjustment_endpoints.py
# and append to backend/app/routers/stock_adjustments.py
cat add_stock_adjustment_endpoints.py >> backend/app/routers/stock_adjustments.py

# Restart API
docker-compose restart api
```

Then update the frontend components as described above.
