# backend/app/schemas/predictive_maintenance.py

from typing import List, Optional, Dict, Any, Union
from datetime import datetime
import uuid
from enum import Enum
from pydantic import BaseModel, Field

# Enums
class MaintenanceRiskLevelEnum(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class MaintenancePriorityEnum(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

class MaintenanceStatusEnum(str, Enum):
    PENDING = "pending"
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class MaintenanceTypeEnum(str, Enum):
    SCHEDULED = "scheduled"
    UNSCHEDULED = "unscheduled"
    REPAIR = "repair"
    INSPECTION = "inspection"
    CLEANING = "cleaning"
    CALIBRATION = "calibration"
    OTHER = "other"

# Base Models
class PredictiveMaintenanceModelBase(BaseModel):
    name: str
    description: Optional[str] = None
    model_type: str
    target_metric: str
    features: List[str]
    hyperparameters: Optional[Dict[str, Any]] = None
    version: str
    is_active: bool = True

class PredictiveMaintenanceModelCreate(PredictiveMaintenanceModelBase):
    created_by_user_id: uuid.UUID

class PredictiveMaintenanceModelUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    hyperparameters: Optional[Dict[str, Any]] = None
    performance_metrics: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None

class PredictiveMaintenanceModelResponse(PredictiveMaintenanceModelBase):
    id: uuid.UUID
    performance_metrics: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime
    created_by_user_id: uuid.UUID

    class Config:
        from_attributes = True

class MachineModelAssociationBase(BaseModel):
    predictive_model_id: uuid.UUID
    machine_model_type: str
    is_active: bool = True

class MachineModelAssociationCreate(MachineModelAssociationBase):
    pass

class MachineModelAssociationUpdate(BaseModel):
    is_active: Optional[bool] = None

class MachineModelAssociationResponse(MachineModelAssociationBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class MachinePredictionBase(BaseModel):
    machine_id: uuid.UUID
    predictive_model_id: uuid.UUID
    failure_probability: Optional[float] = None
    remaining_useful_life: Optional[int] = None
    predicted_failure_date: Optional[datetime] = None
    risk_level: MaintenanceRiskLevelEnum
    prediction_details: Optional[Dict[str, Any]] = None

class MachinePredictionCreate(MachinePredictionBase):
    pass

class MachinePredictionResponse(MachinePredictionBase):
    id: uuid.UUID
    prediction_date: datetime
    created_at: datetime
    machine_serial_number: str
    machine_model_type: str
    model_name: str

    class Config:
        from_attributes = True

class MaintenanceRecommendationBase(BaseModel):
    machine_id: uuid.UUID
    prediction_id: uuid.UUID
    recommended_maintenance_type: MaintenanceTypeEnum
    priority: MaintenancePriorityEnum
    recommended_completion_date: datetime
    description: str
    status: MaintenanceStatusEnum = MaintenanceStatusEnum.PENDING

class MaintenanceRecommendationCreate(MaintenanceRecommendationBase):
    pass

class MaintenanceRecommendationUpdate(BaseModel):
    recommended_maintenance_type: Optional[MaintenanceTypeEnum] = None
    priority: Optional[MaintenancePriorityEnum] = None
    recommended_completion_date: Optional[datetime] = None
    description: Optional[str] = None
    status: Optional[MaintenanceStatusEnum] = None
    resolved_by_maintenance_id: Optional[uuid.UUID] = None

class MaintenanceRecommendationResponse(MaintenanceRecommendationBase):
    id: uuid.UUID
    recommendation_date: datetime
    resolved_by_maintenance_id: Optional[uuid.UUID] = None
    created_at: datetime
    updated_at: datetime
    machine_serial_number: str
    machine_model_type: str
    risk_level: MaintenanceRiskLevelEnum
    recommended_parts: List["RecommendedPartResponse"] = []

    class Config:
        from_attributes = True

class RecommendedPartBase(BaseModel):
    recommendation_id: uuid.UUID
    part_id: uuid.UUID
    quantity: float
    reason: Optional[str] = None

class RecommendedPartCreate(RecommendedPartBase):
    pass

class RecommendedPartResponse(RecommendedPartBase):
    id: uuid.UUID
    created_at: datetime
    part_number: str
    part_name: str

    class Config:
        from_attributes = True

class MaintenanceIndicatorBase(BaseModel):
    name: str
    description: Optional[str] = None
    indicator_type: str
    unit_of_measure: Optional[str] = None
    threshold_warning: Optional[float] = None
    threshold_critical: Optional[float] = None
    is_active: bool = True

class MaintenanceIndicatorCreate(MaintenanceIndicatorBase):
    pass

class MaintenanceIndicatorUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    threshold_warning: Optional[float] = None
    threshold_critical: Optional[float] = None
    is_active: Optional[bool] = None

class MaintenanceIndicatorResponse(MaintenanceIndicatorBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class MachineIndicatorValueBase(BaseModel):
    machine_id: uuid.UUID
    indicator_id: uuid.UUID
    value: float
    recorded_at: datetime
    recorded_by_user_id: Optional[uuid.UUID] = None
    notes: Optional[str] = None

class MachineIndicatorValueCreate(MachineIndicatorValueBase):
    pass

class MachineIndicatorValueResponse(MachineIndicatorValueBase):
    id: uuid.UUID
    created_at: datetime
    indicator_name: str
    indicator_type: str
    unit_of_measure: Optional[str] = None
    machine_serial_number: str
    machine_model_type: str
    recorded_by_username: Optional[str] = None
    status: str  # "normal", "warning", "critical" based on thresholds

    class Config:
        from_attributes = True

# Update MaintenanceRecommendationResponse to reference RecommendedPartResponse
MaintenanceRecommendationResponse.update_forward_refs()

# Prediction Request Models
class PredictionRequest(BaseModel):
    machine_id: uuid.UUID
    indicators: Dict[str, float]  # indicator_name: value
    additional_data: Optional[Dict[str, Any]] = None

class PredictionResponse(BaseModel):
    prediction_id: uuid.UUID
    machine_id: uuid.UUID
    machine_serial_number: str
    machine_model_type: str
    failure_probability: float
    remaining_useful_life: Optional[int] = None
    predicted_failure_date: Optional[datetime] = None
    risk_level: MaintenanceRiskLevelEnum
    recommendation_id: Optional[uuid.UUID] = None
    recommendation_details: Optional[Dict[str, Any]] = None

# Batch Models
class BatchPredictionRequest(BaseModel):
    machine_ids: List[uuid.UUID]

class BatchIndicatorUpload(BaseModel):
    machine_id: uuid.UUID
    indicator_values: List[Dict[str, Any]]  # List of indicator values with names and values

# Dashboard Models
class MaintenanceRiskSummary(BaseModel):
    total_machines: int
    low_risk: int
    medium_risk: int
    high_risk: int
    critical_risk: int
    pending_recommendations: int
    scheduled_maintenance: int
    overdue_maintenance: int

class MachinePredictionTrend(BaseModel):
    machine_id: uuid.UUID
    machine_serial_number: str
    machine_model_type: str
    predictions: List[Dict[str, Any]]  # List of predictions over time
    indicators: List[Dict[str, Any]]  # List of indicator values over time

class MaintenanceEffectivenessMetrics(BaseModel):
    total_recommendations: int
    completed_recommendations: int
    cancelled_recommendations: int
    average_time_to_resolution: float  # in days
    prevented_failures: int
    cost_savings: float