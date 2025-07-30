# backend/app/crud/part_usage.py

import uuid
from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_

from .. import models, schemas
from ..schemas.part_usage import PartUsageRequest, PartUsageResponse

def create_part_usage(db: Session, part_usage: PartUsageRequest) -> models.PartUsageRecord:
    """Create a new part usage record (machine part consumption)"""
    
    # Validate machine exists
    machine = db.query(models.Machine).filter(models.Machine.id == part_usage.machine_id).first()
    if not machine:
        raise ValueError(f"Machine {part_usage.machine_id} not found")
    
    # Validate warehouse exists and belongs to the same organization as the machine
    warehouse = db.query(models.Warehouse).filter(models.Warehouse.id == part_usage.from_warehouse_id).first()
    if not warehouse:
        raise ValueError(f"Warehouse {part_usage.from_warehouse_id} not found")
    
    if warehouse.organization_id != machine.customer_organization_id:
        raise ValueError(f"Warehouse {part_usage.from_warehouse_id} does not belong to the same organization as machine {part_usage.machine_id}")
    
    # Validate user exists
    user = db.query(models.User).filter(models.User.id == part_usage.performed_by_user_id).first()
    if not user:
        raise ValueError(f"User {part_usage.performed_by_user_id} not found")
    
    # Validate all parts exist and have sufficient inventory
    for item in part_usage.usage_items:
        part = db.query(models.Part).filter(models.Part.id == item.part_id).first()
        if not part:
            raise ValueError(f"Part {item.part_id} not found")
        
        # Check inventory availability
        inventory_item = db.query(models.Inventory).filter(
            and_(
                models.Inventory.warehouse_id == part_usage.from_warehouse_id,
                models.Inventory.part_id == item.part_id
            )
        ).first()
        
        if not inventory_item or inventory_item.current_stock < item.quantity:
            available_stock = inventory_item.current_stock if inventory_item else 0
            raise ValueError(f"Insufficient stock for part {item.part_id}. Available: {available_stock}, Required: {item.quantity}")
    
    # Create the part usage record
    db_part_usage = models.PartUsageRecord(
        machine_id=part_usage.machine_id,
        from_warehouse_id=part_usage.from_warehouse_id,
        usage_date=part_usage.usage_date,
        performed_by_user_id=part_usage.performed_by_user_id,
        service_type=part_usage.service_type,
        machine_hours=part_usage.machine_hours,
        notes=part_usage.notes,
        reference_number=part_usage.reference_number
    )
    
    db.add(db_part_usage)
    db.flush()  # Get the ID
    
    # Create usage items and corresponding transactions
    for item in part_usage.usage_items:
        # Create usage item
        db_usage_item = models.PartUsageItem(
            usage_record_id=db_part_usage.id,
            part_id=item.part_id,
            quantity=item.quantity,
            notes=item.notes
        )
        db.add(db_usage_item)
        
        # Create consumption transaction
        part = db.query(models.Part).filter(models.Part.id == item.part_id).first()
        
        transaction = models.Transaction(
            transaction_type=models.TransactionType.CONSUMPTION.value,
            part_id=item.part_id,
            from_warehouse_id=part_usage.from_warehouse_id,
            machine_id=part_usage.machine_id,
            quantity=item.quantity,
            unit_of_measure=part.unit_of_measure,
            performed_by_user_id=part_usage.performed_by_user_id,
            transaction_date=part_usage.usage_date,
            notes=f"Part usage in machine - Service: {part_usage.service_type or 'General'}",
            reference_number=part_usage.reference_number
        )
        db.add(transaction)
        
        # Update inventory
        inventory_item = db.query(models.Inventory).filter(
            and_(
                models.Inventory.warehouse_id == part_usage.from_warehouse_id,
                models.Inventory.part_id == item.part_id
            )
        ).first()
        
        if inventory_item:
            inventory_item.current_stock -= item.quantity
            inventory_item.last_updated = part_usage.usage_date
    
    # Record machine hours if provided
    if part_usage.machine_hours is not None:
        machine_hours_record = models.MachineHours(
            machine_id=part_usage.machine_id,
            recorded_by_user_id=part_usage.performed_by_user_id,
            hours_value=part_usage.machine_hours,
            recorded_date=part_usage.usage_date,
            notes=f"Recorded during part usage - Service: {part_usage.service_type or 'General'}"
        )
        db.add(machine_hours_record)
    
    db.commit()
    db.refresh(db_part_usage)
    
    return db_part_usage

def get_part_usage(db: Session, usage_id: uuid.UUID) -> Optional[dict]:
    """Get a part usage record by ID with related data"""
    
    usage = db.query(models.PartUsageRecord).filter(models.PartUsageRecord.id == usage_id).first()
    if not usage:
        return None
    
    # Get related data
    machine = db.query(models.Machine).filter(models.Machine.id == usage.machine_id).first()
    warehouse = db.query(models.Warehouse).filter(models.Warehouse.id == usage.from_warehouse_id).first()
    user = db.query(models.User).filter(models.User.id == usage.performed_by_user_id).first()
    
    # Get usage items
    usage_items = db.query(models.PartUsageItem).filter(models.PartUsageItem.usage_record_id == usage.id).all()
    
    items_data = []
    for item in usage_items:
        part = db.query(models.Part).filter(models.Part.id == item.part_id).first()
        item_data = {
            **item.__dict__,
            "part_name": part.name if part else None,
            "part_number": part.part_number if part else None,
            "unit_of_measure": part.unit_of_measure if part else None
        }
        items_data.append(item_data)
    
    # Build response
    result = {
        **usage.__dict__,
        "machine_serial": machine.serial_number if machine else None,
        "machine_name": machine.name if machine else None,
        "from_warehouse_name": warehouse.name if warehouse else None,
        "performed_by_username": user.username if user else None,
        "usage_items": items_data,
        "total_items": len(items_data)
    }
    
    return result

def get_part_usages(db: Session, skip: int = 0, limit: int = 100, organization_id: Optional[uuid.UUID] = None, machine_id: Optional[uuid.UUID] = None) -> List[dict]:
    """Get part usage records with optional filtering"""
    
    query = db.query(models.PartUsageRecord)
    
    # Filter by machine if provided
    if machine_id:
        query = query.filter(models.PartUsageRecord.machine_id == machine_id)
    
    # Filter by organization if provided
    if organization_id:
        # Get all machines and warehouses for the organization
        machines = db.query(models.Machine).filter(models.Machine.customer_organization_id == organization_id).all()
        machine_ids = [m.id for m in machines]
        
        warehouses = db.query(models.Warehouse).filter(models.Warehouse.organization_id == organization_id).all()
        warehouse_ids = [w.id for w in warehouses]
        
        query = query.filter(
            (models.PartUsageRecord.machine_id.in_(machine_ids)) |
            (models.PartUsageRecord.from_warehouse_id.in_(warehouse_ids))
        )
    
    usages = query.order_by(models.PartUsageRecord.usage_date.desc()).offset(skip).limit(limit).all()
    
    results = []
    for usage in usages:
        # Get related data
        machine = db.query(models.Machine).filter(models.Machine.id == usage.machine_id).first()
        warehouse = db.query(models.Warehouse).filter(models.Warehouse.id == usage.from_warehouse_id).first()
        user = db.query(models.User).filter(models.User.id == usage.performed_by_user_id).first()
        
        # Get usage items count
        usage_items_count = db.query(models.PartUsageItem).filter(models.PartUsageItem.usage_record_id == usage.id).count()
        
        # Build response
        result = {
            **usage.__dict__,
            "machine_serial": machine.serial_number if machine else None,
            "machine_name": machine.name if machine else None,
            "from_warehouse_name": warehouse.name if warehouse else None,
            "performed_by_username": user.username if user else None,
            "total_items": usage_items_count
        }
        
        results.append(result)
    
    return results

def get_part_usages_by_machine(db: Session, machine_id: uuid.UUID, skip: int = 0, limit: int = 100) -> List[dict]:
    """Get all part usage records for a specific machine"""
    
    return get_part_usages(db, skip=skip, limit=limit, machine_id=machine_id)

def get_part_usage_summary(db: Session, days: int = 30, organization_id: Optional[uuid.UUID] = None) -> dict:
    """Get part usage summary statistics"""
    
    from datetime import timedelta
    from sqlalchemy import func
    
    # Calculate the start date for the summary period
    start_date = datetime.now() - timedelta(days=days)
    
    query = db.query(models.PartUsageRecord).filter(models.PartUsageRecord.usage_date >= start_date)
    
    # Filter by organization if provided
    if organization_id:
        machines = db.query(models.Machine).filter(models.Machine.customer_organization_id == organization_id).all()
        machine_ids = [m.id for m in machines]
        query = query.filter(models.PartUsageRecord.machine_id.in_(machine_ids))
    
    total_usage_records = query.count()
    
    # Get service type breakdown
    service_type_counts = db.query(
        models.PartUsageRecord.service_type,
        func.count(models.PartUsageRecord.id).label("count")
    ).filter(
        models.PartUsageRecord.usage_date >= start_date
    ).group_by(
        models.PartUsageRecord.service_type
    )
    
    if organization_id:
        service_type_counts = service_type_counts.filter(models.PartUsageRecord.machine_id.in_(machine_ids))
    
    service_breakdown = {st.service_type or 'General': st.count for st in service_type_counts.all()}
    
    return {
        "period_days": days,
        "total_usage_records": total_usage_records,
        "daily_average": total_usage_records / days if days > 0 else 0,
        "service_type_breakdown": service_breakdown
    }