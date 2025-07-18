# backend/app/schemas/warehouse.py

import uuid
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field

class BaseSchema(BaseModel):
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    class Config:
        from_attributes = True # Allow ORM models to be converted to Pydantic models

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