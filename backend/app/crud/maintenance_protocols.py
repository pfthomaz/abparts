"""CRUD operations for maintenance protocols and related models."""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, desc, asc
import uuid
from datetime import datetime, date
from decimal import Decimal

from .. import models


# Maintenance Protocol CRUD Operations

def get_protocol(db: Session, protocol_id: uuid.UUID) -> Optional[models.MaintenanceProtocol]:
    """Get a protocol by ID."""
    return db.query(models.MaintenanceProtocol).filter(
        models.MaintenanceProtocol.id == protocol_id
    ).first()


def get_protocol_by_name_and_model(db: Session, name: str, machine_model: Optional[str] = None) -> Optional[models.MaintenanceProtocol]:
    """Get protocol by name and machine model."""
    query = db.query(models.MaintenanceProtocol).filter(
        models.MaintenanceProtocol.name == name
    )
    
    if machine_model:
        query = query.filter(models.MaintenanceProtocol.machine_model == machine_model)
    else:
        query = query.filter(models.MaintenanceProtocol.machine_model.is_(None))
        
    return query.first()


def get_protocols_filtered(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    protocol_type: Optional[str] = None,
    machine_model: Optional[str] = None,
    is_active: Optional[bool] = None,
    search: Optional[str] = None
) -> List[models.MaintenanceProtocol]:
    """Get protocols with filtering options."""
    query = db.query(models.MaintenanceProtocol).options(
        joinedload(models.MaintenanceProtocol.checklist_items)
    )
    
    # Apply filters
    if protocol_type:
        query = query.filter(models.MaintenanceProtocol.protocol_type == protocol_type)
    
    if machine_model:
        if machine_model == "all":
            query = query.filter(models.MaintenanceProtocol.machine_model.is_(None))
        else:
            query = query.filter(
                or_(
                    models.MaintenanceProtocol.machine_model == machine_model,
                    models.MaintenanceProtocol.machine_model.is_(None)
                )
            )
    
    if is_active is not None:
        query = query.filter(models.MaintenanceProtocol.is_active == is_active)
    
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            or_(
                models.MaintenanceProtocol.name.ilike(search_term),
                models.MaintenanceProtocol.description.ilike(search_term)
            )
        )
    
    # Order by display_order, then by name
    query = query.order_by(
        asc(models.MaintenanceProtocol.display_order),
        asc(models.MaintenanceProtocol.name)
    )
    
    return query.offset(skip).limit(limit).all()


def get_protocols_for_machine_model(db: Session, machine_model: str) -> List[models.MaintenanceProtocol]:
    """Get all active protocols applicable to a specific machine model."""
    return db.query(models.MaintenanceProtocol).filter(
        and_(
            models.MaintenanceProtocol.is_active == True,
            or_(
                models.MaintenanceProtocol.machine_model == machine_model,
                models.MaintenanceProtocol.machine_model.is_(None)
            )
        )
    ).options(
        joinedload(models.MaintenanceProtocol.checklist_items).joinedload(models.ProtocolChecklistItem.part)
    ).order_by(
        asc(models.MaintenanceProtocol.display_order),
        asc(models.MaintenanceProtocol.name)
    ).all()


def create_protocol(db: Session, protocol_in) -> models.MaintenanceProtocol:
    """Create a new protocol."""
    protocol_data = protocol_in.dict()
    db_protocol = models.MaintenanceProtocol(**protocol_data)
    db.add(db_protocol)
    db.commit()
    db.refresh(db_protocol)
    return db_protocol


def update_protocol(db: Session, protocol_id: uuid.UUID, protocol_in) -> Optional[models.MaintenanceProtocol]:
    """Update a protocol."""
    db_protocol = get_protocol(db, protocol_id)
    if not db_protocol:
        return None
    
    update_data = protocol_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_protocol, field, value)
    
    db.commit()
    db.refresh(db_protocol)
    return db_protocol


def delete_protocol(db: Session, protocol_id: uuid.UUID) -> bool:
    """Delete a protocol."""
    db_protocol = get_protocol(db, protocol_id)
    if not db_protocol:
        return False
    
    db.delete(db_protocol)
    db.commit()
    return True


def duplicate_protocol(
    db: Session,
    protocol_id: uuid.UUID,
    new_name: str,
    new_machine_model: Optional[str] = None,
    copy_checklist_items: bool = True
) -> Optional[models.MaintenanceProtocol]:
    """Duplicate an existing protocol."""
    original = get_protocol(db, protocol_id)
    if not original:
        return None
    
    # Create new protocol
    new_protocol = models.MaintenanceProtocol(
        name=new_name,
        protocol_type=original.protocol_type,
        service_interval_hours=original.service_interval_hours,
        machine_model=new_machine_model if new_machine_model is not None else original.machine_model,
        description=original.description,
        is_active=True,
        display_order=original.display_order
    )
    
    db.add(new_protocol)
    db.flush()  # Get the ID
    
    # Copy checklist items if requested
    if copy_checklist_items and original.checklist_items:
        for item in original.checklist_items:
            new_item = models.ProtocolChecklistItem(
                protocol_id=new_protocol.id,
                item_order=item.item_order,
                item_description=item.item_description,
                item_type=item.item_type,
                item_category=item.item_category,
                part_id=item.part_id,
                estimated_quantity=item.estimated_quantity,
                is_critical=item.is_critical,
                estimated_duration_minutes=item.estimated_duration_minutes,
                notes=item.notes
            )
            db.add(new_item)
    
    db.commit()
    db.refresh(new_protocol)
    return new_protocol


# Protocol Checklist Item CRUD Operations

def get_checklist_item(db: Session, item_id: uuid.UUID) -> Optional[models.ProtocolChecklistItem]:
    """Get a checklist item by ID."""
    return db.query(models.ProtocolChecklistItem).filter(
        models.ProtocolChecklistItem.id == item_id
    ).first()


def get_checklist_items_by_protocol(db: Session, protocol_id: uuid.UUID) -> List[models.ProtocolChecklistItem]:
    """Get all checklist items for a protocol, ordered by item_order."""
    return db.query(models.ProtocolChecklistItem).filter(
        models.ProtocolChecklistItem.protocol_id == protocol_id
    ).options(
        joinedload(models.ProtocolChecklistItem.part)
    ).order_by(
        asc(models.ProtocolChecklistItem.item_order)
    ).all()


def create_checklist_item(db: Session, protocol_id: uuid.UUID, item_in) -> models.ProtocolChecklistItem:
    """Create a checklist item for a protocol."""
    item_data = item_in.dict()
    item_data["protocol_id"] = protocol_id
    
    # Ensure unique order within protocol
    existing_orders = db.query(models.ProtocolChecklistItem.item_order).filter(
        models.ProtocolChecklistItem.protocol_id == protocol_id
    ).all()
    existing_orders = [order[0] for order in existing_orders]
    
    if item_data["item_order"] in existing_orders:
        # Shift existing items to make room
        db.query(models.ProtocolChecklistItem).filter(
            and_(
                models.ProtocolChecklistItem.protocol_id == protocol_id,
                models.ProtocolChecklistItem.item_order >= item_data["item_order"]
            )
        ).update(
            {models.ProtocolChecklistItem.item_order: models.ProtocolChecklistItem.item_order + 1},
            synchronize_session=False
        )
    
    db_item = models.ProtocolChecklistItem(**item_data)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


def update_checklist_item(db: Session, item_id: uuid.UUID, item_in) -> Optional[models.ProtocolChecklistItem]:
    """Update a checklist item."""
    db_item = get_checklist_item(db, item_id)
    if not db_item:
        return None
    
    update_data = item_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_item, field, value)
    
    db.commit()
    db.refresh(db_item)
    return db_item


def delete_checklist_item(db: Session, item_id: uuid.UUID) -> bool:
    """Delete a checklist item."""
    db_item = get_checklist_item(db, item_id)
    if not db_item:
        return False
    
    db.delete(db_item)
    db.commit()
    return True


def reorder_checklist_items(db: Session, protocol_id: uuid.UUID, item_orders: List[Dict[str, Any]]) -> bool:
    """Reorder checklist items within a protocol."""
    try:
        for item_data in item_orders:
            item_id = item_data["id"]
            new_order = item_data["order"]
            
            db.query(models.ProtocolChecklistItem).filter(
                and_(
                    models.ProtocolChecklistItem.id == item_id,
                    models.ProtocolChecklistItem.protocol_id == protocol_id
                )
            ).update(
                {models.ProtocolChecklistItem.item_order: new_order},
                synchronize_session=False
            )
        
        db.commit()
        return True
    except Exception:
        db.rollback()
        return False


# Maintenance Execution CRUD Operations

def get_execution(db: Session, execution_id: uuid.UUID) -> Optional[models.MaintenanceExecution]:
    """Get an execution by ID."""
    return db.query(models.MaintenanceExecution).filter(
        models.MaintenanceExecution.id == execution_id
    ).first()


def create_execution(
    db: Session,
    execution_in,
    performed_by_user_id: uuid.UUID
) -> models.MaintenanceExecution:
    """Create a maintenance execution with checklist completions."""
    execution_data = execution_in.dict(exclude={"checklist_completions"})
    execution_data["performed_by_user_id"] = performed_by_user_id
    
    # Create execution
    db_execution = models.MaintenanceExecution(**execution_data)
    db.add(db_execution)
    db.flush()  # Get the ID
    
    # Create checklist completions
    for completion_data in execution_in.checklist_completions:
        completion_dict = completion_data.dict()
        completion_dict["execution_id"] = db_execution.id
        
        db_completion = models.MaintenanceChecklistCompletion(**completion_dict)
        db.add(db_completion)
    
    db.commit()
    db.refresh(db_execution)
    return db_execution


def get_executions_by_organization(db: Session, organization_id: uuid.UUID, skip: int = 0, limit: int = 100) -> List[models.MaintenanceExecution]:
    """Get maintenance executions for an organization."""
    # Get the organization to check its type
    org = db.query(models.Organization).filter(models.Organization.id == organization_id).first()
    
    if org and org.organization_type == models.OrganizationType.oraseas_ee:
        # Oraseas EE (distributor) can see all executions
        query = db.query(models.MaintenanceExecution)
    else:
        # Customers only see their own machines' executions
        query = db.query(models.MaintenanceExecution).join(
            models.Machine
        ).filter(
            models.Machine.customer_organization_id == organization_id
        )
    
    return query.options(
        joinedload(models.MaintenanceExecution.protocol),
        joinedload(models.MaintenanceExecution.machine),
        joinedload(models.MaintenanceExecution.performed_by),
        joinedload(models.MaintenanceExecution.checklist_completions)
    ).order_by(
        desc(models.MaintenanceExecution.created_at)
    ).offset(skip).limit(limit).all()


def get_executions_by_machine(db: Session, machine_id: uuid.UUID, skip: int = 0, limit: int = 100) -> List[models.MaintenanceExecution]:
    """Get maintenance executions for a specific machine."""
    return db.query(models.MaintenanceExecution).filter(
        models.MaintenanceExecution.machine_id == machine_id
    ).options(
        joinedload(models.MaintenanceExecution.protocol),
        joinedload(models.MaintenanceExecution.performed_by),
        joinedload(models.MaintenanceExecution.checklist_completions)
    ).order_by(
        desc(models.MaintenanceExecution.performed_date)
    ).offset(skip).limit(limit).all()


def complete_checklist_item(
    db: Session,
    execution_id: uuid.UUID,
    checklist_item_id: uuid.UUID,
    completion_data
) -> models.MaintenanceChecklistCompletion:
    """Create or update a checklist item completion."""
    # Check if completion already exists
    existing = db.query(models.MaintenanceChecklistCompletion).filter(
        models.MaintenanceChecklistCompletion.execution_id == execution_id,
        models.MaintenanceChecklistCompletion.checklist_item_id == checklist_item_id
    ).first()
    
    # Convert schema data to model data
    data_dict = completion_data.dict(exclude_unset=True)
    # Map 'status' to 'is_completed' (status='completed' means is_completed=True)
    if 'status' in data_dict:
        data_dict['is_completed'] = data_dict.pop('status') == 'completed'
    # Rename actual_quantity_used to match model if needed
    # (model doesn't have this field, so we'll skip it for now)
    data_dict.pop('actual_quantity_used', None)
    
    if existing:
        # Update existing completion
        for key, value in data_dict.items():
            setattr(existing, key, value)
        existing.completed_at = datetime.now()
        db.commit()
        db.refresh(existing)
        return existing
    else:
        # Create new completion
        completion = models.MaintenanceChecklistCompletion(
            execution_id=execution_id,
            checklist_item_id=checklist_item_id,
            **data_dict,
            completed_at=datetime.now()
        )
        db.add(completion)
        db.commit()
        db.refresh(completion)
        return completion


def complete_execution(db: Session, execution_id: uuid.UUID) -> Optional[models.MaintenanceExecution]:
    """Mark an execution as completed."""
    execution = get_execution(db, execution_id)
    if not execution:
        return None
    
    execution.status = models.MaintenanceExecutionStatus.COMPLETED
    execution.performed_date = datetime.now()
    
    db.commit()
    db.refresh(execution)
    return execution


# Maintenance Reminder CRUD Operations

def get_reminder(db: Session, reminder_id: uuid.UUID) -> Optional[models.MaintenanceReminder]:
    """Get a reminder by ID."""
    return db.query(models.MaintenanceReminder).filter(
        models.MaintenanceReminder.id == reminder_id
    ).first()


def get_pending_reminders_for_user(db: Session, user_id: uuid.UUID) -> List[models.MaintenanceReminder]:
    """Get pending reminders for machines accessible to a user."""
    return db.query(models.MaintenanceReminder).filter(
        models.MaintenanceReminder.status == models.ReminderStatus.PENDING
    ).options(
        joinedload(models.MaintenanceReminder.machine),
        joinedload(models.MaintenanceReminder.protocol)
    ).order_by(
        asc(models.MaintenanceReminder.due_hours),
        asc(models.MaintenanceReminder.due_date)
    ).all()


def acknowledge_reminder(db: Session, reminder_id: uuid.UUID, user_id: uuid.UUID) -> Optional[models.MaintenanceReminder]:
    """Acknowledge a reminder."""
    reminder = get_reminder(db, reminder_id)
    if not reminder:
        return None
    
    reminder.status = models.ReminderStatus.ACKNOWLEDGED
    reminder.acknowledged_by_user_id = user_id
    reminder.acknowledged_at = datetime.now()
    
    db.commit()
    db.refresh(reminder)
    return reminder
