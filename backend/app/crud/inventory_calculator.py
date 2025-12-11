# backend/app/crud/inventory_calculator.py

import uuid
from decimal import Decimal
from typing import Dict, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, case
from datetime import datetime

from .. import models


def calculate_current_stock(
    db: Session,
    warehouse_id: uuid.UUID,
    part_id: uuid.UUID,
    as_of_date: Optional[datetime] = None
) -> Decimal:
    """
    Calculate current stock for a part in a warehouse by summing all transactions and adjustments.
    
    This is the single source of truth for inventory levels.
    
    Logic:
    1. Start with the last stock adjustment (if any) as the baseline
    2. Add all transactions after that adjustment:
       - Purchases/Creation: + quantity (to_warehouse_id matches)
       - Transfers IN: + quantity (to_warehouse_id matches)
       - Transfers OUT: - quantity (from_warehouse_id matches)
       - Consumption: - quantity (from_warehouse_id matches)
    
    Args:
        db: Database session
        warehouse_id: Warehouse to calculate stock for
        part_id: Part to calculate stock for
        as_of_date: Calculate stock as of this date (default: now)
    
    Returns:
        Current stock quantity as Decimal
    """
    if as_of_date is None:
        as_of_date = datetime.utcnow()
    
    # Step 1: Find the most recent stock adjustment for this part/warehouse
    last_adjustment = db.query(
        models.StockAdjustmentItem.quantity_after,
        models.StockAdjustment.adjustment_date
    ).join(
        models.StockAdjustment,
        models.StockAdjustmentItem.stock_adjustment_id == models.StockAdjustment.id
    ).filter(
        and_(
            models.StockAdjustment.warehouse_id == warehouse_id,
            models.StockAdjustmentItem.part_id == part_id,
            models.StockAdjustment.adjustment_date <= as_of_date
        )
    ).order_by(
        models.StockAdjustment.adjustment_date.desc()
    ).first()
    
    if last_adjustment:
        baseline_stock = last_adjustment.quantity_after
        baseline_date = last_adjustment.adjustment_date
    else:
        # No adjustments found, start from zero
        baseline_stock = Decimal('0')
        baseline_date = datetime.min
    
    # Step 2: Sum all transactions after the last adjustment
    # Transactions increase stock when to_warehouse_id matches (purchases, transfers in)
    # Transactions decrease stock when from_warehouse_id matches (consumption, transfers out)
    
    transaction_sum = db.query(
        func.coalesce(
            func.sum(
                case(
                    # Incoming: to_warehouse matches
                    (models.Transaction.to_warehouse_id == warehouse_id, models.Transaction.quantity),
                    # Outgoing: from_warehouse matches
                    (models.Transaction.from_warehouse_id == warehouse_id, -models.Transaction.quantity),
                    else_=Decimal('0')
                )
            ),
            Decimal('0')
        )
    ).filter(
        and_(
            models.Transaction.part_id == part_id,
            models.Transaction.transaction_date > baseline_date,
            models.Transaction.transaction_date <= as_of_date,
            or_(
                models.Transaction.to_warehouse_id == warehouse_id,
                models.Transaction.from_warehouse_id == warehouse_id
            )
        )
    ).scalar()
    
    current_stock = baseline_stock + (transaction_sum or Decimal('0'))
    
    return current_stock


def calculate_all_warehouse_stock(
    db: Session,
    warehouse_id: uuid.UUID,
    as_of_date: Optional[datetime] = None
) -> Dict[uuid.UUID, Decimal]:
    """
    Calculate current stock for all parts in a warehouse.
    
    Returns:
        Dictionary mapping part_id to current stock quantity
    """
    if as_of_date is None:
        as_of_date = datetime.utcnow()
    
    # Get all parts that have ever been in this warehouse
    # (from transactions, adjustments, or inventory records)
    part_ids = set()
    
    # From transactions
    transaction_parts = db.query(models.Transaction.part_id).filter(
        or_(
            models.Transaction.to_warehouse_id == warehouse_id,
            models.Transaction.from_warehouse_id == warehouse_id
        )
    ).distinct().all()
    part_ids.update([p[0] for p in transaction_parts])
    
    # From adjustments
    adjustment_parts = db.query(models.StockAdjustmentItem.part_id).join(
        models.StockAdjustment
    ).filter(
        models.StockAdjustment.warehouse_id == warehouse_id
    ).distinct().all()
    part_ids.update([p[0] for p in adjustment_parts])
    
    # From inventory records
    inventory_parts = db.query(models.Inventory.part_id).filter(
        models.Inventory.warehouse_id == warehouse_id
    ).distinct().all()
    part_ids.update([p[0] for p in inventory_parts])
    
    # Calculate stock for each part
    stock_levels = {}
    for part_id in part_ids:
        stock = calculate_current_stock(db, warehouse_id, part_id, as_of_date)
        if stock != 0:  # Only include parts with non-zero stock
            stock_levels[part_id] = stock
    
    return stock_levels


def refresh_inventory_cache(
    db: Session,
    warehouse_id: Optional[uuid.UUID] = None,
    part_id: Optional[uuid.UUID] = None
) -> int:
    """
    Refresh the cached current_stock values in the inventory table.
    
    This is optional - the system works without it, but caching improves performance.
    
    Args:
        db: Database session
        warehouse_id: Only refresh this warehouse (optional)
        part_id: Only refresh this part (optional)
    
    Returns:
        Number of inventory records updated
    """
    query = db.query(models.Inventory)
    
    if warehouse_id:
        query = query.filter(models.Inventory.warehouse_id == warehouse_id)
    
    if part_id:
        query = query.filter(models.Inventory.part_id == part_id)
    
    inventory_records = query.all()
    updated_count = 0
    
    for inventory in inventory_records:
        calculated_stock = calculate_current_stock(
            db,
            inventory.warehouse_id,
            inventory.part_id
        )
        
        if inventory.current_stock != calculated_stock:
            inventory.current_stock = calculated_stock
            inventory.last_updated = datetime.utcnow()
            updated_count += 1
    
    if updated_count > 0:
        db.commit()
    
    return updated_count


def get_inventory_with_calculated_stock(
    db: Session,
    warehouse_id: Optional[uuid.UUID] = None,
    part_id: Optional[uuid.UUID] = None,
    include_zero_stock: bool = False
) -> list:
    """
    Get inventory records with calculated (not cached) stock levels.
    
    This is the recommended way to get accurate inventory data.
    """
    # Build base query for inventory records
    query = db.query(models.Inventory)
    
    if warehouse_id:
        query = query.filter(models.Inventory.warehouse_id == warehouse_id)
    
    if part_id:
        query = query.filter(models.Inventory.part_id == part_id)
    
    inventory_records = query.all()
    
    # Calculate actual stock for each record
    results = []
    for inventory in inventory_records:
        calculated_stock = calculate_current_stock(
            db,
            inventory.warehouse_id,
            inventory.part_id
        )
        
        if include_zero_stock or calculated_stock > 0:
            results.append({
                'warehouse_id': inventory.warehouse_id,
                'part_id': inventory.part_id,
                'current_stock': calculated_stock,  # Use calculated value
                'cached_stock': inventory.current_stock,  # Show cached value for comparison
                'unit_of_measure': inventory.unit_of_measure,
                'last_updated': inventory.last_updated
            })
    
    return results
