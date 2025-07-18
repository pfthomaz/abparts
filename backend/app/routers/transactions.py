# backend/app/routers/transactions.py

import uuid
from typing import List, Optional
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from .. import schemas, crud, models
from ..database import get_db
from ..auth import get_current_user, TokenData
from ..permissions import (
    ResourceType, PermissionType, require_permission, require_super_admin,
    OrganizationScopedQueries, check_organization_access, permission_checker
)

router = APIRouter()

# --- Transactions CRUD ---
@router.get("/", response_model=List[schemas.TransactionResponse])
async def get_transactions(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(require_permission(ResourceType.TRANSACTION, PermissionType.READ))
):
    """
    Get all transactions with pagination.
    Super admins see all transactions, regular users see only transactions involving their organization's warehouses.
    """
    # If user is not a super_admin, filter transactions by organization
    if not permission_checker.is_super_admin(current_user):
        # Get all warehouses for the user's organization
        warehouses = db.query(models.Warehouse).filter(models.Warehouse.organization_id == current_user.organization_id).all()
        warehouse_ids = [w.id for w in warehouses]
        
        # Create a filter for transactions involving the organization's warehouses
        filters = schemas.TransactionFilter()
        # We'll handle the warehouse filtering in the search_transactions function
        transactions = crud.transaction.search_transactions(db, filters, skip, limit)
        
        # Filter transactions where from_warehouse_id or to_warehouse_id is in the organization's warehouses
        transactions = [
            t for t in transactions 
            if (t.get("from_warehouse_id") in warehouse_ids or t.get("to_warehouse_id") in warehouse_ids)
        ]
        
        return transactions[:limit]  # Apply limit after filtering
    else:
        # Super admins see all transactions
        return crud.transaction.get_transactions(db, skip, limit)

@router.get("/{transaction_id}", response_model=schemas.TransactionResponse)
async def get_transaction(
    transaction_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(require_permission(ResourceType.TRANSACTION, PermissionType.READ))
):
    """
    Get a single transaction by ID.
    Users can only view transactions involving their organization's warehouses.
    """
    transaction = crud.transaction.get_transaction(db, transaction_id)
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    # Check if user can access this transaction
    if not permission_checker.is_super_admin(current_user):
        # Get all warehouses for the user's organization
        warehouses = db.query(models.Warehouse).filter(models.Warehouse.organization_id == current_user.organization_id).all()
        warehouse_ids = [w.id for w in warehouses]
        
        # Check if transaction involves the organization's warehouses
        if (transaction.get("from_warehouse_id") not in warehouse_ids and 
            transaction.get("to_warehouse_id") not in warehouse_ids):
            raise HTTPException(status_code=403, detail="Not authorized to view this transaction")
    
    return transaction

@router.post("/", response_model=schemas.TransactionResponse, status_code=status.HTTP_201_CREATED)
async def create_transaction(
    transaction: schemas.TransactionCreate,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(require_permission(ResourceType.TRANSACTION, PermissionType.WRITE))
):
    """
    Create a new transaction.
    Users can only create transactions involving their organization's warehouses.
    """
    # Check if user can access the warehouses involved in the transaction
    if not permission_checker.is_super_admin(current_user):
        # Get all warehouses for the user's organization
        warehouses = db.query(models.Warehouse).filter(models.Warehouse.organization_id == current_user.organization_id).all()
        warehouse_ids = [w.id for w in warehouses]
        
        # Check if transaction involves the organization's warehouses
        if transaction.from_warehouse_id and transaction.from_warehouse_id not in warehouse_ids:
            raise HTTPException(status_code=403, detail="Not authorized to create transactions from this warehouse")
        
        if transaction.to_warehouse_id and transaction.to_warehouse_id not in warehouse_ids:
            raise HTTPException(status_code=403, detail="Not authorized to create transactions to this warehouse")
    
    # Set performed_by_user_id to current user if not provided
    if not transaction.performed_by_user_id:
        transaction.performed_by_user_id = current_user.user_id
    
    # Create the transaction
    try:
        db_transaction = crud.transaction.create_transaction(db, transaction)
        return db_transaction
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/search", response_model=List[schemas.TransactionResponse])
async def search_transactions(
    filters: schemas.TransactionFilter,
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(require_permission(ResourceType.TRANSACTION, PermissionType.READ))
):
    """
    Search transactions with filters.
    Users can only view transactions involving their organization's warehouses.
    """
    # If user is not a super_admin, filter transactions by organization
    if not permission_checker.is_super_admin(current_user):
        # Get all warehouses for the user's organization
        warehouses = db.query(models.Warehouse).filter(models.Warehouse.organization_id == current_user.organization_id).all()
        warehouse_ids = [w.id for w in warehouses]
        
        # Search transactions
        transactions = crud.transaction.search_transactions(db, filters, skip, limit)
        
        # Filter transactions where from_warehouse_id or to_warehouse_id is in the organization's warehouses
        transactions = [
            t for t in transactions 
            if (t.get("from_warehouse_id") in warehouse_ids or t.get("to_warehouse_id") in warehouse_ids)
        ]
        
        return transactions[:limit]  # Apply limit after filtering
    else:
        # Super admins see all transactions
        return crud.transaction.search_transactions(db, filters, skip, limit)

@router.post("/reverse", response_model=schemas.TransactionResponse)
async def reverse_transaction(
    reversal: schemas.TransactionReversal,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(require_permission(ResourceType.TRANSACTION, PermissionType.WRITE))
):
    """
    Reverse a transaction by creating a new transaction with opposite effect.
    Users can only reverse transactions involving their organization's warehouses.
    """
    # Get the original transaction
    original_transaction = crud.transaction.get_transaction(db, reversal.transaction_id)
    if not original_transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    # Check if user can access this transaction
    if not permission_checker.is_super_admin(current_user):
        # Get all warehouses for the user's organization
        warehouses = db.query(models.Warehouse).filter(models.Warehouse.organization_id == current_user.organization_id).all()
        warehouse_ids = [w.id for w in warehouses]
        
        # Check if transaction involves the organization's warehouses
        if (original_transaction.get("from_warehouse_id") not in warehouse_ids and 
            original_transaction.get("to_warehouse_id") not in warehouse_ids):
            raise HTTPException(status_code=403, detail="Not authorized to reverse this transaction")
    
    # Set performed_by_user_id to current user if not provided
    if not reversal.performed_by_user_id:
        reversal.performed_by_user_id = current_user.user_id
    
    # Reverse the transaction
    try:
        reversed_transaction = crud.transaction.reverse_transaction(db, reversal)
        return reversed_transaction
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/summary", response_model=List[schemas.TransactionSummary])
async def get_transaction_summary(
    days: int = Query(30, ge=1, le=365, description="Number of days to include in summary"),
    organization_id: Optional[uuid.UUID] = Query(None, description="Filter by organization ID"),
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(require_permission(ResourceType.TRANSACTION, PermissionType.READ))
):
    """
    Get transaction summary statistics.
    If organization_id is provided, only transactions involving that organization's warehouses are included.
    Otherwise, for regular users, only transactions involving their organization's warehouses are shown.
    Super admins see all transactions across all organizations if no organization_id is specified.
    """
    # If organization_id is not provided, use the current user's organization
    # unless the user is a super_admin
    if not organization_id and not permission_checker.is_super_admin(current_user):
        organization_id = current_user.organization_id
    
    # Check organization access if organization_id is provided
    if organization_id and not check_organization_access(current_user, organization_id, db):
        raise HTTPException(status_code=403, detail="Not authorized to access this organization's data")
    
    # Get transaction summary
    summary = crud.transaction.get_transaction_summary(db, days, organization_id)
    return summary

@router.get("/warehouse-summary", response_model=List[schemas.WarehouseTransactionSummary])
async def get_warehouse_transaction_summary(
    days: int = Query(30, ge=1, le=365, description="Number of days to include in summary"),
    organization_id: Optional[uuid.UUID] = Query(None, description="Filter by organization ID"),
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(require_permission(ResourceType.TRANSACTION, PermissionType.READ))
):
    """
    Get transaction summary by warehouse.
    If organization_id is provided, only warehouses from that organization are included.
    Otherwise, for regular users, only warehouses from their organization are shown.
    Super admins see all warehouses across all organizations if no organization_id is specified.
    """
    # If organization_id is not provided, use the current user's organization
    # unless the user is a super_admin
    if not organization_id and not permission_checker.is_super_admin(current_user):
        organization_id = current_user.organization_id
    
    # Check organization access if organization_id is provided
    if organization_id and not check_organization_access(current_user, organization_id, db):
        raise HTTPException(status_code=403, detail="Not authorized to access this organization's data")
    
    # Get warehouse transaction summary
    summary = crud.transaction.get_warehouse_transaction_summary(db, days, organization_id)
    return summary

@router.get("/part/{part_id}/history", response_model=schemas.PartTransactionHistory)
async def get_part_transaction_history(
    part_id: uuid.UUID,
    days: int = Query(90, ge=1, le=365, description="Number of days to look back for history"),
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(require_permission(ResourceType.TRANSACTION, PermissionType.READ))
):
    """
    Get transaction history for a specific part.
    Users can only view transactions involving their organization's warehouses.
    """
    try:
        # Get part transaction history
        history = crud.transaction.get_part_transaction_history(db, part_id, days)
        
        # Filter transactions if user is not a super_admin
        if not permission_checker.is_super_admin(current_user):
            # Get all warehouses for the user's organization
            warehouses = db.query(models.Warehouse).filter(models.Warehouse.organization_id == current_user.organization_id).all()
            warehouse_ids = [w.id for w in warehouses]
            
            # Filter transactions where from_warehouse_id or to_warehouse_id is in the organization's warehouses
            history["transactions"] = [
                t for t in history["transactions"] 
                if (t.get("from_warehouse_id") in warehouse_ids or t.get("to_warehouse_id") in warehouse_ids)
            ]
        
        return history
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
@router.post("/batch", response_model=List[schemas.TransactionResponse], status_code=status.HTTP_201_CREATED)
async def create_transaction_batch(
    batch: schemas.TransactionBatchRequest,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(require_permission(ResourceType.TRANSACTION, PermissionType.WRITE))
):
    """
    Create a batch of transactions in a single database transaction.
    Users can only create transactions involving their organization's warehouses.
    """
    # Check if user can access the warehouses involved in all transactions
    if not permission_checker.is_super_admin(current_user):
        # Get all warehouses for the user's organization
        warehouses = db.query(models.Warehouse).filter(models.Warehouse.organization_id == current_user.organization_id).all()
        warehouse_ids = [w.id for w in warehouses]
        
        # Check if all transactions involve the organization's warehouses
        for transaction in batch.transactions:
            if transaction.from_warehouse_id and transaction.from_warehouse_id not in warehouse_ids:
                raise HTTPException(status_code=403, detail="Not authorized to create transactions from this warehouse")
            
            if transaction.to_warehouse_id and transaction.to_warehouse_id not in warehouse_ids:
                raise HTTPException(status_code=403, detail="Not authorized to create transactions to this warehouse")
    
    # Set performed_by_user_id to current user if not provided for each transaction
    for transaction in batch.transactions:
        if not transaction.performed_by_user_id:
            transaction.performed_by_user_id = current_user.user_id
    
    # Create the transaction batch
    try:
        from ..transaction_processor import get_transaction_processor
        processor = get_transaction_processor(db)
        db_transactions = processor.process_transaction_batch(batch.transactions)
        return db_transactions
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/approval", response_model=schemas.TransactionApprovalResponse)
async def approve_transaction(
    approval: schemas.TransactionApprovalRequest,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(require_permission(ResourceType.TRANSACTION, PermissionType.WRITE))
):
    """
    Approve or reject a transaction that requires approval.
    Only admins and super_admins can approve transactions.
    """
    # Check if user is an admin or super_admin
    if not (permission_checker.is_admin(current_user) or permission_checker.is_super_admin(current_user)):
        raise HTTPException(status_code=403, detail="Only admins can approve transactions")
    
    # Get the transaction
    transaction = crud.transaction.get_transaction(db, approval.transaction_id)
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    # Check if user can access this transaction
    if not permission_checker.is_super_admin(current_user):
        # Get all warehouses for the user's organization
        warehouses = db.query(models.Warehouse).filter(models.Warehouse.organization_id == current_user.organization_id).all()
        warehouse_ids = [w.id for w in warehouses]
        
        # Check if transaction involves the organization's warehouses
        if (transaction.get("from_warehouse_id") not in warehouse_ids and 
            transaction.get("to_warehouse_id") not in warehouse_ids):
            raise HTTPException(status_code=403, detail="Not authorized to approve this transaction")
    
    # Set approver_id to current user if not provided
    if not approval.approver_id:
        approval.approver_id = current_user.user_id
    
    # Create a new TransactionApproval record
    db_approval = models.TransactionApproval(
        transaction_id=approval.transaction_id,
        approver_id=approval.approver_id,
        status=approval.status,
        notes=approval.notes,
        created_at=datetime.now()
    )
    
    try:
        db.add(db_approval)
        db.commit()
        db.refresh(db_approval)
        
        # If approved, process the transaction
        if approval.status == schemas.TransactionApprovalStatus.APPROVED:
            from ..transaction_processor import get_transaction_processor
            processor = get_transaction_processor(db)
            try:
                processor.process_approved_transaction(approval.transaction_id)
            except Exception as e:
                db.rollback()
                raise HTTPException(status_code=400, detail=f"Error processing approved transaction: {str(e)}")
        
        return db_approval
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Error approving transaction: {str(e)}")

@router.get("/pending-approval", response_model=List[schemas.TransactionResponse])
async def get_pending_approval_transactions(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(require_permission(ResourceType.TRANSACTION, PermissionType.READ))
):
    """
    Get all transactions that require approval and are currently pending.
    Only admins and super_admins can view pending approval transactions.
    """
    # Check if user is an admin or super_admin
    if not (permission_checker.is_admin(current_user) or permission_checker.is_super_admin(current_user)):
        raise HTTPException(status_code=403, detail="Only admins can view pending approval transactions")
    
    # Query for transactions that require approval and are pending
    query = db.query(models.Transaction).filter(
        models.Transaction.requires_approval == True,
        models.Transaction.approval_status == 'pending'
    )
    
    # If user is not a super_admin, filter transactions by organization
    if not permission_checker.is_super_admin(current_user):
        # Get all warehouses for the user's organization
        warehouses = db.query(models.Warehouse).filter(models.Warehouse.organization_id == current_user.organization_id).all()
        warehouse_ids = [w.id for w in warehouses]
        
        # Filter transactions where from_warehouse_id or to_warehouse_id is in the organization's warehouses
        query = query.filter(
            (models.Transaction.from_warehouse_id.in_(warehouse_ids)) | 
            (models.Transaction.to_warehouse_id.in_(warehouse_ids))
        )
    
    # Apply pagination
    transactions = query.order_by(models.Transaction.created_at.desc()).offset(skip).limit(limit).all()
    
    # Convert to response format
    results = []
    for transaction in transactions:
        # Get part details
        part = db.query(models.Part).filter(models.Part.id == transaction.part_id).first()
        
        # Get user details
        user = db.query(models.User).filter(models.User.id == transaction.performed_by_user_id).first()
        
        # Get warehouse names
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
        
        # Create response object
        result = {
            **transaction.__dict__,
            "part_name": part.name if part else None,
            "part_number": part.part_number if part else None,
            "from_warehouse_name": from_warehouse_name,
            "to_warehouse_name": to_warehouse_name,
            "machine_serial": machine_serial,
            "performed_by_username": user.username if user else None
        }
        
        results.append(result)
    
    return results