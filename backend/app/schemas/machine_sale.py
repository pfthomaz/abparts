# backend/app/schemas/machine_sale.py

import uuid
from typing import Optional
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, Field

class MachineSaleRequest(BaseModel):
    """Schema for machine sale transaction request"""
    machine_id: uuid.UUID = Field(..., description="ID of the machine being sold")
    from_organization_id: uuid.UUID = Field(..., description="ID of the selling organization (typically Oraseas EE)")
    to_organization_id: uuid.UUID = Field(..., description="ID of the buying organization (customer)")
    sale_price: Optional[Decimal] = Field(None, description="Sale price of the machine")
    sale_date: datetime = Field(..., description="Date of the sale")
    performed_by_user_id: Optional[uuid.UUID] = Field(None, description="ID of the user performing the sale")
    notes: Optional[str] = Field(None, description="Additional notes about the sale")
    reference_number: Optional[str] = Field(None, description="Reference number for the sale")

class MachineSaleResponse(BaseModel):
    """Schema for machine sale transaction response"""
    machine_id: uuid.UUID
    from_organization_id: uuid.UUID
    to_organization_id: uuid.UUID
    sale_price: Optional[Decimal]
    sale_date: datetime
    performed_by_user_id: uuid.UUID
    notes: Optional[str]
    reference_number: Optional[str]
    created_at: datetime
    
    # Include related data
    machine_serial: Optional[str] = None
    machine_name: Optional[str] = None
    from_organization_name: Optional[str] = None
    to_organization_name: Optional[str] = None
    performed_by_username: Optional[str] = None

    class Config:
        from_attributes = True