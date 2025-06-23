# backend/app/crud/supplier_order_items.py

import uuid
import logging
from typing import List, Optional

from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from .. import models, schemas # Import models and schemas

logger = logging.getLogger(__name__)

def get_supplier_order_item(db: Session, item_id: uuid.UUID):
    """Retrieve a single supplier order item by ID."""
    return db.query(models.SupplierOrderItem).filter(models.SupplierOrderItem.id == item_id).first()

def get_supplier_order_items(db: Session, skip: int = 0, limit: int = 100):
    """Retrieve a list of supplier order items."""
    return db.query(models.SupplierOrderItem).offset(skip).limit(limit).all()

def create_supplier_order_item(db: Session, item: schemas.SupplierOrderItemCreate):
    """Create a new supplier order item."""
    # Validate FKs - these checks should ideally be in the router or a service layer
    order = db.query(models.SupplierOrder).filter(models.SupplierOrder.id == item.supplier_order_id).first()
    part = db.query(models.Part).filter(models.Part.id == item.part_id).first()
    if not order:
        raise HTTPException(status_code=400, detail="Supplier Order ID not found")
    if not part:
        raise HTTPException(status_code=400, detail="Part ID not found")

    db_item = models.SupplierOrderItem(**item.dict())
    try:
        db.add(db_item)
        db.commit()
        db.refresh(db_item)
        return db_item
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating supplier order item: {e}")
        raise HTTPException(status_code=400, detail="Error creating supplier order item")

def update_supplier_order_item(db: Session, item_id: uuid.UUID, item_update: schemas.SupplierOrderItemUpdate):
    """Update an existing supplier order item."""
    db_item = db.query(models.SupplierOrderItem).filter(models.SupplierOrderItem.id == item_id).first()
    if not db_item:
        return None # Indicate not found

    update_data = item_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_item, key, value)
    try:
        # Re-validate FKs if IDs are updated
        if "supplier_order_id" in update_data:
            order = db.query(models.SupplierOrder).filter(models.SupplierOrder.id == db_item.supplier_order_id).first()
            if not order: raise HTTPException(status_code=400, detail="Supplier Order ID not found")
        if "part_id" in update_data:
            part = db.query(models.Part).filter(models.Part.id == db_item.part_id).first()
            if not part: raise HTTPException(status_code=400, detail="Part ID not found")

        db.add(db_item)
        db.commit()
        db.refresh(db_item)
        return db_item
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating supplier order item: {e}")
        raise HTTPException(status_code=400, detail="Error updating supplier order item")

def delete_supplier_order_item(db: Session, item_id: uuid.UUID):
    """Delete a supplier order item by ID."""
    db_item = db.query(models.SupplierOrderItem).filter(models.SupplierOrderItem.id == item_id).first()
    if not db_item:
        return None # Indicate not found
    try:
        db.delete(db_item)
        db.commit()
        return {"message": "Supplier order item deleted successfully"}
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting supplier order item: {e}")
        raise HTTPException(status_code=400, detail="Error deleting supplier order item. Check for dependent records.")
