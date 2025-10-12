# backend/app/crud/warehouses.py

import uuid
import logging
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from .. import models, schemas

logger = logging.getLogger(__name__)


def get_warehouse(db: Session, warehouse_id: uuid.UUID) -> Optional[models.Warehouse]:
    """Get a single warehouse by ID."""
    return db.query(models.Warehouse).filter(models.Warehouse.id == warehouse_id).first()


def get_warehouses(db: Session, skip: int = 0, limit: int = 100) -> List[models.Warehouse]:
    """Get all warehouses with pagination."""
    return db.query(models.Warehouse).offset(skip).limit(limit).all()


def get_warehouses_by_organization(db: Session, organization_id: uuid.UUID, 
                                 include_inactive: bool = False, skip: int = 0, limit: int = 100) -> List[models.Warehouse]:
    """Get warehouses for a specific organization."""
    query = db.query(models.Warehouse).filter(models.Warehouse.organization_id == organization_id)
    
    if not include_inactive:
        query = query.filter(models.Warehouse.is_active == True)
    
    return query.offset(skip).limit(limit).all()


def search_warehouses(db: Session, search_term: str, organization_id: Optional[uuid.UUID] = None,
                     include_inactive: bool = False, skip: int = 0, limit: int = 100) -> List[models.Warehouse]:
    """Search warehouses by name with optional organization filtering."""
    query = db.query(models.Warehouse).filter(
        or_(
            models.Warehouse.name.ilike(f"%{search_term}%"),
            models.Warehouse.location.ilike(f"%{search_term}%"),
            models.Warehouse.description.ilike(f"%{search_term}%")
        )
    )
    
    if organization_id:
        query = query.filter(models.Warehouse.organization_id == organization_id)
    
    if not include_inactive:
        query = query.filter(models.Warehouse.is_active == True)
    
    return query.offset(skip).limit(limit).all()


def create_warehouse(db: Session, warehouse: "schemas.WarehouseCreate") -> models.Warehouse:
    """Create a new warehouse."""
    # Validate organization exists
    organization = db.query(models.Organization).filter(models.Organization.id == warehouse.organization_id).first()
    if not organization:
        raise ValueError("Organization not found")
    
    # Check for duplicate warehouse name within organization
    existing_warehouse = db.query(models.Warehouse).filter(
        and_(
            models.Warehouse.organization_id == warehouse.organization_id,
            models.Warehouse.name == warehouse.name
        )
    ).first()
    
    if existing_warehouse:
        raise ValueError(f"Warehouse with name '{warehouse.name}' already exists in this organization")
    
    # Create warehouse
    db_warehouse = models.Warehouse(
        organization_id=warehouse.organization_id,
        name=warehouse.name,
        location=warehouse.location,
        description=warehouse.description,
        is_active=warehouse.is_active
    )
    
    db.add(db_warehouse)
    db.commit()
    db.refresh(db_warehouse)
    return db_warehouse


def update_warehouse(db: Session, warehouse_id: uuid.UUID, warehouse_update: "schemas.WarehouseUpdate") -> Optional[models.Warehouse]:
    """Update an existing warehouse."""
    db_warehouse = get_warehouse(db, warehouse_id)
    if not db_warehouse:
        return None
    
    # Check for duplicate name if name is being updated
    if warehouse_update.name and warehouse_update.name != db_warehouse.name:
        existing_warehouse = db.query(models.Warehouse).filter(
            and_(
                models.Warehouse.organization_id == db_warehouse.organization_id,
                models.Warehouse.name == warehouse_update.name,
                models.Warehouse.id != warehouse_id
            )
        ).first()
        
        if existing_warehouse:
            raise ValueError(f"Warehouse with name '{warehouse_update.name}' already exists in this organization")
    
    # Update fields
    update_data = warehouse_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_warehouse, field, value)
    
    db.commit()
    db.refresh(db_warehouse)
    return db_warehouse


def delete_warehouse(db: Session, warehouse_id: uuid.UUID) -> bool:
    """Delete (deactivate) a warehouse."""
    logger.info(f"Starting warehouse deletion for ID: {warehouse_id}")
    db_warehouse = get_warehouse(db, warehouse_id)
    if not db_warehouse:
        logger.warning(f"Warehouse not found: {warehouse_id}")
        return False
    
    # Check if warehouse has inventory items with non-zero stock
    inventory_with_stock = db.query(models.Inventory).filter(
        models.Inventory.warehouse_id == warehouse_id,
        models.Inventory.current_stock > 0
    ).count()
    if inventory_with_stock > 0:
        raise ValueError("Cannot delete warehouse with existing inventory stock. Transfer or adjust inventory to zero first.")
    
    # Clean up any zero-stock inventory records before deletion
    zero_stock_inventory = db.query(models.Inventory).filter(
        models.Inventory.warehouse_id == warehouse_id,
        models.Inventory.current_stock == 0
    )
    zero_stock_count = zero_stock_inventory.count()
    if zero_stock_count > 0:
        logger.info(f"Cleaning up {zero_stock_count} zero-stock inventory records for warehouse {warehouse_id}")
        zero_stock_inventory.delete(synchronize_session=False)
    
    # Check if warehouse has transactions
    transaction_count = db.query(models.Transaction).filter(
        or_(
            models.Transaction.from_warehouse_id == warehouse_id,
            models.Transaction.to_warehouse_id == warehouse_id
        )
    ).count()
    
    if transaction_count > 0:
        raise ValueError("Cannot delete warehouse with existing transactions. Deactivate instead.")
    
    # Check if warehouse has stock adjustments (through inventory items)
    adjustments_count = db.query(models.StockAdjustment).join(
        models.Inventory, models.StockAdjustment.inventory_id == models.Inventory.id
    ).filter(
        models.Inventory.warehouse_id == warehouse_id
    ).count()
    if adjustments_count > 0:
        raise ValueError("Cannot delete warehouse with existing stock adjustments. Deactivate instead.")
    
    # Note: Stocktake and MachineWarehouseAssignment models don't exist in current schema
    # Additional constraint checks can be added here when those models are implemented
    
    # Safe to delete
    logger.info(f"All checks passed, proceeding with warehouse deletion: {warehouse_id}")
    try:
        db.delete(db_warehouse)
        db.commit()
        logger.info(f"Warehouse successfully deleted: {warehouse_id}")
        return True
    except Exception as e:
        logger.error(f"Error during warehouse deletion: {e}")
        db.rollback()
        raise


def activate_warehouse(db: Session, warehouse_id: uuid.UUID) -> Optional[models.Warehouse]:
    """Activate a warehouse."""
    db_warehouse = get_warehouse(db, warehouse_id)
    if not db_warehouse:
        return None
    
    db_warehouse.is_active = True
    db.commit()
    db.refresh(db_warehouse)
    return db_warehouse


def deactivate_warehouse(db: Session, warehouse_id: uuid.UUID) -> Optional[models.Warehouse]:
    """Deactivate a warehouse."""
    db_warehouse = get_warehouse(db, warehouse_id)
    if not db_warehouse:
        return None
    
    db_warehouse.is_active = False
    db.commit()
    db.refresh(db_warehouse)
    return db_warehouse


def get_warehouse_inventory_summary(db: Session, warehouse_id: uuid.UUID) -> dict:
    """Get inventory summary for a warehouse."""
    warehouse = get_warehouse(db, warehouse_id)
    if not warehouse:
        return None
    
    # Get inventory statistics
    inventory_items = db.query(models.Inventory).filter(models.Inventory.warehouse_id == warehouse_id).all()
    
    total_items = len(inventory_items)
    total_stock_value = sum(item.current_stock for item in inventory_items)
    low_stock_items = sum(1 for item in inventory_items if item.current_stock <= item.minimum_stock_recommendation)
    
    return {
        "warehouse_id": warehouse_id,
        "warehouse_name": warehouse.name,
        "total_inventory_items": total_items,
        "total_stock_quantity": float(total_stock_value),
        "low_stock_items_count": low_stock_items,
        "is_active": warehouse.is_active
    }