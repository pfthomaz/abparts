# backend/app/schemas/customer_order.py

import uuid
from typing import Optional, List
from decimal import Decimal
from datetime import datetime
from pydantic import BaseModel, Field

class CustomerOrderBase(BaseModel):
    customer_organization_id: uuid.UUID
    oraseas_organization_id: uuid.UUID
    order_date: datetime
    expected_delivery_date: Optional[datetime] = None
    shipped_date: Optional[datetime] = None
    shipped_by_user_id: Optional[uuid.UUID] = None
    status: str = "Pending"  # Requested, Pending, Shipped, Received, Delivered, Cancelled
    ordered_by_user_id: Optional[uuid.UUID] = None
    notes: Optional[str] = None

class CustomerOrderCreate(CustomerOrderBase):
    pass

class CustomerOrderUpdate(BaseModel):
    expected_delivery_date: Optional[datetime] = None
    shipped_date: Optional[datetime] = None
    shipped_by_user_id: Optional[uuid.UUID] = None
    actual_delivery_date: Optional[datetime] = None
    status: Optional[str] = None
    notes: Optional[str] = None
    receiving_warehouse_id: Optional[uuid.UUID] = None

class CustomerOrderResponse(CustomerOrderBase):
    id: uuid.UUID
    actual_delivery_date: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    
    # Include related data for easier display
    customer_organization_name: Optional[str] = None
    oraseas_organization_name: Optional[str] = None
    ordered_by_username: Optional[str] = None
    shipped_by_username: Optional[str] = None
    
    # Include order items
    items: List['CustomerOrderItemResponse'] = []

    class Config:
        from_attributes = True

# --- Customer Order Action Schemas ---
class CustomerOrderShipItemRequest(BaseModel):
    """A single line item being shipped now, as part of a (possibly partial) shipment."""
    customer_order_item_id: uuid.UUID
    quantity: Decimal = Field(..., gt=0, decimal_places=3)

class CustomerOrderShipRequest(BaseModel):
    """Request schema for marking an order as shipped (Oraseas EE action)"""
    shipped_date: datetime = Field(default_factory=datetime.now)
    tracking_number: Optional[str] = Field(None, max_length=255)
    source_warehouse_id: Optional[uuid.UUID] = Field(None, description="Warehouse to ship from. If not provided, uses the first warehouse of the Oraseas organization.")
    notes: Optional[str] = None
    items: List[CustomerOrderShipItemRequest] = Field(..., min_length=1, description="Line items and quantities being shipped in this batch. Can be less than the full remaining quantity for a partial shipment.")

class CustomerOrderReceiptItemRequest(BaseModel):
    """A single line item being confirmed as received now, as part of a (possibly partial) receipt."""
    customer_order_item_id: uuid.UUID
    quantity: Decimal = Field(..., gt=0, decimal_places=3)

class CustomerOrderConfirmReceiptRequest(BaseModel):
    """Request schema for confirming order receipt (Customer action)"""
    actual_delivery_date: datetime = Field(default_factory=datetime.now)
    receiving_warehouse_id: uuid.UUID
    notes: Optional[str] = None
    items: List[CustomerOrderReceiptItemRequest] = Field(..., min_length=1, description="Line items and quantities being confirmed as received now. Can be less than the full shipped-but-unreceived quantity for a partial receipt.")

class CustomerOrderItemBase(BaseModel):
    customer_order_id: uuid.UUID
    part_id: uuid.UUID
    quantity: Decimal
    unit_price: Optional[Decimal] = None

class CustomerOrderItemCreate(CustomerOrderItemBase):
    pass

class CustomerOrderItemUpdate(BaseModel):
    quantity: Optional[Decimal] = None
    unit_price: Optional[Decimal] = None

class CustomerOrderItemResponse(CustomerOrderItemBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    # Include related data for easier display
    part_number: Optional[str] = None
    part_name: Optional[str] = None
    unit_of_measure: Optional[str] = None
    quantity_shipped: Decimal = Field(default=0, decimal_places=3)
    quantity_received: Decimal = Field(default=0, decimal_places=3)

    class Config:
        from_attributes = True

# Update forward references for Pydantic
CustomerOrderResponse.model_rebuild()