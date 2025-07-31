# backend/app/audit_trail.py

import uuid
import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List
from enum import Enum

from fastapi import Request
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc

from .auth import TokenData
from .models import SecurityEvent, UserManagementAuditLog, InvitationAuditLog
from .database import get_db

logger = logging.getLogger(__name__)

class AuditEventType(str, Enum):
    """Types of audit events that can be tracked."""
    # Authentication events
    LOGIN_SUCCESS = "login_success"
    LOGIN_FAILED = "login_failed"
    LOGOUT = "logout"
    SESSION_TERMINATED = "session_terminated"
    PASSWORD_CHANGED = "password_changed"
    
    # Authorization events
    PERMISSION_DENIED = "permission_denied"
    PERMISSION_GRANTED = "permission_granted"
    ROLE_ESCALATION = "role_escalation"
    
    # Data access events
    DATA_ACCESS = "data_access"
    DATA_MODIFICATION = "data_modification"
    DATA_DELETION = "data_deletion"
    CROSS_ORG_ACCESS = "cross_org_access"
    
    # Security events
    SUSPICIOUS_ACTIVITY = "suspicious_activity"
    ACCOUNT_LOCKED = "account_locked"
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"
    SECURITY_VIOLATION = "security_violation"
    
    # Organizational isolation events
    ORG_BOUNDARY_VIOLATION = "org_boundary_violation"
    SUPPLIER_ACCESS_DENIED = "supplier_access_denied"
    BOSSAQUA_ACCESS_ATTEMPT = "bossaqua_access_attempt"
    
    # Administrative events
    USER_CREATED = "user_created"
    USER_MODIFIED = "user_modified"
    USER_DEACTIVATED = "user_deactivated"
    ORGANIZATION_MODIFIED = "organization_modified"

class RiskLevel(str, Enum):
    """Risk levels for audit events."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class AuditTrailManager:
    """
    Enhanced audit trail manager for comprehensive security and data access tracking.
    Implements requirements 10.1, 10.2, 10.4, 10.5 for audit trail tracking.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def log_security_event(
        self,
        event_type: AuditEventType,
        user_id: Optional[uuid.UUID] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        session_id: Optional[str] = None,
        details: Optional[str] = None,
        risk_level: RiskLevel = RiskLevel.LOW,
        additional_context: Optional[Dict[str, Any]] = None,
        db: Session = None
    ) -> Optional[uuid.UUID]:
        """
        Log a security event to the audit trail.
        
        Args:
            event_type: Type of security event
            user_id: ID of the user involved (if applicable)
            ip_address: IP address of the request
            user_agent: User agent string
            session_id: Session ID (if applicable)
            details: Additional details about the event
            risk_level: Risk level of the event
            additional_context: Additional context data
            db: Database session
            
        Returns:
            UUID of the created security event record
        """
        try:
            if not db:
                self.logger.warning("No database session provided for security event logging")
                return None
            
            # Prepare details with additional context
            event_details = details or ""
            if additional_context:
                context_str = json.dumps(additional_context, default=str)
                event_details = f"{event_details}\nContext: {context_str}" if event_details else f"Context: {context_str}"
            
            # Create security event record
            security_event = SecurityEvent(
                user_id=user_id,
                event_type=event_type.value,
                ip_address=ip_address,
                user_agent=user_agent,
                session_id=session_id,
                details=event_details,
                risk_level=risk_level.value
            )
            
            db.add(security_event)
            db.commit()
            
            # Log to application logger based on risk level
            log_message = f"Security Event: {event_type.value} - Risk: {risk_level.value}"
            if user_id:
                log_message += f" - User: {user_id}"
            if ip_address:
                log_message += f" - IP: {ip_address}"
            
            if risk_level == RiskLevel.CRITICAL:
                self.logger.critical(log_message)
            elif risk_level == RiskLevel.HIGH:
                self.logger.error(log_message)
            elif risk_level == RiskLevel.MEDIUM:
                self.logger.warning(log_message)
            else:
                self.logger.info(log_message)
            
            return security_event.id
            
        except Exception as e:
            self.logger.error(f"Failed to log security event {event_type.value}: {e}")
            return None
    
    def log_data_access(
        self,
        user: TokenData,
        resource_type: str,
        resource_id: Optional[uuid.UUID] = None,
        organization_id: Optional[uuid.UUID] = None,
        action: str = "read",
        request: Optional[Request] = None,
        db: Session = None
    ) -> Optional[uuid.UUID]:
        """
        Log data access events for audit trail.
        
        Args:
            user: Current user token data
            resource_type: Type of resource being accessed
            resource_id: ID of the specific resource
            organization_id: Organization ID of the resource
            action: Action being performed (read, write, delete)
            request: FastAPI request object
            db: Database session
            
        Returns:
            UUID of the created audit record
        """
        try:
            # Extract request information
            ip_address = None
            user_agent = None
            if request:
                ip_address = request.client.host if request.client else None
                user_agent = request.headers.get("user-agent")
            
            # Prepare context
            context = {
                "resource_type": resource_type,
                "action": action,
                "user_organization_id": str(user.organization_id)
            }
            
            if resource_id:
                context["resource_id"] = str(resource_id)
            if organization_id:
                context["resource_organization_id"] = str(organization_id)
            
            # Determine risk level based on action and cross-organizational access
            risk_level = RiskLevel.LOW
            if action in ["write", "delete"]:
                risk_level = RiskLevel.MEDIUM
            
            # Check for cross-organizational access
            if organization_id and organization_id != user.organization_id and user.role != "super_admin":
                risk_level = RiskLevel.MEDIUM
                context["cross_organizational_access"] = True
            
            details = f"Data access: {action} on {resource_type}"
            if resource_id:
                details += f" (ID: {resource_id})"
            
            return self.log_security_event(
                event_type=AuditEventType.DATA_ACCESS,
                user_id=user.user_id,
                ip_address=ip_address,
                user_agent=user_agent,
                details=details,
                risk_level=risk_level,
                additional_context=context,
                db=db
            )
            
        except Exception as e:
            self.logger.error(f"Failed to log data access event: {e}")
            return None
    
    def log_organizational_boundary_violation(
        self,
        user: TokenData,
        attempted_organization_id: uuid.UUID,
        resource_type: str,
        action: str,
        request: Optional[Request] = None,
        db: Session = None
    ) -> Optional[uuid.UUID]:
        """
        Log organizational boundary violations.
        
        Args:
            user: Current user token data
            attempted_organization_id: Organization ID that was attempted to be accessed
            resource_type: Type of resource
            action: Action that was attempted
            request: FastAPI request object
            db: Database session
            
        Returns:
            UUID of the created audit record
        """
        try:
            # Extract request information
            ip_address = None
            user_agent = None
            endpoint = None
            if request:
                ip_address = request.client.host if request.client else None
                user_agent = request.headers.get("user-agent")
                endpoint = str(request.url)
            
            context = {
                "user_organization_id": str(user.organization_id),
                "attempted_organization_id": str(attempted_organization_id),
                "resource_type": resource_type,
                "action": action,
                "user_role": user.role
            }
            
            if endpoint:
                context["endpoint"] = endpoint
            
            details = (
                f"Organizational boundary violation: User from organization {user.organization_id} "
                f"attempted {action} on {resource_type} in organization {attempted_organization_id}"
            )
            
            return self.log_security_event(
                event_type=AuditEventType.ORG_BOUNDARY_VIOLATION,
                user_id=user.user_id,
                ip_address=ip_address,
                user_agent=user_agent,
                details=details,
                risk_level=RiskLevel.HIGH,
                additional_context=context,
                db=db
            )
            
        except Exception as e:
            self.logger.error(f"Failed to log organizational boundary violation: {e}")
            return None
    
    def log_supplier_visibility_violation(
        self,
        user: TokenData,
        supplier_id: uuid.UUID,
        action: str,
        request: Optional[Request] = None,
        db: Session = None
    ) -> Optional[uuid.UUID]:
        """
        Log supplier visibility restriction violations.
        
        Args:
            user: Current user token data
            supplier_id: Supplier organization ID
            action: Action that was attempted
            request: FastAPI request object
            db: Database session
            
        Returns:
            UUID of the created audit record
        """
        try:
            # Extract request information
            ip_address = None
            user_agent = None
            if request:
                ip_address = request.client.host if request.client else None
                user_agent = request.headers.get("user-agent")
            
            context = {
                "user_organization_id": str(user.organization_id),
                "supplier_id": str(supplier_id),
                "action": action,
                "user_role": user.role
            }
            
            details = (
                f"Supplier visibility violation: User from organization {user.organization_id} "
                f"attempted {action} on supplier {supplier_id} which is not visible to them"
            )
            
            return self.log_security_event(
                event_type=AuditEventType.SUPPLIER_ACCESS_DENIED,
                user_id=user.user_id,
                ip_address=ip_address,
                user_agent=user_agent,
                details=details,
                risk_level=RiskLevel.MEDIUM,
                additional_context=context,
                db=db
            )
            
        except Exception as e:
            self.logger.error(f"Failed to log supplier visibility violation: {e}")
            return None
    
    def log_bossaqua_access_attempt(
        self,
        user: TokenData,
        resource_type: str,
        action: str,
        request: Optional[Request] = None,
        db: Session = None
    ) -> Optional[uuid.UUID]:
        """
        Log attempts to access BossAqua data by non-superadmin users.
        
        Args:
            user: Current user token data
            resource_type: Type of resource
            action: Action that was attempted
            request: FastAPI request object
            db: Database session
            
        Returns:
            UUID of the created audit record
        """
        try:
            # Extract request information
            ip_address = None
            user_agent = None
            if request:
                ip_address = request.client.host if request.client else None
                user_agent = request.headers.get("user-agent")
            
            context = {
                "user_organization_id": str(user.organization_id),
                "resource_type": resource_type,
                "action": action,
                "user_role": user.role
            }
            
            details = (
                f"BossAqua access attempt: Non-superadmin user {user.username} "
                f"attempted {action} on BossAqua {resource_type}"
            )
            
            return self.log_security_event(
                event_type=AuditEventType.BOSSAQUA_ACCESS_ATTEMPT,
                user_id=user.user_id,
                ip_address=ip_address,
                user_agent=user_agent,
                details=details,
                risk_level=RiskLevel.HIGH,
                additional_context=context,
                db=db
            )
            
        except Exception as e:
            self.logger.error(f"Failed to log BossAqua access attempt: {e}")
            return None
    
    def log_permission_denied(
        self,
        user: TokenData,
        resource_type: str,
        permission: str,
        context: Optional[Dict[str, Any]] = None,
        request: Optional[Request] = None,
        db: Session = None
    ) -> Optional[uuid.UUID]:
        """
        Log permission denied events.
        
        Args:
            user: Current user token data
            resource_type: Type of resource
            permission: Permission that was denied
            context: Additional context
            request: FastAPI request object
            db: Database session
            
        Returns:
            UUID of the created audit record
        """
        try:
            # Extract request information
            ip_address = None
            user_agent = None
            endpoint = None
            if request:
                ip_address = request.client.host if request.client else None
                user_agent = request.headers.get("user-agent")
                endpoint = str(request.url)
            
            audit_context = {
                "resource_type": resource_type,
                "permission": permission,
                "user_role": user.role,
                "user_organization_id": str(user.organization_id)
            }
            
            if context:
                audit_context.update(context)
            if endpoint:
                audit_context["endpoint"] = endpoint
            
            details = f"Permission denied: {permission} on {resource_type}"
            
            return self.log_security_event(
                event_type=AuditEventType.PERMISSION_DENIED,
                user_id=user.user_id,
                ip_address=ip_address,
                user_agent=user_agent,
                details=details,
                risk_level=RiskLevel.MEDIUM,
                additional_context=audit_context,
                db=db
            )
            
        except Exception as e:
            self.logger.error(f"Failed to log permission denied event: {e}")
            return None
    
    def get_security_events(
        self,
        user: TokenData,
        organization_id: Optional[uuid.UUID] = None,
        event_type: Optional[AuditEventType] = None,
        risk_level: Optional[RiskLevel] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100,
        db: Session = None
    ) -> List[SecurityEvent]:
        """
        Retrieve security events with organizational filtering.
        
        Args:
            user: Current user token data
            organization_id: Filter by organization ID
            event_type: Filter by event type
            risk_level: Filter by risk level
            start_date: Start date for filtering
            end_date: End date for filtering
            limit: Maximum number of records to return
            db: Database session
            
        Returns:
            List of security events
        """
        try:
            if not db:
                return []
            
            query = db.query(SecurityEvent)
            
            # Apply organizational filtering
            if user.role != "super_admin":
                # Non-superadmins can only see events from their own organization
                # We need to join with users to filter by organization
                from .models import User
                query = query.join(User, SecurityEvent.user_id == User.id, isouter=True)
                query = query.filter(
                    or_(
                        User.organization_id == user.organization_id,
                        SecurityEvent.user_id.is_(None)  # Include events without user_id
                    )
                )
            
            # Apply additional filters
            if organization_id and user.role == "super_admin":
                from .models import User
                query = query.join(User, SecurityEvent.user_id == User.id, isouter=True)
                query = query.filter(User.organization_id == organization_id)
            
            if event_type:
                query = query.filter(SecurityEvent.event_type == event_type.value)
            
            if risk_level:
                query = query.filter(SecurityEvent.risk_level == risk_level.value)
            
            if start_date:
                query = query.filter(SecurityEvent.timestamp >= start_date)
            
            if end_date:
                query = query.filter(SecurityEvent.timestamp <= end_date)
            
            # Order by timestamp descending and limit results
            query = query.order_by(desc(SecurityEvent.timestamp)).limit(limit)
            
            return query.all()
            
        except Exception as e:
            self.logger.error(f"Failed to retrieve security events: {e}")
            return []
    
    def get_audit_summary(
        self,
        user: TokenData,
        organization_id: Optional[uuid.UUID] = None,
        days: int = 30,
        db: Session = None
    ) -> Dict[str, Any]:
        """
        Get audit summary statistics.
        
        Args:
            user: Current user token data
            organization_id: Filter by organization ID
            days: Number of days to include in summary
            db: Database session
            
        Returns:
            Dictionary containing audit summary statistics
        """
        try:
            if not db:
                return {}
            
            from datetime import timedelta
            start_date = datetime.utcnow() - timedelta(days=days)
            
            # Get security events
            events = self.get_security_events(
                user=user,
                organization_id=organization_id,
                start_date=start_date,
                limit=10000,  # High limit for summary
                db=db
            )
            
            # Calculate statistics
            total_events = len(events)
            event_types = {}
            risk_levels = {}
            
            for event in events:
                # Count by event type
                event_types[event.event_type] = event_types.get(event.event_type, 0) + 1
                
                # Count by risk level
                risk_levels[event.risk_level] = risk_levels.get(event.risk_level, 0) + 1
            
            # Get high-risk events
            high_risk_events = [e for e in events if e.risk_level in ['high', 'critical']]
            
            return {
                "period_days": days,
                "total_events": total_events,
                "event_types": event_types,
                "risk_levels": risk_levels,
                "high_risk_events_count": len(high_risk_events),
                "recent_high_risk_events": [
                    {
                        "id": str(e.id),
                        "event_type": e.event_type,
                        "risk_level": e.risk_level,
                        "timestamp": e.timestamp.isoformat(),
                        "details": e.details
                    }
                    for e in high_risk_events[:10]  # Last 10 high-risk events
                ]
            }
            
        except Exception as e:
            self.logger.error(f"Failed to generate audit summary: {e}")
            return {"error": str(e)}

# Global audit trail manager instance
audit_trail_manager = AuditTrailManager()

# Convenience functions for common audit operations
def log_data_access(user: TokenData, resource_type: str, action: str = "read", 
                   resource_id: Optional[uuid.UUID] = None, 
                   organization_id: Optional[uuid.UUID] = None,
                   request: Optional[Request] = None, db: Session = None):
    """Convenience function to log data access."""
    return audit_trail_manager.log_data_access(
        user=user,
        resource_type=resource_type,
        resource_id=resource_id,
        organization_id=organization_id,
        action=action,
        request=request,
        db=db
    )

def log_organizational_violation(user: TokenData, attempted_org_id: uuid.UUID, 
                               resource_type: str, action: str,
                               request: Optional[Request] = None, db: Session = None):
    """Convenience function to log organizational boundary violations."""
    return audit_trail_manager.log_organizational_boundary_violation(
        user=user,
        attempted_organization_id=attempted_org_id,
        resource_type=resource_type,
        action=action,
        request=request,
        db=db
    )

def log_permission_denied(user: TokenData, resource_type: str, permission: str,
                         context: Optional[Dict[str, Any]] = None,
                         request: Optional[Request] = None, db: Session = None):
    """Convenience function to log permission denied events."""
    return audit_trail_manager.log_permission_denied(
        user=user,
        resource_type=resource_type,
        permission=permission,
        context=context,
        request=request,
        db=db
    )