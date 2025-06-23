# backend/app/auth.py

import uuid
import logging
from datetime import datetime, timedelta
from typing import List, Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, Field # Keep BaseModel and Field as they are used for TokenData
from sqlalchemy.orm import Session # Import Session here

from . import models # Import your SQLAlchemy models
from .database import get_db # Import your database session dependency
from .schemas import Token # Import Token from schemas.py

logger = logging.getLogger(__name__)

# OAuth2PasswordBearer will manage the "Bearer" token in the header
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token") # tokenUrl is the endpoint for getting a token


class TokenData(BaseModel):
    username: Optional[str] = None
    user_id: Optional[uuid.UUID] = None
    organization_id: Optional[uuid.UUID] = None
    role: Optional[str] = None

def verify_password_stub(plain_password: str, hashed_password: str) -> bool:
    """
    STUB: In a real application, use bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8')).
    This just checks if the plain_password matches the hashed_password (which includes "_hashed").
    """
    return (plain_password + "_hashed") == hashed_password

async def authenticate_user(db: Session, username: str, password: str):
    """
    Authenticates a user against the database.
    """
    user = db.query(models.User).filter(models.User.username == username).first()
    if not user:
        return None
    # STUB: In real app, use bcrypt.checkpw
    if not verify_password_stub(password, user.password_hash):
        return None
    return user

def create_access_token(user: models.User, expires_delta: Optional[timedelta] = None):
    """
    STUB: In a real application, this would generate a JWT token.
    For now, it's a simple base64 encoded string or similar.
    """
    to_encode = {
        "sub": user.username,
        "user_id": str(user.id), # UUIDs need to be stringified for JWT payload
        "organization_id": str(user.organization_id),
        "role": user.role
    }
    # In a real JWT, you'd encode this payload with a secret key and algorithm
    # For this stub, we'll just simulate a token
    fake_token = f"fake-jwt-{user.username}-{user.role}-{uuid.uuid4()}"
    return fake_token

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """
    Dependency to get the current authenticated user from the token.
    STUB: This would decode and validate a JWT token in a real app.
    For this stub, we're just parsing the fake token.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # STUB: Parse the fake token to extract user info
        # Expects token like "fake-jwt-username-role-uuid"
        parts = token.split('-')
        if len(parts) != 4 or parts[0] != "fake" or parts[1] != "jwt":
             raise credentials_exception

        username = parts[2]
        role = parts[3] # This is a simplification; a real JWT would have a structured payload

        user = db.query(models.User).filter(models.User.username == username).first()
        if user is None:
            raise credentials_exception

        # For the stub, we just confirm the role matches
        if user.role != role:
            raise credentials_exception

        # Populate a TokenData model for consistency
        current_user_data = TokenData(
            username=user.username,
            user_id=user.id,
            organization_id=user.organization_id,
            role=user.role
        )
        return current_user_data
    except Exception as e:
        logger.error(f"Error validating token: {e}")
        raise credentials_exception


# Dependency factories for role-based authorization
def has_role(required_role: str):
    def role_checker(current_user: TokenData = Depends(get_current_user)):
        if current_user.role != required_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Not authorized. Requires '{required_role}' role."
            )
        return current_user
    return role_checker

def has_roles(required_roles: List[str]):
    def roles_checker(current_user: TokenData = Depends(get_current_user)):
        if current_user.role not in required_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Not authorized. Requires one of {required_roles} roles."
            )
        return current_user
    return roles_checker

# Authentication Endpoints (These will be imported into main.py)

async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    Login endpoint to get an access token.
    Use 'username' and 'password' in form-data.
    """
    user = await authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(user=user)
    return {"access_token": access_token, "token_type": "bearer"}

async def read_users_me(current_user: TokenData = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Get details of the currently authenticated user.
    """
    user_db = db.query(models.User).filter(models.User.id == current_user.user_id).first()
    if not user_db:
        raise HTTPException(status_code=404, detail="User not found in DB")
    return user_db
