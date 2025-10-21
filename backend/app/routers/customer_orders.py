# backend/app/routers/customer_orders.py

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

@router.post("/", response_model=schemas.CustomerOrderResponse, status_code=201)
def create_customer_order(
    order: schemas.CustomerOrderCreate, 
    db: Session = Depends(get_db), 
    current_user: TokenData = Depends(require_permission(ResourceType.ORDER, PermissionType.WRITE))
):
    """Create a new customer order with organization access control."""
    # Ensure user can only create orders for their own organization (unless super admin)
    if not permission_checker.is_super_admin(current_user):
        if hasattr(order, 'customer_organization_id') and order.customer_organization_id != current_user.organization_id:
            raise HTTPException(status_code=403, detail="Cannot create orders for other organizations")
    
    return crud.customer_orders.create_customer_order(db=db, order=order)

@router.get("/", response_model=List[schemas.CustomerOrderResponse])
def read_customer_orders(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db), 
    current_user: TokenData = Depends(require_permission(ResourceType.ORDER, PermissionType.READ))
):
    """
    Retrieves a list of customer orders with organization-scoped filtering.
    """
    # Apply organization-scoped filtering
    query = db.query(models.CustomerOrder).options(
        selectinload(models.CustomerOrder.items).selectinload(models.CustomerOrderItem.part),
        selectinload(models.CustomerOrder.customer_organization),
        selectinload(models.CustomerOrder.oraseas_organization),
        selectinload(models.CustomerOrder.ordered_by_user)
    )
    
    # Filter based on user permissions
    if not permission_checker.is_super_admin(current_user):
        query = query.filter(models.CustomerOrder.customer_organization_id == current_user.organization_id)
    
    orders = query.order_by(models.CustomerOrder.order_date.desc()).offset(skip).limit(limit).all()
    
    # Convert to response format with populated flat fields
    response_orders = []
    for order in orders:
        # Create a dict from the order
        order_dict = {
            "id": order.id,
            "customer_organization_id": order.customer_organization_id,
            "oraseas_organization_id": order.oraseas_organization_id,
            "order_date": order.order_date,
            "expected_delivery_date": order.expected_delivery_date,
            "actual_delivery_date": order.actual_delivery_date,
            "status": order.status,
            "ordered_by_user_id": order.ordered_by_user_id,
            "notes": order.notes,
            "created_at": order.created_at,
            "updated_at": order.updated_at,
            # Populate flat fields from relationships
            "customer_organization_name": order.customer_organization.name if order.customer_organization else None,
            "oraseas_organization_name": order.oraseas_organization.name if order.oraseas_organization else None,
            "ordered_by_username": order.ordered_by_user.username if order.ordered_by_user else None,
            "items": []
        }
        
        # Populate items with part information
        for item in order.items:
            item_dict = {
                "id": item.id,
                "customer_order_id": item.customer_order_id,
                "part_id": item.part_id,
                "quantity": item.quantity,
                "unit_price": item.unit_price,
                "created_at": item.created_at,
                "updated_at": item.updated_at,
                "part_number": item.part.part_number if item.part else None,
                "part_name": item.part.name if item.part else None,
                "unit_of_measure": item.part.unit_of_measure if item.part else None
            }
            order_dict["items"].append(item_dict)
        
        response_orders.append(order_dict)
    
    return response_orders

@router.put("/{order_id}", response_model=schemas.CustomerOrderResponse)
def update_customer_order(
    order_id: str,
    order_update: schemas.CustomerOrderUpdate,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(require_permission(ResourceType.ORDER, PermissionType.WRITE))
):
    """Update a customer order with organization access control."""
    # Get the existing order
    order = db.query(models.CustomerOrder).filter(models.CustomerOrder.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Customer order not found")
    
    # Check permissions
    if not permission_checker.is_super_admin(current_user):
        # Users can only update orders from their organization
        if order.customer_organization_id != current_user.organization_id:
            raise HTTPException(status_code=403, detail="Cannot update orders for other organizations")
    
    return crud.customer_orders.update_customer_order(db=db, order_id=order_id, order_update=order_update, current_user_id=current_user.user_id)

@router.get("/{order_id}", response_model=schemas.CustomerOrderResponse)
def get_customer_order(
    order_id: str,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(require_permission(ResourceType.ORDER, PermissionType.READ))
):
    """Get a specific customer order with organization access control."""
    order = db.query(models.CustomerOrder).options(
        selectinload(models.CustomerOrder.items).selectinload(models.CustomerOrderItem.part),
        selectinload(models.CustomerOrder.customer_organization)
    ).filter(models.CustomerOrder.id == order_id).first()
    
    if not order:
        raise HTTPException(status_code=404, detail="Customer order not found")
    
    # Check permissions
    if not permission_checker.is_super_admin(current_user):
        if order.customer_organization_id != current_user.organization_id:
            raise HTTPException(status_code=403, detail="Access denied to this order")
    
    return order