# backend/app/schemas/part.py

import uuid
from typing import Optional, List, Dict, Any
from enum import Enum
from datetime import datetime
from decimal import Decimal
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
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }

class ImageUploadResponse(BaseModel):
    url: str

    class Config:
        orm_mode = True

class WarehouseInventoryItem(BaseModel):
    """Inventory information for a part in a specific warehouse"""
    warehouse_id: uuid.UUID
    warehouse_name: str
    current_stock: Decimal
    minimum_stock_recommendation: Decimal
    is_low_stock: bool
    unit_of_measure: str

    class Config:
        orm_mode = True

class PartWithInventoryResponse(PartResponse):
    """Part response with inventory information across warehouses"""
    total_stock: Decimal
    warehouse_inventory: List[WarehouseInventoryItem] = []
    is_low_stock: bool = False
    
    class Config:
        orm_mode = True

class PartUsageHistoryItem(BaseModel):
    """Usage history item for a part"""
    usage_date: datetime
    quantity: Decimal
    machine_id: Optional[uuid.UUID] = None
    machine_serial: Optional[str] = None
    warehouse_id: uuid.UUID
    warehouse_name: str
    
    class Config:
        orm_mode = True

class PartWithUsageResponse(PartWithInventoryResponse):
    """Part response with inventory and usage history"""
    usage_history: List[PartUsageHistoryItem] = []
    avg_monthly_usage: Optional[Decimal] = None
    estimated_depletion_days: Optional[int] = None
    
    class Config:
        orm_mode = True

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
        orm_mode = True