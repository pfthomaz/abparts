# backend/app/crud/customer_order_items.py

import uuid
import logging
from typing import List, Optional

from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from .. import models, schemas # Import models and schemas

logger = logging.getLogger(__name__)

def get_customer_order_item(db: Session, item_id: uuid.UUID):
    """Retrieve a single customer order item by ID."""
    return db.query(models.CustomerOrderItem).filter(models.CustomerOrderItem.id == item_id).first()

def get_customer_order_items(db: Session, skip: int = 0, limit: int = 100):
    """Retrieve a list of customer order items."""
    return db.query(models.CustomerOrderItem).offset(skip).limit(limit).all()

def create_customer_order_item(db: Session, item: schemas.CustomerOrderItemCreate):
    """Create a new customer order item."""
    # Validate FKs - these checks should ideally be in the router or a service layer
    order = db.query(models.CustomerOrder).filter(models.CustomerOrder.id == item.customer_order_id).first()
    part = db.query(models.Part).filter(models.Part.id == item.part_id).first()
    if not order:
        raise HTTPException(status_code=400, detail="Customer Order ID not found")
    if not part:
        raise HTTPException(status_code=400, detail="Part ID not found")

    db_item = models.CustomerOrderItem(**item.dict())
    try:
        db.add(db_item)
        db.commit()
        db.refresh(db_item)
        return db_item
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating customer order item: {e}")
        raise HTTPException(status_code=400, detail="Error creating customer order item")

def update_customer_order_item(db: Session, item_id: uuid.UUID, item_update: schemas.CustomerOrderItemUpdate):
    """Update an existing customer order item."""
    db_item = db.query(models.CustomerOrderItem).filter(models.CustomerOrderItem.id == item_id).first()
    if not db_item:
        return None # Indicate not found

    update_data = item_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_item, key, value)
    try:
        # Re-validate FKs if IDs are updated
        if "customer_order_id" in update_data:
            order = db.query(models.CustomerOrder).filter(models.CustomerOrder.id == db_item.customer_order_id).first()
            if not order: raise HTTPException(status_code=400, detail="Customer Order ID not found")
        if "part_id" in update_data:
            part = db.query(models.Part).filter(models.Part.id == db_item.part_id).first()
            if not part: raise HTTPException(status_code=400, detail="Part ID not found")

        db.add(db_item)
        db.commit()
        db.refresh(db_item)
        return db_item
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating customer order item: {e}")
        raise HTTPException(status_code=400, detail="Error updating customer order item")

def delete_customer_order_item(db: Session, item_id: uuid.UUID):
    """Delete a customer order item by ID."""
    db_item = db.query(models.CustomerOrderItem).filter(models.CustomerOrderItem.id == item_id).first()
    if not db_item:
        return None # Indicate not found
    try:
        db.delete(db_item)
        db.commit()
        return {"message": "Customer order item deleted successfully"}
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting customer order item: {e}")
        raise HTTPException(status_code=400, detail="Error deleting customer order item. Check for dependent records.")
