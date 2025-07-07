# c:/abparts/backend/app/crud/dashboard.py

from sqlalchemy.orm import Session
from sqlalchemy import func
from .. import models

def get_dashboard_metrics(db: Session):
    """
    Calculates and returns key metrics for the dashboard.
    """
    total_parts = db.query(models.Part).count()
    total_inventory_items = db.query(models.Inventory).count()

    # Low stock is where current_stock is less than or equal to minimum_stock_recommendation
    # and minimum_stock_recommendation is greater than 0 to avoid flagging items with 0/0 stock.
    low_stock_items = db.query(models.Inventory).filter(
        models.Inventory.current_stock <= models.Inventory.minimum_stock_recommendation,
        models.Inventory.minimum_stock_recommendation > 0
    ).count()

    pending_customer_orders = db.query(models.CustomerOrder).filter(models.CustomerOrder.status == 'Pending').count()
    pending_supplier_orders = db.query(models.SupplierOrder).filter(models.SupplierOrder.status == 'Pending').count()

    return {
        "total_parts": total_parts,
        "total_inventory_items": total_inventory_items,
        "low_stock_items": low_stock_items,
        "pending_customer_orders": pending_customer_orders,
        "pending_supplier_orders": pending_supplier_orders,
    }

def get_low_stock_by_organization(db: Session):
    """
    Calculates the count of low-stock items for each organization.
    """
    results = db.query(
        models.Organization.name,
        func.count(models.Inventory.id)
    ).join(
        models.Inventory, models.Organization.id == models.Inventory.organization_id
    ).filter(
        models.Inventory.current_stock <= models.Inventory.minimum_stock_recommendation,
        models.Inventory.minimum_stock_recommendation > 0
    ).group_by(
        models.Organization.name
    ).order_by(
        models.Organization.name
    ).all()

    return [{"organization_name": name, "low_stock_count": count} for name, count in results]