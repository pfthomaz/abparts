"""API router for maintenance protocols and related operations."""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
import uuid

from app import models, schemas
from app.crud import maintenance_protocols as crud_maintenance, parts as crud_parts, machines as crud_machines
from app.database import get_db
from app.auth import get_current_user, TokenData
from app.permissions import require_permission, ResourceType, PermissionType, permission_checker

router = APIRouter()


# Maintenance Protocol Endpoints

@router.get("/", response_model=List[schemas.MaintenanceProtocolResponse])
def list_protocols(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    protocol_type: Optional[str] = Query(None),
    machine_model: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)  # All authenticated users can view protocols
):
    """List maintenance protocols with filtering options. All users can view to perform maintenance."""
    protocols = crud_maintenance.get_protocols_filtered(
        db=db,
        skip=skip,
        limit=limit,
        protocol_type=protocol_type,
        machine_model=machine_model,
        is_active=is_active,
        search=search
    )
    return protocols


@router.post("/", response_model=schemas.MaintenanceProtocolResponse)
def create_protocol(
    protocol_in: schemas.MaintenanceProtocolCreate,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(require_permission(ResourceType.MAINTENANCE, PermissionType.WRITE))
):
    """Create a new maintenance protocol. Super admin only."""
    if not permission_checker.is_super_admin(current_user):
        raise HTTPException(status_code=403, detail="Only super admins can create maintenance protocols")
    
    existing = crud_maintenance.get_protocol_by_name_and_model(
        db=db, 
        name=protocol_in.name, 
        machine_model=protocol_in.machine_model
    )
    if existing:
        raise HTTPException(
            status_code=400, 
            detail=f"Protocol '{protocol_in.name}' already exists for machine model '{protocol_in.machine_model or 'All Models'}'"
        )
    
    protocol = crud_maintenance.create_protocol(db=db, protocol_in=protocol_in)
    return protocol


# Execution endpoints - must be before /{protocol_id} to avoid path conflicts

@router.get("/executions", response_model=List[schemas.MaintenanceExecutionResponse])
def get_executions(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)
):
    """Get all maintenance executions for the current user's organization."""
    executions = crud_maintenance.get_executions_by_organization(
        db=db, organization_id=current_user.organization_id, skip=skip, limit=limit
    )
    return executions


@router.post("/executions", response_model=schemas.MaintenanceExecutionResponse)
def create_execution(
    execution_in: schemas.MaintenanceExecutionCreate,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)
):
    """Record a maintenance execution."""
    machine = db.query(models.Machine).filter(models.Machine.id == execution_in.machine_id).first()
    if not machine:
        raise HTTPException(status_code=404, detail="Machine not found")
    
    if execution_in.protocol_id:
        protocol = crud_maintenance.get_protocol(db=db, protocol_id=execution_in.protocol_id)
        if not protocol:
            raise HTTPException(status_code=404, detail="Protocol not found")
    
    execution = crud_maintenance.create_execution(
        db=db, execution_in=execution_in, performed_by_user_id=current_user.user_id
    )
    return execution


@router.get("/{protocol_id}", response_model=schemas.MaintenanceProtocolResponse)
def get_protocol(
    protocol_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(require_permission(ResourceType.MAINTENANCE, PermissionType.READ))
):
    """Get a specific maintenance protocol by ID."""
    protocol = crud_maintenance.get_protocol(db=db, protocol_id=protocol_id)
    if not protocol:
        raise HTTPException(status_code=404, detail="Protocol not found")
    return protocol


@router.put("/{protocol_id}", response_model=schemas.MaintenanceProtocolResponse)
def update_protocol(
    protocol_id: uuid.UUID,
    protocol_in: schemas.MaintenanceProtocolUpdate,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(require_permission(ResourceType.MAINTENANCE, PermissionType.WRITE))
):
    """Update a maintenance protocol. Super admin only."""
    if not permission_checker.is_super_admin(current_user):
        raise HTTPException(status_code=403, detail="Only super admins can update maintenance protocols")
    
    protocol = crud_maintenance.update_protocol(db=db, protocol_id=protocol_id, protocol_in=protocol_in)
    if not protocol:
        raise HTTPException(status_code=404, detail="Protocol not found")
    
    return protocol


@router.delete("/{protocol_id}", status_code=204)
def delete_protocol(
    protocol_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(require_permission(ResourceType.MAINTENANCE, PermissionType.DELETE))
):
    """Delete a maintenance protocol. Super admin only."""
    if not permission_checker.is_super_admin(current_user):
        raise HTTPException(status_code=403, detail="Only super admins can delete maintenance protocols")
    
    # Check if protocol has any executions
    executions_count = db.query(models.MaintenanceExecution).filter(
        models.MaintenanceExecution.protocol_id == protocol_id
    ).count()
    
    if executions_count > 0:
        raise HTTPException(
            status_code=400, 
            detail=f"Cannot delete protocol. It has {executions_count} execution records. Consider deactivating instead."
        )
    
    success = crud_maintenance.delete_protocol(db=db, protocol_id=protocol_id)
    if not success:
        raise HTTPException(status_code=404, detail="Protocol not found")


@router.post("/{protocol_id}/duplicate", response_model=schemas.MaintenanceProtocolResponse)
def duplicate_protocol(
    protocol_id: uuid.UUID,
    duplicate_request: schemas.ProtocolDuplicateRequest,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(require_permission(ResourceType.MAINTENANCE, PermissionType.WRITE))
):
    """Duplicate an existing protocol. Super admin only."""
    if not permission_checker.is_super_admin(current_user):
        raise HTTPException(status_code=403, detail="Only super admins can duplicate maintenance protocols")
    
    existing = crud_maintenance.get_protocol_by_name_and_model(
        db=db, 
        name=duplicate_request.new_name, 
        machine_model=duplicate_request.new_machine_model
    )
    if existing:
        raise HTTPException(
            status_code=400, 
            detail=f"Protocol '{duplicate_request.new_name}' already exists"
        )
    
    new_protocol = crud_maintenance.duplicate_protocol(
        db=db,
        protocol_id=protocol_id,
        new_name=duplicate_request.new_name,
        new_machine_model=duplicate_request.new_machine_model,
        copy_checklist_items=duplicate_request.copy_checklist_items
    )
    
    if not new_protocol:
        raise HTTPException(status_code=404, detail="Original protocol not found")
    
    return new_protocol


# Checklist Item Endpoints

@router.get("/{protocol_id}/checklist-items", response_model=List[schemas.ProtocolChecklistItemResponse])
def list_checklist_items(
    protocol_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)  # All authenticated users can view checklist items
):
    """List checklist items for a protocol. All users can view to perform maintenance."""
    protocol = crud_maintenance.get_protocol(db=db, protocol_id=protocol_id)
    if not protocol:
        raise HTTPException(status_code=404, detail="Protocol not found")
    
    items = crud_maintenance.get_checklist_items_by_protocol(db=db, protocol_id=protocol_id)
    return items


@router.post("/{protocol_id}/checklist-items", response_model=schemas.ProtocolChecklistItemResponse)
def create_checklist_item(
    protocol_id: uuid.UUID,
    item_in: schemas.ProtocolChecklistItemCreate,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(require_permission(ResourceType.MAINTENANCE, PermissionType.WRITE))
):
    """Add a checklist item to a protocol. Super admin only."""
    if not permission_checker.is_super_admin(current_user):
        raise HTTPException(status_code=403, detail="Only super admins can modify maintenance protocols")
    
    protocol = crud_maintenance.get_protocol(db=db, protocol_id=protocol_id)
    if not protocol:
        raise HTTPException(status_code=404, detail="Protocol not found")
    
    item = crud_maintenance.create_checklist_item(db=db, protocol_id=protocol_id, item_in=item_in)
    return item


@router.put("/{protocol_id}/checklist-items/{item_id}", response_model=schemas.ProtocolChecklistItemResponse)
def update_checklist_item(
    protocol_id: uuid.UUID,
    item_id: uuid.UUID,
    item_in: schemas.ProtocolChecklistItemUpdate,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(require_permission(ResourceType.MAINTENANCE, PermissionType.WRITE))
):
    """Update a checklist item. Super admin only."""
    if not permission_checker.is_super_admin(current_user):
        raise HTTPException(status_code=403, detail="Only super admins can modify maintenance protocols")
    
    item = crud_maintenance.update_checklist_item(db=db, item_id=item_id, item_in=item_in)
    if not item:
        raise HTTPException(status_code=404, detail="Checklist item not found")
    
    return item


@router.delete("/{protocol_id}/checklist-items/{item_id}", status_code=204)
def delete_checklist_item(
    protocol_id: uuid.UUID,
    item_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(require_permission(ResourceType.MAINTENANCE, PermissionType.DELETE))
):
    """Delete a checklist item. Super admin only."""
    if not permission_checker.is_super_admin(current_user):
        raise HTTPException(status_code=403, detail="Only super admins can modify maintenance protocols")
    
    # Check if item has any completions
    completions_count = db.query(models.MaintenanceChecklistCompletion).filter(
        models.MaintenanceChecklistCompletion.checklist_item_id == item_id
    ).count()
    
    if completions_count > 0:
        raise HTTPException(
            status_code=400, 
            detail=f"Cannot delete checklist item. It has {completions_count} completion records."
        )
    
    success = crud_maintenance.delete_checklist_item(db=db, item_id=item_id)
    if not success:
        raise HTTPException(status_code=404, detail="Checklist item not found")


@router.post("/{protocol_id}/checklist-items/reorder", status_code=200)
def reorder_checklist_items(
    protocol_id: uuid.UUID,
    reorder_request: schemas.ChecklistItemReorderRequest,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(require_permission(ResourceType.MAINTENANCE, PermissionType.WRITE))
):
    """Reorder checklist items within a protocol. Super admin only."""
    if not permission_checker.is_super_admin(current_user):
        raise HTTPException(status_code=403, detail="Only super admins can modify maintenance protocols")
    
    success = crud_maintenance.reorder_checklist_items(
        db=db, protocol_id=protocol_id, item_orders=reorder_request.item_orders
    )
    
    if not success:
        raise HTTPException(status_code=500, detail="Failed to reorder items")
    
    return {"message": "Items reordered successfully"}


# User-facing endpoints

@router.get("/for-machine/{machine_id}", response_model=List[schemas.MaintenanceProtocolResponse])
def get_protocols_for_machine(
    machine_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)
):
    """Get all applicable protocols for a specific machine."""
    machine = db.query(models.Machine).filter(models.Machine.id == machine_id).first()
    if not machine:
        raise HTTPException(status_code=404, detail="Machine not found")
    
    machine_model = getattr(machine, 'machine_model', 'V3.1B')
    
    protocols = crud_maintenance.get_protocols_for_machine_model(
        db=db, machine_model=machine_model
    )
    return protocols


@router.get("/executions/machine/{machine_id}", response_model=List[schemas.MaintenanceExecutionResponse])
def get_executions_for_machine(
    machine_id: uuid.UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)
):
    """Get maintenance execution history for a machine."""
    machine = db.query(models.Machine).filter(models.Machine.id == machine_id).first()
    if not machine:
        raise HTTPException(status_code=404, detail="Machine not found")
    
    executions = crud_maintenance.get_executions_by_machine(
        db=db, machine_id=machine_id, skip=skip, limit=limit
    )
    return executions


@router.post("/executions/{execution_id}/checklist/{item_id}/complete", response_model=schemas.MaintenanceChecklistCompletionResponse)
def complete_checklist_item(
    execution_id: uuid.UUID,
    item_id: uuid.UUID,
    completion_in: schemas.MaintenanceChecklistCompletionCreate,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)
):
    """Mark a checklist item as completed during execution."""
    # Verify execution exists and belongs to user's organization
    execution = db.query(models.MaintenanceExecution).filter(
        models.MaintenanceExecution.id == execution_id
    ).first()
    
    if not execution:
        raise HTTPException(status_code=404, detail="Execution not found")
    
    # Verify checklist item belongs to the protocol
    checklist_item = db.query(models.ProtocolChecklistItem).filter(
        models.ProtocolChecklistItem.id == item_id,
        models.ProtocolChecklistItem.protocol_id == execution.protocol_id
    ).first()
    
    if not checklist_item:
        raise HTTPException(status_code=404, detail="Checklist item not found")
    
    # Create or update completion record
    completion = crud_maintenance.complete_checklist_item(
        db=db,
        execution_id=execution_id,
        checklist_item_id=item_id,
        completion_data=completion_in
    )
    
    return completion


@router.put("/executions/{execution_id}/complete", response_model=schemas.MaintenanceExecutionResponse)
def complete_execution(
    execution_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)
):
    """Mark an execution as completed."""
    execution = crud_maintenance.complete_execution(
        db=db, execution_id=execution_id
    )
    
    if not execution:
        raise HTTPException(status_code=404, detail="Execution not found")
    
    return execution


@router.get("/reminders/pending", response_model=List[schemas.MaintenanceReminderResponse])
def get_pending_reminders(
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)
):
    """Get pending maintenance reminders for the current user."""
    reminders = crud_maintenance.get_pending_reminders_for_user(
        db=db, user_id=current_user.user_id
    )
    return reminders


@router.put("/reminders/{reminder_id}/acknowledge", response_model=schemas.MaintenanceReminderResponse)
def acknowledge_reminder(
    reminder_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)
):
    """Acknowledge a maintenance reminder."""
    reminder = crud_maintenance.acknowledge_reminder(
        db=db, reminder_id=reminder_id, user_id=current_user.user_id
    )
    
    if not reminder:
        raise HTTPException(status_code=404, detail="Reminder not found")
    
    return reminder
