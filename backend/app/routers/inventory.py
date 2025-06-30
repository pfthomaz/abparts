# backend/app/routers/inventory.py

import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .. import schemas, crud, models # Import schemas, CRUD functions, and models
from ..database import get_db # Import DB session dependency
from ..auth import get_current_user, has_role, has_roles, TokenData # Import authentication dependencies

router = APIRouter()

# --- Inventory CRUD ---
@router.get("/", response_model=List[schemas.InventoryResponse])
async def get_inventory_items(
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)
):
    if current_user.role == "Oraseas Admin":
        inventory_items = crud.inventory.get_inventory_items(db)
    elif current_user.role in ["Customer Admin", "Customer User"]:
        # Customers can only see inventory of their own organization
        inventory_items = db.query(models.Inventory).filter(models.Inventory.organization_id == current_user.organization_id).all()
    else:
        raise HTTPException(status_code=403, detail="Not authorized to view this inventory")
    return inventory_items

@router.get("/{inventory_id}", response_model=schemas.InventoryResponse)
async def get_inventory_item(
    inventory_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)
):
    inventory_item = crud.inventory.get_inventory_item(db, inventory_id)
    if not inventory_item:
        raise HTTPException(status_code=404, detail="Inventory item not found")

    if current_user.role == "Oraseas Admin" or inventory_item.organization_id == current_user.organization_id:
        return inventory_item
    else:
        raise HTTPException(status_code=403, detail="Not authorized to view this inventory item")

@router.post("/", response_model=schemas.InventoryResponse, status_code=status.HTTP_201_CREATED)
async def create_inventory_item(
    item: schemas.InventoryCreate,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(has_roles(["Oraseas Admin", "Oraseas Inventory Manager"])) # Only Oraseas can create new stock records
):
    # Authorization check for Oraseas: can only manage Oraseas warehouse inventory directly
    # (Customers update their inventory via orders/usage, not direct creation here)
    oraseas_org = db.query(models.Organization).filter(models.Organization.name == 'Oraseas EE').first() # Get Oraseas's actual ID
    if not oraseas_org or item.organization_id != oraseas_org.id:
        raise HTTPException(status_code=403, detail="Only Oraseas can create new inventory records.")

    db_item = crud.inventory.create_inventory_item(db, item)
    if not db_item:
        raise HTTPException(status_code=400, detail="Failed to create inventory item")
    return db_item

@router.put("/{inventory_id}", response_model=schemas.InventoryResponse)
async def update_inventory_item(
    inventory_id: uuid.UUID,
    item_update: schemas.InventoryUpdate,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(has_roles(["Oraseas Admin", "Oraseas Inventory Manager", "Customer Admin"]))
):
    db_item = crud.inventory.get_inventory_item(db, inventory_id)
    if not db_item:
        raise HTTPException(status_code=404, detail="Inventory item not found")

    # Authorization:
    # Oraseas Admin/Inventory Manager can update any inventory item.
    # Customer Admin can only update their OWN organization's inventory items.
    if current_user.role in ["Oraseas Admin", "Oraseas Inventory Manager"] or \
       (current_user.role == "Customer Admin" and db_item.organization_id == current_user.organization_id):
        
        # Prevent customers from changing organization_id or part_id on update
        if current_user.role == "Customer Admin":
            if item_update.organization_id is not None and item_update.organization_id != db_item.organization_id:
                raise HTTPException(status_code=403, detail="Customer Admin cannot change inventory organization ID.")
            if item_update.part_id is not None and item_update.part_id != db_item.part_id:
                raise HTTPException(status_code=403, detail="Customer Admin cannot change inventory part ID.")

        updated_item = crud.inventory.update_inventory_item(db, inventory_id, item_update)
        if not updated_item:
            raise HTTPException(status_code=400, detail="Failed to update inventory item")
        return updated_item
    else:
        raise HTTPException(status_code=403, detail="Not authorized to update this inventory item")


@router.delete("/{inventory_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_inventory_item(
    inventory_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(has_roles(["Oraseas Admin", "Oraseas Inventory Manager"])) # Only Oraseas can delete stock records
):
    db_item = crud.inventory.get_inventory_item(db, inventory_id)
    if not db_item:
        raise HTTPException(status_code=404, detail="Inventory item not found")

    oraseas_org = db.query(models.Organization).filter(models.Organization.name == 'Oraseas EE').first()
    if not oraseas_org or db_item.organization_id != oraseas_org.id:
        raise HTTPException(status_code=403, detail="Only Oraseas can delete inventory records directly.")

    result = crud.inventory.delete_inventory_item(db, inventory_id)
    if not result:
        raise HTTPException(status_code=400, detail="Failed to delete inventory item")
    return result


@router.get("/worksheet/stocktake", response_model=List[schemas.StocktakeWorksheetItemResponse])
async def get_stocktake_worksheet(
    organization_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(has_roles(["Oraseas Admin", "Oraseas Inventory Manager"]))
):
    """
    Generate a stocktake worksheet for a specific organization.
    Lists parts with their current system stock levels.
    """
    # Validate organization_id
    organization = db.query(models.Organization).filter(models.Organization.id == organization_id).first()
    if not organization:
        raise HTTPException(status_code=404, detail="Organization not found")

    # Authorization: Oraseas Inventory Manager should only be able to generate for Oraseas EE.
    # Oraseas Admin can generate for any.
    if current_user.role == "Oraseas Inventory Manager":
        user_org = db.query(models.Organization).filter(models.Organization.id == current_user.organization_id).first()
        # Check if the inventory manager is part of Oraseas EE AND the request is for Oraseas EE.
        if not (user_org and user_org.name == "Oraseas EE" and organization.name == "Oraseas EE"):
            raise HTTPException(status_code=403, detail="Oraseas Inventory Manager can only generate worksheets for Oraseas EE.")

    # For Oraseas Admin, no additional check needed as they can access any org.

    worksheet_items = crud.inventory.get_stocktake_worksheet_items(db, organization_id=organization_id)
    if not worksheet_items:
        # It's not an error if there are no items, just return an empty list.
        # Client can decide how to present this (e.g., "No inventory items found for this organization").
        pass # Fall through to return empty list

    return worksheet_items
