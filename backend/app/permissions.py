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
        """Internal method to perform actual permission checking logic."""
        context = context or {}
        
        # Super admins have access to everything
        if self.is_super_admin(user):
            return True
        
        # Resource-specific permission checks
        if resource == ResourceType.ORGANIZATION:
            if permission == PermissionType.READ:
                # Users can read organizations they have access to
                org_id = context.get("organization_id")
                if org_id and db:
                    return self.can_access_organization(user, org_id, db)
                return self.is_user(user)  # Can read own organization
            elif permission in [PermissionType.WRITE, PermissionType.DELETE]:
                # Only super admins can write/delete organizations
                return self.is_super_admin(user)
        
        elif resource == ResourceType.USER:
            if permission == PermissionType.READ:
                # Users can read users in their organization
                target_org_id = context.get("organization_id", user.organization_id)
                return self.can_access_organization(user, target_org_id, db) if db else True
            elif permission in [PermissionType.WRITE, PermissionType.DELETE, PermissionType.ADMIN]:
                # Admins can manage users in their organization
                target_org_id = context.get("organization_id", user.organization_id)
                return self.can_manage_users(user, target_org_id)
        
        elif resource == ResourceType.WAREHOUSE:
            org_id = context.get("organization_id")
            if permission == PermissionType.READ:
                return self.can_access_organization(user, org_id, db) if org_id and db else self.is_user(user)
            elif permission in [PermissionType.WRITE, PermissionType.DELETE]:
                return self.can_manage_warehouses(user, org_id) if org_id else self.is_admin(user)
        
        elif resource == ResourceType.INVENTORY:
            if permission == PermissionType.READ:
                org_id = context.get("organization_id")
                return self.can_access_organization(user, org_id, db) if org_id and db else self.is_user(user)
            elif permission == PermissionType.WRITE:
                warehouse_id = context.get("warehouse_id")
                return self.can_adjust_inventory(user, warehouse_id, db) if warehouse_id and db else self.is_admin(user)
        
        elif resource == ResourceType.MACHINE:
            if permission == PermissionType.READ:
                org_id = context.get("organization_id")
                return self.can_access_organization(user, org_id, db) if org_id and db else self.is_user(user)
            elif permission in [PermissionType.WRITE, PermissionType.DELETE]:
                return self.can_register_machines(user)
        
        elif resource == ResourceType.TRANSACTION:
            org_id = context.get("organization_id")
            if permission == PermissionType.READ:
                return self.can_view_transactions(user, org_id, db) if org_id and db else self.is_user(user)
            elif permission == PermissionType.WRITE:
                return self.is_user(user)  # All users can create transactions
        
        elif resource == ResourceType.PART:
            if permission == PermissionType.READ:
                return self.is_user(user)  # All users can read parts
            elif permission in [PermissionType.WRITE, PermissionType.DELETE]:
                return self.is_super_admin(user)  # Only super admins can manage parts
        
        elif resource == ResourceType.ORDER:
            org_id = context.get("organization_id")
            if permission == PermissionType.READ:
                return self.can_access_organization(user, org_id, db) if org_id and db else self.is_user(user)
            elif permission == PermissionType.WRITE:
                return self.is_user(user)  # All users can create orders
        
        elif resource == ResourceType.DASHBOARD:
            if permission == PermissionType.READ:
                return self.is_user(user)  # All users can view dashboard
        
        elif resource == ResourceType.AUDIT_LOG:
            if permission == PermissionType.READ:
                target_org_id = context.get("organization_id", user.organization_id)
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

# --- Organization-Scoped Query Filters ---

class OrganizationScopedQueries:
    """Helper class for applying organization-scoped filters to database queries."""
    
    @staticmethod
    def filter_organizations(query, user: TokenData):
        """Apply organization-scoped filtering to organization queries."""
        if permission_checker.is_super_admin(user):
            return query  # Super admins see all organizations
        
        # Regular users see their own organization and its suppliers
        return query.filter(
            or_(
                models.Organization.id == user.organization_id,
                models.Organization.parent_organization_id == user.organization_id
            )
        )
    
    @staticmethod
    def filter_users(query, user: TokenData):
        """Apply organization-scoped filtering to user queries."""
        if permission_checker.is_super_admin(user):
            return query  # Super admins see all users
        
        # Regular users see users from their own organization
        return query.filter(models.User.organization_id == user.organization_id)
    
    @staticmethod
    def filter_warehouses(query, user: TokenData):
        """Apply organization-scoped filtering to warehouse queries."""
        if permission_checker.is_super_admin(user):
            return query  # Super admins see all warehouses
        
        # Regular users see warehouses from their own organization and suppliers
        return query.join(models.Organization).filter(
            or_(
                models.Organization.id == user.organization_id,
                models.Organization.parent_organization_id == user.organization_id
            )
        )
    
    @staticmethod
    def filter_inventory(query, user: TokenData):
        """Apply organization-scoped filtering to inventory queries."""
        if permission_checker.is_super_admin(user):
            return query  # Super admins see all inventory
        
        # Regular users see inventory from their accessible warehouses
        return query.join(models.Warehouse).join(models.Organization).filter(
            or_(
                models.Organization.id == user.organization_id,
                models.Organization.parent_organization_id == user.organization_id
            )
        )
    
    @staticmethod
    def filter_machines(query, user: TokenData):
        """Apply organization-scoped filtering to machine queries."""
        if permission_checker.is_super_admin(user):
            return query  # Super admins see all machines
        
        # Regular users see machines owned by their organization
        return query.filter(models.Machine.customer_organization_id == user.organization_id)
    
    @staticmethod
    def filter_transactions(query, user: TokenData):
        """Apply organization-scoped filtering to transaction queries."""
        if permission_checker.is_super_admin(user):
            return query  # Super admins see all transactions
        
        # Regular users see transactions involving their warehouses
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
        """Log permission granted events for sensitive operations."""
        if resource in [ResourceType.USER, ResourceType.ORGANIZATION] and permission in [PermissionType.WRITE, PermissionType.DELETE]:
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
            
            logger.info(f"Sensitive permission granted: {log_data}")

# Global audit logger instance
audit_logger = AuditLogger()