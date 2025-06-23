# backend/app/crud/organizations.py

import uuid
import logging
from typing import List, Optional

from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from .. import models, schemas # Import models and schemas

logger = logging.getLogger(__name__)

def get_organization(db: Session, org_id: uuid.UUID):
    """Retrieve a single organization by ID."""
    return db.query(models.Organization).filter(models.Organization.id == org_id).first()

def get_organizations(db: Session, skip: int = 0, limit: int = 100):
    """Retrieve a list of organizations."""
    return db.query(models.Organization).offset(skip).limit(limit).all()

def create_organization(db: Session, org: schemas.OrganizationCreate):
    """Create a new organization."""
    db_organization = models.Organization(**org.dict())
    try:
        db.add(db_organization)
        db.commit()
        db.refresh(db_organization)
        return db_organization
    except Exception as e:
        db.rollback()
        if "duplicate key value violates unique constraint" in str(e):
            raise HTTPException(status_code=409, detail="Organization with this name already exists")
        logger.error(f"Error creating organization: {e}")
        raise HTTPException(status_code=400, detail="Error creating organization")

def update_organization(db: Session, org_id: uuid.UUID, org_update: schemas.OrganizationUpdate):
    """Update an existing organization."""
    db_organization = db.query(models.Organization).filter(models.Organization.id == org_id).first()
    if not db_organization:
        return None

    update_data = org_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_organization, key, value)
    try:
        db.add(db_organization)
        db.commit()
        db.refresh(db_organization)
        return db_organization
    except Exception as e:
        db.rollback()
        if "duplicate key value violates unique constraint" in str(e):
            raise HTTPException(status_code=409, detail="Organization with this name already exists")
        logger.error(f"Error updating organization: {e}")
        raise HTTPException(status_code=400, detail="Error updating organization")

def delete_organization(db: Session, org_id: uuid.UUID):
    """Delete an organization by ID."""
    db_organization = db.query(models.Organization).filter(models.Organization.id == org_id).first()
    if not db_organization:
        return None
    try:
        db.delete(db_organization)
        db.commit()
        return {"message": "Organization deleted successfully"}
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting organization: {e}")
        raise HTTPException(status_code=400, detail="Error deleting organization. Check for dependent records.")

