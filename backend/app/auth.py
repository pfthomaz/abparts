# backend/app/auth.py

import uuid
import logging
import json # New: for JSON encoding/decoding
import base64 # New: for Base64 encoding/decoding
from datetime import datetime, timedelta
from typing import List, Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from . import models
from .database import get_db
from .schemas import Token

logger = logging.getLogger(__name__)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")

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
    if not verify_password_stub(password, user.password_hash):
        return None
    return user

def create_access_token(user: models.User, expires_delta: Optional[timedelta] = None):
    """
    STUB: Generates a "fake" access token by Base64 encoding a JSON payload.
    In a real application, this would generate a cryptographically signed JWT.
    """
    # Payload for the fake token
    payload = {
        "sub": user.username,
        "user_id": str(user.id),
        "organization_id": str(user.organization_id),
        "role": user.role,
        # 'exp': (datetime.utcnow() + expires_delta).timestamp() if expires_delta else None # Optional: add expiry
    }
    # Encode payload to JSON string, then to bytes, then Base64 encode
    encoded_payload = base64.urlsafe_b64encode(json.dumps(payload).encode('utf-8')).decode('utf-8').rstrip("=")
    
    # Prefix with "fake." to resemble JWT structure (header.payload.signature)
    # Since we're not doing signature, it's just header.payload
    fake_header = base64.urlsafe_b64encode(json.dumps({"alg": "none", "typ": "JWT"}).encode('utf-8')).decode('utf-8').rstrip("=")
    
    return f"{fake_header}.{encoded_payload}." # Trailing dot for "no signature"

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """
    Dependency to get the current authenticated user from the token.
    STUB: Decodes and validates the "fake" Base64 encoded token.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # Split the token into header, payload, (and optional signature)
        parts = token.split('.')
        if len(parts) < 2: # Expect at least header.payload
            raise credentials_exception
        
        # Decode the payload (second part of the token)
        # Add padding back if it was stripped
        encoded_payload = parts[1] + "=" * ((4 - len(parts[1]) % 4) % 4)
        decoded_payload = base64.urlsafe_b64decode(encoded_payload).decode('utf-8')
        payload_data = json.loads(decoded_payload)

        username = payload_data.get("sub")
        user_id_str = payload_data.get("user_id")
        organization_id_str = payload_data.get("organization_id")
        role = payload_data.get("role")

        if not all([username, user_id_str, organization_id_str, role]):
            raise credentials_exception

        # Convert UUID strings back to UUID objects
        user_id = uuid.UUID(user_id_str)
        organization_id = uuid.UUID(organization_id_str)

        # Basic user existence check
        user = db.query(models.User).filter(models.User.id == user_id, models.User.username == username).first()
        if user is None:
            raise credentials_exception

        # For the stub, we just confirm the role matches
        if user.role != role:
            raise credentials_exception

        current_user_data = TokenData(
            username=username,
            user_id=user_id,
            organization_id=organization_id,
            role=role
        )
        return current_user_data
    except (json.JSONDecodeError, UnicodeDecodeError, ValueError, IndexError) as e:
        logger.error(f"Token parsing error: {e}")
        raise credentials_exception
    except Exception as e:
        logger.error(f"Unexpected error validating token: {e}")
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

async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
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
    user_db = db.query(models.User).filter(models.User.id == current_user.user_id).first()
    if not user_db:
        raise HTTPException(status_code=404, detail="User not found in DB")
    return user_db

