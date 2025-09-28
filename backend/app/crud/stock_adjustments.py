# backend/app/crud/stock_adjustments.py

import uuid
import logging
from typing import List, Optional

from sqlalchemy.orm import Session
from sqlalchemy import func # for sum
from fastapi import HTTPException, status

from .. import models, schemas # Import models and schemas
from ..models import StockAdjustmentReason # Import the enum

logger = logging.getLogger(__name__)

def create_stock_adjustment(db: Session, inventory_id: uuid.UUID, adjustment_in: schemas.StockAdjustmentCreate, user_id: uuid.UUID):
    """
    Create a new stock adjustment and update the inventory's current_stock.
    """
    # Validate reason_code
    try:
        StockAdjustmentReason(adjustment_in.reason_code)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid reason_code: {adjustment_in.reason_code}. Must be one of {[r.value for r in StockAdjustmentReason]}")

    # Begin a transaction
    try:
        # Fetch the inventory item
        inventory_item = db.query(models.Inventory).filter(models.Inventory.id == inventory_id).first()
        if not inventory_item:
            raise HTTPException(status_code=404, detail="Inventory item not found")

        # Create the stock adjustment record
        db_adjustment = models.StockAdjustment(
            inventory_id=inventory_id,
            user_id=user_id,
            quantity_adjusted=adjustment_in.quantity_adjusted,
            reason_code=adjustment_in.reason_code,
            notes=adjustment_in.notes
            # adjustment_date is server_default
        )
        db.add(db_adjustment)

        # Update the current stock in the inventory item
        inventory_item.current_stock += adjustment_in.quantity_adjusted

        # Sanity check: stock should not go below zero if not allowed by business logic (not enforced here yet)
        # if inventory_item.current_stock < 0:
        #     raise HTTPException(status_code=400, detail="Stock cannot go below zero.")

        db.add(inventory_item)

        db.commit()
        db.refresh(db_adjustment)
        db.refresh(inventory_item) # Refresh to get updated inventory

        return db_adjustment

    except HTTPException: # Re-raise HTTPExceptions
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating stock adjustment: {e}")
        raise HTTPException(status_code=500, detail="Error creating stock adjustment")


def get_stock_adjustment(db: Session, adjustment_id: uuid.UUID) -> Optional[models.StockAdjustment]:
    """Retrieve a single stock adjustment by ID."""
    return db.query(models.StockAdjustment).filter(models.StockAdjustment.id == adjustment_id).first()


def get_stock_adjustments_for_inventory_item(
    db: Session,
    inventory_id: uuid.UUID,
    skip: int = 0,
    limit: int = 100
) -> List[models.StockAdjustment]:
    """Retrieve a list of stock adjustments for a specific inventory item."""
    return db.query(models.StockAdjustment)\
        .filter(models.StockAdjustment.inventory_id == inventory_id)\
        .order_by(models.StockAdjustment.adjustment_date.desc())\
        .offset(skip)\
        .limit(limit)\
        .all()

def get_all_stock_adjustments(db: Session, skip: int = 0, limit: int = 100) -> List[models.StockAdjustment]:
    """Retrieve all stock adjustments (admin use)."""
    return db.query(models.StockAdjustment)\
        .order_by(models.StockAdjustment.adjustment_date.desc())\
        .offset(skip)\
        .limit(limit)\
        .all()

def get_stock_adjustments_by_organization(
    db: Session, 
    organization_id: uuid.UUID, 
    skip: int = 0, 
    limit: int = 100
) -> List[models.StockAdjustment]:
    """Retrieve stock adjustments for a specific organization."""
    return db.query(models.StockAdjustment)\
        .join(models.Inventory, models.StockAdjustment.inventory_id == models.Inventory.id)\
        .join(models.Warehouse, models.Inventory.warehouse_id == models.Warehouse.id)\
        .filter(models.Warehouse.organization_id == organization_id)\
        .order_by(models.StockAdjustment.adjustment_date.desc())\
        .offset(skip)\
        .limit(limit)\
        .all()

def create_stock_adjustment_with_frontend_schema(
    db: Session, 
    inventory_id: uuid.UUID, 
    adjustment_in: schemas.StockAdjustmentCreate, 
    user_id: uuid.UUID
):
    """
    Create a stock adjustment using frontend-compatible schema.
    Maps frontend field names to database field names.
    """
    # Map frontend schema to database schema
    db_adjustment_data = {
        "quantity_adjusted": adjustment_in.quantity_change,
        "reason_code": adjustment_in.reason,
        "notes": adjustment_in.notes
    }
    
    # Create a temporary schema object with database field names
    class TempAdjustmentCreate:
        def __init__(self, quantity_adjusted, reason_code, notes):
            self.quantity_adjusted = quantity_adjusted
            self.reason_code = reason_code
            self.notes = notes
    
    temp_adjustment = TempAdjustmentCreate(
        quantity_adjusted=adjustment_in.quantity_change,
        reason_code=adjustment_in.reason,
        notes=adjustment_in.notes
    )
    
    # Validate reason (skip enum validation for now since frontend uses free text)
    # We'll store the reason as-is for now
    
    try:
        # Fetch the inventory item
        inventory_item = db.query(models.Inventory).filter(models.Inventory.id == inventory_id).first()
        if not inventory_item:
            raise HTTPException(status_code=404, detail="Inventory item not found")

        # Create the stock adjustment record
        db_adjustment = models.StockAdjustment(
            inventory_id=inventory_id,
            user_id=user_id,
            quantity_adjusted=adjustment_in.quantity_change,
            reason_code=adjustment_in.reason,
            notes=adjustment_in.notes
        )
        db.add(db_adjustment)

        # Update the current stock in the inventory item
        inventory_item.current_stock += adjustment_in.quantity_change

        db.add(inventory_item)
        db.commit()
        db.refresh(db_adjustment)
        db.refresh(inventory_item)

        return db_adjustment

    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating stock adjustment: {e}")
        raise HTTPException(status_code=500, detail="Error creating stock adjustment")
