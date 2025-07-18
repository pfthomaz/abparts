# backend/app/crud/machines.py

import uuid
import logging
from typing import List, Optional, Dict, Any
from datetime import datetime

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc
from fastapi import HTTPException, status

from .. import models, schemas

logger = logging.getLogger(__name__)

def get_machine(db: Session, machine_id: uuid.UUID):
    """Retrieve a single machine by ID."""
    machine = db.query(
        models.Machine,
        models.Organization.name.label("customer_organization_name")
    ).join(
        models.Organization, models.Machine.customer_organization_id == models.Organization.id
    ).filter(
        models.Machine.id == machine_id
    ).first()
    
    if not machine:
        return None
    
    # Extract the machine and related data
    machine_obj, customer_organization_name = machine
    
    # Create a dictionary with all the data
    result = {
        **machine_obj.__dict__,
        "customer_organization_name": customer_organization_name
    }
    
    return result

def get_machines(db: Session, skip: int = 0, limit: int = 100, organization_id: Optional[uuid.UUID] = None):
    """
    Retrieve a list of machines, optionally filtered by organization ID.
    This function handles the database query and filtering.
    Authentication/Authorization is handled in the router.
    """
    query = db.query(
        models.Machine,
        models.Organization.name.label("customer_organization_name")
    ).join(
        models.Organization, models.Machine.customer_organization_id == models.Organization.id
    )
    
    if organization_id:
        query = query.filter(models.Machine.customer_organization_id == organization_id)
    
    machines = query.order_by(models.Machine.created_at.desc()).offset(skip).limit(limit).all()
    
    results = []
    for machine, customer_organization_name in machines:
        # Create a dictionary with all the data
        result = {
            **machine.__dict__,
            "customer_organization_name": customer_organization_name
        }
        
        results.append(result)
    
    return results

def create_machine(db: Session, machine: schemas.MachineCreate):
    """Create a new machine."""
    # Check if organization_id exists BEFORE creating the machine
    organization = db.query(models.Organization).filter(models.Organization.id == machine.customer_organization_id).first()
    if not organization:
        raise HTTPException(status_code=400, detail="Organization ID not found")
    
    # Ensure the organization is a customer organization
    if organization.organization_type != models.OrganizationType.CUSTOMER:
        raise HTTPException(status_code=400, detail="Machines can only be assigned to customer organizations")

    db_machine = models.Machine(**machine.dict())
    try:
        db.add(db_machine)
        db.commit()
        db.refresh(db_machine)
        
        # Create a machine sale transaction
        transaction = models.Transaction(
            transaction_type=models.TransactionType.CREATION,
            part_id=None,  # No part involved in machine sale
            to_warehouse_id=None,  # No warehouse involved in machine sale
            machine_id=db_machine.id,
            quantity=1,  # One machine
            unit_of_measure="unit",
            performed_by_user_id=db.query(models.User).filter(models.User.role == models.UserRole.super_admin).first().id,
            transaction_date=datetime.now(),
            notes=f"Machine sale: {db_machine.model_type} ({db_machine.serial_number}) to {organization.name}",
            reference_number=f"MACHINE-SALE-{db_machine.serial_number}"
        )
        db.add(transaction)
        db.commit()
        
        # Get the machine with organization name
        result = get_machine(db, db_machine.id)
        return result
    except Exception as e:
        db.rollback()
        # Specific error handling for unique constraint violation
        if "duplicate key value violates unique constraint" in str(e).lower() and "serial_number" in str(e).lower():
            raise HTTPException(status_code=409, detail="Machine with this serial number already exists")
        logger.error(f"Error creating machine: {e}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred while creating the machine.")

def update_machine(db: Session, machine_id: uuid.UUID, machine_update: schemas.MachineUpdate):
    """Update an existing machine."""
    db_machine = db.query(models.Machine).filter(models.Machine.id == machine_id).first()
    if not db_machine:
        return None

    update_data = machine_update.dict(exclude_unset=True)

    # If customer_organization_id is being updated, check if the new ID exists and is a customer
    if "customer_organization_id" in update_data and update_data["customer_organization_id"] != db_machine.customer_organization_id:
        organization = db.query(models.Organization).filter(models.Organization.id == update_data["customer_organization_id"]).first()
        if not organization:
            raise HTTPException(status_code=400, detail="New Organization ID not found for machine update")
        if organization.organization_type != models.OrganizationType.CUSTOMER:
            raise HTTPException(status_code=400, detail="Machines can only be assigned to customer organizations")

    for key, value in update_data.items():
        setattr(db_machine, key, value)
    
    try:
        db.add(db_machine) # Re-add to session to mark as dirty for update
        db.commit()
        db.refresh(db_machine)
        
        # Get the machine with organization name
        result = get_machine(db, db_machine.id)
        return result
    except Exception as e:
        db.rollback()
        if "duplicate key value violates unique constraint" in str(e).lower() and "serial_number" in str(e).lower():
            raise HTTPException(status_code=409, detail="Machine with this serial number already exists")
        logger.error(f"Error updating machine: {e}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred while updating the machine.")

def delete_machine(db: Session, machine_id: uuid.UUID):
    """Delete a machine by ID."""
    db_machine = db.query(models.Machine).filter(models.Machine.id == machine_id).first()
    if not db_machine:
        return None
    try:
        db.delete(db_machine)
        db.commit()
        return {"message": "Machine deleted successfully"}
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting machine: {e}")
        # Provide a more specific error if it's due to foreign key constraints
        if "violates foreign key constraint" in str(e).lower():
            raise HTTPException(status_code=400, detail="Cannot delete machine due to existing dependent records (e.g., part usage). Please delete associated records first.")
        raise HTTPException(status_code=500, detail="An unexpected error occurred while deleting the machine.")

def transfer_machine(db: Session, transfer: schemas.MachineTransferRequest):
    """Transfer a machine to a new customer organization."""
    # Get the machine
    db_machine = db.query(models.Machine).filter(models.Machine.id == transfer.machine_id).first()
    if not db_machine:
        raise HTTPException(status_code=404, detail="Machine not found")
    
    # Get the new organization
    new_organization = db.query(models.Organization).filter(models.Organization.id == transfer.new_customer_organization_id).first()
    if not new_organization:
        raise HTTPException(status_code=400, detail="New organization not found")
    
    # Ensure the new organization is a customer organization
    if new_organization.organization_type != models.OrganizationType.CUSTOMER:
        raise HTTPException(status_code=400, detail="Machines can only be transferred to customer organizations")
    
    # Get the old organization for the transaction notes
    old_organization = db.query(models.Organization).filter(models.Organization.id == db_machine.customer_organization_id).first()
    
    try:
        # Update the machine's customer_organization_id
        db_machine.customer_organization_id = transfer.new_customer_organization_id
        
        # Add a note about the transfer
        if db_machine.notes:
            db_machine.notes += f"\n\nTransferred from {old_organization.name} to {new_organization.name} on {transfer.transfer_date.strftime('%Y-%m-%d')}"
            if transfer.transfer_notes:
                db_machine.notes += f": {transfer.transfer_notes}"
        else:
            db_machine.notes = f"Transferred from {old_organization.name} to {new_organization.name} on {transfer.transfer_date.strftime('%Y-%m-%d')}"
            if transfer.transfer_notes:
                db_machine.notes += f": {transfer.transfer_notes}"
        
        # Create a transaction record for the transfer
        transaction = models.Transaction(
            transaction_type=models.TransactionType.TRANSFER,
            part_id=None,  # No part involved in machine transfer
            from_warehouse_id=None,  # No warehouse involved in machine transfer
            to_warehouse_id=None,  # No warehouse involved in machine transfer
            machine_id=db_machine.id,
            quantity=1,  # One machine
            unit_of_measure="unit",
            performed_by_user_id=db.query(models.User).filter(models.User.role == models.UserRole.super_admin).first().id,
            transaction_date=transfer.transfer_date,
            notes=f"Machine transfer: {db_machine.model_type} ({db_machine.serial_number}) from {old_organization.name} to {new_organization.name}",
            reference_number=f"MACHINE-TRANSFER-{db_machine.serial_number}"
        )
        
        db.add(db_machine)
        db.add(transaction)
        db.commit()
        db.refresh(db_machine)
        
        # Get the machine with organization name
        result = get_machine(db, db_machine.id)
        return result
    except Exception as e:
        db.rollback()
        logger.error(f"Error transferring machine: {e}")
        raise HTTPException(status_code=500, detail=f"Error transferring machine: {str(e)}")

def get_machine_maintenance_history(db: Session, machine_id: uuid.UUID, skip: int = 0, limit: int = 100):
    """Get maintenance history for a specific machine."""
    # Check if machine exists
    machine = db.query(models.Machine).filter(models.Machine.id == machine_id).first()
    if not machine:
        raise HTTPException(status_code=404, detail="Machine not found")
    
    # Get maintenance records
    maintenance_records = db.query(
        models.MachineMaintenance,
        models.User.username.label("performed_by_username")
    ).join(
        models.User, models.MachineMaintenance.performed_by_user_id == models.User.id
    ).filter(
        models.MachineMaintenance.machine_id == machine_id
    ).order_by(
        desc(models.MachineMaintenance.maintenance_date)
    ).offset(skip).limit(limit).all()
    
    results = []
    for maintenance, performed_by_username in maintenance_records:
        # Create a dictionary with all the data
        result = {
            **maintenance.__dict__,
            "performed_by_username": performed_by_username,
            "machine_name": machine.name,
            "machine_serial_number": machine.serial_number
        }
        
        results.append(result)
    
    return results

def create_machine_maintenance(db: Session, maintenance: schemas.MaintenanceCreate):
    """Create a new maintenance record for a machine."""
    # Check if machine exists
    machine = db.query(models.Machine).filter(models.Machine.id == maintenance.machine_id).first()
    if not machine:
        raise HTTPException(status_code=404, detail="Machine not found")
    
    # Check if user exists
    user = db.query(models.User).filter(models.User.id == maintenance.performed_by_user_id).first()
    if not user:
        raise HTTPException(status_code=400, detail="User not found")
    
    db_maintenance = models.MachineMaintenance(**maintenance.dict())
    try:
        db.add(db_maintenance)
        
        # Update the machine's last_maintenance_date and next_maintenance_date
        machine.last_maintenance_date = maintenance.maintenance_date
        if maintenance.next_maintenance_date:
            machine.next_maintenance_date = maintenance.next_maintenance_date
        
        db.commit()
        db.refresh(db_maintenance)
        
        # Get the maintenance record with related data
        result = {
            **db_maintenance.__dict__,
            "performed_by_username": user.username,
            "machine_name": machine.name,
            "machine_serial_number": machine.serial_number
        }
        
        return result
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating maintenance record: {e}")
        raise HTTPException(status_code=500, detail=f"Error creating maintenance record: {str(e)}")

def add_part_to_maintenance(db: Session, part_usage: schemas.MaintenancePartUsageCreate):
    """Add a part to a maintenance record."""
    # Check if maintenance record exists
    maintenance = db.query(models.MachineMaintenance).filter(models.MachineMaintenance.id == part_usage.maintenance_id).first()
    if not maintenance:
        raise HTTPException(status_code=404, detail="Maintenance record not found")
    
    # Check if part exists
    part = db.query(models.Part).filter(models.Part.id == part_usage.part_id).first()
    if not part:
        raise HTTPException(status_code=400, detail="Part not found")
    
    # Check if warehouse exists
    warehouse = db.query(models.Warehouse).filter(models.Warehouse.id == part_usage.warehouse_id).first()
    if not warehouse:
        raise HTTPException(status_code=400, detail="Warehouse not found")
    
    # Check if there's enough stock in the warehouse
    inventory = db.query(models.Inventory).filter(
        models.Inventory.warehouse_id == part_usage.warehouse_id,
        models.Inventory.part_id == part_usage.part_id
    ).first()
    
    if not inventory or inventory.current_stock < part_usage.quantity:
        raise HTTPException(status_code=400, detail="Insufficient stock in warehouse")
    
    db_part_usage = models.MaintenancePartUsage(**part_usage.dict())
    try:
        db.add(db_part_usage)
        
        # Create a transaction for the part consumption
        transaction = models.Transaction(
            transaction_type=models.TransactionType.CONSUMPTION,
            part_id=part_usage.part_id,
            from_warehouse_id=part_usage.warehouse_id,
            machine_id=maintenance.machine_id,
            quantity=part_usage.quantity,
            unit_of_measure=part.unit_of_measure,
            performed_by_user_id=maintenance.performed_by_user_id,
            transaction_date=maintenance.maintenance_date,
            notes=f"Part used in maintenance: {part.name} for {maintenance.maintenance_type.value} maintenance",
            reference_number=f"MAINT-PART-{uuid.uuid4().hex[:8]}"
        )
        db.add(transaction)
        
        db.commit()
        db.refresh(db_part_usage)
        
        # Get the part usage record with related data
        result = {
            **db_part_usage.__dict__,
            "part_number": part.part_number,
            "part_name": part.name,
            "warehouse_name": warehouse.name
        }
        
        return result
    except Exception as e:
        db.rollback()
        logger.error(f"Error adding part to maintenance: {e}")
        raise HTTPException(status_code=500, detail=f"Error adding part to maintenance: {str(e)}")

def get_machine_part_compatibility(db: Session, machine_id: uuid.UUID, skip: int = 0, limit: int = 100):
    """Get compatible parts for a specific machine."""
    # Check if machine exists
    machine = db.query(models.Machine).filter(models.Machine.id == machine_id).first()
    if not machine:
        raise HTTPException(status_code=404, detail="Machine not found")
    
    # Get compatible parts
    compatibility_records = db.query(
        models.MachinePartCompatibility,
        models.Part.part_number.label("part_number"),
        models.Part.name.label("part_name")
    ).join(
        models.Part, models.MachinePartCompatibility.part_id == models.Part.id
    ).filter(
        models.MachinePartCompatibility.machine_id == machine_id
    ).order_by(
        models.MachinePartCompatibility.is_recommended.desc(),
        models.Part.part_number
    ).offset(skip).limit(limit).all()
    
    results = []
    for compatibility, part_number, part_name in compatibility_records:
        # Create a dictionary with all the data
        result = {
            **compatibility.__dict__,
            "part_number": part_number,
            "part_name": part_name,
            "machine_name": machine.name,
            "machine_model_type": machine.model_type
        }
        
        results.append(result)
    
    return results

def add_compatible_part(db: Session, compatibility: schemas.MachinePartCompatibilityCreate):
    """Add a compatible part to a machine."""
    # Check if machine exists
    machine = db.query(models.Machine).filter(models.Machine.id == compatibility.machine_id).first()
    if not machine:
        raise HTTPException(status_code=404, detail="Machine not found")
    
    # Check if part exists
    part = db.query(models.Part).filter(models.Part.id == compatibility.part_id).first()
    if not part:
        raise HTTPException(status_code=400, detail="Part not found")
    
    # Check if compatibility record already exists
    existing_compatibility = db.query(models.MachinePartCompatibility).filter(
        models.MachinePartCompatibility.machine_id == compatibility.machine_id,
        models.MachinePartCompatibility.part_id == compatibility.part_id
    ).first()
    
    if existing_compatibility:
        raise HTTPException(status_code=409, detail="Part is already marked as compatible with this machine")
    
    db_compatibility = models.MachinePartCompatibility(**compatibility.dict())
    try:
        db.add(db_compatibility)
        db.commit()
        db.refresh(db_compatibility)
        
        # Get the compatibility record with related data
        result = {
            **db_compatibility.__dict__,
            "part_number": part.part_number,
            "part_name": part.name,
            "machine_name": machine.name,
            "machine_model_type": machine.model_type
        }
        
        return result
    except Exception as e:
        db.rollback()
        logger.error(f"Error adding compatible part: {e}")
        raise HTTPException(status_code=500, detail=f"Error adding compatible part: {str(e)}")

def remove_compatible_part(db: Session, machine_id: uuid.UUID, part_id: uuid.UUID):
    """Remove a compatible part from a machine."""
    # Check if compatibility record exists
    compatibility = db.query(models.MachinePartCompatibility).filter(
        models.MachinePartCompatibility.machine_id == machine_id,
        models.MachinePartCompatibility.part_id == part_id
    ).first()
    
    if not compatibility:
        raise HTTPException(status_code=404, detail="Part is not marked as compatible with this machine")
    
    try:
        db.delete(compatibility)
        db.commit()
        return {"message": "Compatible part removed successfully"}
    except Exception as e:
        db.rollback()
        logger.error(f"Error removing compatible part: {e}")
        raise HTTPException(status_code=500, detail=f"Error removing compatible part: {str(e)}")

def get_machine_usage_history(db: Session, machine_id: uuid.UUID, skip: int = 0, limit: int = 100):
    """Get part usage history for a specific machine."""
    # Check if machine exists
    machine = db.query(models.Machine).filter(models.Machine.id == machine_id).first()
    if not machine:
        raise HTTPException(status_code=404, detail="Machine not found")
    
    # Get part usage records
    usage_records = db.query(
        models.PartUsage,
        models.Part.part_number.label("part_number"),
        models.Part.name.label("part_name"),
        models.User.username.label("recorded_by_username")
    ).join(
        models.Part, models.PartUsage.part_id == models.Part.id
    ).outerjoin(
        models.User, models.PartUsage.recorded_by_user_id == models.User.id
    ).filter(
        models.PartUsage.machine_id == machine_id
    ).order_by(
        desc(models.PartUsage.usage_date)
    ).offset(skip).limit(limit).all()
    
    results = []
    for usage, part_number, part_name, recorded_by_username in usage_records:
        # Create a dictionary with all the data
        result = {
            **usage.__dict__,
            "part_number": part_number,
            "part_name": part_name,
            "recorded_by_username": recorded_by_username,
            "machine_name": machine.name
        }
        
        results.append(result)
    
    return results

