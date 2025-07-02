# backend/app/crud/users.py

import uuid
import logging
from typing import List, Optional

from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from .. import models, schemas # Import models and schemas

logger = logging.getLogger(__name__)

def get_user(db: Session, user_id: uuid.UUID):
    """Retrieve a single user by ID."""
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_users(db: Session, skip: int = 0, limit: int = 100):
    """Retrieve a list of users."""
    return db.query(models.User).offset(skip).limit(limit).all()

def create_user(db: Session, user: schemas.UserCreate):
    """Create a new user."""

    hashed_password = user.password + "_hashed" # Revert to direct stub hashing
    db_user = models.User(**user.dict(exclude={"password"}), password_hash=hashed_password)
    try:
        # Check if organization_id exists
        organization = db.query(models.Organization).filter(models.Organization.id == db_user.organization_id).first()
        if not organization:
            raise HTTPException(status_code=400, detail="Organization ID not found")

        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    except Exception as e:
        db.rollback()
        if "duplicate key value violates unique constraint" in str(e):
            raise HTTPException(status_code=409, detail="User with this username or email already exists")
        logger.error(f"Error creating user: {e}")
        raise HTTPException(status_code=400, detail="Error creating user")

def update_user(db: Session, user_id: uuid.UUID, user_update: schemas.UserUpdate):
    """Update an existing user."""
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if not db_user:
        return None

    update_data = user_update.dict(exclude_unset=True)

    if "password" in update_data and update_data["password"] is not None and update_data["password"] != "":
        update_data["password_hash"] = update_data["password"] + "_hashed" # Revert to direct stub hashing
        del update_data["password"]
    elif "password" in update_data: # If password key exists but is None or empty string, just remove it

        del update_data["password"]
    elif "password" in update_data and update_data["password"] is None:
        # If password is explicitly set to None (or empty string handled by schema), remove it so it's not processed
        del update_data["password"]


    for key, value in update_data.items():
        setattr(db_user, key, value)
    try:
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    except Exception as e:
        db.rollback()
        if "duplicate key value violates unique constraint" in str(e):
            raise HTTPException(status_code=409, detail="User with this username or email already exists")
        logger.error(f"Error updating user: {e}")
        raise HTTPException(status_code=400, detail="Error updating user")

def delete_user(db: Session, user_id: uuid.UUID):
    """Delete a user by ID."""
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if not db_user:
        return None
    try:
        db.delete(db_user)
        db.commit()
        return {"message": "User deleted successfully"}
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting user: {e}")
        raise HTTPException(status_code=400, detail="Error deleting user. Check for dependent records.")

