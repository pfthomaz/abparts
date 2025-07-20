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
    
    return crud.supplier_orders.create_supplier_order(db=db, order=order)

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

@router.put("/{order_id}", response_model=schemas.SupplierOrderResponse)
def update_supplier_order(
    order_id: str,
    order_update: schemas.SupplierOrderUpdate,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(require_permission(ResourceType.ORDER, PermissionType.WRITE))
):
    """Update a supplier order with organization access control."""
    # Get the existing order
    order = db.query(models.SupplierOrder).filter(models.SupplierOrder.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Supplier order not found")
    
    # Check permissions
    if not permission_checker.is_super_admin(current_user):
        # Users can only update orders from their organization
        if order.ordering_organization_id != current_user.organization_id:
            raise HTTPException(status_code=403, detail="Cannot update orders for other organizations")
    
    return crud.supplier_orders.update_supplier_order(db=db, order_id=order_id, order_update=order_update)

@router.get("/{order_id}", response_model=schemas.SupplierOrderResponse)
def get_supplier_order(
    order_id: str,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(require_permission(ResourceType.ORDER, PermissionType.READ))
):
    """Get a specific supplier order with organization access control."""
    order = db.query(models.SupplierOrder).options(
        selectinload(models.SupplierOrder.items).selectinload(models.SupplierOrderItem.part)
    ).filter(models.SupplierOrder.id == order_id).first()
    
    if not order:
        raise HTTPException(status_code=404, detail="Supplier order not found")
    
    # Check permissions
    if not permission_checker.is_super_admin(current_user):
        if (order.customer_organization_id != current_user.organization_id and 
            order.supplier_organization_id != current_user.organization_id):
            raise HTTPException(status_code=403, detail="Access denied to this order")
    
    return order