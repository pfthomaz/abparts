# backend/app/main.py

from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles # New: Import StaticFiles
from fastapi.encoders import jsonable_encoder
import os
import logging
import time
import json
import uuid
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import text
import redis

# Import database configuration
from .database import engine, Base, get_db

# Import CORS configuration
from .cors_config import get_cors_origins, get_cors_settings

# Import models and schemas for type hinting in auth endpoints if needed directly in main.py
from . import models, schemas

# Import routers directly from their files, aliasing them to avoid naming conflicts
from .routers.organizations import router as organizations_router
from .routers.users import router as users_router
from .routers.parts import router as parts_router
from .routers.warehouses import router as warehouses_router
from .routers.inventory import router as inventory_router
from .routers.inventory_reports import router as inventory_reports_router # New: Import inventory_reports_router
from .routers.supplier_orders import router as supplier_orders_router
from .routers.supplier_order_items import router as supplier_order_items_router
from .routers.customer_orders import router as customer_orders_router
from .routers.customer_order_items import router as customer_order_items_router
from .routers.part_usage import router as part_usage_router
from .routers.machines import router as machines_router
from .routers.predictive_maintenance import router as predictive_maintenance_router
from .routers.part_order import router as part_order_router
from .routers.stock_adjustments import router as stock_adjustments_router # New: Import stock_adjustments_router
# from .routers.stocktake import router as stocktake_router  # Replaced by inventory_workflow_router
from .routers.dashboard import router as dashboard_router # New: Import dashboard router
from .routers.sessions import router as sessions_router # New: Import sessions router
from .routers.transactions import router as transactions_router # New: Import transactions router
from .routers.inventory_workflow import router as inventory_workflow_router # New: Import inventory workflow router
from .routers.monitoring import router as monitoring_router # New: Import monitoring router
from .auth import login_for_access_token, read_users_me, TokenData


# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from fastapi.openapi.docs import get_swagger_ui_html, get_redoc_html
from fastapi.responses import HTMLResponse

# Custom JSON encoder for datetime and UUID objects
class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        elif isinstance(obj, uuid.UUID):
            return str(obj)
        return super().default(obj)

# --- FastAPI App Initialization ---
app = FastAPI(
    title="ABParts API",
    description="API for managing AutoBoss parts inventory and customer stock.",
    version="0.1.0",
    swagger_ui_parameters={
        "persistAuthorization": True,
        "displayRequestDuration": True,
        "docExpansion": "none",
        "filter": True,
        "tryItOutEnabled": True
    },
    docs_url=None,  # Disable automatic docs
    redoc_url=None,  # Disable automatic redoc
)

# --- CORS Configuration ---
# Get dynamic CORS configuration from environment-aware module
cors_origins = get_cors_origins()
cors_settings = get_cors_settings()

# Import CORS error handling
from .cors_error_handler import CORSLoggingMiddleware, log_cors_request, log_cors_response

# Log CORS configuration on startup
logger.info(f"CORS configuration loaded:")
logger.info(f"  Allowed origins: {cors_origins}")
logger.info(f"  Allow credentials: {cors_settings.get('allow_credentials', False)}")
logger.info(f"  Allowed methods: {cors_settings.get('allow_methods', [])}")
logger.info(f"  Allowed headers: {cors_settings.get('allow_headers', [])}")

# CORS middleware will be added after other middleware to ensure it runs first

# Set up CORS violation monitoring
cors_violations = 0
cors_requests = 0

# Add CORS monitoring middleware
@app.middleware("http")
async def cors_monitoring_middleware(request: Request, call_next):
    """Monitor and log CORS requests and violations"""
    global cors_requests, cors_violations
    
    # Track CORS requests
    origin = request.headers.get("Origin")
    if origin:
        cors_requests += 1
        log_cors_request(request, origin)
        
        # Check if origin is allowed
        if origin not in cors_origins and "*" not in cors_origins:
            cors_violations += 1
            logger.warning(f"CORS violation detected: Origin '{origin}' not in allowed origins")
    
    # Process the request
    response = await call_next(request)
    
    # Log CORS response if applicable
    if origin:
        log_cors_response(response, origin)
    
    return response

# --- Add Security and Permission Middleware ---
from .middleware import (
    SecurityHeadersMiddleware, RequestLoggingMiddleware, ErrorHandlingMiddleware,
    PermissionEnforcementMiddleware, RateLimitingMiddleware, SessionManagementMiddleware,
    CORSViolationHandlerMiddleware
)
from .monitoring import get_monitoring_system, track_request_middleware
import os
import redis

# Initialize Redis client for middleware
redis_url = os.getenv("REDIS_URL")
redis_client = None
if redis_url:
    try:
        redis_client = redis.StrictRedis.from_url(redis_url, decode_responses=True)
        redis_client.ping()  # Test connection
        logger.info("Redis connection established for middleware")
    except Exception as e:
        logger.warning(f"Redis connection failed, middleware will work without caching: {e}")
        redis_client = None

# Apply middleware stack (in reverse order - last added is executed first)
app.add_middleware(ErrorHandlingMiddleware)
app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(SecurityHeadersMiddleware)
# Add HTTPS redirect middleware
from .middleware import HTTPSRedirectMiddleware
app.add_middleware(HTTPSRedirectMiddleware)
# Add CORS violation handler before permission middleware
app.add_middleware(
    CORSViolationHandlerMiddleware,
    exclude_paths=["/health", "/", "/docs", "/redoc", "/openapi.json"],
    exclude_prefixes=["/static/"]
)
app.add_middleware(PermissionEnforcementMiddleware)
if redis_client:
    app.add_middleware(SessionManagementMiddleware, redis_client=redis_client)
    app.add_middleware(RateLimitingMiddleware, redis_client=redis_client)

# Add CORS middleware LAST so it executes FIRST (middleware runs in reverse order)
# Use enhanced CORS logging middleware instead of standard CORSMiddleware
app.add_middleware(
    CORSLoggingMiddleware,
    allow_origins=cors_origins,
    allow_credentials=cors_settings.get("allow_credentials", True),
    allow_methods=cors_settings.get("allow_methods", ["*"]),
    allow_headers=cors_settings.get("allow_headers", ["*"]),
    expose_headers=["X-Process-Time", "X-Request-ID"],
    max_age=cors_settings.get("max_age", 600),
)

# Add request tracking middleware for monitoring
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    request.state.elapsed_time = process_time
    track_request_middleware(request, response)
    return response

# --- Mount Static Files Directory ---
# This makes files in the UPLOAD_DIRECTORY accessible via /static/images/your_image.jpg
# IMPORTANT: In production, consider serving static files via a CDN or dedicated static file server.
app.mount("/static/images", StaticFiles(directory="/app/static/images"), name="static_images")
# Ensure the directory exists when the container starts
# This will create the directory if it doesn't exist within the container
# Also consider adding this as a Docker volume in docker-compose.yml for persistence
# in local dev.
UPLOAD_DIRECTORY = "/app/static/images"
os.makedirs(UPLOAD_DIRECTORY, exist_ok=True)


# --- Include Routers ---
app.include_router(organizations_router, prefix="/organizations", tags=["Organizations"])
app.include_router(users_router, prefix="/users", tags=["Users"])
app.include_router(parts_router, prefix="/parts", tags=["Parts"])
app.include_router(warehouses_router, prefix="/warehouses", tags=["Warehouses"])
app.include_router(inventory_router, prefix="/inventory", tags=["Inventory"])
app.include_router(inventory_reports_router, prefix="/inventory-reports", tags=["Inventory Reports"])
app.include_router(supplier_orders_router, prefix="/supplier_orders", tags=["Supplier Orders"])
app.include_router(supplier_order_items_router, prefix="/supplier_order_items", tags=["Supplier Order Items"])
app.include_router(customer_orders_router, prefix="/customer_orders", tags=["Customer Orders"])
app.include_router(customer_order_items_router, prefix="/customer_order_items", tags=["Customer Order Items"])
app.include_router(part_usage_router, prefix="/part_usage", tags=["Part Usage"])
app.include_router(machines_router, prefix="/machines", tags=["Machines"])
app.include_router(predictive_maintenance_router, prefix="/predictive-maintenance", tags=["Predictive Maintenance"])
app.include_router(part_order_router, prefix="/part-orders", tags=["Part Orders"])
app.include_router(stock_adjustments_router, prefix="/stock_adjustments", tags=["Stock Adjustments"])
# app.include_router(stocktake_router, prefix="/stocktake", tags=["Stocktake"])  # Replaced by inventory_workflow_router
app.include_router(dashboard_router, prefix="/dashboard", tags=["Dashboard"])
app.include_router(sessions_router, prefix="/sessions", tags=["Sessions"])
app.include_router(transactions_router, prefix="/transactions", tags=["Transactions"])
app.include_router(inventory_workflow_router, tags=["Inventory Workflows"])
app.include_router(monitoring_router, prefix="/monitoring", tags=["Monitoring"])

# --- Authentication Endpoints (kept in main for simplicity of login flow) ---
app.post("/token", tags=["Authentication"])(login_for_access_token)
app.get("/users/me/", response_model=schemas.UserResponse, tags=["Authentication"])(read_users_me)


# --- Root and Health Check Endpoints ---
@app.get("/")
async def read_root():
    return {"message": "Welcome to ABParts API!"}

@app.get("/health")
async def health_check(db: Session = Depends(get_db)):
    db_status = "unreachable"
    redis_status = "unreachable"

    redis_url = os.getenv("REDIS_URL")
    if not redis_url:
        logger.error("REDIS_URL environment variable is not set.")
        raise ValueError("REDIS_URL environment variable is not set.")
    
    try:
        current_redis_client = redis.StrictRedis.from_url(redis_url, decode_responses=True)
        current_redis_client.ping()
        redis_status = "connected"
    except Exception as e:
        logger.error(f"Redis connection failed: {e}")
        redis_status = "unreachable"

    try:
        db.execute(text("SELECT 1"))
        db_status = "connected"
    except Exception as e:
        logger.error(f"Database connection failed: {e}")

    return {
        "status": "healthy" if db_status == "connected" and redis_status == "connected" else "unhealthy",
        "database": db_status,
        "redis": redis_status,
    }


# --- Database Table Creation on Startup ---
# Commented out to allow Alembic migrations to handle schema creation
# @app.on_event("startup")
def startup_event():
    logger.info("Application startup event triggered.")
    # Initialize monitoring system
    from .database import SessionLocal
    monitoring = get_monitoring_system(SessionLocal, redis_url)
    logger.info("Monitoring system initialized.")
    
    # Uncomment to create tables on startup (not recommended for production)
    # try:
    #     Base.metadata.create_all(bind=engine)
    #     logger.info("Database tables checked/created successfully.")
    # except Exception as e:
    #     logger.error(f"Error creating database tables on startup: {e}")
# --- Custom Swagger UI and ReDoc routes ---
@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url="/openapi.json",
        title=f"{app.title} - Swagger UI",
        oauth2_redirect_url="/docs/oauth2-redirect",
        swagger_js_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-bundle.js",
        swagger_css_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui.css",
        swagger_favicon_url="https://fastapi.tiangolo.com/img/favicon.png",
        swagger_ui_parameters=app.swagger_ui_parameters,
    )

@app.get("/redoc", include_in_schema=False)
async def redoc_html():
    return get_redoc_html(
        openapi_url="/openapi.json",
        title=f"{app.title} - ReDoc",
        redoc_js_url="https://cdn.jsdelivr.net/npm/redoc@next/bundles/redoc.standalone.js",
        redoc_favicon_url="https://fastapi.tiangolo.com/img/favicon.png",
    )

@app.get("/docs/oauth2-redirect", include_in_schema=False)
async def oauth2_redirect():
    return HTMLResponse("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>OAuth2 Redirect</title>
    </head>
    <body>
        <script>
            window.opener.swaggerUIRedirectOauth2(window.location.href.split('#')[1]);
            window.close();
        </script>
    </body>
    </html>
    """)