# backend/app/schemas/maintenance_protocol.py

import uuid
from datetime import datetime, date
from decimal import Decimal
from typing import List, Optional, TYPE_CHECKING
from pydantic import BaseModel, Field, validator
from enum import Enum

if TYPE_CHECKING:
    from .part import PartResponse
    from .machine import MachineResponse
    from .user import UserResponse
    from .part_usage import PartUsageResponse


# Base schema with common fields
class BaseSchema(BaseModel):
    class Config:
        from_attributes = True


# Enums for validation
class ProtocolTypeEnum(str, Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    SCHEDULED = "scheduled"
    CUSTOM = "custom"


class ChecklistItemTypeEnum(str, Enum):
    CHECK = "check"
    SERVICE = "service"
    REPLACEMENT = "replacement"


class ChecklistItemStatusEnum(str, Enum):
    COMPLETED = "completed"
    SKIPPED = "skipped"


class MaintenanceExecutionStatusEnum(str, Enum):
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    PARTIAL = "partial"
    SKIPPED = "skipped"


class ReminderStatusEnum(str, Enum):
    PENDING = "pending"
    ACKNOWLEDGED = "acknowledged"
    COMPLETED = "completed"
    DISMISSED = "dismissed"


# Protocol Checklist Item Schemas
class ProtocolChecklistItemBase(BaseModel):
    item_description: str = Field(..., max_length=500)
    item_type: ChecklistItemTypeEnum
    item_category: Optional[str] = Field(None, max_length=100)
    part_id: Optional[uuid.UUID] = None
    estimated_quantity: Optional[Decimal] = Field(None, decimal_places=3)
    is_critical: bool = False
    estimated_duration_minutes: Optional[int] = Field(None, ge=0)
    notes: Optional[str] = None


class ProtocolChecklistItemCreate(ProtocolChecklistItemBase):
    item_order: int = Field(..., ge=1)


class ProtocolChecklistItemUpdate(BaseModel):
    item_description: Optional[str] = Field(None, max_length=500)
    item_type: Optional[ChecklistItemTypeEnum] = None
    item_category: Optional[str] = Field(None, max_length=100)
    part_id: Optional[uuid.UUID] = None
    estimated_quantity: Optional[Decimal] = Field(None, decimal_places=3)
    is_critical: Optional[bool] = None
    estimated_duration_minutes: Optional[int] = Field(None, ge=0)
    notes: Optional[str] = None
    item_order: Optional[int] = Field(None, ge=1)


class ProtocolChecklistItemResponse(ProtocolChecklistItemBase, BaseSchema):
    id: uuid.UUID
    protocol_id: uuid.UUID
    item_order: int
    part: Optional['PartResponse'] = None
    created_at: datetime


# Maintenance Protocol Schemas
class MaintenanceProtocolBase(BaseModel):
    name: str = Field(..., max_length=255)
    protocol_type: ProtocolTypeEnum
    service_interval_hours: Optional[Decimal] = Field(None, decimal_places=2, ge=0)
    is_recurring: bool = False
    machine_model: Optional[str] = Field(None, max_length=50)
    description: Optional[str] = None
    is_active: bool = True
    display_order: int = Field(default=0, ge=0)


class MaintenanceProtocolCreate(MaintenanceProtocolBase):
    pass


class MaintenanceProtocolUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=255)
    protocol_type: Optional[ProtocolTypeEnum] = None
    service_interval_hours: Optional[Decimal] = Field(None, decimal_places=2, ge=0)
    is_recurring: Optional[bool] = None
    machine_model: Optional[str] = Field(None, max_length=50)
    description: Optional[str] = None
    is_active: Optional[bool] = None
    display_order: Optional[int] = Field(None, ge=0)


class MaintenanceProtocolResponse(MaintenanceProtocolBase, BaseSchema):
    id: uuid.UUID
    checklist_items: List[ProtocolChecklistItemResponse] = []
    created_at: datetime
    updated_at: datetime


# Maintenance Execution Schemas
class MaintenanceExecutionBase(BaseModel):
    machine_id: uuid.UUID
    protocol_id: Optional[uuid.UUID] = None
    performed_date: Optional[datetime] = None
    machine_hours_at_service: Optional[Decimal] = Field(None, decimal_places=2, ge=0)
    next_service_due_hours: Optional[Decimal] = Field(None, decimal_places=2, ge=0)
    status: MaintenanceExecutionStatusEnum = MaintenanceExecutionStatusEnum.IN_PROGRESS
    notes: Optional[str] = None


class MaintenanceExecutionCreate(BaseModel):
    machine_id: uuid.UUID
    protocol_id: Optional[uuid.UUID] = None
    performed_date: Optional[datetime] = None
    machine_hours_at_service: Optional[Decimal] = Field(None, decimal_places=2, ge=0)
    next_service_due_hours: Optional[Decimal] = Field(None, decimal_places=2, ge=0)
    status: Optional[MaintenanceExecutionStatusEnum] = MaintenanceExecutionStatusEnum.IN_PROGRESS
    notes: Optional[str] = None
    checklist_completions: List['MaintenanceChecklistCompletionCreate'] = []


class MaintenanceExecutionUpdate(BaseModel):
    performed_date: Optional[datetime] = None
    machine_hours_at_service: Optional[Decimal] = Field(None, decimal_places=2, ge=0)
    next_service_due_hours: Optional[Decimal] = Field(None, decimal_places=2, ge=0)
    status: Optional[MaintenanceExecutionStatusEnum] = None
    notes: Optional[str] = None


class MaintenanceExecutionResponse(MaintenanceExecutionBase, BaseSchema):
    id: uuid.UUID
    performed_by_user_id: uuid.UUID
    machine: Optional['MachineResponse'] = None
    protocol: Optional[MaintenanceProtocolResponse] = None
    performed_by: Optional['UserResponse'] = None
    checklist_completions: List['MaintenanceChecklistCompletionResponse'] = []
    created_at: datetime
    updated_at: datetime


# Maintenance Checklist Completion Schemas
class MaintenanceChecklistCompletionBase(BaseModel):
    checklist_item_id: uuid.UUID
    status: ChecklistItemStatusEnum = ChecklistItemStatusEnum.COMPLETED
    actual_quantity_used: Optional[Decimal] = Field(None, decimal_places=3)
    notes: Optional[str] = None
    completed_at: Optional[datetime] = None


class MaintenanceChecklistCompletionCreate(BaseModel):
    status: ChecklistItemStatusEnum = ChecklistItemStatusEnum.COMPLETED
    actual_quantity_used: Optional[Decimal] = Field(None, decimal_places=3)
    notes: Optional[str] = None


class MaintenanceChecklistCompletionUpdate(BaseModel):
    is_completed: Optional[bool] = None
    completed_at: Optional[datetime] = None
    part_usage_id: Optional[uuid.UUID] = None
    notes: Optional[str] = None


class MaintenanceChecklistCompletionResponse(MaintenanceChecklistCompletionBase, BaseSchema):
    id: uuid.UUID
    execution_id: uuid.UUID
    checklist_item: Optional[ProtocolChecklistItemResponse] = None
    part_usage: Optional['PartUsageResponse'] = None
    created_at: datetime


# Maintenance Reminder Schemas
class MaintenanceReminderBase(BaseModel):
    machine_id: uuid.UUID
    protocol_id: uuid.UUID
    reminder_type: str = Field(..., max_length=50)
    due_date: Optional[date] = None
    due_hours: Optional[Decimal] = Field(None, decimal_places=2, ge=0)
    status: ReminderStatusEnum = ReminderStatusEnum.PENDING


class MaintenanceReminderCreate(MaintenanceReminderBase):
    pass


class MaintenanceReminderUpdate(BaseModel):
    status: Optional[ReminderStatusEnum] = None
    acknowledged_by_user_id: Optional[uuid.UUID] = None
    acknowledged_at: Optional[datetime] = None


class MaintenanceReminderResponse(MaintenanceReminderBase, BaseSchema):
    id: uuid.UUID
    machine: Optional['MachineResponse'] = None
    protocol: Optional[MaintenanceProtocolResponse] = None
    acknowledged_by_user_id: Optional[uuid.UUID] = None
    acknowledged_by: Optional['UserResponse'] = None
    acknowledged_at: Optional[datetime] = None
    created_at: datetime


# Reorder Schema for Checklist Items
class ChecklistItemReorderRequest(BaseModel):
    item_orders: List[dict] = Field(..., description="List of {id: uuid, order: int} objects")

    @validator('item_orders')
    def validate_item_orders(cls, v):
        if not v:
            raise ValueError('item_orders cannot be empty')
        
        for item in v:
            if 'id' not in item or 'order' not in item:
                raise ValueError('Each item must have id and order fields')
            
            try:
                uuid.UUID(str(item['id']))
            except ValueError:
                raise ValueError(f"Invalid UUID: {item['id']}")
            
            if not isinstance(item['order'], int) or item['order'] < 1:
                raise ValueError(f"Order must be a positive integer: {item['order']}")
        
        return v


# Protocol Duplication Schema
class ProtocolDuplicateRequest(BaseModel):
    new_name: str = Field(..., max_length=255)
    new_machine_model: Optional[str] = Field(None, max_length=50)
    copy_checklist_items: bool = True
