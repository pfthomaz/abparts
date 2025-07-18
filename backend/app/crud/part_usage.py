# backend/app/crud/part_usage.py

import uuid
import logging
from typing import List, Optional

from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from .. import models, schemas # Import models and schemas

logger = logging.getLogger(__name__)

def get_part_usage(db: Session, usage_id: uuid.UUID):
    """Retrieve a single part usage record by ID."""
    return db.query(models.PartUsage).filter(models.PartUsage.id == usage_id).first()

def get_part_usages(db: Session, skip: int = 0, limit: int = 100):
    """Retrieve a list of part usage records."""
    return db.query(models.PartUsage).offset(skip).limit(limit).all()

def create_part_usage(db: Session, usage: schemas.PartUsageCreate):
    """Create a new part usage record."""
    # Validate FKs - these checks should ideally be in the router or a service layer
    customer_org = db.query(models.Organization).filter(models.Organization.id == usage.customer_organization_id).first()
    part = db.query(models.Part).filter(models.Part.id == usage.part_id).first()
    warehouse = db.query(models.Warehouse).filter(models.Warehouse.id == usage.warehouse_id).first()
    if not customer_org:
        raise HTTPException(status_code=400, detail="Customer Organization ID not found")
    if not part:
        raise HTTPException(status_code=400, detail="Part ID not found")
    if not warehouse:
        raise HTTPException(status_code=400, detail="Warehouse ID not found")
    if usage.recorded_by_user_id:
        user = db.query(models.User).filter(models.User.id == usage.recorded_by_user_id).first()
        if not user: raise HTTPException(status_code=400, detail="Recorded by User ID not found")

    db_usage = models.PartUsage(**usage.dict())
    try:
        db.add(db_usage)
        db.commit()
        db.refresh(db_usage)
        return db_usage
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating part usage record: {e}")
        raise HTTPException(status_code=400, detail="Error creating part usage record")

def update_part_usage(db: Session, usage_id: uuid.UUID, usage_update: schemas.PartUsageUpdate):
    """Update an existing part usage record."""
    db_usage = db.query(models.PartUsage).filter(models.PartUsage.id == usage_id).first()
    if not db_usage:
        return None # Indicate not found

    update_data = usage_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_usage, key, value)
    try:
        # Re-validate FKs if IDs are updated
        if "customer_organization_id" in update_data:
            customer_org = db.query(models.Organization).filter(models.Organization.id == db_usage.customer_organization_id).first()
            if not customer_org: raise HTTPException(status_code=400, detail="Customer Organization ID not found")
        if "part_id" in update_data:
            part = db.query(models.Part).filter(models.Part.id == db_usage.part_id).first()
            if not part: raise HTTPException(status_code=400, detail="Part ID not found")
        if "recorded_by_user_id" in update_data and db_usage.recorded_by_user_id:
            user = db.query(models.User).filter(models.User.id == db_usage.recorded_by_user_id).first()
            if not user: raise HTTPException(status_code=400, detail="Recorded by User ID not found")

        db.add(db_usage)
        db.commit()
        db.refresh(db_usage)
        return db_usage
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating part usage record: {e}")
        raise HTTPException(status_code=400, detail="Error updating part usage record")

def delete_part_usage(db: Session, usage_id: uuid.UUID):
    """Delete a part usage record by ID."""
    db_usage = db.query(models.PartUsage).filter(models.PartUsage.id == usage_id).first()
    if not db_usage:
        return None # Indicate not found
    try:
        db.delete(db_usage)
        db.commit()
        return {"message": "Part usage record deleted successfully"}
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting part usage record: {e}")
        raise HTTPException(status_code=400, detail="Error deleting part usage record. Check for dependent records.")
def get_part_usage_history(db: Session, part_id: uuid.UUID, organization_id: Optional[uuid.UUID] = None, days: int = 90):
    """
    Get usage history for a specific part.
    
    Args:
        db: Database session
        part_id: Part ID to get usage history for
        organization_id: Optional organization ID to filter usage
        days: Number of days to look back for usage history
        
    Returns:
        List of usage history items
    """
    from datetime import datetime, timedelta
    from sqlalchemy import desc
    
    # Calculate the start date for the history period
    start_date = datetime.now() - timedelta(days=days)
    
    # Query for part usage records
    usage_query = db.query(
        models.PartUsage,
        models.Machine.serial_number.label("machine_serial"),
        models.Warehouse.name.label("warehouse_name")
    ).join(
        models.Warehouse, models.PartUsage.warehouse_id == models.Warehouse.id
    ).outerjoin(  # Use outer join since machine might be null for some usage records
        models.Machine, models.PartUsage.machine_id == models.Machine.id
    ).filter(
        models.PartUsage.part_id == part_id,
        models.PartUsage.usage_date >= start_date
    )
    
    # Filter by organization if provided
    if organization_id:
        usage_query = usage_query.filter(models.PartUsage.customer_organization_id == organization_id)
    
    # Order by usage date descending (most recent first)
    usage_records = usage_query.order_by(desc(models.PartUsage.usage_date)).all()
    
    # Format the results
    usage_history = []
    for usage, machine_serial, warehouse_name in usage_records:
        usage_history.append({
            "id": usage.id,
            "usage_date": usage.usage_date,
            "quantity": usage.quantity,
            "machine_id": usage.machine_id,
            "machine_serial": machine_serial,
            "warehouse_id": usage.warehouse_id,
            "warehouse_name": warehouse_name,
            "notes": usage.notes
        })
    
    return usage_history

def get_part_usage_statistics(db: Session, part_id: uuid.UUID, organization_id: Optional[uuid.UUID] = None, days: int = 90):
    """
    Get usage statistics for a specific part.
    
    Args:
        db: Database session
        part_id: Part ID to get usage statistics for
        organization_id: Optional organization ID to filter usage
        days: Number of days to look back for usage statistics
        
    Returns:
        Dictionary with usage statistics
    """
    from datetime import datetime, timedelta
    from sqlalchemy import func
    from decimal import Decimal
    
    # Calculate the start date for the history period
    start_date = datetime.now() - timedelta(days=days)
    
    # Base query for part usage records
    usage_query = db.query(
        func.sum(models.PartUsage.quantity).label("total_quantity"),
        func.count(models.PartUsage.id).label("usage_count")
    ).filter(
        models.PartUsage.part_id == part_id,
        models.PartUsage.usage_date >= start_date
    )
    
    # Filter by organization if provided
    if organization_id:
        usage_query = usage_query.filter(models.PartUsage.customer_organization_id == organization_id)
    
    # Execute query
    result = usage_query.first()
    
    # Calculate average monthly usage
    total_quantity = result.total_quantity or Decimal('0')
    usage_count = result.usage_count or 0
    
    # Convert days to months (approximate)
    months = days / 30.0
    
    # Calculate average monthly usage
    avg_monthly_usage = total_quantity / Decimal(months) if months > 0 else Decimal('0')
    
    # Get part details
    part = db.query(models.Part).filter(models.Part.id == part_id).first()
    
    # Get current inventory levels
    inventory_query = db.query(func.sum(models.Inventory.current_stock).label("total_stock"))
    inventory_query = inventory_query.filter(models.Inventory.part_id == part_id)
    
    if organization_id:
        inventory_query = inventory_query.join(
            models.Warehouse, models.Inventory.warehouse_id == models.Warehouse.id
        ).filter(models.Warehouse.organization_id == organization_id)
    
    inventory_result = inventory_query.first()
    total_stock = inventory_result.total_stock or Decimal('0')
    
    # Calculate estimated depletion days
    estimated_depletion_days = None
    if avg_monthly_usage > Decimal('0'):
        # Convert monthly usage to daily usage
        daily_usage = avg_monthly_usage / Decimal('30')
        
        # Calculate days until depletion
        if daily_usage > Decimal('0'):
            estimated_depletion_days = int(total_stock / daily_usage)
    
    return {
        "part_id": part_id,
        "part_number": part.part_number if part else None,
        "part_name": part.name if part else None,
        "total_usage_quantity": total_quantity,
        "usage_count": usage_count,
        "avg_monthly_usage": avg_monthly_usage,
        "current_total_stock": total_stock,
        "estimated_depletion_days": estimated_depletion_days,
        "days_analyzed": days
    }

def get_parts_with_low_stock(db: Session, organization_id: Optional[uuid.UUID] = None, threshold_days: int = 30, limit: int = 10):
    """
    Get parts with low stock based on usage patterns.
    
    Args:
        db: Database session
        organization_id: Optional organization ID to filter warehouses
        threshold_days: Threshold for days of stock remaining to trigger suggestion
        limit: Maximum number of parts to return
        
    Returns:
        List of parts with low stock
    """
    from sqlalchemy import desc
    
    # Get all parts
    parts_query = db.query(models.Part)
    parts = parts_query.all()
    
    # Calculate reorder suggestions
    low_stock_parts = []
    
    for part in parts:
        # Get usage statistics
        stats = get_part_usage_statistics(db, part.id, organization_id, days=90)
        
        # Skip parts with no usage history or no inventory
        if not stats["avg_monthly_usage"] or stats["avg_monthly_usage"] <= 0:
            continue
        
        # Check if estimated depletion days is below threshold
        if stats["estimated_depletion_days"] and stats["estimated_depletion_days"] <= threshold_days:
            # Calculate suggested reorder quantity (2 months of usage)
            suggested_reorder_quantity = stats["avg_monthly_usage"] * 2
            
            low_stock_parts.append({
                "part_id": part.id,
                "part_number": part.part_number,
                "part_name": part.name,
                "current_total_stock": stats["current_total_stock"],
                "avg_monthly_usage": stats["avg_monthly_usage"],
                "estimated_depletion_days": stats["estimated_depletion_days"],
                "suggested_reorder_quantity": suggested_reorder_quantity,
                "unit_of_measure": part.unit_of_measure,
                "is_proprietary": part.is_proprietary
            })
    
    # Sort by estimated depletion days (ascending)
    low_stock_parts.sort(key=lambda x: x["estimated_depletion_days"])
    
    # Limit the number of results
    return low_stock_parts[:limit]