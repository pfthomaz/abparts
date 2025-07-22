"""
CORS Error Handler Module

Provides comprehensive error handling and logging for CORS-related issues.
"""

import json
from typing import Dict, Any, List, Optional
import logging
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.cors import CORSMiddleware
from starlette.types import ASGIApp, Receive, Scope, Send

# Configure logger
logger = logging.getLogger(__name__)

# CORS error codes
CORS_ERROR_ORIGIN_NOT_ALLOWED = "CORS_ORIGIN_NOT_ALLOWED"
CORS_ERROR_MISSING_ORIGIN = "CORS_MISSING_ORIGIN"
CORS_ERROR_INVALID_METHOD = "CORS_METHOD_NOT_ALLOWED"
CORS_ERROR_INVALID_HEADER = "CORS_HEADER_NOT_ALLOWED"
CORS_ERROR_PREFLIGHT_FAILURE = "CORS_PREFLIGHT_FAILURE"

class CORSErrorResponse:
    """Helper class to generate consistent CORS error responses"""
    
    @staticmethod
    def origin_not_allowed(origin: str, allowed_origins: List[str]) -> Dict[str, Any]:
        """Generate error response for disallowed origin"""
        logger.warning(f"CORS violation: Origin '{origin}' not in allowed origins {allowed_origins}")
        return {
            "detail": f"CORS policy violation: Origin '{origin}' not allowed",
            "error_code": CORS_ERROR_ORIGIN_NOT_ALLOWED,
            "allowed_origins": allowed_origins
        }
    
    @staticmethod
    def missing_origin() -> Dict[str, Any]:
        """Generate error response for missing origin header"""
        logger.warning("CORS violation: Missing Origin header")
        return {
            "detail": "CORS policy violation: Missing Origin header",
            "error_code": CORS_ERROR_MISSING_ORIGIN
        }
    
    @staticmethod
    def method_not_allowed(method: str, allowed_methods: List[str]) -> Dict[str, Any]:
        """Generate error response for disallowed method"""
        logger.warning(f"CORS violation: Method '{method}' not in allowed methods {allowed_methods}")
        return {
            "detail": f"CORS policy violation: Method '{method}' not allowed",
            "error_code": CORS_ERROR_INVALID_METHOD,
            "allowed_methods": allowed_methods
        }
    
    @staticmethod
    def header_not_allowed(header: str, allowed_headers: List[str]) -> Dict[str, Any]:
        """Generate error response for disallowed header"""
        logger.warning(f"CORS violation: Header '{header}' not in allowed headers {allowed_headers}")
        return {
            "detail": f"CORS policy violation: Header '{header}' not allowed",
            "error_code": CORS_ERROR_INVALID_HEADER,
            "allowed_headers": allowed_headers
        }
    
    @staticmethod
    def preflight_failure(reason: str) -> Dict[str, Any]:
        """Generate error response for preflight failure"""
        logger.warning(f"CORS preflight failure: {reason}")
        return {
            "detail": f"CORS preflight failure: {reason}",
            "error_code": CORS_ERROR_PREFLIGHT_FAILURE
        }

class CORSLoggingMiddleware:
    """
    Middleware for logging CORS requests and violations.
    
    This middleware wraps the standard CORSMiddleware to add detailed
    logging for CORS requests, responses, and violations.
    """
    
    def __init__(
        self,
        app: ASGIApp,
        allow_origins: List[str] = None,
        allow_methods: List[str] = None,
        allow_headers: List[str] = None,
        allow_credentials: bool = False,
        allow_origin_regex: str = None,
        expose_headers: List[str] = None,
        max_age: int = 600,
    ) -> None:
        """Initialize the middleware with CORS settings"""
        # Create the standard CORSMiddleware
        self.cors_middleware = CORSMiddleware(
            app=app,
            allow_origins=allow_origins or [],
            allow_methods=allow_methods or ["GET"],
            allow_headers=allow_headers or [],
            allow_credentials=allow_credentials,
            allow_origin_regex=allow_origin_regex,
            expose_headers=expose_headers or [],
            max_age=max_age,
        )
        
        # Store configuration for logging
        self.allow_origins = allow_origins or []
        self.allow_methods = allow_methods or ["GET"]
        self.allow_headers = allow_headers or []
        self.allow_credentials = allow_credentials
        self.allow_origin_regex = allow_origin_regex
        
        # Log initialization
        logger.info(f"CORSLoggingMiddleware initialized with:")
        logger.info(f"  - allow_origins: {self.allow_origins}")
        logger.info(f"  - allow_methods: {self.allow_methods}")
        logger.info(f"  - allow_credentials: {self.allow_credentials}")
    
    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        """Process the request and add logging"""
        if scope["type"] != "http":
            # Pass through non-HTTP requests
            await self.cors_middleware(scope, receive, send)
            return
        
        # Extract request details for logging
        method = scope.get("method", "")
        headers = dict(scope.get("headers", []))
        path = scope.get("path", "")
        
        # Get origin from headers
        origin_bytes = headers.get(b"origin")
        origin = origin_bytes.decode("latin1") if origin_bytes else None
        
        # Log the CORS request
        if origin:
            logger.info(f"CORS request: {method} {path} from origin '{origin}'")
            
            # Check if origin is allowed
            is_allowed = origin in self.allow_origins or "*" in self.allow_origins
            if not is_allowed and self.allow_origin_regex:
                # TODO: Check regex if needed
                pass
            
            if not is_allowed:
                logger.warning(f"CORS violation: Origin '{origin}' not allowed for {method} {path}")
        
        # Create a wrapper for the send function to log responses
        async def send_wrapper(message):
            if message["type"] == "http.response.start":
                # Log response headers for CORS requests
                if origin:
                    status = message.get("status", 0)
                    headers = dict(message.get("headers", []))
                    
                    cors_origin = headers.get(b"access-control-allow-origin")
                    cors_origin_str = cors_origin.decode("latin1") if cors_origin else None
                    
                    if cors_origin_str:
                        logger.info(f"CORS response: {status} to '{origin}' with Access-Control-Allow-Origin: {cors_origin_str}")
                    else:
                        logger.warning(f"CORS response: {status} to '{origin}' without Access-Control-Allow-Origin header")
            
            # Pass through to the original send function
            await send(message)
        
        # Process the request with the wrapped send function
        await self.cors_middleware(scope, receive, send_wrapper)

def log_cors_request(request: Request, origin: Optional[str] = None) -> None:
    """Log details about a CORS request"""
    if not origin:
        origin = request.headers.get("Origin")
    
    if origin:
        logger.info(f"CORS request: {request.method} {request.url.path} from origin '{origin}'")
        logger.debug(f"CORS request headers: {dict(request.headers)}")

def log_cors_response(response: Response, origin: Optional[str] = None) -> None:
    """Log details about a CORS response"""
    if not origin:
        # This would be set from the request
        return
    
    cors_origin = response.headers.get("Access-Control-Allow-Origin")
    if cors_origin:
        logger.info(f"CORS response: {response.status_code} to '{origin}' with Access-Control-Allow-Origin: {cors_origin}")
    else:
        logger.warning(f"CORS response: {response.status_code} to '{origin}' without Access-Control-Allow-Origin header")

def create_cors_error_response(error_type: str, **kwargs) -> JSONResponse:
    """Create a standardized CORS error response"""
    if error_type == CORS_ERROR_ORIGIN_NOT_ALLOWED:
        content = CORSErrorResponse.origin_not_allowed(
            kwargs.get("origin", "unknown"),
            kwargs.get("allowed_origins", [])
        )
    elif error_type == CORS_ERROR_MISSING_ORIGIN:
        content = CORSErrorResponse.missing_origin()
    elif error_type == CORS_ERROR_INVALID_METHOD:
        content = CORSErrorResponse.method_not_allowed(
            kwargs.get("method", "unknown"),
            kwargs.get("allowed_methods", [])
        )
    elif error_type == CORS_ERROR_INVALID_HEADER:
        content = CORSErrorResponse.header_not_allowed(
            kwargs.get("header", "unknown"),
            kwargs.get("allowed_headers", [])
        )
    elif error_type == CORS_ERROR_PREFLIGHT_FAILURE:
        content = CORSErrorResponse.preflight_failure(
            kwargs.get("reason", "Unknown reason")
        )
    else:
        content = {"detail": "CORS policy violation", "error_code": "CORS_ERROR"}
    
    return JSONResponse(
        status_code=kwargs.get("status_code", 403),
        content=content
    )