# backend/app/crud/inventory.py

import uuid
import logging
from typing import List, Optional

from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from .. import models, schemas # Import models and schemas

logger = logging.getLogger(__name__)

def get_inventory_item(db: Session, inventory_id: uuid.UUID):
    """Retrieve a single inventory item by ID."""
    return db.query(models.Inventory).filter(models.Inventory.id == inventory_id).first()

def get_inventory_items(db: Session, skip: int = 0, limit: int = 100):
    """Retrieve a list of inventory items."""
    return db.query(models.Inventory).offset(skip).limit(limit).all()

def create_inventory_item(db: Session, item: schemas.InventoryCreate):
    """Create a new inventory item."""
    # Validate FKs - these checks should ideally be in the router or a service layer
    # but for direct CRUD function, they are fine here for simplicity.
    organization = db.query(models.Organization).filter(models.Organization.id == item.organization_id).first()
    part = db.query(models.Part).filter(models.Part.id == item.part_id).first()
    if not organization:
        raise HTTPException(status_code=400, detail="Organization ID not found")
    if not part:
        raise HTTPException(status_code=400, detail="Part ID not found")

    db_item = models.Inventory(**item.dict())
    try:
        db.add(db_item)
        db.commit()
        db.refresh(db_item)
        return db_item
    except Exception as e:
        db.rollback()
        if "duplicate key value violates unique constraint" in str(e):
            raise HTTPException(status_code=409, detail="Inventory for this organization and part already exists")
        logger.error(f"Error creating inventory item: {e}")
        raise HTTPException(status_code=400, detail="Error creating inventory item")

def update_inventory_item(db: Session, inventory_id: uuid.UUID, item_update: schemas.InventoryUpdate):
    """Update an existing inventory item."""
    db_item = db.query(models.Inventory).filter(models.Inventory.id == inventory_id).first()
    if not db_item:
        return None # Indicate not found

    update_data = item_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_item, key, value)
    try:
        # Re-validate FKs if organization_id or part_id are updated
        if "organization_id" in update_data:
            organization = db.query(models.Organization).filter(models.Organization.id == db_item.organization_id).first()
            if not organization: raise HTTPException(status_code=400, detail="Organization ID not found")
        if "part_id" in update_data:
            part = db.query(models.Part).filter(models.Part.id == db_item.part_id).first()
            if not part: raise HTTPException(status_code=400, detail="Part ID not found")

        db.add(db_item)
        db.commit()
        db.refresh(db_item)
        return db_item
    except Exception as e:
        db.rollback()
        if "duplicate key value violates unique constraint" in str(e):
            raise HTTPException(status_code=409, detail="Inventory for this organization and part already exists")
        logger.error(f"Error updating inventory item: {e}")
        raise HTTPException(status_code=400, detail="Error updating inventory item")

def delete_inventory_item(db: Session, inventory_id: uuid.UUID):
    """Delete an inventory item by ID."""
    db_item = db.query(models.Inventory).filter(models.Inventory.id == inventory_id).first()
    if not db_item:
        return None # Indicate not found
    try:
        db.delete(db_item)
        db.commit()
        return {"message": "Inventory item deleted successfully"}
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting inventory item: {e}")
        raise HTTPException(status_code=400, detail="Error deleting inventory item.")


def get_stocktake_worksheet_items(db: Session, organization_id: uuid.UUID) -> List[schemas.StocktakeWorksheetItemResponse]:
    """
    Retrieve inventory items for a stocktake worksheet for a given organization.
    Includes part details (number, name) and current stock.
    """
    # Fetch inventory items for the organization, joining with Part to get part details
    results = db.query(
        models.Inventory.id, # inventory_id
        models.Part.id,      # part_id
        models.Part.part_number,
        models.Part.name,    # part_name
        models.Inventory.current_stock # system_quantity
    ).join(models.Part, models.Inventory.part_id == models.Part.id)\
     .filter(models.Inventory.organization_id == organization_id)\
     .order_by(models.Part.part_number)\
     .all()

    if not results:
        return []

    # Map results to the Pydantic schema
    worksheet_items = [
        schemas.StocktakeWorksheetItemResponse(
            inventory_id=row[0],
            part_id=row[1],
            part_number=row[2],
            part_name=row[3],
            system_quantity=row[4]
        ) for row in results
    ]
    return worksheet_items
