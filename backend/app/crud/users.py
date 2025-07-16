# c:/abparts/backend/app/crud/users.py

import uuid
import secrets
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from typing import List, Optional

from .. import models, schemas
from ..auth import get_password_hash

def get_user(db: Session, user_id: uuid.UUID) -> models.User | None:
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_username(db: Session, username: str) -> models.User | None:
    return db.query(models.User).filter(models.User.username == username).first()

def get_users(db: Session, skip: int = 0, limit: int = 100) -> List[models.User]:
    return db.query(models.User).offset(skip).limit(limit).all()

def create_user(db: Session, user: schemas.UserCreate) -> models.User:
    hashed_password = get_password_hash(user.password)
    db_user = models.User(
        username=user.username,
        email=user.email,
        password_hash=hashed_password,
        organization_id=user.organization_id,
        name=user.name,
        role=user.role
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user(db: Session, user_id: uuid.UUID, user_update: schemas.UserUpdate) -> models.User | None:
    db_user = get_user(db, user_id)
    if not db_user:
        return None

    update_data = user_update.model_dump(exclude_unset=True)
    
    if "password" in update_data and update_data["password"]:
        hashed_password = get_password_hash(update_data["password"])
        db_user.password_hash = hashed_password
        del update_data["password"] # Don't try to set password field on model

    for key, value in update_data.items():
        setattr(db_user, key, value)
        
    db.commit()
    db.refresh(db_user)
    return db_user

def delete_user(db: Session, user_id: uuid.UUID) -> bool:
    db_user = get_user(db, user_id)
    if not db_user:
        return False
    db.delete(db_user)
    db.commit()
    return True

def set_user_active_status(db: Session, user_id: uuid.UUID, is_active: bool) -> models.User | None:
    db_user = get_user(db, user_id)
    if not db_user:
        return None
    
    db_user.is_active = is_active
    db.commit()
    db.refresh(db_user)
    return db_user


# --- User Invitation Functions ---

def create_user_invitation(db: Session, invitation: schemas.UserInvitationCreate, invited_by_user_id: uuid.UUID) -> models.User:
    """
    Create a new user with pending invitation status.
    """
    # Generate secure invitation token
    invitation_token = secrets.token_urlsafe(32)
    invitation_expires_at = datetime.utcnow() + timedelta(days=7)
    
    # Create user with pending invitation status
    db_user = models.User(
        email=invitation.email,
        name=invitation.name,
        role=invitation.role,
        organization_id=invitation.organization_id,
        user_status=models.UserStatus.pending_invitation,
        invitation_token=invitation_token,
        invitation_expires_at=invitation_expires_at,
        invited_by_user_id=invited_by_user_id,
        username="",  # Will be set when invitation is accepted
        password_hash="",  # Will be set when invitation is accepted
        is_active=False
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    # Create audit log entry
    audit_log = models.InvitationAuditLog(
        user_id=db_user.id,
        action="invited",
        performed_by_user_id=invited_by_user_id,
        details=f"Invitation sent to {invitation.email}"
    )
    db.add(audit_log)
    db.commit()
    
    return db_user

def get_user_by_email(db: Session, email: str) -> Optional[models.User]:
    """
    Get user by email address.
    """
    return db.query(models.User).filter(models.User.email == email).first()

def get_user_by_invitation_token(db: Session, token: str) -> Optional[models.User]:
    """
    Get user by invitation token.
    """
    return db.query(models.User).filter(
        models.User.invitation_token == token,
        models.User.user_status == models.UserStatus.pending_invitation,
        models.User.invitation_expires_at > datetime.utcnow()
    ).first()

def accept_user_invitation(db: Session, token: str, username: str, password: str, name: Optional[str] = None) -> Optional[models.User]:
    """
    Accept a user invitation by setting username, password, and activating the account.
    """
    db_user = get_user_by_invitation_token(db, token)
    if not db_user:
        return None
    
    # Check if username is already taken
    existing_user = get_user_by_username(db, username)
    if existing_user:
        raise ValueError("Username already exists")
    
    # Update user with account details
    db_user.username = username
    db_user.password_hash = get_password_hash(password)
    if name:
        db_user.name = name
    db_user.user_status = models.UserStatus.active
    db_user.is_active = True
    db_user.invitation_token = None
    db_user.invitation_expires_at = None
    
    db.commit()
    db.refresh(db_user)
    
    # Create audit log entry
    audit_log = models.InvitationAuditLog(
        user_id=db_user.id,
        action="accepted",
        performed_by_user_id=db_user.id,
        details=f"Invitation accepted, username set to {username}"
    )
    db.add(audit_log)
    db.commit()
    
    return db_user

def resend_user_invitation(db: Session, user_id: uuid.UUID, resent_by_user_id: uuid.UUID) -> Optional[models.User]:
    """
    Resend invitation by generating new token and extending expiry.
    """
    db_user = get_user(db, user_id)
    if not db_user or db_user.user_status != models.UserStatus.pending_invitation:
        return None
    
    # Generate new token and extend expiry
    db_user.invitation_token = secrets.token_urlsafe(32)
    db_user.invitation_expires_at = datetime.utcnow() + timedelta(days=7)
    
    db.commit()
    db.refresh(db_user)
    
    # Create audit log entry
    audit_log = models.InvitationAuditLog(
        user_id=db_user.id,
        action="resent",
        performed_by_user_id=resent_by_user_id,
        details="Invitation resent with new token"
    )
    db.add(audit_log)
    db.commit()
    
    return db_user

def get_pending_invitations(db: Session, organization_id: Optional[uuid.UUID] = None, skip: int = 0, limit: int = 100) -> List[models.User]:
    """
    Get all pending invitations, optionally filtered by organization.
    """
    query = db.query(models.User).filter(models.User.user_status == models.UserStatus.pending_invitation)
    
    if organization_id:
        query = query.filter(models.User.organization_id == organization_id)
    
    return query.offset(skip).limit(limit).all()

def get_expired_invitations(db: Session) -> List[models.User]:
    """
    Get all expired invitations.
    """
    return db.query(models.User).filter(
        models.User.user_status == models.UserStatus.pending_invitation,
        models.User.invitation_expires_at < datetime.utcnow()
    ).all()

def mark_invitations_as_expired(db: Session) -> int:
    """
    Mark expired invitations and create audit log entries.
    Returns the number of invitations marked as expired.
    """
    expired_users = get_expired_invitations(db)
    count = 0
    
    for user in expired_users:
        # Create audit log entry
        audit_log = models.InvitationAuditLog(
            user_id=user.id,
            action="expired",
            performed_by_user_id=None,
            details="Invitation expired automatically"
        )
        db.add(audit_log)
        count += 1
    
    if count > 0:
        db.commit()
    
    return count

def get_invitation_audit_logs(db: Session, user_id: uuid.UUID) -> List[models.InvitationAuditLog]:
    """
    Get invitation audit logs for a specific user.
    """
    return db.query(models.InvitationAuditLog).filter(
        models.InvitationAuditLog.user_id == user_id
    ).order_by(models.InvitationAuditLog.timestamp.desc()).all()

def get_users_by_organization(db: Session, organization_id: uuid.UUID, skip: int = 0, limit: int = 100) -> List[models.User]:
    """
    Get users filtered by organization.
    """
    return db.query(models.User).filter(
        models.User.organization_id == organization_id
    ).offset(skip).limit(limit).all()