# backend/app/schemas/part_order.py

import uuid
from typing import Optional, List
from datetime import datetime
from decimal import Decimal
from enum import Enum
from pydantic import BaseModel, Field

class PartOrderPhase(str, Enum):
    """Enum for part order phases"""
    REQUEST = "request"
    RECEIPT = "receipt"

class PartOrderStatus(str, Enum):
    """Enum for part order status"""
    REQUESTED = "requested"
    APPROVED = "approved"
    SHIPPED = "shipped"
    RECEIVED = "received"
    CANCELLED = "cancelled"

class PartOrderItemRequest(BaseModel):
    """Schema for individual part order item"""
    part_id: uuid.UUID = Field(..., description="ID of the part being ordered")
    quantity: Decimal = Field(..., gt=0, description="Quantity of the part being ordered")
    unit_price: Optional[Decimal] = Field(None, description="Unit price of the part")
    notes: Optional[str] = Field(None, description="Notes for this specific part")

class PartOrderRequest(BaseModel):
    """Schema for part order request (phase 1)"""
    from_organization_id: uuid.UUID = Field(..., description="ID of the ordering organization")
    to_organization_id: uuid.UUID = Field(..., description="ID of the supplier organization")
    from_warehouse_id: Optional[uuid.UUID] = Field(None, description="Destination warehouse for the parts")
    order_items: List[PartOrderItemRequest] = Field(..., min_items=1, description="List of parts being ordered")
    order_date: datetime = Field(..., description="Date of the order")
    expected_delivery_date: Optional[datetime] = Field(None, description="Expected delivery date")
    performed_by_user_id: Optional[uuid.UUID] = Field(None, description="ID of the user placing the order")
    notes: Optional[str] = Field(None, description="General notes about the order")
    reference_number: Optional[str] = Field(None, description="Reference number for the order")

class PartOrderReceiptRequest(BaseModel):
    """Schema for part order receipt (phase 2)"""
    order_id: uuid.UUID = Field(..., description="ID of the original order")
    received_items: List[PartOrderItemRequest] = Field(..., min_items=1, description="List of parts actually received")
    received_date: datetime = Field(..., description="Date the parts were received")
    performed_by_user_id: Optional[uuid.UUID] = Field(None, description="ID of the user receiving the parts")
    notes: Optional[str] = Field(None, description="Notes about the receipt")

class PartOrderItemResponse(BaseModel):
    """Schema for part order item response"""
    id: uuid.UUID
    part_id: uuid.UUID
    quantity: Decimal
    unit_price: Optional[Decimal]
    notes: Optional[str]
    
    # Include related data
    part_name: Optional[str] = None
    part_number: Optional[str] = None

    class Config:
        from_attributes = True

class PartOrderResponse(BaseModel):
    """Schema for part order response"""
    id: uuid.UUID
    order_number: str
    customer_organization_id: uuid.UUID  # This is from_organization_id in the request
    supplier_organization_id: Optional[uuid.UUID]  # This is to_organization_id in the request
    supplier_name: Optional[str]
    status: str  # Using string instead of enum to match model
    priority: str
    requested_delivery_date: Optional[datetime]
    expected_delivery_date: Optional[datetime]
    actual_delivery_date: Optional[datetime]
    notes: Optional[str]
    fulfillment_notes: Optional[str]
    requested_by_user_id: uuid.UUID
    approved_by_user_id: Optional[uuid.UUID]
    received_by_user_id: Optional[uuid.UUID]
    created_at: datetime
    updated_at: datetime
    
    # Order items
    order_items: List[PartOrderItemResponse] = []
    
    # Include related data
    from_organization_name: Optional[str] = None  # customer_organization_name
    to_organization_name: Optional[str] = None    # supplier_organization_name
    performed_by_username: Optional[str] = None   # requested_by_username
    total_items: Optional[int] = None
    total_value: Optional[Decimal] = None

    class Config:
        from_attributes = True