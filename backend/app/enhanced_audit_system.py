# backend/app/enhanced_audit_system.py

import uuid
import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List, Union
from contextlib import contextmanager

from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from fastapi import Request

from .database import SessionLocal
from .models import AuditLog, SecurityEventLog, User, Organization

# Configure specialized loggers
audit_logger = logging.getLogger("audit")
security_logger = logging.getLogger("security")

class EnhancedAuditSystem:
    """Enhanced audit system for comprehensive tracking of all data access and modifications"""
    
    @staticmethod
    def log_data_access(
        user_id: uuid.UUID,
        organization_id: uuid.UUID,
        resource_type: str,
        resource_id: uuid.UUID,
        action: str,
        details: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        endpoint: Optional[str] = None,
        http_method: Optional[str] = None,
        db: Optional[Session] = None
    ) -> bool:
        """Log data access events with comprehensive context"""
        
        should_close_db = False
        if db is None:
            db = SessionLocal()
            should_close_db = True
        
        try:
            audit_entry = AuditLog(
                user_id=user_id,
                organization_id=organization_id,
                resource_type=resource_type,
                resource_id=resource_id,
                action=action,
                details=json.dumps(details) if details else None,
                ip_address=ip_address,
                user_agent=user_agent,
                endpoint=endpoint,
                http_method=http_method
            )
            
            db.add(audit_entry)
            db.commit()
            
            # Also log to application logger
            audit_logger.info(
                f"DATA_ACCESS: user={user_id} org={organization_id} "
                f"resource={resource_type}:{resource_id} action={action}"
            )
            
            return True
            
        except SQLAlchemyError as e:
            db.rollback()
            audit_logger.error(f"Failed to log audit entry: {str(e)}")
            return False
        finally:
            if should_close_db:
                db.close()
    
    @staticmethod
    def log_data_modification(
        user_id: uuid.UUID,
        organization_id: uuid.UUID,
        resource_type: str,
        resource_id: uuid.UUID,
        action: str,
        old_values: Optional[Dict[str, Any]] = None,
        new_values: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        endpoint: Optional[str] = None,
        http_method: Optional[str] = None,
        db: Optional[Session] = None
    ) -> bool:
        """Log data modification events with before/after values"""
        
        should_close_db = False
        if db is None:
            db = SessionLocal()
            should_close_db = True
        
        try:
            audit_entry = AuditLog(
                user_id=user_id,
                organization_id=organization_id,
                resource_type=resource_type,
                resource_id=resource_id,
                action=action,
                old_values=json.dumps(old_values) if old_values else None,
                new_values=json.dumps(new_values) if new_values else None,
                ip_address=ip_address,
                user_agent=user_agent,
                endpoint=endpoint,
                http_method=http_method
            )
            
            db.add(audit_entry)
            db.commit()
            
            # Also log to application logger
            audit_logger.info(
                f"DATA_MODIFY: user={user_id} org={organization_id} "
                f"resource={resource_type}:{resource_id} action={action}"
            )
            
            return True
            
        except SQLAlchemyError as e:
            db.rollback()
            audit_logger.error(f"Failed to log modification audit entry: {str(e)}")
            return False
        finally:
            if should_close_db:
                db.close()
    
    @staticmethod
    def log_security_event(
        event_type: str,
        severity: str,
        description: str,
        user_id: Optional[uuid.UUID] = None,
        organization_id: Optional[uuid.UUID] = None,
        details: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        endpoint: Optional[str] = None,
        db: Optional[Session] = None
    ) -> bool:
        """Log security events"""
        
        should_close_db = False
        if db is None:
            db = SessionLocal()
            should_close_db = True
        
        try:
            security_event = SecurityEventLog(
                event_type=event_type,
                severity=severity,
                description=description,
                user_id=user_id,
                organization_id=organization_id,
                details=json.dumps(details) if details else None,
                ip_address=ip_address,
                user_agent=user_agent,
                endpoint=endpoint,
                resolved="OPEN"
            )
            
            db.add(security_event)
            db.commit()
            
            # Also log to security logger
            security_logger.warning(
                f"SECURITY_EVENT: type={event_type} severity={severity} "
                f"user={user_id} org={organization_id} desc={description}"
            )
            
            return True
            
        except SQLAlchemyError as e:
            db.rollback()
            security_logger.error(f"Failed to log security event: {str(e)}")
            return False
        finally:
            if should_close_db:
                db.close()
    
    @staticmethod
    def log_organizational_isolation_violation(
        user_id: uuid.UUID,
        user_organization_id: uuid.UUID,
        attempted_organization_id: uuid.UUID,
        resource_type: str,
        action: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        endpoint: Optional[str] = None,
        db: Optional[Session] = None
    ) -> bool:
        """Log organizational isolation violations"""
        
        details = {
            "user_organization_id": str(user_organization_id),
            "attempted_organization_id": str(attempted_organization_id),
            "resource_type": resource_type,
            "action": action
        }
        
        return EnhancedAuditSystem.log_security_event(
            event_type="ORGANIZATIONAL_ISOLATION_VIOLATION",
            severity="HIGH",
            description=f"User {user_id} attempted to access {resource_type} from organization {attempted_organization_id}",
            user_id=user_id,
            organization_id=user_organization_id,
            details=details,
            ip_address=ip_address,
            user_agent=user_agent,
            endpoint=endpoint,
            db=db
        )
    
    @staticmethod
    def log_bossaqua_access_violation(
        user_id: uuid.UUID,
        user_organization_id: uuid.UUID,
        user_role: str,
        action: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        endpoint: Optional[str] = None,
        db: Optional[Session] = None
    ) -> bool:
        """Log BossAqua access violations"""
        
        details = {
            "user_role": user_role,
            "action": action,
            "violation_type": "BOSSAQUA_ACCESS_DENIED"
        }
        
        return EnhancedAuditSystem.log_security_event(
            event_type="BOSSAQUA_ACCESS_VIOLATION",
            severity="HIGH",
            description=f"Non-superadmin user {user_id} (role: {user_role}) attempted BossAqua access: {action}",
            user_id=user_id,
            organization_id=user_organization_id,
            details=details,
            ip_address=ip_address,
            user_agent=user_agent,
            endpoint=endpoint,
            db=db
        )
    
    @staticmethod
    def log_supplier_visibility_violation(
        user_id: uuid.UUID,
        user_organization_id: uuid.UUID,
        attempted_supplier_id: uuid.UUID,
        action: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        endpoint: Optional[str] = None,
        db: Optional[Session] = None
    ) -> bool:
        """Log supplier visibility violations"""
        
        details = {
            "attempted_supplier_id": str(attempted_supplier_id),
            "action": action,
            "violation_type": "SUPPLIER_VISIBILITY_DENIED"
        }
        
        return EnhancedAuditSystem.log_security_event(
            event_type="SUPPLIER_VISIBILITY_VIOLATION",
            severity="MEDIUM",
            description=f"User {user_id} attempted to access supplier {attempted_supplier_id} outside their organization",
            user_id=user_id,
            organization_id=user_organization_id,
            details=details,
            ip_address=ip_address,
            user_agent=user_agent,
            endpoint=endpoint,
            db=db
        )

class AuditContext:
    """Context manager for audit tracking"""
    
    def __init__(self, user: User, request: Optional[Request] = None):
        self.user = user
        self.request = request
        self.ip_address = None
        self.user_agent = None
        self.endpoint = None
        self.http_method = None
        
        if request:
            self.ip_address = request.client.host if request.client else None
            self.user_agent = request.headers.get("user-agent")
            self.endpoint = request.url.path
            self.http_method = request.method
    
    def log_access(self, resource_type: str, resource_id: uuid.UUID, action: str, 
                   details: Optional[Dict[str, Any]] = None, db: Optional[Session] = None):
        """Log data access within this context"""
        return EnhancedAuditSystem.log_data_access(
            user_id=self.user.id,
            organization_id=self.user.organization_id,
            resource_type=resource_type,
            resource_id=resource_id,
            action=action,
            details=details,
            ip_address=self.ip_address,
            user_agent=self.user_agent,
            endpoint=self.endpoint,
            http_method=self.http_method,
            db=db
        )
    
    def log_modification(self, resource_type: str, resource_id: uuid.UUID, action: str,
                        old_values: Optional[Dict[str, Any]] = None,
                        new_values: Optional[Dict[str, Any]] = None,
                        db: Optional[Session] = None):
        """Log data modification within this context"""
        return EnhancedAuditSystem.log_data_modification(
            user_id=self.user.id,
            organization_id=self.user.organization_id,
            resource_type=resource_type,
            resource_id=resource_id,
            action=action,
            old_values=old_values,
            new_values=new_values,
            ip_address=self.ip_address,
            user_agent=self.user_agent,
            endpoint=self.endpoint,
            http_method=self.http_method,
            db=db
        )
    
    def log_security_event(self, event_type: str, severity: str, description: str,
                          details: Optional[Dict[str, Any]] = None,
                          db: Optional[Session] = None):
        """Log security event within this context"""
        return EnhancedAuditSystem.log_security_event(
            event_type=event_type,
            severity=severity,
            description=description,
            user_id=self.user.id,
            organization_id=self.user.organization_id,
            details=details,
            ip_address=self.ip_address,
            user_agent=self.user_agent,
            endpoint=self.endpoint,
            db=db
        )

# Decorator for automatic audit logging
def audit_data_access(resource_type: str, action: str):
    """Decorator to automatically audit data access"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            # Extract user and resource_id from function arguments
            user = kwargs.get('current_user')
            resource_id = kwargs.get('id') or kwargs.get('resource_id')
            request = kwargs.get('request')
            db = kwargs.get('db')
            
            if user and resource_id:
                audit_context = AuditContext(user, request)
                audit_context.log_access(resource_type, resource_id, action, db=db)
            
            return func(*args, **kwargs)
        return wrapper
    return decorator

def audit_data_modification(resource_type: str, action: str):
    """Decorator to automatically audit data modifications"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            # Extract user and resource_id from function arguments
            user = kwargs.get('current_user')
            resource_id = kwargs.get('id') or kwargs.get('resource_id')
            request = kwargs.get('request')
            db = kwargs.get('db')
            
            # Get old values before modification
            old_values = None
            if user and resource_id and db and action in ['UPDATE', 'DELETE']:
                # This would need to be customized per resource type
                # For now, we'll just log that we attempted to get old values
                old_values = {"note": "Old values retrieval not implemented for this resource"}
            
            # Execute the function
            result = func(*args, **kwargs)
            
            # Log the modification
            if user and resource_id:
                audit_context = AuditContext(user, request)
                new_values = {"note": "New values extraction not implemented for this resource"}
                audit_context.log_modification(
                    resource_type, resource_id, action, 
                    old_values=old_values, new_values=new_values, db=db
                )
            
            return result
        return wrapper
    return decorator