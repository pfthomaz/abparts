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
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from jose import jwt

from . import models
from .database import get_db
from .schemas import Token
from .models import UserRole

# Role mapping for backward compatibility
LEGACY_ROLE_MAPPING = {
    # Legacy role strings -> New enum values
    "Oraseas Admin": "super_admin",
    "Customer Admin": "admin", 
    "Customer User": "user",
    "Supplier User": "user",
    "Oraseas Inventory Manager": "admin",
    # New enum values (pass through)
    "super_admin": "super_admin",
    "admin": "admin",
    "user": "user"
}

# Reverse mapping for token generation
ENUM_TO_LEGACY_MAPPING = {
    "super_admin": ["Oraseas Admin"],
    "admin": ["Customer Admin", "Oraseas Inventory Manager"],
    "user": ["Customer User", "Supplier User"]
}

def normalize_role(role_input) -> str:
    """Convert any role input to the new enum string value."""
    if isinstance(role_input, UserRole):
        return role_input.value
    elif isinstance(role_input, str):
        return LEGACY_ROLE_MAPPING.get(role_input, role_input)
    return str(role_input)

def role_matches(user_role, required_roles) -> bool:
    """Check if user role matches any of the required roles (supports legacy and new roles)."""
    normalized_user_role = normalize_role(user_role)
    
    if isinstance(required_roles, str):
        required_roles = [required_roles]
    
    for required_role in required_roles:
        normalized_required = normalize_role(required_role)
        if normalized_user_role == normalized_required:
            return True
    
    return False

logger = logging.getLogger(__name__)

# --- Password Hashing Setup ---
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")

SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"

class TokenData(BaseModel):
    username: Optional[str] = None
    user_id: Optional[uuid.UUID] = None
    organization_id: Optional[uuid.UUID] = None
    role: Optional[str] = None

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifies a plain password against a hashed password using passlib.
    """
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hashes a password using passlib's bcrypt context."""
    return pwd_context.hash(password)

async def authenticate_user(db: Session, username: str, password: str):
    """
    Authenticates a user against the database.
    """
    user = db.query(models.User).filter(models.User.username == username).first()
    if not user:
        return None
    if not verify_password(password, user.password_hash):
        return None
    return user

def create_access_token(user: models.User, expires_delta: Optional[timedelta] = None):
    to_encode = {
        "sub": user.username,
        "user_id": str(user.id),
        "organization_id": str(user.organization_id),
        "role": user.role.value if isinstance(user.role, UserRole) else user.role,
    }
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=12)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

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
        user_role_value = user.role.value if isinstance(user.role, UserRole) else user.role
        if user_role_value != role:
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
        if not role_matches(current_user.role, required_role):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Not authorized. Requires '{required_role}' role."
            )
        return current_user
    return role_checker

def has_roles(required_roles: List[str]):
    def roles_checker(current_user: TokenData = Depends(get_current_user)):
        if not role_matches(current_user.role, required_roles):
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
