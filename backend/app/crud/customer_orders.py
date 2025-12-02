# backend/app/crud/customer_orders.py

import uuid
import logging
from typing import List, Optional
from decimal import Decimal
from datetime import datetime

from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from .. import models, schemas # Import models and schemas
from ..transaction_processor import TransactionProcessor

logger = logging.getLogger(__name__)

def get_customer_order(db: Session, order_id: uuid.UUID):
    """Retrieve a single customer order by ID."""
    return db.query(models.CustomerOrder).filter(models.CustomerOrder.id == order_id).first()

def get_customer_orders(db: Session, skip: int = 0, limit: int = 100):
    """Retrieve a list of customer orders."""
    return db.query(models.CustomerOrder).offset(skip).limit(limit).all()

def create_customer_order(db: Session, order: schemas.CustomerOrderCreate):
    """Create a new customer order."""
    # Validate FKs - these checks should ideally be in the router or a service layer
    customer_org = db.query(models.Organization).filter(models.Organization.id == order.customer_organization_id).first()
    oraseas_org = db.query(models.Organization).filter(models.Organization.id == order.oraseas_organization_id).first()
    if not customer_org or not oraseas_org:
        raise HTTPException(status_code=400, detail="Customer or Oraseas Organization ID not found")
    if order.ordered_by_user_id:
        user = db.query(models.User).filter(models.User.id == order.ordered_by_user_id).first()
        if not user: raise HTTPException(status_code=400, detail="Ordered by User ID not found")

    db_order = models.CustomerOrder(**order.dict())
    try:
        db.add(db_order)
        db.commit()
        db.refresh(db_order)
        return db_order
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating customer order: {e}")
        raise HTTPException(status_code=400, detail="Error creating customer order")

def update_customer_order(db: Session, order_id: uuid.UUID, order_update: schemas.CustomerOrderUpdate, current_user_id: uuid.UUID = None, items_data: list = None):
    """Update an existing customer order and handle inventory updates on fulfillment."""
    db_order = db.query(models.CustomerOrder).filter(models.CustomerOrder.id == order_id).first()
    if not db_order:
        return None # Indicate not found

    # Store the old status to check if we need to update inventory
    old_status = db_order.status
    
    update_data = order_update.dict(exclude_unset=True)
    full_update_data = order_update.dict()  # Get all fields including None values
    
    # Add items to full_update_data if provided
    if items_data is not None:
        full_update_data['items'] = items_data
        logger.info(f"Items data added to full_update_data: {len(items_data)} items")
    
    for key, value in update_data.items():
        if key != 'items':  # Don't try to set items on the order object
            setattr(db_order, key, value)
    
    try:
        # Re-validate FKs if IDs are updated
        if "customer_organization_id" in update_data:
            customer_org = db.query(models.Organization).filter(models.Organization.id == db_order.customer_organization_id).first()
            if not customer_org: raise HTTPException(status_code=400, detail="Customer Organization ID not found")
        if "oraseas_organization_id" in update_data:
            oraseas_org = db.query(models.Organization).filter(models.Organization.id == db_order.oraseas_organization_id).first()
            if not oraseas_org: raise HTTPException(status_code=400, detail="Oraseas Organization ID not found")
        if "ordered_by_user_id" in update_data and db_order.ordered_by_user_id:
            user = db.query(models.User).filter(models.User.id == db_order.ordered_by_user_id).first()
            if not user: raise HTTPException(status_code=400, detail="Ordered by User ID not found")

        # Check if order is being fulfilled (status changed to Received or Delivered)
        new_status = db_order.status
        logger.info(f"Order status change: {old_status} -> {new_status}")
        logger.info(f"Order update object: {order_update}")
        logger.info(f"Order update dict: {order_update.dict()}")
        logger.info(f"Order update data (exclude_unset): {update_data}")
        logger.info(f"Full update data: {full_update_data}")
        logger.info(f"Has receiving_warehouse_id: {hasattr(order_update, 'receiving_warehouse_id')}")
        logger.info(f"Receiving warehouse ID: {getattr(order_update, 'receiving_warehouse_id', None)}")
        
        if (old_status not in ["Received", "Delivered"] and 
            new_status in ["Received", "Delivered"] and
            'receiving_warehouse_id' in full_update_data and 
            full_update_data['receiving_warehouse_id']):
            
            logger.info(f"Updating inventory for order {db_order.id}")
            # Update inventory for all order items
            _update_inventory_on_fulfillment(db, db_order, full_update_data['receiving_warehouse_id'], current_user_id)
        else:
            logger.info(f"Inventory update conditions not met for order {db_order.id}")

        # Update order items if provided
        logger.info(f"Checking for items update - 'items' in full_update_data: {'items' in full_update_data}")
        logger.info(f"Full update data keys: {full_update_data.keys()}")
        if 'items' in full_update_data:
            logger.info(f"Items value: {full_update_data['items']}")
        
        if 'items' in full_update_data and full_update_data['items'] is not None:
            logger.info(f"Updating order items for order {db_order.id} - {len(full_update_data['items'])} items")
            # Delete existing items
            deleted_count = db.query(models.CustomerOrderItem).filter(
                models.CustomerOrderItem.customer_order_id == order_id
            ).delete()
            logger.info(f"Deleted {deleted_count} existing items")
            
            # Add new items
            for idx, item_data in enumerate(full_update_data['items']):
                logger.info(f"Adding item {idx}: part_id={item_data.get('part_id')}, quantity={item_data.get('quantity')}")
                new_item = models.CustomerOrderItem(
                    customer_order_id=order_id,
                    part_id=item_data['part_id'],
                    quantity=item_data['quantity'],
                    unit_price=item_data.get('unit_price')
                )
                db.add(new_item)
            logger.info(f"Added {len(full_update_data['items'])} new items")
        else:
            logger.info(f"No items to update for order {db_order.id}")

        db.add(db_order)
        db.commit()
        db.refresh(db_order)
        return db_order
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating customer order: {e}")
        raise HTTPException(status_code=400, detail="Error updating customer order")

def _update_inventory_on_fulfillment(db: Session, order: models.CustomerOrder, receiving_warehouse_id: uuid.UUID, current_user_id: uuid.UUID = None):
    """Update customer warehouse inventory when order is fulfilled."""
    try:
        # Get all order items
        order_items = db.query(models.CustomerOrderItem).filter(
            models.CustomerOrderItem.customer_order_id == order.id
        ).all()
        
        if not order_items:
            logger.warning(f"No items found for customer order {order.id}")
            return
        
        # Initialize transaction processor
        transaction_processor = TransactionProcessor(db)
        
        # Create inventory transactions for each order item
        for item in order_items:
            # Get part details for unit_of_measure
            part = db.query(models.Part).filter(models.Part.id == item.part_id).first()
            if not part:
                logger.error(f"Part {item.part_id} not found for order item")
                continue
                
            # Create a "creation" transaction to add parts to customer's warehouse
            from ..schemas.transaction import TransactionCreate, TransactionTypeEnum
            transaction_data = TransactionCreate(
                transaction_type=TransactionTypeEnum.CREATION,
                part_id=item.part_id,
                quantity=item.quantity,
                unit_of_measure=part.unit_of_measure,
                to_warehouse_id=receiving_warehouse_id,
                from_warehouse_id=None,  # Creation doesn't have a source warehouse
                machine_id=None,
                transaction_date=datetime.now(),
                notes=f"Customer order fulfillment - Order ID: {order.id}",
                performed_by_user_id=current_user_id  # User fulfilling the order
            )
            
            # Process the transaction (this will update inventory automatically)
            transaction_processor.process_transaction(transaction_data)
            logger.info(f"Created inventory transaction for order {order.id}, part {item.part_id}, quantity {item.quantity}")
            
    except Exception as e:
        logger.error(f"Error updating inventory for customer order {order.id}: {e}")
        raise HTTPException(status_code=400, detail=f"Error updating inventory: {str(e)}")

def delete_customer_order(db: Session, order_id: uuid.UUID):
    """Delete a customer order by ID."""
    db_order = db.query(models.CustomerOrder).filter(models.CustomerOrder.id == order_id).first()
    if not db_order:
        return None # Indicate not found
    try:
        db.delete(db_order)
        db.commit()
        return {"message": "Customer order deleted successfully"}
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting customer order: {e}")
        raise HTTPException(status_code=400, detail="Error deleting customer order. Check for dependent records.")
