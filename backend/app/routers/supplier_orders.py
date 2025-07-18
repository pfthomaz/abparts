# backend/app/routers/supplier_orders.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, selectinload
from typing import List

from .. import models, schemas, crud
from ..database import get_db
from ..auth import get_current_user, TokenData
from ..permissions import (
    ResourceType, PermissionType, require_permission,
    OrganizationScopedQueries, check_organization_access, permission_checker
)

router = APIRouter()

@router.post("/", response_model=schemas.SupplierOrderResponse, status_code=201)
def create_supplier_order(
    order: schemas.SupplierOrderCreate, 
    db: Session = Depends(get_db), 
    current_user: TokenData = Depends(require_permission(ResourceType.ORDER, PermissionType.WRITE))
):
    """Create a new supplier order with organization access control."""
    # Ensure user can only create orders for their own organization (unless super admin)
    if not permission_checker.is_super_admin(current_user):
        if hasattr(order, 'organization_id') and order.organization_id != current_user.organization_id:
            raise HTTPException(status_code=403, detail="Cannot create orders for other organizations")
    
    return crud.supplier_order.create(db=db, order=order)

@router.get("/", response_model=List[schemas.SupplierOrderResponse])
def read_supplier_orders(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db), 
    current_user: TokenData = Depends(require_permission(ResourceType.ORDER, PermissionType.READ))
):
    """
    Retrieves a list of supplier orders with organization-scoped filtering.
    """
    # Apply organization-scoped filtering
    query = db.query(models.SupplierOrder).options(
        selectinload(models.SupplierOrder.items).selectinload(models.SupplierOrderItem.part)
    )
    
    # Filter based on user permissions
    if not permission_checker.is_super_admin(current_user):
        # Users can see orders from their organization or orders placed with their organization as supplier
        query = query.filter(
            (models.SupplierOrder.customer_organization_id == current_user.organization_id) |
            (models.SupplierOrder.supplier_organization_id == current_user.organization_id)
        )
    
    orders = query.order_by(models.SupplierOrder.order_date.desc()).offset(skip).limit(limit).all()
    return orders