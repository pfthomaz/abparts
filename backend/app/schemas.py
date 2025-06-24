# backend/app/schemas.py

import uuid
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, EmailStr

# Base models for common attributes
class OrganizationBase(BaseModel):
    name: str
    type: str
    address: Optional[str] = None
    contact_info: Optional[str] = None

class UserBase(BaseModel):
    username: str
    email: EmailStr # Use EmailStr for email validation
    name: Optional[str] = None
    role: str
    organization_id: uuid.UUID # Added: User must belong to an organization

class PartBase(BaseModel):
    part_number: str
    name: str
    description: Optional[str] = None
    is_proprietary: bool = False
    is_consumable: bool = False
    manufacturer_delivery_time_days: Optional[int] = None
    local_supplier_delivery_time_days: Optional[int] = None
    image_urls: List[str] = Field(default_factory=list, description="URLs of images associated with the part") # New: List of image URLs

class InventoryBase(BaseModel):
    organization_id: uuid.UUID
    part_id: uuid.UUID
    current_stock: int = 0
    minimum_stock_recommendation: int = 0
    reorder_threshold_set_by: Optional[str] = None
    last_recommendation_update: Optional[datetime] = None

class SupplierOrderBase(BaseModel):
    ordering_organization_id: uuid.UUID
    supplier_name: str
    order_date: datetime
    expected_delivery_date: Optional[datetime] = None
    actual_delivery_date: Optional[datetime] = None
    status: str
    notes: Optional[str] = None

class SupplierOrderItemBase(BaseModel):
    supplier_order_id: uuid.UUID
    part_id: uuid.UUID
    quantity: int = 1
    unit_price: Optional[float] = None # Using float for price, consider Decimal for precision

class CustomerOrderBase(BaseModel):
    customer_organization_id: uuid.UUID
    oraseas_organization_id: uuid.UUID
    order_date: datetime
    expected_delivery_date: Optional[datetime] = None
    actual_delivery_date: Optional[datetime] = None
    status: str
    ordered_by_user_id: Optional[uuid.UUID] = None
    notes: Optional[str] = None

class CustomerOrderItemBase(BaseModel):
    customer_order_id: uuid.UUID
    part_id: uuid.UUID
    quantity: int = 1
    unit_price: Optional[float] = None

class PartUsageBase(BaseModel):
    customer_organization_id: uuid.UUID
    part_id: uuid.UUID
    usage_date: datetime
    quantity_used: int = 1
    machine_id: Optional[str] = None
    recorded_by_user_id: Optional[uuid.UUID] = None
    notes: Optional[str] = None


# Create models (for POST requests)
class OrganizationCreate(OrganizationBase):
    pass

class UserCreate(UserBase):
    password: str # Password for creation, will be hashed

class PartCreate(PartBase):
    pass

class InventoryCreate(InventoryBase):
    pass

class SupplierOrderCreate(SupplierOrderBase):
    pass

class SupplierOrderItemCreate(SupplierOrderItemBase):
    pass

class CustomerOrderCreate(CustomerOrderBase):
    pass

class CustomerOrderItemCreate(CustomerOrderItemBase):
    pass

class PartUsageCreate(PartUsageBase):
    pass


# Update models (for PUT requests, fields are optional)
class OrganizationUpdate(OrganizationBase):
    name: Optional[str] = None
    type: Optional[str] = None
    address: Optional[str] = None
    contact_info: Optional[str] = None

class UserUpdate(UserBase):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None # Password can be optional for update
    name: Optional[str] = None
    role: Optional[str] = None
    organization_id: Optional[uuid.UUID] = None # Make organization_id optional for update

class PartUpdate(PartBase):
    part_number: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    is_proprietary: Optional[bool] = None
    is_consumable: Optional[bool] = None
    manufacturer_delivery_time_days: Optional[int] = None
    local_supplier_delivery_time_days: Optional[int] = None
    image_urls: Optional[List[str]] = None # New: Optional for updates

class InventoryUpdate(InventoryBase):
    organization_id: Optional[uuid.UUID] = None
    part_id: Optional[uuid.UUID] = None
    current_stock: Optional[int] = None
    minimum_stock_recommendation: Optional[int] = None
    reorder_threshold_set_by: Optional[str] = None
    last_recommendation_update: Optional[datetime] = None

class SupplierOrderUpdate(SupplierOrderBase):
    ordering_organization_id: Optional[uuid.UUID] = None
    supplier_name: Optional[str] = None
    order_date: Optional[datetime] = None
    expected_delivery_date: Optional[datetime] = None
    actual_delivery_date: Optional[str] = None
    status: Optional[str] = None
    notes: Optional[str] = None

class SupplierOrderItemUpdate(SupplierOrderItemBase):
    supplier_order_id: Optional[uuid.UUID] = None
    part_id: Optional[uuid.UUID] = None
    quantity: Optional[int] = None
    unit_price: Optional[float] = None

class CustomerOrderUpdate(CustomerOrderBase):
    customer_organization_id: Optional[uuid.UUID] = None
    oraseas_organization_id: Optional[uuid.UUID] = None
    order_date: Optional[datetime] = None
    expected_delivery_date: Optional[datetime] = None
    actual_delivery_date: Optional[str] = None
    status: Optional[str] = None
    ordered_by_user_id: Optional[uuid.UUID] = None
    notes: Optional[str] = None

class CustomerOrderItemUpdate(CustomerOrderItemBase):
    customer_order_id: Optional[uuid.UUID] = None
    part_id: Optional[uuid.UUID] = None
    quantity: Optional[int] = None
    unit_price: Optional[float] = None

class PartUsageUpdate(PartUsageBase):
    customer_organization_id: Optional[uuid.UUID] = None
    part_id: Optional[uuid.UUID] = None
    usage_date: Optional[datetime] = None
    quantity_used: Optional[int] = None
    machine_id: Optional[str] = None
    recorded_by_user_id: Optional[uuid.UUID] = None
    notes: Optional[str] = None


# Response models (for GET responses, include the ID and any relationships you want to expose)
class OrganizationResponse(OrganizationBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    class Config:
        orm_mode = True # Enables ORM mode for automatic mapping from SQLAlchemy to Pydantic

class UserResponse(UserBase):
    id: uuid.UUID
    # organization_id: uuid.UUID # Removed from UserResponse as it's already in UserBase
    created_at: datetime
    updated_at: datetime
    class Config:
        orm_mode = True

class PartResponse(PartBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    class Config:
        orm_mode = True

class InventoryResponse(InventoryBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    class Config:
        orm_mode = True

class SupplierOrderResponse(SupplierOrderBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    class Config:
        orm_mode = True

class SupplierOrderItemResponse(SupplierOrderItemBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    class Config:
        orm_mode = True

class CustomerOrderResponse(CustomerOrderBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    class Config:
        orm_mode = True

class CustomerOrderItemResponse(CustomerOrderItemBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    class Config:
        orm_mode = True

class PartUsageResponse(PartUsageBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    class Config:
        orm_mode = True

# Pydantic model for image upload response
class ImageUploadResponse(BaseModel): # New: Schema for image upload response
    url: str

# Pydantic model for the token response
class Token(BaseModel):
    access_token: str
    token_type: str
