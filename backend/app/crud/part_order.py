# backend/app/crud/part_order.py

import uuid
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, func, desc

from .. import models, schemas

def get_part_order_requests(
    db: Session,
    customer_organization_id: Optional[uuid.UUID] = None,
    status: Optional[schemas.OrderStatusEnum] = None,
    priority: Optional[schemas.OrderPriorityEnum] = None,
    supplier_type: Optional[schemas.SupplierTypeEnum] = None,
    skip: int = 0,
    limit: int = 100
) -> List[Dict[str, Any]]:
    """Get part order requests with optional filtering"""
    
    query = db.query(models.PartOrderRequest)
    
    # Apply filters
    if customer_organization_id:
        query = query.filter(models.PartOrderRequest.customer_organization_id == customer_organization_id)
    
    if status:
        query = query.filter(models.PartOrderRequest.status == status.value)
    
    if priority:
        query = query.filter(models.PartOrderRequest.priority == priority.value)
    
    if supplier_type:
        query = query.filter(models.PartOrderRequest.supplier_type == supplier_type.value)
    
    orders = query.order_by(models.PartOrderRequest.created_at.desc()).offset(skip).limit(limit).all()
    
    results = []
    for order in orders:
        # Get related data
        customer_org = db.query(models.Organization).filter(models.Organization.id == order.customer_organization_id).first()
        supplier_org = db.query(models.Organization).filter(models.Organization.id == order.supplier_organization_id).first() if order.supplier_organization_id else None
        requested_by = db.query(models.User).filter(models.User.id == order.requested_by_user_id).first()
        approved_by = db.query(models.User).filter(models.User.id == order.approved_by_user_id).first() if order.approved_by_user_id else None
        received_by = db.query(models.User).filter(models.User.id == order.received_by_user_id).first() if order.received_by_user_id else None
        
        # Build response
        result = {
            **order.__dict__,
            "customer_organization_name": customer_org.name if customer_org else None,
            "supplier_organization_name": supplier_org.name if supplier_org else None,
            "requested_by_username": requested_by.username if requested_by else None,
            "approved_by_username": approved_by.username if approved_by else None,
            "received_by_username": received_by.username if received_by else None
        }
        
        results.append(result)
    
    return results

def get_part_order_request(db: Session, order_id: uuid.UUID) -> Optional[Dict[str, Any]]:
    """Get a part order request by ID with related data"""
    
    order = db.query(models.PartOrderRequest).filter(models.PartOrderRequest.id == order_id).first()
    if not order:
        return None
    
    # Get related data
    customer_org = db.query(models.Organization).filter(models.Organization.id == order.customer_organization_id).first()
    supplier_org = db.query(models.Organization).filter(models.Organization.id == order.supplier_organization_id).first() if order.supplier_organization_id else None
    requested_by = db.query(models.User).filter(models.User.id == order.requested_by_user_id).first()
    approved_by = db.query(models.User).filter(models.User.id == order.approved_by_user_id).first() if order.approved_by_user_id else None
    received_by = db.query(models.User).filter(models.User.id == order.received_by_user_id).first() if order.received_by_user_id else None
    
    # Build response
    result = {
        **order.__dict__,
        "customer_organization_name": customer_org.name if customer_org else None,
        "supplier_organization_name": supplier_org.name if supplier_org else None,
        "requested_by_username": requested_by.username if requested_by else None,
        "approved_by_username": approved_by.username if approved_by else None,
        "received_by_username": received_by.username if received_by else None
    }
    
    return result

def create_part_order_request(db: Session, order: schemas.PartOrderRequestCreate, user_id: uuid.UUID) -> Dict[str, Any]:
    """Create a new part order request"""
    
    # Generate order number
    order_count = db.query(models.PartOrderRequest).count()
    order_number = f"PO-{datetime.now().strftime('%Y%m%d')}-{order_count + 1:04d}"
    
    # Create the order
    db_order = models.PartOrderRequest(
        order_number=order_number,
        customer_organization_id=order.customer_organization_id,
        supplier_type=order.supplier_type,
        supplier_organization_id=order.supplier_organization_id,
        supplier_name=order.supplier_name,
        status=models.OrderStatus.REQUESTED,
        priority=order.priority,
        requested_delivery_date=order.requested_delivery_date,
        notes=order.notes,
        requested_by_user_id=user_id
    )
    
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    
    return get_part_order_request(db, db_order.id)

def update_part_order_request(db: Session, order_id: uuid.UUID, order_update: schemas.PartOrderRequestUpdate) -> Dict[str, Any]:
    """Update a part order request"""
    
    order = db.query(models.PartOrderRequest).filter(models.PartOrderRequest.id == order_id).first()
    if not order:
        raise ValueError(f"Order {order_id} not found")
    
    # Update fields
    update_data = order_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(order, field, value)
    
    db.commit()
    db.refresh(order)
    
    return get_part_order_request(db, order_id)

def delete_part_order_request(db: Session, order_id: uuid.UUID) -> Dict[str, str]:
    """Delete a part order request"""
    
    order = db.query(models.PartOrderRequest).filter(models.PartOrderRequest.id == order_id).first()
    if not order:
        raise ValueError(f"Order {order_id} not found")
    
    db.delete(order)
    db.commit()
    
    return {"message": "Order deleted successfully"}

def approve_order_request(db: Session, order_id: uuid.UUID, approval: schemas.OrderApprovalRequest, user_id: uuid.UUID) -> Dict[str, Any]:
    """Approve or reject a part order request"""
    
    order = db.query(models.PartOrderRequest).filter(models.PartOrderRequest.id == order_id).first()
    if not order:
        raise ValueError(f"Order {order_id} not found")
    
    # Update order status
    if approval.approved:
        order.status = models.OrderStatus.APPROVED
    else:
        order.status = models.OrderStatus.CANCELLED
    
    order.approved_by_user_id = user_id
    order.fulfillment_notes = approval.notes
    
    db.commit()
    db.refresh(order)
    
    return get_part_order_request(db, order_id)

def fulfill_order_request(db: Session, order_id: uuid.UUID, fulfillment: schemas.OrderFulfillmentRequest, user_id: uuid.UUID) -> Dict[str, Any]:
    """Fulfill a part order request"""
    
    order = db.query(models.PartOrderRequest).filter(models.PartOrderRequest.id == order_id).first()
    if not order:
        raise ValueError(f"Order {order_id} not found")
    
    # Update order status
    order.status = models.OrderStatus.RECEIVED
    order.received_by_user_id = user_id
    order.actual_delivery_date = fulfillment.actual_delivery_date or datetime.now()
    if fulfillment.fulfillment_notes:
        order.fulfillment_notes = fulfillment.fulfillment_notes
    
    db.commit()
    db.refresh(order)
    
    return get_part_order_request(db, order_id)

def create_batch_order_request(db: Session, batch_order: schemas.BatchOrderRequest, user_id: uuid.UUID) -> Dict[str, Any]:
    """Create a batch part order request"""
    
    # For now, just create a simple order - batch functionality can be expanded later
    order_create = schemas.PartOrderRequestCreate(
        customer_organization_id=batch_order.customer_organization_id,
        supplier_type=batch_order.supplier_type,
        supplier_organization_id=batch_order.supplier_organization_id,
        supplier_name=batch_order.supplier_name,
        priority=batch_order.priority,
        requested_delivery_date=batch_order.requested_delivery_date,
        notes=batch_order.notes
    )
    
    return create_part_order_request(db, order_create, user_id)

def get_order_analytics(db: Session, customer_organization_id: Optional[uuid.UUID] = None, days: int = 30) -> Dict[str, Any]:
    """Get order analytics"""
    
    # Calculate the start date for the analytics period
    start_date = datetime.now() - timedelta(days=days)
    
    query = db.query(models.PartOrderRequest).filter(models.PartOrderRequest.created_at >= start_date)
    
    if customer_organization_id:
        query = query.filter(models.PartOrderRequest.customer_organization_id == customer_organization_id)
    
    orders = query.all()
    
    # Calculate metrics
    total_orders = len(orders)
    
    # Orders by status
    orders_by_status = {}
    for status in models.OrderStatus:
        count = len([o for o in orders if o.status == status])
        orders_by_status[status.value] = count
    
    # Orders by priority
    orders_by_priority = {}
    for priority in models.OrderPriority:
        count = len([o for o in orders if o.priority == priority])
        orders_by_priority[priority.value] = count
    
    # Average fulfillment time
    fulfilled_orders = [o for o in orders if o.actual_delivery_date and o.created_at]
    if fulfilled_orders:
        fulfillment_times = [(o.actual_delivery_date - o.created_at).days for o in fulfilled_orders]
        average_fulfillment_time = sum(fulfillment_times) / len(fulfillment_times)
    else:
        average_fulfillment_time = None
    
    # Top suppliers
    supplier_counts = {}
    for order in orders:
        supplier_name = order.supplier_name or "Unknown"
        supplier_counts[supplier_name] = supplier_counts.get(supplier_name, 0) + 1
    
    top_suppliers = [
        {"name": name, "order_count": count}
        for name, count in sorted(supplier_counts.items(), key=lambda x: x[1], reverse=True)[:5]
    ]
    
    return {
        "total_orders": total_orders,
        "orders_by_status": orders_by_status,
        "orders_by_priority": orders_by_priority,
        "average_fulfillment_time": average_fulfillment_time,
        "top_suppliers": top_suppliers
    }

def get_reorder_suggestions(db: Session, request: schemas.ReorderSuggestionRequest) -> List[Dict[str, Any]]:
    """Get reorder suggestions based on inventory levels"""
    
    query = db.query(models.Inventory).join(models.Part).join(models.Warehouse)
    
    if request.organization_id:
        query = query.filter(models.Warehouse.organization_id == request.organization_id)
    
    if request.warehouse_id:
        query = query.filter(models.Inventory.warehouse_id == request.warehouse_id)
    
    # Filter by low stock
    threshold = request.minimum_stock_threshold or 10
    inventory_items = query.filter(models.Inventory.current_stock <= threshold).all()
    
    suggestions = []
    for item in inventory_items:
        part = db.query(models.Part).filter(models.Part.id == item.part_id).first()
        warehouse = db.query(models.Warehouse).filter(models.Warehouse.id == item.warehouse_id).first()
        
        # Simple suggestion logic - suggest 3x the threshold
        suggested_quantity = threshold * 3
        
        suggestion = {
            "part_id": str(item.part_id),
            "part_name": part.name if part else "Unknown",
            "part_number": part.part_number if part else "Unknown",
            "current_stock": item.current_stock,
            "suggested_quantity": suggested_quantity,
            "warehouse_id": str(item.warehouse_id),
            "warehouse_name": warehouse.name if warehouse else "Unknown"
        }
        
        suggestions.append(suggestion)
    
    return suggestions