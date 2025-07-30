# backend/app/crud/part_order.py

import uuid
from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_

from .. import models, schemas
from ..schemas.part_order_transaction import PartOrderRequest, PartOrderReceiptRequest, PartOrderResponse, PartOrderStatus

def create_part_order(db: Session, part_order: PartOrderRequest) -> models.PartOrderRequest:
    """Create a new part order request (phase 1)"""
    
    # Validate organizations exist
    from_org = db.query(models.Organization).filter(models.Organization.id == part_order.from_organization_id).first()
    if not from_org:
        raise ValueError(f"From organization {part_order.from_organization_id} not found")
    
    to_org = db.query(models.Organization).filter(models.Organization.id == part_order.to_organization_id).first()
    if not to_org:
        raise ValueError(f"To organization {part_order.to_organization_id} not found")
    
    # Validate warehouse if provided
    if part_order.from_warehouse_id:
        warehouse = db.query(models.Warehouse).filter(models.Warehouse.id == part_order.from_warehouse_id).first()
        if not warehouse:
            raise ValueError(f"Warehouse {part_order.from_warehouse_id} not found")
        if warehouse.organization_id != part_order.from_organization_id:
            raise ValueError(f"Warehouse {part_order.from_warehouse_id} does not belong to organization {part_order.from_organization_id}")
    
    # Validate user exists
    user = db.query(models.User).filter(models.User.id == part_order.performed_by_user_id).first()
    if not user:
        raise ValueError(f"User {part_order.performed_by_user_id} not found")
    
    # Validate all parts exist
    for item in part_order.order_items:
        part = db.query(models.Part).filter(models.Part.id == item.part_id).first()
        if not part:
            raise ValueError(f"Part {item.part_id} not found")
    
    # Generate order number
    order_count = db.query(models.PartOrderRequest).count()
    order_number = f"PO-{datetime.now().strftime('%Y%m%d')}-{order_count + 1:04d}"
    
    # Create the part order request
    db_part_order = models.PartOrderRequest(
        order_number=order_number,
        customer_organization_id=part_order.from_organization_id,
        supplier_organization_id=part_order.to_organization_id,
        supplier_type=models.SupplierType.EXTERNAL_SUPPLIER if to_org.organization_type == models.OrganizationType.supplier else models.SupplierType.ORASEAS_EE,
        supplier_name=to_org.name,
        status=models.OrderStatus.REQUESTED,
        priority=models.OrderPriority.MEDIUM,  # Default priority
        expected_delivery_date=part_order.expected_delivery_date,
        notes=part_order.notes,
        requested_by_user_id=part_order.performed_by_user_id
    )
    
    db.add(db_part_order)
    db.flush()  # Get the ID
    
    # Create order items
    for item in part_order.order_items:
        # Use the provided warehouse or default to first warehouse of the organization
        destination_warehouse_id = part_order.from_warehouse_id
        if not destination_warehouse_id:
            default_warehouse = db.query(models.Warehouse).filter(
                models.Warehouse.organization_id == part_order.from_organization_id
            ).first()
            if default_warehouse:
                destination_warehouse_id = default_warehouse.id
            else:
                raise ValueError(f"No warehouse found for organization {part_order.from_organization_id}")
        
        db_item = models.PartOrderItem(
            order_request_id=db_part_order.id,
            part_id=item.part_id,
            quantity=item.quantity,
            unit_price=item.unit_price,
            destination_warehouse_id=destination_warehouse_id,
            notes=item.notes
        )
        db.add(db_item)
    
    db.commit()
    db.refresh(db_part_order)
    
    return db_part_order

def receive_part_order(db: Session, receipt: PartOrderReceiptRequest) -> models.PartOrderRequest:
    """Process part order receipt (phase 2)"""
    
    # Get the original order
    order = db.query(models.PartOrderRequest).filter(models.PartOrderRequest.id == receipt.order_id).first()
    if not order:
        raise ValueError(f"Order {receipt.order_id} not found")
    
    if order.status not in [models.OrderStatus.REQUESTED, models.OrderStatus.APPROVED, models.OrderStatus.SHIPPED]:
        raise ValueError(f"Order {receipt.order_id} cannot be received in status {order.status}")
    
    # Validate user exists
    user = db.query(models.User).filter(models.User.id == receipt.performed_by_user_id).first()
    if not user:
        raise ValueError(f"User {receipt.performed_by_user_id} not found")
    
    # Update order status and receipt information
    order.status = models.OrderStatus.RECEIVED
    order.actual_delivery_date = receipt.received_date
    order.received_by_user_id = receipt.performed_by_user_id
    order.fulfillment_notes = receipt.notes
    
    # Update received quantities for each item and create inventory transactions
    for received_item in receipt.received_items:
        # Find the corresponding order item
        order_item = db.query(models.PartOrderItem).filter(
            and_(
                models.PartOrderItem.order_request_id == receipt.order_id,
                models.PartOrderItem.part_id == received_item.part_id
            )
        ).first()
        
        if not order_item:
            raise ValueError(f"Part {received_item.part_id} not found in original order")
        
        # Update received quantity
        order_item.received_quantity = received_item.quantity
        
        # Create inventory transaction for the received parts
        part = db.query(models.Part).filter(models.Part.id == received_item.part_id).first()
        
        transaction = models.Transaction(
            transaction_type=models.TransactionType.CREATION.value,
            part_id=received_item.part_id,
            to_warehouse_id=order_item.destination_warehouse_id,
            quantity=received_item.quantity,
            unit_of_measure=part.unit_of_measure,
            performed_by_user_id=receipt.performed_by_user_id,
            transaction_date=receipt.received_date,
            notes=f"Part order receipt - Order: {order.order_number}",
            reference_number=order.order_number
        )
        db.add(transaction)
        
        # Update inventory
        inventory_item = db.query(models.Inventory).filter(
            and_(
                models.Inventory.warehouse_id == order_item.destination_warehouse_id,
                models.Inventory.part_id == received_item.part_id
            )
        ).first()
        
        if inventory_item:
            inventory_item.current_stock += received_item.quantity
            inventory_item.last_updated = receipt.received_date
        else:
            # Create new inventory item
            inventory_item = models.Inventory(
                warehouse_id=order_item.destination_warehouse_id,
                part_id=received_item.part_id,
                current_stock=received_item.quantity,
                unit_of_measure=part.unit_of_measure,
                last_updated=receipt.received_date
            )
            db.add(inventory_item)
    
    db.commit()
    db.refresh(order)
    
    return order

def get_part_order(db: Session, order_id: uuid.UUID) -> Optional[dict]:
    """Get a part order by ID with related data"""
    
    order = db.query(models.PartOrderRequest).filter(models.PartOrderRequest.id == order_id).first()
    if not order:
        return None
    
    # Get related data
    customer_org = db.query(models.Organization).filter(models.Organization.id == order.customer_organization_id).first()
    supplier_org = db.query(models.Organization).filter(models.Organization.id == order.supplier_organization_id).first()
    requested_by = db.query(models.User).filter(models.User.id == order.requested_by_user_id).first()
    
    # Get order items
    order_items = db.query(models.PartOrderItem).filter(models.PartOrderItem.order_request_id == order.id).all()
    
    items_data = []
    total_value = 0
    for item in order_items:
        part = db.query(models.Part).filter(models.Part.id == item.part_id).first()
        item_data = {
            **item.__dict__,
            "part_name": part.name if part else None,
            "part_number": part.part_number if part else None
        }
        items_data.append(item_data)
        
        if item.unit_price:
            total_value += float(item.unit_price * item.quantity)
    
    # Build response
    result = {
        **order.__dict__,
        "from_organization_name": customer_org.name if customer_org else None,
        "to_organization_name": supplier_org.name if supplier_org else None,
        "performed_by_username": requested_by.username if requested_by else None,
        "order_items": items_data,
        "total_items": len(items_data),
        "total_value": total_value,
        # Convert enum values to strings for response
        "status": order.status.value if hasattr(order.status, 'value') else str(order.status),
        "priority": order.priority.value if hasattr(order.priority, 'value') else str(order.priority),
        "supplier_type": order.supplier_type.value if hasattr(order.supplier_type, 'value') else str(order.supplier_type)
    }
    
    return result

def get_part_orders(db: Session, skip: int = 0, limit: int = 100, organization_id: Optional[uuid.UUID] = None) -> List[dict]:
    """Get part orders with optional organization filtering"""
    
    query = db.query(models.PartOrderRequest)
    
    # Filter by organization if provided
    if organization_id:
        query = query.filter(
            (models.PartOrderRequest.customer_organization_id == organization_id) |
            (models.PartOrderRequest.supplier_organization_id == organization_id)
        )
    
    orders = query.order_by(models.PartOrderRequest.created_at.desc()).offset(skip).limit(limit).all()
    
    results = []
    for order in orders:
        # Get related data
        customer_org = db.query(models.Organization).filter(models.Organization.id == order.customer_organization_id).first()
        supplier_org = db.query(models.Organization).filter(models.Organization.id == order.supplier_organization_id).first()
        requested_by = db.query(models.User).filter(models.User.id == order.requested_by_user_id).first()
        
        # Get order items count and total value
        order_items = db.query(models.PartOrderItem).filter(models.PartOrderItem.order_request_id == order.id).all()
        total_value = sum(float(item.unit_price * item.quantity) if item.unit_price else 0 for item in order_items)
        
        # Build response
        result = {
            **order.__dict__,
            "from_organization_name": customer_org.name if customer_org else None,
            "to_organization_name": supplier_org.name if supplier_org else None,
            "performed_by_username": requested_by.username if requested_by else None,
            "total_items": len(order_items),
            "total_value": total_value,
            # Convert enum values to strings for response
            "status": order.status.value if hasattr(order.status, 'value') else str(order.status),
            "priority": order.priority.value if hasattr(order.priority, 'value') else str(order.priority),
            "supplier_type": order.supplier_type.value if hasattr(order.supplier_type, 'value') else str(order.supplier_type)
        }
        
        results.append(result)
    
    return results