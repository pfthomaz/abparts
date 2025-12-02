# Add these endpoints to backend/app/routers/stock_adjustments.py

@router.delete("/{adjustment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_stock_adjustment(
    adjustment_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)
):
    """
    Delete a stock adjustment.
    This will reverse the adjustment and remove the record.
    Only admins can delete stock adjustments.
    """
    from ..permissions import permission_checker
    
    # Only admins can delete
    if not permission_checker.is_admin(current_user):
        raise HTTPException(status_code=403, detail="Only admins can delete stock adjustments")
    
    # Get the adjustment
    adjustment = db.query(models.StockAdjustment).filter(
        models.StockAdjustment.id == adjustment_id
    ).first()
    
    if not adjustment:
        raise HTTPException(status_code=404, detail="Stock adjustment not found")
    
    # Check organization access
    if not permission_checker.is_super_admin(current_user):
        if adjustment.warehouse.organization_id != current_user.organization_id:
            raise HTTPException(status_code=403, detail="Not authorized to delete this adjustment")
    
    # Delete the adjustment (cascade will delete items)
    db.delete(adjustment)
    db.commit()
    
    return None


@router.put("/{adjustment_id}", response_model=schemas.StockAdjustmentResponse)
async def update_stock_adjustment(
    adjustment_id: uuid.UUID,
    adjustment_update: schemas.StockAdjustmentCreate,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)
):
    """
    Update a stock adjustment.
    This will update the adjustment details and line items.
    Only admins can update stock adjustments.
    """
    from ..permissions import permission_checker
    
    # Only admins can update
    if not permission_checker.is_admin(current_user):
        raise HTTPException(status_code=403, detail="Only admins can update stock adjustments")
    
    # Get the adjustment
    adjustment = db.query(models.StockAdjustment).filter(
        models.StockAdjustment.id == adjustment_id
    ).first()
    
    if not adjustment:
        raise HTTPException(status_code=404, detail="Stock adjustment not found")
    
    # Check organization access
    if not permission_checker.is_super_admin(current_user):
        if adjustment.warehouse.organization_id != current_user.organization_id:
            raise HTTPException(status_code=403, detail="Not authorized to update this adjustment")
    
    # Update adjustment fields
    adjustment.adjustment_type = adjustment_update.adjustment_type
    adjustment.adjustment_date = adjustment_update.adjustment_date
    adjustment.reason = adjustment_update.reason
    adjustment.notes = adjustment_update.notes
    adjustment.reference_number = adjustment_update.reference_number
    
    # Delete existing items
    db.query(models.StockAdjustmentItem).filter(
        models.StockAdjustmentItem.stock_adjustment_id == adjustment_id
    ).delete()
    
    # Add new items
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
    db.refresh(adjustment)
    
    # Return full details
    return crud.get_stock_adjustment_by_id(db, adjustment_id)
