# backend/app/schemas/part_order.py

import uuid
from typing import Optional, List, Dict, Any
from decimal import Decimal
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field

# Enums for order workflow
class OrderStatusEnum(str, Enum):
    REQUESTED = "requested"
    APPROVED = "approved"
    ORDERED = "ordered"
    SHIPPED = "shipped"
    RECEIVED = "received"
    CANCELLED = "cancelled"

class SupplierTypeEnum(str, Enum):
    ORASEAS_EE = "oraseas_ee"
    EXTERNAL_SUPPLIER = "external_supplier"

class OrderPriorityEnum(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

# Part Order Request Schemas
class PartOrderRequestBase(BaseModel):
    customer_organization_id: uuid.UUID
    supplier_type: SupplierTypeEnum
    supplier_organization_id: Optional[uuid.UUID] = None  # For Oraseas EE orders
    supplier_name: Optional[str] = None  # For external suppliers
    priority: OrderPriorityEnum = OrderPriorityEnum.MEDIUM
    requested_delivery_date: Optional[datetime] = None
    notes: Optional[str] = None

class PartOrderRequestCreate(PartOrderRequestBase):
    requested_by_user_id: Optional[uuid.UUID] = None  # Will be set to current user if not provided

class PartOrderRequestUpdate(BaseModel):
    supplier_type: Optional[SupplierTypeEnum] = None
    supplier_organization_id: Optional[uuid.UUID] = None
    supplier_name: Optional[str] = None
    priority: Optional[OrderPriorityEnum] = None
    requested_delivery_date: Optional[datetime] = None
    expected_delivery_date: Optional[datetime] = None
    actual_delivery_date: Optional[datetime] = None
    status: Optional[OrderStatusEnum] = None
    notes: Optional[str] = None
    fulfillment_notes: Optional[str] = None

class PartOrderRequestResponse(PartOrderRequestBase):
    id: uuid.UUID
    order_number: str
    status: OrderStatusEnum
    expected_delivery_date: Optional[datetime] = None
    actual_delivery_date: Optional[datetime] = None
    fulfillment_notes: Optional[str] = None
    requested_by_user_id: uuid.UUID
    approved_by_user_id: Optional[uuid.UUID] = None
    received_by_user_id: Optional[uuid.UUID] = None
    created_at: datetime
    updated_at: datetime
    
    # Related data
    customer_organization_name: str
    requested_by_username: str
    approved_by_username: Optional[str] = None
    received_by_username: Optional[str] = None
    total_items: int
    total_value: Optional[Decimal] = None
    items: List["PartOrderItemResponse"] = []

    class Config:
        from_attributes = True

# Part Order Item Schemas
class PartOrderItemBase(BaseModel):
    order_request_id: uuid.UUID
    part_id: uuid.UUID
    quantity: Decimal
    unit_price: Optional[Decimal] = None
    destination_warehouse_id: uuid.UUID
    notes: Optional[str] = None

class PartOrderItemCreate(PartOrderItemBase):
    pass

class PartOrderItemUpdate(BaseModel):
    quantity: Optional[Decimal] = None
    unit_price: Optional[Decimal] = None
    destination_warehouse_id: Optional[uuid.UUID] = None
    received_quantity: Optional[Decimal] = None
    notes: Optional[str] = None

class PartOrderItemResponse(PartOrderItemBase):
    id: uuid.UUID
    received_quantity: Optional[Decimal] = None
    created_at: datetime
    updated_at: datetime
    
    # Related data
    part_number: str
    part_name: str
    part_type: str
    unit_of_measure: str
    warehouse_name: str
    is_proprietary: bool

    class Config:
        from_attributes = True

# Order Approval Schemas
class OrderApprovalRequest(BaseModel):
    order_request_id: uuid.UUID
    approved: bool
    approval_notes: Optional[str] = None
    expected_delivery_date: Optional[datetime] = None

class OrderApprovalResponse(BaseModel):
    id: uuid.UUID
    order_request_id: uuid.UUID
    approved_by_user_id: uuid.UUID
    approved: bool
    approval_notes: Optional[str] = None
    approved_at: datetime
    
    # Related data
    approved_by_username: str

    class Config:
        from_attributes = True

# Order Fulfillment Schemas
class OrderFulfillmentRequest(BaseModel):
    order_request_id: uuid.UUID
    items: List[Dict[str, Any]]  # List of {item_id, received_quantity, notes}
    actual_delivery_date: datetime
    fulfillment_notes: Optional[str] = None

class OrderFulfillmentResponse(BaseModel):
    order_request_id: uuid.UUID
    fulfilled_by_user_id: uuid.UUID
    fulfillment_date: datetime
    fulfillment_notes: Optional[str] = None
    transactions_created: List[uuid.UUID]  # List of transaction IDs created
    
    # Related data
    fulfilled_by_username: str

    class Config:
        from_attributes = True

# Batch Order Schemas
class BatchOrderRequest(BaseModel):
    customer_organization_id: uuid.UUID
    supplier_type: SupplierTypeEnum
    supplier_organization_id: Optional[uuid.UUID] = None
    supplier_name: Optional[str] = None
    priority: OrderPriorityEnum = OrderPriorityEnum.MEDIUM
    requested_delivery_date: Optional[datetime] = None
    notes: Optional[str] = None
    items: List[Dict[str, Any]]  # List of {part_id, quantity, destination_warehouse_id, unit_price?, notes?}

# Order History and Analytics
class OrderHistoryFilter(BaseModel):
    customer_organization_id: Optional[uuid.UUID] = None
    supplier_type: Optional[SupplierTypeEnum] = None
    status: Optional[OrderStatusEnum] = None
    priority: Optional[OrderPriorityEnum] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    part_id: Optional[uuid.UUID] = None

class OrderAnalytics(BaseModel):
    total_orders: int
    orders_by_status: Dict[str, int]
    orders_by_priority: Dict[str, int]
    orders_by_supplier_type: Dict[str, int]
    average_fulfillment_time: float  # in days
    total_value: Decimal
    most_ordered_parts: List[Dict[str, Any]]
    supplier_performance: List[Dict[str, Any]]

# Reorder Suggestions
class ReorderSuggestion(BaseModel):
    part_id: uuid.UUID
    part_number: str
    part_name: str
    warehouse_id: uuid.UUID
    warehouse_name: str
    current_stock: Decimal
    minimum_stock_recommendation: Decimal
    suggested_order_quantity: Decimal
    last_order_date: Optional[datetime] = None
    average_monthly_usage: Decimal
    days_until_stockout: Optional[int] = None
    priority: OrderPriorityEnum

class ReorderSuggestionRequest(BaseModel):
    organization_id: Optional[uuid.UUID] = None
    warehouse_id: Optional[uuid.UUID] = None
    part_type: Optional[str] = None
    minimum_days_stock: int = 30  # Suggest reorder if stock will run out within X days

# Update forward references
PartOrderRequestResponse.model_rebuild()