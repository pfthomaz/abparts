# backend/app/crud/part_order.py

import uuid
import logging
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from decimal import Decimal

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc
from fastapi import HTTPException, status

from .. import models, schemas

logger = logging.getLogger(__name__)

def generate_order_number(db: Session) -> str:
    """Generate a unique order number."""
    # Get the current date
    today = datetime.now()
    date_prefix = today.strftime("%Y%m%d")
    
    # Count orders created today
    today_start = today.replace(hour=0, minute=0, second=0, microsecond=0)
    today_end = today_start + timedelta(days=1)
    
    count = db.query(models.PartOrderRequest).filter(
        models.PartOrderRequest.created_at >= today_start,
        models.PartOrderRequest.created_at < today_end
    ).count()
    
    # Generate order number: YYYYMMDD-NNNN
    order_number = f"{date_prefix}-{count + 1:04d}"
    
    # Ensure uniqueness
    while db.query(models.PartOrderRequest).filter(models.PartOrderRequest.order_number == order_number).first():
        count += 1
        order_number = f"{date_prefix}-{count + 1:04d}"
    
    return order_number

# Part Order Request CRUD
def get_part_order_request(db: Session, order_id: uuid.UUID):
    """Get a part order request by ID with related data."""
    order = db.query(
        models.PartOrderRequest,
        models.Organization.name.label("customer_organization_name"),
        models.User.username.label("requested_by_username")
    ).join(
        models.Organization, models.PartOrderRequest.customer_organization_id == models.Organization.id
    ).join(
        models.User, models.PartOrderRequest.requested_by_user_id == models.User.id
    ).filter(
        models.PartOrderRequest.id == order_id
    ).first()
    
    if not order:
        return None
    
    order_obj, customer_organization_name, requested_by_username = order
    
    # Get approved by username if exists
    approved_by_username = None
    if order_obj.approved_by_user_id:
        approved_user = db.query(models.User).filter(models.User.id == order_obj.approved_by_user_id).first()
        approved_by_username = approved_user.username if approved_user else None
    
    # Get received by username if exists
    received_by_username = None
    if order_obj.received_by_user_id:
        received_user = db.query(models.User).filter(models.User.id == order_obj.received_by_user_id).first()
        received_by_username = received_user.username if received_user else None
    
    # Get order items
    items = get_order_items(db, order_id)
    
    # Calculate totals
    total_items = len(items)
    total_value = sum(item.get("unit_price", 0) * item.get("quantity", 0) for item in items if item.get("unit_price"))
    
    result = {
        **order_obj.__dict__,
        "customer_organization_name": customer_organization_name,
        "requested_by_username": requested_by_username,
        "approved_by_username": approved_by_username,
        "received_by_username": received_by_username,
        "total_items": total_items,
        "total_value": total_value,
        "items": items
    }
    
    return result

def get_part_order_requests(db: Session, customer_organization_id: Optional[uuid.UUID] = None,
                           status: Optional[str] = None, priority: Optional[str] = None,
                           supplier_type: Optional[str] = None, skip: int = 0, limit: int = 100):
    """Get part order requests with optional filtering."""
    query = db.query(
        models.PartOrderRequest,
        models.Organization.name.label("customer_organization_name"),
        models.User.username.label("requested_by_username")
    ).join(
        models.Organization, models.PartOrderRequest.customer_organization_id == models.Organization.id
    ).join(
        models.User, models.PartOrderRequest.requested_by_user_id == models.User.id
    )
    
    if customer_organization_id:
        query = query.filter(models.PartOrderRequest.customer_organization_id == customer_organization_id)
    
    if status:
        query = query.filter(models.PartOrderRequest.status == status)
    
    if priority:
        query = query.filter(models.PartOrderRequest.priority == priority)
    
    if supplier_type:
        query = query.filter(models.PartOrderRequest.supplier_type == supplier_type)
    
    orders = query.order_by(models.PartOrderRequest.created_at.desc()).offset(skip).limit(limit).all()
    
    results = []
    for order, customer_organization_name, requested_by_username in orders:
        # Get basic item count and total value
        items_count = db.query(models.PartOrderItem).filter(models.PartOrderItem.order_request_id == order.id).count()
        
        total_value_query = db.query(
            func.sum(models.PartOrderItem.quantity * models.PartOrderItem.unit_price)
        ).filter(
            models.PartOrderItem.order_request_id == order.id,
            models.PartOrderItem.unit_price.isnot(None)
        ).scalar()
        
        total_value = total_value_query or 0
        
        result = {
            **order.__dict__,
            "customer_organization_name": customer_organization_name,
            "requested_by_username": requested_by_username,
            "total_items": items_count,
            "total_value": total_value,
            "items": []  # Don't load items for list view for performance
        }
        
        results.append(result)
    
    return results

def create_part_order_request(db: Session, order: schemas.PartOrderRequestCreate, current_user_id: uuid.UUID):
    """Create a new part order request."""
    # Check if customer organization exists
    customer_org = db.query(models.Organization).filter(models.Organization.id == order.customer_organization_id).first()
    if not customer_org:
        raise HTTPException(status_code=404, detail="Customer organization not found")
    
    # If supplier is Oraseas EE, validate supplier organization
    if order.supplier_type == models.SupplierType.ORASEAS_EE:
        if not order.supplier_organization_id:
            # Find Oraseas EE organization
            oraseas_org = db.query(models.Organization).filter(
                models.Organization.organization_type == models.OrganizationType.ORASEAS_EE
            ).first()
            if not oraseas_org:
                raise HTTPException(status_code=400, detail="Oraseas EE organization not found")
            order.supplier_organization_id = oraseas_org.id
        else:
            supplier_org = db.query(models.Organization).filter(models.Organization.id == order.supplier_organization_id).first()
            if not supplier_org:
                raise HTTPException(status_code=404, detail="Supplier organization not found")
    
    # Generate order number
    order_number = generate_order_number(db)
    
    # Set requested by user if not provided
    if not order.requested_by_user_id:
        order.requested_by_user_id = current_user_id
    
    # Create the order request
    db_order = models.PartOrderRequest(
        order_number=order_number,
        **order.dict()
    )
    
    try:
        db.add(db_order)
        db.commit()
        db.refresh(db_order)
        
        # Get the order with related data
        result = get_part_order_request(db, db_order.id)
        return result
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating part order request: {e}")
        raise HTTPException(status_code=500, detail=f"Error creating part order request: {str(e)}")

def update_part_order_request(db: Session, order_id: uuid.UUID, order_update: schemas.PartOrderRequestUpdate):
    """Update a part order request."""
    db_order = db.query(models.PartOrderRequest).filter(models.PartOrderRequest.id == order_id).first()
    if not db_order:
        return None
    
    update_data = order_update.dict(exclude_unset=True)
    
    # Validate supplier organization if being updated
    if "supplier_organization_id" in update_data and update_data["supplier_organization_id"]:
        supplier_org = db.query(models.Organization).filter(
            models.Organization.id == update_data["supplier_organization_id"]
        ).first()
        if not supplier_org:
            raise HTTPException(status_code=404, detail="Supplier organization not found")
    
    for key, value in update_data.items():
        setattr(db_order, key, value)
    
    try:
        db.add(db_order)
        db.commit()
        db.refresh(db_order)
        
        # Get the order with related data
        result = get_part_order_request(db, db_order.id)
        return result
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating part order request: {e}")
        raise HTTPException(status_code=500, detail=f"Error updating part order request: {str(e)}")

def delete_part_order_request(db: Session, order_id: uuid.UUID):
    """Delete a part order request."""
    db_order = db.query(models.PartOrderRequest).filter(models.PartOrderRequest.id == order_id).first()
    if not db_order:
        return None
    
    # Check if order can be deleted (only if status is REQUESTED or CANCELLED)
    if db_order.status not in [models.OrderStatus.REQUESTED, models.OrderStatus.CANCELLED]:
        raise HTTPException(
            status_code=400, 
            detail="Cannot delete order that has been approved or is in progress"
        )
    
    try:
        # Delete order items first
        db.query(models.PartOrderItem).filter(models.PartOrderItem.order_request_id == order_id).delete()
        
        # Delete approvals
        db.query(models.OrderApproval).filter(models.OrderApproval.order_request_id == order_id).delete()
        
        # Delete order transactions
        db.query(models.OrderTransaction).filter(models.OrderTransaction.order_request_id == order_id).delete()
        
        # Delete the order
        db.delete(db_order)
        db.commit()
        return {"message": "Part order request deleted successfully"}
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting part order request: {e}")
        raise HTTPException(status_code=500, detail=f"Error deleting part order request: {str(e)}")

# Part Order Item CRUD
def get_order_items(db: Session, order_id: uuid.UUID):
    """Get all items for a specific order."""
    items = db.query(
        models.PartOrderItem,
        models.Part.part_number.label("part_number"),
        models.Part.name.label("part_name"),
        models.Part.part_type.label("part_type"),
        models.Part.unit_of_measure.label("unit_of_measure"),
        models.Part.is_proprietary.label("is_proprietary"),
        models.Warehouse.name.label("warehouse_name")
    ).join(
        models.Part, models.PartOrderItem.part_id == models.Part.id
    ).join(
        models.Warehouse, models.PartOrderItem.destination_warehouse_id == models.Warehouse.id
    ).filter(
        models.PartOrderItem.order_request_id == order_id
    ).all()
    
    results = []
    for item, part_number, part_name, part_type, unit_of_measure, is_proprietary, warehouse_name in items:
        result = {
            **item.__dict__,
            "part_number": part_number,
            "part_name": part_name,
            "part_type": part_type,
            "unit_of_measure": unit_of_measure,
            "is_proprietary": is_proprietary,
            "warehouse_name": warehouse_name
        }
        results.append(result)
    
    return results

def add_order_item(db: Session, item: schemas.PartOrderItemCreate):
    """Add an item to a part order request."""
    # Check if order exists
    order = db.query(models.PartOrderRequest).filter(models.PartOrderRequest.id == item.order_request_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Part order request not found")
    
    # Check if order can be modified (only if status is REQUESTED)
    if order.status != models.OrderStatus.REQUESTED:
        raise HTTPException(status_code=400, detail="Cannot modify order that has been approved or is in progress")
    
    # Check if part exists
    part = db.query(models.Part).filter(models.Part.id == item.part_id).first()
    if not part:
        raise HTTPException(status_code=404, detail="Part not found")
    
    # Check if warehouse exists and belongs to the customer organization
    warehouse = db.query(models.Warehouse).filter(models.Warehouse.id == item.destination_warehouse_id).first()
    if not warehouse:
        raise HTTPException(status_code=404, detail="Warehouse not found")
    
    if warehouse.organization_id != order.customer_organization_id:
        raise HTTPException(status_code=400, detail="Warehouse does not belong to the customer organization")
    
    # Create the order item
    db_item = models.PartOrderItem(**item.dict())
    
    try:
        db.add(db_item)
        db.commit()
        db.refresh(db_item)
        
        # Get the item with related data
        result = {
            **db_item.__dict__,
            "part_number": part.part_number,
            "part_name": part.name,
            "part_type": part.part_type.value,
            "unit_of_measure": part.unit_of_measure,
            "is_proprietary": part.is_proprietary,
            "warehouse_name": warehouse.name
        }
        
        return result
    except Exception as e:
        db.rollback()
        logger.error(f"Error adding order item: {e}")
        raise HTTPException(status_code=500, detail=f"Error adding order item: {str(e)}")

def update_order_item(db: Session, item_id: uuid.UUID, item_update: schemas.PartOrderItemUpdate):
    """Update an order item."""
    db_item = db.query(models.PartOrderItem).filter(models.PartOrderItem.id == item_id).first()
    if not db_item:
        return None
    
    # Check if order can be modified
    order = db.query(models.PartOrderRequest).filter(models.PartOrderRequest.id == db_item.order_request_id).first()
    if order.status not in [models.OrderStatus.REQUESTED, models.OrderStatus.APPROVED]:
        raise HTTPException(status_code=400, detail="Cannot modify items in orders that are shipped or received")
    
    update_data = item_update.dict(exclude_unset=True)
    
    # Validate warehouse if being updated
    if "destination_warehouse_id" in update_data:
        warehouse = db.query(models.Warehouse).filter(
            models.Warehouse.id == update_data["destination_warehouse_id"]
        ).first()
        if not warehouse:
            raise HTTPException(status_code=404, detail="Warehouse not found")
        
        if warehouse.organization_id != order.customer_organization_id:
            raise HTTPException(status_code=400, detail="Warehouse does not belong to the customer organization")
    
    for key, value in update_data.items():
        setattr(db_item, key, value)
    
    try:
        db.add(db_item)
        db.commit()
        db.refresh(db_item)
        
        # Get the item with related data
        part = db.query(models.Part).filter(models.Part.id == db_item.part_id).first()
        warehouse = db.query(models.Warehouse).filter(models.Warehouse.id == db_item.destination_warehouse_id).first()
        
        result = {
            **db_item.__dict__,
            "part_number": part.part_number,
            "part_name": part.name,
            "part_type": part.part_type.value,
            "unit_of_measure": part.unit_of_measure,
            "is_proprietary": part.is_proprietary,
            "warehouse_name": warehouse.name
        }
        
        return result
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating order item: {e}")
        raise HTTPException(status_code=500, detail=f"Error updating order item: {str(e)}")

def remove_order_item(db: Session, item_id: uuid.UUID):
    """Remove an item from a part order request."""
    db_item = db.query(models.PartOrderItem).filter(models.PartOrderItem.id == item_id).first()
    if not db_item:
        return None
    
    # Check if order can be modified
    order = db.query(models.PartOrderRequest).filter(models.PartOrderRequest.id == db_item.order_request_id).first()
    if order.status != models.OrderStatus.REQUESTED:
        raise HTTPException(status_code=400, detail="Cannot remove items from orders that have been approved or are in progress")
    
    try:
        db.delete(db_item)
        db.commit()
        return {"message": "Order item removed successfully"}
    except Exception as e:
        db.rollback()
        logger.error(f"Error removing order item: {e}")
        raise HTTPException(status_code=500, detail=f"Error removing order item: {str(e)}")

# Order Approval Functions
def approve_order_request(db: Session, order_id: uuid.UUID, approval: schemas.OrderApprovalRequest, approver_user_id: uuid.UUID):
    """Approve or reject a part order request."""
    # Get the order
    db_order = db.query(models.PartOrderRequest).filter(models.PartOrderRequest.id == order_id).first()
    if not db_order:
        raise HTTPException(status_code=404, detail="Part order request not found")
    
    # Check if order can be approved (only if status is REQUESTED)
    if db_order.status != models.OrderStatus.REQUESTED:
        raise HTTPException(status_code=400, detail="Order has already been processed")
    
    # Create approval record
    db_approval = models.OrderApproval(
        order_request_id=order_id,
        approved_by_user_id=approver_user_id,
        approved=approval.approved,
        approval_notes=approval.approval_notes
    )
    
    try:
        db.add(db_approval)
        
        # Update order status and details
        if approval.approved:
            db_order.status = models.OrderStatus.APPROVED
            db_order.approved_by_user_id = approver_user_id
            if approval.expected_delivery_date:
                db_order.expected_delivery_date = approval.expected_delivery_date
        else:
            db_order.status = models.OrderStatus.CANCELLED
        
        db.add(db_order)
        db.commit()
        db.refresh(db_order)
        
        # Get the order with related data
        result = get_part_order_request(db, db_order.id)
        return result
    except Exception as e:
        db.rollback()
        logger.error(f"Error approving order request: {e}")
        raise HTTPException(status_code=500, detail=f"Error approving order request: {str(e)}")

def fulfill_order_request(db: Session, order_id: uuid.UUID, fulfillment: schemas.OrderFulfillmentRequest, fulfilled_by_user_id: uuid.UUID):
    """Fulfill a part order request by recording received items and updating inventory."""
    # Get the order
    db_order = db.query(models.PartOrderRequest).filter(models.PartOrderRequest.id == order_id).first()
    if not db_order:
        raise HTTPException(status_code=404, detail="Part order request not found")
    
    # Check if order can be fulfilled
    if db_order.status not in [models.OrderStatus.APPROVED, models.OrderStatus.ORDERED, models.OrderStatus.SHIPPED]:
        raise HTTPException(status_code=400, detail="Order must be approved, ordered, or shipped before it can be fulfilled")
    
    transaction_ids = []
    
    try:
        # Process each item in the fulfillment
        for item_data in fulfillment.items:
            item_id = item_data.get("item_id")
            received_quantity = item_data.get("received_quantity", 0)
            item_notes = item_data.get("notes", "")
            
            # Get the order item
            order_item = db.query(models.PartOrderItem).filter(models.PartOrderItem.id == item_id).first()
            if not order_item:
                continue
            
            # Update the received quantity
            order_item.received_quantity = received_quantity
            if item_notes:
                order_item.notes = f"{order_item.notes or ''}\nReceived: {item_notes}".strip()
            
            db.add(order_item)
            
            # Create inventory transaction if quantity was received
            if received_quantity > 0:
                # Get part and warehouse details
                part = db.query(models.Part).filter(models.Part.id == order_item.part_id).first()
                
                # Create transaction based on supplier type
                if db_order.supplier_type == SupplierType.ORASEAS_EE:
                    # This is a transfer from Oraseas EE to customer
                    # Find Oraseas EE warehouse (simplified - use first warehouse)
                    oraseas_warehouse = db.query(models.Warehouse).filter(
                        models.Warehouse.organization_id == db_order.supplier_organization_id
                    ).first()
                    
                    transaction = models.Transaction(
                        transaction_type=models.TransactionType.TRANSFER,
                        part_id=order_item.part_id,
                        from_warehouse_id=oraseas_warehouse.id if oraseas_warehouse else None,
                        to_warehouse_id=order_item.destination_warehouse_id,
                        quantity=received_quantity,
                        unit_of_measure=part.unit_of_measure,
                        performed_by_user_id=fulfilled_by_user_id,
                        transaction_date=fulfillment.actual_delivery_date,
                        notes=f"Order fulfillment: {db_order.order_number}",
                        reference_number=f"ORDER-{db_order.order_number}-{item_id}"
                    )
                else:
                    # This is inventory creation from external supplier
                    transaction = models.Transaction(
                        transaction_type=models.TransactionType.CREATION,
                        part_id=order_item.part_id,
                        to_warehouse_id=order_item.destination_warehouse_id,
                        quantity=received_quantity,
                        unit_of_measure=part.unit_of_measure,
                        performed_by_user_id=fulfilled_by_user_id,
                        transaction_date=fulfillment.actual_delivery_date,
                        notes=f"Order fulfillment from {db_order.supplier_name}: {db_order.order_number}",
                        reference_number=f"ORDER-{db_order.order_number}-{item_id}"
                    )
                
                db.add(transaction)
                db.flush()  # Get the transaction ID
                transaction_ids.append(transaction.id)
                
                # Create order transaction link
                order_transaction = models.OrderTransaction(
                    order_request_id=order_id,
                    transaction_id=transaction.id,
                    order_item_id=order_item.id
                )
                db.add(order_transaction)
        
        # Update order status and details
        db_order.status = models.OrderStatus.RECEIVED
        db_order.actual_delivery_date = fulfillment.actual_delivery_date
        db_order.received_by_user_id = fulfilled_by_user_id
        if fulfillment.fulfillment_notes:
            db_order.fulfillment_notes = fulfillment.fulfillment_notes
        
        db.add(db_order)
        db.commit()
        
        # Get the order with related data
        result = get_part_order_request(db, db_order.id)
        return result
    except Exception as e:
        db.rollback()
        logger.error(f"Error fulfilling order request: {e}")
        raise HTTPException(status_code=500, detail=f"Error fulfilling order request: {str(e)}")

def create_batch_order_request(db: Session, batch_order: schemas.BatchOrderRequest, current_user_id: uuid.UUID):
    """Create a part order request with multiple items."""
    # Create the order request
    order_create = schemas.PartOrderRequestCreate(
        customer_organization_id=batch_order.customer_organization_id,
        supplier_type=batch_order.supplier_type,
        supplier_organization_id=batch_order.supplier_organization_id,
        supplier_name=batch_order.supplier_name,
        priority=batch_order.priority,
        requested_delivery_date=batch_order.requested_delivery_date,
        notes=batch_order.notes,
        requested_by_user_id=current_user_id
    )
    
    # Create the order
    order = create_part_order_request(db, order_create, current_user_id)
    
    # Add all items
    for item_data in batch_order.items:
        item_create = schemas.PartOrderItemCreate(
            order_request_id=order["id"],
            part_id=item_data["part_id"],
            quantity=item_data["quantity"],
            destination_warehouse_id=item_data["destination_warehouse_id"],
            unit_price=item_data.get("unit_price"),
            notes=item_data.get("notes")
        )
        
        add_order_item(db, item_create)
    
    # Get the complete order with items
    result = get_part_order_request(db, order["id"])
    return result

# Analytics and Reporting Functions
def get_order_analytics(db: Session, customer_organization_id: Optional[uuid.UUID] = None, days: int = 30):
    """Get order analytics and metrics."""
    cutoff_date = datetime.now() - timedelta(days=days)
    
    # Base query for orders
    orders_query = db.query(models.PartOrderRequest).filter(models.PartOrderRequest.created_at >= cutoff_date)
    
    if customer_organization_id:
        orders_query = orders_query.filter(models.PartOrderRequest.customer_organization_id == customer_organization_id)
    
    # Total orders
    total_orders = orders_query.count()
    
    # Orders by status
    orders_by_status = {}
    for status in models.OrderStatus:
        count = orders_query.filter(models.PartOrderRequest.status == status).count()
        orders_by_status[status.value] = count
    
    # Orders by priority
    orders_by_priority = {}
    for priority in models.OrderPriority:
        count = orders_query.filter(models.PartOrderRequest.priority == priority).count()
        orders_by_priority[priority.value] = count
    
    # Orders by supplier type
    orders_by_supplier_type = {}
    for supplier_type in models.SupplierType:
        count = orders_query.filter(models.PartOrderRequest.supplier_type == supplier_type).count()
        orders_by_supplier_type[supplier_type.value] = count
    
    # Average fulfillment time (for completed orders)
    completed_orders = orders_query.filter(
        models.PartOrderRequest.status == models.OrderStatus.RECEIVED,
        models.PartOrderRequest.actual_delivery_date.isnot(None)
    ).all()
    
    total_fulfillment_days = 0
    for order in completed_orders:
        if order.actual_delivery_date and order.created_at:
            delta = order.actual_delivery_date - order.created_at
            total_fulfillment_days += delta.days
    
    average_fulfillment_time = total_fulfillment_days / len(completed_orders) if completed_orders else 0
    
    # Total value (sum of all order items with unit prices)
    total_value_query = db.query(
        func.sum(PartOrderItem.quantity * PartOrderItem.unit_price)
    ).join(
        PartOrderRequest, PartOrderItem.order_request_id == PartOrderRequest.id
    ).filter(
        PartOrderRequest.created_at >= cutoff_date,
        PartOrderItem.unit_price.isnot(None)
    )
    
    if customer_organization_id:
        total_value_query = total_value_query.filter(PartOrderRequest.customer_organization_id == customer_organization_id)
    
    total_value = total_value_query.scalar() or 0
    
    # Most ordered parts
    most_ordered_parts_query = db.query(
        models.Part.id,
        models.Part.part_number,
        models.Part.name,
        func.sum(PartOrderItem.quantity).label("total_quantity"),
        func.count(PartOrderItem.id).label("order_count")
    ).join(
        PartOrderItem, models.Part.id == PartOrderItem.part_id
    ).join(
        PartOrderRequest, PartOrderItem.order_request_id == PartOrderRequest.id
    ).filter(
        PartOrderRequest.created_at >= cutoff_date
    )
    
    if customer_organization_id:
        most_ordered_parts_query = most_ordered_parts_query.filter(
            PartOrderRequest.customer_organization_id == customer_organization_id
        )
    
    most_ordered_parts = most_ordered_parts_query.group_by(
        models.Part.id, models.Part.part_number, models.Part.name
    ).order_by(
        func.sum(PartOrderItem.quantity).desc()
    ).limit(10).all()
    
    most_ordered_parts_list = []
    for part_id, part_number, part_name, total_quantity, order_count in most_ordered_parts:
        most_ordered_parts_list.append({
            "part_id": part_id,
            "part_number": part_number,
            "part_name": part_name,
            "total_quantity": float(total_quantity),
            "order_count": order_count
        })
    
    # Supplier performance (for Oraseas EE orders)
    supplier_performance_query = db.query(
        PartOrderRequest.supplier_organization_id,
        PartOrderRequest.supplier_name,
        func.count(PartOrderRequest.id).label("total_orders"),
        func.avg(
            func.extract('epoch', PartOrderRequest.actual_delivery_date - PartOrderRequest.created_at) / 86400
        ).label("avg_fulfillment_days")
    ).filter(
        PartOrderRequest.created_at >= cutoff_date,
        PartOrderRequest.status == OrderStatus.RECEIVED,
        PartOrderRequest.actual_delivery_date.isnot(None)
    )
    
    if customer_organization_id:
        supplier_performance_query = supplier_performance_query.filter(
            PartOrderRequest.customer_organization_id == customer_organization_id
        )
    
    supplier_performance = supplier_performance_query.group_by(
        PartOrderRequest.supplier_organization_id,
        PartOrderRequest.supplier_name
    ).all()
    
    supplier_performance_list = []
    for supplier_org_id, supplier_name, total_orders, avg_fulfillment_days in supplier_performance:
        supplier_name_display = supplier_name
        if supplier_org_id:
            # Get organization name
            org = db.query(models.Organization).filter(models.Organization.id == supplier_org_id).first()
            if org:
                supplier_name_display = org.name
        
        supplier_performance_list.append({
            "supplier_id": supplier_org_id,
            "supplier_name": supplier_name_display,
            "total_orders": total_orders,
            "average_fulfillment_days": float(avg_fulfillment_days) if avg_fulfillment_days else 0
        })
    
    return {
        "total_orders": total_orders,
        "orders_by_status": orders_by_status,
        "orders_by_priority": orders_by_priority,
        "orders_by_supplier_type": orders_by_supplier_type,
        "average_fulfillment_time": average_fulfillment_time,
        "total_value": total_value,
        "most_ordered_parts": most_ordered_parts_list,
        "supplier_performance": supplier_performance_list
    }

def get_reorder_suggestions(db: Session, request: schemas.ReorderSuggestionRequest):
    """Get reorder suggestions based on current inventory levels and usage patterns."""
    # Base query for inventory items
    inventory_query = db.query(
        models.Inventory,
        models.Part.part_number,
        models.Part.name,
        models.Part.part_type,
        models.Warehouse.name.label("warehouse_name")
    ).join(
        models.Part, models.Inventory.part_id == models.Part.id
    ).join(
        models.Warehouse, models.Inventory.warehouse_id == models.Warehouse.id
    )
    
    # Apply filters
    if request.organization_id:
        inventory_query = inventory_query.filter(models.Warehouse.organization_id == request.organization_id)
    
    if request.warehouse_id:
        inventory_query = inventory_query.filter(models.Inventory.warehouse_id == request.warehouse_id)
    
    if request.part_type:
        inventory_query = inventory_query.filter(models.Part.part_type == request.part_type)
    
    # Get inventory items that are below minimum stock or will run out soon
    inventory_items = inventory_query.filter(
        or_(
            models.Inventory.current_stock <= models.Inventory.minimum_stock_recommendation,
            models.Inventory.minimum_stock_recommendation == 0  # Include items with no minimum set
        )
    ).all()
    
    suggestions = []
    cutoff_date = datetime.now() - timedelta(days=90)  # Look at last 90 days for usage patterns
    
    for inventory, part_number, part_name, part_type, warehouse_name in inventory_items:
        # Calculate average monthly usage
        usage_query = db.query(
            func.sum(models.PartUsage.quantity)
        ).filter(
            models.PartUsage.part_id == inventory.part_id,
            models.PartUsage.warehouse_id == inventory.warehouse_id,
            models.PartUsage.usage_date >= cutoff_date
        ).scalar()
        
        total_usage = usage_query or 0
        average_monthly_usage = total_usage / 3  # 90 days = ~3 months
        
        # Get last order date
        last_order_query = db.query(
            func.max(PartOrderRequest.created_at)
        ).join(
            PartOrderItem, PartOrderRequest.id == PartOrderItem.order_request_id
        ).filter(
            PartOrderItem.part_id == inventory.part_id,
            PartOrderItem.destination_warehouse_id == inventory.warehouse_id,
            PartOrderRequest.status.in_([OrderStatus.RECEIVED, OrderStatus.SHIPPED])
        ).scalar()
        
        # Calculate days until stockout
        days_until_stockout = None
        if average_monthly_usage > 0:
            days_until_stockout = int((inventory.current_stock / average_monthly_usage) * 30)
        
        # Determine priority
        priority = OrderPriority.LOW
        if inventory.current_stock <= 0:
            priority = OrderPriority.URGENT
        elif days_until_stockout and days_until_stockout <= 7:
            priority = OrderPriority.HIGH
        elif days_until_stockout and days_until_stockout <= request.minimum_days_stock:
            priority = OrderPriority.MEDIUM
        elif inventory.current_stock <= inventory.minimum_stock_recommendation:
            priority = OrderPriority.MEDIUM
        
        # Calculate suggested order quantity
        # Suggest enough for minimum_days_stock worth of usage, or minimum stock recommendation, whichever is higher
        suggested_quantity = max(
            inventory.minimum_stock_recommendation,
            (average_monthly_usage / 30) * request.minimum_days_stock if average_monthly_usage > 0 else inventory.minimum_stock_recommendation
        )
        
        # Only suggest if there's a real need
        if (inventory.current_stock <= inventory.minimum_stock_recommendation or 
            (days_until_stockout and days_until_stockout <= request.minimum_days_stock)):
            
            suggestions.append({
                "part_id": inventory.part_id,
                "part_number": part_number,
                "part_name": part_name,
                "warehouse_id": inventory.warehouse_id,
                "warehouse_name": warehouse_name,
                "current_stock": inventory.current_stock,
                "minimum_stock_recommendation": inventory.minimum_stock_recommendation,
                "suggested_order_quantity": suggested_quantity,
                "last_order_date": last_order_query,
                "average_monthly_usage": average_monthly_usage,
                "days_until_stockout": days_until_stockout,
                "priority": priority
            })
    
    # Sort by priority (urgent first) and then by days until stockout
    priority_order = {OrderPriority.URGENT: 0, OrderPriority.HIGH: 1, OrderPriority.MEDIUM: 2, OrderPriority.LOW: 3}
    suggestions.sort(key=lambda x: (priority_order[x["priority"]], x["days_until_stockout"] or 999))
    
    return suggestions