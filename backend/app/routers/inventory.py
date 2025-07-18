# backend/app/routers/inventory.py

import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from .. import schemas, crud, models # Import schemas, CRUD functions, and models
from ..database import get_db # Import DB session dependency
from ..auth import get_current_user, TokenData # Import authentication dependencies
from ..permissions import (
    ResourceType, PermissionType, require_permission, require_admin,
    OrganizationScopedQueries, check_organization_access, permission_checker
)

router = APIRouter()

# --- Helper Functions ---
def check_warehouse_access(user: TokenData, warehouse_id: uuid.UUID, db: Session) -> bool:
    """Check if user can access a specific warehouse."""
    if permission_checker.is_super_admin(user):
        return True
    
    warehouse = db.query(models.Warehouse).filter(models.Warehouse.id == warehouse_id).first()
    if not warehouse:
        return False
    
    return warehouse.organization_id == user.organization_id

# --- Inventory CRUD ---
@router.get("/", response_model=List[schemas.InventoryResponse])
async def get_inventory_items(
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)
):
    # Apply organization-scoped filtering based on user role
    if current_user.role == "super_admin":
        inventory_items = crud.inventory.get_inventory_items(db)
    else:
        # Regular users can only see inventory from their organization's warehouses
        inventory_items = crud.inventory.get_inventory_by_organization(db, current_user.organization_id)
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

    # Check if user can access this inventory item's warehouse
    if current_user.role != "super_admin":
        # Get warehouse to check organization
        warehouse = db.query(models.Warehouse).filter(models.Warehouse.id == inventory_item.warehouse_id).first()
        if not warehouse or warehouse.organization_id != current_user.organization_id:
            raise HTTPException(status_code=403, detail="Not authorized to view this inventory item")
    
    return inventory_item

@router.post("/", response_model=schemas.InventoryResponse, status_code=status.HTTP_201_CREATED)
async def create_inventory_item(
    item: schemas.InventoryCreate,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(require_permission(ResourceType.INVENTORY, PermissionType.WRITE))
):
    # Check if user can access the warehouse for this inventory item
    if current_user.role != "super_admin":
        warehouse = db.query(models.Warehouse).filter(models.Warehouse.id == item.warehouse_id).first()
        if not warehouse or warehouse.organization_id != current_user.organization_id:
            raise HTTPException(status_code=403, detail="Not authorized to create inventory in this warehouse")

    db_item = crud.inventory.create_inventory_item(db, item)
    if not db_item:
        raise HTTPException(status_code=400, detail="Failed to create inventory item")
    return db_item

@router.put("/{inventory_id}", response_model=schemas.InventoryResponse)
async def update_inventory_item(
    inventory_id: uuid.UUID,
    item_update: schemas.InventoryUpdate,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(require_permission(ResourceType.INVENTORY, PermissionType.WRITE))
):
    db_item = crud.inventory.get_inventory_item(db, inventory_id)
    if not db_item:
        raise HTTPException(status_code=404, detail="Inventory item not found")

    # Check if user can access this inventory item's warehouse
    if current_user.role != "super_admin":
        warehouse = db.query(models.Warehouse).filter(models.Warehouse.id == db_item.warehouse_id).first()
        if not warehouse or warehouse.organization_id != current_user.organization_id:
            raise HTTPException(status_code=403, detail="Not authorized to update this inventory item")

    updated_item = crud.inventory.update_inventory_item(db, inventory_id, item_update)
    if not updated_item:
        raise HTTPException(status_code=400, detail="Failed to update inventory item")
    return updated_item


@router.delete("/{inventory_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_inventory_item(
    inventory_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(require_permission(ResourceType.INVENTORY, PermissionType.DELETE))
):
    db_item = crud.inventory.get_inventory_item(db, inventory_id)
    if not db_item:
        raise HTTPException(status_code=404, detail="Inventory item not found")

    # Check if user can access this inventory item's warehouse
    if current_user.role != "super_admin":
        warehouse = db.query(models.Warehouse).filter(models.Warehouse.id == db_item.warehouse_id).first()
        if not warehouse or warehouse.organization_id != current_user.organization_id:
            raise HTTPException(status_code=403, detail="Not authorized to delete this inventory item")

    result = crud.inventory.delete_inventory_item(db, inventory_id)
    if not result:
        raise HTTPException(status_code=400, detail="Failed to delete inventory item")
    return result


@router.get("/worksheet/stocktake", response_model=List[schemas.StocktakeWorksheetItemResponse])
async def get_stocktake_worksheet(
    organization_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)
):
    """
    Generate a stocktake worksheet for a specific organization.
    Lists parts with their current system stock levels across all warehouses.
    """
    # Validate organization_id
    organization = db.query(models.Organization).filter(models.Organization.id == organization_id).first()
    if not organization:
        raise HTTPException(status_code=404, detail="Organization not found")

    # Check if user can access this organization
    if current_user.role != "super_admin" and organization_id != current_user.organization_id:
        raise HTTPException(status_code=403, detail="Not authorized to generate stocktake worksheet for this organization")

    worksheet_items = crud.inventory.get_stocktake_worksheet_items(db, organization_id=organization_id)
    if not worksheet_items:
        # It's not an error if there are no items, just return an empty list.
        # Client can decide how to present this (e.g., "No inventory items found for this organization").
        pass # Fall through to return empty list

    return worksheet_items


# --- Warehouse-based inventory endpoints ---

@router.get("/warehouse/{warehouse_id}", response_model=List[schemas.InventoryResponse])
async def get_warehouse_inventory(
    warehouse_id: uuid.UUID,
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)
):
    """Get all inventory items for a specific warehouse."""
    # Check if user can access this warehouse
    if current_user.role != "super_admin":
        warehouse = db.query(models.Warehouse).filter(models.Warehouse.id == warehouse_id).first()
        if not warehouse or warehouse.organization_id != current_user.organization_id:
            raise HTTPException(status_code=403, detail="Not authorized to view this warehouse's inventory")
    
    inventory_items = crud.inventory.get_inventory_by_warehouse(db, warehouse_id, skip, limit)
    return inventory_items


@router.get("/organization/{organization_id}/aggregated")
async def get_organization_inventory_aggregated(
    organization_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)
):
    """Get inventory aggregated by part across all warehouses for an organization."""
    # Check if user can access this organization
    if current_user.role != "super_admin" and organization_id != current_user.organization_id:
        raise HTTPException(status_code=403, detail="Not authorized to view this organization's inventory")
    
    aggregated_inventory = crud.inventory.get_inventory_aggregation_by_organization(db, organization_id)
    return {
        "organization_id": str(organization_id),
        "inventory_summary": aggregated_inventory,
        "total_parts": len(aggregated_inventory),
        "low_stock_parts": sum(1 for item in aggregated_inventory if item['is_low_stock'])
    }


@router.get("/organization/{organization_id}/by-warehouse", response_model=List[schemas.InventoryResponse])
async def get_organization_inventory_by_warehouse(
    organization_id: uuid.UUID,
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)
):
    """Get all inventory items for an organization across all its warehouses."""
    # Check if user can access this organization
    if current_user.role != "super_admin" and organization_id != current_user.organization_id:
        raise HTTPException(status_code=403, detail="Not authorized to view this organization's inventory")
    
    inventory_items = crud.inventory.get_inventory_by_organization(db, organization_id, skip, limit)
    return inventory_items


@router.post("/transfer")
async def transfer_inventory_between_warehouses(
    transfer_request: schemas.InventoryTransferRequest,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(require_permission(ResourceType.INVENTORY, PermissionType.WRITE))
):
    """Transfer inventory between warehouses."""
    # Check if user can access both warehouses
    if not check_warehouse_access(current_user, transfer_request.from_warehouse_id, db):
        raise HTTPException(status_code=403, detail="Not authorized to transfer from this warehouse")
    
    if not check_warehouse_access(current_user, transfer_request.to_warehouse_id, db):
        raise HTTPException(status_code=403, detail="Not authorized to transfer to this warehouse")
    
    try:
        success = crud.inventory.transfer_inventory_between_warehouses(
            db=db,
            from_warehouse_id=transfer_request.from_warehouse_id,
            to_warehouse_id=transfer_request.to_warehouse_id,
            part_id=transfer_request.part_id,
            quantity=transfer_request.quantity,
            performed_by_user_id=current_user.user_id
        )
        
        if success:
            return {
                "message": "Inventory transfer completed successfully",
                "from_warehouse_id": str(transfer_request.from_warehouse_id),
                "to_warehouse_id": str(transfer_request.to_warehouse_id),
                "part_id": str(transfer_request.part_id),
                "quantity": transfer_request.quantity
            }
        else:
            raise HTTPException(status_code=400, detail="Failed to transfer inventory")
            
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/warehouse/{warehouse_id}/balance-calculations")
async def get_warehouse_inventory_balance_calculations(
    warehouse_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(require_permission(ResourceType.INVENTORY, PermissionType.READ))
):
    """Get inventory balance calculations based on transactions for a warehouse."""
    # Check if user can access this warehouse
    if not check_warehouse_access(current_user, warehouse_id, db):
        raise HTTPException(status_code=403, detail="Not authorized to view this warehouse's balance calculations")
    
    balance_calculations = crud.inventory.get_inventory_balance_calculations(db, warehouse_id)
    return {
        "warehouse_id": str(warehouse_id),
        "balance_calculations": balance_calculations,
        "total_parts": len(balance_calculations)
    }
