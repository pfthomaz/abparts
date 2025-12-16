# backend/app/schemas/organization.py

import uuid
from datetime import datetime
from typing import Optional, List
from enum import Enum
from pydantic import BaseModel, Field

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
    KSA = "KSA"  # Saudi Arabia

class OrganizationBase(BaseModel):
    name: str = Field(..., max_length=255)
    organization_type: OrganizationTypeEnum
    parent_organization_id: Optional[uuid.UUID] = None
    country: Optional[CountryEnum] = None
    address: Optional[str] = None
    contact_info: Optional[str] = None
    logo_url: Optional[str] = None
    is_active: bool = True

class OrganizationCreate(OrganizationBase):
    pass

class OrganizationUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=255)
    organization_type: Optional[OrganizationTypeEnum] = None
    parent_organization_id: Optional[uuid.UUID] = None
    country: Optional[CountryEnum] = None
    address: Optional[str] = None
    contact_info: Optional[str] = None
    logo_url: Optional[str] = None
    is_active: Optional[bool] = None

class OrganizationResponse(OrganizationBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    logo_data_url: Optional[str] = None  # Data URL for logo display

    class Config:
        from_attributes = True

class OrganizationTypeFilterResponse(BaseModel):
    organization_type: OrganizationTypeEnum
    display_name: str
    description: Optional[str] = None
    count: Optional[int] = None

    class Config:
        from_attributes = True

class OrganizationHierarchyResponse(BaseModel):
    id: uuid.UUID
    name: str
    organization_type: OrganizationTypeEnum
    parent_organization_id: Optional[uuid.UUID] = None
    children: List['OrganizationHierarchyResponse'] = []
    user_count: Optional[int] = None
    warehouse_count: Optional[int] = None
    is_active: bool
    logo_data_url: Optional[str] = None  # Data URL for logo display

    class Config:
        from_attributes = True

class OrganizationValidationRequest(BaseModel):
    """Schema for organization validation requests"""
    name: str
    organization_type: OrganizationTypeEnum
    parent_organization_id: Optional[uuid.UUID] = None
    address: Optional[str] = None
    contact_info: Optional[str] = None
    is_active: bool = True
    id: Optional[uuid.UUID] = None  # For update validation

class ValidationError(BaseModel):
    """Schema for individual validation errors"""
    field: str
    message: str

class OrganizationValidationResponse(BaseModel):
    """Schema for organization validation responses"""
    valid: bool
    errors: List[ValidationError] = []

class OrganizationHierarchyNode(BaseModel):
    """Response schema for organization hierarchy tree structure with complete organization data"""
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
    logo_data_url: Optional[str] = None  # Data URL for logo display
    
    class Config:
        from_attributes = True

# Enable forward references for self-referencing models
OrganizationHierarchyResponse.model_rebuild()
OrganizationHierarchyNode.model_rebuild()