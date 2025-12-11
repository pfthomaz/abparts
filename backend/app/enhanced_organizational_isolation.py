# backend/app/enhanced_organizational_isolation.py

import uuid
import logging
from typing import Dict, Any, Optional, List, Set, Tuple, Union
from datetime import datetime
from functools import wraps

from fastapi import Request, HTTPException, status, Depends
from sqlalchemy.orm import Session, Query
from sqlalchemy import and_, or_, text
from sqlalchemy.exc import SQLAlchemyError

from .database import get_db
from .models import User, Organization, Part, Machine, Warehouse, Inventory, Transaction, OrganizationType, UserRole
from .enhanced_audit_system import EnhancedAuditSystem, AuditContext

# Configure logging for security events
security_logger = logging.getLogger("security")
audit_logger = logging.getLogger("audit")

class OrganizationalIsolationError(Exception):
    """Custom exception for organizational isolation violations"""
    pass

class EnhancedOrganizationalDataFilter:
    """Enhanced organizational data isolation enforcement with comprehensive validation"""
    
    @staticmethod
    def validate_organization_access(current_user: User, target_organization_id: uuid.UUID, 
                                   db: Session, audit_context: Optional[AuditContext] = None) -> Dict[str, Any]:
        """
        Validate if user can access data from target organization with detailed reasoning
        
        Returns:
            Dict with 'allowed' (bool), 'reason' (str), and 'context' (dict)
        """
        user_role = current_user.role.value if hasattr(current_user.role, 'value') else str(current_user.role)
        
        # Superadmin has access to all organizations
        if user_role == "super_admin":
            if audit_context:
                audit_context.log_access(
                    "ORGANIZATION_ACCESS", target_organization_id, "VALIDATE_ACCESS",
                    details={"access_granted": True, "reason": "superadmin_privilege"}
                )
            return {
                "allowed": True,
                "reason": "Superadmin has access to all organizations",
                "context": {"user_role": user_role}
            }
        
        # Users can access their own organization
        if current_user.organization_id == target_organization_id:
            if audit_context:
                audit_context.log_access(
                    "ORGANIZATION_ACCESS", target_organization_id, "VALIDATE_ACCESS",
                    details={"access_granted": True, "reason": "own_organization"}
                )
            return {
                "allowed": True,
                "reason": "User belongs to target organization",
                "context": {"user_role": user_role, "own_organization": True}
            }
        
        # Check if target is a supplier of user's organization (for admins)
        if user_role == "admin":
            target_org = db.query(Organization).filter(Organization.id == target_organization_id).first()
            if (target_org and 
                target_org.organization_type == OrganizationType.supplier and
                target_org.parent_organization_id == current_user.organization_id):
                
                if audit_context:
                    audit_context.log_access(
                        "ORGANIZATION_ACCESS", target_organization_id, "VALIDATE_ACCESS",
                        details={"access_granted": True, "reason": "supplier_relationship"}
                    )
                return {
                    "allowed": True,
                    "reason": "Admin can access suppliers of their organization",
                    "context": {"user_role": user_role, "supplier_relationship": True}
                }
        
        # Access denied - log security event
        if audit_context:
            audit_context.log_security_event(
                "ORGANIZATIONAL_ACCESS_DENIED",
                "MEDIUM",
                f"User attempted to access organization {target_organization_id}",
                details={
                    "target_organization_id": str(target_organization_id),
                    "user_organization_id": str(current_user.organization_id),
                    "user_role": user_role
                }
            )
        
        # Log isolation violation
        EnhancedAuditSystem.log_organizational_isolation_violation(
            user_id=current_user.id,
            user_organization_id=current_user.organization_id,
            attempted_organization_id=target_organization_id,
            resource_type="ORGANIZATION",
            action="ACCESS_VALIDATION",
            db=db
        )
        
        return {
            "allowed": False,
            "reason": "User does not have access to target organization",
            "context": {"user_role": user_role, "violation_logged": True}
        }
    
    @staticmethod
    def get_accessible_organization_ids(current_user: User, db: Session, 
                                      audit_context: Optional[AuditContext] = None) -> List[uuid.UUID]:
        """Get comprehensive list of organization IDs the user can access"""
        user_role = current_user.role.value if hasattr(current_user.role, 'value') else str(current_user.role)
        
        if user_role == "super_admin":
            # Superadmin can access all organizations
            orgs = db.query(Organization.id).filter(Organization.is_active == True).all()
            org_ids = [org.id for org in orgs]
            
            if audit_context:
                audit_context.log_access(
                    "ORGANIZATION_LIST", current_user.id, "GET_ACCESSIBLE_ORGS",
                    details={"accessible_count": len(org_ids), "reason": "superadmin_privilege"}
                )
            
            return org_ids
        
        accessible_ids = [current_user.organization_id]
        
        # Add supplier organizations if user is admin
        if user_role == "admin":
            suppliers = db.query(Organization.id).filter(
                Organization.parent_organization_id == current_user.organization_id,
                Organization.organization_type == OrganizationType.supplier,
                Organization.is_active == True
            ).all()
            supplier_ids = [supplier.id for supplier in suppliers]
            accessible_ids.extend(supplier_ids)
            
            if audit_context:
                audit_context.log_access(
                    "ORGANIZATION_LIST", current_user.id, "GET_ACCESSIBLE_ORGS",
                    details={
                        "accessible_count": len(accessible_ids),
                        "supplier_count": len(supplier_ids),
                        "reason": "admin_with_suppliers"
                    }
                )
        else:
            if audit_context:
                audit_context.log_access(
                    "ORGANIZATION_LIST", current_user.id, "GET_ACCESSIBLE_ORGS",
                    details={"accessible_count": len(accessible_ids), "reason": "own_organization_only"}
                )
        
        return accessible_ids
    
    @staticmethod
    def filter_query_by_organization(query: Query, model_class, current_user: User, 
                                   db: Session, audit_context: Optional[AuditContext] = None) -> Query:
        """Apply comprehensive organizational filtering to SQLAlchemy queries"""
        accessible_org_ids = EnhancedOrganizationalDataFilter.get_accessible_organization_ids(
            current_user, db, audit_context
        )
        
        # Apply organization filter based on model type
        if hasattr(model_class, 'organization_id'):
            filtered_query = query.filter(model_class.organization_id.in_(accessible_org_ids))
        elif hasattr(model_class, 'customer_organization_id'):
            filtered_query = query.filter(model_class.customer_organization_id.in_(accessible_org_ids))
        else:
            # If no organization field, return original query but log warning
            security_logger.warning(f"No organization field found for model {model_class.__name__}")
            filtered_query = query
        
        if audit_context:
            audit_context.log_access(
                "QUERY_FILTER", current_user.id, "APPLY_ORG_FILTER",
                details={
                    "model_class": model_class.__name__,
                    "accessible_org_count": len(accessible_org_ids),
                    "filter_applied": hasattr(model_class, 'organization_id') or hasattr(model_class, 'customer_organization_id')
                }
            )
        
        return filtered_query
    
    @staticmethod
    def validate_resource_access(current_user: User, resource_organization_id: uuid.UUID,
                               resource_type: str, resource_id: uuid.UUID,
                               action: str, db: Session,
                               audit_context: Optional[AuditContext] = None) -> bool:
        """Validate access to a specific resource with comprehensive logging"""
        
        validation_result = EnhancedOrganizationalDataFilter.validate_organization_access(
            current_user, resource_organization_id, db, audit_context
        )
        
        if not validation_result["allowed"]:
            # Log the access denial
            EnhancedAuditSystem.log_organizational_isolation_violation(
                user_id=current_user.id,
                user_organization_id=current_user.organization_id,
                attempted_organization_id=resource_organization_id,
                resource_type=resource_type,
                action=action,
                db=db
            )
            
            if audit_context:
                audit_context.log_security_event(
                    "RESOURCE_ACCESS_DENIED",
                    "HIGH",
                    f"Access denied to {resource_type}:{resource_id}",
                    details={
                        "resource_type": resource_type,
                        "resource_id": str(resource_id),
                        "resource_organization_id": str(resource_organization_id),
                        "action": action,
                        "denial_reason": validation_result["reason"]
                    }
                )
            
            return False
        
        # Log successful access
        if audit_context:
            audit_context.log_access(
                resource_type, resource_id, action,
                details={
                    "resource_organization_id": str(resource_organization_id),
                    "access_reason": validation_result["reason"]
                }
            )
        
        return True

class EnhancedBossAquaAccessControl:
    """Enhanced access control for BossAqua organization data with comprehensive auditing"""
    
    @staticmethod
    def validate_bossaqua_access(current_user: User, action: str, 
                               audit_context: Optional[AuditContext] = None,
                               db: Optional[Session] = None) -> bool:
        """Validate access to BossAqua organization data with detailed logging"""
        user_role = current_user.role.value if hasattr(current_user.role, 'value') else str(current_user.role)
        
        # Only superadmin can interact with BossAqua data initially
        if user_role != "super_admin":
            # Log security violation
            EnhancedAuditSystem.log_bossaqua_access_violation(
                user_id=current_user.id,
                user_organization_id=current_user.organization_id,
                user_role=user_role,
                action=action,
                db=db
            )
            
            if audit_context:
                audit_context.log_security_event(
                    "BOSSAQUA_ACCESS_DENIED",
                    "HIGH",
                    f"Non-superadmin attempted BossAqua access: {action}",
                    details={
                        "user_role": user_role,
                        "action": action,
                        "violation_type": "BOSSAQUA_ACCESS_DENIED"
                    }
                )
            
            security_logger.warning(
                f"Non-superadmin user {current_user.id} (role: {user_role}) "
                f"attempted BossAqua access: {action}"
            )
            return False
        
        # Log successful BossAqua access for superadmin
        if audit_context:
            audit_context.log_access(
                "BOSSAQUA_DATA", current_user.id, action,
                details={
                    "user_role": user_role,
                    "access_granted": True,
                    "reason": "superadmin_privilege"
                }
            )
        
        return True
    
    @staticmethod
    def is_bossaqua_organization(organization_id: uuid.UUID, db: Session) -> bool:
        """Check if organization is BossAqua"""
        org = db.query(Organization).filter(Organization.id == organization_id).first()
        return org and org.organization_type == OrganizationType.bossaqua
    
    @staticmethod
    def is_bossaqua_resource(resource_type: str, resource_id: uuid.UUID, db: Session) -> bool:
        """Check if a resource belongs to BossAqua organization"""
        if resource_type.lower() == "organization":
            return EnhancedBossAquaAccessControl.is_bossaqua_organization(resource_id, db)
        
        # Check other resource types
        if resource_type.lower() == "part":
            part = db.query(Part).filter(Part.id == resource_id).first()
            return part and part.is_proprietary  # Assuming proprietary parts are BossAqua
        
        if resource_type.lower() == "machine":
            machine = db.query(Machine).filter(Machine.id == resource_id).first()
            if machine:
                return EnhancedBossAquaAccessControl.is_bossaqua_organization(
                    machine.customer_organization_id, db
                )
        
        # Add more resource type checks as needed
        return False

class EnhancedSupplierVisibilityControl:
    """Enhanced supplier visibility control with comprehensive auditing"""
    
    @staticmethod
    def get_visible_suppliers(current_user: User, db: Session,
                            audit_context: Optional[AuditContext] = None) -> List[Organization]:
        """Get suppliers visible to the current user with audit logging"""
        user_role = current_user.role.value if hasattr(current_user.role, 'value') else str(current_user.role)
        
        if user_role == "super_admin":
            # Superadmin sees all suppliers
            suppliers = db.query(Organization).filter(
                Organization.organization_type == OrganizationType.supplier,
                Organization.is_active == True
            ).all()
            
            if audit_context:
                audit_context.log_access(
                    "SUPPLIER_LIST", current_user.id, "GET_VISIBLE_SUPPLIERS",
                    details={
                        "visible_count": len(suppliers),
                        "reason": "superadmin_privilege",
                        "scope": "all_suppliers"
                    }
                )
            
            return suppliers
        
        # Regular users only see suppliers belonging to their organization
        suppliers = db.query(Organization).filter(
            Organization.organization_type == OrganizationType.supplier,
            Organization.parent_organization_id == current_user.organization_id,
            Organization.is_active == True
        ).all()
        
        if audit_context:
            audit_context.log_access(
                "SUPPLIER_LIST", current_user.id, "GET_VISIBLE_SUPPLIERS",
                details={
                    "visible_count": len(suppliers),
                    "reason": "organization_scoped",
                    "scope": "own_organization_suppliers"
                }
            )
        
        return suppliers
    
    @staticmethod
    def validate_supplier_access(current_user: User, supplier_id: uuid.UUID, 
                               action: str, db: Session,
                               audit_context: Optional[AuditContext] = None) -> bool:
        """Validate if user can access specific supplier with comprehensive logging"""
        user_role = current_user.role.value if hasattr(current_user.role, 'value') else str(current_user.role)
        
        if user_role == "super_admin":
            if audit_context:
                audit_context.log_access(
                    "SUPPLIER", supplier_id, action,
                    details={"access_granted": True, "reason": "superadmin_privilege"}
                )
            return True
        
        supplier = db.query(Organization).filter(Organization.id == supplier_id).first()
        if not supplier or supplier.organization_type != OrganizationType.supplier:
            if audit_context:
                audit_context.log_security_event(
                    "INVALID_SUPPLIER_ACCESS",
                    "MEDIUM",
                    f"Attempted access to invalid supplier: {supplier_id}",
                    details={
                        "supplier_id": str(supplier_id),
                        "action": action,
                        "supplier_exists": supplier is not None,
                        "is_supplier_type": supplier.organization_type == OrganizationType.supplier if supplier else False
                    }
                )
            return False
        
        # Check if supplier belongs to user's organization
        if supplier.parent_organization_id == current_user.organization_id:
            if audit_context:
                audit_context.log_access(
                    "SUPPLIER", supplier_id, action,
                    details={
                        "access_granted": True,
                        "reason": "supplier_belongs_to_user_organization"
                    }
                )
            return True
        
        # Access denied - log violation
        EnhancedAuditSystem.log_supplier_visibility_violation(
            user_id=current_user.id,
            user_organization_id=current_user.organization_id,
            attempted_supplier_id=supplier_id,
            action=action,
            db=db
        )
        
        if audit_context:
            audit_context.log_security_event(
                "SUPPLIER_ACCESS_DENIED",
                "MEDIUM",
                f"Access denied to supplier {supplier_id}",
                details={
                    "supplier_id": str(supplier_id),
                    "supplier_parent_org": str(supplier.parent_organization_id),
                    "user_organization": str(current_user.organization_id),
                    "action": action
                }
            )
        
        return False

# Decorator for enforcing organizational isolation
def enforce_organizational_isolation(resource_type: str, get_resource_org_id=None):
    """
    Decorator to enforce organizational data isolation
    
    Args:
        resource_type: Type of resource being accessed
        get_resource_org_id: Function to extract organization ID from resource
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            current_user = kwargs.get('current_user')
            db = kwargs.get('db')
            request = kwargs.get('request')
            
            if not current_user or not db:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Missing required dependencies for isolation check"
                )
            
            audit_context = AuditContext(current_user, request)
            
            # For superadmin, allow all access but still log it
            user_role = current_user.role.value if hasattr(current_user.role, 'value') else str(current_user.role)
            if user_role == "super_admin":
                audit_context.log_access(
                    resource_type, current_user.id, "ISOLATION_CHECK_BYPASSED",
                    details={"reason": "superadmin_privilege"}
                )
                return await func(*args, **kwargs)
            
            # If we have a function to get resource organization ID, validate access
            if get_resource_org_id:
                try:
                    resource_org_id = get_resource_org_id(*args, **kwargs)
                    if resource_org_id:
                        validation_result = EnhancedOrganizationalDataFilter.validate_organization_access(
                            current_user, resource_org_id, db, audit_context
                        )
                        
                        if not validation_result["allowed"]:
                            raise HTTPException(
                                status_code=status.HTTP_403_FORBIDDEN,
                                detail=f"Access denied: {validation_result['reason']}"
                            )
                except Exception as e:
                    # Log the error but don't block the request
                    audit_context.log_security_event(
                        "ISOLATION_CHECK_ERROR",
                        "MEDIUM",
                        f"Error during isolation check: {str(e)}",
                        details={"resource_type": resource_type, "error": str(e)}
                    )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator

# Helper functions for common organizational queries
def get_organization_scoped_query(model_class, current_user: User, db: Session,
                                audit_context: Optional[AuditContext] = None):
    """Get a query pre-filtered by organizational access"""
    base_query = db.query(model_class)
    return EnhancedOrganizationalDataFilter.filter_query_by_organization(
        base_query, model_class, current_user, db, audit_context
    )

def validate_cross_organizational_transaction(
    source_org_id: uuid.UUID, 
    target_org_id: uuid.UUID, 
    current_user: User, 
    db: Session,
    audit_context: Optional[AuditContext] = None
) -> bool:
    """Validate if a cross-organizational transaction is allowed"""
    user_role = current_user.role.value if hasattr(current_user.role, 'value') else str(current_user.role)
    
    # Superadmin can perform any transaction
    if user_role == "super_admin":
        if audit_context:
            audit_context.log_access(
                "CROSS_ORG_TRANSACTION", current_user.id, "VALIDATE_TRANSACTION",
                details={
                    "source_org": str(source_org_id),
                    "target_org": str(target_org_id),
                    "allowed": True,
                    "reason": "superadmin_privilege"
                }
            )
        return True
    
    # Users can only perform transactions within their accessible organizations
    accessible_org_ids = EnhancedOrganizationalDataFilter.get_accessible_organization_ids(
        current_user, db, audit_context
    )
    
    transaction_allowed = (source_org_id in accessible_org_ids and target_org_id in accessible_org_ids)
    
    if audit_context:
        audit_context.log_access(
            "CROSS_ORG_TRANSACTION", current_user.id, "VALIDATE_TRANSACTION",
            details={
                "source_org": str(source_org_id),
                "target_org": str(target_org_id),
                "allowed": transaction_allowed,
                "accessible_org_count": len(accessible_org_ids),
                "reason": "within_accessible_orgs" if transaction_allowed else "outside_accessible_orgs"
            }
        )
    
    return transaction_allowed