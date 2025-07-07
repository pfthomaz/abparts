# c:/abparts/backend/app/routers/dashboard.py

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from .. import schemas, crud
from ..database import get_db
from ..auth import get_current_user

router = APIRouter()

@router.get("/metrics", response_model=schemas.DashboardMetricsResponse, tags=["Dashboard"])
def get_metrics(
    db: Session = Depends(get_db),
    current_user: schemas.TokenData = Depends(get_current_user)
):
    """
    Retrieves key metrics for the main dashboard.
    """
    return crud.dashboard.get_dashboard_metrics(db=db)

@router.get("/low-stock-by-org", response_model=List[schemas.LowStockByOrgResponse], tags=["Dashboard"])
def get_low_stock_chart_data(
    db: Session = Depends(get_db),
    current_user: schemas.TokenData = Depends(get_current_user)
):
    """
    Retrieves data for a chart showing low stock items per organization.
    """
    return crud.dashboard.get_low_stock_by_organization(db=db)