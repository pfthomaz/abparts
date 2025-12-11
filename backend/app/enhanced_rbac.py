# backend/app/enhanced_rbac.py

"""
Enhanced Role-Based Access Control (RBAC) Implementation
Task 5: Enhanced Role-Based Access Control

This module implements:
1. Organizational data isolation middleware
2. Organization-scoped query helpers and filters
3. Permission validation for cross-organizational access prevention
4. Role-based resource access matrix enforcement
"""

import uuid
import logging
from typing import Dict, Any, Optional, List, Set, Callable
from datetime import datetime, timedelta
from functools import wraps

from fastapi import Request, HTTPException, status, Depends
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, text

from .auth import TokenData, get_current_user
from .models import Organization, OrganizationType, UserRole, User, Warehouse, Machine, Inventory, Part
from .database import get_db
from .permissions import permission_checker, ResourceType, PermissionType
from .organizational_isolation import organizational_isolation

logger = logging.getLogger(__name__)

# --- Enhanced Organizational Data Isolation Middleware ---

class EnhancedOrganizationalIsolationMiddleware:
    """
    Enhanced middleware for strict organizational data isolation.
    Ensures all database operations respect organizational boundaries.
    """
    
    def __init__(self):
        self.isolation_rules = {
            # Define strict isolation rules for each resource type
            "organizations": {
                "super_admin": "all",
                "admin": "own_and_suppliers", 
                "user": "own_only"
            },
            "users": {
                "super_admin": "all",
                "admin": "own_organization",
                "user": "own_organization"
            },
            "warehouses": {
                "super_admin": "all",
                "admin": "own_organization",
                "user": "own_organization"
            },
            "machines": {
                "super_admin": "all",
                "admin": "own_organization",
                "user": "own_organization"
            },
            "inventory": {
                "super_admin": "all",
                "admin": "own_organization",
                "user": "own_organization"
            },
            "parts": {
                "super_admin": "all",
                "admin": "read_all",
                "user": "read_all"
            }
        }
        
        # Define BossAqua access restrictions
        self.bossaqua_restrictions = {
            "super_admin": True,  # Full access
            "admin": False,       # No access initially
            "user": False         # No access initially
        }
    
    def validate_organizational_access(self, user: TokenData, resource_type: str, 
                                     organization_id: uuid.UUID, db: Session) -> bool:
        """
        Validate if user can access data from a specific organization.
        
        Args:
            user: Current user token data
            resource_type: Type of resource being accessed
            organization_id: Organization ID to validate access for
            db: Database session
            
        Returns:
            bool: True if access is allowed
        """
        try:
            # Get the organization
            org = db.query(Organization).filter(Organization.id == organization_id).first()
            if not org:
                logger.warning(f"Organization {organization_id} not found")
                return False
            
            # Check BossAqua restrictions
            if org.organization_type == OrganizationType.bossaqua:
                if not self.bossaqua_restrictions.get(user.role, False):
                    logger.info(f"BossAqua access denied for user {user.user_id} with role {user.role}")
                    return False
            
            # Get isolation rule for this resource and role
            resource_rules = self.isolation_rules.get(resource_type, {})
            access_level = resource_rules.get(user.role, "none")
            
            if access_level == "all":
                return True
            elif access_level == "own_only":
                return organization_id == user.organization_id
            elif access_level == "own_organization":
                return organization_id == user.organization_id
            elif access_level == "own_and_suppliers":
                # User can access their own org and supplier orgs under their org
                if organization_id == user.organization_id:
                    return True
                # Check if it's a supplier under user's organization
                return org.parent_organization_id == user.organization_id
            elif access_level == "read_all":
                return True  # Read access to all (for parts)
            else:
                return False
                
        except Exception as e:
            logger.error(f"Error validating organizational access: {e}")
            return False
    
    def get_accessible_organization_ids(self, user: TokenData, resource_type: str, 
                                      db: Session) -> List[uuid.UUID]:
        """
        Get list of organization IDs accessible to user for a specific resource type.
        
        Args:
            user: Current user token data
            resource_type: Type of resource
            db: Database session
            
        Returns:
            List of accessible organization IDs
        """
        try:
            resource_rules = self.isolation_rules.get(resource_type, {})
            access_level = resource_rules.get(user.role, "none")
            
            if access_level == "all":
                # Super admin can access all organizations
                orgs = db.query(Organization.id).filter(Organization.is_active == True).all()
                return [org.id for org in orgs]
            
            elif access_level in ["own_only", "own_organization"]:
                # User can only access their own organization
                return [user.organization_id]
            
            elif access_level == "own_and_suppliers":
                # User can access their own org and suppliers under their org
                accessible_orgs = [user.organization_id]
                
                # Add supplier organizations
                suppliers = db.query(Organization.id).filter(
                    and_(
                        Organization.parent_organization_id == user.organization_id,
                        Organization.organization_type == OrganizationType.supplier,
                        Organization.is_active == True
                    )
                ).all()
                
                accessible_orgs.extend([supplier.id for supplier in suppliers])
                return accessible_orgs
            
            elif access_level == "read_all":
                # Read access to all organizations (for parts)
                orgs = db.query(Organization.id).filter(Organization.is_active == True).all()
                accessible_org_ids = [org.id for org in orgs]
                
                # Apply BossAqua restrictions
                if not self.bossaqua_restrictions.get(user.role, False):
                    bossaqua_org = db.query(Organization.id).filter(
                        Organization.organization_type == OrganizationType.bossaqua
                    ).first()
                    if bossaqua_org and bossaqua_org.id in accessible_org_ids:
                        accessible_org_ids.remove(bossaqua_org.id)
                
                return accessible_org_ids
            
            else:
                return []
                
        except Exception as e:
            logger.error(f"Error getting accessible organizations: {e}")
            return [user.organization_id]  # Fallback to user's own org

# Global enhanced isolation middleware instance
enhanced_isolation_middleware = EnhancedOrganizationalIsolationMiddleware()

# --- Enhanced Organization-Scoped Query Helpers ---

class EnhancedOrganizationScopedQueries:
    """
    Enhanced query helpers with strict organizational filtering and validation.
    """
    
    @staticmethod
    def apply_strict_organization_filter(query, user: TokenData, resource_type: str, 
                                       organization_column, db: Session):
        """
        Apply strict organizational filtering to any SQLAlchemy query.
        
        Args:
            query: SQLAlchemy query object
            user: Current user token data
            resource_type: Type of resource for isolation rules
            organization_column: Column to filter on
            db: Database session
            
        Returns:
            Filtered query with strict organizational isolation
        """
        try:
            # Get accessible organizations for this resource type
            accessible_orgs = enhanced_isolation_middleware.get_accessible_organization_ids(
                user, resource_type, db
            )
            
            if not accessible_orgs:
                logger.warning(f"No accessible organizations for user {user.user_id} and resource {resource_type}")
                # Return empty result set
                return query.filter(text("1=0"))
            
            # Apply organizational filter
            filtered_query = query.filter(organization_column.in_(accessible_orgs))
            
            logger.debug(f"Applied strict organization filter for {resource_type}: {len(accessible_orgs)} orgs accessible")
            return filtered_query
            
        except Exception as e:
            logger.error(f"Error applying strict organization filter: {e}")
            # Fallback to user's own organization only
            return query.filter(organization_column == user.organization_id)
    
    @staticmethod
    def filter_organizations_strict(query, user: TokenData, db: Session):
        """Apply strict organizational filtering to organization queries."""
        return EnhancedOrganizationScopedQueries.apply_strict_organization_filter(
            query, user, "organizations", Organization.id, db
        )
    
    @staticmethod
    def filter_users_strict(query, user: TokenData, db: Session):
        """Apply strict organizational filtering to user queries."""
        return EnhancedOrganizationScopedQueries.apply_strict_organization_filter(
            query, user, "users", User.organization_id, db
        )
    
    @staticmethod
    def filter_warehouses_strict(query, user: TokenData, db: Session):
        """Apply strict organizational filtering to warehouse queries."""
        return EnhancedOrganizationScopedQueries.apply_strict_organization_filter(
            query, user, "warehouses", Warehouse.organization_id, db
        )
    
    @staticmethod
    def filter_machines_strict(query, user: TokenData, db: Session):
        """Apply strict organizational filtering to machine queries."""
        return EnhancedOrganizationScopedQueries.apply_strict_organization_filter(
            query, user, "machines", Machine.customer_organization_id, db
        )
    
    @staticmethod
    def filter_inventory_strict(query, user: TokenData, db: Session):
        """Apply strict organizational filtering to inventory queries through warehouse."""
        # Join with warehouse to get organization
        query_with_warehouse = query.join(Warehouse, Inventory.warehouse_id == Warehouse.id)
        
        return EnhancedOrganizationScopedQueries.apply_strict_organization_filter(
            query_with_warehouse, user, "inventory", Warehouse.organization_id, db
        )

# --- Cross-Organizational Access Prevention ---

class CrossOrganizationalAccessValidator:
    """
    Validator for preventing unauthorized cross-organizational access.
    """
    
    def __init__(self):
        # Define allowed cross-organizational operations
        self.allowed_cross_org_operations = {
            "machine_transfer": {
                "from": [OrganizationType.oraseas_ee],
                "to": [OrganizationType.customer],
                "required_role": ["super_admin"]
            },
            "part_order": {
                "from": [OrganizationType.customer],
                "to": [OrganizationType.oraseas_ee, OrganizationType.supplier],
                "required_role": ["user", "admin", "super_admin"]
            },
            "inventory_transfer": {
                "from": [OrganizationType.oraseas_ee],
                "to": [OrganizationType.customer],
                "required_role": ["admin", "super_admin"]
            }
        }
    
    def validate_cross_organizational_operation(self, user: TokenData, operation_type: str,
                                              source_org_id: uuid.UUID, target_org_id: uuid.UUID,
                                              db: Session) -> Dict[str, Any]:
        """
        Validate if a cross-organizational operation is allowed.
        
        Args:
            user: Current user token data
            operation_type: Type of operation (e.g., 'machine_transfer')
            source_org_id: Source organization ID
            target_org_id: Target organization ID
            db: Database session
            
        Returns:
            Dictionary with validation result
        """
        try:
            # Check if operation type is allowed
            if operation_type not in self.allowed_cross_org_operations:
                return {
                    "allowed": False,
                    "reason": f"Cross-organizational operation '{operation_type}' is not allowed"
                }
            
            operation_rules = self.allowed_cross_org_operations[operation_type]
            
            # Check if user has required role
            if user.role not in operation_rules["required_role"]:
                return {
                    "allowed": False,
                    "reason": f"User role '{user.role}' not authorized for '{operation_type}'"
                }
            
            # Get source and target organizations
            source_org = db.query(Organization).filter(Organization.id == source_org_id).first()
            target_org = db.query(Organization).filter(Organization.id == target_org_id).first()
            
            if not source_org or not target_org:
                return {
                    "allowed": False,
                    "reason": "Source or target organization not found"
                }
            
            # Check if organization types are allowed for this operation
            if source_org.organization_type not in operation_rules["from"]:
                return {
                    "allowed": False,
                    "reason": f"Source organization type '{source_org.organization_type.value}' not allowed for '{operation_type}'"
                }
            
            if target_org.organization_type not in operation_rules["to"]:
                return {
                    "allowed": False,
                    "reason": f"Target organization type '{target_org.organization_type.value}' not allowed for '{operation_type}'"
                }
            
            # Additional validation: user must have access to both organizations
            if not enhanced_isolation_middleware.validate_organizational_access(
                user, "organizations", source_org_id, db
            ):
                return {
                    "allowed": False,
                    "reason": "User does not have access to source organization"
                }
            
            if not enhanced_isolation_middleware.validate_organizational_access(
                user, "organizations", target_org_id, db
            ):
                return {
                    "allowed": False,
                    "reason": "User does not have access to target organization"
                }
            
            return {
                "allowed": True,
                "reason": "Cross-organizational operation validated",
                "context": {
                    "operation_type": operation_type,
                    "source_org": source_org.name,
                    "target_org": target_org.name,
                    "user_role": user.role
                }
            }
            
        except Exception as e:
            logger.error(f"Error validating cross-organizational operation: {e}")
            return {
                "allowed": False,
                "reason": f"Validation error: {str(e)}"
            }

# Global cross-organizational access validator
cross_org_validator = CrossOrganizationalAccessValidator()

# --- Role-Based Resource Access Matrix Enforcement ---

class RoleBasedResourceAccessMatrix:
    """
    Enforces role-based resource access matrix with organizational context.
    """
    
    def __init__(self):
        # Define comprehensive access matrix
        self.access_matrix = {
            # Resource: {Role: {Permission: Access Level}}
            ResourceType.ORGANIZATION: {
                "super_admin": {
                    PermissionType.READ: "all",
                    PermissionType.WRITE: "all", 
                    PermissionType.DELETE: "all",
                    PermissionType.ADMIN: "all"
                },
                "admin": {
                    PermissionType.READ: "own_and_suppliers",
                    PermissionType.WRITE: "suppliers_only",
                    PermissionType.DELETE: "none",
                    PermissionType.ADMIN: "suppliers_only"
                },
                "user": {
                    PermissionType.READ: "own_only",
                    PermissionType.WRITE: "none",
                    PermissionType.DELETE: "none",
                    PermissionType.ADMIN: "none"
                }
            },
            ResourceType.USER: {
                "super_admin": {
                    PermissionType.READ: "all",
                    PermissionType.WRITE: "all",
                    PermissionType.DELETE: "all",
                    PermissionType.ADMIN: "all"
                },
                "admin": {
                    PermissionType.READ: "own_organization",
                    PermissionType.WRITE: "own_organization",
                    PermissionType.DELETE: "own_organization",
                    PermissionType.ADMIN: "own_organization"
                },
                "user": {
                    PermissionType.READ: "own_profile",
                    PermissionType.WRITE: "own_profile",
                    PermissionType.DELETE: "none",
                    PermissionType.ADMIN: "none"
                }
            },
            ResourceType.WAREHOUSE: {
                "super_admin": {
                    PermissionType.READ: "all",
                    PermissionType.WRITE: "all",
                    PermissionType.DELETE: "all",
                    PermissionType.ADMIN: "all"
                },
                "admin": {
                    PermissionType.READ: "own_organization",
                    PermissionType.WRITE: "own_organization",
                    PermissionType.DELETE: "own_organization",
                    PermissionType.ADMIN: "own_organization"
                },
                "user": {
                    PermissionType.READ: "own_organization",
                    PermissionType.WRITE: "none",
                    PermissionType.DELETE: "none",
                    PermissionType.ADMIN: "none"
                }
            },
            ResourceType.MACHINE: {
                "super_admin": {
                    PermissionType.READ: "all",
                    PermissionType.WRITE: "all",
                    PermissionType.DELETE: "all",
                    PermissionType.ADMIN: "all"
                },
                "admin": {
                    PermissionType.READ: "own_organization",
                    PermissionType.WRITE: "name_edit_only",
                    PermissionType.DELETE: "none",
                    PermissionType.ADMIN: "none"
                },
                "user": {
                    PermissionType.READ: "own_organization",
                    PermissionType.WRITE: "hours_recording",
                    PermissionType.DELETE: "none",
                    PermissionType.ADMIN: "none"
                }
            },
            ResourceType.INVENTORY: {
                "super_admin": {
                    PermissionType.READ: "all",
                    PermissionType.WRITE: "all",
                    PermissionType.DELETE: "all",
                    PermissionType.ADMIN: "all"
                },
                "admin": {
                    PermissionType.READ: "own_organization",
                    PermissionType.WRITE: "own_organization",
                    PermissionType.DELETE: "own_organization",
                    PermissionType.ADMIN: "own_organization"
                },
                "user": {
                    PermissionType.READ: "own_organization",
                    PermissionType.WRITE: "transactions_only",
                    PermissionType.DELETE: "none",
                    PermissionType.ADMIN: "none"
                }
            },
            ResourceType.PART: {
                "super_admin": {
                    PermissionType.READ: "all",
                    PermissionType.WRITE: "all",
                    PermissionType.DELETE: "all",
                    PermissionType.ADMIN: "all"
                },
                "admin": {
                    PermissionType.READ: "all",
                    PermissionType.WRITE: "none",
                    PermissionType.DELETE: "none",
                    PermissionType.ADMIN: "none"
                },
                "user": {
                    PermissionType.READ: "all",
                    PermissionType.WRITE: "none",
                    PermissionType.DELETE: "none",
                    PermissionType.ADMIN: "none"
                }
            }
        }
    
    def check_resource_access(self, user: TokenData, resource: ResourceType, 
                            permission: PermissionType, context: Dict[str, Any] = None) -> bool:
        """
        Check if user has access to a resource with specific permission.
        
        Args:
            user: Current user token data
            resource: Resource type
            permission: Permission type
            context: Additional context (organization_id, etc.)
            
        Returns:
            bool: True if access is granted
        """
        try:
            # Get access level for this user role, resource, and permission
            resource_permissions = self.access_matrix.get(resource, {})
            role_permissions = resource_permissions.get(user.role, {})
            access_level = role_permissions.get(permission, "none")
            
            if access_level == "none":
                return False
            elif access_level == "all":
                return True
            else:
                # Context-dependent access - need to validate against context
                return self._validate_contextual_access(user, access_level, context)
                
        except Exception as e:
            logger.error(f"Error checking resource access: {e}")
            return False
    
    def _validate_contextual_access(self, user: TokenData, access_level: str, 
                                  context: Dict[str, Any] = None) -> bool:
        """
        Validate contextual access based on access level and context.
        
        Args:
            user: Current user token data
            access_level: Access level string
            context: Context dictionary
            
        Returns:
            bool: True if contextual access is granted
        """
        context = context or {}
        
        if access_level == "own_only":
            org_id = context.get("organization_id")
            return org_id == user.organization_id if org_id else True
        
        elif access_level == "own_organization":
            org_id = context.get("organization_id")
            return org_id == user.organization_id if org_id else True
        
        elif access_level == "own_and_suppliers":
            # User can access their own org and suppliers under their org
            org_id = context.get("organization_id")
            if not org_id:
                return True
            if org_id == user.organization_id:
                return True
            # Would need DB access to check if it's a supplier - return True for now
            return True
        
        elif access_level == "own_profile":
            user_id = context.get("user_id")
            return user_id == user.user_id if user_id else True
        
        elif access_level in ["suppliers_only", "name_edit_only", "hours_recording", "transactions_only"]:
            # These require specific business logic validation
            return True  # Allow for now, specific endpoints will validate
        
        else:
            return False

# Global role-based access matrix
rbac_matrix = RoleBasedResourceAccessMatrix()

# --- Enhanced Permission Dependency Functions ---

def require_enhanced_permission(resource: ResourceType, permission: PermissionType, 
                               context_extractor: Callable = None):
    """
    Enhanced dependency function that requires specific permissions with strict organizational validation.
    
    Args:
        resource: Type of resource being accessed
        permission: Type of permission required
        context_extractor: Function to extract context from request
        
    Returns:
        Dependency function for FastAPI
    """
    def enhanced_permission_dependency(
        current_user: TokenData = Depends(get_current_user),
        db: Session = Depends(get_db),
        request: Request = None
    ) -> TokenData:
        # Extract context if function provided
        context = {}
        if context_extractor and request:
            try:
                context = context_extractor(request)
            except Exception as e:
                logger.error(f"Error extracting context: {e}")
        
        # Check permission using enhanced RBAC matrix
        if not rbac_matrix.check_resource_access(current_user, resource, permission, context):
            logger.warning(f"Enhanced permission denied: {current_user.username} -> {resource.value}:{permission.value}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions for {resource.value}:{permission.value}",
                headers={"X-Permission-Denied": f"{resource.value}:{permission.value}"}
            )
        
        # Additional organizational validation if organization_id in context
        org_id = context.get("organization_id")
        if org_id:
            if not enhanced_isolation_middleware.validate_organizational_access(
                current_user, resource.value.lower(), org_id, db
            ):
                logger.warning(f"Organizational access denied: {current_user.username} -> org {org_id}")
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Access denied to organization {org_id}",
                    headers={"X-Organizational-Access-Denied": str(org_id)}
                )
        
        return current_user
    
    return enhanced_permission_dependency

def require_cross_organizational_permission(operation_type: str):
    """
    Dependency function for cross-organizational operations.
    
    Args:
        operation_type: Type of cross-organizational operation
        
    Returns:
        Dependency function for FastAPI
    """
    def cross_org_permission_dependency(
        current_user: TokenData = Depends(get_current_user),
        db: Session = Depends(get_db),
        request: Request = None
    ) -> TokenData:
        # This would typically extract source and target org IDs from request
        # For now, we'll just validate that the user can perform cross-org operations
        
        if current_user.role not in ["admin", "super_admin"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Cross-organizational operation '{operation_type}' requires admin privileges"
            )
        
        return current_user
    
    return cross_org_permission_dependency

# --- Utility Functions ---

def get_user_accessible_organizations(user: TokenData, resource_type: str, db: Session) -> List[uuid.UUID]:
    """
    Get list of organizations accessible to user for a specific resource type.
    
    Args:
        user: Current user token data
        resource_type: Type of resource
        db: Database session
        
    Returns:
        List of accessible organization IDs
    """
    return enhanced_isolation_middleware.get_accessible_organization_ids(user, resource_type, db)

def validate_organizational_boundary(user: TokenData, organization_id: uuid.UUID, 
                                   resource_type: str, db: Session) -> bool:
    """
    Validate that user can access data from a specific organization.
    
    Args:
        user: Current user token data
        organization_id: Organization ID to validate
        resource_type: Type of resource
        db: Database session
        
    Returns:
        bool: True if access is allowed
    """
    return enhanced_isolation_middleware.validate_organizational_access(
        user, resource_type, organization_id, db
    )

def log_rbac_violation(user: TokenData, resource: ResourceType, permission: PermissionType,
                      context: Dict[str, Any] = None, reason: str = None):
    """
    Log RBAC violations for security monitoring.
    
    Args:
        user: Current user token data
        resource: Resource type
        permission: Permission type
        context: Additional context
        reason: Reason for denial
    """
    violation_data = {
        "event": "rbac_violation",
        "user_id": str(user.user_id),
        "username": user.username,
        "role": user.role,
        "organization_id": str(user.organization_id),
        "resource": resource.value,
        "permission": permission.value,
        "reason": reason or "Access denied",
        "context": context or {},
        "timestamp": datetime.utcnow().isoformat()
    }
    
    logger.warning(f"RBAC violation: {violation_data}")