# c:/abparts/backend/app/crud/dashboard.py

from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional
import uuid
from .. import models

def get_dashboard_metrics(db: Session, organization_id: Optional[uuid.UUID] = None):
    """
    Calculates and returns key metrics for the dashboard.
    If organization_id is provided, metrics are scoped to that organization.
    """
    from datetime import datetime, timedelta
    
    # Base queries
    parts_query = db.query(models.Part)
    inventory_query = db.query(models.Inventory)
    customer_orders_query = db.query(models.CustomerOrder)
    supplier_orders_query = db.query(models.SupplierOrder)
    users_query = db.query(models.User)
    organizations_query = db.query(models.Organization)
    machines_query = db.query(models.Machine)
    
    # Apply organization scoping if provided
    if organization_id:
        # Inventory is warehouse-scoped, so we need to join through warehouses to get organization scope
        inventory_query = inventory_query.join(models.Warehouse).filter(models.Warehouse.organization_id == organization_id)
        # Orders are organization-scoped
        customer_orders_query = customer_orders_query.filter(models.CustomerOrder.organization_id == organization_id)
        supplier_orders_query = supplier_orders_query.filter(models.SupplierOrder.organization_id == organization_id)
        # Users are organization-scoped
        users_query = users_query.filter(models.User.organization_id == organization_id)
        # Organizations - if scoped, only show the specific organization
        organizations_query = organizations_query.filter(models.Organization.id == organization_id)
        # Machines are organization-scoped
        machines_query = machines_query.filter(models.Machine.customer_organization_id == organization_id)
    
    # Basic counts
    total_parts = parts_query.count()
    total_inventory_items = inventory_query.count()
    
    # User metrics (with error handling)
    total_users = 0
    active_users = 0
    pending_invitations = 0
    locked_accounts = 0
    try:
        total_users = users_query.count()
        active_users = users_query.filter(models.User.is_active == True, models.User.user_status == models.UserStatus.active).count()
        pending_invitations = users_query.filter(models.User.user_status == models.UserStatus.pending_invitation).count()
        locked_accounts = users_query.filter(models.User.user_status == models.UserStatus.locked).count()
    except Exception as e:
        # Handle database schema issues with users
        total_users = active_users = pending_invitations = locked_accounts = 0
    
    # Organization metrics (with error handling)
    total_organizations = 0
    customer_organizations = 0
    supplier_organizations = 0
    try:
        total_organizations = organizations_query.count()
        customer_organizations = organizations_query.filter(models.Organization.organization_type == models.OrganizationType.customer).count()
        supplier_organizations = organizations_query.filter(models.Organization.organization_type == models.OrganizationType.supplier).count()
    except Exception as e:
        # Handle database schema issues with organizations
        total_organizations = customer_organizations = supplier_organizations = 0

    # Inventory metrics (with error handling)
    low_stock_items = 0
    out_of_stock_items = 0
    try:
        low_stock_items = inventory_query.filter(
            models.Inventory.current_stock <= models.Inventory.minimum_stock_recommendation,
            models.Inventory.minimum_stock_recommendation > 0
        ).count()
        out_of_stock_items = inventory_query.filter(models.Inventory.current_stock == 0).count()
    except Exception as e:
        # Handle database schema issues with inventory
        low_stock_items = out_of_stock_items = 0
    
    # Machine metrics (with error handling for schema issues)
    total_machines = 0
    active_machines = 0
    try:
        total_machines = machines_query.count()
        active_machines = machines_query.filter(models.Machine.status == models.MachineStatus.ACTIVE).count()
    except Exception as e:
        # Handle database schema mismatch - machines table may not have all expected columns
        total_machines = 0
        active_machines = 0

    # Order metrics (with error handling)
    pending_customer_orders = 0
    pending_supplier_orders = 0
    try:
        pending_customer_orders = customer_orders_query.filter(models.CustomerOrder.status == 'Pending').count()
    except Exception as e:
        # Handle database schema issues with customer orders
        pending_customer_orders = 0
    
    try:
        pending_supplier_orders = supplier_orders_query.filter(models.SupplierOrder.status == 'Pending').count()
    except Exception as e:
        # Handle database schema issues with supplier orders
        pending_supplier_orders = 0
    
    # Orders completed this month (with error handling)
    completed_orders_this_month = 0
    try:
        start_of_month = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        completed_customer_orders = customer_orders_query.filter(
            models.CustomerOrder.status == 'Completed',
            models.CustomerOrder.updated_at >= start_of_month
        ).count()
        completed_supplier_orders = supplier_orders_query.filter(
            models.SupplierOrder.status == 'Completed',
            models.SupplierOrder.updated_at >= start_of_month
        ).count()
        completed_orders_this_month = completed_customer_orders + completed_supplier_orders
    except Exception as e:
        # Handle database schema issues with completed orders
        completed_orders_this_month = 0
    
    # Recent activity (last 7 days)
    week_ago = datetime.now() - timedelta(days=7)
    
    # Recent part usage - count from part_usage table if it exists
    recent_part_usage = 0
    try:
        if hasattr(models, 'PartUsage'):
            part_usage_query = db.query(models.PartUsage).filter(models.PartUsage.created_at >= week_ago)
            if organization_id:
                # PartUsage is linked to customer_organization_id directly
                part_usage_query = part_usage_query.filter(models.PartUsage.customer_organization_id == organization_id)
            recent_part_usage = part_usage_query.count()
    except:
        recent_part_usage = 0
    
    # Recent stock adjustments
    recent_stock_adjustments = 0
    try:
        if hasattr(models, 'StockAdjustment'):
            stock_adj_query = db.query(models.StockAdjustment).filter(models.StockAdjustment.created_at >= week_ago)
            if organization_id:
                # StockAdjustment is linked through inventory -> warehouse -> organization
                stock_adj_query = stock_adj_query.join(models.Inventory).join(models.Warehouse).filter(models.Warehouse.organization_id == organization_id)
            recent_stock_adjustments = stock_adj_query.count()
    except:
        recent_stock_adjustments = 0
    
    # Recent transactions
    recent_transactions = 0
    try:
        if hasattr(models, 'Transaction'):
            trans_query = db.query(models.Transaction).filter(models.Transaction.created_at >= week_ago)
            if organization_id:
                trans_query = trans_query.filter(models.Transaction.organization_id == organization_id)
            recent_transactions = trans_query.count()
    except:
        recent_transactions = 0
    
    # Security metrics (simplified - would need proper security event tracking)
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    failed_login_attempts_today = 0  # Would need security events table
    security_events_today = 0  # Would need security events table
    active_sessions = 0  # Would need session tracking
    
    return {
        # User metrics
        "total_users": total_users,
        "active_users": active_users,
        "pending_invitations": pending_invitations,
        "locked_accounts": locked_accounts,
        
        # Organization metrics
        "total_organizations": total_organizations,
        "customer_organizations": customer_organizations,
        "supplier_organizations": supplier_organizations,
        
        # Inventory metrics
        "total_parts": total_parts,
        "total_inventory_items": total_inventory_items,
        "low_stock_items": low_stock_items,
        "out_of_stock_items": out_of_stock_items,
        
        # Machine metrics
        "total_machines": total_machines,
        "active_machines": active_machines,
        
        # Order metrics
        "pending_customer_orders": pending_customer_orders,
        "pending_supplier_orders": pending_supplier_orders,
        "completed_orders_this_month": completed_orders_this_month,
        
        # Recent activity
        "recent_part_usage": recent_part_usage,
        "recent_stock_adjustments": recent_stock_adjustments,
        "recent_transactions": recent_transactions,
        
        # Security metrics
        "failed_login_attempts_today": failed_login_attempts_today,
        "security_events_today": security_events_today,
        "active_sessions": active_sessions,
        
        # Timestamp
        "generated_at": datetime.now(),
    }

def get_low_stock_by_organization(db: Session, organization_id: Optional[uuid.UUID] = None):
    """
    Calculates the count of low-stock items for each organization.
    If organization_id is provided, results are scoped to that organization only.
    """
    query = db.query(
        models.Organization.name,
        func.count(models.Inventory.id)
    ).join(
        models.Warehouse, models.Organization.id == models.Warehouse.organization_id
    ).join(
        models.Inventory, models.Warehouse.id == models.Inventory.warehouse_id
    ).filter(
        models.Inventory.current_stock <= models.Inventory.minimum_stock_recommendation,
        models.Inventory.minimum_stock_recommendation > 0
    )
    
    # Apply organization scoping if provided
    if organization_id:
        query = query.filter(models.Organization.id == organization_id)
    
    results = query.group_by(
        models.Organization.name
    ).order_by(
        models.Organization.name
    ).all()

    return [{"organization_name": name, "low_stock_count": count} for name, count in results]