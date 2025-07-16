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


# --- User Profile and Self-Service Functions ---

def update_user_profile(db: Session, user_id: uuid.UUID, profile_update: schemas.UserProfileUpdate) -> Optional[models.User]:
    """
    Update user profile information (name, email).
    """
    db_user = get_user(db, user_id)
    if not db_user:
        return None
    
    update_data = profile_update.model_dump(exclude_unset=True)
    
    # Handle email change - set as pending if email is being changed
    if "email" in update_data and update_data["email"] != db_user.email:
        # Check if new email is already in use
        existing_user = get_user_by_email(db, update_data["email"])
        if existing_user and existing_user.id != user_id:
            raise ValueError("Email address is already in use")
        
        # Set pending email instead of directly updating
        db_user.pending_email = update_data["email"]
        del update_data["email"]  # Don't update email directly
    
    # Update other fields
    for key, value in update_data.items():
        setattr(db_user, key, value)
    
    db.commit()
    db.refresh(db_user)
    return db_user

def change_user_password(db: Session, user_id: uuid.UUID, current_password: str, new_password: str) -> bool:
    """
    Change user password with current password validation.
    """
    from ..auth import verify_password, get_password_hash
    
    db_user = get_user(db, user_id)
    if not db_user:
        return False
    
    # Verify current password
    if not verify_password(current_password, db_user.password_hash):
        raise ValueError("Current password is incorrect")
    
    # Update password
    db_user.password_hash = get_password_hash(new_password)
    db.commit()
    
    return True

def request_password_reset(db: Session, email: str) -> Optional[models.User]:
    """
    Generate password reset token for user.
    """
    db_user = get_user_by_email(db, email)
    if not db_user:
        return None
    
    # Generate secure reset token
    reset_token = secrets.token_urlsafe(32)
    reset_expires_at = datetime.utcnow() + timedelta(hours=1)  # 1 hour expiry
    
    db_user.password_reset_token = reset_token
    db_user.password_reset_expires_at = reset_expires_at
    
    db.commit()
    db.refresh(db_user)
    return db_user

def get_user_by_reset_token(db: Session, token: str) -> Optional[models.User]:
    """
    Get user by password reset token.
    """
    return db.query(models.User).filter(
        models.User.password_reset_token == token,
        models.User.password_reset_expires_at > datetime.utcnow()
    ).first()

def confirm_password_reset(db: Session, token: str, new_password: str) -> Optional[models.User]:
    """
    Confirm password reset with token.
    """
    from ..auth import get_password_hash
    
    db_user = get_user_by_reset_token(db, token)
    if not db_user:
        return None
    
    # Update password and clear reset token
    db_user.password_hash = get_password_hash(new_password)
    db_user.password_reset_token = None
    db_user.password_reset_expires_at = None
    
    db.commit()
    db.refresh(db_user)
    return db_user

def request_email_verification(db: Session, user_id: uuid.UUID, new_email: str) -> Optional[models.User]:
    """
    Generate email verification token for email change.
    """
    db_user = get_user(db, user_id)
    if not db_user:
        return None
    
    # Check if new email is already in use
    existing_user = get_user_by_email(db, new_email)
    if existing_user and existing_user.id != user_id:
        raise ValueError("Email address is already in use")
    
    # Generate secure verification token
    verification_token = secrets.token_urlsafe(32)
    verification_expires_at = datetime.utcnow() + timedelta(hours=24)  # 24 hour expiry
    
    db_user.pending_email = new_email
    db_user.email_verification_token = verification_token
    db_user.email_verification_expires_at = verification_expires_at
    
    db.commit()
    db.refresh(db_user)
    return db_user

def get_user_by_verification_token(db: Session, token: str) -> Optional[models.User]:
    """
    Get user by email verification token.
    """
    return db.query(models.User).filter(
        models.User.email_verification_token == token,
        models.User.email_verification_expires_at > datetime.utcnow()
    ).first()

def confirm_email_verification(db: Session, token: str) -> Optional[models.User]:
    """
    Confirm email verification with token.
    """
    db_user = get_user_by_verification_token(db, token)
    if not db_user:
        return None
    
    # Update email and clear verification token
    if db_user.pending_email:
        db_user.email = db_user.pending_email
        db_user.pending_email = None
    
    db_user.email_verification_token = None
    db_user.email_verification_expires_at = None
    
    db.commit()
    db.refresh(db_user)
    return db_user

def get_user_profile_with_organization(db: Session, user_id: uuid.UUID) -> Optional[dict]:
    """
    Get user profile with organization information.
    """
    result = db.query(models.User, models.Organization).join(
        models.Organization, models.User.organization_id == models.Organization.id
    ).filter(models.User.id == user_id).first()
    
    if not result:
        return None
    
    user, organization = result
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "name": user.name,
        "role": user.role,
        "user_status": user.user_status,
        "organization_id": user.organization_id,
        "organization_name": organization.name,
        "organization_type": organization.organization_type.value,
        "last_login": user.last_login,
        "created_at": user.created_at,
        "updated_at": user.updated_at
    }

def update_user_status(db: Session, user_id: uuid.UUID, new_status: models.UserStatus) -> Optional[models.User]:
    """
    Update user account status.
    """
    db_user = get_user(db, user_id)
    if not db_user:
        return None
    
    db_user.user_status = new_status
    
    # If deactivating, also set is_active to False
    if new_status == models.UserStatus.inactive:
        db_user.is_active = False
    elif new_status == models.UserStatus.active:
        db_user.is_active = True
    
    db.commit()
    db.refresh(db_user)
    return db_user


# --- Advanced User Administration Functions (Task 3.4) ---

def search_users(
    db: Session, 
    organization_id: Optional[uuid.UUID] = None,
    role: Optional[models.UserRole] = None,
    status: Optional[models.UserStatus] = None,
    search_term: Optional[str] = None,
    skip: int = 0,
    limit: int = 100
) -> List[models.User]:
    """
    Advanced user search and filtering.
    Requirements: 2C.1, 2C.2
    """
    query = db.query(models.User)
    
    # Apply filters
    if organization_id:
        query = query.filter(models.User.organization_id == organization_id)
    
    if role:
        query = query.filter(models.User.role == role)
    
    if status:
        query = query.filter(models.User.user_status == status)
    
    if search_term:
        search_pattern = f"%{search_term}%"
        query = query.filter(
            (models.User.name.ilike(search_pattern)) |
            (models.User.email.ilike(search_pattern)) |
            (models.User.username.ilike(search_pattern))
        )
    
    return query.offset(skip).limit(limit).all()

def deactivate_user_with_session_termination(
    db: Session, 
    user_id: uuid.UUID, 
    performed_by_user_id: uuid.UUID
) -> Optional[models.User]:
    """
    Deactivate user with immediate session termination and audit logging.
    Requirements: 2C.3
    """
    db_user = get_user(db, user_id)
    if not db_user:
        return None
    
    # Store original status for audit log
    original_status = db_user.user_status
    
    # Deactivate user
    db_user.user_status = models.UserStatus.inactive
    db_user.is_active = False
    db_user.updated_at = datetime.utcnow()
    
    # Note: Session termination would be handled by a Redis-based session store
    # For now, we'll create an audit log entry indicating sessions should be terminated
    
    db.commit()
    db.refresh(db_user)
    
    # Create audit log entry
    audit_log = models.UserManagementAuditLog(
        user_id=user_id,
        action="deactivated",
        performed_by_user_id=performed_by_user_id,
        details=f"User deactivated. Previous status: {original_status.value}. Sessions terminated."
    )
    db.add(audit_log)
    db.commit()
    
    return db_user

def reactivate_user_with_notification(
    db: Session, 
    user_id: uuid.UUID, 
    performed_by_user_id: uuid.UUID
) -> Optional[models.User]:
    """
    Reactivate user with notification system and audit logging.
    Requirements: 2C.4
    """
    db_user = get_user(db, user_id)
    if not db_user:
        return None
    
    # Store original status for audit log
    original_status = db_user.user_status
    
    # Reactivate user
    db_user.user_status = models.UserStatus.active
    db_user.is_active = True
    db_user.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(db_user)
    
    # Create audit log entry
    audit_log = models.UserManagementAuditLog(
        user_id=user_id,
        action="reactivated",
        performed_by_user_id=performed_by_user_id,
        details=f"User reactivated. Previous status: {original_status.value}. Notification sent."
    )
    db.add(audit_log)
    db.commit()
    
    return db_user

def soft_delete_user_with_dependency_check(
    db: Session, 
    user_id: uuid.UUID, 
    performed_by_user_id: uuid.UUID
) -> dict:
    """
    Soft delete user with transaction dependency checking.
    Requirements: 2C.5
    """
    db_user = get_user(db, user_id)
    if not db_user:
        return {"success": False, "message": "User not found"}
    
    # Check for transaction dependencies
    transaction_count = db.query(models.Transaction).filter(
        models.Transaction.performed_by_user_id == user_id
    ).count()
    
    part_usage_count = db.query(models.PartUsage).filter(
        models.PartUsage.recorded_by_user_id == user_id
    ).count()
    
    customer_order_count = db.query(models.CustomerOrder).filter(
        models.CustomerOrder.ordered_by_user_id == user_id
    ).count()
    
    stock_adjustment_count = db.query(models.StockAdjustment).filter(
        models.StockAdjustment.user_id == user_id
    ).count()
    
    total_dependencies = transaction_count + part_usage_count + customer_order_count + stock_adjustment_count
    
    if total_dependencies > 0:
        dependency_details = []
        if transaction_count > 0:
            dependency_details.append(f"{transaction_count} transactions")
        if part_usage_count > 0:
            dependency_details.append(f"{part_usage_count} part usage records")
        if customer_order_count > 0:
            dependency_details.append(f"{customer_order_count} customer orders")
        if stock_adjustment_count > 0:
            dependency_details.append(f"{stock_adjustment_count} stock adjustments")
        
        return {
            "success": False,
            "message": f"Cannot delete user due to existing dependencies: {', '.join(dependency_details)}",
            "dependencies": {
                "transactions": transaction_count,
                "part_usage": part_usage_count,
                "customer_orders": customer_order_count,
                "stock_adjustments": stock_adjustment_count
            }
        }
    
    # Perform soft delete (mark as inactive and add deleted flag)
    original_status = db_user.user_status
    db_user.user_status = models.UserStatus.inactive
    db_user.is_active = False
    db_user.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(db_user)
    
    # Create audit log entry
    audit_log = models.UserManagementAuditLog(
        user_id=user_id,
        action="soft_deleted",
        performed_by_user_id=performed_by_user_id,
        details=f"User soft deleted. Previous status: {original_status.value}. No transaction dependencies found."
    )
    db.add(audit_log)
    db.commit()
    
    return {
        "success": True,
        "message": "User successfully soft deleted",
        "user_id": str(user_id)
    }

def get_inactive_users(
    db: Session,
    days_threshold: int = 90,
    organization_id: Optional[uuid.UUID] = None,
    skip: int = 0,
    limit: int = 100
) -> List[models.User]:
    """
    Get users flagged as inactive based on threshold.
    Requirements: 2C.6
    """
    threshold_date = datetime.utcnow() - timedelta(days=days_threshold)
    
    query = db.query(models.User).filter(
        (models.User.last_login < threshold_date) | 
        (models.User.last_login.is_(None) & (models.User.created_at < threshold_date))
    )
    
    if organization_id:
        query = query.filter(models.User.organization_id == organization_id)
    
    return query.offset(skip).limit(limit).all()

def get_user_management_audit_logs(
    db: Session,
    user_id: uuid.UUID,
    skip: int = 0,
    limit: int = 100
) -> List[dict]:
    """
    Get user management audit logs for a specific user with user details.
    Requirements: 2C.7
    """
    results = db.query(
        models.UserManagementAuditLog,
        models.User.email.label('user_email'),
        models.User.name.label('user_name'),
        models.User.username.label('user_username')
    ).join(
        models.User, models.UserManagementAuditLog.user_id == models.User.id
    ).filter(
        models.UserManagementAuditLog.user_id == user_id
    ).order_by(
        models.UserManagementAuditLog.timestamp.desc()
    ).offset(skip).limit(limit).all()
    
    # Get performed_by user details
    audit_logs = []
    for audit_log, user_email, user_name, user_username in results:
        performed_by_user = get_user(db, audit_log.performed_by_user_id)
        performed_by_name = None
        if performed_by_user:
            performed_by_name = performed_by_user.name or performed_by_user.username
        
        audit_logs.append({
            "id": audit_log.id,
            "user_id": audit_log.user_id,
            "action": audit_log.action,
            "performed_by_user_id": audit_log.performed_by_user_id,
            "timestamp": audit_log.timestamp,
            "details": audit_log.details,
            "user_email": user_email,
            "user_name": user_name or user_username,
            "performed_by_name": performed_by_name
        })
    
    return audit_logs

def get_all_user_management_audit_logs(
    db: Session,
    organization_id: Optional[uuid.UUID] = None,
    action: Optional[str] = None,
    skip: int = 0,
    limit: int = 100
) -> List[dict]:
    """
    Get all user management audit logs with filtering.
    Requirements: 2C.7
    """
    query = db.query(
        models.UserManagementAuditLog,
        models.User.email.label('user_email'),
        models.User.name.label('user_name'),
        models.User.username.label('user_username'),
        models.User.organization_id.label('user_organization_id')
    ).join(
        models.User, models.UserManagementAuditLog.user_id == models.User.id
    )
    
    if organization_id:
        query = query.filter(models.User.organization_id == organization_id)
    
    if action:
        query = query.filter(models.UserManagementAuditLog.action == action)
    
    results = query.order_by(
        models.UserManagementAuditLog.timestamp.desc()
    ).offset(skip).limit(limit).all()
    
    # Get performed_by user details
    audit_logs = []
    for audit_log, user_email, user_name, user_username, user_org_id in results:
        performed_by_user = get_user(db, audit_log.performed_by_user_id)
        performed_by_name = None
        if performed_by_user:
            performed_by_name = performed_by_user.name or performed_by_user.username
        
        audit_logs.append({
            "id": audit_log.id,
            "user_id": audit_log.user_id,
            "action": audit_log.action,
            "performed_by_user_id": audit_log.performed_by_user_id,
            "timestamp": audit_log.timestamp,
            "details": audit_log.details,
            "user_email": user_email,
            "user_name": user_name or user_username,
            "performed_by_name": performed_by_name
        })
    
    return audit_logs