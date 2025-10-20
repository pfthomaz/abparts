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
    status: str = "Pending"  # Pending, Shipped, Delivered, Cancelled
    ordered_by_user_id: Optional[uuid.UUID] = None
    notes: Optional[str] = None

class CustomerOrderCreate(CustomerOrderBase):
    pass

class CustomerOrderUpdate(BaseModel):
    expected_delivery_date: Optional[datetime] = None
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
    
    # Include order items
    items: List['CustomerOrderItemResponse'] = []

    class Config:
        from_attributes = True

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

    class Config:
        from_attributes = True

# Update forward references for Pydantic
CustomerOrderResponse.model_rebuild()