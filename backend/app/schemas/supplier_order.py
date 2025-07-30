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

class SupplierOrderResponse(SupplierOrderBase):
    id: uuid.UUID
    actual_delivery_date: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    
    # Include organization name for easier display
    ordering_organization_name: Optional[str] = None

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

    class Config:
        from_attributes = True