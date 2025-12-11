# backend/app/schemas/stocktake.py

import uuid
from typing import Optional, List
from decimal import Decimal
from datetime import datetime
from pydantic import BaseModel, Field

class StocktakeLocation(BaseModel):
    warehouse_id: uuid.UUID
    warehouse_name: str
    organization_id: uuid.UUID
    organization_name: str
    total_parts: int
    last_stocktake: Optional[datetime] = None

    class Config:
        from_attributes = True

class StocktakeWorksheetItemBase(BaseModel):
    warehouse_id: uuid.UUID
    part_id: uuid.UUID
    expected_quantity: Decimal
    actual_quantity: Optional[Decimal] = None
    variance: Optional[Decimal] = None
    notes: Optional[str] = None

class StocktakeWorksheetItemCreate(StocktakeWorksheetItemBase):
    pass

class StocktakeWorksheetItemUpdate(BaseModel):
    actual_quantity: Optional[Decimal] = None
    variance: Optional[Decimal] = None
    notes: Optional[str] = None

class StocktakeWorksheetItemResponse(StocktakeWorksheetItemBase):
    id: uuid.UUID
    # Include related data for easier display
    warehouse_name: Optional[str] = None
    part_number: Optional[str] = None
    part_name: Optional[str] = None
    unit_of_measure: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class StocktakeSessionBase(BaseModel):
    organization_id: uuid.UUID
    name: str
    description: Optional[str] = None
    status: str = "planned"  # planned, in_progress, completed, cancelled

class StocktakeSessionCreate(StocktakeSessionBase):
    pass

class StocktakeSessionUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None

class StocktakeSessionResponse(StocktakeSessionBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_by_user_id: Optional[uuid.UUID] = None
    
    # Summary data
    total_items: Optional[int] = None
    completed_items: Optional[int] = None
    variance_count: Optional[int] = None

    class Config:
        from_attributes = True