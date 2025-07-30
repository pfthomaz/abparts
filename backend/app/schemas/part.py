# backend/app/schemas/part.py

import uuid
from typing import Optional, List, Dict, Any
from enum import Enum
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, Field, field_validator

from .organization import OrganizationTypeEnum

class PartTypeEnum(str, Enum):
    CONSUMABLE = "consumable"
    BULK_MATERIAL = "bulk_material"

class PartBase(BaseModel):
    part_number: str = Field(..., max_length=255)
    name: str = Field(..., min_length=1, description="Multilingual part name (supports compound strings)")
    description: Optional[str] = None
    part_type: PartTypeEnum = PartTypeEnum.CONSUMABLE
    is_proprietary: bool = False
    unit_of_measure: str = Field(default="pieces", max_length=50)
    manufacturer: Optional[str] = Field(None, max_length=255, description="Part manufacturer name")
    part_code: Optional[str] = Field(None, max_length=100, description="AutoBoss-specific part code")
    serial_number: Optional[str] = Field(None, max_length=255, description="Part serial number if available")
    manufacturer_part_number: Optional[str] = Field(None, max_length=255)
    manufacturer_delivery_time_days: Optional[int] = None
    local_supplier_delivery_time_days: Optional[int] = None
    image_urls: Optional[List[str]] = Field(None, max_items=4, description="Up to 4 image URLs")
    
    @field_validator('image_urls')
    @classmethod
    def validate_image_urls(cls, v):
        if v is not None:
            if len(v) > 4:
                raise ValueError('Maximum 4 images allowed per part')
            # Validate each URL is not empty
            for url in v:
                if not url or not url.strip():
                    raise ValueError('Image URLs cannot be empty')
        return v
    
    @field_validator('part_type')
    @classmethod
    def validate_part_type(cls, v):
        if v not in [PartTypeEnum.CONSUMABLE, PartTypeEnum.BULK_MATERIAL]:
            raise ValueError('Part type must be either consumable or bulk_material')
        return v
    
    @field_validator('name')
    @classmethod
    def validate_multilingual_name(cls, v):
        if not v or not v.strip():
            raise ValueError('Part name cannot be empty')
        # Allow multilingual compound strings - no specific format validation for now
        # This can be extended later for specific multilingual formats
        return v.strip()

class PartCreate(PartBase):
    pass

class PartUpdate(BaseModel):
    part_number: Optional[str] = Field(None, max_length=255)
    name: Optional[str] = Field(None, min_length=1, description="Multilingual part name (supports compound strings)")
    description: Optional[str] = None
    part_type: Optional[PartTypeEnum] = None
    is_proprietary: Optional[bool] = None
    unit_of_measure: Optional[str] = Field(None, max_length=50)
    manufacturer: Optional[str] = Field(None, max_length=255, description="Part manufacturer name")
    part_code: Optional[str] = Field(None, max_length=100, description="AutoBoss-specific part code")
    serial_number: Optional[str] = Field(None, max_length=255, description="Part serial number if available")
    manufacturer_part_number: Optional[str] = Field(None, max_length=255)
    manufacturer_delivery_time_days: Optional[int] = None
    local_supplier_delivery_time_days: Optional[int] = None
    image_urls: Optional[List[str]] = Field(None, max_items=4, description="Up to 4 image URLs")
    
    @field_validator('image_urls')
    @classmethod
    def validate_image_urls(cls, v):
        if v is not None:
            if len(v) > 4:
                raise ValueError('Maximum 4 images allowed per part')
            # Validate each URL is not empty
            for url in v:
                if not url or not url.strip():
                    raise ValueError('Image URLs cannot be empty')
        return v
    
    @field_validator('part_type')
    @classmethod
    def validate_part_type(cls, v):
        if v is not None and v not in [PartTypeEnum.CONSUMABLE, PartTypeEnum.BULK_MATERIAL]:
            raise ValueError('Part type must be either consumable or bulk_material')
        return v
    
    @field_validator('name')
    @classmethod
    def validate_multilingual_name(cls, v):
        if v is not None:
            if not v or not v.strip():
                raise ValueError('Part name cannot be empty')
            return v.strip()
        return v

class PartResponse(PartBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }

class ImageUploadResponse(BaseModel):
    url: str

    class Config:
        from_attributes = True

class WarehouseInventoryItem(BaseModel):
    """Inventory information for a part in a specific warehouse"""
    warehouse_id: uuid.UUID
    warehouse_name: str
    current_stock: Decimal
    minimum_stock_recommendation: Decimal
    is_low_stock: bool
    unit_of_measure: str

    class Config:
        from_attributes = True

class PartWithInventoryResponse(PartResponse):
    """Part response with inventory information across warehouses"""
    total_stock: Decimal
    warehouse_inventory: List[WarehouseInventoryItem] = []
    is_low_stock: bool = False
    
    class Config:
        from_attributes = True

class PartUsageHistoryItem(BaseModel):
    """Usage history item for a part"""
    usage_date: datetime
    quantity: Decimal
    machine_id: Optional[uuid.UUID] = None
    machine_serial: Optional[str] = None
    warehouse_id: uuid.UUID
    warehouse_name: str
    
    class Config:
        from_attributes = True

class PartWithUsageResponse(PartWithInventoryResponse):
    """Part response with inventory and usage history"""
    usage_history: List[PartUsageHistoryItem] = []
    avg_monthly_usage: Optional[Decimal] = None
    estimated_depletion_days: Optional[int] = None
    
    class Config:
        from_attributes = True

class PartReorderSuggestion(BaseModel):
    """Reorder suggestion for a part based on usage patterns"""
    part_id: uuid.UUID
    part_number: str
    part_name: str
    current_total_stock: Decimal
    avg_monthly_usage: Decimal
    estimated_depletion_days: int
    suggested_reorder_quantity: Decimal
    unit_of_measure: str
    is_proprietary: bool
    
    class Config:
        from_attributes = True