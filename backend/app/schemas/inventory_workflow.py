# backend/app/schemas/inventory_workflow.py

import uuid
from typing import Optional, List, Dict, Any
from decimal import Decimal
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field

# Enums for inventory workflows
class StocktakeStatusEnum(str, Enum):
    PLANNED = "planned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class InventoryAlertTypeEnum(str, Enum):
    LOW_STOCK = "low_stock"
    STOCKOUT = "stockout"
    EXPIRING = "expiring"
    EXPIRED = "expired"
    EXCESS = "excess"
    DISCREPANCY = "discrepancy"

class InventoryAlertSeverityEnum(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

# Stocktake Schemas
class StocktakeBase(BaseModel):
    warehouse_id: uuid.UUID
    scheduled_date: datetime
    notes: Optional[str] = None

class StocktakeCreate(StocktakeBase):
    scheduled_by_user_id: Optional[uuid.UUID] = None  # Will be set to current user if not provided

class StocktakeUpdate(BaseModel):
    scheduled_date: Optional[datetime] = None
    status: Optional[StocktakeStatusEnum] = None
    notes: Optional[str] = None
    completed_date: Optional[datetime] = None
    completed_by_user_id: Optional[uuid.UUID] = None

class StocktakeResponse(StocktakeBase):
    id: uuid.UUID
    status: StocktakeStatusEnum
    scheduled_by_user_id: uuid.UUID
    completed_date: Optional[datetime] = None
    completed_by_user_id: Optional[uuid.UUID] = None
    created_at: datetime
    updated_at: datetime
    
    # Related data
    warehouse_name: str
    warehouse_location: str
    organization_id: uuid.UUID
    organization_name: str
    scheduled_by_username: str
    completed_by_username: Optional[str] = None
    total_items: int
    items_counted: int
    discrepancy_count: int
    total_discrepancy_value: Optional[Decimal] = None
    items: List["StocktakeItemResponse"] = []

    class Config:
        from_attributes = True

# Stocktake Item Schemas
class StocktakeItemBase(BaseModel):
    stocktake_id: uuid.UUID
    part_id: uuid.UUID
    expected_quantity: Decimal
    actual_quantity: Optional[Decimal] = None
    notes: Optional[str] = None

class StocktakeItemCreate(StocktakeItemBase):
    pass

class StocktakeItemUpdate(BaseModel):
    actual_quantity: Decimal
    notes: Optional[str] = None

class StocktakeItemResponse(StocktakeItemBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    counted_at: Optional[datetime] = None
    counted_by_user_id: Optional[uuid.UUID] = None
    discrepancy: Optional[Decimal] = None
    discrepancy_percentage: Optional[float] = None
    
    # Related data
    part_number: str
    part_name: str
    part_type: str
    unit_of_measure: str
    unit_price: Optional[Decimal] = None
    discrepancy_value: Optional[Decimal] = None
    counted_by_username: Optional[str] = None

    class Config:
        from_attributes = True

# Inventory Alert Schemas
class InventoryAlertBase(BaseModel):
    warehouse_id: uuid.UUID
    part_id: uuid.UUID
    alert_type: InventoryAlertTypeEnum
    severity: InventoryAlertSeverityEnum
    threshold_value: Optional[Decimal] = None
    current_value: Decimal
    message: str
    is_active: bool = True

class InventoryAlertCreate(InventoryAlertBase):
    pass

class InventoryAlertUpdate(BaseModel):
    severity: Optional[InventoryAlertSeverityEnum] = None
    current_value: Optional[Decimal] = None
    message: Optional[str] = None
    is_active: Optional[bool] = None
    resolved_by_user_id: Optional[uuid.UUID] = None
    resolution_notes: Optional[str] = None

class InventoryAlertResponse(InventoryAlertBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    resolved_at: Optional[datetime] = None
    resolved_by_user_id: Optional[uuid.UUID] = None
    resolution_notes: Optional[str] = None
    
    # Related data
    warehouse_name: str
    organization_id: uuid.UUID
    organization_name: str
    part_number: str
    part_name: str
    part_type: str
    unit_of_measure: str
    resolved_by_username: Optional[str] = None

    class Config:
        from_attributes = True

# Inventory Adjustment Schemas
class InventoryAdjustmentBase(BaseModel):
    warehouse_id: uuid.UUID
    part_id: uuid.UUID
    quantity_change: Decimal
    reason: str
    notes: Optional[str] = None
    stocktake_id: Optional[uuid.UUID] = None

class InventoryAdjustmentCreate(InventoryAdjustmentBase):
    adjusted_by_user_id: Optional[uuid.UUID] = None  # Will be set to current user if not provided

class InventoryAdjustmentResponse(InventoryAdjustmentBase):
    id: uuid.UUID
    adjusted_by_user_id: uuid.UUID
    adjustment_date: datetime
    created_at: datetime
    
    # Related data
    warehouse_name: str
    organization_id: uuid.UUID
    organization_name: str
    part_number: str
    part_name: str
    part_type: str
    unit_of_measure: str
    adjusted_by_username: str
    previous_quantity: Decimal
    new_quantity: Decimal
    transaction_id: Optional[uuid.UUID] = None

    class Config:
        from_attributes = True

# Batch Operations
class BatchStocktakeItemUpdate(BaseModel):
    items: List[Dict[str, Any]]  # List of {item_id, actual_quantity, notes}

class BatchInventoryAdjustment(BaseModel):
    warehouse_id: uuid.UUID
    adjustments: List[Dict[str, Any]]  # List of {part_id, quantity_change, reason, notes}

# Inventory Analytics
class InventoryAnalyticsRequest(BaseModel):
    organization_id: Optional[uuid.UUID] = None
    warehouse_id: Optional[uuid.UUID] = None
    part_type: Optional[str] = None
    days: int = 30

class InventoryAnalytics(BaseModel):
    total_inventory_value: Decimal
    total_parts_count: int
    low_stock_count: int
    stockout_count: int
    excess_stock_count: int
    inventory_by_part_type: Dict[str, Dict[str, Any]]
    inventory_by_warehouse: Dict[str, Dict[str, Any]]
    top_moving_parts: List[Dict[str, Any]]
    slow_moving_parts: List[Dict[str, Any]]
    recent_adjustments: List[Dict[str, Any]]
    stocktake_accuracy: Optional[float] = None

# Update forward references
StocktakeResponse.model_rebuild()