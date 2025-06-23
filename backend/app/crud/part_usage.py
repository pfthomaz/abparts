# backend/app/crud/part_usage.py

import uuid
import logging
from typing import List, Optional

from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from .. import models, schemas # Import models and schemas

logger = logging.getLogger(__name__)

def get_part_usage(db: Session, usage_id: uuid.UUID):
    """Retrieve a single part usage record by ID."""
    return db.query(models.PartUsage).filter(models.PartUsage.id == usage_id).first()

def get_part_usages(db: Session, skip: int = 0, limit: int = 100):
    """Retrieve a list of part usage records."""
    return db.query(models.PartUsage).offset(skip).limit(limit).all()

def create_part_usage(db: Session, usage: schemas.PartUsageCreate):
    """Create a new part usage record."""
    # Validate FKs - these checks should ideally be in the router or a service layer
    customer_org = db.query(models.Organization).filter(models.Organization.id == usage.customer_organization_id).first()
    part = db.query(models.Part).filter(models.Part.id == usage.part_id).first()
    if not customer_org:
        raise HTTPException(status_code=400, detail="Customer Organization ID not found")
    if not part:
        raise HTTPException(status_code=400, detail="Part ID not found")
    if usage.recorded_by_user_id:
        user = db.query(models.User).filter(models.User.id == usage.recorded_by_user_id).first()
        if not user: raise HTTPException(status_code=400, detail="Recorded by User ID not found")

    db_usage = models.PartUsage(**usage.dict())
    try:
        db.add(db_usage)
        db.commit()
        db.refresh(db_usage)
        return db_usage
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating part usage record: {e}")
        raise HTTPException(status_code=400, detail="Error creating part usage record")

def update_part_usage(db: Session, usage_id: uuid.UUID, usage_update: schemas.PartUsageUpdate):
    """Update an existing part usage record."""
    db_usage = db.query(models.PartUsage).filter(models.PartUsage.id == usage_id).first()
    if not db_usage:
        return None # Indicate not found

    update_data = usage_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_usage, key, value)
    try:
        # Re-validate FKs if IDs are updated
        if "customer_organization_id" in update_data:
            customer_org = db.query(models.Organization).filter(models.Organization.id == db_usage.customer_organization_id).first()
            if not customer_org: raise HTTPException(status_code=400, detail="Customer Organization ID not found")
        if "part_id" in update_data:
            part = db.query(models.Part).filter(models.Part.id == db_usage.part_id).first()
            if not part: raise HTTPException(status_code=400, detail="Part ID not found")
        if "recorded_by_user_id" in update_data and db_usage.recorded_by_user_id:
            user = db.query(models.User).filter(models.User.id == db_usage.recorded_by_user_id).first()
            if not user: raise HTTPException(status_code=400, detail="Recorded by User ID not found")

        db.add(db_usage)
        db.commit()
        db.refresh(db_usage)
        return db_usage
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating part usage record: {e}")
        raise HTTPException(status_code=400, detail="Error updating part usage record")

def delete_part_usage(db: Session, usage_id: uuid.UUID):
    """Delete a part usage record by ID."""
    db_usage = db.query(models.PartUsage).filter(models.PartUsage.id == usage_id).first()
    if not db_usage:
        return None # Indicate not found
    try:
        db.delete(db_usage)
        db.commit()
        return {"message": "Part usage record deleted successfully"}
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting part usage record: {e}")
        raise HTTPException(status_code=400, detail="Error deleting part usage record. Check for dependent records.")
