# backend/app/crud/machines.py

import uuid
import logging
from typing import List, Optional

from sqlalchemy.orm import Session
from fastapi import HTTPException, status # Import HTTPException and status

from .. import models, schemas # Import models and schemas

logger = logging.getLogger(__name__)

def get_machine(db: Session, machine_id: uuid.UUID):
    """Retrieve a single machine by ID."""
    return db.query(models.Machine).filter(models.Machine.id == machine_id).first()

def get_machines(db: Session, skip: int = 0, limit: int = 100, organization_id: Optional[uuid.UUID] = None):
    """
    Retrieve a list of machines, optionally filtered by organization ID.
    This function handles the database query and filtering.
    Authentication/Authorization is handled in the router.
    """
    query = db.query(models.Machine)
    if organization_id:
        query = query.filter(models.Machine.organization_id == organization_id)
    return query.offset(skip).limit(limit).all()

def create_machine(db: Session, machine: schemas.MachineCreate):
    """Create a new machine."""
    # Check if organization_id exists BEFORE creating the machine
    organization = db.query(models.Organization).filter(models.Organization.id == machine.organization_id).first()
    if not organization:
        raise HTTPException(status_code=400, detail="Organization ID not found")

    db_machine = models.Machine(**machine.dict())
    try:
        db.add(db_machine)
        db.commit()
        db.refresh(db_machine)
        return db_machine
    except Exception as e:
        db.rollback()
        # Specific error handling for unique constraint violation
        if "duplicate key value violates unique constraint" in str(e).lower() and "serial_number" in str(e).lower():
            raise HTTPException(status_code=409, detail="Machine with this serial number already exists for this organization.")
        logger.error(f"Error creating machine: {e}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred while creating the machine.")

def update_machine(db: Session, machine_id: uuid.UUID, machine_update: schemas.MachineUpdate):
    """Update an existing machine."""
    db_machine = db.query(models.Machine).filter(models.Machine.id == machine_id).first()
    if not db_machine:
        return None

    update_data = machine_update.dict(exclude_unset=True)

    # If organization_id is being updated, check if the new ID exists
    if "organization_id" in update_data and update_data["organization_id"] != db_machine.organization_id:
        organization = db.query(models.Organization).filter(models.Organization.id == update_data["organization_id"]).first()
        if not organization:
            raise HTTPException(status_code=400, detail="New Organization ID not found for machine update")

    for key, value in update_data.items():
        setattr(db_machine, key, value)
    
    try:
        db.add(db_machine) # Re-add to session to mark as dirty for update
        db.commit()
        db.refresh(db_machine)
        return db_machine
    except Exception as e:
        db.rollback()
        if "duplicate key value violates unique constraint" in str(e).lower() and "serial_number" in str(e).lower():
            raise HTTPException(status_code=409, detail="Machine with this serial number already exists for the target organization.")
        logger.error(f"Error updating machine: {e}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred while updating the machine.")

def delete_machine(db: Session, machine_id: uuid.UUID):
    """Delete a machine by ID."""
    db_machine = db.query(models.Machine).filter(models.Machine.id == machine_id).first()
    if not db_machine:
        return None
    try:
        db.delete(db_machine)
        db.commit()
        return {"message": "Machine deleted successfully"}
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting machine: {e}")
        # Provide a more specific error if it's due to foreign key constraints
        if "violates foreign key constraint" in str(e).lower():
            raise HTTPException(status_code=400, detail="Cannot delete machine due to existing dependent records (e.g., part usage). Please delete associated records first.")
        raise HTTPException(status_code=500, detail="An unexpected error occurred while deleting the machine.")

