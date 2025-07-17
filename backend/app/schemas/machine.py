# backend/app/schemas/machine.py

import uuid
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field

class MachineBase(BaseModel):
    customer_organization_id: uuid.UUID
    model_type: str  # e.g., 'V3.1B', 'V4.0'
    name: str
    serial_number: str

class MachineCreate(MachineBase):
    pass

class MachineUpdate(BaseModel):
    model_type: Optional[str] = None
    name: Optional[str] = None
    serial_number: Optional[str] = None

class MachineResponse(MachineBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    
    # Include organization name for easier display
    customer_organization_name: Optional[str] = None

    class Config:
        orm_mode = True

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
        orm_mode = True