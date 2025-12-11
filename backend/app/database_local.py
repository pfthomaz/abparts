"""
Local database configuration for test discovery
This module provides mock database functionality for IDE test discovery
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from unittest.mock import MagicMock

# Check if we're in test discovery mode
if os.getenv("ENVIRONMENT") == "test_discovery":
    # Use in-memory SQLite for discovery
    SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
    
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        connect_args={"check_same_thread": False}
    )
    
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base = declarative_base()
    
    def get_db():
        """Mock database session for test discovery"""
        return MagicMock()
        
else:
    # Import the real database module
    from .database import engine, SessionLocal, Base, get_db