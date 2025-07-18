# backend/app/schemas/machine.py

import uuid
from typing import Optional, List
from datetime import datetime
from enum import Enum
from decimal import Decimal
from pydantic import BaseModel, Field

class MachineStatusEnum(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    MAINTENANCE = "maintenance"
    DECOMMISSIONED = "decommissioned"

class MaintenanceTypeEnum(str, Enum):
    SCHEDULED = "scheduled"
    UNSCHEDULED = "unscheduled"
    REPAIR = "repair"
    INSPECTION = "inspection"
    CLEANING = "cleaning"
    CALIBRATION = "calibration"
    OTHER = "other"

class MachineBase(BaseModel):
    customer_organization_id: uuid.UUID
    model_type: str  # e.g., 'V3.1B', 'V4.0'
    name: str
    serial_number: str
    purchase_date: Optional[datetime] = None
    warranty_expiry_date: Optional[datetime] = None
    status: MachineStatusEnum = MachineStatusEnum.ACTIVE
    last_maintenance_date: Optional[datetime] = None
    next_maintenance_date: Optional[datetime] = None
    location: Optional[str] = None
    notes: Optional[str] = None

class MachineCreate(MachineBase):
    pass

class MachineUpdate(BaseModel):
    customer_organization_id: Optional[uuid.UUID] = None
    model_type: Optional[str] = None
    name: Optional[str] = None
    serial_number: Optional[str] = None
    purchase_date: Optional[datetime] = None
    warranty_expiry_date: Optional[datetime] = None
    status: Optional[MachineStatusEnum] = None
    last_maintenance_date: Optional[datetime] = None
    next_maintenance_date: Optional[datetime] = None
    location: Optional[str] = None
    notes: Optional[str] = None

class MachineResponse(MachineBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    
    # Include organization name for easier display
    customer_organization_name: Optional[str] = None

    class Config:
        from_attributes = True

class PartUsageBase(BaseModel):
    customer_organization_id: uuid.UUID
    part_id: uuid.UUID
    usage_date: datetime
    quantity_used: float
    machine_id: Optional[uuid.UUID] = None
    recorded_by_user_id: Optional[uuid.UUID] = None
    notes: Optional[str] = None

class PartUsageCreate(PartUsageBase):
    pass

class PartUsageUpdate(BaseModel):
    usage_date: Optional[datetime] = None
    quantity_used: Optional[float] = None
    machine_id: Optional[uuid.UUID] = None
    notes: Optional[str] = None

class PartUsageResponse(PartUsageBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    
    # Include related data for easier display
    customer_organization_name: Optional[str] = None
    part_number: Optional[str] = None
    part_name: Optional[str] = None
    machine_name: Optional[str] = None
    recorded_by_username: Optional[str] = None

    class Config:
        from_attributes = True

# Machine Maintenance Schemas
class MaintenanceBase(BaseModel):
    machine_id: uuid.UUID
    maintenance_date: datetime
    maintenance_type: MaintenanceTypeEnum
    performed_by_user_id: uuid.UUID
    description: str
    hours_spent: Optional[Decimal] = None
    cost: Optional[Decimal] = None
    next_maintenance_date: Optional[datetime] = None
    notes: Optional[str] = None

class MaintenanceCreate(MaintenanceBase):
    pass

class MaintenanceUpdate(BaseModel):
    maintenance_date: Optional[datetime] = None
    maintenance_type: Optional[MaintenanceTypeEnum] = None
    performed_by_user_id: Optional[uuid.UUID] = None
    description: Optional[str] = None
    hours_spent: Optional[Decimal] = None
    cost: Optional[Decimal] = None
    next_maintenance_date: Optional[datetime] = None
    notes: Optional[str] = None

class MaintenanceResponse(MaintenanceBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    
    # Include related data for easier display
    machine_name: Optional[str] = None
    machine_serial_number: Optional[str] = None
    performed_by_username: Optional[str] = None

    class Config:
        from_attributes = True

# Maintenance Part Usage Schemas
class MaintenancePartUsageBase(BaseModel):
    maintenance_id: uuid.UUID
    part_id: uuid.UUID
    quantity: Decimal
    warehouse_id: uuid.UUID
    notes: Optional[str] = None

class MaintenancePartUsageCreate(MaintenancePartUsageBase):
    pass

class MaintenancePartUsageUpdate(BaseModel):
    quantity: Optional[Decimal] = None
    warehouse_id: Optional[uuid.UUID] = None
    notes: Optional[str] = None

class MaintenancePartUsageResponse(MaintenancePartUsageBase):
    id: uuid.UUID
    created_at: datetime
    
    # Include related data for easier display
    part_number: Optional[str] = None
    part_name: Optional[str] = None
    warehouse_name: Optional[str] = None

    class Config:
        from_attributes = True

# Machine Part Compatibility Schemas
class MachinePartCompatibilityBase(BaseModel):
    machine_id: uuid.UUID
    part_id: uuid.UUID
    is_recommended: bool = False
    notes: Optional[str] = None

class MachinePartCompatibilityCreate(MachinePartCompatibilityBase):
    pass

class MachinePartCompatibilityUpdate(BaseModel):
    is_recommended: Optional[bool] = None
    notes: Optional[str] = None

class MachinePartCompatibilityResponse(MachinePartCompatibilityBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    
    # Include related data for easier display
    machine_name: Optional[str] = None
    machine_model_type: Optional[str] = None
    part_number: Optional[str] = None
    part_name: Optional[str] = None

    class Config:
        from_attributes = True

# Machine Transfer Schema
class MachineTransferRequest(BaseModel):
    machine_id: uuid.UUID
    new_customer_organization_id: uuid.UUID
    transfer_date: datetime = Field(default_factory=datetime.now)
    transfer_notes: Optional[str] = None