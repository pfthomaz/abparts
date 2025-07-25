# backend/app/schemas/organization.py

import uuid
from datetime import datetime
from typing import Optional, List
from enum import Enum
from pydantic import BaseModel

class OrganizationTypeEnum(str, Enum):
    oraseas_ee = "oraseas_ee"
    bossaqua = "bossaqua"
    customer = "customer"
    supplier = "supplier"

class OrganizationBase(BaseModel):
    name: str
    organization_type: OrganizationTypeEnum
    parent_organization_id: Optional[uuid.UUID] = None
    address: Optional[str] = None
    contact_info: Optional[str] = None
    is_active: bool = True

class OrganizationCreate(OrganizationBase):
    pass

class OrganizationUpdate(BaseModel):
    name: Optional[str] = None
    organization_type: Optional[OrganizationTypeEnum] = None
    parent_organization_id: Optional[uuid.UUID] = None
    address: Optional[str] = None
    contact_info: Optional[str] = None
    is_active: Optional[bool] = None

class OrganizationResponse(OrganizationBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class OrganizationTypeFilterResponse(BaseModel):
    organization_type: OrganizationTypeEnum
    display_name: str
    description: Optional[str] = None
    count: Optional[int] = None

    class Config:
        orm_mode = True

class OrganizationHierarchyResponse(BaseModel):
    id: uuid.UUID
    name: str
    organization_type: OrganizationTypeEnum
    parent_organization_id: Optional[uuid.UUID] = None
    children: List['OrganizationHierarchyResponse'] = []
    user_count: Optional[int] = None
    warehouse_count: Optional[int] = None
    is_active: bool

    class Config:
        orm_mode = True

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
    
    class Config:
        from_attributes = True

# Enable forward references for self-referencing models
OrganizationHierarchyResponse.model_rebuild()
OrganizationHierarchyNode.model_rebuild()