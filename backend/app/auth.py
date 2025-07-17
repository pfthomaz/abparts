# backend/app/auth.py

import uuid
import logging
import json # New: for JSON encoding/decoding
import base64 # New: for Base64 encoding/decoding
from datetime import datetime, timedelta
from typing import List, Optional

from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, Field
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from jose import jwt

from . import models
from .database import get_db
from .schemas import Token
from .models import UserRole
from .session_manager import session_manager

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

async def authenticate_user(db: Session, username: str, password: str, ip_address: str = None):
    """
    Authenticates a user against the database with security features.
    Requirements: 2D.4
    """
    # Check if user is locked
    if session_manager.is_user_locked(username, db):
        session_manager.log_security_event(
            event_type="login_failed",
            ip_address=ip_address,
            details=f"Login attempt for locked account: {username}",
            risk_level="medium",
            db=db
        )
        return None
    
    user = db.query(models.User).filter(models.User.username == username).first()
    if not user:
        # Record failed attempt for non-existent user
        session_manager.record_failed_login(username, ip_address, db)
        session_manager.log_security_event(
            event_type="login_failed",
            ip_address=ip_address,
            details=f"Login attempt for non-existent user: {username}",
            risk_level="low",
            db=db
        )
        return None
    
    # Check if user account is active
    if not user.is_active or user.user_status != models.UserStatus.active:
        session_manager.log_security_event(
            event_type="login_failed",
            user_id=user.id,
            ip_address=ip_address,
            details=f"Login attempt for inactive account: {username}",
            risk_level="medium",
            db=db
        )
        return None
    
    if not verify_password(password, user.password_hash):
        # Record failed login attempt
        session_manager.record_failed_login(username, ip_address, db)
        session_manager.log_security_event(
            event_type="login_failed",
            user_id=user.id,
            ip_address=ip_address,
            details="Invalid password",
            risk_level="low",
            db=db
        )
        return None
    
    # Clear failed attempts on successful authentication
    session_manager.clear_failed_login_attempts(username, db)
    session_manager.log_security_event(
        event_type="login_success",
        user_id=user.id,
        ip_address=ip_address,
        details="Successful login",
        risk_level="low",
        db=db
    )
    
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
    Dependency to get the current authenticated user from session token.
    Requirements: 2D.1, 2D.2
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Get session data from Redis
        session_data = session_manager.get_session(token)
        if not session_data:
            raise credentials_exception
        
        # Extract user information from session
        user_id = uuid.UUID(session_data["user_id"])
        username = session_data["username"]
        organization_id = uuid.UUID(session_data["organization_id"])
        role = session_data["role"]
        
        # Verify user still exists and is active
        user = db.query(models.User).filter(
            models.User.id == user_id, 
            models.User.username == username,
            models.User.is_active == True,
            models.User.user_status == models.UserStatus.active
        ).first()
        
        if not user:
            # User no longer exists or is inactive, terminate session
            session_manager.terminate_session(token, "user_inactive", db)
            raise credentials_exception
        
        current_user_data = TokenData(
            username=username,
            user_id=user_id,
            organization_id=organization_id,
            role=role
        )
        return current_user_data
        
    except ValueError as e:
        logger.error(f"Invalid UUID in session data: {e}")
        session_manager.terminate_session(token, "invalid_data", db)
        raise credentials_exception
    except Exception as e:
        logger.error(f"Unexpected error validating session: {e}")
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

async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), request: Request = None, db: Session = Depends(get_db)):
    """
    Enhanced login with session management and security features.
    Requirements: 2D.1, 2D.4
    """
    # Extract client information
    ip_address = None
    user_agent = None
    if request:
        ip_address = request.client.host if request.client else None
        user_agent = request.headers.get("user-agent")
    
    # Check rate limiting
    if ip_address and not session_manager.check_rate_limit(ip_address, "login"):
        session_manager.log_security_event(
            event_type="rate_limit_exceeded",
            ip_address=ip_address,
            user_agent=user_agent,
            details="Login rate limit exceeded",
            risk_level="medium",
            db=db
        )
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many login attempts. Please try again later.",
            headers={"Retry-After": "60"}
        )
    
    user = await authenticate_user(db, form_data.username, form_data.password, ip_address)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Check for suspicious activity and require additional verification if needed
    if ip_address and session_manager.detect_suspicious_activity(ip_address, user_agent, db):
        session_manager.require_additional_verification(user.id, ip_address, db)
        
        # Send verification code
        verification_code = session_manager.send_verification_code(user.id, "email", db)
        
        raise HTTPException(
            status_code=status.HTTP_202_ACCEPTED,
            detail="Additional verification required. Check your email for verification code.",
            headers={"X-Verification-Required": "true"}
        )
    
    # Create session instead of JWT token
    session_token = session_manager.create_session(user, ip_address, user_agent, db)
    return {"access_token": session_token, "token_type": "bearer"}

async def read_users_me(current_user: TokenData = Depends(get_current_user), db: Session = Depends(get_db)):
    user_db = db.query(models.User).filter(models.User.id == current_user.user_id).first()
    if not user_db:
        raise HTTPException(status_code=404, detail="User not found in DB")
    return user_db
