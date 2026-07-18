# backend/app/schemas/supplier_order.py

import uuid
from typing import Optional, List
from decimal import Decimal
from datetime import datetime
from pydantic import BaseModel, Field

class SupplierOrderBase(BaseModel):
    ordering_organization_id: uuid.UUID
    supplier_name: str
    order_date: datetime
    expected_delivery_date: Optional[datetime] = None
    status: str = "Pending"  # Pending, Shipped, Delivered, Cancelled
    notes: Optional[str] = None

class SupplierOrderCreate(SupplierOrderBase):
    pass

class SupplierOrderUpdate(BaseModel):
    supplier_name: Optional[str] = None
    expected_delivery_date: Optional[datetime] = None
    actual_delivery_date: Optional[datetime] = None
    status: Optional[str] = None
    notes: Optional[str] = None
    receiving_warehouse_id: Optional[uuid.UUID] = None

class SupplierOrderResponse(SupplierOrderBase):
    id: uuid.UUID
    actual_delivery_date: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    
    # Include organization name for easier display
    ordering_organization_name: Optional[str] = None
    
    # Include order items
    items: List['SupplierOrderItemResponse'] = []

    class Config:
        from_attributes = True

class SupplierOrderItemBase(BaseModel):
    supplier_order_id: uuid.UUID
    part_id: uuid.UUID
    quantity: Decimal
    unit_price: Optional[Decimal] = None

class SupplierOrderItemCreate(SupplierOrderItemBase):
    pass

class SupplierOrderItemUpdate(BaseModel):
    quantity: Optional[Decimal] = None
    unit_price: Optional[Decimal] = None

class SupplierOrderItemResponse(SupplierOrderItemBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    # Include related data for easier display
    part_number: Optional[str] = None
    part_name: Optional[str] = None
    unit_of_measure: Optional[str] = None
    quantity_received: Decimal = Field(default=0, decimal_places=3)
    quantity_written_off: Decimal = Field(default=0, decimal_places=3)

    class Config:
        from_attributes = True

# --- Supplier Order Action Schemas ---
class SupplierOrderReceiveItemRequest(BaseModel):
    """A single line item being received now, as part of a (possibly partial) delivery."""
    supplier_order_item_id: uuid.UUID
    quantity: Decimal = Field(..., gt=0, decimal_places=3)

class SupplierOrderReceiveRequest(BaseModel):
    """Request schema for receiving a supplier order, in full or in part."""
    actual_delivery_date: datetime = Field(default_factory=datetime.now)
    receiving_warehouse_id: uuid.UUID
    notes: Optional[str] = None
    items: List[SupplierOrderReceiveItemRequest] = Field(..., min_length=1, description="Line items and quantities being received now. Can be less than the full remaining ordered quantity for a partial delivery.")

class SupplierOrderWriteOffItemRequest(BaseModel):
    """A single line item being declared lost/discontinued/never coming, closing the receipt gap for that quantity."""
    supplier_order_item_id: uuid.UUID
    quantity: Decimal = Field(..., gt=0, decimal_places=3)
    reason: str = Field(..., min_length=1, max_length=255, description="Why this quantity is being written off, e.g. 'Backordered - cancelled'.")

class SupplierOrderWriteOffRequest(BaseModel):
    """Request schema for writing off outstanding ordered-but-never-received quantity."""
    notes: Optional[str] = None
    items: List[SupplierOrderWriteOffItemRequest] = Field(..., min_length=1, description="Line items and quantities being written off as never coming.")

# Update forward references for Pydantic
SupplierOrderResponse.model_rebuild()