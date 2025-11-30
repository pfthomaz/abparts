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
