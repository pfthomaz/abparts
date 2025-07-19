# backend/app/routers/predictive_maintenance.py

import uuid
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from .. import schemas, models
from ..database import get_db
from ..auth import get_current_user, TokenData
from ..permissions import (
    ResourceType, PermissionType, require_permission, require_super_admin,
    OrganizationScopedQueries, check_organization_access, permission_checker
)
from ..crud import predictive_maintenance as crud

router = APIRouter()

# Predictive Maintenance Models
@router.get("/models", response_model=List[schemas.PredictiveMaintenanceModelResponse])
async def get_predictive_models(
    active_only: bool = Query(False, description="Filter to only active models"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(require_permission(ResourceType.MACHINE, PermissionType.READ))
):
    """
    Get all predictive maintenance models.
    Only super admins can access this endpoint.
    """
    if not permission_checker.is_super_admin(current_user):
        raise HTTPException(status_code=403, detail="Only super admins can access predictive maintenance models")
    
    models = crud.get_predictive_models(db, skip, limit, active_only)
    return models

@router.get("/models/{model_id}", response_model=schemas.PredictiveMaintenanceModelResponse)
async def get_predictive_model(
    model_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(require_permission(ResourceType.MACHINE, PermissionType.READ))
):
    """
    Get a specific predictive maintenance model by ID.
    Only super admins can access this endpoint.
    """
    if not permission_checker.is_super_admin(current_user):
        raise HTTPException(status_code=403, detail="Only super admins can access predictive maintenance models")
    
    model = crud.get_predictive_model(db, model_id)
    if not model:
        raise HTTPException(status_code=404, detail="Predictive maintenance model not found")
    
    return model

@router.post("/models", response_model=schemas.PredictiveMaintenanceModelResponse, status_code=status.HTTP_201_CREATED)
async def create_predictive_model(
    model: schemas.PredictiveMaintenanceModelCreate,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(require_permission(ResourceType.MACHINE, PermissionType.WRITE))
):
    """
    Create a new predictive maintenance model.
    Only super admins can access this endpoint.
    """
    if not permission_checker.is_super_admin(current_user):
        raise HTTPException(status_code=403, detail="Only super admins can create predictive maintenance models")
    
    # Set the current user as the creator if not provided
    if not model.created_by_user_id:
        model.created_by_user_id = current_user.user_id
    
    return crud.create_predictive_model(db, model)

@router.put("/models/{model_id}", response_model=schemas.PredictiveMaintenanceModelResponse)
async def update_predictive_model(
    model_id: uuid.UUID,
    model_update: schemas.PredictiveMaintenanceModelUpdate,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(require_permission(ResourceType.MACHINE, PermissionType.WRITE))
):
    """
    Update a predictive maintenance model.
    Only super admins can access this endpoint.
    """
    if not permission_checker.is_super_admin(current_user):
        raise HTTPException(status_code=403, detail="Only super admins can update predictive maintenance models")
    
    updated_model = crud.update_predictive_model(db, model_id, model_update)
    if not updated_model:
        raise HTTPException(status_code=404, detail="Predictive maintenance model not found")
    
    return updated_model

@router.delete("/models/{model_id}")
async def delete_predictive_model(
    model_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(require_permission(ResourceType.MACHINE, PermissionType.DELETE))
):
    """
    Delete a predictive maintenance model.
    Only super admins can access this endpoint.
    """
    if not permission_checker.is_super_admin(current_user):
        raise HTTPException(status_code=403, detail="Only super admins can delete predictive maintenance models")
    
    result = crud.delete_predictive_model(db, model_id)
    if not result:
        raise HTTPException(status_code=404, detail="Predictive maintenance model not found")
    
    return result

# Machine Model Associations
@router.get("/model-associations", response_model=List[schemas.MachineModelAssociationResponse])
async def get_machine_model_associations(
    predictive_model_id: Optional[uuid.UUID] = Query(None, description="Filter by predictive model ID"),
    machine_model_type: Optional[str] = Query(None, description="Filter by machine model type"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(require_permission(ResourceType.MACHINE, PermissionType.READ))
):
    """
    Get machine model associations.
    Only super admins can access this endpoint.
    """
    if not permission_checker.is_super_admin(current_user):
        raise HTTPException(status_code=403, detail="Only super admins can access machine model associations")
    
    associations = crud.get_machine_model_associations(db, predictive_model_id, machine_model_type, skip, limit)
    return associations

@router.post("/model-associations", response_model=schemas.MachineModelAssociationResponse, status_code=status.HTTP_201_CREATED)
async def create_machine_model_association(
    association: schemas.MachineModelAssociationCreate,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(require_permission(ResourceType.MACHINE, PermissionType.WRITE))
):
    """
    Create a new machine model association.
    Only super admins can access this endpoint.
    """
    if not permission_checker.is_super_admin(current_user):
        raise HTTPException(status_code=403, detail="Only super admins can create machine model associations")
    
    return crud.create_machine_model_association(db, association)

@router.put("/model-associations/{association_id}", response_model=schemas.MachineModelAssociationResponse)
async def update_machine_model_association(
    association_id: uuid.UUID,
    association_update: schemas.MachineModelAssociationUpdate,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(require_permission(ResourceType.MACHINE, PermissionType.WRITE))
):
    """
    Update a machine model association.
    Only super admins can access this endpoint.
    """
    if not permission_checker.is_super_admin(current_user):
        raise HTTPException(status_code=403, detail="Only super admins can update machine model associations")
    
    updated_association = crud.update_machine_model_association(db, association_id, association_update)
    if not updated_association:
        raise HTTPException(status_code=404, detail="Machine model association not found")
    
    return updated_association

@router.delete("/model-associations/{association_id}")
async def delete_machine_model_association(
    association_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(require_permission(ResourceType.MACHINE, PermissionType.DELETE))
):
    """
    Delete a machine model association.
    Only super admins can access this endpoint.
    """
    if not permission_checker.is_super_admin(current_user):
        raise HTTPException(status_code=403, detail="Only super admins can delete machine model associations")
    
    result = crud.delete_machine_model_association(db, association_id)
    if not result:
        raise HTTPException(status_code=404, detail="Machine model association not found")
    
    return result

# Machine Predictions
@router.get("/predictions", response_model=List[schemas.MachinePredictionResponse])
async def get_machine_predictions(
    machine_id: Optional[uuid.UUID] = Query(None, description="Filter by machine ID"),
    risk_level: Optional[schemas.MaintenanceRiskLevelEnum] = Query(None, description="Filter by risk level"),
    days: Optional[int] = Query(None, ge=1, description="Filter by predictions made within the last X days"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(require_permission(ResourceType.MACHINE, PermissionType.READ))
):
    """
    Get machine predictions with optional filtering.
    Users can only view predictions for machines owned by their organization.
    """
    # If machine_id is provided, check if user has access to the machine
    if machine_id:
        machine = db.query(models.Machine).filter(models.Machine.id == machine_id).first()
        if not machine:
            raise HTTPException(status_code=404, detail="Machine not found")
        
        if not check_organization_access(current_user, machine.customer_organization_id, db):
            raise HTTPException(status_code=403, detail="Not authorized to view predictions for this machine")
    
    # If no machine_id is provided and user is not super_admin, filter by organization
    elif not permission_checker.is_super_admin(current_user):
        # Get all machines for the user's organization
        machines = db.query(models.Machine).filter(
            models.Machine.customer_organization_id == current_user.organization_id
        ).all()
        
        if not machines:
            return []
        
        # Get predictions for these machines
        predictions = []
        for machine in machines:
            machine_predictions = crud.get_machine_predictions(db, machine.id, risk_level, days, 0, limit)
            predictions.extend(machine_predictions)
            if len(predictions) >= limit:
                predictions = predictions[:limit]
                break
        
        return predictions
    
    # Otherwise, get predictions with the provided filters
    predictions = crud.get_machine_predictions(db, machine_id, risk_level, days, skip, limit)
    return predictions

@router.get("/predictions/{prediction_id}", response_model=schemas.MachinePredictionResponse)
async def get_machine_prediction(
    prediction_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(require_permission(ResourceType.MACHINE, PermissionType.READ))
):
    """
    Get a specific machine prediction by ID.
    Users can only view predictions for machines owned by their organization.
    """
    prediction = crud.get_machine_prediction(db, prediction_id)
    if not prediction:
        raise HTTPException(status_code=404, detail="Machine prediction not found")
    
    # Check if user has access to the machine
    machine = db.query(models.Machine).filter(models.Machine.id == prediction["machine_id"]).first()
    if not check_organization_access(current_user, machine.customer_organization_id, db):
        raise HTTPException(status_code=403, detail="Not authorized to view this prediction")
    
    return prediction

@router.post("/predictions", response_model=schemas.PredictionResponse)
async def create_prediction(
    request: schemas.PredictionRequest,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(require_permission(ResourceType.MACHINE, PermissionType.WRITE))
):
    """
    Generate a prediction for a machine based on indicator values.
    Users can only create predictions for machines owned by their organization.
    """
    # Check if user has access to the machine
    machine = db.query(models.Machine).filter(models.Machine.id == request.machine_id).first()
    if not machine:
        raise HTTPException(status_code=404, detail="Machine not found")
    
    if not check_organization_access(current_user, machine.customer_organization_id, db):
        raise HTTPException(status_code=403, detail="Not authorized to create predictions for this machine")
    
    return crud.generate_machine_prediction(db, request)

@router.post("/batch-predictions", response_model=List[Dict[str, Any]])
async def batch_create_predictions(
    request: schemas.BatchPredictionRequest,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(require_permission(ResourceType.MACHINE, PermissionType.WRITE))
):
    """
    Generate predictions for multiple machines.
    Users can only create predictions for machines owned by their organization.
    """
    # Check if user has access to all machines
    for machine_id in request.machine_ids:
        machine = db.query(models.Machine).filter(models.Machine.id == machine_id).first()
        if not machine:
            raise HTTPException(status_code=404, detail=f"Machine with ID {machine_id} not found")
        
        if not check_organization_access(current_user, machine.customer_organization_id, db):
            raise HTTPException(status_code=403, detail=f"Not authorized to create predictions for machine with ID {machine_id}")
    
    return crud.batch_generate_predictions(db, request)

@router.delete("/predictions/{prediction_id}")
async def delete_machine_prediction(
    prediction_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(require_permission(ResourceType.MACHINE, PermissionType.DELETE))
):
    """
    Delete a machine prediction.
    Only super admins can delete predictions.
    """
    if not permission_checker.is_super_admin(current_user):
        raise HTTPException(status_code=403, detail="Only super admins can delete machine predictions")
    
    result = crud.delete_machine_prediction(db, prediction_id)
    if not result:
        raise HTTPException(status_code=404, detail="Machine prediction not found")
    
    return result

# Maintenance Recommendations
@router.get("/recommendations", response_model=List[schemas.MaintenanceRecommendationResponse])
async def get_maintenance_recommendations(
    machine_id: Optional[uuid.UUID] = Query(None, description="Filter by machine ID"),
    status: Optional[schemas.MaintenanceStatusEnum] = Query(None, description="Filter by status"),
    priority: Optional[schemas.MaintenancePriorityEnum] = Query(None, description="Filter by priority"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(require_permission(ResourceType.MACHINE, PermissionType.READ))
):
    """
    Get maintenance recommendations with optional filtering.
    Users can only view recommendations for machines owned by their organization.
    """
    # If machine_id is provided, check if user has access to the machine
    if machine_id:
        machine = db.query(models.Machine).filter(models.Machine.id == machine_id).first()
        if not machine:
            raise HTTPException(status_code=404, detail="Machine not found")
        
        if not check_organization_access(current_user, machine.customer_organization_id, db):
            raise HTTPException(status_code=403, detail="Not authorized to view recommendations for this machine")
    
    # If no machine_id is provided and user is not super_admin, filter by organization
    elif not permission_checker.is_super_admin(current_user):
        # Get all machines for the user's organization
        machines = db.query(models.Machine).filter(
            models.Machine.customer_organization_id == current_user.organization_id
        ).all()
        
        if not machines:
            return []
        
        # Get recommendations for these machines
        recommendations = []
        for machine in machines:
            machine_recommendations = crud.get_maintenance_recommendations(db, machine.id, status, priority, 0, limit)
            recommendations.extend(machine_recommendations)
            if len(recommendations) >= limit:
                recommendations = recommendations[:limit]
                break
        
        return recommendations
    
    # Otherwise, get recommendations with the provided filters
    recommendations = crud.get_maintenance_recommendations(db, machine_id, status, priority, skip, limit)
    return recommendations

@router.get("/recommendations/{recommendation_id}", response_model=schemas.MaintenanceRecommendationResponse)
async def get_maintenance_recommendation(
    recommendation_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(require_permission(ResourceType.MACHINE, PermissionType.READ))
):
    """
    Get a specific maintenance recommendation by ID.
    Users can only view recommendations for machines owned by their organization.
    """
    recommendation = crud.get_maintenance_recommendation(db, recommendation_id)
    if not recommendation:
        raise HTTPException(status_code=404, detail="Maintenance recommendation not found")
    
    # Check if user has access to the machine
    machine = db.query(models.Machine).filter(models.Machine.id == recommendation["machine_id"]).first()
    if not check_organization_access(current_user, machine.customer_organization_id, db):
        raise HTTPException(status_code=403, detail="Not authorized to view this recommendation")
    
    return recommendation

@router.put("/recommendations/{recommendation_id}", response_model=schemas.MaintenanceRecommendationResponse)
async def update_maintenance_recommendation(
    recommendation_id: uuid.UUID,
    recommendation_update: schemas.MaintenanceRecommendationUpdate,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(require_permission(ResourceType.MACHINE, PermissionType.WRITE))
):
    """
    Update a maintenance recommendation.
    Users can only update recommendations for machines owned by their organization.
    """
    # Check if recommendation exists
    recommendation = crud.get_maintenance_recommendation(db, recommendation_id)
    if not recommendation:
        raise HTTPException(status_code=404, detail="Maintenance recommendation not found")
    
    # Check if user has access to the machine
    machine = db.query(models.Machine).filter(models.Machine.id == recommendation["machine_id"]).first()
    if not check_organization_access(current_user, machine.customer_organization_id, db):
        raise HTTPException(status_code=403, detail="Not authorized to update this recommendation")
    
    updated_recommendation = crud.update_maintenance_recommendation(db, recommendation_id, recommendation_update)
    return updated_recommendation

@router.delete("/recommendations/{recommendation_id}")
async def delete_maintenance_recommendation(
    recommendation_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(require_permission(ResourceType.MACHINE, PermissionType.DELETE))
):
    """
    Delete a maintenance recommendation.
    Only super admins can delete recommendations.
    """
    if not permission_checker.is_super_admin(current_user):
        raise HTTPException(status_code=403, detail="Only super admins can delete maintenance recommendations")
    
    result = crud.delete_maintenance_recommendation(db, recommendation_id)
    if not result:
        raise HTTPException(status_code=404, detail="Maintenance recommendation not found")
    
    return result

# Analytics
@router.get("/analytics/risk-summary", response_model=schemas.MaintenanceRiskSummary)
async def get_maintenance_risk_summary(
    organization_id: Optional[uuid.UUID] = Query(None, description="Filter by organization ID"),
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(require_permission(ResourceType.MACHINE, PermissionType.READ))
):
    """
    Get a summary of maintenance risks across machines.
    Users can only view data for their organization.
    """
    # If organization_id is provided, check if user has access to it
    if organization_id:
        if not check_organization_access(current_user, organization_id, db):
            raise HTTPException(status_code=403, detail="Not authorized to view data for this organization")
    
    # If no organization_id is provided and user is not super_admin, use their organization
    elif not permission_checker.is_super_admin(current_user):
        organization_id = current_user.organization_id
    
    return crud.get_maintenance_risk_summary(db, organization_id)

@router.get("/analytics/machine-prediction-trend/{machine_id}", response_model=schemas.MachinePredictionTrend)
async def get_machine_prediction_trend(
    machine_id: uuid.UUID,
    days: int = Query(30, ge=1, le=365, description="Number of days to include in the trend"),
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(require_permission(ResourceType.MACHINE, PermissionType.READ))
):
    """
    Get prediction trend data for a specific machine.
    Users can only view data for machines owned by their organization.
    """
    # Check if user has access to the machine
    machine = db.query(models.Machine).filter(models.Machine.id == machine_id).first()
    if not machine:
        raise HTTPException(status_code=404, detail="Machine not found")
    
    if not check_organization_access(current_user, machine.customer_organization_id, db):
        raise HTTPException(status_code=403, detail="Not authorized to view data for this machine")
    
    return crud.get_machine_prediction_trend(db, machine_id, days)

@router.get("/analytics/maintenance-effectiveness", response_model=schemas.MaintenanceEffectivenessMetrics)
async def get_maintenance_effectiveness_metrics(
    organization_id: Optional[uuid.UUID] = Query(None, description="Filter by organization ID"),
    days: int = Query(90, ge=1, le=365, description="Number of days to include in the metrics"),
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(require_permission(ResourceType.MACHINE, PermissionType.READ))
):
    """
    Get metrics on the effectiveness of the predictive maintenance system.
    Users can only view data for their organization.
    """
    # If organization_id is provided, check if user has access to it
    if organization_id:
        if not check_organization_access(current_user, organization_id, db):
            raise HTTPException(status_code=403, detail="Not authorized to view data for this organization")
    
    # If no organization_id is provided and user is not super_admin, use their organization
    elif not permission_checker.is_super_admin(current_user):
        organization_id = current_user.organization_id
    
    return crud.get_maintenance_effectiveness_metrics(db, organization_id, days)