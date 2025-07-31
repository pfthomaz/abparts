# backend/app/routers/configuration.py

import logging
import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from ..database import get_db
from ..auth import get_current_user
from ..models import User, Organization
from ..models_config import SystemConfiguration, OrganizationConfiguration, ConfigurationCategory, ConfigurationDataType
from ..schemas_config import (
    SystemConfigurationCreate, SystemConfigurationUpdate, SystemConfigurationResponse,
    OrganizationConfigurationCreate, OrganizationConfigurationUpdate, OrganizationConfigurationResponse,
    ConfigurationValidationRequest, ConfigurationValidationResponse,
    ConfigurationCategoryResponse, ConfigurationBulkUpdateRequest, ConfigurationBulkUpdateResponse,
    ConfigurationExportResponse, ConfigurationImportRequest, ConfigurationImportResponse,
    ConfigurationTemplateResponse, OrganizationManagementConfig, PartsManagementConfig,
    UserManagementConfig, LocalizationConfig, ConfigurationCategoryEnum
)

# Set up logging
logger = logging.getLogger(__name__)

router = APIRouter()


def get_user_role(user: User) -> str:
    """Get user role as string, handling both enum and string values."""
    return user.role.value if hasattr(user.role, 'value') else user.role


def check_admin_access(user: User):
    """Check if user has admin or superadmin access."""
    role = get_user_role(user)
    if role not in ["admin", "super_admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Admin privileges required."
        )


def check_superadmin_access(user: User):
    """Check if user has superadmin access."""
    role = get_user_role(user)
    if role != "super_admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Superadmin privileges required."
        )


# --- System Configuration Endpoints ---

@router.get("/system", response_model=List[SystemConfigurationResponse])
async def get_system_configurations(
    category: Optional[ConfigurationCategoryEnum] = None,
    user_configurable_only: bool = Query(False, description="Only return user-configurable settings"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get system configuration settings.
    
    Superadmins can see all configurations.
    Admins can only see user-configurable settings.
    """
    check_admin_access(current_user)
    
    query = db.query(SystemConfiguration)
    
    # Filter by category if specified
    if category:
        query = query.filter(SystemConfiguration.category == category)
    
    # Filter by user-configurable if requested or if user is not superadmin
    if user_configurable_only or get_user_role(current_user) != "super_admin":
        query = query.filter(SystemConfiguration.is_user_configurable == True)
    
    # Apply pagination
    configurations = query.offset(skip).limit(limit).all()
    
    # Convert to response format with typed values
    response_configs = []
    for config in configurations:
        config_dict = {
            "id": config.id,
            "category": config.category,
            "key": config.key,
            "value": config.value,
            "data_type": config.data_type,
            "description": config.description,
            "is_system_managed": config.is_system_managed,
            "is_user_configurable": config.is_user_configurable,
            "requires_restart": config.requires_restart,
            "validation_rules": config.validation_rules,
            "default_value": config.default_value,
            "created_by_user_id": config.created_by_user_id,
            "updated_by_user_id": config.updated_by_user_id,
            "created_at": config.created_at,
            "updated_at": config.updated_at,
            "typed_value": config.get_typed_value()
        }
        response_configs.append(SystemConfigurationResponse(**config_dict))
    
    return response_configs


@router.get("/system/categories", response_model=List[ConfigurationCategoryResponse])
async def get_configurations_by_category(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get system configurations grouped by category."""
    check_admin_access(current_user)
    
    categories = []
    
    for category in ConfigurationCategory:
        query = db.query(SystemConfiguration).filter(SystemConfiguration.category == category)
        
        # Filter by user-configurable if user is not superadmin
        if get_user_role(current_user) != "super_admin":
            query = query.filter(SystemConfiguration.is_user_configurable == True)
        
        configurations = query.all()
        
        # Convert to response format
        response_configs = []
        for config in configurations:
            config_dict = {
                "id": config.id,
                "category": config.category,
                "key": config.key,
                "value": config.value,
                "data_type": config.data_type,
                "description": config.description,
                "is_system_managed": config.is_system_managed,
                "is_user_configurable": config.is_user_configurable,
                "requires_restart": config.requires_restart,
                "validation_rules": config.validation_rules,
                "default_value": config.default_value,
                "created_by_user_id": config.created_by_user_id,
                "updated_by_user_id": config.updated_by_user_id,
                "created_at": config.created_at,
                "updated_at": config.updated_at,
                "typed_value": config.get_typed_value()
            }
            response_configs.append(SystemConfigurationResponse(**config_dict))
        
        categories.append(ConfigurationCategoryResponse(
            category=category,
            configurations=response_configs,
            count=len(response_configs)
        ))
    
    return categories


@router.post("/system", response_model=SystemConfigurationResponse)
async def create_system_configuration(
    configuration: SystemConfigurationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new system configuration setting. Only superadmins can create system configurations."""
    check_superadmin_access(current_user)
    
    # Check if configuration key already exists
    existing_config = db.query(SystemConfiguration).filter(
        SystemConfiguration.key == configuration.key
    ).first()
    
    if existing_config:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Configuration with key '{configuration.key}' already exists"
        )
    
    # Create new configuration
    db_config = SystemConfiguration(
        category=configuration.category,
        key=configuration.key,
        value=configuration.value,
        data_type=configuration.data_type,
        description=configuration.description,
        is_system_managed=configuration.is_system_managed,
        is_user_configurable=configuration.is_user_configurable,
        requires_restart=configuration.requires_restart,
        validation_rules=configuration.validation_rules,
        default_value=configuration.default_value,
        created_by_user_id=current_user.user_id,
        updated_by_user_id=current_user.user_id
    )
    
    # Validate the value if validation rules exist
    if configuration.validation_rules and configuration.value:
        is_valid, error_message = db_config.validate_value(configuration.value)
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid configuration value: {error_message}"
            )
    
    db.add(db_config)
    db.commit()
    db.refresh(db_config)
    
    logger.info(f"System configuration '{configuration.key}' created by user {current_user.username}")
    
    # Return response with typed value
    config_dict = {
        "id": db_config.id,
        "category": db_config.category,
        "key": db_config.key,
        "value": db_config.value,
        "data_type": db_config.data_type,
        "description": db_config.description,
        "is_system_managed": db_config.is_system_managed,
        "is_user_configurable": db_config.is_user_configurable,
        "requires_restart": db_config.requires_restart,
        "validation_rules": db_config.validation_rules,
        "default_value": db_config.default_value,
        "created_by_user_id": db_config.created_by_user_id,
        "updated_by_user_id": db_config.updated_by_user_id,
        "created_at": db_config.created_at,
        "updated_at": db_config.updated_at,
        "typed_value": db_config.get_typed_value()
    }
    
    return SystemConfigurationResponse(**config_dict)


@router.put("/system/{config_id}", response_model=SystemConfigurationResponse)
async def update_system_configuration(
    config_id: uuid.UUID,
    configuration: SystemConfigurationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a system configuration setting."""
    check_admin_access(current_user)
    
    # Get existing configuration
    db_config = db.query(SystemConfiguration).filter(SystemConfiguration.id == config_id).first()
    if not db_config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Configuration not found"
        )
    
    # Check permissions
    if get_user_role(current_user) != "super_admin":
        if not db_config.is_user_configurable:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to modify this configuration"
            )
        
        # Admins can only update the value, not other properties
        if any([
            configuration.category is not None,
            configuration.key is not None,
            configuration.data_type is not None,
            configuration.is_system_managed is not None,
            configuration.is_user_configurable is not None,
            configuration.requires_restart is not None,
            configuration.validation_rules is not None,
            configuration.default_value is not None
        ]):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admins can only update configuration values"
            )
    
    # Update fields
    update_data = configuration.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_config, field, value)
    
    # Validate the new value if it's being updated
    if configuration.value is not None:
        is_valid, error_message = db_config.validate_value(configuration.value)
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid configuration value: {error_message}"
            )
    
    db_config.updated_by_user_id = current_user.user_id
    db_config.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(db_config)
    
    logger.info(f"System configuration '{db_config.key}' updated by user {current_user.username}")
    
    # Return response with typed value
    config_dict = {
        "id": db_config.id,
        "category": db_config.category,
        "key": db_config.key,
        "value": db_config.value,
        "data_type": db_config.data_type,
        "description": db_config.description,
        "is_system_managed": db_config.is_system_managed,
        "is_user_configurable": db_config.is_user_configurable,
        "requires_restart": db_config.requires_restart,
        "validation_rules": db_config.validation_rules,
        "default_value": db_config.default_value,
        "created_by_user_id": db_config.created_by_user_id,
        "updated_by_user_id": db_config.updated_by_user_id,
        "created_at": db_config.created_at,
        "updated_at": db_config.updated_at,
        "typed_value": db_config.get_typed_value()
    }
    
    return SystemConfigurationResponse(**config_dict)


@router.delete("/system/{config_id}")
async def delete_system_configuration(
    config_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a system configuration setting. Only superadmins can delete system configurations."""
    check_superadmin_access(current_user)
    
    db_config = db.query(SystemConfiguration).filter(SystemConfiguration.id == config_id).first()
    if not db_config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Configuration not found"
        )
    
    # Check if it's system managed
    if db_config.is_system_managed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete system-managed configuration"
        )
    
    config_key = db_config.key
    db.delete(db_config)
    db.commit()
    
    logger.info(f"System configuration '{config_key}' deleted by user {current_user.username}")
    
    return {"message": f"Configuration '{config_key}' deleted successfully"}


# --- Organization Configuration Endpoints ---

@router.get("/organization/{organization_id}", response_model=List[OrganizationConfigurationResponse])
async def get_organization_configurations(
    organization_id: uuid.UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get organization-specific configuration overrides."""
    check_admin_access(current_user)
    
    # Check permissions
    if get_user_role(current_user) != "super_admin":
        if current_user.organization_id != organization_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only access configurations for your own organization"
            )
    
    # Verify organization exists
    organization = db.query(Organization).filter(Organization.id == organization_id).first()
    if not organization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found"
        )
    
    configurations = db.query(OrganizationConfiguration)\
        .filter(OrganizationConfiguration.organization_id == organization_id)\
        .offset(skip).limit(limit).all()
    
    return configurations


@router.post("/organization", response_model=OrganizationConfigurationResponse)
async def create_organization_configuration(
    configuration: OrganizationConfigurationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create an organization-specific configuration override."""
    check_admin_access(current_user)
    
    # Check permissions
    if get_user_role(current_user) != "super_admin":
        if current_user.organization_id != configuration.organization_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only create configurations for your own organization"
            )
    
    # Verify organization exists
    organization = db.query(Organization).filter(Organization.id == configuration.organization_id).first()
    if not organization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found"
        )
    
    # Check if configuration key exists in system configurations
    system_config = db.query(SystemConfiguration).filter(
        SystemConfiguration.key == configuration.configuration_key
    ).first()
    
    if not system_config:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"System configuration '{configuration.configuration_key}' does not exist"
        )
    
    if not system_config.is_user_configurable:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Configuration '{configuration.configuration_key}' is not user-configurable"
        )
    
    # Check if organization configuration already exists
    existing_config = db.query(OrganizationConfiguration).filter(
        and_(
            OrganizationConfiguration.organization_id == configuration.organization_id,
            OrganizationConfiguration.configuration_key == configuration.configuration_key
        )
    ).first()
    
    if existing_config:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Organization configuration for '{configuration.configuration_key}' already exists"
        )
    
    # Validate the value against system configuration rules
    if configuration.value and system_config.validation_rules:
        is_valid, error_message = system_config.validate_value(configuration.value)
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid configuration value: {error_message}"
            )
    
    # Create organization configuration
    db_config = OrganizationConfiguration(
        organization_id=configuration.organization_id,
        configuration_key=configuration.configuration_key,
        value=configuration.value,
        is_active=configuration.is_active,
        created_by_user_id=current_user.user_id,
        updated_by_user_id=current_user.user_id
    )
    
    db.add(db_config)
    db.commit()
    db.refresh(db_config)
    
    logger.info(f"Organization configuration '{configuration.configuration_key}' created for organization {organization_id} by user {current_user.username}")
    
    return db_config


# --- Configuration Templates ---

@router.get("/templates", response_model=ConfigurationTemplateResponse)
async def get_configuration_templates(
    current_user: User = Depends(get_current_user)
):
    """Get predefined configuration templates for different categories."""
    check_admin_access(current_user)
    
    return ConfigurationTemplateResponse(
        organization_management=OrganizationManagementConfig(),
        parts_management=PartsManagementConfig(),
        user_management=UserManagementConfig(),
        localization=LocalizationConfig()
    )


@router.post("/initialize-defaults")
async def initialize_default_configurations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Initialize default system configurations. Only superadmins can initialize defaults."""
    check_superadmin_access(current_user)
    
    default_configs = [
        # Organization Management
        {
            "category": ConfigurationCategory.ORGANIZATION,
            "key": "org.default_country",
            "value": "GR",
            "data_type": ConfigurationDataType.ENUM,
            "description": "Default country for new organizations",
            "validation_rules": {"allowed_values": ["GR", "KSA", "ES", "CY", "OM"]},
            "default_value": "GR"
        },
        {
            "category": ConfigurationCategory.ORGANIZATION,
            "key": "org.auto_create_warehouse",
            "value": "true",
            "data_type": ConfigurationDataType.BOOLEAN,
            "description": "Automatically create default warehouse for new organizations",
            "default_value": "true"
        },
        {
            "category": ConfigurationCategory.ORGANIZATION,
            "key": "org.max_suppliers_per_organization",
            "value": "50",
            "data_type": ConfigurationDataType.INTEGER,
            "description": "Maximum number of suppliers per organization",
            "validation_rules": {"min": 1, "max": 200},
            "default_value": "50"
        },
        
        # Parts Management
        {
            "category": ConfigurationCategory.PARTS,
            "key": "parts.max_photos_per_part",
            "value": "4",
            "data_type": ConfigurationDataType.INTEGER,
            "description": "Maximum number of photos per part",
            "validation_rules": {"min": 1, "max": 10},
            "default_value": "4"
        },
        {
            "category": ConfigurationCategory.PARTS,
            "key": "parts.photo_max_size_mb",
            "value": "5",
            "data_type": ConfigurationDataType.INTEGER,
            "description": "Maximum photo size in MB",
            "validation_rules": {"min": 1, "max": 20},
            "default_value": "5"
        },
        {
            "category": ConfigurationCategory.PARTS,
            "key": "parts.supported_photo_formats",
            "value": '["jpg", "jpeg", "png", "webp"]',
            "data_type": ConfigurationDataType.JSON,
            "description": "Supported photo formats for parts",
            "default_value": '["jpg", "jpeg", "png", "webp"]'
        },
        
        # User Management
        {
            "category": ConfigurationCategory.USER_MANAGEMENT,
            "key": "user.password_min_length",
            "value": "8",
            "data_type": ConfigurationDataType.INTEGER,
            "description": "Minimum password length",
            "validation_rules": {"min": 6, "max": 128},
            "default_value": "8"
        },
        {
            "category": ConfigurationCategory.USER_MANAGEMENT,
            "key": "user.session_timeout_minutes",
            "value": "480",
            "data_type": ConfigurationDataType.INTEGER,
            "description": "Session timeout in minutes",
            "validation_rules": {"min": 30, "max": 1440},
            "default_value": "480"
        },
        {
            "category": ConfigurationCategory.USER_MANAGEMENT,
            "key": "user.max_failed_login_attempts",
            "value": "5",
            "data_type": ConfigurationDataType.INTEGER,
            "description": "Maximum failed login attempts before lockout",
            "validation_rules": {"min": 3, "max": 10},
            "default_value": "5"
        },
        
        # Localization
        {
            "category": ConfigurationCategory.LOCALIZATION,
            "key": "locale.supported_languages",
            "value": '["en", "el", "ar", "es"]',
            "data_type": ConfigurationDataType.JSON,
            "description": "Supported languages",
            "default_value": '["en", "el", "ar", "es"]'
        },
        {
            "category": ConfigurationCategory.LOCALIZATION,
            "key": "locale.supported_countries",
            "value": '["GR", "KSA", "ES", "CY", "OM"]',
            "data_type": ConfigurationDataType.JSON,
            "description": "Supported countries",
            "default_value": '["GR", "KSA", "ES", "CY", "OM"]'
        },
        {
            "category": ConfigurationCategory.LOCALIZATION,
            "key": "locale.default_language",
            "value": "en",
            "data_type": ConfigurationDataType.ENUM,
            "description": "Default language for new users",
            "validation_rules": {"allowed_values": ["en", "el", "ar", "es"]},
            "default_value": "en"
        }
    ]
    
    created_count = 0
    skipped_count = 0
    
    for config_data in default_configs:
        # Check if configuration already exists
        existing_config = db.query(SystemConfiguration).filter(
            SystemConfiguration.key == config_data["key"]
        ).first()
        
        if existing_config:
            skipped_count += 1
            continue
        
        # Create new configuration
        db_config = SystemConfiguration(
            category=config_data["category"],
            key=config_data["key"],
            value=config_data["value"],
            data_type=config_data["data_type"],
            description=config_data["description"],
            is_system_managed=False,
            is_user_configurable=True,
            requires_restart=False,
            validation_rules=config_data.get("validation_rules"),
            default_value=config_data["default_value"],
            created_by_user_id=current_user.user_id,
            updated_by_user_id=current_user.user_id
        )
        
        db.add(db_config)
        created_count += 1
    
    db.commit()
    
    logger.info(f"Default configurations initialized: {created_count} created, {skipped_count} skipped by user {current_user.username}")
    
    return {
        "message": "Default configurations initialized successfully",
        "created_count": created_count,
        "skipped_count": skipped_count
    }


# --- Validation Endpoint ---

@router.post("/validate", response_model=ConfigurationValidationResponse)
async def validate_configuration_value(
    validation_request: ConfigurationValidationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Validate a configuration value against its validation rules."""
    check_admin_access(current_user)
    
    # Get system configuration
    system_config = db.query(SystemConfiguration).filter(
        SystemConfiguration.key == validation_request.key
    ).first()
    
    if not system_config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Configuration '{validation_request.key}' not found"
        )
    
    # Validate the value
    is_valid, error_message = system_config.validate_value(validation_request.value)
    
    return ConfigurationValidationResponse(
        is_valid=is_valid,
        error_message=error_message
    )