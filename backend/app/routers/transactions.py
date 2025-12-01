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
from ..schemas.machine_sale import MachineSaleRequest, MachineSaleResponse
from ..schemas.part_order_transaction import PartOrderRequest, PartOrderReceiptRequest, PartOrderResponse
from ..schemas.part_usage import PartUsageRequest, PartUsageResponse
from ..crud import machine_sale, part_order_transaction, part_usage

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
    
    # TODO: Implement approval workflow - for now return empty list
    # The approval workflow fields (requires_approval, approval_status) are not yet 
    # implemented in the database schema, so we return an empty list to prevent errors
    return []

# --- New Transaction Management API Extensions ---

@router.post("/machine-sale", response_model=MachineSaleResponse, status_code=status.HTTP_201_CREATED)
async def create_machine_sale(
    machine_sale_request: MachineSaleRequest,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(require_permission(ResourceType.TRANSACTION, PermissionType.WRITE))
):
    """
    Record machine ownership transfer from one organization to another.
    Typically used for sales from Oraseas EE to customers.
    Only super_admin and admins can create machine sales.
    """
    # Check if user has permission to perform machine sales
    if not (permission_checker.is_super_admin(current_user) or permission_checker.is_admin(current_user)):
        raise HTTPException(status_code=403, detail="Only admins can record machine sales")
    
    # Validate organizational access
    if not permission_checker.is_super_admin(current_user):
        # Admin users can only sell machines from their own organization
        if machine_sale_request.from_organization_id != current_user.organization_id:
            raise HTTPException(status_code=403, detail="Not authorized to sell machines from this organization")
    
    # Set performed_by_user_id to current user if not provided
    if not machine_sale_request.performed_by_user_id:
        machine_sale_request.performed_by_user_id = current_user.user_id
    
    try:
        db_machine_sale = machine_sale.create_machine_sale(db, machine_sale_request)
        
        # Get the response with related data
        result = machine_sale.get_machine_sale(db, db_machine_sale.id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/part-order", response_model=PartOrderResponse, status_code=status.HTTP_201_CREATED)
async def create_part_order(
    part_order_request: PartOrderRequest,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(require_permission(ResourceType.TRANSACTION, PermissionType.WRITE))
):
    """
    Create a part order request (phase 1 of two-phase recording).
    Users can only create orders from their own organization.
    """
    # Validate organizational access
    if not permission_checker.is_super_admin(current_user):
        # Users can only create orders from their own organization
        if part_order_request.from_organization_id != current_user.organization_id:
            raise HTTPException(status_code=403, detail="Not authorized to create orders from this organization")
        
        # Validate warehouse access if provided
        if part_order_request.from_warehouse_id:
            warehouse = db.query(models.Warehouse).filter(models.Warehouse.id == part_order_request.from_warehouse_id).first()
            if not warehouse or warehouse.organization_id != current_user.organization_id:
                raise HTTPException(status_code=403, detail="Not authorized to use this warehouse")
    
    # Set performed_by_user_id to current user if not provided
    if not part_order_request.performed_by_user_id:
        part_order_request.performed_by_user_id = current_user.user_id
    
    try:
        db_part_order = part_order_transaction.create_part_order(db, part_order_request)
        
        # Get the response with related data
        result = part_order_transaction.get_part_order(db, db_part_order.id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/part-order/{order_id}/receipt", response_model=PartOrderResponse)
async def receive_part_order(
    order_id: uuid.UUID,
    receipt_request: PartOrderReceiptRequest,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(require_permission(ResourceType.TRANSACTION, PermissionType.WRITE))
):
    """
    Process part order receipt (phase 2 of two-phase recording).
    Creates inventory transactions and updates stock levels.
    """
    # Validate that the order exists and user has access
    order = db.query(models.PartOrderRequest).filter(models.PartOrderRequest.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # Check organizational access
    if not permission_checker.is_super_admin(current_user):
        if order.customer_organization_id != current_user.organization_id:
            raise HTTPException(status_code=403, detail="Not authorized to receive this order")
    
    # Set the order_id and performed_by_user_id
    receipt_request.order_id = order_id
    if not receipt_request.performed_by_user_id:
        receipt_request.performed_by_user_id = current_user.user_id
    
    try:
        db_part_order = part_order_transaction.receive_part_order(db, receipt_request)
        
        # Get the response with related data
        result = part_order_transaction.get_part_order(db, db_part_order.id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/part-usage", response_model=PartUsageResponse, status_code=status.HTTP_201_CREATED)
async def create_part_usage(
    part_usage_request: PartUsageRequest,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(require_permission(ResourceType.TRANSACTION, PermissionType.WRITE))
):
    """
    Record part usage in machines (machine part consumption).
    Creates consumption transactions and updates inventory levels.
    Users can only record usage for machines and warehouses in their organization.
    """
    # Validate organizational access
    if not permission_checker.is_super_admin(current_user):
        # Check machine access
        machine = db.query(models.Machine).filter(models.Machine.id == part_usage_request.machine_id).first()
        if not machine or machine.customer_organization_id != current_user.organization_id:
            raise HTTPException(status_code=403, detail="Not authorized to record usage for this machine")
        
        # Check warehouse access
        warehouse = db.query(models.Warehouse).filter(models.Warehouse.id == part_usage_request.from_warehouse_id).first()
        if not warehouse or warehouse.organization_id != current_user.organization_id:
            raise HTTPException(status_code=403, detail="Not authorized to use parts from this warehouse")
    
    # Set performed_by_user_id to current user if not provided
    if not part_usage_request.performed_by_user_id:
        part_usage_request.performed_by_user_id = current_user.user_id
    
    try:
        db_part_usage = part_usage.create_part_usage(db, part_usage_request)
        
        # Get the response with related data
        result = part_usage.get_part_usage(db, db_part_usage.id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

# --- Additional endpoints for the new transaction types ---

@router.get("/machine-sales", response_model=List[MachineSaleResponse])
async def get_machine_sales(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(require_permission(ResourceType.TRANSACTION, PermissionType.READ))
):
    """
    Get machine sales with pagination.
    Users see only sales involving their organization.
    """
    organization_id = None if permission_checker.is_super_admin(current_user) else current_user.organization_id
    
    try:
        sales = machine_sale.get_machine_sales(db, skip=skip, limit=limit, organization_id=organization_id)
        return sales
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/part-orders", response_model=List[PartOrderResponse])
async def get_part_orders(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(require_permission(ResourceType.TRANSACTION, PermissionType.READ))
):
    """
    Get part orders with pagination.
    Users see only orders involving their organization.
    """
    organization_id = None if permission_checker.is_super_admin(current_user) else current_user.organization_id
    
    try:
        orders = part_order_transaction.get_part_orders(db, skip=skip, limit=limit, organization_id=organization_id)
        return orders
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/part-usages", response_model=List[PartUsageResponse])
async def get_part_usages(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    machine_id: Optional[uuid.UUID] = Query(None, description="Filter by machine ID"),
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(require_permission(ResourceType.TRANSACTION, PermissionType.READ))
):
    """
    Get part usage records with pagination.
    Users see only usage records involving their organization.
    """
    organization_id = None if permission_checker.is_super_admin(current_user) else current_user.organization_id
    
    try:
        usages = part_usage.get_part_usages(db, skip=skip, limit=limit, organization_id=organization_id, machine_id=machine_id)
        return usages
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# --- Individual Transaction Lookup (must be last to avoid catching other routes) ---
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

# --- Delete Transaction ---
@router.delete("/{transaction_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_transaction(
    transaction_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(require_permission(ResourceType.TRANSACTION, PermissionType.WRITE))
):
    """
    Delete a transaction.
    With calculated inventory, deleting transactions is safe - inventory will automatically recalculate.
    Users can only delete transactions involving their organization's warehouses.
    """
    # Get the transaction
    transaction = db.query(models.Transaction).filter(models.Transaction.id == transaction_id).first()
    
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    # Check permissions
    if not permission_checker.is_super_admin(current_user):
        # Get all warehouses for the user's organization
        warehouses = db.query(models.Warehouse).filter(
            models.Warehouse.organization_id == current_user.organization_id
        ).all()
        warehouse_ids = [w.id for w in warehouses]
        
        # Check if transaction involves the organization's warehouses
        if transaction.from_warehouse_id not in warehouse_ids and transaction.to_warehouse_id not in warehouse_ids:
            raise HTTPException(status_code=403, detail="Not authorized to delete this transaction")
    
    # Delete the transaction
    # Note: Inventory will automatically recalculate without this transaction
    db.delete(transaction)
    db.commit()
    
    return None


# --- Update Transaction ---
@router.put("/{transaction_id}", response_model=schemas.TransactionResponse)
async def update_transaction(
    transaction_id: uuid.UUID,
    transaction_update: schemas.TransactionCreate,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(require_permission(ResourceType.TRANSACTION, PermissionType.WRITE))
):
    """
    Update a transaction.
    With calculated inventory, updating transactions is safe - inventory will automatically recalculate.
    Users can only update transactions involving their organization's warehouses.
    
    Note: If this transaction is linked to a PartUsageItem, that will also be updated.
    """
    # Get the transaction
    transaction = db.query(models.Transaction).filter(models.Transaction.id == transaction_id).first()
    
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    # Store old quantity for part_usage_item update
    old_quantity = transaction.quantity
    
    # Check permissions for the existing transaction
    if not permission_checker.is_super_admin(current_user):
        warehouses = db.query(models.Warehouse).filter(
            models.Warehouse.organization_id == current_user.organization_id
        ).all()
        warehouse_ids = [w.id for w in warehouses]
        
        # Check existing transaction
        if transaction.from_warehouse_id not in warehouse_ids and transaction.to_warehouse_id not in warehouse_ids:
            raise HTTPException(status_code=403, detail="Not authorized to update this transaction")
        
        # Check new warehouse IDs
        if transaction_update.from_warehouse_id and transaction_update.from_warehouse_id not in warehouse_ids:
            raise HTTPException(status_code=403, detail="Not authorized to update to this warehouse")
        
        if transaction_update.to_warehouse_id and transaction_update.to_warehouse_id not in warehouse_ids:
            raise HTTPException(status_code=403, detail="Not authorized to update to this warehouse")
    
    # Update the transaction fields
    for field, value in transaction_update.dict(exclude_unset=True).items():
        setattr(transaction, field, value)
    
    # Validate the updated transaction
    try:
        crud.transaction.validate_transaction_data(transaction_update)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    # If this is a consumption transaction with a machine_id, check for linked PartUsageItem
    # and update it as well to keep the records in sync
    if transaction.transaction_type == 'consumption' and transaction.machine_id:
        # Find any PartUsageItem that might be linked to this transaction
        # We match by: machine_id, part_id, and quantity (within a small time window)
        from datetime import timedelta
        time_window_start = transaction.transaction_date - timedelta(minutes=5)
        time_window_end = transaction.transaction_date + timedelta(minutes=5)
        
        # Find part_usage_records in the time window for this machine
        usage_records = db.query(models.PartUsageRecord).filter(
            models.PartUsageRecord.machine_id == transaction.machine_id,
            models.PartUsageRecord.usage_date >= time_window_start,
            models.PartUsageRecord.usage_date <= time_window_end
        ).all()
        
        # Find matching part_usage_item
        for usage_record in usage_records:
            usage_item = db.query(models.PartUsageItem).filter(
                models.PartUsageItem.usage_record_id == usage_record.id,
                models.PartUsageItem.part_id == transaction.part_id,
                models.PartUsageItem.quantity == old_quantity
            ).first()
            
            if usage_item:
                # Update the part_usage_item to match the transaction
                usage_item.quantity = transaction.quantity
                if transaction_update.notes:
                    usage_item.notes = transaction_update.notes
                break
    
    db.commit()
    db.refresh(transaction)
    
    return transaction
