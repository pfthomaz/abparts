# backend/app/crud/inventory.py

import uuid
import logging
from typing import List, Optional

from sqlalchemy.orm import Session
from sqlalchemy import func, case, or_
from fastapi import HTTPException, status

from .. import models, schemas # Import models and schemas

logger = logging.getLogger(__name__)

def get_inventory_item(db: Session, inventory_id: uuid.UUID):
    """Retrieve a single inventory item by ID."""
    return db.query(models.Inventory).filter(models.Inventory.id == inventory_id).first()

def get_inventory_items(db: Session, skip: int = 0, limit: int = 100):
    """Retrieve a list of inventory items."""
    return db.query(models.Inventory).offset(skip).limit(limit).all()

def create_inventory_item(db: Session, item: schemas.InventoryCreate):
    """Create a new inventory item."""
    # Validate FKs - these checks should ideally be in the router or a service layer
    # but for direct CRUD function, they are fine here for simplicity.
    warehouse = db.query(models.Warehouse).filter(models.Warehouse.id == item.warehouse_id).first()
    part = db.query(models.Part).filter(models.Part.id == item.part_id).first()
    if not warehouse:
        raise HTTPException(status_code=400, detail="Warehouse ID not found")
    if not part:
        raise HTTPException(status_code=400, detail="Part ID not found")

    db_item = models.Inventory(**item.dict())
    try:
        db.add(db_item)
        db.commit()
        db.refresh(db_item)
        return db_item
    except Exception as e:
        db.rollback()
        if "duplicate key value violates unique constraint" in str(e):
            raise HTTPException(status_code=409, detail="Inventory for this warehouse and part already exists")
        logger.error(f"Error creating inventory item: {e}")
        raise HTTPException(status_code=400, detail="Error creating inventory item")

def update_inventory_item(db: Session, inventory_id: uuid.UUID, item_update: schemas.InventoryUpdate):
    """Update an existing inventory item."""
    db_item = db.query(models.Inventory).filter(models.Inventory.id == inventory_id).first()
    if not db_item:
        return None # Indicate not found

    update_data = item_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_item, key, value)
    try:
        # Re-validate FKs if warehouse_id or part_id are updated
        if "warehouse_id" in update_data:
            warehouse = db.query(models.Warehouse).filter(models.Warehouse.id == db_item.warehouse_id).first()
            if not warehouse: raise HTTPException(status_code=400, detail="Warehouse ID not found")
        if "part_id" in update_data:
            part = db.query(models.Part).filter(models.Part.id == db_item.part_id).first()
            if not part: raise HTTPException(status_code=400, detail="Part ID not found")

        db.add(db_item)
        db.commit()
        db.refresh(db_item)
        return db_item
    except Exception as e:
        db.rollback()
        if "duplicate key value violates unique constraint" in str(e):
            raise HTTPException(status_code=409, detail="Inventory for this warehouse and part already exists")
        logger.error(f"Error updating inventory item: {e}")
        raise HTTPException(status_code=400, detail="Error updating inventory item")

def delete_inventory_item(db: Session, inventory_id: uuid.UUID):
    """Delete an inventory item by ID."""
    db_item = db.query(models.Inventory).filter(models.Inventory.id == inventory_id).first()
    if not db_item:
        return None # Indicate not found
    try:
        db.delete(db_item)
        db.commit()
        return {"message": "Inventory item deleted successfully"}
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting inventory item: {e}")
        raise HTTPException(status_code=400, detail="Error deleting inventory item.")


def get_stocktake_worksheet_items(db: Session, organization_id: uuid.UUID) -> List[schemas.StocktakeWorksheetItemResponse]:
    """
    Retrieve inventory items for a stocktake worksheet for a given organization.
    Includes part details (number, name) and current stock across all warehouses.
    """
    # Fetch inventory items for the organization's warehouses, joining with Part and Warehouse
    results = db.query(
        models.Inventory.id, # inventory_id
        models.Part.id,      # part_id
        models.Part.part_number,
        models.Part.name,    # part_name
        models.Inventory.current_stock, # system_quantity
        models.Warehouse.name # warehouse_name
    ).join(models.Part, models.Inventory.part_id == models.Part.id)\
     .join(models.Warehouse, models.Inventory.warehouse_id == models.Warehouse.id)\
     .filter(models.Warehouse.organization_id == organization_id)\
     .order_by(models.Part.part_number, models.Warehouse.name)\
     .all()

    if not results:
        return []

    # Map results to the Pydantic schema
    worksheet_items = [
        schemas.StocktakeWorksheetItemResponse(
            inventory_id=row[0],
            part_id=row[1],
            part_number=row[2],
            part_name=row[3],
            system_quantity=row[4],
            warehouse_name=row[5]
        ) for row in results
    ]
    return worksheet_items


# --- Warehouse-specific inventory functions ---

def get_inventory_by_warehouse(db: Session, warehouse_id: uuid.UUID, skip: int = 0, limit: int = 100) -> List[models.Inventory]:
    """Get all inventory items for a specific warehouse."""
    return db.query(models.Inventory).filter(
        models.Inventory.warehouse_id == warehouse_id
    ).offset(skip).limit(limit).all()


def get_inventory_by_organization(db: Session, organization_id: uuid.UUID, skip: int = 0, limit: int = 100) -> List[models.Inventory]:
    """Get all inventory items for an organization across all its warehouses."""
    return db.query(models.Inventory).join(
        models.Warehouse, models.Inventory.warehouse_id == models.Warehouse.id
    ).filter(
        models.Warehouse.organization_id == organization_id
    ).offset(skip).limit(limit).all()


def get_inventory_aggregation_by_organization(db: Session, organization_id: uuid.UUID) -> List[dict]:
    """Get inventory aggregated by part across all warehouses for an organization."""
    from sqlalchemy import func
    
    results = db.query(
        models.Part.id.label('part_id'),
        models.Part.part_number,
        models.Part.name.label('part_name'),
        models.Part.unit_of_measure,
        func.sum(models.Inventory.current_stock).label('total_stock'),
        func.count(models.Inventory.id).label('warehouse_count'),
        func.sum(models.Inventory.minimum_stock_recommendation).label('total_min_stock')
    ).join(
        models.Inventory, models.Part.id == models.Inventory.part_id
    ).join(
        models.Warehouse, models.Inventory.warehouse_id == models.Warehouse.id
    ).filter(
        models.Warehouse.organization_id == organization_id
    ).group_by(
        models.Part.id, models.Part.part_number, models.Part.name, models.Part.unit_of_measure
    ).order_by(models.Part.part_number).all()
    
    return [
        {
            'part_id': str(row.part_id),
            'part_number': row.part_number,
            'part_name': row.part_name,
            'unit_of_measure': row.unit_of_measure,
            'total_stock': float(row.total_stock),
            'warehouse_count': row.warehouse_count,
            'total_minimum_stock': float(row.total_min_stock),
            'is_low_stock': float(row.total_stock) <= float(row.total_min_stock)
        }
        for row in results
    ]


def transfer_inventory_between_warehouses(db: Session, from_warehouse_id: uuid.UUID, 
                                        to_warehouse_id: uuid.UUID, part_id: uuid.UUID, 
                                        quantity: float, performed_by_user_id: uuid.UUID) -> bool:
    """Transfer inventory between warehouses."""
    try:
        # Validate warehouses exist
        from_warehouse = db.query(models.Warehouse).filter(models.Warehouse.id == from_warehouse_id).first()
        to_warehouse = db.query(models.Warehouse).filter(models.Warehouse.id == to_warehouse_id).first()
        
        if not from_warehouse or not to_warehouse:
            raise HTTPException(status_code=400, detail="One or both warehouses not found")
        
        # Get or create inventory items
        from_inventory = db.query(models.Inventory).filter(
            models.Inventory.warehouse_id == from_warehouse_id,
            models.Inventory.part_id == part_id
        ).first()
        
        if not from_inventory or from_inventory.current_stock < quantity:
            raise HTTPException(status_code=400, detail="Insufficient stock in source warehouse")
        
        to_inventory = db.query(models.Inventory).filter(
            models.Inventory.warehouse_id == to_warehouse_id,
            models.Inventory.part_id == part_id
        ).first()
        
        # Get part for unit of measure
        part = db.query(models.Part).filter(models.Part.id == part_id).first()
        if not part:
            raise HTTPException(status_code=400, detail="Part not found")
        
        # Update source inventory
        from_inventory.current_stock -= quantity
        
        # Create or update destination inventory
        if not to_inventory:
            to_inventory = models.Inventory(
                warehouse_id=to_warehouse_id,
                part_id=part_id,
                current_stock=quantity,
                unit_of_measure=part.unit_of_measure,
                minimum_stock_recommendation=0
            )
            db.add(to_inventory)
        else:
            to_inventory.current_stock += quantity
        
        # Create transaction record
        transaction = models.Transaction(
            transaction_type=models.TransactionType.TRANSFER,
            part_id=part_id,
            from_warehouse_id=from_warehouse_id,
            to_warehouse_id=to_warehouse_id,
            quantity=quantity,
            unit_of_measure=part.unit_of_measure,
            performed_by_user_id=performed_by_user_id,
            transaction_date=db.query(func.now()).scalar(),
            notes=f"Transfer from {from_warehouse.name} to {to_warehouse.name}"
        )
        db.add(transaction)
        
        db.commit()
        return True
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error transferring inventory: {e}")
        raise HTTPException(status_code=400, detail=f"Error transferring inventory: {str(e)}")


def get_inventory_balance_calculations(db: Session, warehouse_id: uuid.UUID) -> List[dict]:
    """Calculate inventory balances based on transactions for a warehouse."""
    from sqlalchemy import func, case
    
    # Get all transactions affecting this warehouse
    results = db.query(
        models.Transaction.part_id,
        models.Part.part_number,
        models.Part.name.label('part_name'),
        models.Part.unit_of_measure,
        func.sum(
            case(
                (models.Transaction.to_warehouse_id == warehouse_id, models.Transaction.quantity),
                else_=0
            )
        ).label('total_in'),
        func.sum(
            case(
                (models.Transaction.from_warehouse_id == warehouse_id, models.Transaction.quantity),
                else_=0
            )
        ).label('total_out')
    ).join(
        models.Part, models.Transaction.part_id == models.Part.id
    ).filter(
        or_(
            models.Transaction.from_warehouse_id == warehouse_id,
            models.Transaction.to_warehouse_id == warehouse_id
        )
    ).group_by(
        models.Transaction.part_id, models.Part.part_number, 
        models.Part.name, models.Part.unit_of_measure
    ).all()
    
    return [
        {
            'part_id': str(row.part_id),
            'part_number': row.part_number,
            'part_name': row.part_name,
            'unit_of_measure': row.unit_of_measure,
            'total_in': float(row.total_in or 0),
            'total_out': float(row.total_out or 0),
            'calculated_balance': float((row.total_in or 0) - (row.total_out or 0))
        }
        for row in results
    ]
