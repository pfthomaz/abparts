# backend/app/crud/stock_adjustments.py

import uuid
from decimal import Decimal
from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, desc

from .. import models, schemas


def create_stock_adjustment(
    db: Session,
    adjustment_data: schemas.StockAdjustmentCreate,
    current_user_id: uuid.UUID
) -> models.StockAdjustment:
    """
    Create a new stock adjustment with line items.
    Updates inventory quantities and creates transaction records.
    """
    # Verify warehouse exists
    warehouse = db.query(models.Warehouse).filter(
        models.Warehouse.id == adjustment_data.warehouse_id
    ).first()
    
    if not warehouse:
        raise ValueError(f"Warehouse {adjustment_data.warehouse_id} not found")
    
    # Create the adjustment header
    adjustment = models.StockAdjustment(
        warehouse_id=adjustment_data.warehouse_id,
        adjustment_type=models.AdjustmentType(adjustment_data.adjustment_type.value),
        reason=adjustment_data.reason,
        notes=adjustment_data.notes,
        user_id=current_user_id,
        total_items_adjusted=len(adjustment_data.items)
    )
    
    db.add(adjustment)
    db.flush()  # Get the adjustment ID
    
    # Import the calculator to get actual current stock
    from .inventory_calculator import calculate_current_stock
    
    # Process each line item
    for item_data in adjustment_data.items:
        # Get current inventory record (or create if doesn't exist)
        inventory = db.query(models.Inventory).filter(
            and_(
                models.Inventory.warehouse_id == adjustment_data.warehouse_id,
                models.Inventory.part_id == item_data.part_id
            )
        ).first()
        
        if not inventory:
            # Create inventory record if it doesn't exist
            part = db.query(models.Part).filter(models.Part.id == item_data.part_id).first()
            if not part:
                raise ValueError(f"Part {item_data.part_id} not found")
            
            inventory = models.Inventory(
                warehouse_id=adjustment_data.warehouse_id,
                part_id=item_data.part_id,
                current_stock=Decimal('0'),
                unit_of_measure=part.unit_of_measure or 'units'
            )
            db.add(inventory)
            db.flush()
        
        # Calculate actual current stock from transactions and previous adjustments
        quantity_before = calculate_current_stock(db, adjustment_data.warehouse_id, item_data.part_id)
        quantity_after = item_data.quantity_after
        quantity_change = quantity_after - quantity_before
        
        # Create adjustment item
        adjustment_item = models.StockAdjustmentItem(
            stock_adjustment_id=adjustment.id,
            part_id=item_data.part_id,
            quantity_before=quantity_before,
            quantity_after=quantity_after,
            quantity_change=quantity_change,
            reason=item_data.reason
        )
        db.add(adjustment_item)
        
        # Don't update inventory.current_stock directly
        # Stock levels are calculated from adjustments and transactions
        # Just update the timestamp
        inventory.last_updated = datetime.utcnow()
    
    db.commit()
    db.refresh(adjustment)
    
    return adjustment


def get_stock_adjustments(
    db: Session,
    warehouse_id: Optional[uuid.UUID] = None,
    adjustment_type: Optional[str] = None,
    user_id: Optional[uuid.UUID] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    skip: int = 0,
    limit: int = 100
) -> List[dict]:
    """
    Get stock adjustments with optional filtering.
    Returns list of adjustments with basic info (without full item details).
    """
    query = db.query(
        models.StockAdjustment,
        models.Warehouse.name.label("warehouse_name"),
        models.User.username.label("username")
    ).join(
        models.Warehouse,
        models.StockAdjustment.warehouse_id == models.Warehouse.id
    ).join(
        models.User,
        models.StockAdjustment.user_id == models.User.id
    )
    
    # Apply filters
    if warehouse_id:
        query = query.filter(models.StockAdjustment.warehouse_id == warehouse_id)
    
    if adjustment_type:
        query = query.filter(models.StockAdjustment.adjustment_type == adjustment_type)
    
    if user_id:
        query = query.filter(models.StockAdjustment.user_id == user_id)
    
    if start_date:
        query = query.filter(models.StockAdjustment.adjustment_date >= start_date)
    
    if end_date:
        query = query.filter(models.StockAdjustment.adjustment_date <= end_date)
    
    # Order by most recent first
    query = query.order_by(desc(models.StockAdjustment.adjustment_date))
    
    # Pagination
    results = query.offset(skip).limit(limit).all()
    
    # Format results
    adjustments = []
    for adj, warehouse_name, username in results:
        adjustments.append({
            "id": adj.id,
            "warehouse_id": adj.warehouse_id,
            "warehouse_name": warehouse_name,
            "adjustment_type": adj.adjustment_type.value,  # Convert enum to string value
            "reason": adj.reason,
            "user_id": adj.user_id,
            "username": username,
            "adjustment_date": adj.adjustment_date,
            "total_items_adjusted": adj.total_items_adjusted,
            "created_at": adj.created_at
        })
    
    return adjustments


def get_stock_adjustment_by_id(
    db: Session,
    adjustment_id: uuid.UUID
) -> Optional[dict]:
    """
    Get a single stock adjustment with full details including line items.
    """
    adjustment = db.query(models.StockAdjustment).options(
        joinedload(models.StockAdjustment.items).joinedload(models.StockAdjustmentItem.part),
        joinedload(models.StockAdjustment.warehouse),
        joinedload(models.StockAdjustment.user)
    ).filter(
        models.StockAdjustment.id == adjustment_id
    ).first()
    
    if not adjustment:
        return None
    
    # Format response with items
    items = []
    for item in adjustment.items:
        items.append({
            "id": item.id,
            "stock_adjustment_id": item.stock_adjustment_id,
            "part_id": item.part_id,
            "part_number": item.part.part_number,
            "part_name": item.part.name,
            "unit_of_measure": item.part.unit_of_measure or 'units',
            "quantity_before": item.quantity_before,
            "quantity_after": item.quantity_after,
            "quantity_change": item.quantity_change,
            "reason": item.reason,
            "created_at": item.created_at
        })
    
    return {
        "id": adjustment.id,
        "warehouse_id": adjustment.warehouse_id,
        "warehouse_name": adjustment.warehouse.name,
        "adjustment_type": adjustment.adjustment_type.value,  # Convert enum to string value
        "reason": adjustment.reason,
        "notes": adjustment.notes,
        "user_id": adjustment.user_id,
        "username": adjustment.user.username,
        "adjustment_date": adjustment.adjustment_date,
        "total_items_adjusted": adjustment.total_items_adjusted,
        "items": items,
        "created_at": adjustment.created_at,
        "updated_at": adjustment.updated_at
    }


def get_adjustment_history_for_part(
    db: Session,
    part_id: uuid.UUID,
    warehouse_id: Optional[uuid.UUID] = None,
    limit: int = 50
) -> List[dict]:
    """
    Get adjustment history for a specific part.
    """
    query = db.query(
        models.StockAdjustmentItem,
        models.StockAdjustment,
        models.Warehouse.name.label("warehouse_name"),
        models.User.username.label("username")
    ).join(
        models.StockAdjustment,
        models.StockAdjustmentItem.stock_adjustment_id == models.StockAdjustment.id
    ).join(
        models.Warehouse,
        models.StockAdjustment.warehouse_id == models.Warehouse.id
    ).join(
        models.User,
        models.StockAdjustment.user_id == models.User.id
    ).filter(
        models.StockAdjustmentItem.part_id == part_id
    )
    
    if warehouse_id:
        query = query.filter(models.StockAdjustment.warehouse_id == warehouse_id)
    
    query = query.order_by(desc(models.StockAdjustment.adjustment_date))
    results = query.limit(limit).all()
    
    history = []
    for item, adj, warehouse_name, username in results:
        history.append({
            "adjustment_id": adj.id,
            "adjustment_date": adj.adjustment_date,
            "adjustment_type": adj.adjustment_type,
            "warehouse_name": warehouse_name,
            "username": username,
            "quantity_before": item.quantity_before,
            "quantity_after": item.quantity_after,
            "quantity_change": item.quantity_change,
            "reason": item.reason or adj.reason
        })
    
    return history
