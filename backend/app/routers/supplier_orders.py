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
    # Only Oraseas EE users and super admins can create supplier orders
    if not permission_checker.is_super_admin(current_user):
        # Get user's organization to check type
        user_org = db.query(models.Organization).filter(models.Organization.id == current_user.organization_id).first()
        if not user_org or user_org.organization_type != models.OrganizationType.oraseas_ee:
            raise HTTPException(
                status_code=403, 
                detail="Only Oraseas EE users can create supplier orders"
            )
    
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
        # Users can see orders where their organization is the ordering organization
        query = query.filter(
            models.SupplierOrder.ordering_organization_id == current_user.organization_id
        )
    
    orders = query.order_by(models.SupplierOrder.order_date.desc()).offset(skip).limit(limit).all()
    
    # Convert to response format and populate part information
    response_orders = []
    for order in orders:
        order_dict = {
            "id": order.id,
            "ordering_organization_id": order.ordering_organization_id,
            "supplier_name": order.supplier_name,
            "order_date": order.order_date,
            "expected_delivery_date": order.expected_delivery_date,
            "actual_delivery_date": order.actual_delivery_date,
            "status": order.status,
            "notes": order.notes,
            "created_at": order.created_at,
            "updated_at": order.updated_at,
            "ordering_organization_name": None,  # This would need to be populated from a join
            "items": []
        }
        
        # Populate items with part information
        for item in order.items:
            item_dict = {
                "id": item.id,
                "supplier_order_id": item.supplier_order_id,
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