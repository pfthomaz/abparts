# backend/app/schemas/dashboard.py

import uuid
from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field

class DashboardMetricsResponse(BaseModel):
    # User metrics
    total_users: int
    active_users: int
    pending_invitations: int
    locked_accounts: int
    
    # Organization metrics
    total_organizations: int
    customer_organizations: int
    supplier_organizations: int
    
    # Inventory metrics
    total_parts: int
    total_inventory_items: int
    low_stock_items: int
    out_of_stock_items: int
    
    # Machine metrics
    total_machines: int
    active_machines: int
    
    # Order metrics
    pending_customer_orders: int
    pending_supplier_orders: int
    completed_orders_this_month: int
    
    # Recent activity
    recent_part_usage: int
    recent_stock_adjustments: int
    recent_transactions: int
    
    # Security metrics
    failed_login_attempts_today: int
    security_events_today: int
    active_sessions: int
    
    # Timestamp
    generated_at: datetime
    
    class Config:
        orm_mode = True

class DashboardChartData(BaseModel):
    labels: List[str]
    datasets: List[Dict[str, Any]]
    
class DashboardInventoryAlert(BaseModel):
    part_id: uuid.UUID
    part_number: str
    part_name: str
    warehouse_name: str
    current_stock: float
    minimum_stock: float
    alert_type: str  # "low_stock", "out_of_stock"
    
class DashboardRecentActivity(BaseModel):
    activity_type: str
    description: str
    user_name: Optional[str] = None
    timestamp: datetime
    details: Optional[Dict[str, Any]] = None

class LowStockByOrgResponse(BaseModel):
    organization_id: uuid.UUID
    organization_name: str
    organization_type: str
    low_stock_count: int
    out_of_stock_count: int
    total_parts: int
    critical_parts: List[DashboardInventoryAlert] = []
    
    class Config:
        orm_mode = True