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
        selectinload(models.CustomerOrder.ordered_by_user),
        selectinload(models.CustomerOrder.shipped_by_user)
    )
    
    # Filter based on user permissions and organization type
    if not permission_checker.is_super_admin(current_user):
        # Get the user's organization to check its type
        user_org = db.query(models.Organization).filter(models.Organization.id == current_user.organization_id).first()
        
        if user_org and user_org.name in ['Oraseas EE', 'BossServ LLC', 'BossServ Ltd']:
            # Oraseas EE users see orders placed TO them (where they are the receiver)
            query = query.filter(models.CustomerOrder.oraseas_organization_id == current_user.organization_id)
        else:
            # Customer organizations see orders placed BY them (where they are the customer)
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
            "shipped_date": order.shipped_date,
            "shipped_by_user_id": order.shipped_by_user_id,
            "actual_delivery_date": order.actual_delivery_date,
            "status": order.status,
            "ordered_by_user_id": order.ordered_by_user_id,
            "notes": order.notes,
            "created_at": order.created_at,
            "updated_at": order.updated_at,
            # Populate flat fields from relationships
            "customer_organization_name": order.customer_organization.name if order.customer_organization else None,
            "oraseas_organization_name": order.oraseas_organization.name if order.oraseas_organization else None,
            "ordered_by_username": order.ordered_by_user.name if order.ordered_by_user and order.ordered_by_user.name else (order.ordered_by_user.username if order.ordered_by_user else None),
            "shipped_by_username": order.shipped_by_user.name if order.shipped_by_user and order.shipped_by_user.name else (order.shipped_by_user.username if order.shipped_by_user else None),
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
        # Get the user's organization to check its type
        user_org = db.query(models.Organization).filter(models.Organization.id == current_user.organization_id).first()
        
        # Users can update orders if they are either:
        # 1. The customer organization (who placed the order)
        # 2. The Oraseas EE organization (who receives the order)
        is_customer = order.customer_organization_id == current_user.organization_id
        is_oraseas = order.oraseas_organization_id == current_user.organization_id
        
        if not (is_customer or is_oraseas):
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


@router.patch("/{order_id}/ship", response_model=schemas.CustomerOrderResponse)
def ship_customer_order(
    order_id: str,
    ship_request: schemas.CustomerOrderShipRequest,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(require_permission(ResourceType.ORDER, PermissionType.WRITE))
):
    """
    Mark a customer order as shipped (Oraseas EE only).
    Updates status to 'Shipped' and records the shipped_date.
    """
    # Get the order
    order = db.query(models.CustomerOrder).filter(models.CustomerOrder.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Customer order not found")
    
    # Verify user is from Oraseas EE organization
    user_org = db.query(models.Organization).filter(models.Organization.id == current_user.organization_id).first()
    if not user_org:
        raise HTTPException(status_code=404, detail="User organization not found")
    
    # Check if user is from Oraseas EE (or super admin)
    is_oraseas_ee = user_org.name in ['Oraseas EE', 'BossServ LLC', 'BossServ Ltd']
    if not permission_checker.is_super_admin(current_user) and not is_oraseas_ee:
        raise HTTPException(status_code=403, detail="Only Oraseas EE can mark orders as shipped")
    
    # Verify order is in correct status
    if order.status not in ['Requested', 'Pending']:
        raise HTTPException(status_code=400, detail=f"Cannot ship order with status '{order.status}'")
    
    # Update order
    order.status = 'Shipped'
    order.shipped_date = ship_request.shipped_date
    order.shipped_by_user_id = current_user.user_id  # Record who shipped the order
    if ship_request.notes:
        order.notes = f"{order.notes}\n\nShipped: {ship_request.notes}" if order.notes else f"Shipped: {ship_request.notes}"
    
    db.commit()
    db.refresh(order)
    
    return order


@router.patch("/{order_id}/confirm-receipt", response_model=schemas.CustomerOrderResponse)
def confirm_order_receipt(
    order_id: str,
    receipt_request: schemas.CustomerOrderConfirmReceiptRequest,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(require_permission(ResourceType.ORDER, PermissionType.WRITE))
):
    """
    Confirm receipt of a customer order (Customer organization only).
    Updates status to 'Received' and records the actual_delivery_date.
    """
    # Get the order
    order = db.query(models.CustomerOrder).filter(models.CustomerOrder.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Customer order not found")
    
    # Verify user is from the customer organization that placed the order
    if not permission_checker.is_super_admin(current_user):
        if order.customer_organization_id != current_user.organization_id:
            raise HTTPException(status_code=403, detail="Only the ordering organization can confirm receipt")
    
    # Verify order is in correct status
    if order.status != 'Shipped':
        raise HTTPException(status_code=400, detail=f"Cannot confirm receipt for order with status '{order.status}'")
    
    # Verify warehouse belongs to customer organization
    warehouse = db.query(models.Warehouse).filter(models.Warehouse.id == receipt_request.receiving_warehouse_id).first()
    if not warehouse:
        raise HTTPException(status_code=404, detail="Warehouse not found")
    
    if warehouse.organization_id != order.customer_organization_id:
        raise HTTPException(status_code=400, detail="Warehouse must belong to the customer organization")
    
    # Update order
    order.status = 'Received'
    order.actual_delivery_date = receipt_request.actual_delivery_date
    if receipt_request.notes:
        order.notes = f"{order.notes}\n\nReceived: {receipt_request.notes}" if order.notes else f"Received: {receipt_request.notes}"
    
    # TODO: Update inventory in the receiving warehouse
    # This would involve creating inventory transactions for each order item
    
    db.commit()
    db.refresh(order)
    
    return order