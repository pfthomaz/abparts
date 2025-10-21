# backend/app/routers/inventory_workflow.py

import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from .. import models
from ..schemas import inventory_workflow as schemas
from ..database import get_db
from ..auth import get_current_user_object
from ..crud import inventory_workflow as crud

router = APIRouter(tags=["Inventory Workflows"])

# Stocktake endpoints
@router.post("/stocktakes", response_model=schemas.StocktakeResponse)
def create_stocktake(
    stocktake: schemas.StocktakeCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user_object)
):
    """Create a new stocktake."""
    # Check if user has permission to create stocktakes
    if current_user.role not in [models.UserRole.admin, models.UserRole.super_admin]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to create stocktakes"
        )
    
    # Check if warehouse belongs to user's organization (unless super_admin)
    if current_user.role != models.UserRole.super_admin:
        warehouse = db.query(models.Warehouse).filter(models.Warehouse.id == stocktake.warehouse_id).first()
        if not warehouse or warehouse.organization_id != current_user.organization_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot create stocktake for warehouse outside your organization"
            )
    
    return crud.create_stocktake(db=db, stocktake=stocktake, current_user_id=current_user.id)

@router.get("/stocktakes", response_model=List[schemas.StocktakeResponse])
def get_stocktakes(
    organization_id: Optional[uuid.UUID] = Query(None),
    warehouse_id: Optional[uuid.UUID] = Query(None),
    status: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user_object)
):
    """Get stocktakes with optional filtering."""
    # Apply organization filtering based on user role
    if current_user.role != models.UserRole.super_admin:
        organization_id = current_user.organization_id
    
    # Handle empty string status (convert to None)
    if status == '':
        status = None
    
    return crud.get_stocktakes(
        db=db,
        organization_id=organization_id,
        warehouse_id=warehouse_id,
        status=status,
        skip=skip,
        limit=limit
    )

@router.get("/stocktakes/{stocktake_id}", response_model=schemas.StocktakeResponse)
def get_stocktake(
    stocktake_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user_object)
):
    """Get a specific stocktake by ID."""
    stocktake = crud.get_stocktake(db=db, stocktake_id=stocktake_id)
    if not stocktake:
        raise HTTPException(status_code=404, detail="Stocktake not found")
    
    # Check if user has permission to view this stocktake
    if current_user.role != models.UserRole.super_admin:
        if stocktake.get("organization_id") != current_user.organization_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot view stocktake from another organization"
            )
    
    return stocktake

@router.put("/stocktakes/{stocktake_id}", response_model=schemas.StocktakeResponse)
def update_stocktake(
    stocktake_id: uuid.UUID,
    stocktake_update: schemas.StocktakeUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user_object)
):
    """Update a stocktake."""
    # Check if user has permission to update stocktakes
    if current_user.role not in [models.UserRole.admin, models.UserRole.super_admin]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to update stocktakes"
        )
    
    # Get existing stocktake to check permissions
    existing_stocktake = crud.get_stocktake(db=db, stocktake_id=stocktake_id)
    if not existing_stocktake:
        raise HTTPException(status_code=404, detail="Stocktake not found")
    
    # Check if user has permission to update this stocktake
    if current_user.role != models.UserRole.super_admin:
        if existing_stocktake.get("organization_id") != current_user.organization_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot update stocktake from another organization"
            )
    
    return crud.update_stocktake(db=db, stocktake_id=stocktake_id, stocktake_update=stocktake_update)

@router.delete("/stocktakes/{stocktake_id}")
def delete_stocktake(
    stocktake_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user_object)
):
    """Delete a stocktake."""
    # Check if user has permission to delete stocktakes
    if current_user.role not in [models.UserRole.admin, models.UserRole.super_admin]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to delete stocktakes"
        )
    
    # Get existing stocktake to check permissions
    existing_stocktake = crud.get_stocktake(db=db, stocktake_id=stocktake_id)
    if not existing_stocktake:
        raise HTTPException(status_code=404, detail="Stocktake not found")
    
    # Check if user has permission to delete this stocktake
    if current_user.role != models.UserRole.super_admin:
        if existing_stocktake.get("organization_id") != current_user.organization_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot delete stocktake from another organization"
            )
    
    return crud.delete_stocktake(db=db, stocktake_id=stocktake_id)

# Stocktake Item endpoints
@router.get("/stocktakes/{stocktake_id}/items", response_model=List[schemas.StocktakeItemResponse])
def get_stocktake_items(
    stocktake_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user_object)
):
    """Get all items for a specific stocktake."""
    # Check if stocktake exists and user has permission
    stocktake = crud.get_stocktake(db=db, stocktake_id=stocktake_id)
    if not stocktake:
        raise HTTPException(status_code=404, detail="Stocktake not found")
    
    if current_user.role != models.UserRole.super_admin:
        if stocktake.get("organization_id") != current_user.organization_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot view stocktake items from another organization"
            )
    
    return crud.get_stocktake_items(db=db, stocktake_id=stocktake_id)

@router.put("/stocktake-items/{item_id}", response_model=schemas.StocktakeItemResponse)
def update_stocktake_item(
    item_id: uuid.UUID,
    item_update: schemas.StocktakeItemUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user_object)
):
    """Update a stocktake item with actual count."""
    # Check if user has permission to update stocktake items
    if current_user.role not in [models.UserRole.user, models.UserRole.admin, models.UserRole.super_admin]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to update stocktake items"
        )
    
    return crud.update_stocktake_item(db=db, item_id=item_id, item_update=item_update, current_user_id=current_user.id)

@router.put("/stocktakes/{stocktake_id}/items/batch", response_model=schemas.StocktakeResponse)
def batch_update_stocktake_items(
    stocktake_id: uuid.UUID,
    batch_update: schemas.BatchStocktakeItemUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user_object)
):
    """Update multiple stocktake items in a single operation."""
    # Check if user has permission to update stocktake items
    if current_user.role not in [models.UserRole.user, models.UserRole.admin, models.UserRole.super_admin]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to update stocktake items"
        )
    
    return crud.batch_update_stocktake_items(
        db=db, 
        stocktake_id=stocktake_id, 
        batch_update=batch_update, 
        current_user_id=current_user.id
    )

@router.post("/stocktakes/{stocktake_id}/complete", response_model=schemas.StocktakeResponse)
def complete_stocktake(
    stocktake_id: uuid.UUID,
    apply_adjustments: bool = Query(False, description="Whether to apply inventory adjustments for discrepancies"),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user_object)
):
    """Complete a stocktake and optionally apply inventory adjustments."""
    # Check if user has permission to complete stocktakes
    if current_user.role not in [models.UserRole.admin, models.UserRole.super_admin]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to complete stocktakes"
        )
    
    return crud.complete_stocktake(
        db=db, 
        stocktake_id=stocktake_id, 
        current_user_id=current_user.id, 
        apply_adjustments=apply_adjustments
    )

# Inventory Alert endpoints
@router.get("/alerts", response_model=List[schemas.InventoryAlertResponse])
def get_inventory_alerts(
    organization_id: Optional[uuid.UUID] = Query(None),
    warehouse_id: Optional[uuid.UUID] = Query(None),
    part_id: Optional[uuid.UUID] = Query(None),
    alert_type: Optional[str] = Query(None),
    severity: Optional[str] = Query(None),
    active_only: bool = Query(True),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user_object)
):
    """Get inventory alerts with optional filtering."""
    # Apply organization filtering based on user role
    if current_user.role != models.UserRole.super_admin:
        organization_id = current_user.organization_id
    
    return crud.get_inventory_alerts(
        db=db,
        organization_id=organization_id,
        warehouse_id=warehouse_id,
        part_id=part_id,
        alert_type=alert_type,
        severity=severity,
        active_only=active_only,
        skip=skip,
        limit=limit
    )

@router.post("/alerts", response_model=dict)
def create_inventory_alert(
    alert: schemas.InventoryAlertCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user_object)
):
    """Create a new inventory alert."""
    # Check if user has permission to create alerts
    if current_user.role not in [models.UserRole.admin, models.UserRole.super_admin]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to create inventory alerts"
        )
    
    # Check if warehouse belongs to user's organization (unless super_admin)
    if current_user.role != models.UserRole.super_admin:
        warehouse = db.query(models.Warehouse).filter(models.Warehouse.id == alert.warehouse_id).first()
        if not warehouse or warehouse.organization_id != current_user.organization_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot create alert for warehouse outside your organization"
            )
    
    return crud.create_inventory_alert(db=db, alert=alert)

@router.put("/alerts/{alert_id}", response_model=dict)
def update_inventory_alert(
    alert_id: uuid.UUID,
    alert_update: schemas.InventoryAlertUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user_object)
):
    """Update an inventory alert."""
    # Check if user has permission to update alerts
    if current_user.role not in [models.UserRole.admin, models.UserRole.super_admin]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to update inventory alerts"
        )
    
    return crud.update_inventory_alert(db=db, alert_id=alert_id, alert_update=alert_update)

# Inventory Adjustment endpoints
@router.post("/adjustments", response_model=dict)
def create_inventory_adjustment(
    adjustment: schemas.InventoryAdjustmentCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user_object)
):
    """Create a new inventory adjustment."""
    # Check if user has permission to create adjustments
    if current_user.role not in [models.UserRole.admin, models.UserRole.super_admin]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to create inventory adjustments"
        )
    
    # Check if warehouse belongs to user's organization (unless super_admin)
    if current_user.role != models.UserRole.super_admin:
        warehouse = db.query(models.Warehouse).filter(models.Warehouse.id == adjustment.warehouse_id).first()
        if not warehouse or warehouse.organization_id != current_user.organization_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot create adjustment for warehouse outside your organization"
            )
    
    return crud.create_inventory_adjustment(db=db, adjustment=adjustment, current_user_id=current_user.id)

@router.get("/adjustments", response_model=List[schemas.InventoryAdjustmentResponse])
def get_inventory_adjustments(
    organization_id: Optional[uuid.UUID] = Query(None),
    warehouse_id: Optional[uuid.UUID] = Query(None),
    part_id: Optional[uuid.UUID] = Query(None),
    adjusted_by_user_id: Optional[uuid.UUID] = Query(None),
    stocktake_id: Optional[uuid.UUID] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user_object)
):
    """Get inventory adjustments with optional filtering."""
    # Apply organization filtering based on user role
    if current_user.role != models.UserRole.super_admin:
        organization_id = current_user.organization_id
    
    return crud.get_inventory_adjustments(
        db=db,
        organization_id=organization_id,
        warehouse_id=warehouse_id,
        part_id=part_id,
        adjusted_by_user_id=adjusted_by_user_id,
        stocktake_id=stocktake_id,
        skip=skip,
        limit=limit
    )

@router.post("/adjustments/batch", response_model=List[schemas.InventoryAdjustmentResponse])
def batch_create_inventory_adjustments(
    batch_adjustment: schemas.BatchInventoryAdjustment,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user_object)
):
    """Create multiple inventory adjustments in a single operation."""
    # Check if user has permission to create adjustments
    if current_user.role not in [models.UserRole.admin, models.UserRole.super_admin]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to create inventory adjustments"
        )
    
    # Check if warehouse belongs to user's organization (unless super_admin)
    if current_user.role != models.UserRole.super_admin:
        warehouse = db.query(models.Warehouse).filter(models.Warehouse.id == batch_adjustment.warehouse_id).first()
        if not warehouse or warehouse.organization_id != current_user.organization_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot create adjustments for warehouse outside your organization"
            )
    
    return crud.batch_create_inventory_adjustments(
        db=db, 
        batch_adjustment=batch_adjustment, 
        current_user_id=current_user.id
    )

# Analytics endpoints
@router.post("/analytics", response_model=schemas.InventoryAnalytics)
def get_inventory_analytics(
    request: schemas.InventoryAnalyticsRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user_object)
):
    """Get inventory analytics and insights."""
    # Apply organization filtering based on user role
    if current_user.role != models.UserRole.super_admin:
        request.organization_id = current_user.organization_id
    
    return crud.get_inventory_analytics(db=db, request=request)

@router.post("/alerts/generate")
def generate_inventory_alerts(
    organization_id: Optional[uuid.UUID] = Query(None),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user_object)
):
    """Generate inventory alerts based on current stock levels and thresholds."""
    # Check if user has permission to generate alerts
    if current_user.role not in [models.UserRole.admin, models.UserRole.super_admin]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to generate inventory alerts"
        )
    
    # Apply organization filtering based on user role
    if current_user.role != models.UserRole.super_admin:
        organization_id = current_user.organization_id
    
    return crud.generate_inventory_alerts(db=db, organization_id=organization_id)