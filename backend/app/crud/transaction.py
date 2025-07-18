# backend/app/crud/transaction.py

import uuid
import logging
from typing import List, Optional, Dict, Any
from decimal import Decimal
from datetime import datetime, timedelta

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc, text
from fastapi import HTTPException, status

from .. import models, schemas

logger = logging.getLogger(__name__)

def get_transaction(db: Session, transaction_id: uuid.UUID):
    """Retrieve a single transaction by ID."""
    transaction = db.query(
        models.Transaction,
        models.Part.name.label("part_name"),
        models.Part.part_number.label("part_number"),
        models.User.username.label("performed_by_username")
    ).join(
        models.Part, models.Transaction.part_id == models.Part.id
    ).join(
        models.User, models.Transaction.performed_by_user_id == models.User.id
    ).outerjoin(
        models.Warehouse, models.Transaction.from_warehouse_id == models.Warehouse.id, 
        aliased=True
    ).outerjoin(
        models.Warehouse, models.Transaction.to_warehouse_id == models.Warehouse.id,
        aliased=True
    ).outerjoin(
        models.Machine, models.Transaction.machine_id == models.Machine.id
    ).filter(
        models.Transaction.id == transaction_id
    ).first()
    
    if not transaction:
        return None
    
    # Extract the transaction and related data
    transaction_obj, part_name, part_number, performed_by_username = transaction
    
    # Get warehouse names if they exist
    from_warehouse_name = None
    if transaction_obj.from_warehouse_id:
        from_warehouse = db.query(models.Warehouse).filter(models.Warehouse.id == transaction_obj.from_warehouse_id).first()
        if from_warehouse:
            from_warehouse_name = from_warehouse.name
    
    to_warehouse_name = None
    if transaction_obj.to_warehouse_id:
        to_warehouse = db.query(models.Warehouse).filter(models.Warehouse.id == transaction_obj.to_warehouse_id).first()
        if to_warehouse:
            to_warehouse_name = to_warehouse.name
    
    # Get machine serial if it exists
    machine_serial = None
    if transaction_obj.machine_id:
        machine = db.query(models.Machine).filter(models.Machine.id == transaction_obj.machine_id).first()
        if machine:
            machine_serial = machine.serial_number
    
    # Create a dictionary with all the data
    result = {
        **transaction_obj.__dict__,
        "part_name": part_name,
        "part_number": part_number,
        "from_warehouse_name": from_warehouse_name,
        "to_warehouse_name": to_warehouse_name,
        "machine_serial": machine_serial,
        "performed_by_username": performed_by_username
    }
    
    return result

def get_transactions(db: Session, skip: int = 0, limit: int = 100):
    """Retrieve a list of transactions."""
    transactions = db.query(
        models.Transaction,
        models.Part.name.label("part_name"),
        models.Part.part_number.label("part_number"),
        models.User.username.label("performed_by_username")
    ).join(
        models.Part, models.Transaction.part_id == models.Part.id
    ).join(
        models.User, models.Transaction.performed_by_user_id == models.User.id
    ).order_by(
        desc(models.Transaction.transaction_date)
    ).offset(skip).limit(limit).all()
    
    results = []
    for transaction, part_name, part_number, performed_by_username in transactions:
        # Get warehouse names if they exist
        from_warehouse_name = None
        if transaction.from_warehouse_id:
            from_warehouse = db.query(models.Warehouse).filter(models.Warehouse.id == transaction.from_warehouse_id).first()
            if from_warehouse:
                from_warehouse_name = from_warehouse.name
        
        to_warehouse_name = None
        if transaction.to_warehouse_id:
            to_warehouse = db.query(models.Warehouse).filter(models.Warehouse.id == transaction.to_warehouse_id).first()
            if to_warehouse:
                to_warehouse_name = to_warehouse.name
        
        # Get machine serial if it exists
        machine_serial = None
        if transaction.machine_id:
            machine = db.query(models.Machine).filter(models.Machine.id == transaction.machine_id).first()
            if machine:
                machine_serial = machine.serial_number
        
        # Create a dictionary with all the data
        result = {
            **transaction.__dict__,
            "part_name": part_name,
            "part_number": part_number,
            "from_warehouse_name": from_warehouse_name,
            "to_warehouse_name": to_warehouse_name,
            "machine_serial": machine_serial,
            "performed_by_username": performed_by_username
        }
        
        results.append(result)
    
    return results

def create_transaction(db: Session, transaction: schemas.TransactionCreate):
    """Create a new transaction."""
    # Validate transaction data based on transaction type
    validate_transaction_data(transaction)
    
    # Create the transaction
    db_transaction = models.Transaction(**transaction.dict())
    
    try:
        # Add the transaction to the database
        db.add(db_transaction)
        
        # Update inventory based on transaction type
        update_inventory_from_transaction(db, db_transaction)
        
        # Commit the transaction
        db.commit()
        db.refresh(db_transaction)
        return db_transaction
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating transaction: {e}")
        raise HTTPException(status_code=400, detail=f"Error creating transaction: {str(e)}")

def validate_transaction_data(transaction: schemas.TransactionCreate):
    """Validate transaction data based on transaction type."""
    if transaction.transaction_type == schemas.TransactionTypeEnum.CREATION:
        # Creation requires to_warehouse_id
        if not transaction.to_warehouse_id:
            raise ValueError("Creation transaction requires to_warehouse_id")
        # Creation should not have from_warehouse_id
        if transaction.from_warehouse_id:
            raise ValueError("Creation transaction should not have from_warehouse_id")
    
    elif transaction.transaction_type == schemas.TransactionTypeEnum.TRANSFER:
        # Transfer requires both from_warehouse_id and to_warehouse_id
        if not transaction.from_warehouse_id or not transaction.to_warehouse_id:
            raise ValueError("Transfer transaction requires both from_warehouse_id and to_warehouse_id")
        # Transfer should not have machine_id
        if transaction.machine_id:
            raise ValueError("Transfer transaction should not have machine_id")
    
    elif transaction.transaction_type == schemas.TransactionTypeEnum.CONSUMPTION:
        # Consumption requires from_warehouse_id
        if not transaction.from_warehouse_id:
            raise ValueError("Consumption transaction requires from_warehouse_id")
        # Consumption should not have to_warehouse_id
        if transaction.to_warehouse_id:
            raise ValueError("Consumption transaction should not have to_warehouse_id")
    
    elif transaction.transaction_type == schemas.TransactionTypeEnum.ADJUSTMENT:
        # Adjustment requires from_warehouse_id
        if not transaction.from_warehouse_id:
            raise ValueError("Adjustment transaction requires from_warehouse_id")
        # Adjustment should not have to_warehouse_id or machine_id
        if transaction.to_warehouse_id:
            raise ValueError("Adjustment transaction should not have to_warehouse_id")
        if transaction.machine_id:
            raise ValueError("Adjustment transaction should not have machine_id")
    
    # Quantity must be positive
    if transaction.quantity <= 0:
        raise ValueError("Transaction quantity must be positive")

def update_inventory_from_transaction(db: Session, transaction: models.Transaction):
    """Update inventory based on transaction type."""
    if transaction.transaction_type == models.TransactionType.CREATION:
        # Increase inventory in to_warehouse
        update_inventory(db, transaction.to_warehouse_id, transaction.part_id, transaction.quantity)
    
    elif transaction.transaction_type == models.TransactionType.TRANSFER:
        # Decrease inventory in from_warehouse
        update_inventory(db, transaction.from_warehouse_id, transaction.part_id, -transaction.quantity)
        # Increase inventory in to_warehouse
        update_inventory(db, transaction.to_warehouse_id, transaction.part_id, transaction.quantity)
    
    elif transaction.transaction_type == models.TransactionType.CONSUMPTION:
        # Decrease inventory in from_warehouse
        update_inventory(db, transaction.from_warehouse_id, transaction.part_id, -transaction.quantity)
    
    elif transaction.transaction_type == models.TransactionType.ADJUSTMENT:
        # Adjust inventory in from_warehouse (can be positive or negative)
        update_inventory(db, transaction.from_warehouse_id, transaction.part_id, transaction.quantity)

def update_inventory(db: Session, warehouse_id: uuid.UUID, part_id: uuid.UUID, quantity: Decimal):
    """Update inventory for a part in a warehouse."""
    # Get the inventory item
    inventory_item = db.query(models.Inventory).filter(
        models.Inventory.warehouse_id == warehouse_id,
        models.Inventory.part_id == part_id
    ).first()
    
    if inventory_item:
        # Update existing inventory
        inventory_item.current_stock += quantity
        inventory_item.last_updated = datetime.now()
        
        # Ensure stock doesn't go below zero
        if inventory_item.current_stock < 0:
            raise ValueError(f"Insufficient stock for part {part_id} in warehouse {warehouse_id}")
    else:
        # Create new inventory item if it doesn't exist (only for positive quantities)
        if quantity <= 0:
            raise ValueError(f"Cannot create inventory with negative quantity for part {part_id} in warehouse {warehouse_id}")
        
        # Get part details for unit_of_measure
        part = db.query(models.Part).filter(models.Part.id == part_id).first()
        if not part:
            raise ValueError(f"Part {part_id} not found")
        
        # Create new inventory item
        inventory_item = models.Inventory(
            warehouse_id=warehouse_id,
            part_id=part_id,
            current_stock=quantity,
            unit_of_measure=part.unit_of_measure
        )
        db.add(inventory_item)

def search_transactions(db: Session, filters: schemas.TransactionFilter, skip: int = 0, limit: int = 100):
    """Search transactions with filters."""
    # Start with base query
    query = db.query(
        models.Transaction,
        models.Part.name.label("part_name"),
        models.Part.part_number.label("part_number"),
        models.User.username.label("performed_by_username")
    ).join(
        models.Part, models.Transaction.part_id == models.Part.id
    ).join(
        models.User, models.Transaction.performed_by_user_id == models.User.id
    )
    
    # Apply filters
    if filters.transaction_type:
        query = query.filter(models.Transaction.transaction_type == filters.transaction_type)
    
    if filters.part_id:
        query = query.filter(models.Transaction.part_id == filters.part_id)
    
    if filters.from_warehouse_id:
        query = query.filter(models.Transaction.from_warehouse_id == filters.from_warehouse_id)
    
    if filters.to_warehouse_id:
        query = query.filter(models.Transaction.to_warehouse_id == filters.to_warehouse_id)
    
    if filters.machine_id:
        query = query.filter(models.Transaction.machine_id == filters.machine_id)
    
    if filters.performed_by_user_id:
        query = query.filter(models.Transaction.performed_by_user_id == filters.performed_by_user_id)
    
    if filters.start_date:
        query = query.filter(models.Transaction.transaction_date >= filters.start_date)
    
    if filters.end_date:
        query = query.filter(models.Transaction.transaction_date <= filters.end_date)
    
    if filters.reference_number:
        query = query.filter(models.Transaction.reference_number.ilike(f"%{filters.reference_number}%"))
    
    # Order by transaction date (most recent first)
    query = query.order_by(desc(models.Transaction.transaction_date))
    
    # Apply pagination
    transactions = query.offset(skip).limit(limit).all()
    
    results = []
    for transaction, part_name, part_number, performed_by_username in transactions:
        # Get warehouse names if they exist
        from_warehouse_name = None
        if transaction.from_warehouse_id:
            from_warehouse = db.query(models.Warehouse).filter(models.Warehouse.id == transaction.from_warehouse_id).first()
            if from_warehouse:
                from_warehouse_name = from_warehouse.name
        
        to_warehouse_name = None
        if transaction.to_warehouse_id:
            to_warehouse = db.query(models.Warehouse).filter(models.Warehouse.id == transaction.to_warehouse_id).first()
            if to_warehouse:
                to_warehouse_name = to_warehouse.name
        
        # Get machine serial if it exists
        machine_serial = None
        if transaction.machine_id:
            machine = db.query(models.Machine).filter(models.Machine.id == transaction.machine_id).first()
            if machine:
                machine_serial = machine.serial_number
        
        # Create a dictionary with all the data
        result = {
            **transaction.__dict__,
            "part_name": part_name,
            "part_number": part_number,
            "from_warehouse_name": from_warehouse_name,
            "to_warehouse_name": to_warehouse_name,
            "machine_serial": machine_serial,
            "performed_by_username": performed_by_username
        }
        
        results.append(result)
    
    return results

def reverse_transaction(db: Session, reversal: schemas.TransactionReversal):
    """Reverse a transaction by creating a new transaction with opposite effect."""
    # Get the original transaction
    original_transaction = db.query(models.Transaction).filter(models.Transaction.id == reversal.transaction_id).first()
    if not original_transaction:
        raise ValueError(f"Transaction {reversal.transaction_id} not found")
    
    # Create a new transaction with opposite effect
    new_transaction = models.Transaction(
        transaction_type=original_transaction.transaction_type,
        part_id=original_transaction.part_id,
        from_warehouse_id=original_transaction.to_warehouse_id,  # Swap from and to warehouses
        to_warehouse_id=original_transaction.from_warehouse_id,  # Swap from and to warehouses
        machine_id=original_transaction.machine_id,
        quantity=original_transaction.quantity,  # Keep the same quantity
        unit_of_measure=original_transaction.unit_of_measure,
        performed_by_user_id=reversal.performed_by_user_id,
        transaction_date=datetime.now(),
        notes=f"Reversal of transaction {original_transaction.id}: {reversal.reason}",
        reference_number=f"REV-{original_transaction.reference_number}" if original_transaction.reference_number else f"REV-{original_transaction.id}"
    )
    
    try:
        # Add the transaction to the database
        db.add(new_transaction)
        
        # Update inventory based on transaction type (with opposite effect)
        if original_transaction.transaction_type == models.TransactionType.CREATION:
            # Decrease inventory in original to_warehouse
            update_inventory(db, original_transaction.to_warehouse_id, original_transaction.part_id, -original_transaction.quantity)
        
        elif original_transaction.transaction_type == models.TransactionType.TRANSFER:
            # Increase inventory in original from_warehouse
            update_inventory(db, original_transaction.from_warehouse_id, original_transaction.part_id, original_transaction.quantity)
            # Decrease inventory in original to_warehouse
            update_inventory(db, original_transaction.to_warehouse_id, original_transaction.part_id, -original_transaction.quantity)
        
        elif original_transaction.transaction_type == models.TransactionType.CONSUMPTION:
            # Increase inventory in original from_warehouse
            update_inventory(db, original_transaction.from_warehouse_id, original_transaction.part_id, original_transaction.quantity)
        
        elif original_transaction.transaction_type == models.TransactionType.ADJUSTMENT:
            # Adjust inventory in original from_warehouse (with opposite sign)
            update_inventory(db, original_transaction.from_warehouse_id, original_transaction.part_id, -original_transaction.quantity)
        
        # Commit the transaction
        db.commit()
        db.refresh(new_transaction)
        return new_transaction
    except Exception as e:
        db.rollback()
        logger.error(f"Error reversing transaction: {e}")
        raise HTTPException(status_code=400, detail=f"Error reversing transaction: {str(e)}")

def get_transaction_summary(db: Session, days: int = 30, organization_id: Optional[uuid.UUID] = None):
    """Get transaction summary statistics."""
    # Calculate the start date for the summary period
    start_date = datetime.now() - timedelta(days=days)
    
    # Base query for transaction summary
    query = db.query(
        models.Transaction.transaction_type,
        func.sum(models.Transaction.quantity).label("total_quantity"),
        func.count(models.Transaction.id).label("transaction_count")
    ).filter(
        models.Transaction.transaction_date >= start_date
    ).group_by(
        models.Transaction.transaction_type
    )
    
    # Filter by organization if provided
    if organization_id:
        # Get all warehouses for the organization
        warehouses = db.query(models.Warehouse).filter(models.Warehouse.organization_id == organization_id).all()
        warehouse_ids = [w.id for w in warehouses]
        
        # Filter transactions where from_warehouse_id or to_warehouse_id is in the organization's warehouses
        query = query.filter(
            or_(
                models.Transaction.from_warehouse_id.in_(warehouse_ids),
                models.Transaction.to_warehouse_id.in_(warehouse_ids)
            )
        )
    
    # Execute query
    results = query.all()
    
    # Format results
    summary = []
    for transaction_type, total_quantity, transaction_count in results:
        summary.append({
            "transaction_type": transaction_type,
            "total_quantity": total_quantity,
            "transaction_count": transaction_count
        })
    
    return summary

def get_warehouse_transaction_summary(db: Session, days: int = 30, organization_id: Optional[uuid.UUID] = None):
    """Get transaction summary by warehouse."""
    # Calculate the start date for the summary period
    start_date = datetime.now() - timedelta(days=days)
    
    # Get all warehouses (filtered by organization if provided)
    warehouse_query = db.query(models.Warehouse)
    if organization_id:
        warehouse_query = warehouse_query.filter(models.Warehouse.organization_id == organization_id)
    warehouses = warehouse_query.all()
    
    results = []
    for warehouse in warehouses:
        # Count incoming transactions (to_warehouse_id)
        incoming_query = db.query(
            func.sum(models.Transaction.quantity).label("incoming_quantity"),
            func.count(models.Transaction.id).label("incoming_count")
        ).filter(
            models.Transaction.to_warehouse_id == warehouse.id,
            models.Transaction.transaction_date >= start_date
        )
        incoming_result = incoming_query.first()
        
        # Count outgoing transactions (from_warehouse_id)
        outgoing_query = db.query(
            func.sum(models.Transaction.quantity).label("outgoing_quantity"),
            func.count(models.Transaction.id).label("outgoing_count")
        ).filter(
            models.Transaction.from_warehouse_id == warehouse.id,
            models.Transaction.transaction_date >= start_date
        )
        outgoing_result = outgoing_query.first()
        
        # Calculate net quantity
        incoming_quantity = incoming_result.incoming_quantity or Decimal('0')
        outgoing_quantity = outgoing_result.outgoing_quantity or Decimal('0')
        net_quantity = incoming_quantity - outgoing_quantity
        
        results.append({
            "warehouse_id": warehouse.id,
            "warehouse_name": warehouse.name,
            "incoming_transactions": incoming_result.incoming_count or 0,
            "outgoing_transactions": outgoing_result.outgoing_count or 0,
            "net_quantity": net_quantity
        })
    
    return results

def get_part_transaction_history(db: Session, part_id: uuid.UUID, days: int = 90):
    """Get transaction history for a specific part."""
    # Calculate the start date for the history period
    start_date = datetime.now() - timedelta(days=days)
    
    # Get part details
    part = db.query(models.Part).filter(models.Part.id == part_id).first()
    if not part:
        raise ValueError(f"Part {part_id} not found")
    
    # Get transactions for this part
    transactions = search_transactions(
        db,
        schemas.TransactionFilter(
            part_id=part_id,
            start_date=start_date
        )
    )
    
    # Calculate totals by transaction type
    total_created = Decimal('0')
    total_transferred = Decimal('0')
    total_consumed = Decimal('0')
    total_adjusted = Decimal('0')
    
    for transaction in transactions:
        if transaction["transaction_type"] == models.TransactionType.CREATION:
            total_created += transaction["quantity"]
        elif transaction["transaction_type"] == models.TransactionType.TRANSFER:
            total_transferred += transaction["quantity"]
        elif transaction["transaction_type"] == models.TransactionType.CONSUMPTION:
            total_consumed += transaction["quantity"]
        elif transaction["transaction_type"] == models.TransactionType.ADJUSTMENT:
            total_adjusted += transaction["quantity"]
    
    # Calculate net quantity
    net_quantity = total_created + total_adjusted - total_consumed
    
    return {
        "part_id": part.id,
        "part_name": part.name,
        "part_number": part.part_number,
        "transactions": transactions,
        "total_created": total_created,
        "total_transferred": total_transferred,
        "total_consumed": total_consumed,
        "total_adjusted": total_adjusted,
        "net_quantity": net_quantity
    }