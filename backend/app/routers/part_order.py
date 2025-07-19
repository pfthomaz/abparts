# backend/app/routers/part_order.py

import uuid
from typing import List, Optional, Dict, Any
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from .. import schemas, models
from ..database import get_db
from ..auth import get_current_user, TokenData
from ..permissions import (
    ResourceType, PermissionType, require_permission, require_super_admin,
    OrganizationScopedQueries, check_organization_access, permission_checker
)
from ..crud import part_order as crud

router = APIRouter()

# Part Order Requests
@router.get("/requests", response_model=List[schemas.PartOrderRequestResponse])
async def get_part_order_requests(
    customer_organization_id: Optional[uuid.UUID] = Query(None, description="Filter by customer organization ID"),
    status: Optional[schemas.OrderStatusEnum] = Query(None, description="Filter by order status"),
    priority: Optional[schemas.OrderPriorityEnum] = Query(None, description="Filter by priority"),
    supplier_type: Optional[schemas.SupplierTypeEnum] = Query(None, description="Filter by supplier type"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(require_permission(ResourceType.ORDER, PermissionType.READ))
):
    """
    Get part order requests with optional filtering.
    Users can only view orders for their organization unless they are super admins.
    """
    # If customer_organization_id is provided, check if user has access to it
    if customer_organization_id:
        if not check_organization_access(current_user, customer_organization_id, db):
            raise HTTPException(status_code=403, detail="Not authorized to view orders for this organization")
    
    # If no customer_organization_id is provided and user is not super_admin, use their organization
    elif not permission_checker.is_super_admin(current_user):
        customer_organization_id = current_user.organization_id
    
    orders = crud.get_part_order_requests(
        db, customer_organization_id, status, priority, supplier_type, skip, limit
    )
    return orders

@router.get("/requests/{order_id}", response_model=schemas.PartOrderRequestResponse)
async def get_part_order_request(
    order_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(require_permission(ResourceType.ORDER, PermissionType.READ))
):
    """
    Get a specific part order request by ID.
    Users can only view orders for their organization unless they are super admins.
    """
    order = crud.get_part_order_request(db, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Part order request not found")
    
    # Check if user has access to this order's organization
    if not check_organization_access(current_user, order["customer_organization_id"], db):
        raise HTTPException(status_code=403, detail="Not authorized to view this order")
    
    return order

@router.post("/requests", response_model=schemas.PartOrderRequestResponse, status_code=status.HTTP_201_CREATED)
async def create_part_order_request(
    order: schemas.PartOrderRequestCreate,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(require_permission(ResourceType.ORDER, PermissionType.WRITE))
):
    """
    Create a new part order request.
    Users can only create orders for their organization unless they are super admins.
    """
    # Check if user has access to the customer organization
    if not check_organization_access(current_user, order.customer_organization_id, db):
        raise HTTPException(status_code=403, detail="Not authorized to create orders for this organization")
    
    return crud.create_part_order_request(db, order, current_user.user_id)

@router.put("/requests/{order_id}", response_model=schemas.PartOrderRequestResponse)
async def update_part_order_request(
    order_id: uuid.UUID,
    order_update: schemas.PartOrderRequestUpdate,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(require_permission(ResourceType.ORDER, PermissionType.WRITE))
):
    """
    Update a part order request.
    Users can only update orders for their organization unless they are super admins.
    """
    # Check if order exists
    order = crud.get_part_order_request(db, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Part order request not found")
    
    # Check if user has access to this order's organization
    if not check_organization_access(current_user, order["customer_organization_id"], db):
        raise HTTPException(status_code=403, detail="Not authorized to update this order")
    
    updated_order = crud.update_part_order_request(db, order_id, order_update)
    return updated_order

@router.delete("/requests/{order_id}")
async def delete_part_order_request(
    order_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(require_permission(ResourceType.ORDER, PermissionType.DELETE))
):
    """
    Delete a part order request.
    Users can only delete orders for their organization unless they are super admins.
    """
    # Check if order exists
    order = crud.get_part_order_request(db, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Part order request not found")
    
    # Check if user has access to this order's organization
    if not check_organization_access(current_user, order["customer_organization_id"], db):
        raise HTTPException(status_code=403, detail="Not authorized to delete this order")
    
    result = crud.delete_part_order_request(db, order_id)
    return result

# Order Status Management
@router.patch("/requests/{order_id}/approve", response_model=schemas.PartOrderRequestResponse)
async def approve_order_request(
    order_id: uuid.UUID,
    approval: schemas.OrderApprovalRequest,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(require_permission(ResourceType.ORDER, PermissionType.WRITE))
):
    """
    Approve or reject a part order request.
    Only admins and super admins can approve orders.
    """
    if not permission_checker.is_admin(current_user) and not permission_checker.is_super_admin(current_user):
        raise HTTPException(status_code=403, detail="Only admins can approve orders")
    
    # Check if order exists
    order = crud.get_part_order_request(db, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Part order request not found")
    
    # Check if user has access to this order's organization
    if not permission_checker.is_super_admin(current_user):
        if not check_organization_access(current_user, order["customer_organization_id"], db):
            raise HTTPException(status_code=403, detail="Not authorized to approve this order")
    
    return crud.approve_order_request(db, order_id, approval, current_user.user_id)

@router.patch("/requests/{order_id}/fulfill", response_model=schemas.PartOrderRequestResponse)
async def fulfill_order_request(
    order_id: uuid.UUID,
    fulfillment: schemas.OrderFulfillmentRequest,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(require_permission(ResourceType.ORDER, PermissionType.WRITE))
):
    """
    Fulfill a part order request by recording received items and updating inventory.
    Users can fulfill orders for their organization.
    """
    # Check if order exists
    order = crud.get_part_order_request(db, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Part order request not found")
    
    # Check if user has access to this order's organization
    if not check_organization_access(current_user, order["customer_organization_id"], db):
        raise HTTPException(status_code=403, detail="Not authorized to fulfill this order")
    
    return crud.fulfill_order_request(db, order_id, fulfillment, current_user.user_id)

# Batch Operations
@router.post("/requests/batch", response_model=schemas.PartOrderRequestResponse, status_code=status.HTTP_201_CREATED)
async def create_batch_order_request(
    batch_order: schemas.BatchOrderRequest,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(require_permission(ResourceType.ORDER, PermissionType.WRITE))
):
    """
    Create a part order request with multiple items in a single operation.
    Users can only create orders for their organization unless they are super admins.
    """
    # Check if user has access to the customer organization
    if not check_organization_access(current_user, batch_order.customer_organization_id, db):
        raise HTTPException(status_code=403, detail="Not authorized to create orders for this organization")
    
    return crud.create_batch_order_request(db, batch_order, current_user.user_id)

# Analytics and Reporting
@router.get("/analytics", response_model=schemas.OrderAnalytics)
async def get_order_analytics(
    customer_organization_id: Optional[uuid.UUID] = Query(None, description="Filter by customer organization ID"),
    days: int = Query(30, ge=1, le=365, description="Number of days to include in analytics"),
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(require_permission(ResourceType.ORDER, PermissionType.READ))
):
    """
    Get order analytics and metrics.
    Users can only view analytics for their organization unless they are super admins.
    """
    # If customer_organization_id is provided, check if user has access to it
    if customer_organization_id:
        if not check_organization_access(current_user, customer_organization_id, db):
            raise HTTPException(status_code=403, detail="Not authorized to view analytics for this organization")
    
    # If no customer_organization_id is provided and user is not super_admin, use their organization
    elif not permission_checker.is_super_admin(current_user):
        customer_organization_id = current_user.organization_id
    
    return crud.get_order_analytics(db, customer_organization_id, days)

# Reorder Suggestions
@router.get("/reorder-suggestions", response_model=List[schemas.ReorderSuggestion])
async def get_reorder_suggestions(
    request: schemas.ReorderSuggestionRequest = Depends(),
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(require_permission(ResourceType.INVENTORY, PermissionType.READ))
):
    """
    Get reorder suggestions based on current inventory levels and usage patterns.
    Users can only view suggestions for their organization unless they are super admins.
    """
    # If organization_id is provided, check if user has access to it
    if request.organization_id:
        if not check_organization_access(current_user, request.organization_id, db):
            raise HTTPException(status_code=403, detail="Not authorized to view suggestions for this organization")
    
    # If no organization_id is provided and user is not super_admin, use their organization
    elif not permission_checker.is_super_admin(current_user):
        request.organization_id = current_user.organization_id
    
    return crud.get_reorder_suggestions(db, request)