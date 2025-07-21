# backend/app/routers/dashboard.py

from fastapi import APIRouter, Depends
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

@router.get("/low-stock-by-org", response_model=List[schemas.LowStockByOrgResponse], tags=["Dashboard"])
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