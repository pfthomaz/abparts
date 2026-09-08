# backend/app/crud/customer_orders.py

import uuid
import logging
from collections import defaultdict
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

def update_customer_order(db: Session, order_id: uuid.UUID, order_update: schemas.CustomerOrderUpdate, current_user_id: uuid.UUID = None, items_data: list = None, raw_update_data: dict = None):
    """Update an existing customer order and handle inventory updates on fulfillment."""
    db_order = db.query(models.CustomerOrder).filter(models.CustomerOrder.id == order_id).first()
    if not db_order:
        return None # Indicate not found

    # Store the old status to check if we need to update inventory
    old_status = db_order.status
    
    # Use raw_update_data if provided (has all fields from request), otherwise fall back to Pydantic object
    if raw_update_data:
        from dateutil import parser as date_parser
        full_update_data = raw_update_data.copy()
        
        # Convert date strings to datetime objects
        date_fields = ['order_date', 'expected_delivery_date', 'actual_delivery_date', 'shipped_date']
        for field in date_fields:
            if field in full_update_data and full_update_data[field]:
                if isinstance(full_update_data[field], str):
                    full_update_data[field] = date_parser.parse(full_update_data[field])
    else:
        # Get all fields from the update object (don't exclude anything for the update loop)
        full_update_data = order_update.dict(exclude_unset=False, exclude_none=False)  # Get ALL fields
    
    logger.info(f"=== ORDER UPDATE DEBUG ===")
    logger.info(f"Order ID: {order_id}")
    logger.info(f"Old order_date: {db_order.order_date}")
    logger.info(f"full_update_data keys: {full_update_data.keys()}")
    logger.info(f"order_date in full_update_data: {'order_date' in full_update_data}")
    if 'order_date' in full_update_data:
        logger.info(f"order_date value in full_update_data: {full_update_data['order_date']}")
    
    # Add items to full_update_data if provided
    if items_data is not None:
        full_update_data['items'] = items_data
        logger.info(f"Items data added to full_update_data: {len(items_data)} items")
    
    # Update all fields from full_update_data (including None values to allow clearing fields)
    for key, value in full_update_data.items():
        if key != 'items':  # Don't try to set items on the order object
            logger.info(f"Setting {key} = {value}")
            setattr(db_order, key, value)
    
    try:
        # Re-validate FKs if IDs are updated
        if "customer_organization_id" in full_update_data and full_update_data["customer_organization_id"]:
            customer_org = db.query(models.Organization).filter(models.Organization.id == db_order.customer_organization_id).first()
            if not customer_org: raise HTTPException(status_code=400, detail="Customer Organization ID not found")
        if "oraseas_organization_id" in full_update_data and full_update_data["oraseas_organization_id"]:
            oraseas_org = db.query(models.Organization).filter(models.Organization.id == db_order.oraseas_organization_id).first()
            if not oraseas_org: raise HTTPException(status_code=400, detail="Oraseas Organization ID not found")
        if "ordered_by_user_id" in full_update_data and db_order.ordered_by_user_id:
            user = db.query(models.User).filter(models.User.id == db_order.ordered_by_user_id).first()
            if not user: raise HTTPException(status_code=400, detail="Ordered by User ID not found")

        # Check if order is being fulfilled (status changed to Received or Delivered)
        new_status = db_order.status
        logger.info(f"Order status change: {old_status} -> {new_status}")
        logger.info(f"Order update object: {order_update}")
        logger.info(f"Order update dict: {order_update.dict()}")
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
            logger.info(f"Reconciling order items for order {db_order.id} - {len(full_update_data['items'])} items in payload")
            _merge_customer_order_items(db, db_order, full_update_data['items'], current_user_id)
        else:
            logger.info(f"No items to update for order {db_order.id}")

        db.add(db_order)
        db.commit()
        db.refresh(db_order)
        return db_order
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating customer order: {e}")
        raise HTTPException(status_code=400, detail="Error updating customer order")

def _part_number(db: Session, part_id) -> str:
    p = db.query(models.Part).filter(models.Part.id == part_id).first()
    return p.part_number if p else str(part_id)


def _clean_price(value):
    """Form sends '' for a blank price; the column wants a number or NULL."""
    if value is None or value == '':
        return None
    return value


def _merge_customer_order_items(db: Session, order: models.CustomerOrder, payload_items: list, current_user_id: uuid.UUID = None):
    """
    Reconcile an order's line items against the edit payload without discarding
    fulfilment history.

      * matched lines  - update quantity / unit_price, keep quantity_shipped /
                         quantity_received / quantity_written_off. Reject a
                         quantity below what has already shipped.
      * removed lines  - deleted, but only if nothing has shipped on them.
      * added lines    - created. If every pre-existing line on the order was
                         already fully shipped from a single warehouse, the new
                         line is backfilled the same way: a 'transfer'
                         Transaction takes the stock out of that warehouse (and,
                         if the order was also fully received into a single
                         warehouse, a 'creation' Transaction puts it there and
                         the cached inventory is bumped), so
                         calculate_current_stock() reflects the movement.

    Ambiguous history (partial shipment, or movement spread across more than one
    warehouse) is not guessed at - the new line is added unfulfilled and a note
    is appended to order.notes so an operator ships it explicitly.
    """
    existing = db.query(models.CustomerOrderItem).filter(
        models.CustomerOrderItem.customer_order_id == order.id
    ).all()

    # --- snapshot the pre-edit fulfilment state (drives backfill for new lines)
    order_fully_shipped = bool(existing) and all(
        it.quantity_shipped >= it.quantity and it.quantity_shipped > 0 for it in existing
    )
    order_fully_received = order_fully_shipped and all(
        it.quantity_received >= it.quantity for it in existing
    )

    ship_txns = db.query(models.Transaction).filter(
        models.Transaction.customer_order_id == order.id,
        models.Transaction.transaction_type == 'transfer',
        models.Transaction.from_warehouse_id.isnot(None),
    ).all()
    recv_txns = db.query(models.Transaction).filter(
        models.Transaction.customer_order_id == order.id,
        models.Transaction.transaction_type == 'creation',
        models.Transaction.to_warehouse_id.isnot(None),
    ).all()
    src_wh_ids = {t.from_warehouse_id for t in ship_txns}
    dst_wh_ids = {t.to_warehouse_id for t in recv_txns}

    can_backfill_ship = order_fully_shipped and len(src_wh_ids) == 1
    source_wh_id = next(iter(src_wh_ids)) if can_backfill_ship else None
    ship_date = order.shipped_date or (max(t.transaction_date for t in ship_txns) if ship_txns else None)

    can_backfill_recv = can_backfill_ship and order_fully_received and len(dst_wh_ids) == 1
    dest_wh_id = next(iter(dst_wh_ids)) if can_backfill_recv else None
    recv_date = order.actual_delivery_date or (max(t.transaction_date for t in recv_txns) if recv_txns else None)

    # --- match payload lines to existing rows (by id first, then by part)
    existing_by_id = {str(it.id): it for it in existing}
    existing_by_part = defaultdict(list)
    for it in existing:
        existing_by_part[str(it.part_id)].append(it)

    matched = set()
    to_add = []
    for pi in payload_items:
        row = None
        pid = pi.get('id')
        if pid and str(pid) in existing_by_id and str(pid) not in matched:
            row = existing_by_id[str(pid)]
        else:
            for cand in existing_by_part.get(str(pi['part_id']), []):
                if str(cand.id) not in matched:
                    row = cand
                    break
        if row is None:
            to_add.append(pi)
            continue

        matched.add(str(row.id))
        new_q = Decimal(str(pi['quantity']))
        if new_q < row.quantity_shipped:
            raise HTTPException(
                status_code=400,
                detail=f"Cannot reduce '{_part_number(db, row.part_id)}' to {new_q}: {row.quantity_shipped} already shipped",
            )
        row.quantity = new_q
        row.unit_price = _clean_price(pi.get('unit_price'))
        db.add(row)

    # --- removed lines
    for it in existing:
        if str(it.id) not in matched:
            if it.quantity_shipped and it.quantity_shipped > 0:
                raise HTTPException(
                    status_code=400,
                    detail=f"Cannot remove '{_part_number(db, it.part_id)}': {it.quantity_shipped} already shipped",
                )
            db.delete(it)

    # --- added lines
    unshipped_notes = []
    for pi in to_add:
        part = db.query(models.Part).filter(models.Part.id == pi['part_id']).first()
        uom = (part.unit_of_measure if part and part.unit_of_measure else 'units')
        qty = Decimal(str(pi['quantity']))
        new_item = models.CustomerOrderItem(
            customer_order_id=order.id,
            part_id=pi['part_id'],
            quantity=qty,
            unit_price=_clean_price(pi.get('unit_price')),
        )
        db.add(new_item)
        db.flush()  # need new_item.id for the transaction rows

        if not order_fully_shipped:
            continue  # siblings aren't shipped either - nothing to mirror

        if not can_backfill_ship:
            unshipped_notes.append(_part_number(db, pi['part_id']))
            continue

        db.add(models.Transaction(
            transaction_type='transfer',
            part_id=new_item.part_id,
            from_warehouse_id=source_wh_id,
            to_warehouse_id=None,
            customer_order_id=order.id,
            customer_order_item_id=new_item.id,
            quantity=qty,
            unit_of_measure=uom,
            performed_by_user_id=current_user_id,
            transaction_date=ship_date or datetime.utcnow(),
            notes=f"Order shipped (backfilled when line added) - Order ID: {order.id}",
            reference_number=f"SHIP-{str(order.id)[:8]}-{str(new_item.id)[:8]}",
        ))
        new_item.quantity_shipped = qty

        if can_backfill_recv:
            db.add(models.Transaction(
                transaction_type='creation',
                part_id=new_item.part_id,
                from_warehouse_id=None,
                to_warehouse_id=dest_wh_id,
                customer_order_id=order.id,
                customer_order_item_id=new_item.id,
                quantity=qty,
                unit_of_measure=uom,
                performed_by_user_id=current_user_id,
                transaction_date=recv_date or datetime.utcnow(),
                notes=f"Received from customer order #{str(order.id)[:8]} (backfilled when line added)",
                reference_number=str(order.id),
            ))
            new_item.quantity_received = qty

            inv = db.query(models.Inventory).filter(
                models.Inventory.part_id == new_item.part_id,
                models.Inventory.warehouse_id == dest_wh_id,
            ).first()
            if inv:
                inv.current_stock = (inv.current_stock or Decimal('0')) + qty
                inv.last_updated = datetime.now()
            else:
                db.add(models.Inventory(
                    part_id=new_item.part_id,
                    warehouse_id=dest_wh_id,
                    current_stock=qty,
                    minimum_stock_recommendation=Decimal('0'),
                    unit_of_measure=uom,
                ))
        db.add(new_item)

    if unshipped_notes:
        stamp = datetime.utcnow().date().isoformat()
        msg = (
            f"[{stamp}] Added and left unshipped (shipment history spans multiple warehouses "
            f"or is incomplete - ship manually): {', '.join(unshipped_notes)}"
        )
        order.notes = f"{order.notes}\n\n{msg}" if order.notes else msg

    # keep status truthful after the reconciliation (no-op if nothing shipped)
    db.flush()
    db.expire(order, ['items'])
    order.status = recompute_customer_order_status(order)
    db.add(order)


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

def recompute_customer_order_status(order: models.CustomerOrder) -> str:
    """
    Derive the order's status from the cumulative shipped/received/written-off
    quantities on its items. Shipped-completeness gates before received-completeness,
    since an order can't be "Received" while some of it hasn't shipped yet. A
    written-off quantity (declared lost/damaged in transit) counts as resolved,
    same as a received one - it closes the tracking gap without a receipt.

    Leaves the status untouched if nothing has been shipped yet (order.items
    must already be loaded).
    """
    total_ordered = sum(item.quantity for item in order.items)
    total_shipped = sum(item.quantity_shipped for item in order.items)
    total_received = sum(item.quantity_received for item in order.items)
    total_resolved = total_received + sum(item.quantity_written_off for item in order.items)

    if total_shipped == 0:
        return order.status
    if total_shipped < total_ordered:
        return "Partially Shipped"
    if total_resolved == 0:
        return "Shipped"
    if total_resolved < total_shipped:
        return "Partially Received"
    return "Received"

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
