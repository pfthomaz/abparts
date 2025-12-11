# backend/app/routers/stock_adjustments.py

import uuid
from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from .. import schemas, models
from ..database import get_db
from ..auth import get_current_user, TokenData
from ..crud import stock_adjustments as crud

router = APIRouter()


@router.post("/", response_model=schemas.StockAdjustmentResponse, status_code=status.HTTP_201_CREATED)
async def create_stock_adjustment(
    adjustment: schemas.StockAdjustmentCreate,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)
):
    """
    Create a new stock adjustment with line items.
    
    This will:
    1. Create the adjustment record
    2. Create line items for each part
    3. Update inventory quantities
    4. Create transaction records for audit trail
    """
    try:
        result = crud.create_stock_adjustment(
            db=db,
            adjustment_data=adjustment,
            current_user_id=current_user.user_id
        )
        
        # Get full details for response
        adjustment_detail = crud.get_stock_adjustment_by_id(db, result.id)
        return adjustment_detail
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create stock adjustment: {str(e)}")


@router.get("/", response_model=List[schemas.StockAdjustmentListResponse])
async def list_stock_adjustments(
    warehouse_id: Optional[uuid.UUID] = Query(None, description="Filter by warehouse"),
    adjustment_type: Optional[str] = Query(None, description="Filter by adjustment type"),
    user_id: Optional[uuid.UUID] = Query(None, description="Filter by user who made adjustment"),
    start_date: Optional[datetime] = Query(None, description="Filter by start date"),
    end_date: Optional[datetime] = Query(None, description="Filter by end date"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)
):
    """
    List stock adjustments with optional filtering.
    Returns basic info without full item details for performance.
    """
    try:
        adjustments = crud.get_stock_adjustments(
            db=db,
            warehouse_id=warehouse_id,
            adjustment_type=adjustment_type,
            user_id=user_id,
            start_date=start_date,
            end_date=end_date,
            skip=skip,
            limit=limit
        )
        return adjustments
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch adjustments: {str(e)}")


@router.get("/{adjustment_id}", response_model=schemas.StockAdjustmentResponse)
async def get_stock_adjustment(
    adjustment_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)
):
    """
    Get a single stock adjustment with full details including all line items.
    """
    adjustment = crud.get_stock_adjustment_by_id(db, adjustment_id)
    
    if not adjustment:
        raise HTTPException(status_code=404, detail="Stock adjustment not found")
    
    return adjustment


@router.get("/parts/{part_id}/history", response_model=List[dict])
async def get_part_adjustment_history(
    part_id: uuid.UUID,
    warehouse_id: Optional[uuid.UUID] = Query(None, description="Filter by warehouse"),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)
):
    """
    Get adjustment history for a specific part.
    Useful for tracking how a part's quantity has changed over time.
    """
    try:
        history = crud.get_adjustment_history_for_part(
            db=db,
            part_id=part_id,
            warehouse_id=warehouse_id,
            limit=limit
        )
        return history
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch history: {str(e)}")


# --- Delete Stock Adjustment ---
@router.delete("/{adjustment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_stock_adjustment(
    adjustment_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)
):
    """
    Delete a stock adjustment.
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
        warehouse = db.query(models.Warehouse).filter(
            models.Warehouse.id == adjustment.warehouse_id
        ).first()
        if warehouse and warehouse.organization_id != current_user.organization_id:
            raise HTTPException(status_code=403, detail="Not authorized to delete this adjustment")
    
    # Delete the adjustment (cascade will delete items)
    db.delete(adjustment)
    db.commit()
    
    return None


# --- Update Stock Adjustment ---
@router.put("/{adjustment_id}", response_model=schemas.StockAdjustmentResponse)
async def update_stock_adjustment(
    adjustment_id: uuid.UUID,
    adjustment_update: schemas.StockAdjustmentCreate,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)
):
    """
    Update a stock adjustment.
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
        warehouse = db.query(models.Warehouse).filter(
            models.Warehouse.id == adjustment.warehouse_id
        ).first()
        if warehouse and warehouse.organization_id != current_user.organization_id:
            raise HTTPException(status_code=403, detail="Not authorized to update this adjustment")
    
    try:
        # Update adjustment fields
        adjustment.adjustment_type = adjustment_update.adjustment_type
        adjustment.reason = adjustment_update.reason
        adjustment.notes = adjustment_update.notes
        adjustment.total_items_adjusted = len(adjustment_update.items)
        
        # Delete existing items
        db.query(models.StockAdjustmentItem).filter(
            models.StockAdjustmentItem.stock_adjustment_id == adjustment_id
        ).delete()
        
        # Add new items
        from ..crud.inventory_calculator import calculate_current_stock
        
        for item in adjustment_update.items:
            # Use provided quantity_before or calculate it
            quantity_before = getattr(item, 'quantity_before', None)
            if quantity_before is None:
                quantity_before = calculate_current_stock(db, adjustment.warehouse_id, item.part_id)
            
            quantity_change = item.quantity_after - quantity_before
            db_item = models.StockAdjustmentItem(
                stock_adjustment_id=adjustment_id,
                part_id=item.part_id,
                quantity_before=quantity_before,
                quantity_after=item.quantity_after,
                quantity_change=quantity_change,
                reason=item.reason
            )
            db.add(db_item)
        
        db.commit()
        db.refresh(adjustment)
        
        # Return full details
        return crud.get_stock_adjustment_by_id(db, adjustment_id)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to update stock adjustment: {str(e)}")
