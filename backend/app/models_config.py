# backend/app/models_config.py

import uuid
import enum
from datetime import datetime
from sqlalchemy import Column, String, Boolean, Integer, ForeignKey, DateTime, Text, JSON, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from .database import Base


class ConfigurationCategory(enum.Enum):
    ORGANIZATION = "organization"
    PARTS = "parts"
    USER_MANAGEMENT = "user_management"
    LOCALIZATION = "localization"
    SYSTEM = "system"


class ConfigurationDataType(enum.Enum):
    STRING = "string"
    INTEGER = "integer"
    BOOLEAN = "boolean"
    JSON = "json"
    ENUM = "enum"


class SystemConfiguration(Base):
    """
    SQLAlchemy model for system configuration settings.
    Stores various configuration options for the ABParts system.
    """
    __tablename__ = "system_configurations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    category = Column(Enum(ConfigurationCategory), nullable=False)
    key = Column(String(255), nullable=False, unique=True, index=True)
    value = Column(Text, nullable=True)
    data_type = Column(Enum(ConfigurationDataType), nullable=False)
    description = Column(Text, nullable=True)
    is_system_managed = Column(Boolean, nullable=False, server_default='false')
    is_user_configurable = Column(Boolean, nullable=False, server_default='true')
    requires_restart = Column(Boolean, nullable=False, server_default='false')
    validation_rules = Column(JSON, nullable=True)  # JSON field for validation rules
    default_value = Column(Text, nullable=True)
    created_by_user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    updated_by_user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    created_by_user = relationship("User", foreign_keys=[created_by_user_id])
    updated_by_user = relationship("User", foreign_keys=[updated_by_user_id])

    def get_typed_value(self):
        """Return the configuration value in its proper data type."""
        if self.value is None:
            return None
        
        if self.data_type == ConfigurationDataType.BOOLEAN:
            return self.value.lower() in ('true', '1', 'yes', 'on')
        elif self.data_type == ConfigurationDataType.INTEGER:
            try:
                return int(self.value)
            except (ValueError, TypeError):
                return None
        elif self.data_type == ConfigurationDataType.JSON:
            try:
                import json
                return json.loads(self.value)
            except (ValueError, TypeError):
                return None
        else:  # STRING or ENUM
            return self.value

    def set_typed_value(self, value):
        """Set the configuration value from a typed value."""
        if value is None:
            self.value = None
            return
        
        if self.data_type == ConfigurationDataType.BOOLEAN:
            self.value = str(bool(value)).lower()
        elif self.data_type == ConfigurationDataType.INTEGER:
            self.value = str(int(value))
        elif self.data_type == ConfigurationDataType.JSON:
            import json
            self.value = json.dumps(value)
        else:  # STRING or ENUM
            self.value = str(value)

    def validate_value(self, value):
        """Validate a value against the configuration's validation rules."""
        if not self.validation_rules:
            return True, None
        
        import json
        rules = self.validation_rules if isinstance(self.validation_rules, dict) else json.loads(self.validation_rules)
        
        # Check required
        if rules.get('required', False) and (value is None or value == ''):
            return False, "Value is required"
        
        # Check min/max for integers
        if self.data_type == ConfigurationDataType.INTEGER and value is not None:
            try:
                int_value = int(value)
                if 'min' in rules and int_value < rules['min']:
                    return False, f"Value must be at least {rules['min']}"
                if 'max' in rules and int_value > rules['max']:
                    return False, f"Value must be at most {rules['max']}"
            except (ValueError, TypeError):
                return False, "Value must be a valid integer"
        
        # Check allowed values for enums
        if self.data_type == ConfigurationDataType.ENUM and value is not None:
            allowed_values = rules.get('allowed_values', [])
            if allowed_values and value not in allowed_values:
                return False, f"Value must be one of: {', '.join(allowed_values)}"
        
        # Check string length
        if self.data_type == ConfigurationDataType.STRING and value is not None:
            if 'min_length' in rules and len(str(value)) < rules['min_length']:
                return False, f"Value must be at least {rules['min_length']} characters"
            if 'max_length' in rules and len(str(value)) > rules['max_length']:
                return False, f"Value must be at most {rules['max_length']} characters"
        
        return True, None

    def __repr__(self):
        return f"<SystemConfiguration(key='{self.key}', category='{self.category.value}', value='{self.value}')>"


class OrganizationConfiguration(Base):
    """
    SQLAlchemy model for organization-specific configuration settings.
    Allows organizations to override system-wide settings.
    """
    __tablename__ = "organization_configurations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    configuration_key = Column(String(255), nullable=False)
    value = Column(Text, nullable=True)
    is_active = Column(Boolean, nullable=False, server_default='true')
    created_by_user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    updated_by_user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    organization = relationship("Organization")
    created_by_user = relationship("User", foreign_keys=[created_by_user_id])
    updated_by_user = relationship("User", foreign_keys=[updated_by_user_id])

    # Composite unique constraint
    __table_args__ = (
        {'extend_existing': True}
    )

    def __repr__(self):
        return f"<OrganizationConfiguration(org_id={self.organization_id}, key='{self.configuration_key}', value='{self.value}')>"