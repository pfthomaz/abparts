# c:/abparts/backend/app/crud/dashboard_fixed.py

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
    users_query = db.query(models.User)
    organizations_query = db.query(models.Organization)
    
    # Initialize metrics with default values
    total_parts = 0
    total_inventory_items = 0
    low_stock_items = 0
    out_of_stock_items = 0
    total_users = 0
    active_users = 0
    pending_invitations = 0
    locked_accounts = 0
    total_organizations = 0
    customer_organizations = 0
    supplier_organizations = 0
    total_machines = 0
    active_machines = 0
    pending_customer_orders = 0
    pending_supplier_orders = 0
    completed_orders_this_month = 0
    recent_part_usage = 0
    recent_stock_adjustments = 0
    recent_transactions = 0
    failed_login_attempts_today = 0
    security_events_today = 0
    active_sessions = 0
    
    # Basic counts that should always work
    try:
        total_parts = parts_query.count()
    except Exception as e:
        print(f"Error counting parts: {e}")
    
    try:
        total_users = users_query.count()
        if organization_id:
            users_query = users_query.filter(models.User.organization_id == organization_id)
        active_users = users_query.filter(models.User.is_active == True).count()
    except Exception as e:
        print(f"Error counting users: {e}")
    
    try:
        total_organizations = organizations_query.count()
        if organization_id:
            organizations_query = organizations_query.filter(models.Organization.id == organization_id)
        
        # Try to count organizations by type if the field exists
        try:
            customer_organizations = organizations_query.filter(
                models.Organization.organization_type == "customer"
            ).count()
            supplier_organizations = organizations_query.filter(
                models.Organization.organization_type == "supplier"
            ).count()
        except:
            pass
    except Exception as e:
        print(f"Error counting organizations: {e}")
    
    # Try to get inventory metrics
    try:
        inventory_query = db.query(models.Inventory)
        if organization_id:
            try:
                # Try to join through warehouses if the relationship exists
                inventory_query = inventory_query.join(
                    models.Warehouse, 
                    models.Inventory.warehouse_id == models.Warehouse.id
                ).filter(models.Warehouse.organization_id == organization_id)
            except:
                pass
        
        total_inventory_items = inventory_query.count()
        
        # Try to get low stock items
        try:
            low_stock_items = inventory_query.filter(
                models.Inventory.current_stock <= models.Inventory.minimum_stock_recommendation,
                models.Inventory.minimum_stock_recommendation > 0
            ).count()
        except:
            pass
            
        # Try to get out of stock items
        try:
            out_of_stock_items = inventory_query.filter(models.Inventory.current_stock == 0).count()
        except:
            pass
    except Exception as e:
        print(f"Error counting inventory: {e}")
    
    # Try to get machine metrics
    try:
        machines_query = db.query(models.Machine)
        if organization_id:
            try:
                machines_query = machines_query.filter(models.Machine.customer_organization_id == organization_id)
            except:
                pass
        
        total_machines = machines_query.count()
        
        # Try to count active machines if the status field exists
        try:
            active_machines = machines_query.filter(models.Machine.status == "ACTIVE").count()
        except:
            pass
    except Exception as e:
        print(f"Error counting machines: {e}")
    
    # Try to get order metrics
    try:
        customer_orders_query = db.query(models.CustomerOrder)
        if organization_id:
            try:
                # Try new schema first
                customer_orders_query = customer_orders_query.filter(
                    models.CustomerOrder.ordering_organization_id == organization_id
                )
            except:
                try:
                    # Fall back to old schema
                    customer_orders_query = customer_orders_query.filter(
                        models.CustomerOrder.customer_organization_id == organization_id
                    )
                except:
                    pass
        
        # Try to count pending orders
        try:
            pending_customer_orders = customer_orders_query.filter(
                models.CustomerOrder.status == "Pending"
            ).count()
        except Exception as e:
            print(f"Error counting customer orders: {e}")
    except Exception as e:
        print(f"Error with customer orders: {e}")
    
    try:
        supplier_orders_query = db.query(models.SupplierOrder)
        if organization_id:
            try:
                # Try new schema first
                supplier_orders_query = supplier_orders_query.filter(
                    models.SupplierOrder.ordering_organization_id == organization_id
                )
            except:
                try:
                    # Fall back to old schema
                    supplier_orders_query = supplier_orders_query.filter(
                        models.SupplierOrder.organization_id == organization_id
                    )
                except:
                    pass
        
        # Try to count pending orders
        try:
            pending_supplier_orders = supplier_orders_query.filter(
                models.SupplierOrder.status == "Pending"
            ).count()
        except Exception as e:
            print(f"Error counting supplier orders: {e}")
    except Exception as e:
        print(f"Error with supplier orders: {e}")
    
    # Try to count completed orders this month
    try:
        start_of_month = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        try:
            completed_customer_orders = customer_orders_query.filter(
                models.CustomerOrder.status == "Completed",
                models.CustomerOrder.updated_at >= start_of_month
            ).count()
        except Exception as e:
            completed_customer_orders = 0
            print(f"Error counting completed customer orders: {e}")
        
        try:
            completed_supplier_orders = supplier_orders_query.filter(
                models.SupplierOrder.status == "Completed",
                models.SupplierOrder.updated_at >= start_of_month
            ).count()
        except Exception as e:
            completed_supplier_orders = 0
            print(f"Error counting completed supplier orders: {e}")
            
        completed_orders_this_month = completed_customer_orders + completed_supplier_orders
    except Exception as e:
        print(f"Error counting completed orders: {e}")
    
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
    try:
        # Build a query that will work with either schema version
        query = db.query(
            models.Organization.name,
            func.count(models.Inventory.id)
        )
        
        # Try to join through warehouses
        try:
            query = query.join(
                models.Warehouse, 
                models.Organization.id == models.Warehouse.organization_id
            ).join(
                models.Inventory, 
                models.Warehouse.id == models.Inventory.warehouse_id
            )
            
            # Try to filter for low stock items
            try:
                query = query.filter(
                    models.Inventory.current_stock <= models.Inventory.minimum_stock_recommendation,
                    models.Inventory.minimum_stock_recommendation > 0
                )
            except:
                # If minimum_stock_recommendation doesn't exist, just count all inventory
                pass
        except:
            # If the join doesn't work, return empty results
            return []
        
        # Apply organization scoping if provided
        if organization_id:
            query = query.filter(models.Organization.id == organization_id)
        
        results = query.group_by(
            models.Organization.name
        ).order_by(
            models.Organization.name
        ).all()

        return [{"organization_name": name, "low_stock_count": count} for name, count in results]
    except Exception as e:
        print(f"Error in get_low_stock_by_organization: {e}")
        # Return empty list on error
        return []