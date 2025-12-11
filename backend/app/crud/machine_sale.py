# backend/app/crud/machine_sale.py

import uuid
from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_

from .. import models, schemas
from ..schemas.machine_sale import MachineSaleRequest, MachineSaleResponse

def create_machine_sale(db: Session, machine_sale: MachineSaleRequest) -> models.MachineSale:
    """Create a new machine sale record and update machine ownership"""
    
    # Validate that the machine exists and belongs to the from_organization
    machine = db.query(models.Machine).filter(models.Machine.id == machine_sale.machine_id).first()
    if not machine:
        raise ValueError(f"Machine {machine_sale.machine_id} not found")
    
    if machine.customer_organization_id != machine_sale.from_organization_id:
        raise ValueError(f"Machine {machine_sale.machine_id} does not belong to organization {machine_sale.from_organization_id}")
    
    # Validate organizations exist
    from_org = db.query(models.Organization).filter(models.Organization.id == machine_sale.from_organization_id).first()
    if not from_org:
        raise ValueError(f"From organization {machine_sale.from_organization_id} not found")
    
    to_org = db.query(models.Organization).filter(models.Organization.id == machine_sale.to_organization_id).first()
    if not to_org:
        raise ValueError(f"To organization {machine_sale.to_organization_id} not found")
    
    # Validate user exists
    user = db.query(models.User).filter(models.User.id == machine_sale.performed_by_user_id).first()
    if not user:
        raise ValueError(f"User {machine_sale.performed_by_user_id} not found")
    
    # Create the machine sale record
    db_machine_sale = models.MachineSale(
        machine_id=machine_sale.machine_id,
        from_organization_id=machine_sale.from_organization_id,
        to_organization_id=machine_sale.to_organization_id,
        sale_price=machine_sale.sale_price,
        sale_date=machine_sale.sale_date,
        performed_by_user_id=machine_sale.performed_by_user_id,
        notes=machine_sale.notes,
        reference_number=machine_sale.reference_number
    )
    
    db.add(db_machine_sale)
    
    # Update machine ownership
    machine.customer_organization_id = machine_sale.to_organization_id
    
    db.commit()
    db.refresh(db_machine_sale)
    
    return db_machine_sale

def get_machine_sale(db: Session, machine_sale_id: uuid.UUID) -> Optional[dict]:
    """Get a machine sale by ID with related data"""
    
    machine_sale = db.query(models.MachineSale).filter(models.MachineSale.id == machine_sale_id).first()
    if not machine_sale:
        return None
    
    # Get related data
    machine = db.query(models.Machine).filter(models.Machine.id == machine_sale.machine_id).first()
    from_org = db.query(models.Organization).filter(models.Organization.id == machine_sale.from_organization_id).first()
    to_org = db.query(models.Organization).filter(models.Organization.id == machine_sale.to_organization_id).first()
    user = db.query(models.User).filter(models.User.id == machine_sale.performed_by_user_id).first()
    
    # Build response
    result = {
        **machine_sale.__dict__,
        "machine_serial": machine.serial_number if machine else None,
        "machine_name": machine.name if machine else None,
        "from_organization_name": from_org.name if from_org else None,
        "to_organization_name": to_org.name if to_org else None,
        "performed_by_username": user.username if user else None
    }
    
    return result

def get_machine_sales(db: Session, skip: int = 0, limit: int = 100, organization_id: Optional[uuid.UUID] = None) -> List[dict]:
    """Get machine sales with optional organization filtering"""
    
    query = db.query(models.MachineSale)
    
    # Filter by organization if provided (either from or to organization)
    if organization_id:
        query = query.filter(
            (models.MachineSale.from_organization_id == organization_id) |
            (models.MachineSale.to_organization_id == organization_id)
        )
    
    machine_sales = query.order_by(models.MachineSale.sale_date.desc()).offset(skip).limit(limit).all()
    
    results = []
    for machine_sale in machine_sales:
        # Get related data
        machine = db.query(models.Machine).filter(models.Machine.id == machine_sale.machine_id).first()
        from_org = db.query(models.Organization).filter(models.Organization.id == machine_sale.from_organization_id).first()
        to_org = db.query(models.Organization).filter(models.Organization.id == machine_sale.to_organization_id).first()
        user = db.query(models.User).filter(models.User.id == machine_sale.performed_by_user_id).first()
        
        # Build response
        result = {
            **machine_sale.__dict__,
            "machine_serial": machine.serial_number if machine else None,
            "machine_name": machine.name if machine else None,
            "from_organization_name": from_org.name if from_org else None,
            "to_organization_name": to_org.name if to_org else None,
            "performed_by_username": user.username if user else None
        }
        
        results.append(result)
    
    return results

def get_machine_sales_by_machine(db: Session, machine_id: uuid.UUID) -> List[dict]:
    """Get all sales for a specific machine"""
    
    machine_sales = db.query(models.MachineSale).filter(
        models.MachineSale.machine_id == machine_id
    ).order_by(models.MachineSale.sale_date.desc()).all()
    
    results = []
    for machine_sale in machine_sales:
        # Get related data
        machine = db.query(models.Machine).filter(models.Machine.id == machine_sale.machine_id).first()
        from_org = db.query(models.Organization).filter(models.Organization.id == machine_sale.from_organization_id).first()
        to_org = db.query(models.Organization).filter(models.Organization.id == machine_sale.to_organization_id).first()
        user = db.query(models.User).filter(models.User.id == machine_sale.performed_by_user_id).first()
        
        # Build response
        result = {
            **machine_sale.__dict__,
            "machine_serial": machine.serial_number if machine else None,
            "machine_name": machine.name if machine else None,
            "from_organization_name": from_org.name if from_org else None,
            "to_organization_name": to_org.name if to_org else None,
            "performed_by_username": user.username if user else None
        }
        
        results.append(result)
    
    return results