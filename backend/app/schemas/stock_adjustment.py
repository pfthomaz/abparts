# backend/app/schemas/stock_adjustment.py

import uuid
from typing import Optional, List
from decimal import Decimal
from datetime import datetime
from pydantic import BaseModel, Field
from enum import Enum


class AdjustmentTypeEnum(str, Enum):
    """Types of stock adjustments"""
    STOCK_TAKE = "stock_take"
    DAMAGE = "damage"
    LOSS = "loss"
    FOUND = "found"
    CORRECTION = "correction"
    RETURN = "return"
    OTHER = "other"


class StockAdjustmentItemCreate(BaseModel):
    """Schema for creating a stock adjustment line item"""
    part_id: uuid.UUID
    quantity_after: Decimal = Field(..., description="New quantity after adjustment")
    reason: Optional[str] = Field(None, description="Specific reason for this part adjustment")


class StockAdjustmentItemResponse(BaseModel):
    """Schema for stock adjustment line item response"""
    id: uuid.UUID
    stock_adjustment_id: uuid.UUID
    part_id: uuid.UUID
    part_number: str
    part_name: str
    quantity_before: Decimal
    quantity_after: Decimal
    quantity_change: Decimal
    reason: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


class StockAdjustmentCreate(BaseModel):
    """Schema for creating a stock adjustment"""
    warehouse_id: uuid.UUID
    adjustment_type: AdjustmentTypeEnum
    reason: Optional[str] = Field(None, description="Overall reason for adjustment")
    notes: Optional[str] = Field(None, description="Additional notes")
    items: List[StockAdjustmentItemCreate] = Field(..., min_items=1, description="Parts to adjust")


class StockAdjustmentResponse(BaseModel):
    """Schema for stock adjustment response"""
    id: uuid.UUID
    warehouse_id: uuid.UUID
    warehouse_name: str
    adjustment_type: AdjustmentTypeEnum
    reason: Optional[str]
    notes: Optional[str]
    user_id: uuid.UUID
    username: str
    adjustment_date: datetime
    total_items_adjusted: int
    items: List[StockAdjustmentItemResponse]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class StockAdjustmentListResponse(BaseModel):
    """Schema for stock adjustment list item (without full item details)"""
    id: uuid.UUID
    warehouse_id: uuid.UUID
    warehouse_name: str
    adjustment_type: AdjustmentTypeEnum
    reason: Optional[str]
    user_id: uuid.UUID
    username: str
    adjustment_date: datetime
    total_items_adjusted: int
    created_at: datetime
    
    class Config:
        from_attributes = True