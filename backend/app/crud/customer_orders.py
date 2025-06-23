# backend/app/crud/customer_orders.py

import uuid
import logging
from typing import List, Optional

from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from .. import models, schemas # Import models and schemas

logger = logging.getLogger(__name__)

def get_customer_order(db: Session, order_id: uuid.UUID):
    """Retrieve a single customer order by ID."""
    return db.query(models.CustomerOrder).filter(models.CustomerOrder.id == order_id).first()

def get_customer_orders(db: Session, skip: int = 0, limit: int = 100):
    """Retrieve a list of customer orders."""
    return db.query(models.CustomerOrder).offset(skip).limit(limit).all()

def create_customer_order(db: Session, order: schemas.CustomerOrderCreate):
    """Create a new customer order."""
    # Validate FKs - these checks should ideally be in the router or a service layer
    customer_org = db.query(models.Organization).filter(models.Organization.id == order.customer_organization_id).first()
    oraseas_org = db.query(models.Organization).filter(models.Organization.id == order.oraseas_organization_id).first()
    if not customer_org or not oraseas_org:
        raise HTTPException(status_code=400, detail="Customer or Oraseas Organization ID not found")
    if order.ordered_by_user_id:
        user = db.query(models.User).filter(models.User.id == order.ordered_by_user_id).first()
        if not user: raise HTTPException(status_code=400, detail="Ordered by User ID not found")

    db_order = models.CustomerOrder(**order.dict())
    try:
        db.add(db_order)
        db.commit()
        db.refresh(db_order)
        return db_order
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating customer order: {e}")
        raise HTTPException(status_code=400, detail="Error creating customer order")

def update_customer_order(db: Session, order_id: uuid.UUID, order_update: schemas.CustomerOrderUpdate):
    """Update an existing customer order."""
    db_order = db.query(models.CustomerOrder).filter(models.CustomerOrder.id == order_id).first()
    if not db_order:
        return None # Indicate not found

    update_data = order_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_order, key, value)
    try:
        # Re-validate FKs if IDs are updated
        if "customer_organization_id" in update_data:
            customer_org = db.query(models.Organization).filter(models.Organization.id == db_order.customer_organization_id).first()
            if not customer_org: raise HTTPException(status_code=400, detail="Customer Organization ID not found")
        if "oraseas_organization_id" in update_data:
            oraseas_org = db.query(models.Organization).filter(models.Organization.id == db_order.oraseas_organization_id).first()
            if not oraseas_org: raise HTTPException(status_code=400, detail="Oraseas Organization ID not found")
        if "ordered_by_user_id" in update_data and db_order.ordered_by_user_id:
            user = db.query(models.User).filter(models.User.id == db_order.ordered_by_user_id).first()
            if not user: raise HTTPException(status_code=400, detail="Ordered by User ID not found")

        db.add(db_order)
        db.commit()
        db.refresh(db_order)
        return db_order
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating customer order: {e}")
        raise HTTPException(status_code=400, detail="Error updating customer order")

def delete_customer_order(db: Session, order_id: uuid.UUID):
    """Delete a customer order by ID."""
    db_order = db.query(models.CustomerOrder).filter(models.CustomerOrder.id == order_id).first()
    if not db_order:
        return None # Indicate not found
    try:
        db.delete(db_order)
        db.commit()
        return {"message": "Customer order deleted successfully"}
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting customer order: {e}")
        raise HTTPException(status_code=400, detail="Error deleting customer order. Check for dependent records.")
