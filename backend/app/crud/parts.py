# backend/app/crud/parts.py

import uuid
import logging
from typing import List, Optional

from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from .. import models, schemas # Import models and schemas

logger = logging.getLogger(__name__)

def get_part(db: Session, part_id: uuid.UUID):
    """Retrieve a single part by ID."""
    return db.query(models.Part).filter(models.Part.id == part_id).first()

def get_parts(db: Session, skip: int = 0, limit: int = 100):
    """Retrieve a list of parts."""
    return db.query(models.Part).offset(skip).limit(limit).all()

def create_part(db: Session, part: schemas.PartCreate):
    """Create a new part."""
    # The image_urls field is already a list from the schema, pass it directly
    db_part = models.Part(**part.dict())
    try:
        db.add(db_part)
        db.commit()
        db.refresh(db_part)
        return db_part
    except Exception as e:
        db.rollback()
        if "duplicate key value violates unique constraint" in str(e):
            raise HTTPException(status_code=409, detail="Part with this part number already exists")
        logger.error(f"Error creating part: {e}")
        raise HTTPException(status_code=400, detail="Error creating part")

def update_part(db: Session, part_id: uuid.UUID, part_update: schemas.PartUpdate):
    """Update an existing part."""
    db_part = db.query(models.Part).filter(models.Part.id == part_id).first()
    if not db_part:
        return None # Indicate not found

    update_data = part_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_part, key, value)
    try:
        db.add(db_part)
        db.commit()
        db.refresh(db_part)
        return db_part
    except Exception as e:
        db.rollback()
        if "duplicate key value violates unique constraint" in str(e):
            raise HTTPException(status_code=409, detail="Part with this part number already exists")
        logger.error(f"Error updating part: {e}")
        raise HTTPException(status_code=400, detail="Error updating part")

def delete_part(db: Session, part_id: uuid.UUID):
    """Delete a part by ID."""
    db_part = db.query(models.Part).filter(models.Part.id == part_id).first()
    if not db_part:
        return None # Indicate not found
    try:
        db.delete(db_part)
        db.commit()
        return {"message": "Part deleted successfully"}
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting part: {e}")
        raise HTTPException(status_code=400, detail="Error deleting part. Check for dependent records.")
