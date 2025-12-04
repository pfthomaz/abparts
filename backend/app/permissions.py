# backend/app/permissions.py

import uuid
from enum import Enum
from typing import Optional, List, Dict, Any, Callable
from functools import wraps
import logging
from datetime import datetime, timedelta

from fastapi import Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from .database import get_db
from .auth import get_current_user, TokenData
from . import models

logger = logging.getLogger(__name__)

# --- Permission System Enums ---

class ResourceType(str, Enum):
    """Types of resources that can be accessed."""
    ORGANIZATION = "organization"
    USER = "user"
    WAREHOUSE = "warehouse"
    PART = "part"
    INVENTORY = "inventory"
    MACHINE = "machine"
    TRANSACTION = "transaction"
    ORDER = "order"
    DASHBOARD = "dashboard"
    AUDIT_LOG = "audit_log"
    MAINTENANCE = "maintenance"

class PermissionType(str, Enum):
    """Types of permissions that can be granted."""
    READ = "read"
    WRITE = "write"
    DELETE = "delete"
    ADMIN = "admin"

# --- Permission Checker Class ---

class PermissionChecker:
    """Central class for checking user permissions and access rights."""
    
    def __init__(self):
        self._permission_cache: Dict[str, Dict[str, Any]] = {}
        self._cache_ttl = timedelta(minutes=15)  # Cache permissions for 15 minutes
    
    def _get_cache_key(self, user_id: uuid.UUID, resource: ResourceType, permission: PermissionType) -> str:
        """Generate cache key for permission check."""
        return f"perm:{user_id}:{resource.value}:{permission.value}"
    
    def _is_cache_valid(self, cache_entry: Dict[str, Any]) -> bool:
        """Check if cache entry is still valid."""
        if not cache_entry:
            return False
        cached_at = cache_entry.get("cached_at")
        if not cached_at:
            return False
        return datetime.utcnow() - cached_at < self._cache_ttl
    
    def _cache_permission(self, cache_key: str, result: bool, context: Dict[str, Any] = None):
        """Cache permission check result."""
        self._permission_cache[cache_key] = {
            "result": result,
            "context": context or {},
            "cached_at": datetime.utcnow()
        }
    
    def is_super_admin(self, user: TokenData) -> bool:
        """Check if user is a super admin."""
        return user.role == "super_admin"
    
    def is_admin(self, user: TokenData) -> bool:
        """Check if user is an admin (includes super_admin)."""
        return user.role in ["admin", "super_admin"]
    
    def is_user(self, user: TokenData) -> bool:
        """Check if user has basic user permissions."""
        return user.role in ["user", "admin", "super_admin"]
    
    def can_access_organization(self, user: TokenData, organization_id: uuid.UUID, db: Session) -> bool:
        """Check if user can access data from a specific organization."""
        # Super admins can access all organizations
        if self.is_super_admin(user):
            return True
        
        # Regular users can only access their own organization
        if user.organization_id == organization_id:
            return True
        
        # Check if the organization is a supplier of the user's organization
        org = db.query(models.Organization).filter(models.Organization.id == organization_id).first()
        if org and org.parent_organization_id == user.organization_id:
            return True
        
        return False
    
    def can_manage_users(self, user: TokenData, target_organization_id: uuid.UUID) -> bool:
        """Check if user can manage users in a specific organization."""
        # Super admins can manage users in any organization
        if self.is_super_admin(user):
            return True
        
        # Admins can manage users in their own organization
        if self.is_admin(user) and user.organization_id == target_organization_id:
            return True
        
        return False
    
    def can_manage_warehouses(self, user: TokenData, organization_id: uuid.UUID) -> bool:
        """Check if user can manage warehouses for an organization."""
        # Only admins and super_admins can manage warehouses
        if not self.is_admin(user):
            return False
        
        return self.can_access_organization(user, organization_id, None)
    
    def can_adjust_inventory(self, user: TokenData, warehouse_id: uuid.UUID, db: Session) -> bool:
        """Check if user can adjust inventory in a specific warehouse."""
        # Only admins and super_admins can adjust inventory
        if not self.is_admin(user):
            return False
        
        # Get warehouse organization
        warehouse = db.query(models.Warehouse).filter(models.Warehouse.id == warehouse_id).first()
        if not warehouse:
            return False
        
        return self.can_access_organization(user, warehouse.organization_id, db)
    
    def can_register_machines(self, user: TokenData) -> bool:
        """Check if user can register machines."""
        # Only super admins can register machines
        return self.is_super_admin(user)
    
    def can_view_transactions(self, user: TokenData, organization_id: uuid.UUID, db: Session) -> bool:
        """Check if user can view transactions for an organization."""
        return self.can_access_organization(user, organization_id, db)
    
    def can_view_audit_logs(self, user: TokenData, target_organization_id: uuid.UUID) -> bool:
        """Check if user can view audit logs for an organization."""
        # Super admins can view all audit logs
        if self.is_super_admin(user):
            return True
        
        # Admins can view audit logs for their own organization
        if self.is_admin(user) and user.organization_id == target_organization_id:
            return True
        
        return False
    
    def check_permission(self, user: TokenData, resource: ResourceType, permission: PermissionType, 
                        context: Dict[str, Any] = None, db: Session = None) -> bool:
        """
        Main permission checking method with caching.
        
        Args:
            user: Current user token data
            resource: Type of resource being accessed
            permission: Type of permission required
            context: Additional context (e.g., organization_id, warehouse_id)
            db: Database session for complex checks
        
        Returns:
            bool: True if permission is granted, False otherwise
        """
        # Check cache first
        cache_key = self._get_cache_key(user.user_id, resource, permission)
        cached_result = self._permission_cache.get(cache_key)
        
        if cached_result and self._is_cache_valid(cached_result):
            logger.debug(f"Permission cache hit for {cache_key}")
            return cached_result["result"]
        
        # Perform permission check
        result = self._check_permission_logic(user, resource, permission, context, db)
        
        # Cache the result
        self._cache_permission(cache_key, result, context)
        
        return result
    
    def _check_permission_logic(self, user: TokenData, resource: ResourceType, permission: PermissionType,
                               context: Dict[str, Any] = None, db: Session = None) -> bool:
        """Internal method to perform actual permission checking logic with enhanced organizational isolation."""
        context = context or {}
        
        # Super admins have access to everything
        if self.is_super_admin(user):
            return True
        
        # Import here to avoid circular imports
        from .organizational_isolation import organizational_isolation
        
        # Resource-specific permission checks with enhanced organizational validation
        if resource == ResourceType.ORGANIZATION:
            if permission == PermissionType.READ:
                # Users can read organizations they have access to
                org_id = context.get("organization_id")
                if org_id and db:
                    return organizational_isolation.validate_organization_access(user, org_id, db)
                return self.is_user(user)  # Can read own organization
            elif permission in [PermissionType.WRITE, PermissionType.DELETE]:
                # Only super admins can write/delete organizations
                return self.is_super_admin(user)
        
        elif resource == ResourceType.USER:
            if permission == PermissionType.READ:
                # Users can read users in organizations they have access to
                target_org_id = context.get("organization_id", user.organization_id)
                if db:
                    return organizational_isolation.validate_organization_access(user, target_org_id, db)
                return target_org_id == user.organization_id
            elif permission in [PermissionType.WRITE, PermissionType.DELETE, PermissionType.ADMIN]:
                # Admins can manage users in their organization and suppliers
                target_org_id = context.get("organization_id", user.organization_id)
                if not self.is_admin(user):
                    return False
                if db:
                    return organizational_isolation.validate_organization_access(user, target_org_id, db)
                return target_org_id == user.organization_id
        
        elif resource == ResourceType.WAREHOUSE:
            org_id = context.get("organization_id")
            if permission == PermissionType.READ:
                if org_id and db:
                    return organizational_isolation.validate_organization_access(user, org_id, db)
                return self.is_user(user)
            elif permission in [PermissionType.WRITE, PermissionType.DELETE]:
                if not self.is_admin(user):
                    return False
                if org_id and db:
                    return organizational_isolation.validate_organization_access(user, org_id, db)
                return self.is_admin(user)
        
        elif resource == ResourceType.INVENTORY:
            if permission == PermissionType.READ:
                org_id = context.get("organization_id")
                if org_id and db:
                    return organizational_isolation.validate_organization_access(user, org_id, db)
                return self.is_user(user)
            elif permission == PermissionType.WRITE:
                warehouse_id = context.get("warehouse_id")
                if not self.is_admin(user):
                    return False
                if warehouse_id and db:
                    # Get warehouse organization and validate access
                    warehouse = db.query(models.Warehouse).filter(models.Warehouse.id == warehouse_id).first()
                    if warehouse:
                        return organizational_isolation.validate_organization_access(user, warehouse.organization_id, db)
                return self.is_admin(user)
        
        elif resource == ResourceType.MACHINE:
            if permission == PermissionType.READ:
                org_id = context.get("organization_id")
                if org_id and db:
                    return organizational_isolation.validate_organization_access(user, org_id, db)
                return self.is_user(user)
            elif permission in [PermissionType.WRITE, PermissionType.DELETE]:
                # Machine registration/management requires super admin or specific organizational access
                if self.is_super_admin(user):
                    return True
                # Admins can manage machines in their own organization
                machine_org_id = context.get("organization_id")
                if machine_org_id and db and self.is_admin(user):
                    return organizational_isolation.validate_organization_access(user, machine_org_id, db)
                return False
        
        elif resource == ResourceType.TRANSACTION:
            if permission == PermissionType.READ:
                org_id = context.get("organization_id")
                if org_id and db:
                    return organizational_isolation.validate_organization_access(user, org_id, db)
                return self.is_user(user)
            elif permission == PermissionType.WRITE:
                # Validate cross-organizational transactions
                source_org_id = context.get("source_organization_id")
                target_org_id = context.get("target_organization_id")
                
                if source_org_id and target_org_id and db:
                    return organizational_isolation.validate_cross_organizational_access(
                        user, source_org_id, target_org_id, db
                    )
                elif source_org_id and db:
                    return organizational_isolation.validate_organization_access(user, source_org_id, db)
                
                return self.is_user(user)  # Basic transaction creation
            elif permission == PermissionType.DELETE:
                # Admins and super_admins can delete transactions in their organization
                if not self.is_admin(user):
                    return False
                org_id = context.get("organization_id")
                if org_id and db:
                    return organizational_isolation.validate_organization_access(user, org_id, db)
                return self.is_admin(user)
        
        elif resource == ResourceType.PART:
            if permission == PermissionType.READ:
                return self.is_user(user)  # All users can read parts
            elif permission in [PermissionType.WRITE, PermissionType.DELETE]:
                return self.is_super_admin(user)  # Only super admins can manage parts
        
        elif resource == ResourceType.ORDER:
            if permission == PermissionType.READ:
                org_id = context.get("organization_id")
                if org_id and db:
                    return organizational_isolation.validate_organization_access(user, org_id, db)
                return self.is_user(user)
            elif permission == PermissionType.WRITE:
                # Validate order creation within organizational boundaries
                customer_org_id = context.get("customer_organization_id")
                supplier_org_id = context.get("supplier_organization_id")
                
                if customer_org_id and db:
                    if not organizational_isolation.validate_organization_access(user, customer_org_id, db):
                        return False
                
                if supplier_org_id and db:
                    if not organizational_isolation.validate_supplier_visibility(user, supplier_org_id, db):
                        return False
                
                return self.is_user(user)
            elif permission == PermissionType.DELETE:
                # Only admins can delete orders
                return self.is_admin(user)
        
        elif resource == ResourceType.DASHBOARD:
            if permission == PermissionType.READ:
                return self.is_user(user)  # All users can view dashboard
        
        elif resource == ResourceType.AUDIT_LOG:
            if permission == PermissionType.READ:
                target_org_id = context.get("organization_id", user.organization_id)
                if db:
                    return organizational_isolation.validate_organization_access(user, target_org_id, db)
                return self.can_view_audit_logs(user, target_org_id)
        
        # Default deny
        return False
    
    def clear_cache(self, user_id: uuid.UUID = None):
        """Clear permission cache for a specific user or all users."""
        if user_id:
            # Clear cache for specific user
            keys_to_remove = [key for key in self._permission_cache.keys() if f":{user_id}:" in key]
            for key in keys_to_remove:
                del self._permission_cache[key]
        else:
            # Clear all cache
            self._permission_cache.clear()

# Global permission checker instance
permission_checker = PermissionChecker()

# --- Enhanced Organization-Scoped Query Filters ---

class OrganizationScopedQueries:
    """Enhanced helper class for applying organization-scoped filters to database queries."""
    
    @staticmethod
    def filter_organizations(query, user: TokenData, db: Session = None):
        """Apply organization-scoped filtering to organization queries."""
        if permission_checker.is_super_admin(user):
            return query  # Super admins see all organizations
        
        # Import here to avoid circular imports
        from .organizational_isolation import organizational_isolation
        
        if db:
            accessible_orgs = organizational_isolation.get_accessible_organization_ids(user, db)
            return query.filter(models.Organization.id.in_(accessible_orgs))
        else:
            # Fallback to basic filtering
            return query.filter(
                or_(
                    models.Organization.id == user.organization_id,
                    models.Organization.parent_organization_id == user.organization_id
                )
            )
    
    @staticmethod
    def filter_users(query, user: TokenData, db: Session = None):
        """Apply organization-scoped filtering to user queries."""
        if permission_checker.is_super_admin(user):
            return query  # Super admins see all users
        
        # Import here to avoid circular imports
        from .organizational_isolation import organizational_isolation
        
        if db:
            accessible_orgs = organizational_isolation.get_accessible_organization_ids(user, db)
            return query.filter(models.User.organization_id.in_(accessible_orgs))
        else:
            # Fallback to basic filtering
            return query.filter(models.User.organization_id == user.organization_id)
    
    @staticmethod
    def filter_warehouses(query, user: TokenData, db: Session = None):
        """Apply organization-scoped filtering to warehouse queries."""
        if permission_checker.is_super_admin(user):
            return query  # Super admins see all warehouses
        
        # Import here to avoid circular imports
        from .organizational_isolation import organizational_isolation
        
        if db:
            accessible_orgs = organizational_isolation.get_accessible_organization_ids(user, db)
            return query.join(models.Organization).filter(models.Organization.id.in_(accessible_orgs))
        else:
            # Fallback to basic filtering
            return query.join(models.Organization).filter(
                or_(
                    models.Organization.id == user.organization_id,
                    models.Organization.parent_organization_id == user.organization_id
                )
            )
    
    @staticmethod
    def filter_inventory(query, user: TokenData, db: Session = None):
        """Apply organization-scoped filtering to inventory queries."""
        if permission_checker.is_super_admin(user):
            return query  # Super admins see all inventory
        
        # Import here to avoid circular imports
        from .organizational_isolation import organizational_isolation
        
        if db:
            accessible_orgs = organizational_isolation.get_accessible_organization_ids(user, db)
            return query.join(models.Warehouse).join(models.Organization).filter(
                models.Organization.id.in_(accessible_orgs)
            )
        else:
            # Fallback to basic filtering
            return query.join(models.Warehouse).join(models.Organization).filter(
                or_(
                    models.Organization.id == user.organization_id,
                    models.Organization.parent_organization_id == user.organization_id
                )
            )
    
    @staticmethod
    def filter_machines(query, user: TokenData, db: Session = None):
        """Apply organization-scoped filtering to machine queries."""
        if permission_checker.is_super_admin(user):
            return query  # Super admins see all machines
        
        # Import here to avoid circular imports
        from .organizational_isolation import organizational_isolation
        
        if db:
            accessible_orgs = organizational_isolation.get_accessible_organization_ids(user, db)
            return query.filter(models.Machine.customer_organization_id.in_(accessible_orgs))
        else:
            # Fallback to basic filtering
            return query.filter(models.Machine.customer_organization_id == user.organization_id)
    
    @staticmethod
    def filter_transactions(query, user: TokenData, db: Session = None):
        """Apply organization-scoped filtering to transaction queries."""
        if permission_checker.is_super_admin(user):
            return query  # Super admins see all transactions
        
        # Import here to avoid circular imports
        from .organizational_isolation import organizational_isolation
        
        if db:
            accessible_orgs = organizational_isolation.get_accessible_organization_ids(user, db)
            # Filter transactions involving warehouses from accessible organizations
            return query.join(
                models.Warehouse, 
                or_(
                    models.Transaction.from_warehouse_id == models.Warehouse.id,
                    models.Transaction.to_warehouse_id == models.Warehouse.id
                )
            ).join(models.Organization).filter(models.Organization.id.in_(accessible_orgs))
        else:
            # Fallback to basic filtering
            return query.join(
                models.Warehouse, 
                or_(
                    models.Transaction.from_warehouse_id == models.Warehouse.id,
                    models.Transaction.to_warehouse_id == models.Warehouse.id
                )
            ).join(models.Organization).filter(
                or_(
                    models.Organization.id == user.organization_id,
                    models.Organization.parent_organization_id == user.organization_id
                )
            )
    
    @staticmethod
    def filter_supplier_orders(query, user: TokenData, db: Session = None):
        """Apply organization-scoped filtering to supplier order queries."""
        if permission_checker.is_super_admin(user):
            return query  # Super admins see all supplier orders
        
        # Import here to avoid circular imports
        from .organizational_isolation import organizational_isolation
        
        if db:
            accessible_orgs = organizational_isolation.get_accessible_organization_ids(user, db)
            return query.filter(models.SupplierOrder.ordering_organization_id.in_(accessible_orgs))
        else:
            # Fallback to basic filtering
            return query.filter(models.SupplierOrder.ordering_organization_id == user.organization_id)
    
    @staticmethod
    def filter_customer_orders(query, user: TokenData, db: Session = None):
        """Apply organization-scoped filtering to customer order queries."""
        if permission_checker.is_super_admin(user):
            return query  # Super admins see all customer orders
        
        # Import here to avoid circular imports
        from .organizational_isolation import organizational_isolation
        
        if db:
            accessible_orgs = organizational_isolation.get_accessible_organization_ids(user, db)
            return query.filter(
                or_(
                    models.CustomerOrder.customer_organization_id.in_(accessible_orgs),
                    models.CustomerOrder.oraseas_organization_id.in_(accessible_orgs)
                )
            )
        else:
            # Fallback to basic filtering
            return query.filter(
                or_(
                    models.CustomerOrder.customer_organization_id == user.organization_id,
                    models.CustomerOrder.oraseas_organization_id == user.organization_id
                )
            )
    
    @staticmethod
    def filter_part_usage(query, user: TokenData, db: Session = None):
        """Apply organization-scoped filtering to part usage queries."""
        if permission_checker.is_super_admin(user):
            return query  # Super admins see all part usage
        
        # Import here to avoid circular imports
        from .organizational_isolation import organizational_isolation
        
        if db:
            accessible_orgs = organizational_isolation.get_accessible_organization_ids(user, db)
            return query.filter(models.PartUsage.customer_organization_id.in_(accessible_orgs))
        else:
            # Fallback to basic filtering
            return query.filter(models.PartUsage.customer_organization_id == user.organization_id)

# --- Permission Dependency Functions ---

def require_permission(resource: ResourceType, permission: PermissionType, context_func: Callable = None):
    """
    Dependency function to require specific permissions for an endpoint.
    
    Args:
        resource: Type of resource being accessed
        permission: Type of permission required
        context_func: Optional function to extract context from request
    
    Returns:
        Dependency function for FastAPI
    """
    def permission_dependency(
        current_user: TokenData = Depends(get_current_user),
        db: Session = Depends(get_db),
        request: Request = None
    ) -> TokenData:
        # Extract context if function provided
        context = {}
        if context_func and request:
            context = context_func(request)
        
        # Check permission
        if not permission_checker.check_permission(current_user, resource, permission, context, db):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions for {resource.value}:{permission.value}"
            )
        
        return current_user
    
    return permission_dependency

def require_super_admin():
    """Dependency to require super admin role."""
    def super_admin_dependency(current_user: TokenData = Depends(get_current_user)) -> TokenData:
        if not permission_checker.is_super_admin(current_user):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Super admin access required"
            )
        return current_user
    
    return super_admin_dependency

def require_admin():
    """Dependency to require admin role (includes super_admin)."""
    def admin_dependency(current_user: TokenData = Depends(get_current_user)) -> TokenData:
        if not permission_checker.is_admin(current_user):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin access required"
            )
        return current_user
    
    return admin_dependency

def require_user():
    """Dependency to require basic user access."""
    def user_dependency(current_user: TokenData = Depends(get_current_user)) -> TokenData:
        if not permission_checker.is_user(current_user):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User access required"
            )
        return current_user
    
    return user_dependency

# --- Helper Functions ---

def check_organization_access(user: TokenData, organization_id: uuid.UUID, db: Session) -> bool:
    """Helper function to check if user can access a specific organization."""
    return permission_checker.can_access_organization(user, organization_id, db)

def get_accessible_organization_ids(user: TokenData, db: Session) -> List[uuid.UUID]:
    """Get list of organization IDs that the user can access."""
    if permission_checker.is_super_admin(user):
        # Super admins can access all organizations
        orgs = db.query(models.Organization.id).all()
        return [org.id for org in orgs]
    
    # Regular users can access their own organization and its suppliers
    accessible_orgs = db.query(models.Organization.id).filter(
        or_(
            models.Organization.id == user.organization_id,
            models.Organization.parent_organization_id == user.organization_id
        )
    ).all()
    
    return [org.id for org in accessible_orgs]

# --- Audit Logging ---

class AuditLogger:
    """Class for logging permission-related audit events."""
    
    @staticmethod
    def log_permission_denied(user: TokenData, resource: ResourceType, permission: PermissionType, 
                            context: Dict[str, Any] = None, request: Request = None):
        """Log permission denied events."""
        log_data = {
            "event": "permission_denied",
            "user_id": str(user.user_id),
            "username": user.username,
            "role": user.role,
            "organization_id": str(user.organization_id),
            "resource": resource.value,
            "permission": permission.value,
            "context": context or {},
            "timestamp": datetime.utcnow().isoformat()
        }
        
        if request:
            log_data.update({
                "ip_address": request.client.host if request.client else "unknown",
                "user_agent": request.headers.get("user-agent", "unknown"),
                "endpoint": str(request.url)
            })
        
        logger.warning(f"Permission denied: {log_data}")
    
    @staticmethod
    def log_permission_granted(user: TokenData, resource: ResourceType, permission: PermissionType,
                             context: Dict[str, Any] = None):
        """Log permission granted events."""
        log_data = {
            "event": "permission_granted",
            "user_id": str(user.user_id),
            "username": user.username,
            "role": user.role,
            "organization_id": str(user.organization_id),
            "resource": resource.value,
            "permission": permission.value,
            "context": context or {},
            "timestamp": datetime.utcnow().isoformat()
        }
        
        logger.info(f"Permission granted: {log_data}")

# Global audit logger instance
audit_logger = AuditLogger()

# --- Enhanced Role-Based Resource Access Matrix ---

class RoleBasedAccessMatrix:
    """
    Enhanced role-based access control matrix with organizational isolation.
    Defines granular permissions for each role and resource combination.
    """
    
    def __init__(self):
        # Define the access matrix: role -> resource -> permissions
        self.access_matrix = {
            "super_admin": {
                ResourceType.ORGANIZATION: [PermissionType.READ, PermissionType.WRITE, PermissionType.DELETE, PermissionType.ADMIN],
                ResourceType.USER: [PermissionType.READ, PermissionType.WRITE, PermissionType.DELETE, PermissionType.ADMIN],
                ResourceType.WAREHOUSE: [PermissionType.READ, PermissionType.WRITE, PermissionType.DELETE, PermissionType.ADMIN],
                ResourceType.PART: [PermissionType.READ, PermissionType.WRITE, PermissionType.DELETE, PermissionType.ADMIN],
                ResourceType.INVENTORY: [PermissionType.READ, PermissionType.WRITE, PermissionType.DELETE, PermissionType.ADMIN],
                ResourceType.MACHINE: [PermissionType.READ, PermissionType.WRITE, PermissionType.DELETE, PermissionType.ADMIN],
                ResourceType.TRANSACTION: [PermissionType.READ, PermissionType.WRITE, PermissionType.DELETE, PermissionType.ADMIN],
                ResourceType.ORDER: [PermissionType.READ, PermissionType.WRITE, PermissionType.DELETE, PermissionType.ADMIN],
                ResourceType.DASHBOARD: [PermissionType.READ, PermissionType.ADMIN],
                ResourceType.AUDIT_LOG: [PermissionType.READ, PermissionType.ADMIN]
            },
            "admin": {
                ResourceType.ORGANIZATION: [PermissionType.READ],  # Can only read own organization
                ResourceType.USER: [PermissionType.READ, PermissionType.WRITE, PermissionType.DELETE],  # Within own org
                ResourceType.WAREHOUSE: [PermissionType.READ, PermissionType.WRITE, PermissionType.DELETE],  # Within own org
                ResourceType.PART: [PermissionType.READ],  # Can read all parts, cannot modify
                ResourceType.INVENTORY: [PermissionType.READ, PermissionType.WRITE],  # Can adjust inventory
                ResourceType.MACHINE: [PermissionType.READ, PermissionType.WRITE],  # Can manage machines in own org
                ResourceType.TRANSACTION: [PermissionType.READ, PermissionType.WRITE],  # Can create transactions
                ResourceType.ORDER: [PermissionType.READ, PermissionType.WRITE, PermissionType.DELETE],  # Can manage and delete orders
                ResourceType.DASHBOARD: [PermissionType.READ],
                ResourceType.AUDIT_LOG: [PermissionType.READ]  # Can view own org audit logs
            },
            "user": {
                ResourceType.ORGANIZATION: [PermissionType.READ],  # Can only read own organization
                ResourceType.USER: [PermissionType.READ],  # Can read users in own org
                ResourceType.WAREHOUSE: [PermissionType.READ],  # Can read warehouses in own org
                ResourceType.PART: [PermissionType.READ],  # Can read all parts
                ResourceType.INVENTORY: [PermissionType.READ],  # Can read inventory
                ResourceType.MACHINE: [PermissionType.READ, PermissionType.WRITE],  # Can record hours/usage
                ResourceType.TRANSACTION: [PermissionType.READ, PermissionType.WRITE],  # Can create basic transactions
                ResourceType.ORDER: [PermissionType.READ, PermissionType.WRITE],  # Can place orders
                ResourceType.DASHBOARD: [PermissionType.READ],
                ResourceType.AUDIT_LOG: []  # No audit log access
            }
        }
        
        # Define organizational constraints for each resource
        self.organizational_constraints = {
            ResourceType.ORGANIZATION: {
                "super_admin": "all",  # Can access all organizations
                "admin": "own_and_suppliers",  # Can access own org and its suppliers
                "user": "own_and_suppliers"  # Can access own org and its suppliers
            },
            ResourceType.USER: {
                "super_admin": "all",
                "admin": "own_and_suppliers",
                "user": "own_and_suppliers"
            },
            ResourceType.WAREHOUSE: {
                "super_admin": "all",
                "admin": "own_and_suppliers",
                "user": "own_and_suppliers"
            },
            ResourceType.INVENTORY: {
                "super_admin": "all",
                "admin": "own_and_suppliers",
                "user": "own_and_suppliers"
            },
            ResourceType.MACHINE: {
                "super_admin": "all",
                "admin": "own_and_suppliers",
                "user": "own_and_suppliers"
            },
            ResourceType.TRANSACTION: {
                "super_admin": "all",
                "admin": "own_and_suppliers",
                "user": "own_and_suppliers"
            },
            ResourceType.ORDER: {
                "super_admin": "all",
                "admin": "own_and_suppliers",
                "user": "own_and_suppliers"
            },
            ResourceType.PART: {
                "super_admin": "all",
                "admin": "all",  # Parts are global
                "user": "all"  # Parts are global
            },
            ResourceType.DASHBOARD: {
                "super_admin": "all",
                "admin": "own_and_suppliers",
                "user": "own_and_suppliers"
            },
            ResourceType.AUDIT_LOG: {
                "super_admin": "all",
                "admin": "own_and_suppliers",
                "user": "none"
            }
        }
        
        # Define special business rules
        self.business_rules = {
            "bossaqua_restriction": {
                "description": "BossAqua data is only accessible to super admins initially",
                "applies_to": ["admin", "user"],
                "restriction": "exclude_bossaqua_organization"
            },
            "supplier_visibility": {
                "description": "Suppliers are only visible to their parent organization",
                "applies_to": ["admin", "user"],
                "restriction": "parent_organization_only"
            },
            "machine_registration": {
                "description": "Only super admins can register new machines",
                "applies_to": ["admin", "user"],
                "restriction": "no_machine_creation"
            },
            "parts_management": {
                "description": "Only super admins can create/edit/delete parts",
                "applies_to": ["admin", "user"],
                "restriction": "read_only_parts"
            }
        }
    
    def has_permission(self, user_role: str, resource: ResourceType, permission: PermissionType) -> bool:
        """
        Check if a role has a specific permission for a resource.
        
        Args:
            user_role: User's role
            resource: Resource type
            permission: Permission type
            
        Returns:
            bool: True if permission is granted
        """
        role_permissions = self.access_matrix.get(user_role, {})
        resource_permissions = role_permissions.get(resource, [])
        return permission in resource_permissions
    
    def get_organizational_constraint(self, user_role: str, resource: ResourceType) -> str:
        """
        Get organizational constraint for a role and resource.
        
        Args:
            user_role: User's role
            resource: Resource type
            
        Returns:
            str: Organizational constraint level
        """
        resource_constraints = self.organizational_constraints.get(resource, {})
        return resource_constraints.get(user_role, "none")
    
    def get_role_permissions(self, user_role: str) -> Dict[ResourceType, List[PermissionType]]:
        """
        Get all permissions for a specific role.
        
        Args:
            user_role: User's role
            
        Returns:
            Dictionary mapping resources to permissions
        """
        return self.access_matrix.get(user_role, {})
    
    def get_resource_permissions(self, resource: ResourceType) -> Dict[str, List[PermissionType]]:
        """
        Get all role permissions for a specific resource.
        
        Args:
            resource: Resource type
            
        Returns:
            Dictionary mapping roles to permissions
        """
        resource_perms = {}
        for role, role_permissions in self.access_matrix.items():
            resource_perms[role] = role_permissions.get(resource, [])
        return resource_perms
    
    def validate_business_rules(self, user_role: str, resource: ResourceType, 
                              context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Validate business rules for a role and resource combination.
        
        Args:
            user_role: User's role
            resource: Resource type
            context: Additional context for validation
            
        Returns:
            Dictionary with validation result
        """
        context = context or {}
        violations = []
        
        # Check BossAqua restriction
        if (user_role in self.business_rules["bossaqua_restriction"]["applies_to"] and
            context.get("organization_type") == "bossaqua"):
            violations.append({
                "rule": "bossaqua_restriction",
                "message": "BossAqua data is only accessible to super admins"
            })
        
        # Check supplier visibility
        if (user_role in self.business_rules["supplier_visibility"]["applies_to"] and
            resource == ResourceType.ORGANIZATION and
            context.get("organization_type") == "supplier"):
            if not context.get("is_parent_organization"):
                violations.append({
                    "rule": "supplier_visibility",
                    "message": "Suppliers are only visible to their parent organization"
                })
        
        # Check machine registration
        if (user_role in self.business_rules["machine_registration"]["applies_to"] and
            resource == ResourceType.MACHINE and
            context.get("operation") == "create"):
            violations.append({
                "rule": "machine_registration",
                "message": "Only super admins can register new machines"
            })
        
        # Check parts management
        if (user_role in self.business_rules["parts_management"]["applies_to"] and
            resource == ResourceType.PART and
            context.get("operation") in ["create", "update", "delete"]):
            violations.append({
                "rule": "parts_management",
                "message": "Only super admins can create/edit/delete parts"
            })
        
        return {
            "valid": len(violations) == 0,
            "violations": violations
        }
    
    def get_accessible_resources(self, user_role: str) -> List[ResourceType]:
        """
        Get list of resources that a role can access.
        
        Args:
            user_role: User's role
            
        Returns:
            List of accessible resource types
        """
        role_permissions = self.access_matrix.get(user_role, {})
        return list(role_permissions.keys())
    
    def generate_permission_summary(self, user_role: str) -> Dict[str, Any]:
        """
        Generate a comprehensive permission summary for a role.
        
        Args:
            user_role: User's role
            
        Returns:
            Dictionary with permission summary
        """
        role_permissions = self.get_role_permissions(user_role)
        
        summary = {
            "role": user_role,
            "total_resources": len(role_permissions),
            "permissions_by_resource": {},
            "organizational_constraints": {},
            "business_rules": []
        }
        
        for resource, permissions in role_permissions.items():
            summary["permissions_by_resource"][resource.value] = [p.value for p in permissions]
            summary["organizational_constraints"][resource.value] = self.get_organizational_constraint(user_role, resource)
        
        # Add applicable business rules
        for rule_name, rule_info in self.business_rules.items():
            if user_role in rule_info["applies_to"]:
                summary["business_rules"].append({
                    "rule": rule_name,
                    "description": rule_info["description"],
                    "restriction": rule_info["restriction"]
                })
        
        return summary

# Global access matrix instance
role_based_access_matrix = RoleBasedAccessMatrix()

# --- Enhanced Permission Validation Functions ---

def validate_cross_organizational_access_permission(user: TokenData, source_org_id: uuid.UUID, 
                                                  target_org_id: uuid.UUID, operation: str,
                                                  db: Session) -> Dict[str, Any]:
    """
    Enhanced validation for cross-organizational access with detailed logging.
    
    Args:
        user: Current user token data
        source_org_id: Source organization ID
        target_org_id: Target organization ID
        operation: Type of operation being performed
        db: Database session
        
    Returns:
        Dictionary with validation result and details
    """
    try:
        # Import here to avoid circular imports
        from .organizational_isolation import organizational_isolation
        
        # Super admins can perform any cross-organizational operations
        if user.role == "super_admin":
            audit_logger.log_permission_granted(
                user, ResourceType.TRANSACTION, PermissionType.WRITE,
                {
                    "operation": operation,
                    "source_org": str(source_org_id),
                    "target_org": str(target_org_id),
                    "reason": "super_admin_access"
                }
            )
            return {
                "allowed": True,
                "reason": "super_admin_access",
                "validation_details": {
                    "source_org_accessible": True,
                    "target_org_accessible": True,
                    "cross_org_rules_validated": True
                }
            }
        
        # Validate access to both organizations
        source_accessible = organizational_isolation.validate_organization_access(user, source_org_id, db)
        target_accessible = organizational_isolation.validate_organization_access(user, target_org_id, db)
        
        if not source_accessible:
            audit_logger.log_permission_denied(
                user, ResourceType.TRANSACTION, PermissionType.WRITE,
                {
                    "operation": operation,
                    "source_org": str(source_org_id),
                    "target_org": str(target_org_id),
                    "reason": "source_org_access_denied"
                }
            )
            return {
                "allowed": False,
                "reason": f"Access denied to source organization {source_org_id}",
                "validation_details": {
                    "source_org_accessible": False,
                    "target_org_accessible": target_accessible
                }
            }
        
        if not target_accessible:
            audit_logger.log_permission_denied(
                user, ResourceType.TRANSACTION, PermissionType.WRITE,
                {
                    "operation": operation,
                    "source_org": str(source_org_id),
                    "target_org": str(target_org_id),
                    "reason": "target_org_access_denied"
                }
            )
            return {
                "allowed": False,
                "reason": f"Access denied to target organization {target_org_id}",
                "validation_details": {
                    "source_org_accessible": True,
                    "target_org_accessible": False
                }
            }
        
        # Validate cross-organizational business rules
        cross_org_allowed = organizational_isolation.validate_cross_organizational_access(
            user, source_org_id, target_org_id, db
        )
        
        if not cross_org_allowed:
            audit_logger.log_permission_denied(
                user, ResourceType.TRANSACTION, PermissionType.WRITE,
                {
                    "operation": operation,
                    "source_org": str(source_org_id),
                    "target_org": str(target_org_id),
                    "reason": "cross_org_business_rules_violation"
                }
            )
            return {
                "allowed": False,
                "reason": f"Cross-organizational {operation} not allowed between {source_org_id} and {target_org_id}",
                "validation_details": {
                    "source_org_accessible": True,
                    "target_org_accessible": True,
                    "cross_org_rules_validated": False
                }
            }
        
        # All validations passed
        audit_logger.log_permission_granted(
            user, ResourceType.TRANSACTION, PermissionType.WRITE,
            {
                "operation": operation,
                "source_org": str(source_org_id),
                "target_org": str(target_org_id),
                "reason": "cross_org_validation_passed"
            }
        )
        
        return {
            "allowed": True,
            "reason": "cross_organizational_access_validated",
            "validation_details": {
                "source_org_accessible": True,
                "target_org_accessible": True,
                "cross_org_rules_validated": True
            }
        }
        
    except Exception as e:
        logger.error(f"Error validating cross-organizational access: {e}")
        return {
            "allowed": False,
            "reason": "validation_error",
            "error": str(e)
        }

def enforce_role_based_resource_access(user: TokenData, resource: ResourceType, 
                                     permission: PermissionType, context: Dict[str, Any] = None,
                                     db: Session = None) -> Dict[str, Any]:
    """
    Enforce role-based resource access with enhanced validation and logging.
    
    Args:
        user: Current user token data
        resource: Resource type being accessed
        permission: Permission type required
        context: Additional context for validation
        db: Database session
        
    Returns:
        Dictionary with enforcement result
    """
    context = context or {}
    
    try:
        # Check basic role-based permission
        has_basic_permission = role_based_access_matrix.has_permission(user.role, resource, permission)
        
        if not has_basic_permission:
            audit_logger.log_permission_denied(
                user, resource, permission,
                {**context, "reason": "insufficient_role_permissions"}
            )
            return {
                "allowed": False,
                "reason": f"Role '{user.role}' does not have '{permission.value}' permission for '{resource.value}'",
                "enforcement_details": {
                    "basic_permission_check": False,
                    "organizational_validation": "skipped",
                    "business_rules_validation": "skipped"
                }
            }
        
        # Validate business rules
        business_rules_result = role_based_access_matrix.validate_business_rules(user.role, resource, context)
        
        if not business_rules_result["valid"]:
            audit_logger.log_permission_denied(
                user, resource, permission,
                {**context, "reason": "business_rules_violation", "violations": business_rules_result["violations"]}
            )
            return {
                "allowed": False,
                "reason": "Business rule violations",
                "violations": business_rules_result["violations"],
                "enforcement_details": {
                    "basic_permission_check": True,
                    "organizational_validation": "skipped",
                    "business_rules_validation": False
                }
            }
        
        # Validate organizational constraints if database session provided
        organizational_validation = "not_required"
        if db and context.get("organization_id"):
            from .organizational_isolation import organizational_isolation
            
            org_id = context["organization_id"]
            if isinstance(org_id, str):
                org_id = uuid.UUID(org_id)
            
            org_access_allowed = organizational_isolation.validate_organization_access(user, org_id, db)
            
            if not org_access_allowed:
                audit_logger.log_permission_denied(
                    user, resource, permission,
                    {**context, "reason": "organizational_access_denied"}
                )
                return {
                    "allowed": False,
                    "reason": f"Access denied to organization {org_id}",
                    "enforcement_details": {
                        "basic_permission_check": True,
                        "organizational_validation": False,
                        "business_rules_validation": True
                    }
                }
            
            organizational_validation = "passed"
        
        # All validations passed
        audit_logger.log_permission_granted(
            user, resource, permission,
            {**context, "reason": "all_validations_passed"}
        )
        
        return {
            "allowed": True,
            "reason": "Access granted",
            "enforcement_details": {
                "basic_permission_check": True,
                "organizational_validation": organizational_validation,
                "business_rules_validation": True
            }
        }
        
    except Exception as e:
        logger.error(f"Error enforcing role-based resource access: {e}")
        audit_logger.log_permission_denied(
            user, resource, permission,
            {**context, "reason": "enforcement_error", "error": str(e)}
        )
        return {
            "allowed": False,
            "reason": "Permission enforcement error",
            "error": str(e)
        }

# --- Enhanced Dependency Functions ---

def require_enhanced_permission(resource: ResourceType, permission: PermissionType, 
                              extract_context: Callable = None):
    """
    Enhanced permission dependency with role-based access matrix enforcement.
    
    Args:
        resource: Resource type being accessed
        permission: Permission type required
        extract_context: Function to extract context from request
        
    Returns:
        FastAPI dependency function
    """
    def enhanced_permission_dependency(
        current_user: TokenData = Depends(get_current_user),
        db: Session = Depends(get_db),
        request: Request = None
    ) -> TokenData:
        # Extract context if function provided
        context = {}
        if extract_context and request:
            try:
                context = extract_context(request)
            except Exception as e:
                logger.warning(f"Error extracting context for permission check: {e}")
        
        # Enforce role-based resource access
        enforcement_result = enforce_role_based_resource_access(
            current_user, resource, permission, context, db
        )
        
        if not enforcement_result["allowed"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "message": enforcement_result["reason"],
                    "resource": resource.value,
                    "permission": permission.value,
                    "details": enforcement_result.get("enforcement_details", {}),
                    "violations": enforcement_result.get("violations", [])
                }
            )
        
        return current_user
    
    return enhanced_permission_dependency

def require_organizational_access(organization_param: str = "organization_id"):
    """
    Dependency to require access to a specific organization.
    
    Args:
        organization_param: Name of the parameter containing organization ID
        
    Returns:
        FastAPI dependency function
    """
    def organizational_access_dependency(
        current_user: TokenData = Depends(get_current_user),
        db: Session = Depends(get_db),
        request: Request = None
    ) -> TokenData:
        # Extract organization ID from request
        org_id = None
        
        if request:
            # Try path parameters first
            if hasattr(request, "path_params") and organization_param in request.path_params:
                try:
                    org_id = uuid.UUID(request.path_params[organization_param])
                except ValueError:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Invalid organization ID format: {request.path_params[organization_param]}"
                    )
            
            # Try query parameters if not found in path
            elif request.url.query:
                from urllib.parse import parse_qs
                query_params = parse_qs(request.url.query)
                if organization_param in query_params:
                    try:
                        org_id = uuid.UUID(query_params[organization_param][0])
                    except (ValueError, IndexError):
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Invalid organization ID in query parameters"
                        )
        
        if org_id:
            from .organizational_isolation import organizational_isolation
            
            if not organizational_isolation.validate_organization_access(current_user, org_id, db):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Access denied to organization {org_id}"
                )
        
        return current_user
    
    return organizational_access_dependency

# Note: AuditLogger class is defined earlier in this file (line ~637)
# The global audit_logger instance is also defined there