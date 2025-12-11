# backend/app/database.py

import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import logging
import redis

logger = logging.getLogger(__name__)

# --- Database Configuration ---
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    logger.error("DATABASE_URL environment variable is not set.")
    raise ValueError("DATABASE_URL environment variable is not set.")

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,  # Verify connections before use
    pool_recycle=3600,   # Recycle connections every hour
    echo=False           # Set to True for SQL debugging
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# --- Redis Configuration ---
REDIS_URL = os.getenv("REDIS_URL")
if not REDIS_URL:
    logger.error("REDIS_URL environment variable is not set.")
    raise ValueError("REDIS_URL environment variable is not set.")

redis_client = redis.StrictRedis.from_url(REDIS_URL, decode_responses=True)


# Dependency to get DB session
def get_db():
    """
    Provides a SQLAlchemy session for a request.
    """
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        # Rollback any failed transaction
        db.rollback()
        logger.error(f"Database session error: {e}")
        raise
    finally:
        db.close()

