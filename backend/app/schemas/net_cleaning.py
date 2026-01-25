# backend/app/schemas/net_cleaning.py

from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
from decimal import Decimal
from uuid import UUID


# Farm Site Schemas
class FarmSiteBase(BaseModel):
    name: str = Field(..., max_length=200, description="Farm site name")
    location: Optional[str] = Field(None, max_length=500, description="GPS coordinates or address")
    description: Optional[str] = Field(None, description="Additional details about the farm site")
    active: bool = Field(True, description="Whether the farm site is active")


class FarmSiteCreate(FarmSiteBase):
    pass


class FarmSiteUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=200)
    location: Optional[str] = Field(None, max_length=500)
    description: Optional[str] = None
    active: Optional[bool] = None


class FarmSiteResponse(FarmSiteBase):
    id: UUID
    organization_id: UUID
    created_at: datetime
    updated_at: datetime
    nets_count: Optional[int] = Field(None, description="Number of nets at this site")

    class Config:
        from_attributes = True


class FarmSiteWithNets(FarmSiteResponse):
    nets: List['NetResponse'] = []

    class Config:
        from_attributes = True


# Net Schemas
class NetBase(BaseModel):
    farm_site_id: UUID = Field(..., description="Farm site where this net is located")
    name: str = Field(..., max_length=200, description="Net or cage identifier")
    diameter: Optional[Decimal] = Field(None, ge=0, description="Net diameter in meters")
    vertical_depth: Optional[Decimal] = Field(None, ge=0, description="Vertical depth in meters")
    cone_depth: Optional[Decimal] = Field(None, ge=0, description="Cone depth in meters")
    mesh_size: Optional[str] = Field(None, max_length=50, description="Mesh size (e.g., '22mm')")
    material: Optional[str] = Field(None, max_length=100, description="Net material (e.g., 'Nylon')")
    notes: Optional[str] = None
    active: bool = Field(True, description="Whether the net is active")


class NetCreate(NetBase):
    pass


class NetUpdate(BaseModel):
    farm_site_id: Optional[UUID] = None
    name: Optional[str] = Field(None, max_length=200)
    diameter: Optional[Decimal] = Field(None, ge=0)
    vertical_depth: Optional[Decimal] = Field(None, ge=0)
    cone_depth: Optional[Decimal] = Field(None, ge=0)
    mesh_size: Optional[str] = Field(None, max_length=50)
    material: Optional[str] = Field(None, max_length=100)
    notes: Optional[str] = None
    active: Optional[bool] = None


class NetResponse(NetBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
    cleaning_records_count: Optional[int] = Field(None, description="Number of cleaning records")
    last_cleaning_date: Optional[datetime] = Field(None, description="Date of last cleaning")

    class Config:
        from_attributes = True


class NetWithCleaningHistory(NetResponse):
    cleaning_records: List['NetCleaningRecordResponse'] = []

    class Config:
        from_attributes = True


# Net Cleaning Record Schemas
class NetCleaningRecordBase(BaseModel):
    net_id: UUID = Field(..., description="Net that was cleaned")
    machine_id: Optional[UUID] = Field(None, description="Machine used for cleaning")
    operator_name: str = Field(..., max_length=200, description="Name of the operator")
    cleaning_mode: int = Field(..., ge=1, le=3, description="Cleaning mode (1, 2, or 3)")
    depth_1: Optional[Decimal] = Field(None, ge=0, description="First depth in meters")
    depth_2: Optional[Decimal] = Field(None, ge=0, description="Second depth in meters")
    depth_3: Optional[Decimal] = Field(None, ge=0, description="Third depth in meters")
    start_time: datetime = Field(..., description="Cleaning start time")
    end_time: Optional[datetime] = Field(None, description="Cleaning end time (optional for incomplete records)")
    notes: Optional[str] = None
    status: Optional[str] = Field("completed", description="Status: 'in_progress' or 'completed'")

    @validator('end_time')
    def validate_end_time(cls, v, values):
        if v is not None and 'start_time' in values and v <= values['start_time']:
            raise ValueError('End time must be after start time')
        return v

    @validator('depth_1')
    def validate_depth_1(cls, v, values):
        if 'cleaning_mode' in values and values['cleaning_mode'] >= 1 and v is None:
            raise ValueError('Depth 1 is required for cleaning mode 1, 2, and 3')
        return v

    @validator('depth_2')
    def validate_depth_2(cls, v, values):
        if 'cleaning_mode' in values and values['cleaning_mode'] >= 2 and v is None:
            raise ValueError('Depth 2 is required for cleaning mode 2 and 3')
        return v

    @validator('depth_3')
    def validate_depth_3(cls, v, values):
        if 'cleaning_mode' in values and values['cleaning_mode'] == 3 and v is None:
            raise ValueError('Depth 3 is required for cleaning mode 3')
        return v


class NetCleaningRecordCreate(NetCleaningRecordBase):
    pass


class NetCleaningRecordUpdate(BaseModel):
    net_id: Optional[UUID] = None
    machine_id: Optional[UUID] = None
    operator_name: Optional[str] = Field(None, max_length=200)
    cleaning_mode: Optional[int] = Field(None, ge=1, le=3)
    depth_1: Optional[Decimal] = Field(None, ge=0)
    depth_2: Optional[Decimal] = Field(None, ge=0)
    depth_3: Optional[Decimal] = Field(None, ge=0)
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    notes: Optional[str] = None


class NetCleaningRecordResponse(NetCleaningRecordBase):
    id: UUID
    duration_minutes: Optional[int] = Field(None, description="Cleaning duration in minutes")
    created_by: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class NetCleaningRecordWithDetails(NetCleaningRecordResponse):
    net_name: Optional[str] = Field(None, description="Name of the net")
    farm_site_name: Optional[str] = Field(None, description="Name of the farm site")
    machine_name: Optional[str] = Field(None, description="Name of the machine")
    created_by_username: Optional[str] = Field(None, description="Username of creator")

    class Config:
        from_attributes = True


# Statistics Schemas
class NetCleaningStats(BaseModel):
    total_cleanings: int
    total_duration_minutes: int
    average_duration_minutes: float
    cleanings_by_mode: dict
    cleanings_by_operator: dict
    most_cleaned_nets: List[dict]


# Update forward references
FarmSiteWithNets.model_rebuild()
NetWithCleaningHistory.model_rebuild()
