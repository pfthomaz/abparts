# backend/app/schemas_config.py

import uuid
from datetime import datetime
from typing import List, Optional, Any, Dict
from pydantic import BaseModel, Field, validator
from enum import Enum


class ConfigurationCategoryEnum(str, Enum):
    ORGANIZATION = "organization"
    PARTS = "parts"
    USER_MANAGEMENT = "user_management"
    LOCALIZATION = "localization"
    SYSTEM = "system"


class ConfigurationDataTypeEnum(str, Enum):
    STRING = "string"
    INTEGER = "integer"
    BOOLEAN = "boolean"
    JSON = "json"
    ENUM = "enum"


class SystemConfigurationBase(BaseModel):
    category: ConfigurationCategoryEnum
    key: str = Field(..., max_length=255)
    value: Optional[str] = None
    data_type: ConfigurationDataTypeEnum
    description: Optional[str] = None
    is_system_managed: bool = False
    is_user_configurable: bool = True
    requires_restart: bool = False
    validation_rules: Optional[Dict[str, Any]] = None
    default_value: Optional[str] = None


class SystemConfigurationCreate(SystemConfigurationBase):
    pass


class SystemConfigurationUpdate(BaseModel):
    category: Optional[ConfigurationCategoryEnum] = None
    key: Optional[str] = Field(None, max_length=255)
    value: Optional[str] = None
    data_type: Optional[ConfigurationDataTypeEnum] = None
    description: Optional[str] = None
    is_system_managed: Optional[bool] = None
    is_user_configurable: Optional[bool] = None
    requires_restart: Optional[bool] = None
    validation_rules: Optional[Dict[str, Any]] = None
    default_value: Optional[str] = None


class SystemConfigurationResponse(SystemConfigurationBase):
    id: uuid.UUID
    created_by_user_id: Optional[uuid.UUID] = None
    updated_by_user_id: Optional[uuid.UUID] = None
    created_at: datetime
    updated_at: datetime
    typed_value: Optional[Any] = None  # The value in its proper data type

    class Config:
        from_attributes = True


class OrganizationConfigurationBase(BaseModel):
    organization_id: uuid.UUID
    configuration_key: str = Field(..., max_length=255)
    value: Optional[str] = None
    is_active: bool = True


class OrganizationConfigurationCreate(OrganizationConfigurationBase):
    pass


class OrganizationConfigurationUpdate(BaseModel):
    configuration_key: Optional[str] = Field(None, max_length=255)
    value: Optional[str] = None
    is_active: Optional[bool] = None


class OrganizationConfigurationResponse(OrganizationConfigurationBase):
    id: uuid.UUID
    created_by_user_id: Optional[uuid.UUID] = None
    updated_by_user_id: Optional[uuid.UUID] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ConfigurationValidationRequest(BaseModel):
    """Request schema for validating configuration values"""
    key: str
    value: Any
    organization_id: Optional[uuid.UUID] = None


class ConfigurationValidationResponse(BaseModel):
    """Response schema for configuration validation"""
    is_valid: bool
    error_message: Optional[str] = None


class ConfigurationCategoryResponse(BaseModel):
    """Response schema for configuration by category"""
    category: ConfigurationCategoryEnum
    configurations: List[SystemConfigurationResponse]
    count: int


class ConfigurationBulkUpdateRequest(BaseModel):
    """Request schema for bulk configuration updates"""
    configurations: List[Dict[str, Any]]
    organization_id: Optional[uuid.UUID] = None


class ConfigurationBulkUpdateResponse(BaseModel):
    """Response schema for bulk configuration updates"""
    updated_count: int
    failed_updates: List[Dict[str, str]] = []
    success: bool


class ConfigurationExportResponse(BaseModel):
    """Response schema for configuration export"""
    configurations: List[SystemConfigurationResponse]
    organization_configurations: List[OrganizationConfigurationResponse] = []
    export_timestamp: datetime
    total_count: int


class ConfigurationImportRequest(BaseModel):
    """Request schema for configuration import"""
    configurations: List[Dict[str, Any]]
    organization_id: Optional[uuid.UUID] = None
    overwrite_existing: bool = False


class ConfigurationImportResponse(BaseModel):
    """Response schema for configuration import"""
    imported_count: int
    skipped_count: int
    failed_imports: List[Dict[str, str]] = []
    success: bool


# Predefined configuration templates
class OrganizationManagementConfig(BaseModel):
    """Configuration template for organization management settings"""
    default_country: Optional[str] = "GR"
    auto_create_warehouse: bool = True
    supplier_approval_required: bool = False
    max_suppliers_per_organization: int = 50
    organization_deactivation_policy: str = "soft_delete"


class PartsManagementConfig(BaseModel):
    """Configuration template for parts management settings"""
    multilingual_name_format: str = "compound"
    max_photos_per_part: int = 4
    photo_max_size_mb: int = 5
    supported_photo_formats: List[str] = ["jpg", "jpeg", "png", "webp"]
    part_categorization_required: bool = True
    inventory_threshold_default: float = 10.0


class UserManagementConfig(BaseModel):
    """Configuration template for user management settings"""
    password_min_length: int = 8
    password_require_uppercase: bool = True
    password_require_lowercase: bool = True
    password_require_numbers: bool = True
    password_require_symbols: bool = False
    session_timeout_minutes: int = 480  # 8 hours
    max_failed_login_attempts: int = 5
    account_lockout_duration_minutes: int = 30
    invitation_expiry_days: int = 7


class LocalizationConfig(BaseModel):
    """Configuration template for localization settings"""
    supported_languages: List[str] = ["en", "el", "ar", "es"]
    supported_countries: List[str] = ["GR", "UK", "NO", "CA", "NZ", "TR", "OM", "ES", "CY", "SA"]
    default_language: str = "en"
    default_country: str = "GR"
    rtl_languages: List[str] = ["ar"]
    date_format_by_country: Dict[str, str] = {
        "GR": "DD/MM/YYYY",
        "UK": "DD/MM/YYYY",
        "NO": "DD/MM/YYYY",
        "CA": "MM/DD/YYYY",
        "NZ": "DD/MM/YYYY",
        "TR": "DD/MM/YYYY",
        "OM": "DD/MM/YYYY",
        "ES": "DD/MM/YYYY",
        "CY": "DD/MM/YYYY",
        "SA": "DD/MM/YYYY"
    }
    currency_by_country: Dict[str, str] = {
        "GR": "EUR",
        "UK": "GBP",
        "NO": "NOK",
        "CA": "CAD",
        "NZ": "NZD",
        "TR": "TRY",
        "OM": "OMR",
        "ES": "EUR",
        "CY": "EUR",
        "SA": "SAR"
    }


class ConfigurationTemplateResponse(BaseModel):
    """Response schema for configuration templates"""
    organization_management: OrganizationManagementConfig
    parts_management: PartsManagementConfig
    user_management: UserManagementConfig
    localization: LocalizationConfig