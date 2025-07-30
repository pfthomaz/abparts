# backend/app/schemas/part_order.py

import uuid
from typing import Optional, List, Dict, Any
from decimal import Decimal
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field

# Enums for existing part order system
class OrderStatusEnum(str, Enum):
    REQUESTED = "requested"
    APPROVED = "approved"
    ORDERED = "ordered"
    SHIPPED = "shipped"
    RECEIVED = "received"
    CANCELLED = "cancelled"

class OrderPriorityEnum(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

class SupplierTypeEnum(str, Enum):
    ORASEAS_EE = "oraseas_ee"
    EXTERNAL_SUPPLIER = "external_supplier"

# Base schemas for existing part order system
class PartOrderRequestBase(BaseModel):
    order_number: str
    customer_organization_id: uuid.UUID
    supplier_type: SupplierTypeEnum
    supplier_organization_id: Optional[uuid.UUID] = None
    supplier_name: Optional[str] = None
    status: OrderStatusEnum
    priority: OrderPriorityEnum
    requested_delivery_date: Optional[datetime] = None
    expected_delivery_date: Optional[datetime] = None
    actual_delivery_date: Optional[datetime] = None
    notes: Optional[str] = None
    fulfillment_notes: Optional[str] = None

class PartOrderRequestCreate(BaseModel):
    customer_organization_id: uuid.UUID
    supplier_type: SupplierTypeEnum
    supplier_organization_id: Optional[uuid.UUID] = None
    supplier_name: Optional[str] = None
    priority: OrderPriorityEnum = OrderPriorityEnum.MEDIUM
    requested_delivery_date: Optional[datetime] = None
    notes: Optional[str] = None

class PartOrderRequestUpdate(BaseModel):
    supplier_type: Optional[SupplierTypeEnum] = None
    supplier_organization_id: Optional[uuid.UUID] = None
    supplier_name: Optional[str] = None
    priority: Optional[OrderPriorityEnum] = None
    requested_delivery_date: Optional[datetime] = None
    expected_delivery_date: Optional[datetime] = None
    notes: Optional[str] = None

class PartOrderRequestResponse(PartOrderRequestBase):
    id: uuid.UUID
    requested_by_user_id: uuid.UUID
    approved_by_user_id: Optional[uuid.UUID] = None
    received_by_user_id: Optional[uuid.UUID] = None
    created_at: datetime
    updated_at: datetime
    
    # Include related data
    customer_organization_name: Optional[str] = None
    supplier_organization_name: Optional[str] = None
    requested_by_username: Optional[str] = None
    approved_by_username: Optional[str] = None
    received_by_username: Optional[str] = None

    class Config:
        from_attributes = True

# Order approval and fulfillment schemas
class OrderApprovalRequest(BaseModel):
    approved: bool
    notes: Optional[str] = None

class OrderFulfillmentRequest(BaseModel):
    fulfillment_notes: Optional[str] = None
    actual_delivery_date: Optional[datetime] = None

class BatchOrderRequest(BaseModel):
    customer_organization_id: uuid.UUID
    supplier_type: SupplierTypeEnum
    supplier_organization_id: Optional[uuid.UUID] = None
    supplier_name: Optional[str] = None
    priority: OrderPriorityEnum = OrderPriorityEnum.MEDIUM
    requested_delivery_date: Optional[datetime] = None
    notes: Optional[str] = None
    items: List[Dict[str, Any]] = []

# Analytics schemas
class OrderAnalytics(BaseModel):
    total_orders: int
    orders_by_status: Dict[str, int]
    orders_by_priority: Dict[str, int]
    average_fulfillment_time: Optional[float] = None
    top_suppliers: List[Dict[str, Any]] = []

class ReorderSuggestionRequest(BaseModel):
    organization_id: Optional[uuid.UUID] = None
    warehouse_id: Optional[uuid.UUID] = None
    minimum_stock_threshold: Optional[int] = 10

class ReorderSuggestion(BaseModel):
    part_id: uuid.UUID
    part_name: str
    part_number: str
    current_stock: Decimal
    suggested_quantity: Decimal
    warehouse_id: uuid.UUID
    warehouse_name: str
    
    class Config:
        from_attributes = True