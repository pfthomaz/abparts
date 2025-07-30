# backend/app/schemas/stock_adjustment.py

import uuid
from typing import Optional, List
from decimal import Decimal
from datetime import datetime
from pydantic import BaseModel, Field

class StockAdjustmentBase(BaseModel):
    inventory_id: uuid.UUID
    user_id: uuid.UUID
    adjustment_date: datetime
    quantity_adjusted: Decimal  # Positive for increase, negative for decrease
    reason_code: str
    notes: Optional[str] = None

class StockAdjustmentCreate(StockAdjustmentBase):
    pass

class StockAdjustmentUpdate(BaseModel):
    quantity_adjusted: Optional[Decimal] = None
    reason_code: Optional[str] = None
    notes: Optional[str] = None

class StockAdjustmentResponse(StockAdjustmentBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    
    # Include related data for easier display
    warehouse_name: Optional[str] = None
    part_number: Optional[str] = None
    part_name: Optional[str] = None
    user_username: Optional[str] = None

    class Config:
        from_attributes = True