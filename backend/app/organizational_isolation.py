# backend/app/organizational_isolation.py

import uuid
import logging
from typing import Dict, Any, Optional, List, Set
from datetime import datetime, timedelta
from functools import wraps

from fastapi import Request, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, text

from .auth import TokenData
from .models import Organization, OrganizationType, UserRole
from .database import get_db

logger = logging.getLogger(__name__)

class OrganizationalDataIsolation:
    """
    Core class for enforcing organizational data isolation.
    Ensures users can only access data from their own organization and authorized suppliers.
    """
    
    def __init__(self):
        self._isolation_cache: Dict[str, Dict[str, Any]] = {}
        self._cache_ttl = timedelta(minutes=10)  # Cache isolation rules for 10 minutes
    
    def _get_cache_key(self, user_id: uuid.UUID, resource_type: str) -> str:
        """Generate cache key for isolation rules."""
        return f"isolation:{user_id}:{resource_type}"
    
    def _is_cache_valid(self, cache_entry: Dict[str, Any]) -> bool:
        """Check if cache entry is still valid."""
        if not cache_entry:
            return False
        cached_at = cache_entry.get("cached_at")
        if not cached_at:
            return False
        return datetime.utcnow() - cached_at < self._cache_ttl
    
    def _cache_isolation_rules(self, cache_key: str, accessible_orgs: List[uuid.UUID]):
        """Cache isolation rules for a user."""
        self._isolation_cache[cache_key] = {
            "accessible_organizations": [str(org_id) for org_id in accessible_orgs],
            "cached_at": datetime.utcnow()
        }
    
    def get_accessible_organization_ids(self, user: TokenData, db: Session) -> List[uuid.UUID]:
        """
        Get list of organization IDs that the user can access.
        
        Business Rules:
        - Super admins can access all organizations
        - Admins and users can access their own organization
        - Admins and users can access supplier organizations under their organization
        - BossAqua data is only accessible to super admins initially
        """
        # Check cache first
        cache_key = self._get_cache_key(user.user_id, "organizations")
        cached_result = self._isolation_cache.get(cache_key)
        
        if cached_result and self._is_cache_valid(cached_result):
            logger.debug(f"Isolation cache hit for {cache_key}")
            return [uuid.UUID(org_id) for org_id in cached_result["accessible_organizations"]]
        
        accessible_orgs = []
        
        try:
            if user.role == "super_admin":
                # Super admins can access all organizations
                orgs = db.query(Organization.id).all()
                accessible_orgs = [org.id for org in orgs]
            else:
                # Regular users and admins can access their own organization
                accessible_orgs.append(user.organization_id)
                
                # Get supplier organizations under their organization
                suppliers = db.query(Organization.id).filter(
                    and_(
                        Organization.parent_organization_id == user.organization_id,
                        Organization.organization_type == OrganizationType.supplier,
                        Organization.is_active == True
                    )
                ).all()
                
                accessible_orgs.extend([supplier.id for supplier in suppliers])
                
                # Exclude BossAqua data for non-super admins
                bossaqua_org = db.query(Organization.id).filter(
                    Organization.organization_type == OrganizationType.bossaqua
                ).first()
                
                if bossaqua_org and bossaqua_org.id in accessible_orgs:
                    accessible_orgs.remove(bossaqua_org.id)
            
            # Cache the result
            self._cache_isolation_rules(cache_key, accessible_orgs)
            
            return accessible_orgs
            
        except Exception as e:
            logger.error(f"Error getting accessible organizations for user {user.user_id}: {e}")
            # Fallback to just user's own organization
            return [user.organization_id]
    
    def validate_organization_access(self, user: TokenData, organization_id: uuid.UUID, db: Session) -> bool:
        """
        Validate if user can access data from a specific organization.
        
        Args:
            user: Current user token data
            organization_id: Organization ID to check access for
            db: Database session
            
        Returns:
            bool: True if access is allowed, False otherwise
        """
        accessible_orgs = self.get_accessible_organization_ids(user, db)
        return organization_id in accessible_orgs
    
    def validate_cross_organizational_access(self, user: TokenData, source_org_id: uuid.UUID, 
                                           target_org_id: uuid.UUID, db: Session) -> bool:
        """
        Validate cross-organizational access for operations like transfers.
        
        Args:
            user: Current user token data
            source_org_id: Source organization ID
            target_org_id: Target organization ID
            db: Database session
            
        Returns:
            bool: True if cross-organizational access is allowed
        """
        # Super admins can perform any cross-organizational operations
        if user.role == "super_admin":
            return True
        
        # Get accessible organizations
        accessible_orgs = self.get_accessible_organization_ids(user, db)
        
        # Both organizations must be accessible
        if source_org_id not in accessible_orgs or target_org_id not in accessible_orgs:
            return False
        
        # Additional business rule validation
        try:
            source_org = db.query(Organization).filter(Organization.id == source_org_id).first()
            target_org = db.query(Organization).filter(Organization.id == target_org_id).first()
            
            if not source_org or not target_org:
                return False
            
            # Validate specific cross-organizational business rules
            # Example: Transfers from Oraseas EE to customers are allowed
            if (source_org.organization_type == OrganizationType.oraseas_ee and 
                target_org.organization_type == OrganizationType.customer):
                return True
            
            # Transfers within the same organizational hierarchy are allowed
            if (source_org.parent_organization_id == target_org.parent_organization_id or
                source_org.id == target_org.parent_organization_id or
                target_org.id == source_org.parent_organization_id):
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error validating cross-organizational access: {e}")
            return False
    
    def apply_organization_filter(self, query, user: TokenData, db: Session, 
                                organization_column=None):
        """
        Apply organizational filtering to a SQLAlchemy query.
        
        Args:
            query: SQLAlchemy query object
            user: Current user token data
            db: Database session
            organization_column: Column to filter on (defaults to organization_id)
            
        Returns:
            Filtered query object
        """
        if user.role == "super_admin":
            return query  # Super admins see everything
        
        accessible_orgs = self.get_accessible_organization_ids(user, db)
        
        if organization_column is None:
            # Try to detect the organization column automatically
            if hasattr(query.column_descriptions[0]['type'], 'organization_id'):
                organization_column = query.column_descriptions[0]['type'].organization_id
            else:
                logger.warning("Could not auto-detect organization column for filtering")
                return query
        
        return query.filter(organization_column.in_(accessible_orgs))
    
    def validate_supplier_visibility(self, user: TokenData, supplier_id: uuid.UUID, db: Session) -> bool:
        """
        Validate if user can see a specific supplier.
        Suppliers are only visible to their parent organization and super admins.
        
        Args:
            user: Current user token data
            supplier_id: Supplier organization ID
            db: Database session
            
        Returns:
            bool: True if supplier is visible to user
        """
        if user.role == "super_admin":
            return True
        
        try:
            supplier = db.query(Organization).filter(
                and_(
                    Organization.id == supplier_id,
                    Organization.organization_type == OrganizationType.supplier
                )
            ).first()
            
            if not supplier:
                return False
            
            # Supplier is visible if it belongs to user's organization
            return supplier.parent_organization_id == user.organization_id
            
        except Exception as e:
            logger.error(f"Error validating supplier visibility: {e}")
            return False
    
    def get_organization_hierarchy(self, user: TokenData, db: Session) -> Dict[str, Any]:
        """
        Get the organizational hierarchy that the user can access.
        
        Returns:
            Dictionary containing the organizational hierarchy
        """
        try:
            accessible_orgs = self.get_accessible_organization_ids(user, db)
            
            # Get organization details
            orgs = db.query(Organization).filter(Organization.id.in_(accessible_orgs)).all()
            
            # Build hierarchy structure
            hierarchy = {
                "user_organization": None,
                "suppliers": [],
                "customers": [],
                "total_accessible": len(orgs)
            }
            
            for org in orgs:
                org_data = {
                    "id": str(org.id),
                    "name": org.name,
                    "type": org.organization_type.value,
                    "country": org.country,
                    "is_active": org.is_active
                }
                
                if org.id == user.organization_id:
                    hierarchy["user_organization"] = org_data
                elif org.organization_type == OrganizationType.supplier:
                    hierarchy["suppliers"].append(org_data)
                elif org.organization_type == OrganizationType.customer:
                    hierarchy["customers"].append(org_data)
            
            return hierarchy
            
        except Exception as e:
            logger.error(f"Error building organization hierarchy: {e}")
            return {"error": "Could not build organization hierarchy"}
    
    def clear_cache(self, user_id: uuid.UUID = None):
        """Clear isolation cache for a specific user or all users."""
        if user_id:
            # Clear cache for specific user
            keys_to_remove = [key for key in self._isolation_cache.keys() if f":{user_id}:" in key]
            for key in keys_to_remove:
                del self._isolation_cache[key]
        else:
            # Clear all cache
            self._isolation_cache.clear()

# Global organizational isolation instance
organizational_isolation = OrganizationalDataIsolation()

# --- Decorator for automatic organizational isolation ---

def enforce_organizational_isolation(organization_param: str = "organization_id"):
    """
    Decorator to automatically enforce organizational isolation on endpoint functions.
    
    Args:
        organization_param: Name of the parameter containing organization ID
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract user and db from kwargs
            current_user = kwargs.get('current_user')
            db = kwargs.get('db')
            
            if not current_user or not db:
                logger.warning("Could not find current_user or db in function kwargs for isolation check")
                return await func(*args, **kwargs)
            
            # Check if organization_id is provided
            org_id = kwargs.get(organization_param)
            if org_id:
                if not organizational_isolation.validate_organization_access(current_user, org_id, db):
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail=f"Access denied to organization {org_id}"
                    )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator

# --- Query Helper Functions ---

def get_organization_scoped_query(base_query, user: TokenData, db: Session, 
                                organization_column=None):
    """
    Helper function to apply organizational scoping to any query.
    
    Args:
        base_query: Base SQLAlchemy query
        user: Current user token data
        db: Database session
        organization_column: Column to filter on
        
    Returns:
        Organizationally scoped query
    """
    return organizational_isolation.apply_organization_filter(
        base_query, user, db, organization_column
    )

def validate_organizational_boundary(user: TokenData, resource_org_id: uuid.UUID, 
                                   db: Session, operation: str = "access") -> bool:
    """
    Validate that an operation respects organizational boundaries.
    
    Args:
        user: Current user token data
        resource_org_id: Organization ID of the resource being accessed
        db: Database session
        operation: Type of operation being performed
        
    Returns:
        bool: True if operation is allowed within organizational boundaries
    """
    is_valid = organizational_isolation.validate_organization_access(user, resource_org_id, db)
    
    if not is_valid:
        logger.warning(
            f"Organizational boundary violation: User {user.user_id} "
            f"attempted {operation} on organization {resource_org_id}"
        )
    
    return is_valid

# --- Business Rule Validation Functions ---

def validate_supplier_parent_relationship(supplier_org_id: uuid.UUID, parent_org_id: uuid.UUID, 
                                        db: Session) -> bool:
    """
    Validate that a supplier organization has the correct parent relationship.
    
    Args:
        supplier_org_id: Supplier organization ID
        parent_org_id: Expected parent organization ID
        db: Database session
        
    Returns:
        bool: True if relationship is valid
    """
    try:
        supplier = db.query(Organization).filter(
            and_(
                Organization.id == supplier_org_id,
                Organization.organization_type == OrganizationType.supplier
            )
        ).first()
        
        if not supplier:
            return False
        
        return supplier.parent_organization_id == parent_org_id
        
    except Exception as e:
        logger.error(f"Error validating supplier parent relationship: {e}")
        return False

def get_bossaqua_access_restriction(user: TokenData) -> bool:
    """
    Check if user has access to BossAqua data.
    Initially, only super admins can access BossAqua data.
    
    Args:
        user: Current user token data
        
    Returns:
        bool: True if user can access BossAqua data
    """
    return user.role == "super_admin"

# --- Enhanced Organizational Data Isolation Middleware ---

class OrganizationalDataIsolationMiddleware:
    """
    Enhanced middleware for automatic organizational data isolation.
    Ensures all database queries are automatically scoped to user's accessible organizations.
    """
    
    def __init__(self):
        self.isolation_engine = organizational_isolation
        
        # Define endpoints that require enhanced organizational validation
        self.organizational_endpoints = {
            "/organizations": {"requires_org_validation": True, "resource_type": "organization"},
            "/users": {"requires_org_validation": True, "resource_type": "user"},
            "/warehouses": {"requires_org_validation": True, "resource_type": "warehouse"},
            "/inventory": {"requires_org_validation": True, "resource_type": "inventory"},
            "/machines": {"requires_org_validation": True, "resource_type": "machine"},
            "/transactions": {"requires_org_validation": True, "resource_type": "transaction"},
            "/supplier_orders": {"requires_org_validation": True, "resource_type": "order"},
            "/customer_orders": {"requires_org_validation": True, "resource_type": "order"},
            "/part_usage": {"requires_org_validation": True, "resource_type": "part_usage"},
            "/stock_adjustments": {"requires_org_validation": True, "resource_type": "stock_adjustment"}
        }
        
        # Define cross-organizational operations that need special validation
        self.cross_org_operations = {
            "transfer", "move", "assign", "allocate", "distribute"
        }
    
    def requires_organizational_validation(self, path: str) -> bool:
        """Check if endpoint requires organizational validation."""
        for endpoint_prefix in self.organizational_endpoints:
            if path.startswith(endpoint_prefix):
                return True
        return False
    
    def extract_organization_context(self, request: Request, path: str, method: str) -> Dict[str, Any]:
        """
        Extract organizational context from request.
        
        Args:
            request: FastAPI request object
            path: Request path
            method: HTTP method
            
        Returns:
            Dictionary containing organizational context
        """
        context = {
            "path": path,
            "method": method,
            "organization_ids": [],
            "requires_cross_org_validation": False
        }
        
        try:
            # Extract organization IDs from path parameters
            if hasattr(request, "path_params"):
                for param_name, param_value in request.path_params.items():
                    if "organization" in param_name.lower() and param_value:
                        try:
                            org_id = uuid.UUID(param_value)
                            context["organization_ids"].append(org_id)
                        except ValueError:
                            logger.warning(f"Invalid organization UUID in path: {param_value}")
            
            # Extract organization IDs from query parameters
            if request.url.query:
                from urllib.parse import parse_qs
                query_params = parse_qs(request.url.query)
                for param_name, param_values in query_params.items():
                    if "organization" in param_name.lower() and param_values:
                        for param_value in param_values:
                            try:
                                org_id = uuid.UUID(param_value)
                                context["organization_ids"].append(org_id)
                            except ValueError:
                                logger.warning(f"Invalid organization UUID in query: {param_value}")
            
            # Check for cross-organizational operations
            path_lower = path.lower()
            for operation in self.cross_org_operations:
                if operation in path_lower:
                    context["requires_cross_org_validation"] = True
                    break
            
            # Extract additional context from request body for POST/PUT operations
            if method in ["POST", "PUT", "PATCH"]:
                # This would require reading the request body, which is complex in middleware
                # We'll handle this in the endpoint-specific validation
                pass
            
            return context
            
        except Exception as e:
            logger.error(f"Error extracting organizational context: {e}")
            return context
    
    def validate_organizational_access(self, user: TokenData, context: Dict[str, Any], 
                                     db: Session) -> Dict[str, Any]:
        """
        Validate organizational access based on context.
        
        Args:
            user: Current user token data
            context: Organizational context
            db: Database session
            
        Returns:
            Dictionary with validation result
        """
        try:
            # Super admins bypass all organizational restrictions
            if user.role == "super_admin":
                return {"allowed": True, "reason": "super_admin_access"}
            
            # Get user's accessible organizations
            accessible_orgs = self.isolation_engine.get_accessible_organization_ids(user, db)
            
            # Validate access to all organization IDs in context
            for org_id in context.get("organization_ids", []):
                if org_id not in accessible_orgs:
                    return {
                        "allowed": False,
                        "reason": f"Access denied to organization {org_id}",
                        "context": {"denied_organization": str(org_id)}
                    }
            
            # Special validation for cross-organizational operations
            if context.get("requires_cross_org_validation", False):
                if len(context.get("organization_ids", [])) > 1:
                    # Multiple organizations involved - validate cross-org access
                    org_ids = context["organization_ids"]
                    for i in range(len(org_ids)):
                        for j in range(i + 1, len(org_ids)):
                            if not self.isolation_engine.validate_cross_organizational_access(
                                user, org_ids[i], org_ids[j], db
                            ):
                                return {
                                    "allowed": False,
                                    "reason": f"Cross-organizational access denied between {org_ids[i]} and {org_ids[j]}",
                                    "context": {
                                        "source_org": str(org_ids[i]),
                                        "target_org": str(org_ids[j])
                                    }
                                }
            
            return {"allowed": True, "reason": "organizational_access_validated"}
            
        except Exception as e:
            logger.error(f"Error validating organizational access: {e}")
            return {
                "allowed": False,
                "reason": "validation_error",
                "context": {"error": str(e)}
            }
    
    def apply_automatic_filtering(self, user: TokenData, db: Session, 
                                resource_type: str) -> Dict[str, Any]:
        """
        Apply automatic organizational filtering for database queries.
        
        Args:
            user: Current user token data
            db: Database session
            resource_type: Type of resource being accessed
            
        Returns:
            Dictionary with filtering information
        """
        try:
            accessible_orgs = self.isolation_engine.get_accessible_organization_ids(user, db)
            
            return {
                "accessible_organizations": accessible_orgs,
                "filter_applied": True,
                "resource_type": resource_type,
                "user_role": user.role
            }
            
        except Exception as e:
            logger.error(f"Error applying automatic filtering: {e}")
            return {
                "accessible_organizations": [user.organization_id],
                "filter_applied": False,
                "error": str(e)
            }

# Global middleware instance
organizational_data_isolation_middleware = OrganizationalDataIsolationMiddleware()

# --- Enhanced Query Helpers ---

class EnhancedOrganizationScopedQueries:
    """
    Enhanced query helpers with automatic organizational filtering and validation.
    """
    
    @staticmethod
    def apply_organization_filter(query, user: TokenData, db: Session, 
                                organization_column=None, resource_type: str = "unknown"):
        """
        Apply enhanced organizational filtering to any SQLAlchemy query.
        
        Args:
            query: SQLAlchemy query object
            user: Current user token data
            db: Database session
            organization_column: Column to filter on
            resource_type: Type of resource for logging
            
        Returns:
            Filtered query with organizational isolation applied
        """
        try:
            # Super admins see everything
            if user.role == "super_admin":
                logger.debug(f"Super admin access granted for {resource_type}")
                return query
            
            # Get accessible organizations
            accessible_orgs = organizational_isolation.get_accessible_organization_ids(user, db)
            
            if not accessible_orgs:
                logger.warning(f"No accessible organizations found for user {user.user_id}")
                # Return empty result set
                return query.filter(text("1=0"))
            
            # Apply organizational filter
            if organization_column is not None:
                filtered_query = query.filter(organization_column.in_(accessible_orgs))
                logger.debug(f"Applied organization filter for {resource_type}: {len(accessible_orgs)} orgs")
                return filtered_query
            else:
                logger.warning(f"No organization column specified for {resource_type} filtering")
                return query
                
        except Exception as e:
            logger.error(f"Error applying organization filter for {resource_type}: {e}")
            # Fallback to user's own organization only
            if organization_column is not None:
                return query.filter(organization_column == user.organization_id)
            return query
    
    @staticmethod
    def validate_and_filter_organizations(query, user: TokenData, db: Session):
        """Enhanced organization filtering with business rule validation."""
        filtered_query = EnhancedOrganizationScopedQueries.apply_organization_filter(
            query, user, db, Organization.id, "organizations"
        )
        
        # Additional business rule: exclude BossAqua for non-super admins
        if user.role != "super_admin":
            filtered_query = filtered_query.filter(
                Organization.organization_type != OrganizationType.bossaqua
            )
        
        return filtered_query
    
    @staticmethod
    def validate_and_filter_users(query, user: TokenData, db: Session):
        """Enhanced user filtering with organizational validation."""
        from .models import User
        
        return EnhancedOrganizationScopedQueries.apply_organization_filter(
            query, user, db, User.organization_id, "users"
        )
    
    @staticmethod
    def validate_and_filter_warehouses(query, user: TokenData, db: Session):
        """Enhanced warehouse filtering with organizational validation."""
        from .models import Warehouse
        
        return EnhancedOrganizationScopedQueries.apply_organization_filter(
            query, user, db, Warehouse.organization_id, "warehouses"
        )
    
    @staticmethod
    def validate_and_filter_machines(query, user: TokenData, db: Session):
        """Enhanced machine filtering with organizational validation."""
        from .models import Machine
        
        return EnhancedOrganizationScopedQueries.apply_organization_filter(
            query, user, db, Machine.customer_organization_id, "machines"
        )
    
    @staticmethod
    def validate_and_filter_inventory(query, user: TokenData, db: Session):
        """Enhanced inventory filtering through warehouse organizational validation."""
        from .models import Inventory, Warehouse
        
        # Join with warehouse to get organization
        query_with_warehouse = query.join(Warehouse, Inventory.warehouse_id == Warehouse.id)
        
        return EnhancedOrganizationScopedQueries.apply_organization_filter(
            query_with_warehouse, user, db, Warehouse.organization_id, "inventory"
        )
    
    @staticmethod
    def validate_and_filter_transactions(query, user: TokenData, db: Session):
        """Enhanced transaction filtering with cross-organizational validation."""
        from .models import Transaction, Warehouse
        
        # Complex filtering for transactions involving multiple warehouses
        if user.role == "super_admin":
            return query
        
        accessible_orgs = organizational_isolation.get_accessible_organization_ids(user, db)
        
        # Filter transactions where either source or target warehouse belongs to accessible orgs
        return query.join(
            Warehouse, 
            or_(
                Transaction.from_warehouse_id == Warehouse.id,
                Transaction.to_warehouse_id == Warehouse.id
            )
        ).filter(Warehouse.organization_id.in_(accessible_orgs))
    
    @staticmethod
    def validate_supplier_access(query, user: TokenData, db: Session):
        """Validate and filter supplier access based on parent organization."""
        if user.role == "super_admin":
            return query
        
        # Suppliers are only visible to their parent organization
        return query.filter(
            and_(
                Organization.organization_type == OrganizationType.supplier,
                Organization.parent_organization_id == user.organization_id,
                Organization.is_active == True
            )
        )

# Global enhanced query helpers instance
enhanced_org_queries = EnhancedOrganizationScopedQueries()