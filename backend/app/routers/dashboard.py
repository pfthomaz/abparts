# backend/app/routers/dashboard.py

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from typing import List
from .. import schemas, crud
from ..database import get_db
from ..auth import get_current_user, TokenData
from ..permissions import (
    ResourceType, PermissionType, require_permission,
    OrganizationScopedQueries, check_organization_access, permission_checker
)
from ..crud import dashboard_fixed

router = APIRouter()

@router.get("/metrics", response_model=schemas.DashboardMetricsResponse, tags=["Dashboard"])
def get_metrics(
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(require_permission(ResourceType.DASHBOARD, PermissionType.READ))
):
    """
    Retrieves key metrics for the main dashboard with organization-scoped data.
    """
    # Dashboard metrics should be scoped to user's accessible organizations
    if permission_checker.is_super_admin(current_user):
        return dashboard_fixed.get_dashboard_metrics(db=db)
    else:
        # For non-super admins, pass organization context to limit metrics
        return dashboard_fixed.get_dashboard_metrics(db=db, organization_id=current_user.organization_id)

@router.get("/low-stock-by-org", tags=["Dashboard"])
def get_low_stock_chart_data(
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(require_permission(ResourceType.DASHBOARD, PermissionType.READ))
):
    """
    Retrieves data for a chart showing low stock items per organization with proper access control.
    """
    # Low stock data should be scoped to user's accessible organizations
    if permission_checker.is_super_admin(current_user):
        return dashboard_fixed.get_low_stock_by_organization(db=db)
    else:
        # For non-super admins, filter to their organization only
        return dashboard_fixed.get_low_stock_by_organization(db=db, organization_id=current_user.organization_id)

# Import CORS error handling
from ..cors_error_handler import create_cors_error_response, CORS_ERROR_ORIGIN_NOT_ALLOWED
from ..cors_config import get_cors_origins

# Add OPTIONS method handler for CORS preflight requests with enhanced error handling
@router.options("/low-stock-by-org", tags=["Dashboard"])
def options_low_stock_chart_data(request: Request):
    """
    Handle OPTIONS requests for CORS preflight with comprehensive error handling.
    """
    # Get the origin from the request
    origin = request.headers.get("Origin")
    
    # If no origin, return a basic response
    if not origin:
        return {"detail": "OK"}
    
    # Check if the origin is allowed
    allowed_origins = get_cors_origins()
    if origin not in allowed_origins and "*" not in allowed_origins:
        # Return a detailed error response for disallowed origins
        return create_cors_error_response(
            CORS_ERROR_ORIGIN_NOT_ALLOWED,
            origin=origin,
            allowed_origins=allowed_origins,
            status_code=403
        )
    
    # Origin is allowed, return success response
    return {"detail": "OK"}

# Add OPTIONS method handler for metrics endpoint
@router.options("/metrics", tags=["Dashboard"])
def options_metrics(request: Request):
    """
    Handle OPTIONS requests for metrics endpoint with comprehensive error handling.
    """
    # Get the origin from the request
    origin = request.headers.get("Origin")
    
    # If no origin, return a basic response
    if not origin:
        return {"detail": "OK"}
    
    # Check if the origin is allowed
    allowed_origins = get_cors_origins()
    if origin not in allowed_origins and "*" not in allowed_origins:
        # Return a detailed error response for disallowed origins
        return create_cors_error_response(
            CORS_ERROR_ORIGIN_NOT_ALLOWED,
            origin=origin,
            allowed_origins=allowed_origins,
            status_code=403
        )
    
    # Origin is allowed, return success response
    return {"detail": "OK"}