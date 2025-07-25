# backend/app/schemas.py

import uuid
from datetime import datetime
from decimal import Decimal
from typing import List, Optional
from pydantic import BaseModel, EmailStr, Field, VERSION, validator

# --- Base Schemas with common fields ---
class BaseSchema(BaseModel):
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    class Config:
        from_attributes = True # Allow ORM models to be converted to Pydantic models
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }


# --- Organization Schemas ---
from enum import Enum

class OrganizationTypeEnum(str, Enum):
    oraseas_ee = "oraseas_ee"
    bossaqua = "bossaqua"
    customer = "customer"
    supplier = "supplier"

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

class OrganizationValidationRequest(BaseModel):
    """Request schema for organization validation endpoint"""
    name: str = Field(..., max_length=255)
    organization_type: OrganizationTypeEnum
    parent_organization_id: Optional[uuid.UUID] = None
    address: Optional[str] = None
    contact_info: Optional[str] = None
    is_active: bool = True
    id: Optional[uuid.UUID] = None  # For update validation
    
    @validator('parent_organization_id', pre=True)
    def empty_string_to_none(cls, v):
        if v == '':
            return None
        return v
    
    @validator('address', 'contact_info', pre=True)
    def empty_string_to_none_str(cls, v):
        if v == '':
            return None
        return v

class OrganizationValidationError(BaseModel):
    """Individual validation error"""
    field: str
    message: str

class OrganizationValidationResponse(BaseModel):
    """Response schema for organization validation endpoint"""
    valid: bool
    errors: List[OrganizationValidationError] = []


class OrganizationHierarchyNode(BaseModel):
    """Response schema for organization hierarchy tree structure"""
    id: uuid.UUID
    name: str
    organization_type: OrganizationTypeEnum
    parent_organization_id: Optional[uuid.UUID] = None
    address: Optional[str] = None
    contact_info: Optional[str] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime
    children: List['OrganizationHierarchyNode'] = []
    
    class Config:
        from_attributes = True


# --- User Schemas ---
class UserRoleEnum(str, Enum):
    USER = "user"
    ADMIN = "admin"
    SUPER_ADMIN = "super_admin"

class UserStatusEnum(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    PENDING_INVITATION = "pending_invitation"
    LOCKED = "locked"

class UserBase(BaseModel):
    organization_id: uuid.UUID
    username: str = Field(..., max_length=255)
    email: EmailStr = Field(..., max_length=255)
    name: Optional[str] = Field(None, max_length=255)
    role: UserRoleEnum
    user_status: UserStatusEnum = UserStatusEnum.ACTIVE
    is_active: bool = True

class UserCreate(UserBase):
    password: str = Field(..., min_length=8) # Password should be hashed in backend

class UserUpdate(BaseModel):
    organization_id: Optional[uuid.UUID] = None
    username: Optional[str] = Field(None, max_length=255)
    email: Optional[EmailStr] = Field(None, max_length=255)
    name: Optional[str] = Field(None, max_length=255)
    password: Optional[str] = Field(None, min_length=8) # For password change
    role: Optional[UserRoleEnum] = None
    user_status: Optional[UserStatusEnum] = None
    is_active: Optional[bool] = None

class UserResponse(UserBase, BaseSchema):
    failed_login_attempts: int = 0
    locked_until: Optional[datetime] = None
    last_login: Optional[datetime] = None
    invitation_token: Optional[str] = None
    invitation_expires_at: Optional[datetime] = None
    
    class Config(BaseSchema.Config):
        exclude = {'password_hash', 'password_reset_token', 'password_reset_expires_at'} # Do not expose sensitive fields


# --- Token Schemas (for authentication) ---
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    user_id: uuid.UUID
    username: Optional[str] = None
    organization_id: uuid.UUID
    role: str


# --- User Invitation Schemas ---
class UserInvitationCreate(BaseModel):
    email: EmailStr = Field(..., max_length=255)
    name: Optional[str] = Field(None, max_length=255)
    role: UserRoleEnum
    organization_id: uuid.UUID

class UserInvitationResponse(BaseModel):
    id: uuid.UUID
    email: str
    name: Optional[str]
    role: UserRoleEnum
    organization_id: uuid.UUID
    invitation_token: str
    invitation_expires_at: datetime
    user_status: UserStatusEnum
    invited_by_user_id: uuid.UUID
    created_at: datetime
    
    class Config:
        from_attributes = True

class UserInvitationAcceptance(BaseModel):
    invitation_token: str = Field(..., min_length=32)
    username: str = Field(..., min_length=3, max_length=255)
    password: str = Field(..., min_length=8)
    name: Optional[str] = Field(None, max_length=255)

class UserInvitationResend(BaseModel):
    user_id: uuid.UUID

class InvitationAuditLogResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    action: str  # 'invited', 'resent', 'accepted', 'expired'
    performed_by_user_id: Optional[uuid.UUID]
    timestamp: datetime
    details: Optional[str]
    
    class Config:
        from_attributes = True


# --- User Profile and Self-Service Schemas ---
class UserProfileUpdate(BaseModel):
    """Schema for user profile self-service updates"""
    name: Optional[str] = Field(None, max_length=255)
    email: Optional[EmailStr] = Field(None, max_length=255)
    
class UserPasswordChange(BaseModel):
    """Schema for secure password change"""
    current_password: str = Field(..., min_length=1)
    new_password: str = Field(..., min_length=8)

class UserProfileResponse(BaseModel):
    """Schema for user profile view with role and organization info"""
    id: uuid.UUID
    username: str
    email: str
    name: Optional[str]
    role: UserRoleEnum
    user_status: UserStatusEnum
    organization_id: uuid.UUID
    organization_name: str
    organization_type: str
    last_login: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class PasswordResetRequest(BaseModel):
    """Schema for password reset request"""
    email: EmailStr = Field(..., max_length=255)

class PasswordResetConfirm(BaseModel):
    """Schema for password reset confirmation"""
    reset_token: str = Field(..., min_length=32)
    new_password: str = Field(..., min_length=8)

class EmailVerificationRequest(BaseModel):
    """Schema for email change verification"""
    new_email: EmailStr = Field(..., max_length=255)

class EmailVerificationConfirm(BaseModel):
    """Schema for email verification confirmation"""
    verification_token: str = Field(..., min_length=32)

class UserAccountStatusUpdate(BaseModel):
    """Schema for user account status management"""
    user_status: UserStatusEnum


# --- User Management Audit Log Schemas (Task 3.4) ---
class UserManagementAuditLogResponse(BaseModel):
    """Response schema for user management audit logs"""
    id: uuid.UUID
    user_id: uuid.UUID
    action: str  # 'deactivated', 'reactivated', 'soft_deleted', 'role_changed', 'status_changed'
    performed_by_user_id: uuid.UUID
    timestamp: datetime
    details: Optional[str]
    user_email: Optional[str] = None
    user_name: Optional[str] = None
    performed_by_name: Optional[str] = None
    
    class Config:
        from_attributes = True


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
    customer_organization_id: uuid.UUID
    model_type: str = Field(..., max_length=100) # e.g., 'V3.1B', 'V4.0'
    name: str = Field(..., max_length=255)
    serial_number: str = Field(..., max_length=255)

class MachineCreate(MachineBase):
    pass

class MachineUpdate(BaseModel):
    customer_organization_id: Optional[uuid.UUID] = None
    model_type: Optional[str] = Field(None, max_length=100)
    name: Optional[str] = Field(None, max_length=255)
    serial_number: Optional[str] = Field(None, max_length=255)

class MachineResponse(MachineBase, BaseSchema):
    pass


# --- Part Schemas ---
class PartTypeEnum(str, Enum):
    CONSUMABLE = "consumable"
    BULK_MATERIAL = "bulk_material"

class PartBase(BaseModel):
    part_number: str = Field(..., max_length=255)
    name: str = Field(..., max_length=255)
    description: Optional[str] = None
    part_type: PartTypeEnum = PartTypeEnum.CONSUMABLE
    is_proprietary: bool = False
    unit_of_measure: str = Field(default="pieces", max_length=50)
    manufacturer_part_number: Optional[str] = Field(None, max_length=255)
    manufacturer_delivery_time_days: Optional[int] = None
    local_supplier_delivery_time_days: Optional[int] = None
    image_urls: Optional[List[str]] = None

class PartCreate(PartBase):
    pass

class PartUpdate(BaseModel):
    part_number: Optional[str] = Field(None, max_length=255)
    name: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    part_type: Optional[PartTypeEnum] = None
    is_proprietary: Optional[bool] = None
    unit_of_measure: Optional[str] = Field(None, max_length=50)
    manufacturer_part_number: Optional[str] = Field(None, max_length=255)
    manufacturer_delivery_time_days: Optional[int] = None
    local_supplier_delivery_time_days: Optional[int] = None
    image_urls: Optional[List[str]] = None

class PartResponse(PartBase, BaseSchema):
    pass

# --- New: Image Upload Response Schema ---
class ImageUploadResponse(BaseModel):
    url: str
    message: str = "Image uploaded successfully"


# --- Warehouse Schemas ---
class WarehouseBase(BaseModel):
    organization_id: uuid.UUID
    name: str = Field(..., max_length=255)
    location: Optional[str] = Field(None, max_length=500)
    description: Optional[str] = None
    is_active: bool = True

class WarehouseCreate(WarehouseBase):
    pass

class WarehouseUpdate(BaseModel):
    organization_id: Optional[uuid.UUID] = None
    name: Optional[str] = Field(None, max_length=255)
    location: Optional[str] = Field(None, max_length=500)
    description: Optional[str] = None
    is_active: Optional[bool] = None

class WarehouseResponse(WarehouseBase, BaseSchema):
    """Response schema for warehouse endpoints"""
    class Config:
        from_attributes = True
        
# Explicitly export WarehouseResponse to ensure it's available
__all__ = [
    'WarehouseResponse',
    'WarehouseBase',
    'WarehouseCreate',
    'WarehouseUpdate',
]


# --- Inventory Schemas ---
class InventoryBase(BaseModel):
    warehouse_id: uuid.UUID
    part_id: uuid.UUID
    current_stock: Decimal = Field(default=0, decimal_places=3)
    minimum_stock_recommendation: Decimal = Field(default=0, decimal_places=3)
    unit_of_measure: str = Field(..., max_length=50)
    reorder_threshold_set_by: Optional[str] = Field(None, max_length=50)
    last_recommendation_update: Optional[datetime] = None

class InventoryCreate(InventoryBase):
    pass

class InventoryUpdate(BaseModel):
    warehouse_id: Optional[uuid.UUID] = None
    part_id: Optional[uuid.UUID] = None
    current_stock: Optional[Decimal] = Field(None, decimal_places=3)
    minimum_stock_recommendation: Optional[Decimal] = Field(None, decimal_places=3)
    unit_of_measure: Optional[str] = Field(None, max_length=50)
    reorder_threshold_set_by: Optional[str] = Field(None, max_length=50)
    last_recommendation_update: Optional[datetime] = None

class InventoryResponse(InventoryBase, BaseSchema):
    last_updated: datetime
    pass

class InventoryTransferRequest(BaseModel):
    """Schema for inventory transfer requests between warehouses."""
    from_warehouse_id: uuid.UUID
    to_warehouse_id: uuid.UUID
    part_id: uuid.UUID
    quantity: float = Field(..., gt=0, description="Quantity to transfer (must be positive)")
    notes: Optional[str] = Field(None, max_length=500, description="Optional notes for the transfer")


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
    quantity: Decimal = Field(default=1, decimal_places=3)
    unit_price: Optional[Decimal] = Field(None, decimal_places=2)

class SupplierOrderItemCreate(SupplierOrderItemBase):
    pass

class SupplierOrderItemUpdate(BaseModel):
    supplier_order_id: Optional[uuid.UUID] = None
    part_id: Optional[uuid.UUID] = None
    quantity: Optional[Decimal] = Field(None, decimal_places=3)
    unit_price: Optional[Decimal] = Field(None, decimal_places=2)

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
    quantity: Decimal = Field(default=1, decimal_places=3)
    unit_price: Optional[Decimal] = Field(None, decimal_places=2)

class CustomerOrderItemCreate(CustomerOrderItemBase):
    pass

class CustomerOrderItemUpdate(BaseModel):
    customer_order_id: Optional[uuid.UUID] = None
    part_id: Optional[uuid.UUID] = None
    quantity: Optional[Decimal] = Field(None, decimal_places=3)
    unit_price: Optional[Decimal] = Field(None, decimal_places=2)

class CustomerOrderItemResponse(CustomerOrderItemBase, BaseSchema):
    part: PartResponse

# Forward-referencing resolution
# This handles compatibility between Pydantic v1 and v2.
if VERSION.startswith('1.'):
    SupplierOrderResponse.update_forward_refs()
    CustomerOrderResponse.update_forward_refs()
    OrganizationHierarchyNode.update_forward_refs()
else:
    SupplierOrderResponse.model_rebuild()
    CustomerOrderResponse.model_rebuild()
    OrganizationHierarchyNode.model_rebuild()

# --- Part Usage Schemas ---
class PartUsageBase(BaseModel):
    customer_organization_id: uuid.UUID
    part_id: uuid.UUID
    usage_date: datetime
    quantity_used: Decimal = Field(default=1, decimal_places=3)
    machine_id: Optional[uuid.UUID] = None
    recorded_by_user_id: Optional[uuid.UUID] = None
    notes: Optional[str] = None

class PartUsageCreate(PartUsageBase):
    pass

class PartUsageUpdate(BaseModel):
    customer_organization_id: Optional[uuid.UUID] = None
    part_id: Optional[uuid.UUID] = None
    usage_date: Optional[datetime] = None
    quantity_used: Optional[Decimal] = Field(None, decimal_places=3)
    machine_id: Optional[uuid.UUID] = None
    recorded_by_user_id: Optional[uuid.UUID] = None
    notes: Optional[str] = None

class PartUsageResponse(PartUsageBase, BaseSchema):
    pass


# --- Stock Adjustment Schemas (New!) ---
class StockAdjustmentBase(BaseModel):
    inventory_id: uuid.UUID
    user_id: uuid.UUID # Will be set from current_user in the router
    adjustment_date: datetime = Field(default_factory=datetime.now)
    quantity_adjusted: Decimal = Field(..., decimal_places=3)
    reason_code: str # Should match StockAdjustmentReason enum values
    notes: Optional[str] = None

class StockAdjustmentCreate(BaseModel): # Separate from Base to not include user_id from request body
    # inventory_id will come from path parameter
    quantity_adjusted: Decimal = Field(..., decimal_places=3)
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


# --- Session Schemas (New!) ---
class UserSessionBase(BaseModel):
    ip_address: str
    user_agent: str
    created_at: datetime
    last_activity: datetime
    expires_at: datetime

class UserSessionResponse(UserSessionBase):
    id: uuid.UUID
    session_token: str
    is_current: bool = False

class SecurityEventResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    event_type: str
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    timestamp: datetime
    details: Optional[str] = None
    risk_level: str = "medium"
    success: bool = False

    class Config:
        from_attributes = True

class AdditionalVerification(BaseModel):
    verification_type: str = "email_code"  # Default to email code verification
    verification_code: str

