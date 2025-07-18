# backend/app/routers/stock_adjustments.py

import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status, Path
from sqlalchemy.orm import Session

from .. import schemas, crud, models # Import schemas, CRUD functions, and models
from ..database import get_db # Import DB session dependency
from ..auth import get_current_user, TokenData # Import authentication dependencies
from ..permissions import (
    ResourceType, PermissionType, require_permission, require_admin,
    OrganizationScopedQueries, check_organization_access, permission_checker
)

router = APIRouter(
    prefix="/stock_adjustments", # Prefix for all routes in this router
    tags=["Stock Adjustments"] # Tag for OpenAPI documentation
)

# Endpoint to create a stock adjustment for a specific inventory item
@router.post("/inventory/{inventory_id}", response_model=schemas.StockAdjustmentResponse, status_code=status.HTTP_201_CREATED)
async def create_new_stock_adjustment(
    adjustment_in: schemas.StockAdjustmentCreate,
    inventory_id: uuid.UUID = Path(..., description="The ID of the inventory item to adjust"),
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(require_permission(ResourceType.INVENTORY, PermissionType.WRITE))
):
    """
    Create a new stock adjustment for a given inventory item.
    - **inventory_id**: UUID of the inventory item.
    - **adjustment_in**: Data for the stock adjustment.
    \f
    :param inventory_id: The ID of the inventory item.
    :param adjustment_in: The stock adjustment creation schema.
    :param db: Database session.
    :param current_user: Authenticated user data.
    :return: The created stock adjustment.
    """
    # Check if the inventory item belongs to an organization that Oraseas Admin/Manager can manage.
    # For simplicity, we assume Oraseas personnel can manage any inventory.
    # A more detailed check might involve ensuring the inventory's organization_id is Oraseas EE
    # or if they have specific permissions for other organizations.

    inventory_item = crud.inventory.get_inventory_item(db, inventory_id=inventory_id)
    if not inventory_item:
        raise HTTPException(status_code=404, detail=f"Inventory item with ID {inventory_id} not found.")

    # Check if user can adjust inventory for this warehouse using the permission system
    warehouse = inventory_item.warehouse if hasattr(inventory_item, 'warehouse') else None
    if warehouse and not permission_checker.can_adjust_inventory(current_user, warehouse.id, db):
        raise HTTPException(status_code=403, detail="Not authorized to adjust stock for this inventory item.")


    created_adjustment = crud.stock_adjustments.create_stock_adjustment(
        db=db,
        inventory_id=inventory_id,
        adjustment_in=adjustment_in,
        user_id=current_user.user_id
    )
    return created_adjustment

# Endpoint to get all adjustments for a specific inventory item
@router.get("/inventory/{inventory_id}", response_model=List[schemas.StockAdjustmentResponse])
async def list_adjustments_for_inventory_item(
    inventory_id: uuid.UUID = Path(..., description="The ID of the inventory item"),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(require_permission(ResourceType.INVENTORY, PermissionType.READ))
):
    """
    Get all stock adjustments for a specific inventory item with proper access control.
    """
    inventory_item = crud.inventory.get_inventory_item(db, inventory_id=inventory_id)
    if not inventory_item:
        raise HTTPException(status_code=404, detail=f"Inventory item with ID {inventory_id} not found.")

    # Check if user can access this inventory item's organization
    warehouse = inventory_item.warehouse if hasattr(inventory_item, 'warehouse') else None
    if warehouse and not check_organization_access(current_user, warehouse.organization_id, db):
        raise HTTPException(status_code=403, detail="Not authorized to view adjustments for this inventory item.")

    adjustments = crud.stock_adjustments.get_stock_adjustments_for_inventory_item(
        db=db, inventory_id=inventory_id, skip=skip, limit=limit
    )
    return adjustments

# Endpoint to get a specific stock adjustment by its ID
@router.get("/{adjustment_id}", response_model=schemas.StockAdjustmentResponse)
async def get_specific_stock_adjustment(
    adjustment_id: uuid.UUID = Path(..., description="The ID of the stock adjustment"),
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(require_permission(ResourceType.INVENTORY, PermissionType.READ))
):
    """
    Get a specific stock adjustment by its ID with proper access control.
    """
    adjustment = crud.stock_adjustments.get_stock_adjustment(db, adjustment_id=adjustment_id)
    if not adjustment:
        raise HTTPException(status_code=404, detail=f"Stock adjustment with ID {adjustment_id} not found.")

    # Authorization: User must be able to view the inventory item linked to the adjustment.
    inventory_item = crud.inventory.get_inventory_item(db, inventory_id=adjustment.inventory_id)
    if not inventory_item:
        raise HTTPException(status_code=404, detail="Associated inventory item not found.")

    # Check if user can access this inventory item's organization
    warehouse = inventory_item.warehouse if hasattr(inventory_item, 'warehouse') else None
    if warehouse and not check_organization_access(current_user, warehouse.organization_id, db):
        raise HTTPException(status_code=403, detail="Not authorized to view this stock adjustment.")

    return adjustment

# Endpoint for super admins to see ALL stock adjustments (for audit purposes)
@router.get("/", response_model=List[schemas.StockAdjustmentResponse])
async def list_all_stock_adjustments(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(require_permission(ResourceType.AUDIT_LOG, PermissionType.READ))
):
    """
    Get all stock adjustments across the system with organization-scoped filtering.
    Super admins see all adjustments, regular users see only their organization's adjustments.
    """
    # Apply organization-scoped filtering for audit logs
    if permission_checker.is_super_admin(current_user):
        adjustments = crud.stock_adjustments.get_all_stock_adjustments(db=db, skip=skip, limit=limit)
    else:
        # For non-super admins, filter to their organization's adjustments only
        adjustments = crud.stock_adjustments.get_stock_adjustments_by_organization(
            db=db, organization_id=current_user.organization_id, skip=skip, limit=limit
        )
    return adjustments
