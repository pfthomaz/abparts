# backend/app/schemas/part.py

import uuid
from typing import Optional, List
from enum import Enum
from datetime import datetime
from pydantic import BaseModel, Field

from .organization import OrganizationTypeEnum

class PartTypeEnum(str, Enum):
    CONSUMABLE = "consumable"
    BULK_MATERIAL = "bulk_material"

class PartBase(BaseModel):
    part_number: str
    name: str
    description: Optional[str] = None
    part_type: PartTypeEnum = PartTypeEnum.CONSUMABLE
    is_proprietary: bool = False
    unit_of_measure: str = "pieces"
    manufacturer_part_number: Optional[str] = None
    manufacturer_delivery_time_days: Optional[int] = None
    local_supplier_delivery_time_days: Optional[int] = None
    image_urls: Optional[List[str]] = None

class PartCreate(PartBase):
    pass

class PartUpdate(BaseModel):
    part_number: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    part_type: Optional[PartTypeEnum] = None
    is_proprietary: Optional[bool] = None
    unit_of_measure: Optional[str] = None
    manufacturer_part_number: Optional[str] = None
    manufacturer_delivery_time_days: Optional[int] = None
    local_supplier_delivery_time_days: Optional[int] = None
    image_urls: Optional[List[str]] = None

class PartResponse(PartBase):
    id: uuid.UUID
    created_at: str
    updated_at: str

    class Config:
        orm_mode = True

class ImageUploadResponse(BaseModel):
    filename: str
    url: str
    size: int
    content_type: str
    uploaded_at: datetime

    class Config:
        orm_mode = True