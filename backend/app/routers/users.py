# backend/app/routers/users.py

import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .. import schemas, crud, models # Import schemas, CRUD functions, and models
from ..database import get_db # Import DB session dependency
from ..auth import get_current_user, has_role, has_roles, TokenData # Import authentication dependencies
from ..tasks import send_invitation_email, send_invitation_accepted_notification

router = APIRouter()

def _check_update_user_permissions(user_to_update: models.User, user_update: schemas.UserUpdate, current_user: TokenData):
    """Helper to centralize complex permission checks for updating a user."""
    is_oraseas_admin = current_user.role == "Oraseas Admin"
    is_customer_admin_in_own_org = (
        current_user.role == "Customer Admin" and
        user_to_update.organization_id == current_user.organization_id
    )
    is_self_update = user_to_update.id == current_user.user_id

    if is_oraseas_admin:
        return # Oraseas Admin has full permissions

    if user_update.organization_id is not None and user_update.organization_id != user_to_update.organization_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You cannot change a user's organization.")
    
    if user_update.role is not None and user_update.role != user_to_update.role:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You cannot change a user's role.")

    if not (is_customer_admin_in_own_org or is_self_update):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update this user")

def _check_create_user_permissions(user_to_create: schemas.UserCreate, organization: models.Organization, current_user: TokenData):
    """Helper to centralize permission checks for creating a user."""
    if not organization:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Organization ID not found")

    if current_user.role == "Customer Admin":
        if user_to_create.organization_id != current_user.organization_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Customer Admin can only create users within their own organization")
        if user_to_create.role not in ["Customer Admin", "Customer User"]:
             raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Customer Admin can only create 'Customer Admin' or 'Customer User' roles.")

    if current_user.role == "Oraseas Admin":
        if user_to_create.role == "Oraseas Admin" and organization.type != "Warehouse":
             raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot assign 'Oraseas Admin' role to non-Warehouse organization user.")


# --- Users CRUD ---
@router.get("/", response_model=List[schemas.UserResponse])
async def get_users(
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(has_role("Oraseas Admin")) # Only Oraseas Admin can list all users
):
    users = crud.users.get_users(db)
    return users

@router.get("/{user_id}", response_model=schemas.UserResponse)
async def get_user(
    user_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)
):
    user = crud.users.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if current_user.role == "Oraseas Admin" or user_id == current_user.user_id:
        return user
    else:
        raise HTTPException(status_code=403, detail="Not authorized to view this user's details")

@router.post("/", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user: schemas.UserCreate,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(has_roles(["Oraseas Admin", "Customer Admin"])) # Admin roles can create users
):
    organization = crud.organizations.get_organization(db, user.organization_id)
    _check_create_user_permissions(user, organization, current_user)
    db_user = crud.users.create_user(db=db, user=user)
    if not db_user:
        raise HTTPException(status_code=400, detail="Failed to create user")
    return db_user

@router.put("/{user_id}", response_model=schemas.UserResponse)
async def update_user(
    user_id: uuid.UUID,
    user_update: schemas.UserUpdate,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(has_roles(["Oraseas Admin", "Customer Admin", "Customer User"]))
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
    current_user: TokenData = Depends(has_roles(["Oraseas Admin", "Customer Admin"]))
):
    user_to_deactivate = crud.users.get_user(db, user_id)
    if not user_to_deactivate:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    if current_user.role == "Customer Admin" and user_to_deactivate.organization_id != current_user.organization_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to deactivate this user")

    return crud.users.set_user_active_status(db, user_id, False)

@router.patch("/{user_id}/reactivate", response_model=schemas.UserResponse)
async def reactivate_user(
    user_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(has_roles(["Oraseas Admin", "Customer Admin"]))
):
    user_to_reactivate = crud.users.get_user(db, user_id)
    if not user_to_reactivate:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    if current_user.role == "Customer Admin" and user_to_reactivate.organization_id != current_user.organization_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to reactivate this user")

    return crud.users.set_user_active_status(db, user_id, True)

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(has_role("Oraseas Admin"))
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
    current_user: TokenData = Depends(has_roles(["super_admin", "admin"]))
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
    
    # Super admins can invite to any organization, but super_admin role only to Oraseas EE
    if invitation.role == schemas.UserRoleEnum.SUPER_ADMIN:
        if organization.organization_type != models.OrganizationType.ORASEAS_EE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Super admin role can only be assigned to Oraseas EE organization"
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

@router.get("/pending-invitations", response_model=List[schemas.UserInvitationResponse])
async def get_pending_invitations(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(has_roles(["super_admin", "admin"]))
):
    """
    Get pending invitations.
    Requirements: 2A.6
    """
    organization_id = None
    
    # Admins can only see invitations for their organization
    if current_user.role == "admin":
        organization_id = current_user.organization_id
    
    pending_invitations = crud.users.get_pending_invitations(db, organization_id, skip, limit)
    return pending_invitations

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
    current_user: TokenData = Depends(has_roles(["super_admin", "admin"]))
):
    """
    Get users filtered by organization.
    """
    # Permission checks
    if current_user.role == "admin":
        if organization_id != current_user.organization_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only view users in your organization"
            )
    
    users = crud.users.get_users_by_organization(db, organization_id, skip, limit)
    return users
