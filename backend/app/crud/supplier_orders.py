# backend/app/crud/supplier_orders.py

import uuid
import logging
from typing import List, Optional

from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from .. import models, schemas # Import models and schemas

logger = logging.getLogger(__name__)

def get_supplier_order(db: Session, order_id: uuid.UUID):
    """Retrieve a single supplier order by ID."""
    return db.query(models.SupplierOrder).filter(models.SupplierOrder.id == order_id).first()

def get_supplier_orders(db: Session, skip: int = 0, limit: int = 100):
    """Retrieve a list of supplier orders."""
    return db.query(models.SupplierOrder).offset(skip).limit(limit).all()

def create_supplier_order(db: Session, order: schemas.SupplierOrderCreate):
    """Create a new supplier order."""
    # Validate FK
    organization = db.query(models.Organization).filter(models.Organization.id == order.ordering_organization_id).first()
    if not organization:
        raise HTTPException(status_code=400, detail="Ordering Organization ID not found")

    db_order = models.SupplierOrder(**order.dict())
    try:
        db.add(db_order)
        db.commit()
        db.refresh(db_order)
        return db_order
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating supplier order: {e}")
        raise HTTPException(status_code=400, detail="Error creating supplier order")

def update_supplier_order(db: Session, order_id: uuid.UUID, order_update: schemas.SupplierOrderUpdate):
    """Update an existing supplier order."""
    db_order = db.query(models.SupplierOrder).filter(models.SupplierOrder.id == order_id).first()
    if not db_order:
        return None # Indicate not found

    update_data = order_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_order, key, value)
    try:
        if "ordering_organization_id" in update_data:
            organization = db.query(models.Organization).filter(models.Organization.id == db_order.ordering_organization_id).first()
            if not organization: raise HTTPException(status_code=400, detail="Ordering Organization ID not found")

        db.add(db_order)
        db.commit()
        db.refresh(db_order)
        return db_order
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating supplier order: {e}")
        raise HTTPException(status_code=400, detail="Error updating supplier order")

def delete_supplier_order(db: Session, order_id: uuid.UUID):
    """Delete a supplier order by ID."""
    db_order = db.query(models.SupplierOrder).filter(models.SupplierOrder.id == order_id).first()
    if not db_order:
        return None # Indicate not found
    try:
        db.delete(db_order)
        db.commit()
        return {"message": "Supplier order deleted successfully"}
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting supplier order: {e}")
        raise HTTPException(status_code=400, detail="Error deleting supplier order. Check for dependent records.")

