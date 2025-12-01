# backend/app/routers/inventory_calculator.py

import uuid
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from decimal import Decimal

from ..database import get_db
from ..auth import get_current_user, TokenData
from ..crud import inventory_calculator

router = APIRouter(prefix="/inventory/calculated", tags=["inventory-calculator"])


@router.get("/{warehouse_id}/{part_id}")
async def get_calculated_stock(
    warehouse_id: uuid.UUID,
    part_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)
):
    """
    Get the calculated current stock for a specific part in a warehouse.
    This is calculated from all transactions and adjustments, not from cached values.
    """
    try:
        stock = inventory_calculator.calculate_current_stock(db, warehouse_id, part_id)
        return {
            "warehouse_id": warehouse_id,
            "part_id": part_id,
            "current_stock": float(stock),
            "calculation_method": "sum_of_transactions_and_adjustments"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{warehouse_id}")
async def get_warehouse_calculated_stock(
    warehouse_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)
):
    """
    Get calculated stock levels for all parts in a warehouse.
    """
    try:
        stock_levels = inventory_calculator.calculate_all_warehouse_stock(db, warehouse_id)
        
        # Convert to list format
        results = [
            {
                "part_id": str(part_id),
                "current_stock": float(stock)
            }
            for part_id, stock in stock_levels.items()
        ]
        
        return {
            "warehouse_id": warehouse_id,
            "parts": results,
            "total_parts": len(results),
            "calculation_method": "sum_of_transactions_and_adjustments"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/refresh-cache")
async def refresh_inventory_cache(
    warehouse_id: Optional[uuid.UUID] = Query(None, description="Refresh only this warehouse"),
    part_id: Optional[uuid.UUID] = Query(None, description="Refresh only this part"),
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)
):
    """
    Refresh the cached current_stock values in the inventory table.
    This updates the cache to match calculated values from transactions.
    """
    try:
        updated_count = inventory_calculator.refresh_inventory_cache(db, warehouse_id, part_id)
        return {
            "success": True,
            "records_updated": updated_count,
            "message": f"Updated {updated_count} inventory records"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/")
async def get_all_calculated_inventory(
    warehouse_id: Optional[uuid.UUID] = Query(None),
    part_id: Optional[uuid.UUID] = Query(None),
    include_zero_stock: bool = Query(False),
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)
):
    """
    Get inventory with calculated stock levels.
    Shows both calculated and cached values for comparison.
    """
    try:
        results = inventory_calculator.get_inventory_with_calculated_stock(
            db,
            warehouse_id=warehouse_id,
            part_id=part_id,
            include_zero_stock=include_zero_stock
        )
        
        return {
            "inventory": results,
            "total_records": len(results),
            "calculation_method": "sum_of_transactions_and_adjustments"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
