# backend/app/main.py

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware # Import CORSMiddleware
from sqlalchemy import create_engine, Column, String, DateTime, Boolean, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.dialects.postgresql import UUID
import uuid
import os
import redis
from datetime import datetime
import logging

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
# Define allowed origins for your frontend. In development, this is often your React dev server.
# For production, replace '*' with your actual frontend domain(s).
origins = [
    "http://localhost",
    "http://localhost:3000", # Your React frontend development server
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"], # Allow all methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"], # Allow all headers
)

# --- Database Configuration ---
# Get database URL from environment variable
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    logger.error("DATABASE_URL environment variable is not set.")
    raise ValueError("DATABASE_URL environment variable is not set.")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- Redis Configuration ---
# Get Redis URL from environment variable
REDIS_URL = os.getenv("REDIS_URL")
if not REDIS_URL:
    logger.error("REDIS_URL environment variable is not set.")
    raise ValueError("REDIS_URL environment variable is not set.")

redis_client = redis.StrictRedis.from_url(REDIS_URL, decode_responses=True)

# --- SQLAlchemy Models (Basic Example for 'organizations' table) ---
# This is a simplified example. You would create models for all your tables.
class Organization(Base):
    __tablename__ = "organizations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), unique=True, nullable=False)
    type = Column(String(50), nullable=False)
    address = Column(String)
    contact_info = Column(String)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.now)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=datetime.now, onupdate=datetime.now)

# --- API Endpoints ---

@app.get("/")
async def read_root():
    """
    Root endpoint for the ABParts API.
    """
    return {"message": "Welcome to ABParts API!"}

@app.get("/health")
async def health_check(db: Session = Depends(get_db)):
    """
    Health check endpoint to verify database and Redis connectivity.
    """
    db_status = "unreachable"
    redis_status = "unreachable"

    try:
        # Test DB connection
        db.execute("SELECT 1")
        db_status = "connected"
    except Exception as e:
        logger.error(f"Database connection failed: {e}")

    try:
        # Test Redis connection
        redis_client.ping()
        redis_status = "connected"
    except Exception as e:
        logger.error(f"Redis connection failed: {e}")

    return {
        "status": "healthy" if db_status == "connected" and redis_status == "connected" else "unhealthy",
        "database": db_status,
        "redis": redis_status,
    }

@app.get("/organizations")
async def get_organizations(db: Session = Depends(get_db)):
    """
    Retrieve all organizations from the database.
    """
    try:
        organizations = db.query(Organization).all()
        return organizations
    except Exception as e:
        logger.error(f"Error fetching organizations: {e}")
        raise HTTPException(status_code=500, detail="Could not fetch organizations")

@app.post("/organizations")
async def create_organization(
    name: str,
    org_type: str, # Renamed to avoid conflict with Python's built-in type()
    address: str = None,
    contact_info: str = None,
    db: Session = Depends(get_db)
):
    """
    Create a new organization.
    """
    new_org = Organization(
        name=name,
        type=org_type,
        address=address,
        contact_info=contact_info
    )
    try:
        db.add(new_org)
        db.commit()
        db.refresh(new_org)
        return new_org
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating organization: {e}")
        raise HTTPException(status_code=400, detail="Error creating organization")

@app.get("/cache-test/{key}")
async def get_cache_value(key: str):
    """
    Get a value from Redis cache.
    """
    value = redis_client.get(key)
    if value:
        return {"key": key, "value": value, "source": "cache"}
    return {"key": key, "value": None, "source": "miss"}

@app.post("/cache-test/{key}")
async def set_cache_value(key: str, value: str):
    """
    Set a value in Redis cache.
    """
    redis_client.set(key, value, ex=60) # Set with 60 second expiration
    return {"key": key, "value": value, "status": "set", "expires_in_seconds": 60}


# --- Database Table Creation on Startup ---
@app.on_event("startup")
def startup_event():
    logger.info("Application startup event triggered.")
    # Ensure tables are created
    logger.info("Attempting to create database tables if they don't exist...")
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables checked/created successfully.")
    except Exception as e:
        logger.error(f"Error creating database tables on startup: {e}")
        # Depending on your setup, you might want to stop the app here
        # or handle more gracefully. For local dev, a log might suffice.

