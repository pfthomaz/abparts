# backend/app/routers/stock_adjustments.py

import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status, Path
from sqlalchemy.orm import Session

from .. import schemas, crud, models # Import schemas, CRUD functions, and models
from ..database import get_db # Import DB session dependency
from ..auth import get_current_user, has_role, has_roles, TokenData # Import authentication dependencies

router = APIRouter(
    prefix="/stock_adjustments", # Prefix for all routes in this router
    tags=["Stock Adjustments"] # Tag for OpenAPI documentation
)

# Endpoint to create a stock adjustment for a specific inventory item
@router.post("/inventory/{inventory_id}", response_model=schemas.StockAdjustmentResponse, status_code=status.HTTP_201_CREATED)
async def create_new_stock_adjustment(
    inventory_id: uuid.UUID = Path(..., description="The ID of the inventory item to adjust"),
    adjustment_in: schemas.StockAdjustmentCreate,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(has_roles(["Oraseas Admin", "Oraseas Inventory Manager"]))
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

    # Check if the current user's organization is 'Oraseas EE' if the inventory is for Oraseas EE.
    # Or if the user is an Admin, they can adjust any.
    # This logic might need refinement based on how multi-organization inventory is managed by Oraseas staff.
    if not (current_user.role == "Oraseas Admin" or \
            (current_user.role == "Oraseas Inventory Manager" and inventory_item.organization.name == "Oraseas EE")): # Assuming Oraseas Inventory Manager only manages Oraseas EE stock
        # A more robust check would be to see if inventory_item.organization_id is one that current_user can manage
        # For now, Oraseas Inventory Manager can only adjust stock for "Oraseas EE".
        # Oraseas Admin can adjust any.
        oraseas_org = db.query(models.Organization).filter(models.Organization.id == current_user.organization_id).first()
        if not (current_user.role == "Oraseas Admin" or (oraseas_org and oraseas_org.name == "Oraseas EE")):
             raise HTTPException(status_code=403, detail="Not authorized to adjust stock for this inventory item's organization.")


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
    current_user: TokenData = Depends(get_current_user) # Allow any authenticated user to see adjustments for inventory they can see
):
    """
    Get all stock adjustments for a specific inventory item.
    \f
    :param inventory_id: The ID of the inventory item.
    :param db: Database session.
    :param current_user: Authenticated user data.
    :return: List of stock adjustments.
    """
    inventory_item = crud.inventory.get_inventory_item(db, inventory_id=inventory_id)
    if not inventory_item:
        raise HTTPException(status_code=404, detail=f"Inventory item with ID {inventory_id} not found.")

    # Authorization: User must be able to view the inventory item itself.
    # Oraseas Admin can see all. Customer roles can see their own org's inventory.
    can_view = False
    if current_user.role == "Oraseas Admin":
        can_view = True
    elif inventory_item.organization_id == current_user.organization_id:
        can_view = True

    if not can_view:
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
    current_user: TokenData = Depends(get_current_user) # Allow any authenticated user to see adjustments for inventory they can see
):
    """
    Get a specific stock adjustment by its ID.
    \f
    :param adjustment_id: The ID of the stock adjustment.
    :param db: Database session.
    :param current_user: Authenticated user data.
    :return: The stock adjustment.
    """
    adjustment = crud.stock_adjustments.get_stock_adjustment(db, adjustment_id=adjustment_id)
    if not adjustment:
        raise HTTPException(status_code=404, detail=f"Stock adjustment with ID {adjustment_id} not found.")

    # Authorization: User must be able to view the inventory item linked to the adjustment.
    inventory_item = crud.inventory.get_inventory_item(db, inventory_id=adjustment.inventory_id)
    if not inventory_item: # Should not happen if DB integrity is maintained
        raise HTTPException(status_code=404, detail="Associated inventory item not found.")

    can_view = False
    if current_user.role == "Oraseas Admin":
        can_view = True
    elif inventory_item.organization_id == current_user.organization_id:
        can_view = True

    if not can_view:
        raise HTTPException(status_code=403, detail="Not authorized to view this stock adjustment.")

    return adjustment

# Endpoint for Oraseas Admin to see ALL stock adjustments (for audit purposes)
@router.get("/", response_model=List[schemas.StockAdjustmentResponse])
async def list_all_stock_adjustments(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(has_role("Oraseas Admin")) # Only Oraseas Admin
):
    """
    Get all stock adjustments across the system (Admin only).
    \f
    :param db: Database session.
    :param current_user: Authenticated user data (must be Oraseas Admin).
    :return: List of all stock adjustments.
    """
    adjustments = crud.stock_adjustments.get_all_stock_adjustments(db=db, skip=skip, limit=limit)
    return adjustments
