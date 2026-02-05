# backend/app/routers/users.py

import uuid
from typing import List, Optional
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from sqlalchemy.orm import Session

from .. import schemas, crud, models # Import schemas, CRUD functions, and models
from ..database import get_db # Import DB session dependency
from ..auth import get_current_user, has_role, has_roles, TokenData, oauth2_scheme # Import authentication dependencies
from ..tasks import send_invitation_email, send_invitation_accepted_notification, send_password_reset_email, send_email_verification_email, send_user_reactivation_notification
from ..session_manager import session_manager
from ..permissions import (
    ResourceType, PermissionType, require_permission, require_super_admin, require_admin,
    OrganizationScopedQueries, check_organization_access, permission_checker
)

router = APIRouter()

def _can_have_superadmin_users(organization: models.Organization) -> bool:
    """
    Check if an organization can have superadmin users.
    Key organizations that can have superadmins:
    - Oraseas EE (organization_type: oraseas_ee)
    - BossServ Ltd (supplier organization in UK)
    - BossAqua (supplier organization in New Zealand or bossaqua type)
    """
    # Oraseas EE can always have superadmins
    if organization.organization_type == models.OrganizationType.oraseas_ee:
        return True
    
    # BossAqua organization type can have superadmins
    if organization.organization_type == models.OrganizationType.bossaqua:
        return True
    
    # Specific organizations that can have superadmins (supplier or customer)
    key_organization_names = ["BossServ Ltd", "BossServ LLC", "BossAqua"]
    if (organization.organization_type in [models.OrganizationType.supplier, models.OrganizationType.customer] and 
        organization.name in key_organization_names):
        return True
    
    return False

def _check_update_user_permissions(user_to_update: models.User, user_update: schemas.UserUpdate, current_user: TokenData):
    """Helper to centralize complex permission checks for updating a user."""
    is_super_admin = permission_checker.is_super_admin(current_user)
    is_admin_in_own_org = (
        permission_checker.is_admin(current_user) and
        user_to_update.organization_id == current_user.organization_id
    )
    is_self_update = user_to_update.id == current_user.user_id

    if is_super_admin:
        return # Super admin has full permissions

    # Check if trying to change organization (not allowed for non-super-admins)
    if user_update.organization_id is not None and user_update.organization_id != user_to_update.organization_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You cannot change a user's organization.")
    
    # Check if trying to change role (not allowed for non-super-admins)
    # Only raise error if role is actually being CHANGED, not just included in the update
    if user_update.role is not None:
        # Compare enum values properly
        current_role_value = user_to_update.role.value if hasattr(user_to_update.role, 'value') else str(user_to_update.role)
        update_role_value = user_update.role.value if hasattr(user_update.role, 'value') else str(user_update.role)
        if update_role_value != current_role_value:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You cannot change a user's role.")

    # Check if user has permission to update this user at all
    if not (is_admin_in_own_org or is_self_update):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update this user")

def _check_create_user_permissions(user_to_create: schemas.UserCreate, organization: models.Organization, current_user: TokenData):
    """Helper to centralize permission checks for creating a user."""
    if not organization:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Organization ID not found")

    if permission_checker.is_admin(current_user) and not permission_checker.is_super_admin(current_user):
        if user_to_create.organization_id != current_user.organization_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin can only create users within their own organization")
        if user_to_create.role == "super_admin":
             raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only super admins can create super admin users.")

    if permission_checker.is_super_admin(current_user):
        # Check if organization can have superadmin users
        if user_to_create.role == "super_admin" and not _can_have_superadmin_users(organization):
             raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Super admin role can only be assigned to key organizations (Oraseas EE, BossServ Ltd, BossAqua).")


# --- Users CRUD ---
@router.get("/", response_model=List[schemas.UserResponse])
async def get_users(
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(require_permission(ResourceType.USER, PermissionType.READ))
):
    # Get base query and apply organization-scoped filtering
    query = db.query(models.User)
    query = OrganizationScopedQueries.filter_users(query, current_user)
    users = query.all()
    return users

@router.get("/me/")
async def get_current_user_info(
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)
):
    """
    Get current authenticated user's information with organization details.
    """
    profile_dict = crud.users.get_user_profile_with_organization(db, current_user.user_id)
    if not profile_dict:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    # Return dict directly to include all fields including None values
    return profile_dict

@router.get("/me/profile", response_model=schemas.UserProfileResponse)
async def get_my_profile(
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)
):
    """
    Get current user's profile with role and organization information.
    Requirements: 2B.4
    """
    profile = crud.users.get_user_profile_with_organization(db, current_user.user_id)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User profile not found"
        )
    
    return profile

@router.get("/admin/search", response_model=List[schemas.UserResponse])
async def search_users(
    organization_id: Optional[uuid.UUID] = Query(None, description="Filter by organization ID"),
    role: Optional[schemas.UserRoleEnum] = Query(None, description="Filter by user role"),
    status: Optional[schemas.UserStatusEnum] = Query(None, description="Filter by user status"),
    search: Optional[str] = Query(None, description="Search by name or email"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(has_roles(["super_admin", "admin"]))
):
    """
    Advanced user search and filtering with organization-scoped access.
    Requirements: 2C.1, 2C.2
    """
    # Permission checks - admins can only search within their organization
    if current_user.role == "admin":
        if organization_id and organization_id != current_user.organization_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only search users in your organization"
            )
        # Force organization filter for admins
        organization_id = current_user.organization_id
    
    try:
        users = crud.users.search_users(
            db=db,
            organization_id=organization_id,
            role=role,
            status=status,
            search_term=search,
            skip=skip,
            limit=limit
        )
        return users
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to search users: {str(e)}"
        )

@router.get("/admin/inactive-users", response_model=List[schemas.UserResponse])
async def get_inactive_users(
    days_threshold: int = Query(90, ge=1, le=365, description="Days of inactivity threshold"),
    organization_id: Optional[uuid.UUID] = Query(None, description="Filter by organization ID"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(has_roles(["super_admin", "admin"]))
):
    """
    Get users flagged as inactive based on 90-day threshold or custom threshold.
    Requirements: 2C.6
    """
    # Permission checks - admins can only view users in their organization
    if current_user.role == "admin":
        if organization_id and organization_id != current_user.organization_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only view users in your organization"
            )
        # Force organization filter for admins
        organization_id = current_user.organization_id
    
    try:
        inactive_users = crud.users.get_inactive_users(
            db=db,
            days_threshold=days_threshold,
            organization_id=organization_id,
            skip=skip,
            limit=limit
        )
        return inactive_users
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get inactive users: {str(e)}"
        )

@router.get("/admin/audit-logs", response_model=List[schemas.UserManagementAuditLogResponse])
async def get_all_user_management_audit_logs(
    organization_id: Optional[uuid.UUID] = Query(None, description="Filter by organization ID"),
    action: Optional[str] = Query(None, description="Filter by action type"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(has_roles(["super_admin", "admin"]))
):
    """
    Get all user management audit logs with filtering.
    Requirements: 2C.7
    """
    # Permission checks - admins can only view logs for their organization
    if current_user.role == "admin":
        if organization_id and organization_id != current_user.organization_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only view audit logs for your organization"
            )
        # Force organization filter for admins
        organization_id = current_user.organization_id
    
    try:
        audit_logs = crud.users.get_all_user_management_audit_logs(
            db=db,
            organization_id=organization_id,
            action=action,
            skip=skip,
            limit=limit
        )
        return audit_logs
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get audit logs: {str(e)}"
        )

@router.get("/me/sessions", response_model=List[dict])
async def get_my_active_sessions(
    request: Request,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)
):
    """
    Get all active sessions for the current user.
    Requirements: 2D.7
    """
    from ..session_manager import session_manager
    
    try:
        sessions = session_manager.get_active_sessions(current_user.user_id)
        
        # Get current session token from header
        auth_header = request.headers.get("Authorization", "")
        current_token = auth_header.replace("Bearer ", "") if auth_header.startswith("Bearer ") else None
        
        # Process sessions for frontend
        processed_sessions = []
        for session in sessions:
            # Map session_token to token for frontend compatibility
            session["token"] = session.get("session_token")
            
            # Determine if this is the current session
            if current_token and session.get("session_token") == current_token:
                session["is_current"] = True
            else:
                session["is_current"] = False
                
            processed_sessions.append(session)
            
        return processed_sessions
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get active sessions: {str(e)}"
        )

@router.get("/admin/security-events", response_model=List[dict])
async def get_security_events(
    user_id: Optional[uuid.UUID] = Query(None, description="Filter by user ID"),
    event_type: Optional[str] = Query(None, description="Filter by event type"),
    risk_level: Optional[str] = Query(None, description="Filter by risk level"),
    hours: int = Query(24, ge=1, le=168, description="Hours to look back (max 7 days)"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(has_roles(["super_admin", "admin"]))
):
    """
    Get security events for monitoring and audit purposes.
    Requirements: 2D.7
    """
    try:
        # Calculate time threshold
        time_threshold = datetime.utcnow() - timedelta(hours=hours)
        
        # Build query
        query = db.query(models.SecurityEvent).filter(
            models.SecurityEvent.timestamp >= time_threshold
        )
        
        # Apply filters
        if user_id:
            query = query.filter(models.SecurityEvent.user_id == user_id)
        
        if event_type:
            query = query.filter(models.SecurityEvent.event_type == event_type)
        
        if risk_level:
            query = query.filter(models.SecurityEvent.risk_level == risk_level)
        
        # Permission checks for admins
        if current_user.role == "admin":
            # Admins can only see events for users in their organization
            query = query.join(models.User).filter(
                models.User.organization_id == current_user.organization_id
            )
        
        # Execute query
        events = query.order_by(
            models.SecurityEvent.timestamp.desc()
        ).offset(skip).limit(limit).all()
        
        # Convert to dict format for response
        return [
            {
                "id": event.id,
                "user_id": event.user_id,
                "event_type": event.event_type,
                "details": event.details,
                "risk_level": event.risk_level,
                "timestamp": event.timestamp,
                "ip_address": event.ip_address,
                "user_agent": event.user_agent
            }
            for event in events
        ]
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get security events: {str(e)}"
        )

@router.get("/{user_id}", response_model=schemas.UserResponse)
async def get_user(
    user_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(require_permission(ResourceType.USER, PermissionType.READ))
):
    user = crud.users.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check if user can access this user's details
    if permission_checker.is_super_admin(current_user) or user_id == current_user.user_id or user.organization_id == current_user.organization_id:
        return user
    else:
        raise HTTPException(status_code=403, detail="Not authorized to view this user's details")

@router.post("/", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user: schemas.UserCreate,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(require_permission(ResourceType.USER, PermissionType.WRITE))
):
    organization = crud.organizations.get_organization(db, user.organization_id)
    _check_create_user_permissions(user, organization, current_user)
    
    try:
        db_user = crud.users.create_user(db=db, user=user)
        if not db_user:
            raise HTTPException(status_code=400, detail="Failed to create user")
        return db_user
    except ValueError as e:
        # Handle duplicate email/username errors with user-friendly message
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.put("/{user_id}", response_model=schemas.UserResponse)
async def update_user(
    user_id: uuid.UUID,
    user_update: schemas.UserUpdate,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(require_permission(ResourceType.USER, PermissionType.WRITE))
):
    db_user = crud.users.get_user(db, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    _check_update_user_permissions(db_user, user_update, current_user)
    updated_user = crud.users.update_user(db, user_id, user_update)
    if not updated_user:
        raise HTTPException(status_code=400, detail="Failed to update user")
    return updated_user

@router.patch("/{user_id}/deactivate", response_model=schemas.UserResponse)
async def deactivate_user(
    user_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(require_permission(ResourceType.USER, PermissionType.WRITE))
):
    user_to_deactivate = crud.users.get_user(db, user_id)
    if not user_to_deactivate:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    # Check if user can manage this user (same organization or super admin)
    if not permission_checker.is_super_admin(current_user) and user_to_deactivate.organization_id != current_user.organization_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to deactivate this user")

    return crud.users.set_user_active_status(db, user_id, False)

@router.patch("/{user_id}/reactivate", response_model=schemas.UserResponse)
async def reactivate_user(
    user_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(require_permission(ResourceType.USER, PermissionType.WRITE))
):
    user_to_reactivate = crud.users.get_user(db, user_id)
    if not user_to_reactivate:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    if not permission_checker.is_super_admin(current_user) and user_to_reactivate.organization_id != current_user.organization_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to reactivate this user")

    return crud.users.set_user_active_status(db, user_id, True)

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(require_super_admin())
):
    result = crud.users.delete_user(db, user_id)
    if not result:
        raise HTTPException(status_code=404, detail="User not found or could not be deleted")
    return # A 204 response should not have a body.


# --- User Invitation Endpoints ---

@router.post("/invite", response_model=schemas.UserInvitationResponse, status_code=status.HTTP_201_CREATED)
async def invite_user(
    invitation: schemas.UserInvitationCreate,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(require_permission(ResourceType.USER, PermissionType.WRITE))
):
    """
    Send an invitation to a new user.
    Requirements: 2A.1, 2A.2, 2A.3
    """
    # Check if user already exists
    existing_user = crud.users.get_user_by_email(db, invitation.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="User with this email already exists"
        )
    
    # Validate organization exists
    organization = crud.organizations.get_organization(db, invitation.organization_id)
    if not organization:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Organization not found"
        )
    
    # Permission checks
    if current_user.role == "admin":
        # Admins can only invite users to their own organization
        if invitation.organization_id != current_user.organization_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only invite users to your own organization"
            )
        
        # Admins cannot invite super_admins
        if invitation.role == schemas.UserRoleEnum.SUPER_ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only super admins can invite other super admins"
            )
    
    # Super admins can invite to any organization, but super_admin role only to key organizations
    if invitation.role == schemas.UserRoleEnum.SUPER_ADMIN:
        if not _can_have_superadmin_users(organization):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Super admin role can only be assigned to key organizations (Oraseas EE, BossServ Ltd, BossAqua)"
            )
    
    # Create invitation
    try:
        invited_user = crud.users.create_user_invitation(db, invitation, current_user.user_id)
        
        # Get inviting user details for email
        inviting_user = crud.users.get_user(db, current_user.user_id)
        
        # Send invitation email asynchronously
        send_invitation_email.delay(
            email=invitation.email,
            name=invitation.name,
            invitation_token=invited_user.invitation_token,
            invited_by_name=inviting_user.name or inviting_user.username,
            organization_name=organization.name
        )
        
        return invited_user
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create invitation: {str(e)}"
        )

@router.post("/accept-invitation", response_model=schemas.UserResponse)
async def accept_invitation(
    acceptance: schemas.UserInvitationAcceptance,
    db: Session = Depends(get_db)
):
    """
    Accept a user invitation and complete account setup.
    Requirements: 2A.4, 2A.5
    """
    try:
        # Accept the invitation
        activated_user = crud.users.accept_user_invitation(
            db, 
            acceptance.invitation_token, 
            acceptance.username, 
            acceptance.password,
            acceptance.name
        )
        
        if not activated_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired invitation token"
            )
        
        # Get organization and inviting user details for notification
        organization = crud.organizations.get_organization(db, activated_user.organization_id)
        inviting_user = crud.users.get_user(db, activated_user.invited_by_user_id) if activated_user.invited_by_user_id else None
        
        # Send notification to the admin who invited the user
        if inviting_user and organization:
            send_invitation_accepted_notification.delay(
                admin_email=inviting_user.email,
                user_name=activated_user.name or activated_user.username,
                user_email=activated_user.email,
                organization_name=organization.name
            )
        
        return activated_user
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to accept invitation: {str(e)}"
        )

@router.post("/resend-invitation", response_model=schemas.UserInvitationResponse)
async def resend_invitation(
    resend_request: schemas.UserInvitationResend,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(has_roles(["super_admin", "admin"]))
):
    """
    Resend an invitation to a user.
    Requirements: 2A.4
    """
    # Get the user to resend invitation to
    user_to_resend = crud.users.get_user(db, resend_request.user_id)
    if not user_to_resend:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Check if user is in pending invitation status
    if user_to_resend.user_status != models.UserStatus.pending_invitation:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is not in pending invitation status"
        )
    
    # Permission checks
    if current_user.role == "admin":
        if user_to_resend.organization_id != current_user.organization_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only resend invitations for users in your organization"
            )
    
    # Resend invitation
    try:
        updated_user = crud.users.resend_user_invitation(db, resend_request.user_id, current_user.user_id)
        
        if not updated_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to resend invitation"
            )
        
        # Get organization and current user details for email
        organization = crud.organizations.get_organization(db, updated_user.organization_id)
        current_user_db = crud.users.get_user(db, current_user.user_id)
        
        # Send invitation email asynchronously
        send_invitation_email.delay(
            email=updated_user.email,
            name=updated_user.name,
            invitation_token=updated_user.invitation_token,
            invited_by_name=current_user_db.name or current_user_db.username,
            organization_name=organization.name
        )
        
        return updated_user
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to resend invitation: {str(e)}"
        )

@router.get("/{user_id}/invitation-audit", response_model=List[schemas.InvitationAuditLogResponse])
async def get_invitation_audit_logs(
    user_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(has_roles(["super_admin", "admin"]))
):
    """
    Get invitation audit logs for a specific user.
    Requirements: 2A.6
    """
    # Get the user to check permissions
    user = crud.users.get_user(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Permission checks
    if current_user.role == "admin":
        if user.organization_id != current_user.organization_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only view audit logs for users in your organization"
            )
    
    audit_logs = crud.users.get_invitation_audit_logs(db, user_id)
    return audit_logs

@router.get("/organization/{organization_id}/users", response_model=List[schemas.UserResponse])
async def get_users_by_organization(
    organization_id: uuid.UUID,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)
):
    """
    Get users filtered by organization.
    Regular users can only view users in their own organization.
    Admins can view users in their organization.
    Super admins can view users in any organization.
    """
    # Permission checks
    if current_user.role not in ["super_admin"]:
        # Regular users and admins can only view their own organization
        if organization_id != current_user.organization_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only view users in your organization"
            )
    
    users = crud.users.get_users_by_organization(db, organization_id, skip, limit)
    return users


# --- User Profile and Self-Service Management Endpoints ---
# /me/profile GET route moved above to fix routing conflict with /{user_id}

@router.put("/me/profile", response_model=schemas.UserProfileResponse)
async def update_my_profile(
    profile_update: schemas.UserProfileUpdate,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)
):
    """
    Update current user's profile information (name, email).
    Requirements: 2B.1, 2B.3
    """
    try:
        updated_user = crud.users.update_user_profile(db, current_user.user_id, profile_update)
        if not updated_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # If email was changed, send verification email (if email verification is enabled)
        if profile_update.email and hasattr(updated_user, 'pending_email') and updated_user.pending_email:
            send_email_verification_email.delay(
                email=updated_user.email,  # Send to current email
                name=updated_user.name,
                verification_token=updated_user.email_verification_token,
                new_email=updated_user.pending_email
            )
        
        # Return updated profile
        profile = crud.users.get_user_profile_with_organization(db, current_user.user_id)
        return profile
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update profile: {str(e)}"
        )

@router.post("/me/change-password")
async def change_my_password(
    password_change: schemas.UserPasswordChange,
    request: Request,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)
):
    """
    Change current user's password with current password validation.
    Requirements: 2B.2
    """
    try:
        success = crud.users.change_user_password(
            db, 
            current_user.user_id, 
            password_change.current_password, 
            password_change.new_password
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Get current session token for session management
        auth_header = request.headers.get("Authorization")
        current_token = None
        if auth_header and auth_header.startswith("Bearer "):
            current_token = auth_header.replace("Bearer ", "")
        
        # Terminate all other sessions except current one
        if current_token:
            terminated_count = session_manager.terminate_sessions_on_password_change(
                current_user.user_id, 
                current_token, 
                db
            )
            
            # Log security event
            session_manager.log_security_event(
                event_type="password_changed",
                user_id=current_user.user_id,
                details=f"Password changed, {terminated_count} other sessions terminated",
                risk_level="low",
                db=db
            )
        
        return {
            "message": "Password changed successfully",
            "sessions_terminated": terminated_count if current_token else 0
        }
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to change password: {str(e)}"
        )

@router.post("/request-password-reset")
async def request_password_reset(
    reset_request: schemas.PasswordResetRequest,
    db: Session = Depends(get_db)
):
    """
    Request password reset via email.
    Requirements: 2B.6
    """
    try:
        user = crud.users.request_password_reset(db, reset_request.email)
        
        # Always return success to prevent email enumeration attacks
        if user:
            send_password_reset_email.delay(
                email=user.email,
                name=user.name,
                reset_token=user.password_reset_token
            )
        
        return {"message": "If the email address exists, a password reset link has been sent"}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process password reset request"
        )

@router.post("/confirm-password-reset")
async def confirm_password_reset(
    reset_confirm: schemas.PasswordResetConfirm,
    db: Session = Depends(get_db)
):
    """
    Confirm password reset with token.
    Requirements: 2B.6
    """
    try:
        user = crud.users.confirm_password_reset(db, reset_confirm.reset_token, reset_confirm.new_password)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired reset token"
            )
        
        return {"message": "Password reset successfully"}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to reset password: {str(e)}"
        )

@router.post("/me/request-email-verification")
async def request_email_verification(
    email_request: schemas.EmailVerificationRequest,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)
):
    """
    Request email verification for email change.
    Requirements: 2B.3
    """
    try:
        user = crud.users.request_email_verification(db, current_user.user_id, email_request.new_email)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Send verification email to the new email address
        send_email_verification_email.delay(
            email=user.email,  # Current email for notification
            name=user.name,
            verification_token=user.email_verification_token,
            new_email=user.pending_email
        )
        
        return {"message": "Email verification link sent to the new email address"}
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to request email verification: {str(e)}"
        )

@router.post("/confirm-email-verification")
async def confirm_email_verification(
    verification_confirm: schemas.EmailVerificationConfirm,
    db: Session = Depends(get_db)
):
    """
    Confirm email verification with token.
    Requirements: 2B.3
    """
    try:
        user = crud.users.confirm_email_verification(db, verification_confirm.verification_token)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired verification token"
            )
        
        return {"message": "Email address updated successfully"}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to verify email: {str(e)}"
        )

@router.patch("/{user_id}/status", response_model=schemas.UserResponse)
async def update_user_status(
    user_id: uuid.UUID,
    status_update: schemas.UserAccountStatusUpdate,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(has_roles(["super_admin", "admin"]))
):
    """
    Update user account status.
    Requirements: 2B.5, 2C.3, 2C.4
    """
    # Get the user to update
    user_to_update = crud.users.get_user(db, user_id)
    if not user_to_update:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Permission checks
    if current_user.role == "admin":
        if user_to_update.organization_id != current_user.organization_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only update status for users in your organization"
            )
    
    try:
        updated_user = crud.users.update_user_status(db, user_id, status_update.user_status)
        
        if not updated_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to update user status"
            )
        
        return updated_user
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update user status: {str(e)}"
        )


# --- Advanced User Administration Backend (Task 3.4) ---
# /admin/search route moved above to fix routing conflict with /{user_id}

@router.patch("/{user_id}/deactivate-advanced", response_model=schemas.UserResponse)
async def deactivate_user_advanced(
    user_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(has_roles(["super_admin", "admin"]))
):
    """
    Deactivate user with immediate session termination and audit logging.
    Requirements: 2C.3
    """
    # Get the user to deactivate
    user_to_deactivate = crud.users.get_user(db, user_id)
    if not user_to_deactivate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Permission checks
    if current_user.role == "admin":
        if user_to_deactivate.organization_id != current_user.organization_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only deactivate users in your organization"
            )
    
    # Prevent self-deactivation
    if user_id == current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot deactivate your own account"
        )
    
    try:
        # Deactivate user with session termination and audit logging
        updated_user = crud.users.deactivate_user_with_session_termination(
            db=db,
            user_id=user_id,
            performed_by_user_id=current_user.user_id
        )
        
        if not updated_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to deactivate user"
            )
        
        return updated_user
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to deactivate user: {str(e)}"
        )

@router.patch("/{user_id}/reactivate-advanced", response_model=schemas.UserResponse)
async def reactivate_user_advanced(
    user_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(has_roles(["super_admin", "admin"]))
):
    """
    Reactivate user with notification system and audit logging.
    Requirements: 2C.4
    """
    # Get the user to reactivate
    user_to_reactivate = crud.users.get_user(db, user_id)
    if not user_to_reactivate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Permission checks
    if current_user.role == "admin":
        if user_to_reactivate.organization_id != current_user.organization_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only reactivate users in your organization"
            )
    
    try:
        # Reactivate user with notification and audit logging
        updated_user = crud.users.reactivate_user_with_notification(
            db=db,
            user_id=user_id,
            performed_by_user_id=current_user.user_id
        )
        
        if not updated_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to reactivate user"
            )
        
        # Get organization and admin details for notification
        organization = crud.organizations.get_organization(db, updated_user.organization_id)
        admin_user = crud.users.get_user(db, current_user.user_id)
        
        # Send reactivation notification email
        if organization and admin_user:
            send_user_reactivation_notification.delay(
                user_email=updated_user.email,
                user_name=updated_user.name or updated_user.username,
                admin_name=admin_user.name or admin_user.username,
                organization_name=organization.name
            )
        
        return updated_user
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to reactivate user: {str(e)}"
        )

@router.delete("/{user_id}/soft-delete", response_model=dict)
async def soft_delete_user(
    user_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(has_roles(["super_admin", "admin"]))
):
    """
    Soft delete user with transaction dependency checking.
    Requirements: 2C.5
    """
    # Get the user to delete
    user_to_delete = crud.users.get_user(db, user_id)
    if not user_to_delete:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Permission checks
    if current_user.role == "admin":
        if user_to_delete.organization_id != current_user.organization_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only delete users in your organization"
            )
    
    # Prevent self-deletion
    if user_id == current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot delete your own account"
        )
    
    try:
        # Check for transaction dependencies and perform soft delete
        result = crud.users.soft_delete_user_with_dependency_check(
            db=db,
            user_id=user_id,
            performed_by_user_id=current_user.user_id
        )
        
        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["message"]
            )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete user: {str(e)}"
        )

# /admin/inactive-users route moved above to fix routing conflict with /{user_id}

@router.get("/{user_id}/audit-logs", response_model=List[schemas.UserManagementAuditLogResponse])
async def get_user_management_audit_logs(
    user_id: uuid.UUID,
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(has_roles(["super_admin", "admin"]))
):
    """
    Get user management audit logs for a specific user.
    Requirements: 2C.7
    """
    # Get the user to check permissions
    user = crud.users.get_user(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Permission checks
    if current_user.role == "admin":
        if user.organization_id != current_user.organization_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only view audit logs for users in your organization"
            )
    
    try:
        audit_logs = crud.users.get_user_management_audit_logs(
            db=db,
            user_id=user_id,
            skip=skip,
            limit=limit
        )
        return audit_logs
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get audit logs: {str(e)}"
        )

# /admin/audit-logs route moved above to fix routing conflict with /{user_id}


# --- Session and Security Management Endpoints (Task 3.5) ---
# /me/sessions route moved above to fix routing conflict with /{user_id}

@router.delete("/me/sessions/{session_token}")
async def terminate_my_session(
    session_token: str,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)
):
    """
    Terminate a specific session for the current user.
    Requirements: 2D.5
    """
    from ..session_manager import session_manager
    
    try:
        # Verify the session belongs to the current user
        session_data = session_manager.get_session(session_token)
        if not session_data or session_data.get("user_id") != str(current_user.user_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found or does not belong to current user"
            )
        
        session_manager.terminate_session(session_token, "user_terminated", db)
        return {"message": "Session terminated successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to terminate session: {str(e)}"
        )

@router.delete("/me/sessions")
async def terminate_all_my_sessions(
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)
):
    """
    Terminate all sessions for the current user except the current one.
    Requirements: 2D.5
    """
    from ..session_manager import session_manager
    
    try:
        # Get current session token from the request (we'll need to modify this)
        # For now, terminate all sessions - in production, we'd exclude current session
        terminated_count = session_manager.terminate_all_user_sessions(
            current_user.user_id, "user_terminated_all", db
        )
        
        return {"message": f"Terminated {terminated_count} sessions"}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to terminate sessions: {str(e)}"
        )

@router.post("/logout")
async def logout(
    session_token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    """
    Logout and terminate the current session.
    Requirements: 2D.5
    """
    from ..session_manager import session_manager
    
    try:
        session_manager.terminate_session(session_token, "logout", db)
        return {"message": "Logged out successfully"}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to logout: {str(e)}"
        )

# /admin/security-events route moved above to fix routing conflict with /{user_id}

@router.patch("/{user_id}/unlock", response_model=schemas.UserResponse)
async def unlock_user_account(
    user_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(has_roles(["super_admin", "admin"]))
):
    """
    Manually unlock a user account.
    Requirements: 2D.4
    """
    # Get the user to unlock
    user_to_unlock = crud.users.get_user(db, user_id)
    if not user_to_unlock:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Permission checks
    if current_user.role == "admin":
        if user_to_unlock.organization_id != current_user.organization_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only unlock users in your organization"
            )
    
    try:
        # Unlock the user
        user_to_unlock.user_status = models.UserStatus.active
        user_to_unlock.locked_until = None
        user_to_unlock.failed_login_attempts = 0
        db.commit()
        db.refresh(user_to_unlock)
        
        # Clear Redis failed attempts
        from ..session_manager import session_manager
        session_manager.clear_failed_login_attempts(user_to_unlock.username, db)
        
        # Log security event
        session_manager.log_security_event(
            event_type="account_unlocked",
            user_id=user_to_unlock.id,
            details=f"Account manually unlocked by {current_user.username}",
            risk_level="low",
            db=db
        )
        
        return user_to_unlock
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to unlock user account: {str(e)}"
        )

@router.delete("/{user_id}/sessions")
async def terminate_user_sessions(
    user_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(has_roles(["super_admin", "admin"]))
):
    """
    Terminate all sessions for a specific user (admin function).
    Requirements: 2D.6
    """
    # Get the user
    user_to_terminate = crud.users.get_user(db, user_id)
    if not user_to_terminate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Permission checks
    if current_user.role == "admin":
        if user_to_terminate.organization_id != current_user.organization_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only terminate sessions for users in your organization"
            )
    
    try:
        from ..session_manager import session_manager
        
        terminated_count = session_manager.terminate_all_user_sessions(
            user_id, "admin_terminated", db
        )
        
        # Log security event
        session_manager.log_security_event(
            event_type="sessions_terminated",
            user_id=user_id,
            details=f"All sessions terminated by admin {current_user.username}",
            risk_level="medium",
            db=db
        )
        
        return {"message": f"Terminated {terminated_count} sessions for user"}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to terminate user sessions: {str(e)}"
        )
