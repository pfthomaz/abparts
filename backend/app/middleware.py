# backend/app/middleware.py

import time
import uuid
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import json

from fastapi import Request, Response, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
import redis

from .auth import get_current_user_from_token, TokenData
from .permissions import permission_checker, audit_logger, ResourceType, PermissionType

logger = logging.getLogger(__name__)

# --- Security Headers Middleware ---

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Middleware to add security headers to all responses."""
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
    
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        # Add security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        # More permissive CSP for Swagger UI
        if request.url.path.startswith("/docs") or request.url.path.startswith("/redoc"):
            response.headers["Content-Security-Policy"] = "default-src 'self' cdn.jsdelivr.net; img-src 'self' data:; style-src 'self' 'unsafe-inline' cdn.jsdelivr.net; script-src 'self' 'unsafe-inline' 'unsafe-eval' cdn.jsdelivr.net"
        else:
            response.headers["Content-Security-Policy"] = "default-src 'self'"
        
        # Remove server header for security
        if "server" in response.headers:
            del response.headers["server"]
        
        return response

# --- Rate Limiting Middleware ---

class RateLimitingMiddleware(BaseHTTPMiddleware):
    """Middleware for rate limiting requests per user."""
    
    def __init__(self, app: ASGIApp, redis_client: Optional[redis.Redis] = None):
        super().__init__(app)
        self.redis_client = redis_client
        self.default_rate_limit = 100  # requests per minute
        self.admin_rate_limit = 200    # higher limit for admins
        self.window_size = 60          # 1 minute window
    
    def _get_rate_limit_key(self, identifier: str) -> str:
        """Generate Redis key for rate limiting."""
        return f"rate_limit:{identifier}:{int(time.time() // self.window_size)}"
    
    def _get_user_rate_limit(self, user: TokenData) -> int:
        """Get rate limit based on user role."""
        if user.role in ["admin", "super_admin"]:
            return self.admin_rate_limit
        return self.default_rate_limit
    
    async def dispatch(self, request: Request, call_next):
        # Skip rate limiting for health checks and static files
        if request.url.path in ["/health", "/"] or request.url.path.startswith("/static"):
            return await call_next(request)
        
        # Skip if Redis is not available
        if not self.redis_client:
            return await call_next(request)
        
        try:
            # Try to get user from token
            user = None
            auth_header = request.headers.get("Authorization")
            if auth_header and auth_header.startswith("Bearer "):
                token = auth_header.split(" ")[1]
                try:
                    user = await get_current_user_from_token(token)
                except:
                    pass  # Continue with IP-based rate limiting
            
            # Determine identifier and rate limit
            if user:
                identifier = f"user:{user.user_id}"
                rate_limit = self._get_user_rate_limit(user)
            else:
                # Use IP address for unauthenticated requests
                client_ip = request.client.host if request.client else "unknown"
                identifier = f"ip:{client_ip}"
                rate_limit = self.default_rate_limit // 2  # Lower limit for unauthenticated
            
            # Check rate limit
            rate_key = self._get_rate_limit_key(identifier)
            current_requests = self.redis_client.get(rate_key)
            
            if current_requests is None:
                # First request in this window
                self.redis_client.setex(rate_key, self.window_size, 1)
                current_count = 1
            else:
                current_count = int(current_requests)
                if current_count >= rate_limit:
                    # Rate limit exceeded
                    logger.warning(f"Rate limit exceeded for {identifier}: {current_count}/{rate_limit}")
                    return JSONResponse(
                        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                        content={
                            "detail": "Rate limit exceeded. Please try again later.",
                            "retry_after": self.window_size
                        }
                    )
                else:
                    # Increment counter
                    self.redis_client.incr(rate_key)
                    current_count += 1
            
            # Add rate limit headers to response
            response = await call_next(request)
            response.headers["X-RateLimit-Limit"] = str(rate_limit)
            response.headers["X-RateLimit-Remaining"] = str(max(0, rate_limit - current_count))
            response.headers["X-RateLimit-Reset"] = str(int(time.time()) + self.window_size)
            
            return response
            
        except Exception as e:
            logger.error(f"Rate limiting error: {e}")
            # Continue without rate limiting if there's an error
            return await call_next(request)

# --- Request Logging Middleware ---

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for logging requests and responses."""
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
    
    async def dispatch(self, request: Request, call_next):
        # Generate request ID
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        
        # Log request
        start_time = time.time()
        client_ip = request.client.host if request.client else "unknown"
        
        logger.info(f"Request {request_id}: {request.method} {request.url} from {client_ip}")
        
        try:
            response = await call_next(request)
            
            # Log response
            process_time = time.time() - start_time
            logger.info(f"Response {request_id}: {response.status_code} in {process_time:.3f}s")
            
            # Add request ID to response headers
            response.headers["X-Request-ID"] = request_id
            
            return response
            
        except Exception as e:
            process_time = time.time() - start_time
            logger.error(f"Request {request_id} failed after {process_time:.3f}s: {str(e)}")
            raise

# --- Permission Enforcement Middleware ---

class PermissionEnforcementMiddleware(BaseHTTPMiddleware):
    """Middleware for automatic permission enforcement and audit logging."""
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
        # Define endpoints that don't require permission checks
        self.public_endpoints = {
            "/",
            "/health",
            "/token",
            "/docs",
            "/openapi.json",
            "/redoc"
        }
        # Define endpoints that require authentication but have custom permission logic
        self.custom_permission_endpoints = {
            "/users/me/",
            "/users/profile",
            "/users/change-password"
        }
    
    def _should_check_permissions(self, path: str) -> bool:
        """Determine if endpoint requires permission checking."""
        # Skip public endpoints
        if path in self.public_endpoints:
            return False
        
        # Skip static files
        if path.startswith("/static"):
            return False
        
        # Skip Swagger UI files
        if path.startswith("/docs/") or path == "/docs" or path == "/openapi.json" or path == "/redoc" or path.startswith("/redoc/"):
            return False
        
        # Skip custom permission endpoints (they handle permissions internally)
        if path in self.custom_permission_endpoints:
            return False
        
        return True
    
    def _extract_resource_from_path(self, path: str, method: str) -> Optional[ResourceType]:
        """Extract resource type from request path."""
        path_parts = path.strip("/").split("/")
        
        if not path_parts or not path_parts[0]:
            return None
        
        resource_mapping = {
            "organizations": ResourceType.ORGANIZATION,
            "users": ResourceType.USER,
            "warehouses": ResourceType.WAREHOUSE,
            "parts": ResourceType.PART,
            "inventory": ResourceType.INVENTORY,
            "machines": ResourceType.MACHINE,
            "transactions": ResourceType.TRANSACTION,
            "supplier_orders": ResourceType.ORDER,
            "customer_orders": ResourceType.ORDER,
            "dashboard": ResourceType.DASHBOARD,
            "audit": ResourceType.AUDIT_LOG
        }
        
        return resource_mapping.get(path_parts[0])
    
    def _extract_permission_from_method(self, method: str) -> PermissionType:
        """Extract permission type from HTTP method."""
        method_mapping = {
            "GET": PermissionType.READ,
            "POST": PermissionType.WRITE,
            "PUT": PermissionType.WRITE,
            "PATCH": PermissionType.WRITE,
            "DELETE": PermissionType.DELETE
        }
        
        return method_mapping.get(method, PermissionType.READ)
    
    async def dispatch(self, request: Request, call_next):
        path = request.url.path
        method = request.method
        
        # Skip permission checking for certain endpoints
        if not self._should_check_permissions(path):
            return await call_next(request)
        
        try:
            # Get current user
            auth_header = request.headers.get("Authorization")
            if not auth_header or not auth_header.startswith("Bearer "):
                # No authentication provided for protected endpoint
                return JSONResponse(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    content={"detail": "Authentication required"}
                )
            
            token = auth_header.split(" ")[1]
            user = await get_current_user_from_token(token)
            
            # Extract resource and permission from request
            resource = self._extract_resource_from_path(path, method)
            permission = self._extract_permission_from_method(method)
            
            # If we can't determine resource type, allow the request to proceed
            # (the endpoint will handle its own permission checking)
            if not resource:
                return await call_next(request)
            
            # Check permissions
            context = {"path": path, "method": method}
            has_permission = permission_checker.check_permission(user, resource, permission, context)
            
            if not has_permission:
                # Log permission denied
                audit_logger.log_permission_denied(user, resource, permission, context, request)
                
                return JSONResponse(
                    status_code=status.HTTP_403_FORBIDDEN,
                    content={
                        "detail": f"Insufficient permissions for {resource.value}:{permission.value}",
                        "resource": resource.value,
                        "permission": permission.value
                    }
                )
            
            # Log sensitive operations
            if resource in [ResourceType.USER, ResourceType.ORGANIZATION] and permission in [PermissionType.WRITE, PermissionType.DELETE]:
                audit_logger.log_permission_granted(user, resource, permission, context)
            
            # Add user context to request state
            request.state.current_user = user
            
            return await call_next(request)
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Permission enforcement error: {e}")
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={"detail": "Internal server error during permission check"}
            )

# --- Session Management Middleware ---

class SessionManagementMiddleware(BaseHTTPMiddleware):
    """Middleware for session management and cleanup."""
    
    def __init__(self, app: ASGIApp, redis_client: Optional[redis.Redis] = None):
        super().__init__(app)
        self.redis_client = redis_client
        self.session_timeout = 8 * 60 * 60  # 8 hours in seconds
    
    def _get_session_key(self, user_id: uuid.UUID) -> str:
        """Generate Redis key for user session."""
        return f"session:{user_id}"
    
    def _get_active_sessions_key(self, user_id: uuid.UUID) -> str:
        """Generate Redis key for tracking active sessions."""
        return f"active_sessions:{user_id}"
    
    async def dispatch(self, request: Request, call_next):
        # Skip session management for public endpoints
        if request.url.path in ["/", "/health", "/token"] or request.url.path.startswith("/static"):
            return await call_next(request)
        
        # Skip if Redis is not available
        if not self.redis_client:
            return await call_next(request)
        
        try:
            # Get user from request state (set by permission middleware)
            user = getattr(request.state, "current_user", None)
            
            if user:
                # Update session activity
                session_key = self._get_session_key(user.user_id)
                session_data = {
                    "user_id": str(user.user_id),
                    "username": user.username,
                    "last_activity": datetime.utcnow().isoformat(),
                    "ip_address": request.client.host if request.client else "unknown",
                    "user_agent": request.headers.get("user-agent", "unknown")
                }
                
                # Store session with expiration
                self.redis_client.setex(
                    session_key,
                    self.session_timeout,
                    json.dumps(session_data)
                )
                
                # Track active session
                active_sessions_key = self._get_active_sessions_key(user.user_id)
                self.redis_client.sadd(active_sessions_key, session_key)
                self.redis_client.expire(active_sessions_key, self.session_timeout)
            
            return await call_next(request)
            
        except Exception as e:
            logger.error(f"Session management error: {e}")
            return await call_next(request)

# --- Error Handling Middleware ---

class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    """Middleware for centralized error handling and logging."""
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
    
    async def dispatch(self, request: Request, call_next):
        try:
            return await call_next(request)
        except HTTPException:
            # Re-raise HTTP exceptions (they're handled by FastAPI)
            raise
        except Exception as e:
            # Log unexpected errors
            request_id = getattr(request.state, "request_id", "unknown")
            logger.error(f"Unhandled error in request {request_id}: {str(e)}", exc_info=True)
            
            # Return generic error response
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={
                    "detail": "Internal server error",
                    "request_id": request_id
                }
            )

# --- Middleware Factory Functions ---

def create_security_middleware(app: ASGIApp) -> ASGIApp:
    """Create and configure security middleware stack."""
    # Add middleware in reverse order (last added is executed first)
    app = ErrorHandlingMiddleware(app)
    app = RequestLoggingMiddleware(app)
    app = SecurityHeadersMiddleware(app)
    return app

def create_permission_middleware(app: ASGIApp, redis_client: Optional[redis.Redis] = None) -> ASGIApp:
    """Create and configure permission and session middleware."""
    if redis_client:
        app = SessionManagementMiddleware(app, redis_client)
        app = RateLimitingMiddleware(app, redis_client)
    app = PermissionEnforcementMiddleware(app)
    return app

# --- Utility Functions ---

def clear_user_sessions(user_id: uuid.UUID, redis_client: redis.Redis):
    """Clear all active sessions for a user."""
    try:
        active_sessions_key = f"active_sessions:{user_id}"
        session_keys = redis_client.smembers(active_sessions_key)
        
        if session_keys:
            # Delete all session keys
            redis_client.delete(*session_keys)
            # Clear the active sessions set
            redis_client.delete(active_sessions_key)
            
        logger.info(f"Cleared {len(session_keys)} sessions for user {user_id}")
        
    except Exception as e:
        logger.error(f"Error clearing sessions for user {user_id}: {e}")

def get_active_sessions(user_id: uuid.UUID, redis_client: redis.Redis) -> List[Dict[str, Any]]:
    """Get list of active sessions for a user."""
    try:
        active_sessions_key = f"active_sessions:{user_id}"
        session_keys = redis_client.smembers(active_sessions_key)
        
        sessions = []
        for session_key in session_keys:
            session_data = redis_client.get(session_key)
            if session_data:
                try:
                    sessions.append(json.loads(session_data))
                except json.JSONDecodeError:
                    # Remove invalid session
                    redis_client.delete(session_key)
                    redis_client.srem(active_sessions_key, session_key)
        
        return sessions
        
    except Exception as e:
        logger.error(f"Error getting active sessions for user {user_id}: {e}")
        return []