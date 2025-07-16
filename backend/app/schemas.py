# backend/app/schemas.py

import uuid
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, EmailStr, Field, VERSION

# --- Base Schemas with common fields ---
class BaseSchema(BaseModel):
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    class Config:
        from_attributes = True # Allow ORM models to be converted to Pydantic models


# --- Organization Schemas ---
from enum import Enum

class OrganizationTypeEnum(str, Enum):
    ORASEAS_EE = "oraseas_ee"
    BOSSAQUA = "bossaqua"
    CUSTOMER = "customer"
    SUPPLIER = "supplier"

class OrganizationBase(BaseModel):
    name: str = Field(..., max_length=255)
    organization_type: OrganizationTypeEnum
    parent_organization_id: Optional[uuid.UUID] = None
    address: Optional[str] = None
    contact_info: Optional[str] = None
    is_active: bool = True

class OrganizationCreate(OrganizationBase):
    pass

class OrganizationUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=255)
    organization_type: Optional[OrganizationTypeEnum] = None
    parent_organization_id: Optional[uuid.UUID] = None
    address: Optional[str] = None
    contact_info: Optional[str] = None
    is_active: Optional[bool] = None

class OrganizationResponse(OrganizationBase, BaseSchema):
    parent_organization: Optional['OrganizationResponse'] = None
    child_organizations: List['OrganizationResponse'] = []

class OrganizationHierarchyResponse(BaseModel):
    """Response schema for organization hierarchy queries"""
    organization: OrganizationResponse
    children: List['OrganizationHierarchyResponse'] = []
    depth: int = 0

class OrganizationTypeFilterResponse(BaseModel):
    """Response schema for organization type filtering"""
    organization_type: OrganizationTypeEnum
    organizations: List[OrganizationResponse]
    count: int


# --- User Schemas ---
class UserBase(BaseModel):
    organization_id: uuid.UUID
    username: str = Field(..., max_length=255)
    email: EmailStr = Field(..., max_length=255)
    name: Optional[str] = Field(None, max_length=255)
    role: str = Field(..., max_length=50) # e.g., 'Oraseas Admin', 'Customer User'
    is_active: bool = True

class UserCreate(UserBase):
    password: str = Field(..., min_length=8) # Password should be hashed in backend

class UserUpdate(UserBase):
    organization_id: Optional[uuid.UUID] = None
    username: Optional[str] = Field(None, max_length=255)
    email: Optional[EmailStr] = Field(None, max_length=255)
    password: Optional[str] = Field(None, min_length=8) # For password change
    role: Optional[str] = Field(None, max_length=50)

class UserResponse(UserBase, BaseSchema):
    class Config(BaseSchema.Config):
        exclude = {'password_hash'} # Do not expose password hash


# --- Token Schemas (for authentication) ---
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    user_id: uuid.UUID
    username: Optional[str] = None
    organization_id: uuid.UUID
    role: str


# --- Dashboard Schemas (New!) ---
class DashboardMetricsResponse(BaseModel):
    total_parts: int
    total_inventory_items: int
    low_stock_items: int
    pending_customer_orders: int
    pending_supplier_orders: int

class LowStockByOrgResponse(BaseModel):
    organization_name: str
    low_stock_count: int


# --- Machine Schemas (New!) ---
class MachineBase(BaseModel):
    organization_id: uuid.UUID
    model_type: str = Field(..., max_length=100) # e.g., 'V3.1B', 'V4.0'
    name: str = Field(..., max_length=255)
    serial_number: str = Field(..., max_length=255)

class MachineCreate(MachineBase):
    pass

class MachineUpdate(MachineBase):
    organization_id: Optional[uuid.UUID] = None
    model_type: Optional[str] = Field(None, max_length=100)
    name: Optional[str] = Field(None, max_length=255)
    serial_number: Optional[str] = Field(None, max_length=255)

class MachineResponse(MachineBase, BaseSchema):
    pass


# --- Part Schemas ---
class PartBase(BaseModel):
    part_number: str = Field(..., max_length=255)
    name: str = Field(..., max_length=255)
    description: Optional[str] = None
    is_proprietary: bool = False
    is_consumable: bool = False
    manufacturer_delivery_time_days: Optional[int] = None
    local_supplier_delivery_time_days: Optional[int] = None
    image_urls: Optional[List[str]] = None

class PartCreate(PartBase):
    pass

class PartUpdate(PartBase):
    part_number: Optional[str] = Field(None, max_length=255)
    name: Optional[str] = Field(None, max_length=255)

class PartResponse(PartBase, BaseSchema):
    pass

# --- New: Image Upload Response Schema ---
class ImageUploadResponse(BaseModel):
    url: str
    message: str = "Image uploaded successfully"


# --- Inventory Schemas ---
class InventoryBase(BaseModel):
    organization_id: uuid.UUID
    part_id: uuid.UUID
    location: Optional[str] = Field(None, max_length=255)
    current_stock: int = 0
    minimum_stock_recommendation: int = 0
    reorder_threshold_set_by: Optional[str] = Field(None, max_length=50)
    last_recommendation_update: Optional[datetime] = None

class InventoryCreate(InventoryBase):
    pass

class InventoryUpdate(InventoryBase):
    organization_id: Optional[uuid.UUID] = None
    part_id: Optional[uuid.UUID] = None
    location: Optional[str] = Field(None, max_length=255)
    current_stock: Optional[int] = None
    minimum_stock_recommendation: Optional[int] = None
    reorder_threshold_set_by: Optional[str] = Field(None, max_length=50)
    last_recommendation_update: Optional[datetime] = None

class InventoryResponse(InventoryBase, BaseSchema):
    pass


# --- Supplier Order Schemas ---
class SupplierOrderBase(BaseModel):
    ordering_organization_id: uuid.UUID
    supplier_name: str = Field(..., max_length=255)
    order_date: datetime
    expected_delivery_date: Optional[datetime] = None
    actual_delivery_date: Optional[datetime] = None
    status: str = Field(..., max_length=50)
    notes: Optional[str] = None

class SupplierOrderCreate(SupplierOrderBase):
    pass

class SupplierOrderUpdate(SupplierOrderBase):
    ordering_organization_id: Optional[uuid.UUID] = None
    supplier_name: Optional[str] = Field(None, max_length=255)
    order_date: Optional[datetime] = None
    expected_delivery_date: Optional[datetime] = None
    actual_delivery_date: Optional[datetime] = None
    status: Optional[str] = Field(None, max_length=50)
    notes: Optional[str] = None

class SupplierOrderResponse(SupplierOrderBase, BaseSchema):
    items: List['SupplierOrderItemResponse'] = []


# --- Supplier Order Item Schemas ---
class SupplierOrderItemBase(BaseModel):
    supplier_order_id: uuid.UUID
    part_id: uuid.UUID
    quantity: int = 1
    unit_price: Optional[float] = None

class SupplierOrderItemCreate(SupplierOrderItemBase):
    pass

class SupplierOrderItemUpdate(SupplierOrderItemBase):
    supplier_order_id: Optional[uuid.UUID] = None
    part_id: Optional[uuid.UUID] = None
    quantity: Optional[int] = None
    unit_price: Optional[float] = None

class SupplierOrderItemResponse(SupplierOrderItemBase, BaseSchema):
    part: PartResponse


# --- Customer Order Schemas ---
class CustomerOrderBase(BaseModel):
    customer_organization_id: uuid.UUID
    oraseas_organization_id: uuid.UUID
    order_date: datetime
    expected_delivery_date: Optional[datetime] = None
    actual_delivery_date: Optional[datetime] = None
    status: str = Field(..., max_length=50)
    ordered_by_user_id: Optional[uuid.UUID] = None
    notes: Optional[str] = None

class CustomerOrderCreate(CustomerOrderBase):
    pass

class CustomerOrderUpdate(CustomerOrderBase):
    customer_organization_id: Optional[uuid.UUID] = None
    oraseas_organization_id: Optional[uuid.UUID] = None
    order_date: Optional[datetime] = None
    expected_delivery_date: Optional[datetime] = None
    actual_delivery_date: Optional[datetime] = None
    status: Optional[str] = Field(None, max_length=50)
    ordered_by_user_id: Optional[uuid.UUID] = None
    notes: Optional[str] = None

class CustomerOrderResponse(CustomerOrderBase, BaseSchema):
    items: List['CustomerOrderItemResponse'] = []
    customer_organization: Optional[OrganizationResponse] = None

# --- Customer Order Item Schemas ---
class CustomerOrderItemBase(BaseModel):
    customer_order_id: uuid.UUID
    part_id: uuid.UUID
    quantity: int = 1
    unit_price: Optional[float] = None

class CustomerOrderItemCreate(CustomerOrderItemBase):
    pass

class CustomerOrderItemUpdate(CustomerOrderItemBase):
    customer_order_id: Optional[uuid.UUID] = None
    part_id: Optional[uuid.UUID] = None
    quantity: Optional[int] = None
    unit_price: Optional[float] = None

class CustomerOrderItemResponse(CustomerOrderItemBase, BaseSchema):
    part: PartResponse

# Forward-referencing resolution
# This handles compatibility between Pydantic v1 and v2.
if VERSION.startswith('1.'):
    SupplierOrderResponse.update_forward_refs()
    CustomerOrderResponse.update_forward_refs()
else:
    SupplierOrderResponse.model_rebuild()
    CustomerOrderResponse.model_rebuild()

# --- Part Usage Schemas ---
class PartUsageBase(BaseModel):
    customer_organization_id: uuid.UUID
    part_id: uuid.UUID
    usage_date: datetime
    quantity_used: int = 1
    machine_id: Optional[uuid.UUID] = None # Updated: now expects UUID
    recorded_by_user_id: Optional[uuid.UUID] = None
    notes: Optional[str] = None

class PartUsageCreate(PartUsageBase):
    pass

class PartUsageUpdate(PartUsageBase):
    customer_organization_id: Optional[uuid.UUID] = None
    part_id: Optional[uuid.UUID] = None
    usage_date: Optional[datetime] = None
    quantity_used: Optional[int] = None
    machine_id: Optional[uuid.UUID] = None # Updated: now expects UUID
    recorded_by_user_id: Optional[uuid.UUID] = None
    notes: Optional[str] = None

class PartUsageResponse(PartUsageBase, BaseSchema):
    pass


# --- Stock Adjustment Schemas (New!) ---
class StockAdjustmentBase(BaseModel):
    inventory_id: uuid.UUID
    user_id: uuid.UUID # Will be set from current_user in the router
    adjustment_date: datetime = Field(default_factory=datetime.now)
    quantity_adjusted: int
    reason_code: str # Should match StockAdjustmentReason enum values
    notes: Optional[str] = None

class StockAdjustmentCreate(BaseModel): # Separate from Base to not include user_id from request body
    # inventory_id will come from path parameter
    quantity_adjusted: int
    reason_code: str # Should match StockAdjustmentReason enum values
    notes: Optional[str] = None

class StockAdjustmentResponse(StockAdjustmentBase, BaseSchema):
    # Optionally, include nested user and inventory item details
    # user: Optional[UserResponse] = None # Example: if you want to nest user details
    # inventory_item: Optional[InventoryResponse] = None # Example
    pass


# --- Stocktake Worksheet Schemas (New!) ---
class StocktakeWorksheetItemResponse(BaseModel):
    inventory_id: uuid.UUID # Crucial for making adjustments later
    part_id: uuid.UUID
    part_number: str
    part_name: str
    system_quantity: int

    class Config:
        from_attributes = True # Allow ORM models to be converted (though this is a custom construction)


# --- Stocktake Location Schema (New!) ---
class StocktakeLocation(BaseModel):
    name: str

