# backend/app/routers/supplier_orders.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, selectinload
from typing import List
from datetime import datetime
import logging

from .. import models, schemas, crud
from ..database import get_db
from ..auth import get_current_user, TokenData
from ..permissions import (
    ResourceType, PermissionType, require_permission, require_super_admin,
    OrganizationScopedQueries, check_organization_access, permission_checker
)

router = APIRouter()
logger = logging.getLogger(__name__)

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
    """Update a supplier order. Only admins can edit Pending orders."""
    # Only admins can update orders
    if not permission_checker.is_admin(current_user):
        raise HTTPException(status_code=403, detail="Only admins can edit orders")
    
    # Get the existing order
    order = db.query(models.SupplierOrder).filter(models.SupplierOrder.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Supplier order not found")
    
    # Store old status to detect transitions
    old_status = order.status
    
    # Only allow editing Pending orders (super_admins and fulfillment actions bypass this)
    if order.status != 'Pending' and not permission_checker.is_super_admin(current_user):
        # Allow transitioning Shipped → Delivered (fulfillment)
        if not (order.status == 'Shipped'):
            raise HTTPException(
                status_code=400, 
                detail=f"Cannot edit order with status '{order.status}'. Only orders in 'Pending' or 'Shipped' status can be edited."
            )
    
    # Check organization access for non-super-admins
    if not permission_checker.is_super_admin(current_user):
        # Admins can only update orders from their organization
        if order.ordering_organization_id != current_user.organization_id:
            raise HTTPException(status_code=403, detail="Cannot update orders for other organizations")
    
    # Extract receiving_warehouse_id before passing to CRUD (it's not a model field)
    receiving_warehouse_id = order_update.receiving_warehouse_id
    
    # Update the order via CRUD
    updated_order = crud.supplier_orders.update_supplier_order(db=db, order_id=order_id, order_update=order_update)
    
    # Check if status changed to Delivered or Received with a receiving warehouse
    new_status = order_update.status or old_status
    if (old_status not in ['Delivered', 'Received'] and new_status in ['Delivered', 'Received'] and receiving_warehouse_id):
        logger.info(f"Supplier order {order_id} marked as {new_status} - creating inventory transactions to warehouse {receiving_warehouse_id}")
        _create_inventory_on_supplier_delivery(db, order_id, receiving_warehouse_id, current_user.user_id)
    
    return updated_order


def _create_inventory_on_supplier_delivery(db: Session, order_id: str, receiving_warehouse_id, performed_by_user_id):
    """Create inventory transactions when a supplier order is delivered."""
    import uuid as uuid_module
    from decimal import Decimal
    
    try:
        # Get order items
        order_items = db.query(models.SupplierOrderItem).filter(
            models.SupplierOrderItem.supplier_order_id == order_id
        ).all()
        
        if not order_items:
            logger.warning(f"No items found for supplier order {order_id}")
            return
        
        for item in order_items:
            # Get part for unit_of_measure
            part = db.query(models.Part).filter(models.Part.id == item.part_id).first()
            if not part:
                logger.error(f"Part {item.part_id} not found for supplier order item")
                continue
            
            # Create a "creation" transaction to add parts to the receiving warehouse
            transaction = models.Transaction(
                transaction_type="creation",
                part_id=item.part_id,
                to_warehouse_id=receiving_warehouse_id,
                from_warehouse_id=None,
                customer_order_id=None,
                quantity=item.quantity,
                unit_of_measure=part.unit_of_measure or "units",
                performed_by_user_id=performed_by_user_id,
                transaction_date=datetime.utcnow(),
                notes=f"Supplier order delivery - Order ID: {order_id}",
                reference_number=f"SUP-{str(order_id)[:8]}"
            )
            db.add(transaction)
            logger.info(f"Created transaction for supplier order {order_id}, part {item.part_id}, qty {item.quantity}")
            
            # Ensure an inventory record exists for this part+warehouse combo
            # (so calculate_all_warehouse_stock can discover it)
            inventory = db.query(models.Inventory).filter(
                models.Inventory.part_id == item.part_id,
                models.Inventory.warehouse_id == receiving_warehouse_id
            ).first()
            
            if not inventory:
                inventory = models.Inventory(
                    part_id=item.part_id,
                    warehouse_id=receiving_warehouse_id,
                    current_stock=Decimal('0'),  # Will be recalculated
                    minimum_stock_recommendation=Decimal('0'),
                    unit_of_measure=part.unit_of_measure or "units"
                )
                db.add(inventory)
                logger.info(f"Created inventory record for part {item.part_id} in warehouse {receiving_warehouse_id}")
        
        db.commit()
        logger.info(f"Successfully created inventory transactions for supplier order {order_id}")
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating inventory for supplier order {order_id}: {e}")
        raise HTTPException(status_code=400, detail=f"Error updating inventory: {str(e)}")

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



@router.delete("/{order_id}", status_code=204)
def delete_supplier_order(
    order_id: str,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(require_permission(ResourceType.ORDER, PermissionType.DELETE))
):
    """Delete a supplier order. Only admins can delete orders."""
    # Only admins can delete orders
    if not permission_checker.is_admin(current_user):
        raise HTTPException(status_code=403, detail="Only admins can delete orders")
    
    # Get the existing order
    order = db.query(models.SupplierOrder).filter(models.SupplierOrder.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Supplier order not found")
    
    # Check organization access for non-super-admins
    if not permission_checker.is_super_admin(current_user):
        # Admins can only delete orders from their organization
        if order.ordering_organization_id != current_user.organization_id:
            raise HTTPException(status_code=403, detail="Cannot delete orders for other organizations")
    
    # Check if order can be deleted (only if not yet shipped/received)
    if order.status in ['Shipped', 'Received', 'Delivered']:
        raise HTTPException(
            status_code=400, 
            detail=f"Cannot delete order with status '{order.status}'. Only orders in 'Requested' or 'Pending' status can be deleted."
        )
    
    # Delete the order (cascade will delete items)
    db.delete(order)
    db.commit()
    
    return None
