# backend/app/main.py

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles # New: Import StaticFiles
import os
import logging
from sqlalchemy.orm import Session
import redis

# Import database configuration
from .database import engine, Base, get_db

# Import models and schemas for type hinting in auth endpoints if needed directly in main.py
from . import models, schemas

# Import routers directly from their files, aliasing them to avoid naming conflicts
from .routers.organizations import router as organizations_router
from .routers.users import router as users_router
from .routers.parts import router as parts_router
from .routers.inventory import router as inventory_router
from .routers.supplier_orders import router as supplier_orders_router
from .routers.supplier_order_items import router as supplier_order_items_router
from .routers.customer_orders import router as customer_orders_router
from .routers.customer_order_items import router as customer_order_items_router
from .routers.part_usage import router as part_usage_router
from .auth import login_for_access_token, read_users_me, TokenData


# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- FastAPI App Initialization ---
app = FastAPI(
    title="ABParts API",
    description="API for managing AutoBoss parts inventory and customer stock.",
    version="0.1.0",
)

# --- CORS Configuration ---
origins = [
    "http://localhost",
    "http://localhost:3000", # Your React frontend development server
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
app.include_router(parts_router, prefix="/parts", tags=["Parts"]) # The /parts router now contains /upload-image as well
app.include_router(inventory_router, prefix="/inventory", tags=["Inventory"])
app.include_router(supplier_orders_router, prefix="/supplier_orders", tags=["Supplier Orders"])
app.include_router(supplier_order_items_router, prefix="/supplier_order_items", tags=["Supplier Order Items"])
app.include_router(customer_orders_router, prefix="/customer_orders", tags=["Customer Orders"])
app.include_router(customer_order_items_router, prefix="/customer_order_items", tags=["Customer Order Items"])
app.include_router(part_usage_router, prefix="/part_usage", tags=["Part Usage"])

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
        db.execute("SELECT 1")
        db_status = "connected"
    except Exception as e:
        logger.error(f"Database connection failed: {e}")

    return {
        "status": "healthy" if db_status == "connected" and redis_status == "connected" else "unhealthy",
        "database": db_status,
        "redis": redis_status,
    }


# --- Database Table Creation on Startup ---
@app.on_event("startup")
def startup_event():
    logger.info("Application startup event triggered.")
    logger.info("Attempting to create database tables if they don't exist...")
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables checked/created successfully.")
    except Exception as e:
        logger.error(f"Error creating database tables on startup: {e}")

