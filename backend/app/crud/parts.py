# backend/app/crud/parts.py

import uuid
import logging
import time
from typing import List, Optional, Dict, Any, Tuple
from decimal import Decimal
from datetime import datetime, timedelta

from sqlalchemy.orm import Session
from sqlalchemy import and_, func, desc, text
from fastapi import HTTPException, status

from .. import models, schemas # Import models and schemas
from ..performance_monitoring import monitor_performance

logger = logging.getLogger(__name__)

@monitor_performance("parts_crud.get_part")
def get_part(db: Session, part_id: uuid.UUID):
    """Retrieve a single part by ID."""
    return db.query(models.Part).filter(models.Part.id == part_id).first()

@monitor_performance("parts_crud.get_part_with_monitoring")
def get_part_with_monitoring(db: Session, part_id: uuid.UUID):
    """Retrieve a single part by ID with performance monitoring."""
    return db.query(models.Part).filter(models.Part.id == part_id).first()

@monitor_performance("parts_crud.get_parts", param_keys=["skip", "limit"])
def get_parts(db: Session, skip: int = 0, limit: int = 100):
    """Retrieve a list of parts."""
    return db.query(models.Part).offset(skip).limit(limit).all()

@monitor_performance("parts_crud.create_part")
def create_part(db: Session, part: schemas.PartCreate):
    """Create a new part."""
    # The image_urls field is already a list from the schema, pass it directly
    db_part = models.Part(**part.dict())
    try:
        db.add(db_part)
        db.flush()  # Flush to get the ID without committing
        db.commit()
        db.refresh(db_part)
        return db_part
    except Exception as e:
        db.rollback()
        if "duplicate key value violates unique constraint" in str(e):
            raise HTTPException(status_code=409, detail="Part with this part number already exists")
        logger.error(f"Error creating part: {e}")
        raise HTTPException(status_code=400, detail="Error creating part")

@monitor_performance("parts_crud.update_part")
def update_part(db: Session, part_id: uuid.UUID, part_update: schemas.PartUpdate):
    """Update an existing part."""
    db_part = db.query(models.Part).filter(models.Part.id == part_id).first()
    if not db_part:
        return None # Indicate not found

    update_data = part_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_part, key, value)
    try:
        db.add(db_part)
        db.commit()
        db.refresh(db_part)
        return db_part
    except Exception as e:
        db.rollback()
        if "duplicate key value violates unique constraint" in str(e):
            raise HTTPException(status_code=409, detail="Part with this part number already exists")
        logger.error(f"Error updating part: {e}")
        raise HTTPException(status_code=400, detail="Error updating part")

@monitor_performance("parts_crud.delete_part")
def delete_part(db: Session, part_id: uuid.UUID):
    """Delete a part by ID."""
    db_part = db.query(models.Part).filter(models.Part.id == part_id).first()
    if not db_part:
        return None # Indicate not found
    try:
        db.delete(db_part)
        db.commit()
        return {"message": "Part deleted successfully"}
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting part: {e}")
        raise HTTPException(status_code=400, detail="Error deleting part. Check for dependent records.")

@monitor_performance("parts_crud.get_filtered_parts", param_keys=["part_type", "is_proprietary", "skip", "limit"])
def get_filtered_parts(db: Session, part_type: Optional[str] = None, is_proprietary: Optional[bool] = None, skip: int = 0, limit: int = 100):
    """
    Retrieve a filtered list of parts based on type and origin.
    
    Args:
        db: Database session
        part_type: Filter by part type (consumable or bulk_material)
        is_proprietary: Filter by proprietary status
        skip: Number of records to skip
        limit: Maximum number of records to return
        
    Returns:
        List of parts matching the filter criteria
    """
    query = db.query(models.Part)
    
    # Apply filters if provided
    if part_type:
        try:
            # Convert string to enum value
            enum_part_type = models.PartType(part_type)
            query = query.filter(models.Part.part_type == enum_part_type)
        except ValueError:
            # If invalid part_type is provided, log warning but don't fail
            logger.warning(f"Invalid part_type filter: {part_type}")
    
    if is_proprietary is not None:  # Check for None specifically since False is valid
        query = query.filter(models.Part.is_proprietary == is_proprietary)
    
    # Apply pagination
    return query.offset(skip).limit(limit).all()

@monitor_performance("parts_crud.get_filtered_parts_with_count", param_keys=["part_type", "is_proprietary", "skip", "limit", "include_count"])
def get_filtered_parts_with_count(db: Session, part_type: Optional[str] = None, is_proprietary: Optional[bool] = None, 
                                 skip: int = 0, limit: int = 100, include_count: bool = False) -> Dict[str, Any]:
    """
    Retrieve a filtered list of parts with optional total count.
    
    Args:
        db: Database session
        part_type: Filter by part type (consumable or bulk_material)
        is_proprietary: Filter by proprietary status
        skip: Number of records to skip
        limit: Maximum number of records to return
        include_count: Whether to include total count (impacts performance)
        
    Returns:
        Dictionary with items, total_count (if requested), and has_more flag
    """
    query = db.query(models.Part)
    
    # Apply filters if provided
    if part_type:
        try:
            enum_part_type = models.PartType(part_type)
            query = query.filter(models.Part.part_type == enum_part_type)
        except ValueError:
            logger.warning(f"Invalid part_type filter: {part_type}")
    
    if is_proprietary is not None:
        query = query.filter(models.Part.is_proprietary == is_proprietary)
    
    # Get total count if requested (expensive operation)
    total_count = None
    if include_count:
        total_count = query.count()
    
    # Get paginated results
    items = query.offset(skip).limit(limit + 1).all()  # Get one extra to check if there are more
    
    # Check if there are more items
    has_more = len(items) > limit
    if has_more:
        items = items[:limit]  # Remove the extra item
    
    return {
        "items": items,
        "total_count": total_count,
        "has_more": has_more
    }

@monitor_performance("parts_crud.search_parts", param_keys=["part_type", "is_proprietary", "skip", "limit"])
def search_parts(db: Session, search_term: str, part_type: Optional[str] = None, is_proprietary: Optional[bool] = None, skip: int = 0, limit: int = 100):
    """
    Search parts by name or part number with optional filtering by type and origin.
    
    Args:
        db: Database session
        search_term: Search term for part name or part number
        part_type: Filter by part type (consumable or bulk_material)
        is_proprietary: Filter by proprietary status
        skip: Number of records to skip
        limit: Maximum number of records to return
        
    Returns:
        List of parts matching the search criteria
    """
    from sqlalchemy import or_
    
    # Start with base query
    query = db.query(models.Part).filter(
        or_(
            models.Part.name.ilike(f"%{search_term}%"),
            models.Part.part_number.ilike(f"%{search_term}%"),
            models.Part.description.ilike(f"%{search_term}%")
        )
    )
    
    # Apply additional filters if provided
    if part_type:
        try:
            # Convert string to enum value
            enum_part_type = models.PartType(part_type)
            query = query.filter(models.Part.part_type == enum_part_type)
        except ValueError:
            # If invalid part_type is provided, log warning but don't fail
            logger.warning(f"Invalid part_type filter: {part_type}")
    
    if is_proprietary is not None:  # Check for None specifically since False is valid
        query = query.filter(models.Part.is_proprietary == is_proprietary)
    
    # Apply pagination
    return query.offset(skip).limit(limit).all()

def validate_multilingual_name(name: str) -> bool:
    """
    Validate multilingual name format.
    
    Supports formats like:
    - "English Name" (single language)
    - "English Name|Greek Name GR" (two languages)
    - "English Name|Greek Name GR|Spanish Name ES" (multiple languages)
    
    Args:
        name: The multilingual name string to validate
        
    Returns:
        bool: True if format is valid, False otherwise
    """
    if not name or not name.strip():
        return False
    
    # Single language names are always valid
    if '|' not in name:
        return len(name.strip()) > 0
    
    # Split by pipe and validate each part
    parts = name.split('|')
    for part in parts:
        part = part.strip()
        if not part:
            return False
        # Each part should have at least some text
        if len(part) < 1:
            return False
    
    return True

@monitor_performance("parts_crud.search_parts_multilingual", param_keys=["part_type", "is_proprietary", "skip", "limit"])
def search_parts_multilingual(db: Session, search_term: str, part_type: Optional[str] = None, 
                             is_proprietary: Optional[bool] = None, skip: int = 0, limit: int = 100):
    """
    Enhanced search for parts with multilingual name support.
    
    Searches across:
    - All parts of multilingual names (split by |)
    - Part numbers
    - Descriptions
    - Manufacturer names
    - Part codes
    
    Args:
        db: Database session
        search_term: Search term for multilingual names, part numbers, etc.
        part_type: Filter by part type (consumable or bulk_material)
        is_proprietary: Filter by proprietary status
        skip: Number of records to skip
        limit: Maximum number of records to return
        
    Returns:
        List of parts matching the search criteria
    """
    from sqlalchemy import or_, func
    
    # Create search conditions for multilingual names
    # This will search in the full name field which may contain pipe-separated values
    search_conditions = [
        models.Part.name.ilike(f"%{search_term}%"),
        models.Part.part_number.ilike(f"%{search_term}%"),
        models.Part.description.ilike(f"%{search_term}%")
    ]
    
    # Add search in new fields
    if hasattr(models.Part, 'manufacturer') and models.Part.manufacturer is not None:
        search_conditions.append(models.Part.manufacturer.ilike(f"%{search_term}%"))
    
    if hasattr(models.Part, 'part_code') and models.Part.part_code is not None:
        search_conditions.append(models.Part.part_code.ilike(f"%{search_term}%"))
    
    if hasattr(models.Part, 'serial_number') and models.Part.serial_number is not None:
        search_conditions.append(models.Part.serial_number.ilike(f"%{search_term}%"))
    
    # Start with base query
    query = db.query(models.Part).filter(or_(*search_conditions))
    
    # Apply additional filters if provided
    if part_type:
        try:
            enum_part_type = models.PartType(part_type)
            query = query.filter(models.Part.part_type == enum_part_type)
        except ValueError:
            logger.warning(f"Invalid part_type filter: {part_type}")
    
    if is_proprietary is not None:
        query = query.filter(models.Part.is_proprietary == is_proprietary)
    
    # Apply pagination and return results
    return query.offset(skip).limit(limit).all()

@monitor_performance("parts_crud.search_parts_multilingual_with_count", param_keys=["part_type", "is_proprietary", "skip", "limit", "include_count"])
def search_parts_multilingual_with_count(db: Session, search_term: str, part_type: Optional[str] = None, 
                                        is_proprietary: Optional[bool] = None, skip: int = 0, limit: int = 100,
                                        include_count: bool = False) -> Dict[str, Any]:
    """
    Enhanced search for parts with multilingual name support and optional count.
    
    Args:
        db: Database session
        search_term: Search term for multilingual names, part numbers, etc.
        part_type: Filter by part type (consumable or bulk_material)
        is_proprietary: Filter by proprietary status
        skip: Number of records to skip
        limit: Maximum number of records to return
        include_count: Whether to include total count (impacts performance)
        
    Returns:
        Dictionary with items, total_count (if requested), and has_more flag
    """
    from sqlalchemy import or_, func
    
    # Create search conditions for multilingual names
    search_conditions = [
        models.Part.name.ilike(f"%{search_term}%"),
        models.Part.part_number.ilike(f"%{search_term}%"),
        models.Part.description.ilike(f"%{search_term}%")
    ]
    
    # Add search in new fields
    if hasattr(models.Part, 'manufacturer') and models.Part.manufacturer is not None:
        search_conditions.append(models.Part.manufacturer.ilike(f"%{search_term}%"))
    
    if hasattr(models.Part, 'part_code') and models.Part.part_code is not None:
        search_conditions.append(models.Part.part_code.ilike(f"%{search_term}%"))
    
    if hasattr(models.Part, 'serial_number') and models.Part.serial_number is not None:
        search_conditions.append(models.Part.serial_number.ilike(f"%{search_term}%"))
    
    # Start with base query
    query = db.query(models.Part).filter(or_(*search_conditions))
    
    # Apply additional filters if provided
    if part_type:
        try:
            enum_part_type = models.PartType(part_type)
            query = query.filter(models.Part.part_type == enum_part_type)
        except ValueError:
            logger.warning(f"Invalid part_type filter: {part_type}")
    
    if is_proprietary is not None:
        query = query.filter(models.Part.is_proprietary == is_proprietary)
    
    # Get total count if requested (expensive operation)
    total_count = None
    if include_count:
        total_count = query.count()
    
    # Get paginated results
    items = query.offset(skip).limit(limit + 1).all()  # Get one extra to check if there are more
    
    # Check if there are more items
    has_more = len(items) > limit
    if has_more:
        items = items[:limit]  # Remove the extra item
    
    return {
        "items": items,
        "total_count": total_count,
        "has_more": has_more
    }

@monitor_performance("parts_crud.create_part_enhanced")
def create_part_enhanced(db: Session, part: schemas.PartCreate):
    """
    Enhanced part creation with multilingual name support and new field validation.
    
    Args:
        db: Database session
        part: Part creation schema with enhanced fields
        
    Returns:
        Created part model or None if creation failed
    """
    try:
        # Validate multilingual name format
        if not validate_multilingual_name(part.name):
            logger.error(f"Invalid multilingual name format: {part.name}")
            raise HTTPException(status_code=400, detail="Invalid multilingual name format")
        
        # Create part with all fields
        db_part = models.Part(**part.dict())
        
        # Use a separate transaction to avoid conflicts
        db.add(db_part)
        db.flush()  # Flush to get the ID without committing
        
        # Commit the transaction
        db.commit()
        
        # Refresh to get the latest data
        db.refresh(db_part)
        
        logger.info(f"Created part with enhanced fields: {db_part.id}")
        return db_part
        
    except Exception as e:
        db.rollback()
        if "duplicate key value violates unique constraint" in str(e):
            raise HTTPException(status_code=409, detail="Part with this part number already exists")
        logger.error(f"Error creating enhanced part: {e}")
        raise HTTPException(status_code=400, detail="Error creating part")

@monitor_performance("parts_crud.update_part_enhanced")
def update_part_enhanced(db: Session, part_id: uuid.UUID, part_update: schemas.PartUpdate):
    """
    Enhanced part update with multilingual name support and new field validation.
    
    Args:
        db: Database session
        part_id: ID of part to update
        part_update: Part update schema with enhanced fields
        
    Returns:
        Updated part model or None if not found
    """
    db_part = db.query(models.Part).filter(models.Part.id == part_id).first()
    if not db_part:
        return None
    
    try:
        # Validate multilingual name format if name is being updated
        if part_update.name and not validate_multilingual_name(part_update.name):
            logger.error(f"Invalid multilingual name format: {part_update.name}")
            raise HTTPException(status_code=400, detail="Invalid multilingual name format")
        
        # Apply updates
        update_data = part_update.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_part, key, value)
        
        db.add(db_part)
        db.commit()
        db.refresh(db_part)
        
        logger.info(f"Updated part with enhanced fields: {db_part.id}")
        return db_part
        
    except Exception as e:
        db.rollback()
        if "duplicate key value violates unique constraint" in str(e):
            raise HTTPException(status_code=409, detail="Part with this part number already exists")
        logger.error(f"Error updating enhanced part: {e}")
        raise HTTPException(status_code=400, detail="Error updating part")

@monitor_performance("parts_crud.delete_part_enhanced")
def delete_part_enhanced(db: Session, part_id: uuid.UUID):
    """
    Enhanced part deletion with proper validation.
    
    Args:
        db: Database session
        part_id: ID of part to delete
        
    Returns:
        Success message or None if not found
    """
    db_part = db.query(models.Part).filter(models.Part.id == part_id).first()
    if not db_part:
        return None
    
    try:
        # Check for dependent records before deletion
        # Check inventory items
        inventory_count = db.query(models.Inventory).filter(models.Inventory.part_id == part_id).count()
        if inventory_count > 0:
            raise HTTPException(
                status_code=400, 
                detail=f"Cannot delete part: {inventory_count} inventory records exist. Remove inventory first."
            )
        
        # Check order items
        supplier_order_items = db.query(models.SupplierOrderItem).filter(models.SupplierOrderItem.part_id == part_id).count()
        customer_order_items = db.query(models.CustomerOrderItem).filter(models.CustomerOrderItem.part_id == part_id).count()
        
        if supplier_order_items > 0 or customer_order_items > 0:
            raise HTTPException(
                status_code=400,
                detail=f"Cannot delete part: {supplier_order_items + customer_order_items} order records exist."
            )
        
        # Check part usage records
        usage_count = db.query(models.PartUsage).filter(models.PartUsage.part_id == part_id).count()
        if usage_count > 0:
            raise HTTPException(
                status_code=400,
                detail=f"Cannot delete part: {usage_count} usage records exist."
            )
        
        # If no dependent records, proceed with deletion
        db.delete(db_part)
        db.commit()
        
        logger.info(f"Deleted part: {part_id}")
        return {"message": "Part deleted successfully"}
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting enhanced part: {e}")
        raise HTTPException(status_code=400, detail="Error deleting part")
@monitor_performance("parts_crud.get_part_with_inventory")
def get_part_with_inventory(db: Session, part_id: uuid.UUID, organization_id: Optional[uuid.UUID] = None):
    """
    Retrieve a single part by ID with inventory information across all warehouses.
    
    Args:
        db: Database session
        part_id: Part ID to retrieve
        organization_id: Optional organization ID to filter warehouses
        
    Returns:
        Part with inventory information
    """
    # Get the part
    part = db.query(models.Part).filter(models.Part.id == part_id).first()
    if not part:
        return None
    
    # Get inventory information for this part across all warehouses
    inventory_query = db.query(
        models.Inventory,
        models.Warehouse.name.label("warehouse_name")
    ).join(
        models.Warehouse, models.Inventory.warehouse_id == models.Warehouse.id
    ).filter(
        models.Inventory.part_id == part_id
    )
    
    # Filter by organization if provided
    if organization_id:
        inventory_query = inventory_query.filter(models.Warehouse.organization_id == organization_id)
    
    inventory_items = inventory_query.all()
    
    # Calculate total stock across all warehouses
    total_stock = Decimal('0')
    warehouse_inventory = []
    
    for inv, warehouse_name in inventory_items:
        total_stock += inv.current_stock
        
        # Check if stock is below minimum recommendation
        is_low_stock = inv.current_stock < inv.minimum_stock_recommendation if inv.minimum_stock_recommendation else False
        
        warehouse_inventory.append({
            "warehouse_id": inv.warehouse_id,
            "warehouse_name": warehouse_name,
            "current_stock": inv.current_stock,
            "minimum_stock_recommendation": inv.minimum_stock_recommendation or Decimal('0'),
            "is_low_stock": is_low_stock,
            "unit_of_measure": inv.unit_of_measure
        })
    
    # Check if overall stock is low
    is_low_stock = any(item["is_low_stock"] for item in warehouse_inventory)
    
    # Create response
    result = {
        **part.__dict__,
        "total_stock": total_stock,
        "warehouse_inventory": warehouse_inventory,
        "is_low_stock": is_low_stock
    }
    
    return result

@monitor_performance("parts_crud.get_parts_with_inventory", param_keys=["part_type", "is_proprietary", "skip", "limit"])
def get_parts_with_inventory(db: Session, organization_id: Optional[uuid.UUID] = None, 
                            part_type: Optional[str] = None, is_proprietary: Optional[bool] = None, 
                            skip: int = 0, limit: int = 100):
    """
    Retrieve a list of parts with inventory information across all warehouses.
    
    Args:
        db: Database session
        organization_id: Optional organization ID to filter warehouses
        part_type: Filter by part type (consumable or bulk_material)
        is_proprietary: Filter by proprietary status
        skip: Number of records to skip
        limit: Maximum number of records to return
        
    Returns:
        List of parts with inventory information
    """
    # Start with base query for parts
    parts_query = db.query(models.Part)
    
    # Apply filters if provided
    if part_type:
        try:
            enum_part_type = models.PartType(part_type)
            parts_query = parts_query.filter(models.Part.part_type == enum_part_type)
        except ValueError:
            logger.warning(f"Invalid part_type filter: {part_type}")
    
    if is_proprietary is not None:
        parts_query = parts_query.filter(models.Part.is_proprietary == is_proprietary)
    
    # Apply pagination
    parts = parts_query.offset(skip).limit(limit).all()
    
    # Get inventory information for these parts
    result = []
    for part in parts:
        part_with_inventory = get_part_with_inventory(db, part.id, organization_id)
        result.append(part_with_inventory)
    
    return result

@monitor_performance("parts_crud.get_parts_with_inventory_with_count", param_keys=["part_type", "is_proprietary", "skip", "limit", "include_count"])
def get_parts_with_inventory_with_count(db: Session, organization_id: Optional[uuid.UUID] = None, 
                                       part_type: Optional[str] = None, is_proprietary: Optional[bool] = None, 
                                       skip: int = 0, limit: int = 100, include_count: bool = False) -> Dict[str, Any]:
    """
    Retrieve a list of parts with inventory information and optional count.
    
    Args:
        db: Database session
        organization_id: Optional organization ID to filter warehouses
        part_type: Filter by part type (consumable or bulk_material)
        is_proprietary: Filter by proprietary status
        skip: Number of records to skip
        limit: Maximum number of records to return
        include_count: Whether to include total count (impacts performance)
        
    Returns:
        Dictionary with items, total_count (if requested), and has_more flag
    """
    # Start with base query for parts
    parts_query = db.query(models.Part)
    
    # Apply filters if provided
    if part_type:
        try:
            enum_part_type = models.PartType(part_type)
            parts_query = parts_query.filter(models.Part.part_type == enum_part_type)
        except ValueError:
            logger.warning(f"Invalid part_type filter: {part_type}")
    
    if is_proprietary is not None:
        parts_query = parts_query.filter(models.Part.is_proprietary == is_proprietary)
    
    # Get total count if requested (expensive operation)
    total_count = None
    if include_count:
        total_count = parts_query.count()
    
    # Get paginated results
    parts = parts_query.offset(skip).limit(limit + 1).all()  # Get one extra to check if there are more
    
    # Check if there are more items
    has_more = len(parts) > limit
    if has_more:
        parts = parts[:limit]  # Remove the extra item
    
    # Get inventory information for these parts
    result_items = []
    for part in parts:
        part_with_inventory = get_part_with_inventory(db, part.id, organization_id)
        result_items.append(part_with_inventory)
    
    return {
        "items": result_items,
        "total_count": total_count,
        "has_more": has_more
    }

@monitor_performance("parts_crud.get_part_usage_history", param_keys=["days"])
def get_part_usage_history(db: Session, part_id: uuid.UUID, organization_id: Optional[uuid.UUID] = None, 
                          days: int = 90):
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
        usage_query = usage_query.filter(models.Warehouse.organization_id == organization_id)
    
    # Order by usage date descending (most recent first)
    usage_records = usage_query.order_by(desc(models.PartUsage.usage_date)).all()
    
    # Format the results
    usage_history = []
    for usage, machine_serial, warehouse_name in usage_records:
        usage_history.append({
            "usage_date": usage.usage_date,
            "quantity": usage.quantity,
            "machine_id": usage.machine_id,
            "machine_serial": machine_serial,
            "warehouse_id": usage.warehouse_id,
            "warehouse_name": warehouse_name
        })
    
    return usage_history

@monitor_performance("parts_crud.get_part_with_usage_history", param_keys=["days"])
def get_part_with_usage_history(db: Session, part_id: uuid.UUID, organization_id: Optional[uuid.UUID] = None, 
                               days: int = 90):
    """
    Get a part with inventory information and usage history.
    
    Args:
        db: Database session
        part_id: Part ID to retrieve
        organization_id: Optional organization ID to filter warehouses and usage
        days: Number of days to look back for usage history
        
    Returns:
        Part with inventory information and usage history
    """
    # Get part with inventory
    part_with_inventory = get_part_with_inventory(db, part_id, organization_id)
    if not part_with_inventory:
        return None
    
    # Get usage history
    usage_history = get_part_usage_history(db, part_id, organization_id, days)
    
    # Calculate average monthly usage
    avg_monthly_usage = Decimal('0')
    if usage_history:
        # Calculate total usage in the period
        total_usage = sum(item["quantity"] for item in usage_history)
        
        # Convert days to months (approximate)
        months = days / 30.0
        
        # Calculate average monthly usage
        avg_monthly_usage = total_usage / Decimal(months) if months > 0 else Decimal('0')
    
    # Calculate estimated depletion days
    estimated_depletion_days = None
    if avg_monthly_usage > Decimal('0'):
        # Convert monthly usage to daily usage
        daily_usage = avg_monthly_usage / Decimal('30')
        
        # Calculate days until depletion
        if daily_usage > Decimal('0'):
            estimated_depletion_days = int(part_with_inventory["total_stock"] / daily_usage)
    
    # Add usage history and calculations to the result
    result = {
        **part_with_inventory,
        "usage_history": usage_history,
        "avg_monthly_usage": avg_monthly_usage,
        "estimated_depletion_days": estimated_depletion_days
    }
    
    return result

@monitor_performance("parts_crud.get_parts_reorder_suggestions", param_keys=["threshold_days", "limit"])
def get_parts_reorder_suggestions(db: Session, organization_id: Optional[uuid.UUID] = None, 
                                 threshold_days: int = 30, limit: int = 10):
    """
    Get reorder suggestions for parts based on usage patterns.
    
    Args:
        db: Database session
        organization_id: Optional organization ID to filter warehouses
        threshold_days: Threshold for days of stock remaining to trigger suggestion
        limit: Maximum number of suggestions to return
        
    Returns:
        List of part reorder suggestions
    """
    # Get all parts with inventory information
    parts_query = db.query(models.Part)
    parts = parts_query.all()
    
    # Calculate reorder suggestions
    suggestions = []
    
    for part in parts:
        # Get part with usage history
        part_with_usage = get_part_with_usage_history(db, part.id, organization_id, days=90)
        
        # Skip parts with no usage history or no inventory
        if not part_with_usage or not part_with_usage["avg_monthly_usage"] or part_with_usage["avg_monthly_usage"] <= Decimal('0'):
            continue
        
        # Check if estimated depletion days is below threshold
        if part_with_usage["estimated_depletion_days"] and part_with_usage["estimated_depletion_days"] <= threshold_days:
            # Calculate suggested reorder quantity (2 months of usage)
            suggested_reorder_quantity = part_with_usage["avg_monthly_usage"] * Decimal('2')
            
            suggestions.append({
                "part_id": part.id,
                "part_number": part.part_number,
                "part_name": part.name,
                "current_total_stock": part_with_usage["total_stock"],
                "avg_monthly_usage": part_with_usage["avg_monthly_usage"],
                "estimated_depletion_days": part_with_usage["estimated_depletion_days"],
                "suggested_reorder_quantity": suggested_reorder_quantity,
                "unit_of_measure": part.unit_of_measure,
                "is_proprietary": part.is_proprietary
            })
    
    # Sort suggestions by estimated depletion days (ascending)
    suggestions.sort(key=lambda x: x["estimated_depletion_days"])
    
    # Limit the number of suggestions
    return suggestions[:limit]

@monitor_performance("parts_crud.search_parts_with_inventory", param_keys=["part_type", "is_proprietary", "skip", "limit"])
def search_parts_with_inventory(db: Session, search_term: str, organization_id: Optional[uuid.UUID] = None,
                               part_type: Optional[str] = None, is_proprietary: Optional[bool] = None,
                               skip: int = 0, limit: int = 100):
    """
    Search parts by name or part number with inventory context.
    
    Args:
        db: Database session
        search_term: Search term for part name or part number
        organization_id: Optional organization ID to filter warehouses
        part_type: Filter by part type (consumable or bulk_material)
        is_proprietary: Filter by proprietary status
        skip: Number of records to skip
        limit: Maximum number of records to return
        
    Returns:
        List of parts matching the search criteria with inventory information
    """
    from sqlalchemy import or_
    
    # Start with base query
    query = db.query(models.Part).filter(
        or_(
            models.Part.name.ilike(f"%{search_term}%"),
            models.Part.part_number.ilike(f"%{search_term}%"),
            models.Part.description.ilike(f"%{search_term}%")
        )
    )
    
    # Apply additional filters if provided
    if part_type:
        try:
            enum_part_type = models.PartType(part_type)
            query = query.filter(models.Part.part_type == enum_part_type)
        except ValueError:
            logger.warning(f"Invalid part_type filter: {part_type}")
    
    if is_proprietary is not None:
        query = query.filter(models.Part.is_proprietary == is_proprietary)
    
    # Apply pagination
    parts = query.offset(skip).limit(limit).all()
    
    # Get inventory information for these parts
    result = []
    for part in parts:
        part_with_inventory = get_part_with_inventory(db, part.id, organization_id)
        result.append(part_with_inventory)
    
    return result

@monitor_performance("parts_crud.search_parts_with_inventory_with_count", param_keys=["part_type", "is_proprietary", "skip", "limit", "include_count"])
def search_parts_with_inventory_with_count(db: Session, search_term: str, organization_id: Optional[uuid.UUID] = None,
                                          part_type: Optional[str] = None, is_proprietary: Optional[bool] = None,
                                          skip: int = 0, limit: int = 100, include_count: bool = False) -> Dict[str, Any]:
    """
    Search parts by name or part number with inventory context and optional count.
    
    Args:
        db: Database session
        search_term: Search term for part name or part number
        organization_id: Optional organization ID to filter warehouses
        part_type: Filter by part type (consumable or bulk_material)
        is_proprietary: Filter by proprietary status
        skip: Number of records to skip
        limit: Maximum number of records to return
        include_count: Whether to include total count (impacts performance)
        
    Returns:
        Dictionary with items, total_count (if requested), and has_more flag
    """
    from sqlalchemy import or_
    
    # Start with base query
    query = db.query(models.Part).filter(
        or_(
            models.Part.name.ilike(f"%{search_term}%"),
            models.Part.part_number.ilike(f"%{search_term}%"),
            models.Part.description.ilike(f"%{search_term}%")
        )
    )
    
    # Apply additional filters if provided
    if part_type:
        try:
            enum_part_type = models.PartType(part_type)
            query = query.filter(models.Part.part_type == enum_part_type)
        except ValueError:
            logger.warning(f"Invalid part_type filter: {part_type}")
    
    if is_proprietary is not None:
        query = query.filter(models.Part.is_proprietary == is_proprietary)
    
    # Get total count if requested (expensive operation)
    total_count = None
    if include_count:
        total_count = query.count()
    
    # Get paginated results
    parts = query.offset(skip).limit(limit + 1).all()  # Get one extra to check if there are more
    
    # Check if there are more items
    has_more = len(parts) > limit
    if has_more:
        parts = parts[:limit]  # Remove the extra item
    
    # Get inventory information for these parts
    result_items = []
    for part in parts:
        part_with_inventory = get_part_with_inventory(db, part.id, organization_id)
        result_items.append(part_with_inventory)
    
    return {
        "items": result_items,
        "total_count": total_count,
        "has_more": has_more
    }