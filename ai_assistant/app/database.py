"""
Database configuration for the AI Assistant service.
"""

import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager
from typing import Generator
import logging

from .config import settings

logger = logging.getLogger(__name__)

# Database URL - use ABParts database
DATABASE_URL = settings.DATABASE_URL or "postgresql://abparts_user:abparts_password@db:5432/abparts_dev"

# Create SQLAlchemy engine
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=300,
    echo=settings.DEBUG
)

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    """
    Dependency to get database session.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@contextmanager
def get_db_session():
    """
    Context manager for database sessions.
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


async def init_database():
    """
    Initialize database connection.
    Tables are created via SQL script for now.
    """
    try:
        # Test database connection
        with get_db_session() as db:
            db.execute(text("SELECT 1"))
        logger.info("Database connection established")
    except Exception as e:
        logger.error(f"Failed to connect to database: {e}")
        raise

    _ensure_support_case_columns()


def _ensure_support_case_columns():
    """
    Add support_cases columns introduced after create_support_cases_tables.sql
    was first run, so existing databases pick them up on deploy.
    """
    try:
        with get_db_session() as db:
            if not db.execute(text("SELECT to_regclass('support_cases')")).scalar():
                return
            db.execute(text("ALTER TABLE support_cases ADD COLUMN IF NOT EXISTS contacted_at TIMESTAMP"))
            db.execute(text("ALTER TABLE support_cases ADD COLUMN IF NOT EXISTS contact_channel VARCHAR(30)"))
            db.execute(text("ALTER TABLE support_cases ADD COLUMN IF NOT EXISTS resolved_by VARCHAR(36)"))
    except Exception as e:
        logger.error(f"Failed to add support_cases columns: {e}")


async def close_database():
    """
    Close database connections.
    """
    try:
        engine.dispose()
        logger.info("Database connections closed")
    except Exception as e:
        logger.error(f"Error closing database connections: {e}")