# backend/app/schemas/warehouse.py

import uuid
from datetime import datetime
from typing import Optional, List
from decimal import Decimal
from pydantic import BaseModel, Field

class BaseSchema(BaseModel):
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    class Config:
        from_attributes = True # Allow ORM models to be converted to Pydantic models

class WarehouseBase(BaseModel):
    organization_id: uuid.UUID
    name: str = Field(..., max_length=255)
    location: Optional[str] = Field(None, max_length=500)
    description: Optional[str] = None
    is_active: bool = True

class WarehouseCreate(WarehouseBase):
    pass

class WarehouseUpdate(BaseModel):
    organization_id: Optional[uuid.UUID] = None
    name: Optional[str] = Field(None, max_length=255)
    location: Optional[str] = Field(None, max_length=500)
    description: Optional[str] = None
    is_active: Optional[bool] = None

class WarehouseResponse(WarehouseBase, BaseSchema):
    """Response schema for warehouse endpoints"""
    class Config:
        from_attributes = True


# --- Warehouse Analytics Schemas ---
class WarehouseAnalyticsRequest(BaseModel):
    """Request schema for warehouse analytics with optional date filtering"""
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    days: int = Field(default=30, ge=1, le=365, description="Number of days to include in analytics (1-365)")

class InventorySummary(BaseModel):
    """Schema for inventory summary metrics"""
    total_parts: int = Field(description="Total number of different parts in warehouse")
    total_value: Decimal = Field(decimal_places=2, description="Total monetary value of inventory")
    low_stock_parts: int = Field(description="Number of parts below minimum stock threshold")
    out_of_stock_parts: int = Field(description="Number of parts with zero stock")

class TopPartByValue(BaseModel):
    """Schema for top parts by value information"""
    part_id: uuid.UUID
    part_name: str = Field(max_length=255)
    quantity: Decimal = Field(decimal_places=3, description="Current stock quantity")
    unit_price: Decimal = Field(decimal_places=2, description="Price per unit")
    total_value: Decimal = Field(decimal_places=2, description="Total value (quantity * unit_price)")

class StockMovements(BaseModel):
    """Schema for stock movement metrics"""
    total_inbound: Decimal = Field(decimal_places=3, description="Total quantity received")
    total_outbound: Decimal = Field(decimal_places=3, description="Total quantity consumed/shipped")
    net_change: Decimal = Field(decimal_places=3, description="Net change in stock levels")

class TurnoverMetrics(BaseModel):
    """Schema for inventory turnover metrics"""
    average_turnover_days: Decimal = Field(decimal_places=2, description="Average days for inventory turnover")
    fast_moving_parts: int = Field(description="Number of parts with high turnover")
    slow_moving_parts: int = Field(description="Number of parts with low turnover")

class AnalyticsPeriod(BaseModel):
    """Schema for analytics time period information"""
    start_date: datetime
    end_date: datetime
    days: int

class WarehouseAnalyticsResponse(BaseModel):
    """Response schema for comprehensive warehouse analytics"""
    warehouse_id: uuid.UUID
    warehouse_name: str = Field(max_length=255)
    analytics_period: AnalyticsPeriod
    inventory_summary: InventorySummary
    top_parts_by_value: List[TopPartByValue] = Field(default_factory=list, description="Top 10 parts by total value")
    stock_movements: StockMovements
    turnover_metrics: TurnoverMetrics

class TrendDataPoint(BaseModel):
    """Schema for individual trend data points"""
    date: datetime
    total_value: Decimal = Field(decimal_places=2, description="Total inventory value on this date")
    total_quantity: Decimal = Field(decimal_places=3, description="Total inventory quantity on this date")
    parts_count: int = Field(description="Number of different parts on this date")
    transactions_count: int = Field(description="Number of transactions on this date")

class WarehouseAnalyticsTrendsResponse(BaseModel):
    """Response schema for warehouse analytics trend data"""
    warehouse_id: uuid.UUID
    period: str = Field(description="Aggregation period: daily, weekly, or monthly")
    trends: List[TrendDataPoint] = Field(default_factory=list, description="Time series data points")