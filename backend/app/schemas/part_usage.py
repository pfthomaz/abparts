# backend/app/schemas/part_usage.py

import uuid
from typing import Optional
from decimal import Decimal
from datetime import datetime
from pydantic import BaseModel, Field

class PartUsageBase(BaseModel):
    customer_organization_id: uuid.UUID
    part_id: uuid.UUID
    usage_date: datetime
    quantity: Decimal
    machine_id: Optional[uuid.UUID] = None
    recorded_by_user_id: Optional[uuid.UUID] = None
    warehouse_id: uuid.UUID
    notes: Optional[str] = None

class PartUsageCreate(PartUsageBase):
    pass

class PartUsageUpdate(BaseModel):
    usage_date: Optional[datetime] = None
    quantity: Optional[Decimal] = None
    machine_id: Optional[uuid.UUID] = None
    recorded_by_user_id: Optional[uuid.UUID] = None
    warehouse_id: Optional[uuid.UUID] = None
    notes: Optional[str] = None

class PartUsageResponse(PartUsageBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    
    # Include related data
    part_name: Optional[str] = None
    part_number: Optional[str] = None
    machine_serial: Optional[str] = None
    warehouse_name: Optional[str] = None
    
    class Config:
        orm_mode = True