# backend/app/crud/predictive_maintenance.py

import uuid
import logging
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime, timedelta

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc
from fastapi import HTTPException, status

from .. import models, schemas
from ..models import (
    PredictiveMaintenanceModel, MachinePrediction,
    MaintenanceRecommendation, MaintenanceRiskLevel, MaintenancePriority, MaintenanceStatus
)

logger = logging.getLogger(__name__)

# Predictive Maintenance Model CRUD
def get_predictive_model(db: Session, model_id: uuid.UUID):
    """Get a predictive maintenance model by ID."""
    model = db.query(PredictiveMaintenanceModel).filter(PredictiveMaintenanceModel.id == model_id).first()
    return model

def get_predictive_models(db: Session, skip: int = 0, limit: int = 100, active_only: bool = False):
    """Get all predictive maintenance models."""
    query = db.query(PredictiveMaintenanceModel)
    
    if active_only:
        query = query.filter(PredictiveMaintenanceModel.is_active == True)
    
    models = query.order_by(PredictiveMaintenanceModel.created_at.desc()).offset(skip).limit(limit).all()
    return models

def create_predictive_model(db: Session, model: schemas.PredictiveMaintenanceModelCreate):
    """Create a new predictive maintenance model."""
    db_model = PredictiveMaintenanceModel(**model.dict())
    
    try:
        db.add(db_model)
        db.commit()
        db.refresh(db_model)
        return db_model
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating predictive maintenance model: {e}")
        raise HTTPException(status_code=500, detail=f"Error creating predictive maintenance model: {str(e)}")

def update_predictive_model(db: Session, model_id: uuid.UUID, model_update: schemas.PredictiveMaintenanceModelUpdate):
    """Update a predictive maintenance model."""
    db_model = get_predictive_model(db, model_id)
    if not db_model:
        return None
    
    update_data = model_update.dict(exclude_unset=True)
    
    for key, value in update_data.items():
        setattr(db_model, key, value)
    
    try:
        db.add(db_model)
        db.commit()
        db.refresh(db_model)
        return db_model
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating predictive maintenance model: {e}")
        raise HTTPException(status_code=500, detail=f"Error updating predictive maintenance model: {str(e)}")

def delete_predictive_model(db: Session, model_id: uuid.UUID):
    """Delete a predictive maintenance model."""
    db_model = get_predictive_model(db, model_id)
    if not db_model:
        return None
    
    try:
        # Check if there are any predictions using this model
        predictions = db.query(MachinePrediction).filter(MachinePrediction.predictive_model_id == model_id).count()
        if predictions > 0:
            # Instead of deleting, mark as inactive
            db_model.is_active = False
            db.add(db_model)
            db.commit()
            return {"message": "Model has existing predictions and cannot be deleted. It has been marked as inactive."}
        else:
            # No machine model associations to delete in current implementation
            
            # Delete the model
            db.delete(db_model)
            db.commit()
            return {"message": "Predictive maintenance model deleted successfully"}
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting predictive maintenance model: {e}")
        raise HTTPException(status_code=500, detail=f"Error deleting predictive maintenance model: {str(e)}")

# Machine Model Association CRUD (Simplified - not implemented in current model)
def get_machine_model_association(db: Session, association_id: uuid.UUID):
    """Get a machine model association by ID."""
    # This functionality is not implemented in the current model structure
    return None

def get_machine_model_associations(db: Session, predictive_model_id: Optional[uuid.UUID] = None, 
                                  machine_model_type: Optional[str] = None, skip: int = 0, limit: int = 100):
    """Get machine model associations with optional filtering."""
    # This functionality is not implemented in the current model structure
    return []

def create_machine_model_association(db: Session, association: schemas.MachineModelAssociationCreate):
    """Create a new machine model association."""
    # This functionality is not implemented in the current model structure
    raise HTTPException(status_code=501, detail="Machine model associations are not implemented in the current version")

def update_machine_model_association(db: Session, association_id: uuid.UUID, 
                                    association_update: schemas.MachineModelAssociationUpdate):
    """Update a machine model association."""
    db_association = get_machine_model_association(db, association_id)
    if not db_association:
        return None
    
    update_data = association_update.dict(exclude_unset=True)
    
    for key, value in update_data.items():
        setattr(db_association, key, value)
    
    try:
        db.add(db_association)
        db.commit()
        db.refresh(db_association)
        return db_association
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating machine model association: {e}")
        raise HTTPException(status_code=500, detail=f"Error updating machine model association: {str(e)}")

def delete_machine_model_association(db: Session, association_id: uuid.UUID):
    """Delete a machine model association."""
    db_association = get_machine_model_association(db, association_id)
    if not db_association:
        return None
    
    try:
        db.delete(db_association)
        db.commit()
        return {"message": "Machine model association deleted successfully"}
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting machine model association: {e}")
        raise HTTPException(status_code=500, detail=f"Error deleting machine model association: {str(e)}")

# Machine Prediction CRUD
def get_machine_prediction(db: Session, prediction_id: uuid.UUID):
    """Get a machine prediction by ID with related data."""
    prediction = db.query(
        MachinePrediction,
        models.Machine.serial_number.label("machine_serial_number"),
        models.Machine.model_type.label("machine_model_type"),
        PredictiveMaintenanceModel.name.label("model_name")
    ).join(
        models.Machine, MachinePrediction.machine_id == models.Machine.id
    ).join(
        PredictiveMaintenanceModel, MachinePrediction.predictive_model_id == PredictiveMaintenanceModel.id
    ).filter(
        MachinePrediction.id == prediction_id
    ).first()
    
    if not prediction:
        return None
    
    prediction_obj, machine_serial_number, machine_model_type, model_name = prediction
    
    result = {
        **prediction_obj.__dict__,
        "machine_serial_number": machine_serial_number,
        "machine_model_type": machine_model_type,
        "model_name": model_name
    }
    
    return result

def get_machine_predictions(db: Session, machine_id: Optional[uuid.UUID] = None, 
                           risk_level: Optional[str] = None, days: Optional[int] = None,
                           skip: int = 0, limit: int = 100):
    """Get machine predictions with optional filtering."""
    query = db.query(
        MachinePrediction,
        models.Machine.serial_number.label("machine_serial_number"),
        models.Machine.model_type.label("machine_model_type"),
        PredictiveMaintenanceModel.name.label("model_name")
    ).join(
        models.Machine, MachinePrediction.machine_id == models.Machine.id
    ).join(
        PredictiveMaintenanceModel, MachinePrediction.predictive_model_id == PredictiveMaintenanceModel.id
    )
    
    if machine_id:
        query = query.filter(MachinePrediction.machine_id == machine_id)
    
    if risk_level:
        query = query.filter(MachinePrediction.risk_level == risk_level)
    
    if days:
        cutoff_date = datetime.now() - timedelta(days=days)
        query = query.filter(MachinePrediction.prediction_date >= cutoff_date)
    
    predictions = query.order_by(MachinePrediction.prediction_date.desc()).offset(skip).limit(limit).all()
    
    results = []
    for prediction, machine_serial_number, machine_model_type, model_name in predictions:
        result = {
            **prediction.__dict__,
            "machine_serial_number": machine_serial_number,
            "machine_model_type": machine_model_type,
            "model_name": model_name
        }
        results.append(result)
    
    return results

def create_machine_prediction(db: Session, prediction: schemas.MachinePredictionCreate):
    """Create a new machine prediction."""
    # Check if the machine exists
    machine = db.query(models.Machine).filter(models.Machine.id == prediction.machine_id).first()
    if not machine:
        raise HTTPException(status_code=404, detail="Machine not found")
    
    # Check if the predictive model exists
    model = get_predictive_model(db, prediction.predictive_model_id)
    if not model:
        raise HTTPException(status_code=404, detail="Predictive maintenance model not found")
    
    db_prediction = MachinePrediction(**prediction.dict())
    
    try:
        db.add(db_prediction)
        db.commit()
        db.refresh(db_prediction)
        
        # Get the prediction with related data
        result = get_machine_prediction(db, db_prediction.id)
        return result
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating machine prediction: {e}")
        raise HTTPException(status_code=500, detail=f"Error creating machine prediction: {str(e)}")

def delete_machine_prediction(db: Session, prediction_id: uuid.UUID):
    """Delete a machine prediction."""
    db_prediction = db.query(MachinePrediction).filter(MachinePrediction.id == prediction_id).first()
    if not db_prediction:
        return None
    
    try:
        # Check if there are any recommendations based on this prediction
        recommendations = db.query(MaintenanceRecommendation).filter(
            MaintenanceRecommendation.prediction_id == prediction_id
        ).all()
        
        if recommendations:
            # Delete the recommendations (no recommended parts in current model)
            db.query(MaintenanceRecommendation).filter(
                MaintenanceRecommendation.prediction_id == prediction_id
            ).delete()
        
        # Delete the prediction
        db.delete(db_prediction)
        db.commit()
        return {"message": "Machine prediction deleted successfully"}
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting machine prediction: {e}")
        raise HTTPException(status_code=500, detail=f"Error deleting machine prediction: {str(e)}")

# Prediction Engine
def generate_machine_prediction(db: Session, request: schemas.PredictionRequest):
    """Generate a prediction for a machine based on indicator values."""
    # Check if machine exists
    machine = db.query(models.Machine).filter(models.Machine.id == request.machine_id).first()
    if not machine:
        raise HTTPException(status_code=404, detail="Machine not found")
    
    # Find an active predictive model (simplified - use first active model)
    model = db.query(PredictiveMaintenanceModel).filter(
        PredictiveMaintenanceModel.is_active == True
    ).first()
    
    if not model:
        raise HTTPException(status_code=404, detail="No active predictive model found")
    
    # In a real system, we would use the model to make a prediction
    # For this implementation, we'll simulate a prediction based on the indicators
    
    # Calculate a simple risk score based on indicator values
    risk_score = 0
    for indicator_name, value in request.indicators.items():
        # Simplified risk calculation based on indicator values
        # In a real implementation, this would use actual indicator thresholds
        if value > 80:  # Assume values over 80 are critical
            risk_score += 3
        elif value > 60:  # Assume values over 60 are warning
            risk_score += 1
    
    # Determine risk level based on score
    risk_level = MaintenanceRiskLevel.LOW
    if risk_score >= 5:
        risk_level = MaintenanceRiskLevel.CRITICAL
    elif risk_score >= 3:
        risk_level = MaintenanceRiskLevel.HIGH
    elif risk_score >= 1:
        risk_level = MaintenanceRiskLevel.MEDIUM
    
    # Calculate failure probability (simplified)
    failure_probability = min(risk_score * 0.1, 0.95)
    
    # Calculate remaining useful life (simplified)
    remaining_useful_life = max(100 - (risk_score * 10), 0)
    
    # Calculate predicted failure date
    predicted_failure_date = None
    if remaining_useful_life > 0:
        predicted_failure_date = datetime.now() + timedelta(days=remaining_useful_life)
    
    # Create the prediction
    prediction = MachinePrediction(
        machine_id=machine.id,
        predictive_model_id=model.id,
        failure_probability=failure_probability,
        remaining_useful_life=remaining_useful_life,
        predicted_failure_date=predicted_failure_date,
        risk_level=risk_level,
        prediction_details={
            "risk_score": risk_score,
            "indicators": request.indicators,
            "additional_data": request.additional_data
        }
    )
    
    try:
        db.add(prediction)
        db.commit()
        db.refresh(prediction)
        
        # If risk is high or critical, create a maintenance recommendation
        recommendation_id = None
        priority = None
        if risk_level in [MaintenanceRiskLevel.HIGH, MaintenanceRiskLevel.CRITICAL]:
            # Determine priority based on risk level
            priority = MaintenancePriority.HIGH if risk_level == MaintenanceRiskLevel.HIGH else MaintenancePriority.URGENT
            
            # Create recommendation
            recommendation = MaintenanceRecommendation(
                machine_id=machine.id,
                prediction_id=prediction.id,
                recommended_maintenance_type=models.MaintenanceType.REPAIR,
                priority=priority,
                recommended_completion_date=datetime.now() + timedelta(days=7 if priority == MaintenancePriority.HIGH else 3),
                description=f"Preventive maintenance recommended due to {risk_level.value} risk level detected",
                status=MaintenanceStatus.PENDING
            )
            
            db.add(recommendation)
            db.commit()
            db.refresh(recommendation)
            recommendation_id = recommendation.id
            
            # Add recommended parts based on machine type and risk level
            # In a real system, this would be more sophisticated
            compatible_parts = db.query(models.MachinePartCompatibility).filter(
                models.MachinePartCompatibility.machine_id == machine.id,
                models.MachinePartCompatibility.is_recommended == True
            ).limit(3).all()
            
            for compatible_part in compatible_parts:
                recommended_part = RecommendedPart(
                    recommendation_id=recommendation.id,
                    part_id=compatible_part.part_id,
                    quantity=1,
                    reason="Recommended for preventive maintenance"
                )
                db.add(recommended_part)
            
            db.commit()
        
        # Get the prediction with related data
        result = get_machine_prediction(db, prediction.id)
        
        # Format the response
        response = {
            "prediction_id": prediction.id,
            "machine_id": machine.id,
            "machine_serial_number": result["machine_serial_number"],
            "machine_model_type": result["machine_model_type"],
            "failure_probability": failure_probability,
            "remaining_useful_life": remaining_useful_life,
            "predicted_failure_date": predicted_failure_date,
            "risk_level": risk_level.value,
            "recommendation_id": recommendation_id,
            "recommendation_details": {
                "priority": priority.value if recommendation_id else None,
                "recommended_completion_date": recommendation.recommended_completion_date if recommendation_id else None
            } if recommendation_id else None
        }
        
        return response
    except Exception as e:
        db.rollback()
        logger.error(f"Error generating machine prediction: {e}")
        raise HTTPException(status_code=500, detail=f"Error generating machine prediction: {str(e)}")

def batch_generate_predictions(db: Session, request: schemas.BatchPredictionRequest):
    """Generate predictions for multiple machines."""
    results = []
    for machine_id in request.machine_ids:
        try:
            # Get the latest indicator values for this machine
            latest_indicators = {}
            indicator_values = get_machine_indicator_values(db, machine_id=machine_id, limit=100)
            
            # Group by indicator name and get the latest value for each
            indicator_dict = {}
            for value in indicator_values:
                if value["indicator_name"] not in indicator_dict or value["recorded_at"] > indicator_dict[value["indicator_name"]]["recorded_at"]:
                    indicator_dict[value["indicator_name"]] = value
            
            # Extract the values
            for name, value in indicator_dict.items():
                latest_indicators[name] = value["value"]
            
            # Generate prediction
            prediction_request = schemas.PredictionRequest(
                machine_id=machine_id,
                indicators=latest_indicators
            )
            
            prediction = generate_machine_prediction(db, prediction_request)
            results.append(prediction)
        except Exception as e:
            logger.error(f"Error generating prediction for machine {machine_id}: {e}")
            results.append({
                "machine_id": machine_id,
                "error": str(e)
            })
    
    return results