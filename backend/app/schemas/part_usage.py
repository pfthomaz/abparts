# backend/app/schemas/part_usage.py

import uuid
from typing import Optional, List
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, Field

class PartUsageItemRequest(BaseModel):
    """Schema for individual part usage item"""
    part_id: uuid.UUID = Field(..., description="ID of the part being used")
    quantity: Decimal = Field(..., gt=0, description="Quantity of the part being used")
    notes: Optional[str] = Field(None, description="Notes for this specific part usage")

class PartUsageRequest(BaseModel):
    """Schema for part usage request (machine part consumption)"""
    machine_id: uuid.UUID = Field(..., description="ID of the machine where parts are being used")
    from_warehouse_id: uuid.UUID = Field(..., description="ID of the warehouse from which parts are taken")
    usage_items: List[PartUsageItemRequest] = Field(..., min_items=1, description="List of parts being used")
    usage_date: datetime = Field(..., description="Date when parts were used")
    performed_by_user_id: Optional[uuid.UUID] = Field(None, description="ID of the user recording the usage")
    service_type: Optional[str] = Field(None, description="Type of service (e.g., '50h', '250h', 'repair')")
    machine_hours: Optional[Decimal] = Field(None, description="Machine hours at time of service")
    notes: Optional[str] = Field(None, description="General notes about the part usage")
    reference_number: Optional[str] = Field(None, description="Reference number for the usage")

class PartUsageItemResponse(BaseModel):
    """Schema for part usage item response"""
    id: uuid.UUID
    part_id: uuid.UUID
    quantity: Decimal
    notes: Optional[str]
    
    # Include related data
    part_name: Optional[str] = None
    part_number: Optional[str] = None
    unit_of_measure: Optional[str] = None

    class Config:
        from_attributes = True

class PartUsageResponse(BaseModel):
    """Schema for part usage response"""
    id: uuid.UUID
    machine_id: uuid.UUID
    from_warehouse_id: uuid.UUID
    usage_date: datetime
    performed_by_user_id: uuid.UUID
    service_type: Optional[str]
    machine_hours: Optional[Decimal]
    notes: Optional[str]
    reference_number: Optional[str]
    created_at: datetime
    
    # Usage items
    usage_items: List[PartUsageItemResponse] = []
    
    # Include related data
    machine_serial: Optional[str] = None
    machine_name: Optional[str] = None
    from_warehouse_name: Optional[str] = None
    performed_by_username: Optional[str] = None
    total_items: Optional[int] = None

    class Config:
        from_attributes = True