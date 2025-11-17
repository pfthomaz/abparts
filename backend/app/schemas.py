# backend/app/schemas.py

import uuid
from datetime import datetime
from decimal import Decimal
from typing import List, Optional
from pydantic import BaseModel, EmailStr, Field, VERSION, validator, field_validator
from enum import Enum

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

class CountryEnum(str, Enum):
    GR = "GR"  # Greece
    UK = "UK"  # United Kingdom
    NO = "NO"  # Norway
    CA = "CA"  # Canada
    NZ = "NZ"  # New Zealand
    TR = "TR"  # Turkey
    OM = "OM"  # Oman
    ES = "ES"  # Spain
    CY = "CY"  # Cyprus
    SA = "SA"  # Saudi Arabia

class OrganizationBase(BaseModel):
    name: str = Field(..., max_length=255)
    organization_type: OrganizationTypeEnum
    parent_organization_id: Optional[uuid.UUID] = None
    # country: Optional[CountryEnum] = None  # Commented until DB migration runs
    address: Optional[str] = None
    contact_info: Optional[str] = None
    is_active: bool = True

class OrganizationCreate(OrganizationBase):
    country: Optional[CountryEnum] = None  # Temporarily accept country field

class OrganizationUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=255)
    organization_type: Optional[OrganizationTypeEnum] = None
    parent_organization_id: Optional[uuid.UUID] = None
    country: Optional[CountryEnum] = None
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
    country: Optional[CountryEnum] = None
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
    preferred_language: Optional[str] = Field(None, max_length=5, description="Preferred language code (en, el, ar, es)")
    preferred_country: Optional[str] = Field(None, max_length=3, description="Preferred country code (GR, KSA, ES, CY, OM)")
    localization_preferences: Optional[str] = Field(None, description="JSON string for advanced localization preferences")
    
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
    preferred_language: Optional[str] = None
    preferred_country: Optional[str] = None
    localization_preferences: Optional[str] = None
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
class MachineStatusEnum(str, Enum):
    active = "active"
    inactive = "inactive"
    maintenance = "maintenance"
    decommissioned = "decommissioned"

class MachineBase(BaseModel):
    customer_organization_id: uuid.UUID
    model_type: str = Field(..., max_length=100) # e.g., 'V3.1B', 'V4.0'
    name: str = Field(..., max_length=255)
    serial_number: str = Field(..., max_length=255)
    purchase_date: Optional[datetime] = None
    warranty_expiry_date: Optional[datetime] = None
    status: MachineStatusEnum = MachineStatusEnum.active
    last_maintenance_date: Optional[datetime] = None
    next_maintenance_date: Optional[datetime] = None
    location: Optional[str] = Field(None, max_length=255)
    notes: Optional[str] = None

class MachineCreate(MachineBase):
    pass

class MachineUpdate(BaseModel):
    customer_organization_id: Optional[uuid.UUID] = None
    model_type: Optional[str] = Field(None, max_length=100)
    name: Optional[str] = Field(None, max_length=255)
    serial_number: Optional[str] = Field(None, max_length=255)
    purchase_date: Optional[datetime] = None
    warranty_expiry_date: Optional[datetime] = None
    status: Optional[MachineStatusEnum] = None
    last_maintenance_date: Optional[datetime] = None
    next_maintenance_date: Optional[datetime] = None
    location: Optional[str] = Field(None, max_length=255)
    notes: Optional[str] = None

class MachineResponse(MachineBase, BaseSchema):
    customer_organization_name: Optional[str] = None
    latest_hours: Optional[float] = None
    latest_hours_date: Optional[datetime] = None
    days_since_last_hours_record: Optional[int] = None
    total_hours_records: Optional[int] = None


# --- Machine Transfer Schemas ---
class MachineTransferRequest(BaseModel):
    machine_id: uuid.UUID
    new_customer_organization_id: uuid.UUID
    transfer_reason: Optional[str] = None
    notes: Optional[str] = None


# --- Maintenance Schemas ---
class MaintenanceTypeEnum(str, Enum):
    scheduled = "scheduled"
    unscheduled = "unscheduled"
    repair = "repair"
    inspection = "inspection"
    cleaning = "cleaning"
    calibration = "calibration"
    other = "other"

class MaintenanceBase(BaseModel):
    machine_id: uuid.UUID
    maintenance_date: datetime
    maintenance_type: MaintenanceTypeEnum
    performed_by_user_id: uuid.UUID
    description: str
    hours_spent: Optional[Decimal] = Field(None, decimal_places=2)
    cost: Optional[Decimal] = Field(None, decimal_places=2)
    next_maintenance_date: Optional[datetime] = None
    notes: Optional[str] = None

class MaintenanceCreate(MaintenanceBase):
    pass

class MaintenanceUpdate(BaseModel):
    machine_id: Optional[uuid.UUID] = None
    maintenance_date: Optional[datetime] = None
    maintenance_type: Optional[MaintenanceTypeEnum] = None
    performed_by_user_id: Optional[uuid.UUID] = None
    description: Optional[str] = None
    hours_spent: Optional[Decimal] = Field(None, decimal_places=2)
    cost: Optional[Decimal] = Field(None, decimal_places=2)
    next_maintenance_date: Optional[datetime] = None
    notes: Optional[str] = None

class MaintenanceResponse(MaintenanceBase, BaseSchema):
    class Config:
        from_attributes = True


# --- Maintenance Part Usage Schemas ---
class MaintenancePartUsageBase(BaseModel):
    maintenance_id: uuid.UUID
    part_id: uuid.UUID
    quantity_used: Decimal = Field(default=1, decimal_places=3)
    unit_cost: Optional[Decimal] = Field(None, decimal_places=2)
    notes: Optional[str] = None

class MaintenancePartUsageCreate(MaintenancePartUsageBase):
    pass

class MaintenancePartUsageUpdate(BaseModel):
    maintenance_id: Optional[uuid.UUID] = None
    part_id: Optional[uuid.UUID] = None
    quantity_used: Optional[Decimal] = Field(None, decimal_places=3)
    unit_cost: Optional[Decimal] = Field(None, decimal_places=2)
    notes: Optional[str] = None

class MaintenancePartUsageResponse(MaintenancePartUsageBase, BaseSchema):
    part: Optional['PartResponse'] = None
    
    class Config:
        from_attributes = True


# --- Machine Part Compatibility Schemas ---
class MachinePartCompatibilityBase(BaseModel):
    machine_id: uuid.UUID
    part_id: uuid.UUID
    is_compatible: bool = True
    compatibility_notes: Optional[str] = None

class MachinePartCompatibilityCreate(MachinePartCompatibilityBase):
    pass

class MachinePartCompatibilityUpdate(BaseModel):
    machine_id: Optional[uuid.UUID] = None
    part_id: Optional[uuid.UUID] = None
    is_compatible: Optional[bool] = None
    compatibility_notes: Optional[str] = None

class MachinePartCompatibilityResponse(MachinePartCompatibilityBase, BaseSchema):
    part: Optional['PartResponse'] = None
    
    class Config:
        from_attributes = True


# --- Part Schemas ---
class PartTypeEnum(str, Enum):
    CONSUMABLE = "consumable"
    BULK_MATERIAL = "bulk_material"

class PartBase(BaseModel):
    part_number: str = Field(..., max_length=255)
    name: str = Field(..., min_length=1, description="Multilingual part name (supports compound strings)")
    description: Optional[str] = None
    part_type: PartTypeEnum = PartTypeEnum.CONSUMABLE
    is_proprietary: bool = False
    unit_of_measure: str = Field(default="pieces", max_length=50)
    # manufacturer: Optional[str] = Field(None, max_length=255, description="Part manufacturer name")  # Temporarily commented out
    # part_code: Optional[str] = Field(None, max_length=100, description="AutoBoss-specific part code")  # Temporarily commented out
    # serial_number: Optional[str] = Field(None, max_length=255, description="Part serial number if available")  # Temporarily commented out
    manufacturer_part_number: Optional[str] = Field(None, max_length=255)
    manufacturer_delivery_time_days: Optional[int] = None
    local_supplier_delivery_time_days: Optional[int] = None
    image_urls: Optional[List[str]] = Field(None, max_items=4, description="Up to 4 image URLs")
    
    # Validators temporarily removed to test field definitions
    
    class Config:
        extra = "ignore"  # Ignore extra fields not defined in the schema

class PartCreate(PartBase):
    pass

class PartUpdate(BaseModel):
    part_number: Optional[str] = Field(None, max_length=255)
    name: Optional[str] = Field(None, min_length=1, description="Multilingual part name (supports compound strings)")
    description: Optional[str] = None
    part_type: Optional[PartTypeEnum] = None
    is_proprietary: Optional[bool] = None
    unit_of_measure: Optional[str] = Field(None, max_length=50)
    manufacturer: Optional[str] = Field(None, max_length=255, description="Part manufacturer name")
    part_code: Optional[str] = Field(None, max_length=100, description="AutoBoss-specific part code")
    serial_number: Optional[str] = Field(None, max_length=255, description="Part serial number if available")
    manufacturer_part_number: Optional[str] = Field(None, max_length=255)
    manufacturer_delivery_time_days: Optional[int] = None
    local_supplier_delivery_time_days: Optional[int] = None
    image_urls: Optional[List[str]] = Field(None, max_items=4, description="Up to 4 image URLs")
    
    # Validators temporarily removed to test field definitions

class PartResponse(PartBase, BaseSchema):
    pass

# --- Enhanced Part Response Schemas ---
class WarehouseInventoryItem(BaseModel):
    """Individual warehouse inventory item for parts"""
    warehouse_id: uuid.UUID
    warehouse_name: str
    current_stock: Decimal
    minimum_stock_recommendation: Decimal
    is_low_stock: bool
    unit_of_measure: str

class PartWithInventoryResponse(BaseModel):
    """Part response with inventory information across warehouses"""
    id: uuid.UUID
    part_number: str
    name: str
    description: Optional[str] = None
    part_type: PartTypeEnum
    is_proprietary: bool
    unit_of_measure: str
    manufacturer: Optional[str] = None
    part_code: Optional[str] = None
    serial_number: Optional[str] = None
    manufacturer_part_number: Optional[str] = None
    manufacturer_delivery_time_days: Optional[int] = None
    local_supplier_delivery_time_days: Optional[int] = None
    image_urls: Optional[List[str]] = None
    created_at: datetime
    updated_at: datetime
    total_stock: Decimal
    warehouse_inventory: List[WarehouseInventoryItem]
    is_low_stock: bool
    
    class Config:
        from_attributes = True

class PartUsageHistoryItem(BaseModel):
    """Individual part usage history item"""
    usage_date: datetime
    quantity: Decimal
    machine_id: Optional[uuid.UUID] = None
    machine_serial: Optional[str] = None
    warehouse_id: uuid.UUID
    warehouse_name: str

class PartWithUsageResponse(PartWithInventoryResponse):
    """Part response with inventory and usage history"""
    usage_history: List[PartUsageHistoryItem]
    avg_monthly_usage: Decimal
    estimated_depletion_days: Optional[int] = None

class PartReorderSuggestion(BaseModel):
    """Part reorder suggestion based on usage patterns"""
    part_id: uuid.UUID
    part_number: str
    part_name: str
    current_total_stock: Decimal
    avg_monthly_usage: Decimal
    estimated_depletion_days: int
    suggested_reorder_quantity: Decimal
    unit_of_measure: str
    is_proprietary: bool

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
    shipped_date: Optional[datetime] = None
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
    shipped_date: Optional[datetime] = None
    actual_delivery_date: Optional[datetime] = None
    status: Optional[str] = Field(None, max_length=50)
    ordered_by_user_id: Optional[uuid.UUID] = None
    notes: Optional[str] = None
    receiving_warehouse_id: Optional[uuid.UUID] = None

class CustomerOrderResponse(CustomerOrderBase, BaseSchema):
    items: List['CustomerOrderItemResponse'] = []
    customer_organization: Optional[OrganizationResponse] = None

# --- Customer Order Action Schemas ---
class CustomerOrderShipRequest(BaseModel):
    """Request schema for marking an order as shipped (Oraseas EE action)"""
    shipped_date: datetime = Field(default_factory=datetime.now)
    tracking_number: Optional[str] = Field(None, max_length=255)
    notes: Optional[str] = None

class CustomerOrderConfirmReceiptRequest(BaseModel):
    """Request schema for confirming order receipt (Customer action)"""
    actual_delivery_date: datetime = Field(default_factory=datetime.now)
    receiving_warehouse_id: uuid.UUID
    notes: Optional[str] = None

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
    performed_by_user_id: uuid.UUID # Will be set from current_user in the router
    quantity_change: Decimal = Field(..., decimal_places=3)  # Frontend expects quantity_change
    reason: str # Frontend expects reason (not reason_code)
    notes: Optional[str] = None

class StockAdjustmentCreate(BaseModel): # Separate from Base to not include user_id from request body
    # inventory_id will come from path parameter
    quantity_change: Decimal = Field(..., decimal_places=3)  # Frontend expects quantity_change
    reason: str # Frontend expects reason (not reason_code)
    notes: Optional[str] = None

class WarehouseStockAdjustmentCreate(BaseModel):
    """Schema for creating stock adjustments via warehouse endpoint"""
    part_id: uuid.UUID
    quantity_change: Decimal = Field(..., decimal_places=3)
    reason: str
    notes: Optional[str] = None

class StockAdjustmentResponse(BaseSchema):
    id: uuid.UUID
    inventory_id: uuid.UUID
    part_id: Optional[uuid.UUID] = None
    part_number: Optional[str] = None
    part_name: Optional[str] = None
    quantity_change: Decimal
    unit_of_measure: Optional[str] = None
    reason: str
    notes: Optional[str] = None
    performed_by_user_id: uuid.UUID
    performed_by_user_name: Optional[str] = None
    created_at: datetime
    updated_at: datetime


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


# --- Warehouse Analytics Schemas ---
class WarehouseAnalyticsRequest(BaseModel):
    """Request schema for warehouse analytics with validation"""
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    days: int = Field(default=30, ge=1, le=365, description="Number of days to include (1-365)")
    
    @validator('days')
    def validate_days(cls, v):
        if v < 1 or v > 365:
            raise ValueError('Days must be between 1 and 365')
        return v
    
    @validator('end_date')
    def validate_end_date(cls, v, values):
        if v and 'start_date' in values and values['start_date']:
            if v < values['start_date']:
                raise ValueError('End date must be after start date')
        return v

class WarehouseAnalyticsResponse(BaseModel):
    """Response schema for warehouse analytics"""
    warehouse_id: uuid.UUID
    warehouse_name: str
    analytics_period: dict
    inventory_summary: dict
    top_parts_by_value: List[dict]
    stock_movements: dict
    turnover_metrics: dict
    
    class Config:
        from_attributes = True

class WarehouseAnalyticsTrendsRequest(BaseModel):
    """Request schema for warehouse analytics trends with validation"""
    period: str = Field(default="daily", pattern="^(daily|weekly|monthly)$", description="Aggregation period")
    days: int = Field(default=30, ge=1, le=365, description="Number of days to include (1-365)")
    
    @validator('period')
    def validate_period(cls, v):
        valid_periods = ["daily", "weekly", "monthly"]
        if v not in valid_periods:
            raise ValueError(f'Period must be one of: {", ".join(valid_periods)}')
        return v
    
    @validator('days')
    def validate_days(cls, v):
        if v < 1 or v > 365:
            raise ValueError('Days must be between 1 and 365')
        return v

class WarehouseAnalyticsTrendsResponse(BaseModel):
    """Response schema for warehouse analytics trends"""
    warehouse_id: uuid.UUID
    period: str
    date_range: dict
    trends: List[dict]
    
    class Config:
        from_attributes = True

# --- Machine Hours Schemas ---
class MachineHoursBase(BaseModel):
    machine_id: uuid.UUID
    hours_value: Decimal = Field(..., decimal_places=2, description="Machine hours value")
    recorded_date: datetime = Field(default_factory=datetime.now)
    notes: Optional[str] = None

class MachineHoursCreate(BaseModel):
    hours_value: Decimal = Field(..., decimal_places=2, gt=0, description="Machine hours value (must be positive)")
    recorded_date: Optional[datetime] = Field(default_factory=datetime.now)
    notes: Optional[str] = None

class MachineHoursUpdate(BaseModel):
    hours_value: Optional[Decimal] = Field(None, decimal_places=2, gt=0)
    recorded_date: Optional[datetime] = None
    notes: Optional[str] = None

class MachineHoursResponse(MachineHoursBase, BaseSchema):
    recorded_by_user_id: uuid.UUID
    
    # Include related data for easier display
    recorded_by_username: Optional[str] = None
    machine_name: Optional[str] = None
    machine_serial_number: Optional[str] = None

    class Config:
        from_attributes = True

# --- Machine Name Update Schema ---
class MachineNameUpdateRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=255, description="New machine name")

# --- Machine Model Type Validation Schema ---
class MachineModelTypeEnum(str, Enum):
    V3_1B = "V3.1B"
    V4_0 = "V4.0"

# --- Error Response Schemas ---
class ValidationErrorDetail(BaseModel):
    """Individual validation error detail"""
    field: str
    message: str
    invalid_value: Optional[str] = None

class ErrorResponse(BaseModel):
    """Standardized error response schema"""
    error: str
    message: str
    details: Optional[List[ValidationErrorDetail]] = None
    timestamp: datetime = Field(default_factory=datetime.now)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }

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


# --- Stocktake Schemas ---
class StocktakeStatusEnum(str, Enum):
    planned = "planned"
    in_progress = "in_progress"
    completed = "completed"
    cancelled = "cancelled"

class StocktakeBase(BaseModel):
    warehouse_id: uuid.UUID
    scheduled_date: datetime
    notes: Optional[str] = None

class StocktakeCreate(StocktakeBase):
    scheduled_by_user_id: Optional[uuid.UUID] = None  # Will be set to current user if not provided

class StocktakeUpdate(BaseModel):
    scheduled_date: Optional[datetime] = None
    status: Optional[StocktakeStatusEnum] = None
    notes: Optional[str] = None
    completed_date: Optional[datetime] = None
    completed_by_user_id: Optional[uuid.UUID] = None

class StocktakeResponse(StocktakeBase):
    id: uuid.UUID
    status: StocktakeStatusEnum
    scheduled_by_user_id: uuid.UUID
    completed_date: Optional[datetime] = None
    completed_by_user_id: Optional[uuid.UUID] = None
    created_at: datetime
    updated_at: datetime
    
    # Additional computed fields
    warehouse_name: Optional[str] = None
    organization_id: Optional[uuid.UUID] = None
    organization_name: Optional[str] = None
    scheduled_by_username: Optional[str] = None
    completed_by_username: Optional[str] = None
    total_items: Optional[int] = None
    items_counted: Optional[int] = None
    discrepancy_count: Optional[int] = None
    total_discrepancy_value: Optional[Decimal] = None
    items: Optional[List[dict]] = None

    class Config:
        from_attributes = True

# --- Stocktake Item Schemas ---
class StocktakeItemBase(BaseModel):
    expected_quantity: Decimal
    actual_quantity: Optional[Decimal] = None
    notes: Optional[str] = None

class StocktakeItemUpdate(BaseModel):
    actual_quantity: Optional[Decimal] = None
    notes: Optional[str] = None

class StocktakeItemResponse(StocktakeItemBase):
    id: uuid.UUID
    stocktake_id: uuid.UUID
    part_id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    
    # Additional computed fields
    part_number: Optional[str] = None
    part_name: Optional[str] = None
    part_type: Optional[str] = None
    unit_of_measure: Optional[str] = None
    discrepancy: Optional[Decimal] = None
    discrepancy_percentage: Optional[Decimal] = None
    discrepancy_value: Optional[Decimal] = None

    class Config:
        from_attributes = True

class BatchStocktakeItemUpdate(BaseModel):
    items: List[dict]  # List of {item_id: uuid, actual_quantity: Decimal, notes: Optional[str]}

# --- Inventory Alert Schemas ---
class InventoryAlertCreate(BaseModel):
    warehouse_id: uuid.UUID
    part_id: uuid.UUID
    alert_type: str
    severity: str
    message: str
    threshold_value: Optional[Decimal] = None

class InventoryAlertUpdate(BaseModel):
    severity: Optional[str] = None
    message: Optional[str] = None
    threshold_value: Optional[Decimal] = None
    is_active: Optional[bool] = None

class InventoryAlertResponse(BaseModel):
    id: uuid.UUID
    warehouse_id: uuid.UUID
    part_id: uuid.UUID
    alert_type: str
    severity: str
    message: str
    threshold_value: Optional[Decimal] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    # Additional computed fields
    warehouse_name: Optional[str] = None
    part_number: Optional[str] = None
    part_name: Optional[str] = None
    current_stock: Optional[Decimal] = None

    class Config:
        from_attributes = True

# --- Inventory Adjustment Schemas ---
class InventoryAdjustmentCreate(BaseModel):
    warehouse_id: uuid.UUID
    part_id: uuid.UUID
    quantity_adjusted: Decimal
    reason_code: str
    notes: Optional[str] = None
    stocktake_id: Optional[uuid.UUID] = None

class InventoryAdjustmentResponse(BaseModel):
    id: uuid.UUID
    inventory_id: uuid.UUID
    warehouse_id: uuid.UUID
    part_id: uuid.UUID
    quantity_adjusted: Decimal
    reason_code: str
    notes: Optional[str] = None
    stocktake_id: Optional[uuid.UUID] = None
    adjusted_by_user_id: uuid.UUID
    adjustment_date: datetime
    created_at: datetime
    updated_at: datetime
    
    # Additional computed fields
    warehouse_name: Optional[str] = None
    part_number: Optional[str] = None
    part_name: Optional[str] = None
    adjusted_by_username: Optional[str] = None
    previous_stock: Optional[Decimal] = None
    new_stock: Optional[Decimal] = None

    class Config:
        from_attributes = True

class BatchInventoryAdjustment(BaseModel):
    warehouse_id: uuid.UUID
    adjustments: List[dict]  # List of {part_id: uuid, quantity_adjusted: Decimal, reason_code: str, notes: Optional[str]}
    stocktake_id: Optional[uuid.UUID] = None

# --- Inventory Analytics Schemas ---
class InventoryAnalyticsRequest(BaseModel):
    organization_id: Optional[uuid.UUID] = None
    warehouse_id: Optional[uuid.UUID] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    include_trends: bool = True
    include_alerts: bool = True

class InventoryAnalytics(BaseModel):
    organization_id: Optional[uuid.UUID] = None
    warehouse_id: Optional[uuid.UUID] = None
    analysis_period: dict
    inventory_summary: dict
    stock_movements: dict
    alerts_summary: dict
    trends: Optional[dict] = None
    recommendations: List[dict] = []

    class Config:
        from_attributes = True