# backend/app/schemas/inventory.py

import uuid
from typing import Optional, List
from decimal import Decimal
from datetime import datetime
from pydantic import BaseModel, Field

class InventoryBase(BaseModel):
    warehouse_id: uuid.UUID
    part_id: uuid.UUID
    current_stock: Decimal
    minimum_stock_recommendation: Optional[Decimal] = Field(default=0)
    unit_of_measure: str
    reorder_threshold_set_by: Optional[str] = None
    last_recommendation_update: Optional[datetime] = None

class InventoryCreate(InventoryBase):
    pass

class InventoryUpdate(BaseModel):
    current_stock: Optional[Decimal] = None
    minimum_stock_recommendation: Optional[Decimal] = None
    unit_of_measure: Optional[str] = None
    reorder_threshold_set_by: Optional[str] = None
    last_recommendation_update: Optional[datetime] = None

class InventoryResponse(InventoryBase):
    id: uuid.UUID
    last_updated: datetime
    created_at: datetime
    
    # Include related data
    part_name: Optional[str] = None
    part_number: Optional[str] = None
    warehouse_name: Optional[str] = None

    class Config:
        orm_mode = True