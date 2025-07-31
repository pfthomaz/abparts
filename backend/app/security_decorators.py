# backend/app/security_decorators.py

import uuid
import logging
from functools import wraps
from typing import Dict, Any, Optional, Callable, Union

from fastapi import HTTPException, status, Request, Depends
from sqlalchemy.orm import Session

from .models import User, Organization, OrganizationType, UserRole
from .enhanced_organizational_isolation import (
    EnhancedOrganizationalDataFilter,
    EnhancedBossAquaAccessControl,
    EnhancedSupplierVisibilityControl,
    OrganizationalIsolationError
)
from .enhanced_audit_system import EnhancedAuditSystem, AuditContext
from .database import get_db
from .auth import get_current_user_object

security_logger = logging.getLogger("security")

def validate_organizational_isolation(
    resource_type: str,
    get_organization_id: Optional[Callable] = None,
    allow_superadmin_bypass: bool = True
):
    """
    Decorator to validate organizational data isolation
    
    Args:
        resource_type: Type of resource being accessed
        get_organization_id: Function to extract organization ID from request
        allow_superadmin_bypass: Whether superadmin can bypass isolation checks
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract dependencies
            current_user = kwargs.get('current_user')
            db = kwargs.get('db')
            request = kwargs.get('request')
            
            if not current_user or not db:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Missing required dependencies for isolation validation"
                )
            
            audit_context = AuditContext(current_user, request)
            user_role = current_user.role.value if hasattr(current_user.role, 'value') else str(current_user.role)
            
            # Superadmin bypass if allowed
            if allow_superadmin_bypass and user_role == "super_admin":
                audit_context.log_access(
                    resource_type, current_user.id, "ISOLATION_BYPASSED",
                    details={"reason": "superadmin_privilege"}
                )
                return await func(*args, **kwargs)
            
            # Extract organization ID if function provided
            if get_organization_id:
                try:
                    org_id = get_organization_id(*args, **kwargs)
                    if org_id:
                        validation_result = EnhancedOrganizationalDataFilter.validate_organization_access(
                            current_user, org_id, db, audit_context
                        )
                        
                        if not validation_result["allowed"]:
                            raise HTTPException(
                                status_code=status.HTTP_403_FORBIDDEN,
                                detail=f"Organizational isolation violation: {validation_result['reason']}"
                            )
                except Exception as e:
                    audit_context.log_security_event(
                        "ISOLATION_VALIDATION_ERROR",
                        "MEDIUM",
                        f"Error validating organizational isolation: {str(e)}",
                        details={"resource_type": resource_type, "error": str(e)}
                    )
                    # Continue with request but log the error
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator

def validate_bossaqua_access(action: str):
    """
    Decorator to validate BossAqua data access
    
    Args:
        action: The action being performed on BossAqua data
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
                    detail="Missing required dependencies for BossAqua access validation"
                )
            
            audit_context = AuditContext(current_user, request)
            
            if not EnhancedBossAquaAccessControl.validate_bossaqua_access(
                current_user, action, audit_context, db
            ):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Access denied: Only superadmin can access BossAqua data"
                )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator

def validate_supplier_visibility(get_supplier_id: Callable):
    """
    Decorator to validate supplier visibility restrictions
    
    Args:
        get_supplier_id: Function to extract supplier ID from request
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
                    detail="Missing required dependencies for supplier visibility validation"
                )
            
            audit_context = AuditContext(current_user, request)
            
            try:
                supplier_id = get_supplier_id(*args, **kwargs)
                if supplier_id:
                    if not EnhancedSupplierVisibilityControl.validate_supplier_access(
                        current_user, supplier_id, "ACCESS", db, audit_context
                    ):
                        raise HTTPException(
                            status_code=status.HTTP_403_FORBIDDEN,
                            detail="Access denied: Supplier not visible to your organization"
                        )
            except Exception as e:
                audit_context.log_security_event(
                    "SUPPLIER_VALIDATION_ERROR",
                    "MEDIUM",
                    f"Error validating supplier visibility: {str(e)}",
                    details={"error": str(e)}
                )
                # Continue with request but log the error
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator

def audit_data_access(resource_type: str, action: str, get_resource_id: Optional[Callable] = None):
    """
    Decorator to audit data access operations
    
    Args:
        resource_type: Type of resource being accessed
        action: Action being performed
        get_resource_id: Function to extract resource ID from request
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            current_user = kwargs.get('current_user')
            db = kwargs.get('db')
            request = kwargs.get('request')
            
            if current_user:
                audit_context = AuditContext(current_user, request)
                
                # Extract resource ID if function provided
                resource_id = current_user.id  # Default to user ID
                if get_resource_id:
                    try:
                        extracted_id = get_resource_id(*args, **kwargs)
                        if extracted_id:
                            resource_id = extracted_id
                    except Exception as e:
                        audit_context.log_security_event(
                            "AUDIT_ID_EXTRACTION_ERROR",
                            "LOW",
                            f"Error extracting resource ID for audit: {str(e)}",
                            details={"resource_type": resource_type, "action": action, "error": str(e)}
                        )
                
                # Log the access
                audit_context.log_access(resource_type, resource_id, action, db=db)
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator

def audit_data_modification(resource_type: str, action: str, get_resource_id: Optional[Callable] = None):
    """
    Decorator to audit data modification operations
    
    Args:
        resource_type: Type of resource being modified
        action: Action being performed (CREATE, UPDATE, DELETE)
        get_resource_id: Function to extract resource ID from request
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            current_user = kwargs.get('current_user')
            db = kwargs.get('db')
            request = kwargs.get('request')
            
            if current_user:
                audit_context = AuditContext(current_user, request)
                
                # Extract resource ID if function provided
                resource_id = current_user.id  # Default to user ID
                if get_resource_id:
                    try:
                        extracted_id = get_resource_id(*args, **kwargs)
                        if extracted_id:
                            resource_id = extracted_id
                    except Exception as e:
                        audit_context.log_security_event(
                            "AUDIT_ID_EXTRACTION_ERROR",
                            "LOW",
                            f"Error extracting resource ID for audit: {str(e)}",
                            details={"resource_type": resource_type, "action": action, "error": str(e)}
                        )
                
                # For modifications, we should ideally capture old values
                # This is a simplified implementation
                old_values = {"note": "Old values capture not implemented"}
                
                # Execute the function
                result = await func(*args, **kwargs)
                
                # Log the modification
                new_values = {"note": "New values capture not implemented"}
                audit_context.log_modification(
                    resource_type, resource_id, action,
                    old_values=old_values, new_values=new_values, db=db
                )
                
                return result
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator

def comprehensive_security_validation(
    resource_type: str,
    action: str,
    get_organization_id: Optional[Callable] = None,
    get_resource_id: Optional[Callable] = None,
    check_bossaqua: bool = False,
    check_supplier_visibility: bool = False,
    get_supplier_id: Optional[Callable] = None
):
    """
    Comprehensive security validation decorator that combines multiple checks
    
    Args:
        resource_type: Type of resource being accessed
        action: Action being performed
        get_organization_id: Function to extract organization ID
        get_resource_id: Function to extract resource ID
        check_bossaqua: Whether to check BossAqua access restrictions
        check_supplier_visibility: Whether to check supplier visibility
        get_supplier_id: Function to extract supplier ID
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
                    detail="Missing required dependencies for security validation"
                )
            
            audit_context = AuditContext(current_user, request)
            user_role = current_user.role.value if hasattr(current_user.role, 'value') else str(current_user.role)
            
            try:
                # 1. Organizational isolation validation
                if get_organization_id and user_role != "super_admin":
                    org_id = get_organization_id(*args, **kwargs)
                    if org_id:
                        validation_result = EnhancedOrganizationalDataFilter.validate_organization_access(
                            current_user, org_id, db, audit_context
                        )
                        
                        if not validation_result["allowed"]:
                            raise HTTPException(
                                status_code=status.HTTP_403_FORBIDDEN,
                                detail=f"Organizational isolation violation: {validation_result['reason']}"
                            )
                
                # 2. BossAqua access validation
                if check_bossaqua:
                    if not EnhancedBossAquaAccessControl.validate_bossaqua_access(
                        current_user, action, audit_context, db
                    ):
                        raise HTTPException(
                            status_code=status.HTTP_403_FORBIDDEN,
                            detail="Access denied: Only superadmin can access BossAqua data"
                        )
                
                # 3. Supplier visibility validation
                if check_supplier_visibility and get_supplier_id:
                    supplier_id = get_supplier_id(*args, **kwargs)
                    if supplier_id:
                        if not EnhancedSupplierVisibilityControl.validate_supplier_access(
                            current_user, supplier_id, action, db, audit_context
                        ):
                            raise HTTPException(
                                status_code=status.HTTP_403_FORBIDDEN,
                                detail="Access denied: Supplier not visible to your organization"
                            )
                
                # 4. Audit logging
                resource_id = current_user.id  # Default
                if get_resource_id:
                    try:
                        extracted_id = get_resource_id(*args, **kwargs)
                        if extracted_id:
                            resource_id = extracted_id
                    except Exception:
                        pass  # Use default
                
                # Log the access/modification
                if action in ['CREATE', 'UPDATE', 'DELETE']:
                    audit_context.log_modification(resource_type, resource_id, action, db=db)
                else:
                    audit_context.log_access(resource_type, resource_id, action, db=db)
                
                # Execute the function
                return await func(*args, **kwargs)
                
            except HTTPException:
                raise
            except Exception as e:
                audit_context.log_security_event(
                    "SECURITY_VALIDATION_ERROR",
                    "HIGH",
                    f"Unexpected error in security validation: {str(e)}",
                    details={
                        "resource_type": resource_type,
                        "action": action,
                        "error": str(e)
                    }
                )
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Security validation error"
                )
        
        return wrapper
    return decorator

# Helper functions for common ID extraction patterns
def extract_id_from_path(param_name: str = "id"):
    """Helper to extract ID from path parameters"""
    def extractor(*args, **kwargs):
        return kwargs.get(param_name)
    return extractor

def extract_org_id_from_user(current_user_param: str = "current_user"):
    """Helper to extract organization ID from current user"""
    def extractor(*args, **kwargs):
        user = kwargs.get(current_user_param)
        return user.organization_id if user else None
    return extractor

def extract_org_id_from_resource(resource_param: str, org_field: str = "organization_id"):
    """Helper to extract organization ID from a resource object"""
    def extractor(*args, **kwargs):
        resource = kwargs.get(resource_param)
        return getattr(resource, org_field, None) if resource else None
    return extractor