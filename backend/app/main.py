# backend/app/main.py

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
import os
import logging
from sqlalchemy.orm import Session # Import Session for health check dependency

# Import database configuration
from .database import engine, Base, get_db

# Import models for type hinting in auth endpoints if needed directly in main.py
from . import models, schemas # Import schemas for UserResponse

# Import routers
from .routers import organizations, users # We'll add more routers later
from .auth import login_for_access_token, read_users_me, TokenData # Import TokenData if used in main.py directly


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

# --- Include Routers ---
app.include_router(organizations.router, prefix="/organizations", tags=["Organizations"])
app.include_router(users.router, prefix="/users", tags=["Users"])
# Add other routers here as you create them:
# app.include_router(parts.router, prefix="/parts", tags=["Parts"])
# app.include_router(inventory.router, prefix="/inventory", tags=["Inventory"])
# app.include_router(supplier_orders.router, prefix="/supplier_orders", tags=["Supplier Orders"])
# app.include_router(customer_orders.router, prefix="/customer_orders", tags=["Customer Orders"])
# app.include_router(part_usage.router, prefix="/part_usage", tags=["Part Usage"])

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
    # Redis client is in database.py but we need it here, so let's move redis_client
    # to database.py and access it from there if needed for health check.
    # For now, let's keep redis_client in main.py, as it's directly used here.
    # Alternatively, create a get_redis_client dependency in database.py
    redis_url = os.getenv("REDIS_URL")
    if not redis_url:
        logger.error("REDIS_URL environment variable is not set.")
        raise ValueError("REDIS_URL environment variable is not set.")
    
    # Re-initialize redis_client if it's not available or if this is the first call
    # This is a bit redundant if it's already initialized globally, but safe for health check
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

