# backend/app/security_middleware.py

import json
import uuid
from datetime import datetime
from typing import Optional
from fastapi import Request, Response, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from starlette.middleware.base import BaseHTTPMiddleware
from sqlalchemy.orm import Session

from .database import get_db
from .models import User, AuditLog, SecurityEventLog
from .enhanced_organizational_isolation import (
    OrganizationalIsolationError, 
    EnhancedOrganizationalDataFilter,
    EnhancedBossAquaAccessControl,
    EnhancedSupplierVisibilityControl
)
from .enhanced_audit_system import EnhancedAuditSystem, AuditContext

class SecurityAuditMiddleware(BaseHTTPMiddleware):
    """Enhanced middleware for security auditing and organizational isolation enforcement"""
    
    def __init__(self, app):
        super().__init__(app)
        self.excluded_paths = {
            "/docs", "/redoc", "/openapi.json", "/health", "/token", "/static", "/images"
        }
        self.sensitive_endpoints = {
            "/organizations", "/users", "/machines", "/warehouses", 
            "/inventory", "/parts", "/transactions", "/supplier_orders",
            "/customer_orders", "/part_usage"
        }
    
    async def dispatch(self, request: Request, call_next):
        # Skip audit for excluded paths
        if any(request.url.path.startswith(path) for path in self.excluded_paths):
            return await call_next(request)
        
        # Get client information
        client_ip = self.get_client_ip(request)
        user_agent = request.headers.get("user-agent", "")
        
        # Store request info for audit logging
        request.state.client_ip = client_ip
        request.state.user_agent = user_agent
        request.state.start_time = datetime.utcnow()
        
        # Get current user if available
        current_user = getattr(request.state, "current_user", None)
        audit_context = AuditContext(current_user, request) if current_user else None
        
        try:
            response = await call_next(request)
            
            # Enhanced audit logging for sensitive endpoints
            if self.is_sensitive_endpoint(request.url.path) and current_user:
                await self.log_enhanced_request_audit(request, response, "SUCCESS", audit_context)
            
            return response
            
        except OrganizationalIsolationError as e:
            # Log security violation with enhanced context
            await self.log_enhanced_security_event(
                request, 
                "ORGANIZATIONAL_ISOLATION_VIOLATION",
                "HIGH",
                str(e),
                audit_context
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: Organizational boundary violation"
            )
            
        except HTTPException as e:
            # Log HTTP errors for audit with enhanced context
            if current_user and self.is_sensitive_endpoint(request.url.path):
                await self.log_enhanced_request_audit(request, None, f"HTTP_ERROR_{e.status_code}", audit_context)
            raise
            
        except Exception as e:
            # Log unexpected errors with enhanced context
            await self.log_enhanced_security_event(
                request,
                "UNEXPECTED_ERROR", 
                "MEDIUM",
                f"Unexpected error: {str(e)}",
                audit_context
            )
            raise
    
    def get_client_ip(self, request: Request) -> str:
        """Extract client IP address from request"""
        # Check for forwarded headers first
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip
        
        # Fallback to direct client
        if hasattr(request.client, "host"):
            return request.client.host
        
        return "unknown"
    
    def is_sensitive_endpoint(self, path: str) -> bool:
        """Check if endpoint is sensitive and requires enhanced auditing"""
        return any(path.startswith(endpoint) for endpoint in self.sensitive_endpoints)
    
    async def log_enhanced_request_audit(self, request: Request, response: Optional[Response], 
                                       status: str, audit_context: Optional[AuditContext]):
        """Enhanced request audit logging with comprehensive context"""
        try:
            db = next(get_db())
            
            user = getattr(request.state, "current_user", None)
            if not user:
                return
            
            # Use enhanced audit system
            details = {
                "method": request.method,
                "path": request.url.path,
                "query_params": str(request.query_params),
                "status": status,
                "response_status": response.status_code if response else None,
                "processing_time": (datetime.utcnow() - request.state.start_time).total_seconds() if hasattr(request.state, 'start_time') else None,
                "sensitive_endpoint": self.is_sensitive_endpoint(request.url.path)
            }
            
            EnhancedAuditSystem.log_data_access(
                user_id=user.id,
                organization_id=user.organization_id,
                resource_type="API_REQUEST",
                resource_id=uuid.uuid4(),  # Generate a unique ID for the request
                action=f"{request.method}_{request.url.path}",
                details=details,
                ip_address=request.state.client_ip,
                user_agent=request.state.user_agent,
                endpoint=request.url.path,
                http_method=request.method,
                db=db
            )
            
        except Exception as e:
            # Don't let audit logging break the application
            print(f"Enhanced audit logging error: {e}")
        finally:
            db.close()
    
    async def log_enhanced_security_event(self, request: Request, event_type: str, 
                                        severity: str, description: str,
                                        audit_context: Optional[AuditContext]):
        """Enhanced security event logging with comprehensive context"""
        try:
            db = next(get_db())
            
            user = getattr(request.state, "current_user", None)
            
            details = {
                "method": request.method,
                "path": request.url.path,
                "query_params": str(request.query_params),
                "sensitive_endpoint": self.is_sensitive_endpoint(request.url.path),
                "processing_time": (datetime.utcnow() - request.state.start_time).total_seconds() if hasattr(request.state, 'start_time') else None
            }
            
            EnhancedAuditSystem.log_security_event(
                event_type=event_type,
                severity=severity,
                description=description,
                user_id=user.id if user else None,
                organization_id=user.organization_id if user else None,
                details=details,
                ip_address=request.state.client_ip,
                user_agent=request.state.user_agent,
                endpoint=request.url.path,
                db=db
            )
            
        except Exception as e:
            # Don't let security logging break the application
            print(f"Enhanced security logging error: {e}")
        finally:
            db.close()


class OrganizationalIsolationMiddleware(BaseHTTPMiddleware):
    """Enhanced middleware to enforce organizational data isolation"""
    
    def __init__(self, app):
        super().__init__(app)
        self.protected_endpoints = {
            "/organizations", "/users", "/machines", "/warehouses", 
            "/inventory", "/parts", "/transactions", "/supplier_orders",
            "/customer_orders", "/part_usage"
        }
        self.bossaqua_patterns = [
            "/organizations/bossaqua",
            "/parts/proprietary",  # Assuming proprietary parts are BossAqua
            "/organizations?type=bossaqua",
            "/parts?is_proprietary=true"
        ]
    
    async def dispatch(self, request: Request, call_next):
        # Skip public image endpoints
        if request.url.path.startswith("/images") or request.url.path.startswith("/static"):
            return await call_next(request)
        
        # Check if this is a protected endpoint
        is_protected = any(
            request.url.path.startswith(endpoint) 
            for endpoint in self.protected_endpoints
        )
        
        if not is_protected:
            return await call_next(request)
        
        # Get current user from request state (set by auth middleware)
        current_user = getattr(request.state, "current_user", None)
        
        if not current_user:
            # Let auth middleware handle authentication
            return await call_next(request)
        
        # Create audit context
        audit_context = AuditContext(current_user, request)
        
        try:
            db = next(get_db())
            
            # Enhanced BossAqua access control
            if self.is_bossaqua_endpoint(request.url.path, request.query_params):
                if not EnhancedBossAquaAccessControl.validate_bossaqua_access(
                    current_user, request.method, audit_context, db
                ):
                    raise OrganizationalIsolationError(
                        f"Non-superadmin access to BossAqua data denied for user {current_user.id}"
                    )
            
            # Enhanced organizational isolation validation
            if self.requires_org_validation(request.url.path):
                await self.validate_organizational_access(request, current_user, db, audit_context)
            
        except OrganizationalIsolationError:
            raise
        except Exception as e:
            # Log error but don't block request
            audit_context.log_security_event(
                "ISOLATION_MIDDLEWARE_ERROR",
                "MEDIUM",
                f"Error in isolation middleware: {str(e)}",
                details={"error": str(e), "path": request.url.path}
            )
        finally:
            db.close()
        
        return await call_next(request)
    
    def is_bossaqua_endpoint(self, path: str, query_params) -> bool:
        """Enhanced check if endpoint is related to BossAqua data"""
        # Check path patterns
        if any(pattern in path.lower() for pattern in self.bossaqua_patterns):
            return True
        
        # Check query parameters
        query_string = str(query_params).lower()
        if "bossaqua" in query_string or "is_proprietary=true" in query_string:
            return True
        
        return False
    
    def requires_org_validation(self, path: str) -> bool:
        """Check if endpoint requires organizational validation"""
        # Most protected endpoints require validation
        return any(path.startswith(endpoint) for endpoint in self.protected_endpoints)
    
    async def validate_organizational_access(self, request: Request, current_user: User, 
                                           db: Session, audit_context: AuditContext):
        """Validate organizational access for the request"""
        # Extract organization context from request
        org_id = None
        
        # Try to extract organization ID from path parameters
        path_parts = request.url.path.strip("/").split("/")
        if len(path_parts) >= 3 and path_parts[1] == "organizations":
            try:
                org_id = uuid.UUID(path_parts[2])
            except ValueError:
                pass
        
        # If we have an organization ID, validate access
        if org_id:
            validation_result = EnhancedOrganizationalDataFilter.validate_organization_access(
                current_user, org_id, db, audit_context
            )
            
            if not validation_result["allowed"]:
                raise OrganizationalIsolationError(
                    f"Access denied to organization {org_id}: {validation_result['reason']}"
                )


def get_current_user_with_audit(
    credentials: HTTPAuthorizationCredentials,
    db: Session,
    request: Request
) -> User:
    """Enhanced get_current_user that includes comprehensive audit logging"""
    from .auth import get_current_user_object
    
    # Get user using existing auth logic
    user = get_current_user_object(credentials.credentials, db)
    
    # Store user in request state for middleware access
    request.state.current_user = user
    
    # Create audit context and log authentication event
    audit_context = AuditContext(user, request)
    audit_context.log_access(
        "AUTHENTICATION",
        user.id,
        "TOKEN_VALIDATION_SUCCESS",
        details={
            "user_role": user.role.value if hasattr(user.role, 'value') else str(user.role),
            "organization_id": str(user.organization_id)
        },
        db=db
    )
    
    return user