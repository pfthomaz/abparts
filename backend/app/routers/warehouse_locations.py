# backend/app/routers/warehouse_locations.py

"""API router for warehouse locations and inventory-location assignments."""

import io
import uuid
import logging
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from .. import models
from ..crud import warehouse_locations as crud_locations
from ..schemas.warehouse_location import (
    WarehouseLocationCreate,
    WarehouseLocationUpdate,
    WarehouseLocationResponse,
    InventoryLocationAssign,
    LocationWithParts,
    LabelGenerateRequest,
    PartLocationInfo,
)
from ..services.qr_label_service import generate_label_pdf
from ..database import get_db
from ..auth import get_current_user, TokenData

logger = logging.getLogger(__name__)
router = APIRouter()


# --- Helper ---

def _get_warehouse_or_404(db: Session, warehouse_id: uuid.UUID) -> models.Warehouse:
    """Fetch a warehouse by ID or raise 404."""
    warehouse = db.query(models.Warehouse).filter(
        models.Warehouse.id == warehouse_id
    ).first()
    if not warehouse:
        raise HTTPException(status_code=404, detail="Warehouse not found")
    return warehouse


def _get_location_or_404(db: Session, location_id: uuid.UUID) -> models.WarehouseLocation:
    """Fetch a location by ID or raise 404."""
    location = crud_locations.get_location(db, location_id)
    if not location:
        raise HTTPException(status_code=404, detail="Location not found")
    return location


# --- Warehouse-scoped location endpoints ---

@router.get(
    "/warehouses/{warehouse_id}/locations",
    response_model=List[WarehouseLocationResponse],
    tags=["Warehouse Locations"],
)
async def list_locations(
    warehouse_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user),
):
    """List all locations for a warehouse."""
    _get_warehouse_or_404(db, warehouse_id)
    locations = crud_locations.get_locations_by_warehouse(db, warehouse_id)
    return locations


@router.post(
    "/warehouses/{warehouse_id}/locations",
    response_model=WarehouseLocationResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Warehouse Locations"],
)
async def create_location(
    warehouse_id: uuid.UUID,
    location_data: WarehouseLocationCreate,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user),
):
    """Create a new location in a warehouse."""
    _get_warehouse_or_404(db, warehouse_id)

    # Check for duplicate location_code within this warehouse
    existing = crud_locations.get_location_by_code(db, warehouse_id, location_data.location_code)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Location code '{location_data.location_code}' already exists in this warehouse",
        )

    db_location = crud_locations.create_location(db, warehouse_id, location_data)
    # Return with parts_count = 0 for newly created location
    return WarehouseLocationResponse(
        id=db_location.id,
        warehouse_id=db_location.warehouse_id,
        location_code=db_location.location_code,
        description=db_location.description,
        created_at=db_location.created_at,
        updated_at=db_location.updated_at,
        parts_count=0,
    )


# --- Label generation endpoints ---

BASE_QR_URL = "https://abparts.oraseas.com/locate"


def _build_label_data(db: Session, warehouse_id: uuid.UUID, location_ids: List[uuid.UUID] = None) -> List[dict]:
    """
    Build label data for the given locations (or all locations in the warehouse).
    Returns a list of dicts suitable for generate_label_pdf.
    """
    if location_ids:
        # Fetch specific locations
        locations = []
        for loc_id in location_ids:
            loc = crud_locations.get_location(db, loc_id)
            if loc and loc.warehouse_id == warehouse_id:
                locations.append(loc)
    else:
        # Fetch all locations for the warehouse (raw model objects)
        locations = db.query(models.WarehouseLocation).filter(
            models.WarehouseLocation.warehouse_id == warehouse_id
        ).order_by(models.WarehouseLocation.location_code).all()

    if not locations:
        raise HTTPException(
            status_code=404,
            detail="No locations found to generate labels for",
        )

    label_data = []
    for loc in locations:
        parts = crud_locations.get_parts_at_location(db, loc.id)
        part_names = [p["part_name"] for p in parts]
        label_data.append({
            "location_code": loc.location_code,
            "description": loc.description,
            "parts": part_names,
        })

    return label_data


@router.post(
    "/warehouses/{warehouse_id}/locations/labels",
    tags=["Warehouse Locations"],
    responses={200: {"content": {"application/pdf": {}}}},
)
async def generate_labels(
    warehouse_id: uuid.UUID,
    body: LabelGenerateRequest,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user),
):
    """
    Generate a PDF with QR code labels for selected locations.
    If location_ids is empty or null, generates labels for all locations in the warehouse.
    """
    _get_warehouse_or_404(db, warehouse_id)

    location_ids = body.location_ids if body.location_ids else None
    label_data = _build_label_data(db, warehouse_id, location_ids)

    base_url = f"{BASE_QR_URL}/{warehouse_id}"
    pdf_bytes = generate_label_pdf(locations=label_data, base_url=base_url)

    return StreamingResponse(
        io.BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="warehouse_labels_{warehouse_id}.pdf"'
        },
    )


@router.get(
    "/warehouses/{warehouse_id}/locations/labels/all",
    tags=["Warehouse Locations"],
    responses={200: {"content": {"application/pdf": {}}}},
)
async def generate_all_labels(
    warehouse_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user),
):
    """
    Generate a PDF with QR code labels for ALL locations in the warehouse.
    """
    _get_warehouse_or_404(db, warehouse_id)

    label_data = _build_label_data(db, warehouse_id)

    base_url = f"{BASE_QR_URL}/{warehouse_id}"
    pdf_bytes = generate_label_pdf(locations=label_data, base_url=base_url)

    return StreamingResponse(
        io.BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="warehouse_labels_{warehouse_id}.pdf"'
        },
    )


# --- Find Part (reverse lookup) ---

@router.get(
    "/warehouse-locations/find-part/{inventory_id}",
    response_model=List[WarehouseLocationResponse],
    tags=["Warehouse Locations"],
)
async def find_part_locations(
    inventory_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user),
):
    """
    Find all locations where a specific inventory item (part) is stored.
    Used by the "Where is this?" feature for reverse lookup.
    """
    locations = crud_locations.get_locations_for_inventory(db, inventory_id)
    if not locations:
        return []

    # Build response with parts_count for each location
    result = []
    for loc in locations:
        parts = crud_locations.get_parts_at_location(db, loc.id)
        result.append(WarehouseLocationResponse(
            id=loc.id,
            warehouse_id=loc.warehouse_id,
            location_code=loc.location_code,
            description=loc.description,
            created_at=loc.created_at,
            updated_at=loc.updated_at,
            parts_count=len(parts),
        ))
    return result


# --- Location-level endpoints (by location ID) ---

@router.put(
    "/warehouse-locations/{location_id}",
    response_model=WarehouseLocationResponse,
    tags=["Warehouse Locations"],
)
async def update_location(
    location_id: uuid.UUID,
    location_data: WarehouseLocationUpdate,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user),
):
    """Update a warehouse location."""
    existing = _get_location_or_404(db, location_id)

    # If location_code is being changed, check for duplicates
    if location_data.location_code and location_data.location_code != existing.location_code:
        duplicate = crud_locations.get_location_by_code(
            db, existing.warehouse_id, location_data.location_code
        )
        if duplicate:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Location code '{location_data.location_code}' already exists in this warehouse",
            )

    updated = crud_locations.update_location(db, location_id, location_data)
    if not updated:
        raise HTTPException(status_code=404, detail="Location not found")

    # Get parts_count for response
    parts = crud_locations.get_parts_at_location(db, location_id)
    return WarehouseLocationResponse(
        id=updated.id,
        warehouse_id=updated.warehouse_id,
        location_code=updated.location_code,
        description=updated.description,
        created_at=updated.created_at,
        updated_at=updated.updated_at,
        parts_count=len(parts),
    )


@router.delete(
    "/warehouse-locations/{location_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["Warehouse Locations"],
)
async def delete_location(
    location_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user),
):
    """Delete a warehouse location (cascades to inventory_locations)."""
    _get_location_or_404(db, location_id)
    crud_locations.delete_location(db, location_id)
    return None


# --- Part assignment endpoints ---

@router.post(
    "/warehouse-locations/{location_id}/assign",
    response_model=List[PartLocationInfo],
    status_code=status.HTTP_201_CREATED,
    tags=["Warehouse Locations"],
)
async def assign_parts(
    location_id: uuid.UUID,
    assign_data: InventoryLocationAssign,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user),
):
    """Assign one or more inventory items (parts) to a location."""
    _get_location_or_404(db, location_id)
    crud_locations.assign_parts_to_location(db, location_id, assign_data.inventory_ids)
    # Return the full list of parts now at this location
    parts = crud_locations.get_parts_at_location(db, location_id)
    return parts


@router.delete(
    "/warehouse-locations/{location_id}/unassign/{inventory_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["Warehouse Locations"],
)
async def unassign_part(
    location_id: uuid.UUID,
    inventory_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user),
):
    """Remove a specific inventory item from a location."""
    _get_location_or_404(db, location_id)
    removed = crud_locations.unassign_part_from_location(db, location_id, inventory_id)
    if not removed:
        raise HTTPException(
            status_code=404,
            detail="Assignment not found - this part is not at this location",
        )
    return None


@router.get(
    "/warehouse-locations/{location_id}/parts",
    response_model=List[PartLocationInfo],
    tags=["Warehouse Locations"],
)
async def get_parts_at_location(
    location_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user),
):
    """Get all parts stored at a specific location."""
    _get_location_or_404(db, location_id)
    parts = crud_locations.get_parts_at_location(db, location_id)
    return parts


# --- Public QR lookup endpoint (no auth required) ---

@router.get(
    "/locate/{warehouse_id}/{location_code}",
    response_model=LocationWithParts,
    tags=["Warehouse Locations"],
)
async def locate_by_qr(
    warehouse_id: uuid.UUID,
    location_code: str,
    db: Session = Depends(get_db),
):
    """
    Public endpoint for QR code scanning.
    Returns location details with all parts stored there.
    No authentication required - this is what QR codes link to.
    """
    # Verify warehouse exists
    _get_warehouse_or_404(db, warehouse_id)

    # Look up location by warehouse + code
    location = crud_locations.get_location_by_code(db, warehouse_id, location_code)
    if not location:
        raise HTTPException(
            status_code=404,
            detail=f"Location '{location_code}' not found in this warehouse",
        )

    # Get parts at this location
    parts = crud_locations.get_parts_at_location(db, location.id)

    return LocationWithParts(
        id=location.id,
        warehouse_id=location.warehouse_id,
        location_code=location.location_code,
        description=location.description,
        created_at=location.created_at,
        updated_at=location.updated_at,
        parts_count=len(parts),
        parts=parts,
    )
