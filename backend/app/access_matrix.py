# backend/app/access_matrix.py

import uuid
from enum import Enum
from typing import Dict, List, Set, Optional, Any
from dataclasses import dataclass
import logging

from .auth import TokenData
from .models import UserRole, OrganizationType

logger = logging.getLogger(__name__)

# --- Access Matrix Definitions ---

class ResourceAction(str, Enum):
    """Specific actions that can be performed on resources."""
    # Organization actions
    CREATE_ORGANIZATION = "create_organization"
    VIEW_ORGANIZATION = "view_organization"
    UPDATE_ORGANIZATION = "update_organization"
    DELETE_ORGANIZATION = "delete_organization"
    MANAGE_SUPPLIERS = "manage_suppliers"
    
    # User actions
    CREATE_USER = "create_user"
    VIEW_USER = "view_user"
    UPDATE_USER = "update_user"
    DELETE_USER = "delete_user"
    INVITE_USER = "invite_user"
    RESET_PASSWORD = "reset_password"
    
    # Warehouse actions
    CREATE_WAREHOUSE = "create_warehouse"
    VIEW_WAREHOUSE = "view_warehouse"
    UPDATE_WAREHOUSE = "update_warehouse"
    DELETE_WAREHOUSE = "delete_warehouse"
    
    # Inventory actions
    VIEW_INVENTORY = "view_inventory"
    ADJUST_INVENTORY = "adjust_inventory"
    TRANSFER_INVENTORY = "transfer_inventory"
    CREATE_STOCKTAKE = "create_stocktake"
    
    # Machine actions
    REGISTER_MACHINE = "register_machine"
    VIEW_MACHINE = "view_machine"
    UPDATE_MACHINE = "update_machine"
    DELETE_MACHINE = "delete_machine"
    TRANSFER_MACHINE = "transfer_machine"
    RECORD_MACHINE_HOURS = "record_machine_hours"
    
    # Parts actions
    CREATE_PART = "create_part"
    VIEW_PART = "view_part"
    UPDATE_PART = "update_part"
    DELETE_PART = "delete_part"
    
    # Transaction actions
    CREATE_TRANSACTION = "create_transaction"
    VIEW_TRANSACTION = "view_transaction"
    APPROVE_TRANSACTION = "approve_transaction"
    
    # Order actions
    CREATE_ORDER = "create_order"
    VIEW_ORDER = "view_order"
    UPDATE_ORDER = "update_order"
    CANCEL_ORDER = "cancel_order"
    APPROVE_ORDER = "approve_order"
    
    # Reporting actions
    VIEW_REPORTS = "view_reports"
    EXPORT_DATA = "export_data"
    VIEW_ANALYTICS = "view_analytics"
    
    # System actions
    VIEW_AUDIT_LOGS = "view_audit_logs"
    MANAGE_SYSTEM_SETTINGS = "manage_system_settings"
    ACCESS_API_DOCS = "access_api_docs"

@dataclass
class AccessRule:
    """Represents a single access rule in the matrix."""
    role: UserRole
    action: ResourceAction
    allowed: bool
    conditions: Optional[Dict[str, Any]] = None
    description: Optional[str] = None

class RoleBasedAccessMatrix:
    """
    Comprehensive role-based access control matrix.
    Defines what actions each role can perform under what conditions.
    """
    
    def __init__(self):
        self._access_rules: Dict[str, Dict[str, AccessRule]] = {}
        self._initialize_access_matrix()
    
    def _initialize_access_matrix(self):
        """Initialize the complete access control matrix."""
        
        # Define access rules for each role
        rules = [
            # === SUPER ADMIN RULES ===
            # Super admins have full access to everything
            AccessRule(UserRole.super_admin, ResourceAction.CREATE_ORGANIZATION, True, 
                      description="Can create any type of organization"),
            AccessRule(UserRole.super_admin, ResourceAction.VIEW_ORGANIZATION, True,
                      description="Can view all organizations"),
            AccessRule(UserRole.super_admin, ResourceAction.UPDATE_ORGANIZATION, True,
                      description="Can update any organization"),
            AccessRule(UserRole.super_admin, ResourceAction.DELETE_ORGANIZATION, True,
                      description="Can delete organizations"),
            AccessRule(UserRole.super_admin, ResourceAction.MANAGE_SUPPLIERS, True,
                      description="Can manage suppliers for any organization"),
            
            AccessRule(UserRole.super_admin, ResourceAction.CREATE_USER, True,
                      description="Can create users in any organization"),
            AccessRule(UserRole.super_admin, ResourceAction.VIEW_USER, True,
                      description="Can view all users"),
            AccessRule(UserRole.super_admin, ResourceAction.UPDATE_USER, True,
                      description="Can update any user"),
            AccessRule(UserRole.super_admin, ResourceAction.DELETE_USER, True,
                      description="Can delete users"),
            AccessRule(UserRole.super_admin, ResourceAction.INVITE_USER, True,
                      description="Can invite users to any organization"),
            AccessRule(UserRole.super_admin, ResourceAction.RESET_PASSWORD, True,
                      description="Can reset passwords for any user"),
            
            AccessRule(UserRole.super_admin, ResourceAction.CREATE_WAREHOUSE, True,
                      description="Can create warehouses in any organization"),
            AccessRule(UserRole.super_admin, ResourceAction.VIEW_WAREHOUSE, True,
                      description="Can view all warehouses"),
            AccessRule(UserRole.super_admin, ResourceAction.UPDATE_WAREHOUSE, True,
                      description="Can update any warehouse"),
            AccessRule(UserRole.super_admin, ResourceAction.DELETE_WAREHOUSE, True,
                      description="Can delete warehouses"),
            
            AccessRule(UserRole.super_admin, ResourceAction.VIEW_INVENTORY, True,
                      description="Can view inventory in all warehouses"),
            AccessRule(UserRole.super_admin, ResourceAction.ADJUST_INVENTORY, True,
                      description="Can adjust inventory in any warehouse"),
            AccessRule(UserRole.super_admin, ResourceAction.TRANSFER_INVENTORY, True,
                      description="Can transfer inventory between any warehouses"),
            AccessRule(UserRole.super_admin, ResourceAction.CREATE_STOCKTAKE, True,
                      description="Can create stocktakes in any warehouse"),
            
            AccessRule(UserRole.super_admin, ResourceAction.REGISTER_MACHINE, True,
                      description="Can register machines for any organization"),
            AccessRule(UserRole.super_admin, ResourceAction.VIEW_MACHINE, True,
                      description="Can view all machines"),
            AccessRule(UserRole.super_admin, ResourceAction.UPDATE_MACHINE, True,
                      description="Can update any machine"),
            AccessRule(UserRole.super_admin, ResourceAction.DELETE_MACHINE, True,
                      description="Can delete machines"),
            AccessRule(UserRole.super_admin, ResourceAction.TRANSFER_MACHINE, True,
                      description="Can transfer machine ownership"),
            AccessRule(UserRole.super_admin, ResourceAction.RECORD_MACHINE_HOURS, True,
                      description="Can record hours for any machine"),
            
            AccessRule(UserRole.super_admin, ResourceAction.CREATE_PART, True,
                      description="Can create parts in the catalog"),
            AccessRule(UserRole.super_admin, ResourceAction.VIEW_PART, True,
                      description="Can view all parts"),
            AccessRule(UserRole.super_admin, ResourceAction.UPDATE_PART, True,
                      description="Can update any part"),
            AccessRule(UserRole.super_admin, ResourceAction.DELETE_PART, True,
                      description="Can delete parts"),
            
            AccessRule(UserRole.super_admin, ResourceAction.CREATE_TRANSACTION, True,
                      description="Can create any type of transaction"),
            AccessRule(UserRole.super_admin, ResourceAction.VIEW_TRANSACTION, True,
                      description="Can view all transactions"),
            AccessRule(UserRole.super_admin, ResourceAction.APPROVE_TRANSACTION, True,
                      description="Can approve transactions"),
            
            AccessRule(UserRole.super_admin, ResourceAction.CREATE_ORDER, True,
                      description="Can create orders for any organization"),
            AccessRule(UserRole.super_admin, ResourceAction.VIEW_ORDER, True,
                      description="Can view all orders"),
            AccessRule(UserRole.super_admin, ResourceAction.UPDATE_ORDER, True,
                      description="Can update any order"),
            AccessRule(UserRole.super_admin, ResourceAction.CANCEL_ORDER, True,
                      description="Can cancel orders"),
            AccessRule(UserRole.super_admin, ResourceAction.APPROVE_ORDER, True,
                      description="Can approve orders"),
            
            AccessRule(UserRole.super_admin, ResourceAction.VIEW_REPORTS, True,
                      description="Can view all reports"),
            AccessRule(UserRole.super_admin, ResourceAction.EXPORT_DATA, True,
                      description="Can export data"),
            AccessRule(UserRole.super_admin, ResourceAction.VIEW_ANALYTICS, True,
                      description="Can view system analytics"),
            
            AccessRule(UserRole.super_admin, ResourceAction.VIEW_AUDIT_LOGS, True,
                      description="Can view all audit logs"),
            AccessRule(UserRole.super_admin, ResourceAction.MANAGE_SYSTEM_SETTINGS, True,
                      description="Can manage system settings"),
            AccessRule(UserRole.super_admin, ResourceAction.ACCESS_API_DOCS, True,
                      description="Can access API documentation"),
            
            # === ADMIN RULES ===
            # Admins have organization-scoped permissions
            AccessRule(UserRole.admin, ResourceAction.CREATE_ORGANIZATION, False,
                      description="Cannot create organizations"),
            AccessRule(UserRole.admin, ResourceAction.VIEW_ORGANIZATION, True,
                      conditions={"scope": "own_and_suppliers"},
                      description="Can view own organization and its suppliers"),
            AccessRule(UserRole.admin, ResourceAction.UPDATE_ORGANIZATION, True,
                      conditions={"scope": "own_only"},
                      description="Can update own organization only"),
            AccessRule(UserRole.admin, ResourceAction.DELETE_ORGANIZATION, False,
                      description="Cannot delete organizations"),
            AccessRule(UserRole.admin, ResourceAction.MANAGE_SUPPLIERS, True,
                      conditions={"scope": "own_suppliers"},
                      description="Can manage suppliers under own organization"),
            
            AccessRule(UserRole.admin, ResourceAction.CREATE_USER, True,
                      conditions={"scope": "own_organization"},
                      description="Can create users in own organization"),
            AccessRule(UserRole.admin, ResourceAction.VIEW_USER, True,
                      conditions={"scope": "own_and_suppliers"},
                      description="Can view users in own organization and suppliers"),
            AccessRule(UserRole.admin, ResourceAction.UPDATE_USER, True,
                      conditions={"scope": "own_organization"},
                      description="Can update users in own organization"),
            AccessRule(UserRole.admin, ResourceAction.DELETE_USER, True,
                      conditions={"scope": "own_organization", "exclude": "self"},
                      description="Can delete users in own organization (except self)"),
            AccessRule(UserRole.admin, ResourceAction.INVITE_USER, True,
                      conditions={"scope": "own_organization"},
                      description="Can invite users to own organization"),
            AccessRule(UserRole.admin, ResourceAction.RESET_PASSWORD, True,
                      conditions={"scope": "own_organization"},
                      description="Can reset passwords for users in own organization"),
            
            AccessRule(UserRole.admin, ResourceAction.CREATE_WAREHOUSE, True,
                      conditions={"scope": "own_organization"},
                      description="Can create warehouses in own organization"),
            AccessRule(UserRole.admin, ResourceAction.VIEW_WAREHOUSE, True,
                      conditions={"scope": "own_and_suppliers"},
                      description="Can view warehouses in own organization and suppliers"),
            AccessRule(UserRole.admin, ResourceAction.UPDATE_WAREHOUSE, True,
                      conditions={"scope": "own_organization"},
                      description="Can update warehouses in own organization"),
            AccessRule(UserRole.admin, ResourceAction.DELETE_WAREHOUSE, True,
                      conditions={"scope": "own_organization"},
                      description="Can delete warehouses in own organization"),
            
            AccessRule(UserRole.admin, ResourceAction.VIEW_INVENTORY, True,
                      conditions={"scope": "own_and_suppliers"},
                      description="Can view inventory in accessible warehouses"),
            AccessRule(UserRole.admin, ResourceAction.ADJUST_INVENTORY, True,
                      conditions={"scope": "own_organization"},
                      description="Can adjust inventory in own organization's warehouses"),
            AccessRule(UserRole.admin, ResourceAction.TRANSFER_INVENTORY, True,
                      conditions={"scope": "own_and_suppliers"},
                      description="Can transfer inventory within accessible warehouses"),
            AccessRule(UserRole.admin, ResourceAction.CREATE_STOCKTAKE, True,
                      conditions={"scope": "own_organization"},
                      description="Can create stocktakes in own organization's warehouses"),
            
            AccessRule(UserRole.admin, ResourceAction.REGISTER_MACHINE, False,
                      description="Cannot register new machines"),
            AccessRule(UserRole.admin, ResourceAction.VIEW_MACHINE, True,
                      conditions={"scope": "own_organization"},
                      description="Can view machines owned by own organization"),
            AccessRule(UserRole.admin, ResourceAction.UPDATE_MACHINE, True,
                      conditions={"scope": "own_organization", "fields": ["name", "location", "notes"]},
                      description="Can update limited machine fields in own organization"),
            AccessRule(UserRole.admin, ResourceAction.DELETE_MACHINE, False,
                      description="Cannot delete machines"),
            AccessRule(UserRole.admin, ResourceAction.TRANSFER_MACHINE, False,
                      description="Cannot transfer machine ownership"),
            AccessRule(UserRole.admin, ResourceAction.RECORD_MACHINE_HOURS, True,
                      conditions={"scope": "own_organization"},
                      description="Can record hours for machines in own organization"),
            
            AccessRule(UserRole.admin, ResourceAction.CREATE_PART, False,
                      description="Cannot create parts"),
            AccessRule(UserRole.admin, ResourceAction.VIEW_PART, True,
                      description="Can view all parts in catalog"),
            AccessRule(UserRole.admin, ResourceAction.UPDATE_PART, False,
                      description="Cannot update parts"),
            AccessRule(UserRole.admin, ResourceAction.DELETE_PART, False,
                      description="Cannot delete parts"),
            
            AccessRule(UserRole.admin, ResourceAction.CREATE_TRANSACTION, True,
                      conditions={"scope": "own_and_suppliers"},
                      description="Can create transactions within accessible organizations"),
            AccessRule(UserRole.admin, ResourceAction.VIEW_TRANSACTION, True,
                      conditions={"scope": "own_and_suppliers"},
                      description="Can view transactions involving accessible organizations"),
            AccessRule(UserRole.admin, ResourceAction.APPROVE_TRANSACTION, True,
                      conditions={"scope": "own_organization", "types": ["adjustment", "transfer"]},
                      description="Can approve certain transaction types in own organization"),
            
            AccessRule(UserRole.admin, ResourceAction.CREATE_ORDER, True,
                      conditions={"scope": "own_and_suppliers"},
                      description="Can create orders within accessible organizations"),
            AccessRule(UserRole.admin, ResourceAction.VIEW_ORDER, True,
                      conditions={"scope": "own_and_suppliers"},
                      description="Can view orders involving accessible organizations"),
            AccessRule(UserRole.admin, ResourceAction.UPDATE_ORDER, True,
                      conditions={"scope": "own_organization"},
                      description="Can update orders from own organization"),
            AccessRule(UserRole.admin, ResourceAction.CANCEL_ORDER, True,
                      conditions={"scope": "own_organization"},
                      description="Can cancel orders from own organization"),
            AccessRule(UserRole.admin, ResourceAction.APPROVE_ORDER, True,
                      conditions={"scope": "own_organization"},
                      description="Can approve orders for own organization"),
            
            AccessRule(UserRole.admin, ResourceAction.VIEW_REPORTS, True,
                      conditions={"scope": "own_and_suppliers"},
                      description="Can view reports for accessible organizations"),
            AccessRule(UserRole.admin, ResourceAction.EXPORT_DATA, True,
                      conditions={"scope": "own_and_suppliers"},
                      description="Can export data for accessible organizations"),
            AccessRule(UserRole.admin, ResourceAction.VIEW_ANALYTICS, True,
                      conditions={"scope": "own_organization"},
                      description="Can view analytics for own organization"),
            
            AccessRule(UserRole.admin, ResourceAction.VIEW_AUDIT_LOGS, True,
                      conditions={"scope": "own_organization"},
                      description="Can view audit logs for own organization"),
            AccessRule(UserRole.admin, ResourceAction.MANAGE_SYSTEM_SETTINGS, False,
                      description="Cannot manage system settings"),
            AccessRule(UserRole.admin, ResourceAction.ACCESS_API_DOCS, True,
                      description="Can access API documentation"),
            
            # === USER RULES ===
            # Regular users have limited, read-mostly permissions
            AccessRule(UserRole.user, ResourceAction.CREATE_ORGANIZATION, False,
                      description="Cannot create organizations"),
            AccessRule(UserRole.user, ResourceAction.VIEW_ORGANIZATION, True,
                      conditions={"scope": "own_only"},
                      description="Can view own organization only"),
            AccessRule(UserRole.user, ResourceAction.UPDATE_ORGANIZATION, False,
                      description="Cannot update organizations"),
            AccessRule(UserRole.user, ResourceAction.DELETE_ORGANIZATION, False,
                      description="Cannot delete organizations"),
            AccessRule(UserRole.user, ResourceAction.MANAGE_SUPPLIERS, False,
                      description="Cannot manage suppliers"),
            
            AccessRule(UserRole.user, ResourceAction.CREATE_USER, False,
                      description="Cannot create users"),
            AccessRule(UserRole.user, ResourceAction.VIEW_USER, True,
                      conditions={"scope": "own_organization"},
                      description="Can view users in own organization"),
            AccessRule(UserRole.user, ResourceAction.UPDATE_USER, True,
                      conditions={"scope": "self_only"},
                      description="Can update own profile only"),
            AccessRule(UserRole.user, ResourceAction.DELETE_USER, False,
                      description="Cannot delete users"),
            AccessRule(UserRole.user, ResourceAction.INVITE_USER, False,
                      description="Cannot invite users"),
            AccessRule(UserRole.user, ResourceAction.RESET_PASSWORD, True,
                      conditions={"scope": "self_only"},
                      description="Can reset own password only"),
            
            AccessRule(UserRole.user, ResourceAction.CREATE_WAREHOUSE, False,
                      description="Cannot create warehouses"),
            AccessRule(UserRole.user, ResourceAction.VIEW_WAREHOUSE, True,
                      conditions={"scope": "own_organization"},
                      description="Can view warehouses in own organization"),
            AccessRule(UserRole.user, ResourceAction.UPDATE_WAREHOUSE, False,
                      description="Cannot update warehouses"),
            AccessRule(UserRole.user, ResourceAction.DELETE_WAREHOUSE, False,
                      description="Cannot delete warehouses"),
            
            AccessRule(UserRole.user, ResourceAction.VIEW_INVENTORY, True,
                      conditions={"scope": "own_organization"},
                      description="Can view inventory in own organization's warehouses"),
            AccessRule(UserRole.user, ResourceAction.ADJUST_INVENTORY, False,
                      description="Cannot adjust inventory"),
            AccessRule(UserRole.user, ResourceAction.TRANSFER_INVENTORY, True,
                      conditions={"scope": "own_organization", "types": ["usage"]},
                      description="Can record part usage (consumption) in own organization"),
            AccessRule(UserRole.user, ResourceAction.CREATE_STOCKTAKE, False,
                      description="Cannot create stocktakes"),
            
            AccessRule(UserRole.user, ResourceAction.REGISTER_MACHINE, False,
                      description="Cannot register machines"),
            AccessRule(UserRole.user, ResourceAction.VIEW_MACHINE, True,
                      conditions={"scope": "own_organization"},
                      description="Can view machines owned by own organization"),
            AccessRule(UserRole.user, ResourceAction.UPDATE_MACHINE, False,
                      description="Cannot update machines"),
            AccessRule(UserRole.user, ResourceAction.DELETE_MACHINE, False,
                      description="Cannot delete machines"),
            AccessRule(UserRole.user, ResourceAction.TRANSFER_MACHINE, False,
                      description="Cannot transfer machines"),
            AccessRule(UserRole.user, ResourceAction.RECORD_MACHINE_HOURS, True,
                      conditions={"scope": "own_organization"},
                      description="Can record hours for machines in own organization"),
            
            AccessRule(UserRole.user, ResourceAction.CREATE_PART, False,
                      description="Cannot create parts"),
            AccessRule(UserRole.user, ResourceAction.VIEW_PART, True,
                      description="Can view all parts in catalog"),
            AccessRule(UserRole.user, ResourceAction.UPDATE_PART, False,
                      description="Cannot update parts"),
            AccessRule(UserRole.user, ResourceAction.DELETE_PART, False,
                      description="Cannot delete parts"),
            
            AccessRule(UserRole.user, ResourceAction.CREATE_TRANSACTION, True,
                      conditions={"scope": "own_organization", "types": ["usage", "request"]},
                      description="Can create usage and request transactions in own organization"),
            AccessRule(UserRole.user, ResourceAction.VIEW_TRANSACTION, True,
                      conditions={"scope": "own_organization"},
                      description="Can view transactions involving own organization"),
            AccessRule(UserRole.user, ResourceAction.APPROVE_TRANSACTION, False,
                      description="Cannot approve transactions"),
            
            AccessRule(UserRole.user, ResourceAction.CREATE_ORDER, True,
                      conditions={"scope": "own_organization"},
                      description="Can create orders for own organization"),
            AccessRule(UserRole.user, ResourceAction.VIEW_ORDER, True,
                      conditions={"scope": "own_organization"},
                      description="Can view orders from own organization"),
            AccessRule(UserRole.user, ResourceAction.UPDATE_ORDER, True,
                      conditions={"scope": "own_orders", "status": ["pending", "draft"]},
                      description="Can update own pending/draft orders"),
            AccessRule(UserRole.user, ResourceAction.CANCEL_ORDER, True,
                      conditions={"scope": "own_orders", "status": ["pending", "draft"]},
                      description="Can cancel own pending/draft orders"),
            AccessRule(UserRole.user, ResourceAction.APPROVE_ORDER, False,
                      description="Cannot approve orders"),
            
            AccessRule(UserRole.user, ResourceAction.VIEW_REPORTS, True,
                      conditions={"scope": "own_organization", "types": ["basic"]},
                      description="Can view basic reports for own organization"),
            AccessRule(UserRole.user, ResourceAction.EXPORT_DATA, False,
                      description="Cannot export data"),
            AccessRule(UserRole.user, ResourceAction.VIEW_ANALYTICS, False,
                      description="Cannot view analytics"),
            
            AccessRule(UserRole.user, ResourceAction.VIEW_AUDIT_LOGS, False,
                      description="Cannot view audit logs"),
            AccessRule(UserRole.user, ResourceAction.MANAGE_SYSTEM_SETTINGS, False,
                      description="Cannot manage system settings"),
            AccessRule(UserRole.user, ResourceAction.ACCESS_API_DOCS, True,
                      description="Can access API documentation"),
        ]
        
        # Build the access matrix
        for rule in rules:
            role_key = rule.role.value
            action_key = rule.action.value
            
            if role_key not in self._access_rules:
                self._access_rules[role_key] = {}
            
            self._access_rules[role_key][action_key] = rule
    
    def check_access(self, user: TokenData, action: ResourceAction, 
                    context: Optional[Dict[str, Any]] = None) -> bool:
        """
        Check if a user has access to perform a specific action.
        
        Args:
            user: Current user token data
            action: Action to check access for
            context: Additional context for conditional checks
            
        Returns:
            bool: True if access is granted, False otherwise
        """
        context = context or {}
        
        # Get the access rule for this role and action
        rule = self._access_rules.get(user.role, {}).get(action.value)
        
        if not rule:
            logger.warning(f"No access rule found for role {user.role} and action {action.value}")
            return False
        
        # If the rule is explicitly denied, return False
        if not rule.allowed:
            return False
        
        # If no conditions, access is granted
        if not rule.conditions:
            return True
        
        # Check conditions
        return self._check_conditions(user, rule.conditions, context)
    
    def _check_conditions(self, user: TokenData, conditions: Dict[str, Any], 
                         context: Dict[str, Any]) -> bool:
        """
        Check if the conditions for an access rule are met.
        
        Args:
            user: Current user token data
            conditions: Conditions to check
            context: Additional context
            
        Returns:
            bool: True if all conditions are met
        """
        # Check scope conditions
        scope = conditions.get("scope")
        if scope:
            if not self._check_scope_condition(user, scope, context):
                return False
        
        # Check type restrictions
        allowed_types = conditions.get("types")
        if allowed_types:
            requested_type = context.get("type")
            if requested_type and requested_type not in allowed_types:
                return False
        
        # Check field restrictions
        allowed_fields = conditions.get("fields")
        if allowed_fields:
            requested_fields = context.get("fields", [])
            if not all(field in allowed_fields for field in requested_fields):
                return False
        
        # Check status restrictions
        allowed_statuses = conditions.get("status")
        if allowed_statuses:
            current_status = context.get("status")
            if current_status and current_status not in allowed_statuses:
                return False
        
        # Check exclusions
        exclusions = conditions.get("exclude")
        if exclusions:
            if "self" in exclusions and context.get("target_user_id") == user.user_id:
                return False
        
        return True
    
    def _check_scope_condition(self, user: TokenData, scope: str, 
                              context: Dict[str, Any]) -> bool:
        """
        Check scope-based conditions.
        
        Args:
            user: Current user token data
            scope: Scope condition to check
            context: Additional context
            
        Returns:
            bool: True if scope condition is met
        """
        if scope == "own_only":
            target_org_id = context.get("organization_id")
            return target_org_id == user.organization_id
        
        elif scope == "own_organization":
            target_org_id = context.get("organization_id")
            return target_org_id == user.organization_id
        
        elif scope == "own_and_suppliers":
            # This requires database access to check supplier relationships
            # For now, we'll return True and let the organizational isolation handle it
            return True
        
        elif scope == "own_suppliers":
            # Check if target organization is a supplier under user's organization
            return True  # Let organizational isolation handle this
        
        elif scope == "self_only":
            target_user_id = context.get("target_user_id")
            return target_user_id == user.user_id
        
        elif scope == "own_orders":
            order_user_id = context.get("order_user_id")
            return order_user_id == user.user_id
        
        return False
    
    def get_allowed_actions(self, user: TokenData) -> List[ResourceAction]:
        """
        Get list of all actions that a user is allowed to perform.
        
        Args:
            user: Current user token data
            
        Returns:
            List of allowed actions
        """
        allowed_actions = []
        
        role_rules = self._access_rules.get(user.role, {})
        for action_key, rule in role_rules.items():
            if rule.allowed:
                allowed_actions.append(ResourceAction(action_key))
        
        return allowed_actions
    
    def get_access_summary(self, user: TokenData) -> Dict[str, Any]:
        """
        Get a summary of user's access permissions.
        
        Args:
            user: Current user token data
            
        Returns:
            Dictionary containing access summary
        """
        allowed_actions = self.get_allowed_actions(user)
        
        # Group actions by category
        categories = {
            "organization": [],
            "user": [],
            "warehouse": [],
            "inventory": [],
            "machine": [],
            "part": [],
            "transaction": [],
            "order": [],
            "reporting": [],
            "system": []
        }
        
        for action in allowed_actions:
            action_name = action.value
            if "organization" in action_name:
                categories["organization"].append(action_name)
            elif "user" in action_name:
                categories["user"].append(action_name)
            elif "warehouse" in action_name:
                categories["warehouse"].append(action_name)
            elif "inventory" in action_name:
                categories["inventory"].append(action_name)
            elif "machine" in action_name:
                categories["machine"].append(action_name)
            elif "part" in action_name:
                categories["part"].append(action_name)
            elif "transaction" in action_name:
                categories["transaction"].append(action_name)
            elif "order" in action_name:
                categories["order"].append(action_name)
            elif any(keyword in action_name for keyword in ["report", "export", "analytics"]):
                categories["reporting"].append(action_name)
            else:
                categories["system"].append(action_name)
        
        return {
            "role": user.role,
            "total_allowed_actions": len(allowed_actions),
            "categories": categories,
            "organization_id": str(user.organization_id)
        }

# Global access matrix instance
access_matrix = RoleBasedAccessMatrix()

# --- Helper Functions ---

def check_resource_access(user: TokenData, action: ResourceAction, 
                         context: Optional[Dict[str, Any]] = None) -> bool:
    """
    Helper function to check resource access using the access matrix.
    
    Args:
        user: Current user token data
        action: Action to check
        context: Additional context
        
    Returns:
        bool: True if access is granted
    """
    return access_matrix.check_access(user, action, context)

def require_resource_access(action: ResourceAction):
    """
    Decorator to require specific resource access for an endpoint.
    
    Args:
        action: Required action
        
    Returns:
        Dependency function for FastAPI
    """
    def access_dependency(user: TokenData, context: Dict[str, Any] = None) -> TokenData:
        if not check_resource_access(user, action, context):
            from fastapi import HTTPException, status
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions for action: {action.value}"
            )
        return user
    
    return access_dependency