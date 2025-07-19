# backend/app/crud/inventory_workflow.py

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

# Stocktake CRUD
def get_stocktake(db: Session, stocktake_id: uuid.UUID):
    """Get a stocktake by ID with related data."""
    stocktake = db.query(
        models.Stocktake,
        models.Warehouse.name.label("warehouse_name"),
        models.Warehouse.location.label("warehouse_location"),
        models.Warehouse.organization_id.label("organization_id"),
        models.Organization.name.label("organization_name"),
        models.User.username.label("scheduled_by_username")
    ).join(
        models.Warehouse, models.Stocktake.warehouse_id == models.Warehouse.id
    ).join(
        models.Organization, models.Warehouse.organization_id == models.Organization.id
    ).join(
        models.User, models.Stocktake.scheduled_by_user_id == models.User.id
    ).filter(
        models.Stocktake.id == stocktake_id
    ).first()
    
    if not stocktake:
        return None
    
    stocktake_obj, warehouse_name, warehouse_location, organization_id, organization_name, scheduled_by_username = stocktake
    
    # Get completed by username if exists
    completed_by_username = None
    if stocktake_obj.completed_by_user_id:
        completed_user = db.query(models.User).filter(models.User.id == stocktake_obj.completed_by_user_id).first()
        completed_by_username = completed_user.username if completed_user else None
    
    # Get stocktake items
    items = get_stocktake_items(db, stocktake_id)
    
    # Calculate metrics
    total_items = len(items)
    items_counted = sum(1 for item in items if item.get("actual_quantity") is not None)
    discrepancy_count = sum(1 for item in items if item.get("discrepancy") is not None and item.get("discrepancy") != 0)
    
    # Calculate total discrepancy value
    total_discrepancy_value = sum(
        item.get("discrepancy_value", 0) for item in items if item.get("discrepancy_value") is not None
    )
    
    result = {
        **stocktake_obj.__dict__,
        "warehouse_name": warehouse_name,
        "warehouse_location": warehouse_location,
        "organization_id": organization_id,
        "organization_name": organization_name,
        "scheduled_by_username": scheduled_by_username,
        "completed_by_username": completed_by_username,
        "total_items": total_items,
        "items_counted": items_counted,
        "discrepancy_count": discrepancy_count,
        "total_discrepancy_value": total_discrepancy_value,
        "items": items
    }
    
    return result

def create_stocktake(db: Session, stocktake: schemas.StocktakeCreate, current_user_id: uuid.UUID):
    """Create a new stocktake."""
    # Check if warehouse exists
    warehouse = db.query(models.Warehouse).filter(models.Warehouse.id == stocktake.warehouse_id).first()
    if not warehouse:
        raise HTTPException(status_code=404, detail="Warehouse not found")
    
    # Set scheduled by user if not provided
    if not stocktake.scheduled_by_user_id:
        stocktake.scheduled_by_user_id = current_user_id
    
    # Create the stocktake
    db_stocktake = models.Stocktake(**stocktake.dict())
    
    try:
        db.add(db_stocktake)
        db.commit()
        db.refresh(db_stocktake)
        
        # Automatically create stocktake items for all inventory in the warehouse
        inventory_items = db.query(models.Inventory).filter(
            models.Inventory.warehouse_id == stocktake.warehouse_id
        ).all()
        
        for inventory in inventory_items:
            stocktake_item = models.StocktakeItem(
                stocktake_id=db_stocktake.id,
                part_id=inventory.part_id,
                expected_quantity=inventory.current_stock
            )
            db.add(stocktake_item)
        
        db.commit()
        
        # Get the stocktake with related data
        result = get_stocktake(db, db_stocktake.id)
        return result
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating stocktake: {e}")
        raise HTTPException(status_code=500, detail=f"Error creating stocktake: {str(e)}")

# Stocktake Item CRUD
def get_stocktake_items(db: Session, stocktake_id: uuid.UUID):
    """Get all items for a specific stocktake."""
    items = db.query(
        models.StocktakeItem,
        models.Part.part_number.label("part_number"),
        models.Part.name.label("part_name"),
        models.Part.part_type.label("part_type"),
        models.Part.unit_of_measure.label("unit_of_measure"),
        models.Part.average_cost.label("unit_price")
    ).join(
        models.Part, models.StocktakeItem.part_id == models.Part.id
    ).filter(
        models.StocktakeItem.stocktake_id == stocktake_id
    ).all()
    
    results = []
    for item, part_number, part_name, part_type, unit_of_measure, unit_price in items:
        # Calculate discrepancy if actual quantity is set
        discrepancy = None
        discrepancy_percentage = None
        discrepancy_value = None
        
        if item.actual_quantity is not None:
            discrepancy = item.actual_quantity - item.expected_quantity
            if item.expected_quantity and item.expected_quantity != 0:
                discrepancy_percentage = (discrepancy / item.expected_quantity) * 100
            if unit_price and discrepancy:
                discrepancy_value = discrepancy * unit_price
        
        # Get counted by username if exists
        counted_by_username = None
        if item.counted_by_user_id:
            counted_user = db.query(models.User).filter(models.User.id == item.counted_by_user_id).first()
            counted_by_username = counted_user.username if counted_user else None
        
        result = {
            **item.__dict__,
            "part_number": part_number,
            "part_name": part_name,
            "part_type": part_type.value if hasattr(part_type, 'value') else part_type,
            "unit_of_measure": unit_of_measure,
            "unit_price": unit_price,
            "discrepancy": discrepancy,
            "discrepancy_percentage": discrepancy_percentage,
            "discrepancy_value": discrepancy_value,
            "counted_by_username": counted_by_username
        }
        
        results.append(result)
    
    return results

def create_inventory_adjustment(db: Session, adjustment: schemas.InventoryAdjustmentCreate, current_user_id: uuid.UUID):
    """Create a new inventory adjustment."""
    # Check if warehouse exists
    warehouse = db.query(models.Warehouse).filter(models.Warehouse.id == adjustment.warehouse_id).first()
    if not warehouse:
        raise HTTPException(status_code=404, detail="Warehouse not found")
    
    # Check if part exists
    part = db.query(models.Part).filter(models.Part.id == adjustment.part_id).first()
    if not part:
        raise HTTPException(status_code=404, detail="Part not found")
    
    # Get current inventory
    inventory = db.query(models.Inventory).filter(
        models.Inventory.warehouse_id == adjustment.warehouse_id,
        models.Inventory.part_id == adjustment.part_id
    ).first()
    
    if not inventory:
        # Create inventory record if it doesn't exist
        inventory = models.Inventory(
            warehouse_id=adjustment.warehouse_id,
            part_id=adjustment.part_id,
            current_stock=Decimal('0'),
            reserved_stock=Decimal('0'),
            reorder_point=Decimal('0'),
            max_stock_level=Decimal('0')
        )
        db.add(inventory)
        db.flush()  # Get the ID without committing
    
    # Calculate new quantities
    previous_quantity = inventory.current_stock
    new_quantity = previous_quantity + adjustment.quantity_change
    
    # Validate that new quantity is not negative
    if new_quantity < 0:
        raise HTTPException(
            status_code=400,
            detail=f"Adjustment would result in negative inventory: {new_quantity}"
        )
    
    # Set adjusted by user if not provided
    if not adjustment.adjusted_by_user_id:
        adjustment.adjusted_by_user_id = current_user_id
    
    # Create the adjustment record
    db_adjustment = models.InventoryAdjustment(
        **adjustment.dict(),
        previous_quantity=previous_quantity,
        new_quantity=new_quantity,
        adjustment_date=datetime.now()
    )
    
    try:
        db.add(db_adjustment)
        
        # Update inventory
        inventory.current_stock = new_quantity
        db.add(inventory)
        
        # Create transaction record
        transaction = models.Transaction(
            transaction_type=models.TransactionType.ADJUSTMENT,
            part_id=adjustment.part_id,
            quantity=adjustment.quantity_change,
            from_warehouse_id=adjustment.warehouse_id if adjustment.quantity_change < 0 else None,
            to_warehouse_id=adjustment.warehouse_id if adjustment.quantity_change > 0 else None,
            performed_by_user_id=current_user_id,
            transaction_date=datetime.now(),
            notes=f"Manual adjustment: {adjustment.reason}"
        )
        
        db.add(transaction)
        db.flush()  # Get transaction ID
        
        # Link adjustment to transaction
        db_adjustment.transaction_id = transaction.id
        db.add(db_adjustment)
        
        db.commit()
        db.refresh(db_adjustment)
        
        return {"message": "Inventory adjustment created successfully", "adjustment_id": db_adjustment.id}
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating inventory adjustment: {e}")
        raise HTTPException(status_code=500, detail=f"Error creating inventory adjustment: {str(e)}")

def create_inventory_alert(db: Session, alert: schemas.InventoryAlertCreate):
    """Create a new inventory alert."""
    # Check if warehouse exists
    warehouse = db.query(models.Warehouse).filter(models.Warehouse.id == alert.warehouse_id).first()
    if not warehouse:
        raise HTTPException(status_code=404, detail="Warehouse not found")
    
    # Check if part exists
    part = db.query(models.Part).filter(models.Part.id == alert.part_id).first()
    if not part:
        raise HTTPException(status_code=404, detail="Part not found")
    
    # Check if similar active alert already exists
    existing_alert = db.query(models.InventoryAlert).filter(
        models.InventoryAlert.warehouse_id == alert.warehouse_id,
        models.InventoryAlert.part_id == alert.part_id,
        models.InventoryAlert.alert_type == alert.alert_type,
        models.InventoryAlert.is_active == True
    ).first()
    
    if existing_alert:
        # Update the existing alert instead of creating a new one
        existing_alert.severity = alert.severity
        existing_alert.threshold_value = alert.threshold_value
        existing_alert.current_value = alert.current_value
        existing_alert.message = alert.message
        existing_alert.updated_at = datetime.now()
        
        try:
            db.add(existing_alert)
            db.commit()
            db.refresh(existing_alert)
            return {"message": "Inventory alert updated", "alert_id": existing_alert.id}
        except Exception as e:
            db.rollback()
            logger.error(f"Error updating existing inventory alert: {e}")
            raise HTTPException(status_code=500, detail=f"Error updating existing inventory alert: {str(e)}")
    
    # Create new alert
    db_alert = models.InventoryAlert(**alert.dict())
    
    try:
        db.add(db_alert)
        db.commit()
        db.refresh(db_alert)
        return {"message": "Inventory alert created successfully", "alert_id": db_alert.id}
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating inventory alert: {e}")
        raise HTTPException(status_code=500, detail=f"Error creating inventory alert: {str(e)}")

def get_stocktakes(db: Session, organization_id: Optional[uuid.UUID] = None,
                 warehouse_id: Optional[uuid.UUID] = None, status: Optional[str] = None,
                 skip: int = 0, limit: int = 100):
    """Get stocktakes with optional filtering."""
    query = db.query(
        models.Stocktake,
        models.Warehouse.name.label("warehouse_name"),
        models.Warehouse.location.label("warehouse_location"),
        models.Warehouse.organization_id.label("organization_id"),
        models.Organization.name.label("organization_name"),
        models.User.username.label("scheduled_by_username")
    ).join(
        models.Warehouse, models.Stocktake.warehouse_id == models.Warehouse.id
    ).join(
        models.Organization, models.Warehouse.organization_id == models.Organization.id
    ).join(
        models.User, models.Stocktake.scheduled_by_user_id == models.User.id
    )
    
    if organization_id:
        query = query.filter(models.Warehouse.organization_id == organization_id)
    
    if warehouse_id:
        query = query.filter(models.Stocktake.warehouse_id == warehouse_id)
    
    if status:
        query = query.filter(models.Stocktake.status == status)
    
    stocktakes = query.order_by(models.Stocktake.scheduled_date.desc()).offset(skip).limit(limit).all()
    
    results = []
    for stocktake, warehouse_name, warehouse_location, organization_id, organization_name, scheduled_by_username in stocktakes:
        # Get completed by username if exists
        completed_by_username = None
        if stocktake.completed_by_user_id:
            completed_user = db.query(models.User).filter(models.User.id == stocktake.completed_by_user_id).first()
            completed_by_username = completed_user.username if completed_user else None
        
        # Get basic metrics without loading all items
        items_count = db.query(models.StocktakeItem).filter(models.StocktakeItem.stocktake_id == stocktake.id).count()
        items_counted = db.query(models.StocktakeItem).filter(
            models.StocktakeItem.stocktake_id == stocktake.id,
            models.StocktakeItem.actual_quantity.isnot(None)
        ).count()
        
        discrepancy_count = db.query(models.StocktakeItem).filter(
            models.StocktakeItem.stocktake_id == stocktake.id,
            models.StocktakeItem.actual_quantity.isnot(None),
            models.StocktakeItem.actual_quantity != models.StocktakeItem.expected_quantity
        ).count()
        
        result = {
            **stocktake.__dict__,
            "warehouse_name": warehouse_name,
            "warehouse_location": warehouse_location,
            "organization_id": organization_id,
            "organization_name": organization_name,
            "scheduled_by_username": scheduled_by_username,
            "completed_by_username": completed_by_username,
            "total_items": items_count,
            "items_counted": items_counted,
            "discrepancy_count": discrepancy_count,
            "items": []  # Don't load items for list view for performance
        }
        
        results.append(result)
    
    return results

def update_stocktake(db: Session, stocktake_id: uuid.UUID, stocktake_update: schemas.StocktakeUpdate):
    """Update a stocktake."""
    db_stocktake = db.query(Stocktake).filter(Stocktake.id == stocktake_id).first()
    if not db_stocktake:
        return None
    
    update_data = stocktake_update.dict(exclude_unset=True)
    
    # Validate status transitions
    if "status" in update_data:
        current_status = db_stocktake.status
        new_status = update_data["status"]
        
        # Validate status transitions
        valid_transitions = {
            StocktakeStatus.PLANNED: [StocktakeStatus.IN_PROGRESS, StocktakeStatus.CANCELLED],
            StocktakeStatus.IN_PROGRESS: [StocktakeStatus.COMPLETED, StocktakeStatus.CANCELLED],
            StocktakeStatus.COMPLETED: [],  # Cannot change from completed
            StocktakeStatus.CANCELLED: []   # Cannot change from cancelled
        }
        
        if new_status not in valid_transitions.get(current_status, []):
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid status transition from {current_status.value} to {new_status}"
            )
        
        # If completing the stocktake, ensure all items have been counted
        if new_status == StocktakeStatus.COMPLETED:
            uncounted_items = db.query(StocktakeItem).filter(
                StocktakeItem.stocktake_id == stocktake_id,
                StocktakeItem.actual_quantity.is_(None)
            ).count()
            
            if uncounted_items > 0:
                raise HTTPException(
                    status_code=400,
                    detail=f"Cannot complete stocktake: {uncounted_items} items have not been counted"
                )
    
    for key, value in update_data.items():
        setattr(db_stocktake, key, value)
    
    try:
        db.add(db_stocktake)
        db.commit()
        db.refresh(db_stocktake)
        
        # Get the stocktake with related data
        result = get_stocktake(db, db_stocktake.id)
        return result
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating stocktake: {e}")
        raise HTTPException(status_code=500, detail=f"Error updating stocktake: {str(e)}")

def delete_stocktake(db: Session, stocktake_id: uuid.UUID):
    """Delete a stocktake."""
    db_stocktake = db.query(Stocktake).filter(Stocktake.id == stocktake_id).first()
    if not db_stocktake:
        return None
    
    # Check if stocktake can be deleted (only if status is PLANNED or CANCELLED)
    if db_stocktake.status not in [StocktakeStatus.PLANNED, StocktakeStatus.CANCELLED]:
        raise HTTPException(
            status_code=400, 
            detail="Cannot delete stocktake that is in progress or completed"
        )
    
    try:
        # Delete stocktake items first
        db.query(StocktakeItem).filter(StocktakeItem.stocktake_id == stocktake_id).delete()
        
        # Delete the stocktake
        db.delete(db_stocktake)
        db.commit()
        return {"message": "Stocktake deleted successfully"}
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting stocktake: {e}")
        raise HTTPException(status_code=500, detail=f"Error deleting stocktake: {str(e)}")

def update_stocktake_item(db: Session, item_id: uuid.UUID, item_update: schemas.StocktakeItemUpdate, current_user_id: uuid.UUID):
    """Update a stocktake item with actual count."""
    db_item = db.query(StocktakeItem).filter(StocktakeItem.id == item_id).first()
    if not db_item:
        return None
    
    # Check if stocktake is in a state that allows updates
    stocktake = db.query(Stocktake).filter(Stocktake.id == db_item.stocktake_id).first()
    if not stocktake or stocktake.status not in [StocktakeStatus.PLANNED, StocktakeStatus.IN_PROGRESS]:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot update item: stocktake is in {stocktake.status.value} status"
        )
    
    # If stocktake is still in PLANNED status, change it to IN_PROGRESS
    if stocktake.status == StocktakeStatus.PLANNED:
        stocktake.status = StocktakeStatus.IN_PROGRESS
        db.add(stocktake)
    
    # Update the item
    db_item.actual_quantity = item_update.actual_quantity
    db_item.notes = item_update.notes
    db_item.counted_at = datetime.now()
    db_item.counted_by_user_id = current_user_id
    
    try:
        db.add(db_item)
        db.commit()
        db.refresh(db_item)
        
        # Get the item with related data
        part = db.query(models.Part).filter(models.Part.id == db_item.part_id).first()
        
        # Calculate discrepancy
        discrepancy = db_item.actual_quantity - db_item.expected_quantity
        discrepancy_percentage = None
        if db_item.expected_quantity and db_item.expected_quantity != 0:
            discrepancy_percentage = (discrepancy / db_item.expected_quantity) * 100
        
        # Calculate discrepancy value
        discrepancy_value = None
        if part and part.average_cost:
            discrepancy_value = discrepancy * part.average_cost
        
        # Get counted by username
        counted_user = db.query(models.User).filter(models.User.id == db_item.counted_by_user_id).first()
        counted_by_username = counted_user.username if counted_user else None
        
        result = {
            **db_item.__dict__,
            "part_number": part.part_number,
            "part_name": part.name,
            "part_type": part.part_type.value if hasattr(part.part_type, 'value') else part.part_type,
            "unit_of_measure": part.unit_of_measure,
            "unit_price": part.average_cost,
            "discrepancy": discrepancy,
            "discrepancy_percentage": discrepancy_percentage,
            "discrepancy_value": discrepancy_value,
            "counted_by_username": counted_by_username
        }
        
        return result
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating stocktake item: {e}")
        raise HTTPException(status_code=500, detail=f"Error updating stocktake item: {str(e)}")

def batch_update_stocktake_items(db: Session, stocktake_id: uuid.UUID, batch_update: schemas.BatchStocktakeItemUpdate, current_user_id: uuid.UUID):
    """Update multiple stocktake items in a single operation."""
    # Check if stocktake exists and is in a state that allows updates
    stocktake = db.query(Stocktake).filter(Stocktake.id == stocktake_id).first()
    if not stocktake:
        raise HTTPException(status_code=404, detail="Stocktake not found")
    
    if stocktake.status not in [StocktakeStatus.PLANNED, StocktakeStatus.IN_PROGRESS]:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot update items: stocktake is in {stocktake.status.value} status"
        )
    
    # If stocktake is still in PLANNED status, change it to IN_PROGRESS
    if stocktake.status == StocktakeStatus.PLANNED:
        stocktake.status = StocktakeStatus.IN_PROGRESS
        db.add(stocktake)
    
    updated_items = []
    
    try:
        for item_data in batch_update.items:
            item_id = item_data.get("item_id")
            actual_quantity = item_data.get("actual_quantity")
            notes = item_data.get("notes")
            
            # Get the stocktake item
            db_item = db.query(StocktakeItem).filter(
                StocktakeItem.id == item_id,
                StocktakeItem.stocktake_id == stocktake_id
            ).first()
            
            if not db_item:
                continue
            
            # Update the item
            db_item.actual_quantity = actual_quantity
            db_item.notes = notes
            db_item.counted_at = datetime.now()
            db_item.counted_by_user_id = current_user_id
            
            db.add(db_item)
            
            # Add to updated items list
            updated_items.append(item_id)
        
        db.commit()
        
        # Get the stocktake with all updated items
        result = get_stocktake(db, stocktake_id)
        return result
    except Exception as e:
        db.rollback()
        logger.error(f"Error batch updating stocktake items: {e}")
        raise HTTPException(status_code=500, detail=f"Error batch updating stocktake items: {str(e)}")

def complete_stocktake(db: Session, stocktake_id: uuid.UUID, current_user_id: uuid.UUID, apply_adjustments: bool = False):
    """Complete a stocktake and optionally apply inventory adjustments."""
    # Check if stocktake exists and is in progress
    stocktake = db.query(Stocktake).filter(Stocktake.id == stocktake_id).first()
    if not stocktake:
        raise HTTPException(status_code=404, detail="Stocktake not found")
    
    if stocktake.status != StocktakeStatus.IN_PROGRESS:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot complete stocktake: stocktake is in {stocktake.status.value} status"
        )
    
    # Check if all items have been counted
    uncounted_items = db.query(StocktakeItem).filter(
        StocktakeItem.stocktake_id == stocktake_id,
        StocktakeItem.actual_quantity.is_(None)
    ).count()
    
    if uncounted_items > 0:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot complete stocktake: {uncounted_items} items have not been counted"
        )
    
    try:
        # Get all items with discrepancies
        items_with_discrepancies = db.query(StocktakeItem).filter(
            StocktakeItem.stocktake_id == stocktake_id,
            StocktakeItem.actual_quantity != StocktakeItem.expected_quantity
        ).all()
        
        # If apply_adjustments is True, create inventory adjustments
        if apply_adjustments and items_with_discrepancies:
            for item in items_with_discrepancies:
                # Get current inventory
                inventory = db.query(models.Inventory).filter(
                    models.Inventory.warehouse_id == stocktake.warehouse_id,
                    models.Inventory.part_id == item.part_id
                ).first()
                
                if not inventory:
                    continue
                
                # Calculate adjustment
                quantity_change = item.actual_quantity - item.expected_quantity
                previous_quantity = inventory.current_stock
                new_quantity = previous_quantity + quantity_change
                
                # Create adjustment record
                adjustment = InventoryAdjustment(
                    warehouse_id=stocktake.warehouse_id,
                    part_id=item.part_id,
                    quantity_change=quantity_change,
                    previous_quantity=previous_quantity,
                    new_quantity=new_quantity,
                    reason="Stocktake adjustment",
                    notes=f"Stocktake ID: {stocktake_id}",
                    adjusted_by_user_id=current_user_id,
                    adjustment_date=datetime.now(),
                    stocktake_id=stocktake_id
                )
                
                db.add(adjustment)
                
                # Update inventory
                inventory.current_stock = new_quantity
                db.add(inventory)
                
                # Create inventory alert if significant discrepancy
                discrepancy_percentage = abs(quantity_change / item.expected_quantity * 100) if item.expected_quantity else 0
                
                if discrepancy_percentage > 10:  # More than 10% discrepancy
                    severity = InventoryAlertSeverity.MEDIUM
                    if discrepancy_percentage > 25:  # More than 25% discrepancy
                        severity = InventoryAlertSeverity.HIGH
                    
                    alert = InventoryAlert(
                        warehouse_id=stocktake.warehouse_id,
                        part_id=item.part_id,
                        alert_type=InventoryAlertType.DISCREPANCY,
                        severity=severity,
                        threshold_value=item.expected_quantity,
                        current_value=item.actual_quantity,
                        message=f"Stocktake found {discrepancy_percentage:.1f}% discrepancy",
                        is_active=True
                    )
                    
                    db.add(alert)
        
        # Update stocktake status
        stocktake.status = StocktakeStatus.COMPLETED
        stocktake.completed_date = datetime.now()
        stocktake.completed_by_user_id = current_user_id
        
        db.add(stocktake)
        db.commit()
        
        # Get the stocktake with related data
        result = get_stocktake(db, stocktake_id)
        return result
    except Exception as e:
        db.rollback()
        logger.error(f"Error completing stocktake: {e}")
        raise HTTPException(status_code=500, detail=f"Error completing stocktake: {str(e)}")

def get_inventory_alerts(db: Session, organization_id: Optional[uuid.UUID] = None,
                      warehouse_id: Optional[uuid.UUID] = None, part_id: Optional[uuid.UUID] = None,
                      alert_type: Optional[str] = None, severity: Optional[str] = None,
                      active_only: bool = True, skip: int = 0, limit: int = 100):
    """Get inventory alerts with optional filtering."""
    query = db.query(
        InventoryAlert,
        models.Warehouse.name.label("warehouse_name"),
        models.Warehouse.organization_id.label("organization_id"),
        models.Organization.name.label("organization_name"),
        models.Part.part_number.label("part_number"),
        models.Part.name.label("part_name"),
        models.Part.part_type.label("part_type"),
        models.Part.unit_of_measure.label("unit_of_measure")
    ).join(
        models.Warehouse, InventoryAlert.warehouse_id == models.Warehouse.id
    ).join(
        models.Organization, models.Warehouse.organization_id == models.Organization.id
    ).join(
        models.Part, InventoryAlert.part_id == models.Part.id
    )
    
    if organization_id:
        query = query.filter(models.Warehouse.organization_id == organization_id)
    
    if warehouse_id:
        query = query.filter(InventoryAlert.warehouse_id == warehouse_id)
    
    if part_id:
        query = query.filter(InventoryAlert.part_id == part_id)
    
    if alert_type:
        query = query.filter(InventoryAlert.alert_type == alert_type)
    
    if severity:
        query = query.filter(InventoryAlert.severity == severity)
    
    if active_only:
        query = query.filter(InventoryAlert.is_active == True)
    
    alerts = query.order_by(InventoryAlert.created_at.desc()).offset(skip).limit(limit).all()
    
    results = []
    for alert, warehouse_name, organization_id, organization_name, part_number, part_name, part_type, unit_of_measure in alerts:
        # Get resolved by username if exists
        resolved_by_username = None
        if alert.resolved_by_user_id:
            resolved_user = db.query(models.User).filter(models.User.id == alert.resolved_by_user_id).first()
            resolved_by_username = resolved_user.username if resolved_user else None
        
        result = {
            **alert.__dict__,
            "warehouse_name": warehouse_name,
            "organization_id": organization_id,
            "organization_name": organization_name,
            "part_number": part_number,
            "part_name": part_name,
            "part_type": part_type.value if hasattr(part_type, 'value') else part_type,
            "unit_of_measure": unit_of_measure,
            "resolved_by_username": resolved_by_username
        }
        
        results.append(result)
    
    return results

def update_inventory_alert(db: Session, alert_id: uuid.UUID, alert_update: schemas.InventoryAlertUpdate):
    """Update an inventory alert."""
    db_alert = db.query(InventoryAlert).filter(InventoryAlert.id == alert_id).first()
    if not db_alert:
        return None
    
    update_data = alert_update.dict(exclude_unset=True)
    
    # If resolving the alert, set resolved_at
    if "is_active" in update_data and update_data["is_active"] is False and db_alert.is_active is True:
        update_data["resolved_at"] = datetime.now()
    
    for key, value in update_data.items():
        setattr(db_alert, key, value)
    
    try:
        db.add(db_alert)
        db.commit()
        db.refresh(db_alert)
        return {"message": "Inventory alert updated successfully", "alert_id": db_alert.id}
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating inventory alert: {e}")
        raise HTTPException(status_code=500, detail=f"Error updating inventory alert: {str(e)}")

def get_inventory_adjustments(db: Session, organization_id: Optional[uuid.UUID] = None,
                           warehouse_id: Optional[uuid.UUID] = None, part_id: Optional[uuid.UUID] = None,
                           adjusted_by_user_id: Optional[uuid.UUID] = None, stocktake_id: Optional[uuid.UUID] = None,
                           skip: int = 0, limit: int = 100):
    """Get inventory adjustments with optional filtering."""
    query = db.query(
        InventoryAdjustment,
        models.Warehouse.name.label("warehouse_name"),
        models.Warehouse.organization_id.label("organization_id"),
        models.Organization.name.label("organization_name"),
        models.Part.part_number.label("part_number"),
        models.Part.name.label("part_name"),
        models.Part.part_type.label("part_type"),
        models.Part.unit_of_measure.label("unit_of_measure"),
        models.User.username.label("adjusted_by_username")
    ).join(
        models.Warehouse, InventoryAdjustment.warehouse_id == models.Warehouse.id
    ).join(
        models.Organization, models.Warehouse.organization_id == models.Organization.id
    ).join(
        models.Part, InventoryAdjustment.part_id == models.Part.id
    ).join(
        models.User, InventoryAdjustment.adjusted_by_user_id == models.User.id
    )
    
    if organization_id:
        query = query.filter(models.Warehouse.organization_id == organization_id)
    
    if warehouse_id:
        query = query.filter(InventoryAdjustment.warehouse_id == warehouse_id)
    
    if part_id:
        query = query.filter(InventoryAdjustment.part_id == part_id)
    
    if adjusted_by_user_id:
        query = query.filter(InventoryAdjustment.adjusted_by_user_id == adjusted_by_user_id)
    
    if stocktake_id:
        query = query.filter(InventoryAdjustment.stocktake_id == stocktake_id)
    
    adjustments = query.order_by(InventoryAdjustment.adjustment_date.desc()).offset(skip).limit(limit).all()
    
    results = []
    for adjustment, warehouse_name, organization_id, organization_name, part_number, part_name, part_type, unit_of_measure, adjusted_by_username in adjustments:
        result = {
            **adjustment.__dict__,
            "warehouse_name": warehouse_name,
            "organization_id": organization_id,
            "organization_name": organization_name,
            "part_number": part_number,
            "part_name": part_name,
            "part_type": part_type.value if hasattr(part_type, 'value') else part_type,
            "unit_of_measure": unit_of_measure,
            "adjusted_by_username": adjusted_by_username
        }
        
        results.append(result)
    
    return results

def batch_create_inventory_adjustments(db: Session, batch_adjustment: schemas.BatchInventoryAdjustment, current_user_id: uuid.UUID):
    """Create multiple inventory adjustments in a single operation."""
    # Check if warehouse exists
    warehouse = db.query(models.Warehouse).filter(models.Warehouse.id == batch_adjustment.warehouse_id).first()
    if not warehouse:
        raise HTTPException(status_code=404, detail="Warehouse not found")
    
    created_adjustments = []
    
    try:
        for adjustment_data in batch_adjustment.adjustments:
            part_id = adjustment_data.get("part_id")
            quantity_change = Decimal(str(adjustment_data.get("quantity_change")))
            reason = adjustment_data.get("reason")
            notes = adjustment_data.get("notes")
            
            # Check if part exists
            part = db.query(models.Part).filter(models.Part.id == part_id).first()
            if not part:
                continue  # Skip invalid parts
            
            # Get current inventory
            inventory = db.query(models.Inventory).filter(
                models.Inventory.warehouse_id == batch_adjustment.warehouse_id,
                models.Inventory.part_id == part_id
            ).first()
            
            if not inventory:
                # Create inventory record if it doesn't exist
                inventory = models.Inventory(
                    warehouse_id=batch_adjustment.warehouse_id,
                    part_id=part_id,
                    current_stock=Decimal('0'),
                    reserved_stock=Decimal('0'),
                    reorder_point=Decimal('0'),
                    max_stock_level=Decimal('0')
                )
                db.add(inventory)
                db.flush()
            
            # Calculate new quantities
            previous_quantity = inventory.current_stock
            new_quantity = previous_quantity + quantity_change
            
            # Skip if new quantity would be negative
            if new_quantity < 0:
                continue
            
            # Create the adjustment record
            db_adjustment = InventoryAdjustment(
                warehouse_id=batch_adjustment.warehouse_id,
                part_id=part_id,
                quantity_change=quantity_change,
                previous_quantity=previous_quantity,
                new_quantity=new_quantity,
                reason=reason,
                notes=notes,
                adjusted_by_user_id=current_user_id,
                adjustment_date=datetime.now()
            )
            
            db.add(db_adjustment)
            
            # Update inventory
            inventory.current_stock = new_quantity
            db.add(inventory)
            
            # Create transaction record
            transaction = models.Transaction(
                transaction_type=models.TransactionType.ADJUSTMENT,
                part_id=part_id,
                quantity=quantity_change,
                from_warehouse_id=batch_adjustment.warehouse_id if quantity_change < 0 else None,
                to_warehouse_id=batch_adjustment.warehouse_id if quantity_change > 0 else None,
                performed_by_user_id=current_user_id,
                transaction_date=datetime.now(),
                notes=f"Batch adjustment: {reason}"
            )
            
            db.add(transaction)
            db.flush()
            
            # Link adjustment to transaction
            db_adjustment.transaction_id = transaction.id
            db.add(db_adjustment)
            
            created_adjustments.append(db_adjustment.id)
        
        db.commit()
        
        # Return summary
        return {"message": f"Created {len(created_adjustments)} inventory adjustments", "adjustment_ids": created_adjustments}
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating batch inventory adjustments: {e}")
        raise HTTPException(status_code=500, detail=f"Error creating batch inventory adjustments: {str(e)}")

def get_inventory_analytics(db: Session, request: schemas.InventoryAnalyticsRequest):
    """Get inventory analytics and insights."""
    # For now, return a basic analytics structure
    # This would be expanded with actual calculations
    return schemas.InventoryAnalytics(
        total_inventory_value=Decimal('0'),
        total_parts_count=0,
        low_stock_count=0,
        stockout_count=0,
        excess_stock_count=0,
        inventory_by_part_type={},
        inventory_by_warehouse={},
        top_moving_parts=[],
        slow_moving_parts=[],
        recent_adjustments=[],
        stocktake_accuracy=None
    )

def generate_inventory_alerts(db: Session, organization_id: Optional[uuid.UUID] = None):
    """Generate inventory alerts based on current stock levels and thresholds."""
    # For now, return a basic response
    # This would be expanded with actual alert generation logic
    return {"alerts_created": 0, "message": "Alert generation completed"}