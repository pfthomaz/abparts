# backend/app/schemas/warehouse_location.py

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from decimal import Decimal
from uuid import UUID


# --- Warehouse Location Schemas ---

class WarehouseLocationCreate(BaseModel):
    """Schema for creating a new warehouse location."""
    location_code: str = Field(..., max_length=50, description="Location code (e.g., 'A1', 'B3-top')")
    description: Optional[str] = Field(None, description="Optional description of the location")


class WarehouseLocationUpdate(BaseModel):
    """Schema for updating an existing warehouse location."""
    location_code: Optional[str] = Field(None, max_length=50, description="Location code (e.g., 'A1', 'B3-top')")
    description: Optional[str] = None


class WarehouseLocationResponse(BaseModel):
    """Response schema for a warehouse location."""
    id: UUID
    warehouse_id: UUID
    location_code: str
    description: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    parts_count: Optional[int] = Field(None, description="Number of parts assigned to this location")

    class Config:
        from_attributes = True


# --- Inventory Location Assignment Schemas ---

class InventoryLocationAssign(BaseModel):
    """Schema for bulk assigning inventory items (parts) to a location."""
    inventory_ids: List[UUID] = Field(..., description="List of inventory IDs to assign to this location")


# --- Part Location Info (for LocationWithParts) ---

class PartLocationInfo(BaseModel):
    """Schema for part information within a location context."""
    inventory_id: UUID = Field(..., description="Inventory record ID")
    part_id: UUID = Field(..., description="Part ID")
    part_name: str = Field(..., description="Part name")
    sku: Optional[str] = Field(None, description="Part number / SKU")
    quantity: Decimal = Field(..., description="Current stock quantity at this warehouse")
    photo_url: Optional[str] = Field(None, description="First image URL of the part")

    class Config:
        from_attributes = True


# --- Location With Parts (extended response) ---

class LocationWithParts(WarehouseLocationResponse):
    """Extended location response including the list of parts at this location."""
    parts: List[PartLocationInfo] = Field(default_factory=list, description="Parts stored at this location")

    class Config:
        from_attributes = True


# --- Label Generation Request ---

class LabelGenerateRequest(BaseModel):
    """Schema for requesting label PDF generation for selected locations."""
    location_ids: Optional[List[UUID]] = Field(
        None,
        description="List of location IDs to generate labels for. If empty/null, generates for all locations in the warehouse."
    )
