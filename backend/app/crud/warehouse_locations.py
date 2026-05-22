"""CRUD operations for warehouse locations and inventory-location assignments."""

from typing import List, Optional
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, func
import uuid

from .. import models
from ..schemas.warehouse_location import WarehouseLocationCreate, WarehouseLocationUpdate


# --- Location CRUD ---

def create_location(
    db: Session,
    warehouse_id: uuid.UUID,
    location_data: WarehouseLocationCreate
) -> models.WarehouseLocation:
    """Create a new warehouse location."""
    db_location = models.WarehouseLocation(
        warehouse_id=warehouse_id,
        location_code=location_data.location_code,
        description=location_data.description
    )
    db.add(db_location)
    db.commit()
    db.refresh(db_location)
    return db_location


def get_location(db: Session, location_id: uuid.UUID) -> Optional[models.WarehouseLocation]:
    """Get a single location by ID."""
    return db.query(models.WarehouseLocation).filter(
        models.WarehouseLocation.id == location_id
    ).first()


def get_locations_by_warehouse(db: Session, warehouse_id: uuid.UUID) -> List[dict]:
    """
    List all locations for a warehouse with parts_count.
    Returns a list of dicts with location data + parts_count.
    """
    locations = db.query(models.WarehouseLocation).filter(
        models.WarehouseLocation.warehouse_id == warehouse_id
    ).order_by(models.WarehouseLocation.location_code).all()

    result = []
    for loc in locations:
        parts_count = db.query(func.count(models.InventoryLocation.id)).filter(
            models.InventoryLocation.location_id == loc.id
        ).scalar()

        result.append({
            "id": loc.id,
            "warehouse_id": loc.warehouse_id,
            "location_code": loc.location_code,
            "description": loc.description,
            "created_at": loc.created_at,
            "updated_at": loc.updated_at,
            "parts_count": parts_count
        })

    return result


def update_location(
    db: Session,
    location_id: uuid.UUID,
    location_data: WarehouseLocationUpdate
) -> Optional[models.WarehouseLocation]:
    """Update a location's code and/or description."""
    db_location = get_location(db, location_id)
    if not db_location:
        return None

    update_data = location_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_location, field, value)

    db.commit()
    db.refresh(db_location)
    return db_location


def delete_location(db: Session, location_id: uuid.UUID) -> bool:
    """
    Delete a location and cascade-delete its inventory_locations.
    The cascade is handled by the SQLAlchemy relationship (cascade='all, delete-orphan').
    """
    db_location = get_location(db, location_id)
    if not db_location:
        return False

    db.delete(db_location)
    db.commit()
    return True


# --- Part-Location Assignment ---

def assign_parts_to_location(
    db: Session,
    location_id: uuid.UUID,
    inventory_ids: List[uuid.UUID]
) -> List[models.InventoryLocation]:
    """
    Bulk assign inventory items to a location.
    Skips duplicates (if an inventory item is already at this location).
    """
    created = []
    for inv_id in inventory_ids:
        # Check if assignment already exists
        existing = db.query(models.InventoryLocation).filter(
            and_(
                models.InventoryLocation.inventory_id == inv_id,
                models.InventoryLocation.location_id == location_id
            )
        ).first()

        if not existing:
            assignment = models.InventoryLocation(
                inventory_id=inv_id,
                location_id=location_id
            )
            db.add(assignment)
            created.append(assignment)

    if created:
        db.commit()
        for item in created:
            db.refresh(item)

    return created


def unassign_part_from_location(
    db: Session,
    location_id: uuid.UUID,
    inventory_id: uuid.UUID
) -> bool:
    """Remove a specific inventory item from a location."""
    assignment = db.query(models.InventoryLocation).filter(
        and_(
            models.InventoryLocation.inventory_id == inventory_id,
            models.InventoryLocation.location_id == location_id
        )
    ).first()

    if not assignment:
        return False

    db.delete(assignment)
    db.commit()
    return True


# --- Query helpers ---

def get_parts_at_location(db: Session, location_id: uuid.UUID) -> List[dict]:
    """
    Get all parts stored at a location.
    Returns PartLocationInfo-compatible dicts with calculated current stock from warehouse inventory.
    Uses the same calculation logic as the inventory modal (adjustments + transactions).
    """
    from .inventory_calculator import calculate_current_stock

    # Get the location to know which warehouse it belongs to
    location = db.query(models.WarehouseLocation).filter(
        models.WarehouseLocation.id == location_id
    ).first()
    if not location:
        return []

    warehouse_id = location.warehouse_id

    assignments = db.query(models.InventoryLocation).filter(
        models.InventoryLocation.location_id == location_id
    ).options(
        joinedload(models.InventoryLocation.inventory).joinedload(models.Inventory.part)
    ).all()

    parts = []
    for assignment in assignments:
        inventory = assignment.inventory
        part = inventory.part

        # Calculate current stock using the same logic as the inventory modal
        # (based on stock adjustments + transactions, not the cached current_stock field)
        calculated_stock = calculate_current_stock(db, warehouse_id, part.id)

        # Get first image URL if available
        photo_url = None
        if part.image_urls and len(part.image_urls) > 0:
            photo_url = part.image_urls[0]

        parts.append({
            "inventory_id": inventory.id,
            "part_id": part.id,
            "part_name": part.name,
            "sku": part.part_number,
            "quantity": float(calculated_stock),
            "photo_url": photo_url
        })

    return parts


def get_locations_for_inventory(db: Session, inventory_id: uuid.UUID) -> List[models.WarehouseLocation]:
    """Get all locations where a specific inventory item is stored."""
    assignments = db.query(models.InventoryLocation).filter(
        models.InventoryLocation.inventory_id == inventory_id
    ).options(
        joinedload(models.InventoryLocation.location)
    ).all()

    return [assignment.location for assignment in assignments]


def get_location_by_code(
    db: Session,
    warehouse_id: uuid.UUID,
    location_code: str
) -> Optional[models.WarehouseLocation]:
    """Lookup a location by warehouse + code (used for QR scanning)."""
    return db.query(models.WarehouseLocation).filter(
        and_(
            models.WarehouseLocation.warehouse_id == warehouse_id,
            models.WarehouseLocation.location_code == location_code
        )
    ).first()
