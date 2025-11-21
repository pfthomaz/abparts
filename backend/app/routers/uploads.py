# backend/app/routers/uploads.py

import os
import uuid
import shutil
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.orm import Session

from .. import schemas, models
from ..database import get_db
from ..auth import get_current_user, TokenData
from ..permissions import require_admin, permission_checker

router = APIRouter()

# Upload directory configuration
UPLOAD_DIRECTORY = "/app/static/images"
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

# Ensure upload directory exists
os.makedirs(UPLOAD_DIRECTORY, exist_ok=True)


def validate_image_file(file: UploadFile) -> None:
    """Validate uploaded image file"""
    # Check file extension
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file type. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"
        )


async def save_uploaded_file(file: UploadFile, prefix: str = "upload") -> str:
    """Save uploaded file and return the URL path"""
    validate_image_file(file)
    
    # Generate unique filename
    file_ext = Path(file.filename).suffix.lower()
    unique_filename = f"{prefix}_{uuid.uuid4()}{file_ext}"
    file_path = os.path.join(UPLOAD_DIRECTORY, unique_filename)
    
    # Save file
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save file: {str(e)}"
        )
    
    # Return relative URL path
    return f"/static/images/{unique_filename}"


@router.post("/users/profile-photo", response_model=schemas.ImageUploadResponse, tags=["Users"])
async def upload_user_profile_photo(
    file: UploadFile = File(...),
    current_user: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Upload a profile photo for the current user.
    Users can only upload their own profile photo.
    """
    # Save the file
    photo_url = await save_uploaded_file(file, prefix="profile")
    
    # Update user's profile_photo_url
    user = db.query(models.User).filter(models.User.id == current_user.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user.profile_photo_url = photo_url
    db.commit()
    
    return schemas.ImageUploadResponse(url=photo_url)


@router.delete("/users/profile-photo", tags=["Users"])
async def delete_user_profile_photo(
    current_user: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Remove the profile photo for the current user.
    """
    user = db.query(models.User).filter(models.User.id == current_user.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Delete the file if it exists
    if user.profile_photo_url:
        file_path = os.path.join("/app", user.profile_photo_url.lstrip("/"))
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except Exception as e:
                print(f"Failed to delete file: {e}")
    
    user.profile_photo_url = None
    db.commit()
    
    return {"message": "Profile photo removed successfully"}


@router.post("/organizations/{organization_id}/logo", response_model=schemas.ImageUploadResponse, tags=["Organizations"])
async def upload_organization_logo(
    organization_id: uuid.UUID,
    file: UploadFile = File(...),
    current_user: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Upload a logo for an organization.
    Only admins of the organization or super admins can upload logos.
    """
    # Check if organization exists
    organization = db.query(models.Organization).filter(models.Organization.id == organization_id).first()
    if not organization:
        raise HTTPException(status_code=404, detail="Organization not found")
    
    # Check permissions: must be admin of this organization or super admin
    is_super_admin = permission_checker.is_super_admin(current_user)
    is_org_admin = (
        permission_checker.is_admin(current_user) and 
        current_user.organization_id == organization_id
    )
    
    if not (is_super_admin or is_org_admin):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only organization admins can upload organization logos"
        )
    
    # Save the file
    logo_url = await save_uploaded_file(file, prefix="org_logo")
    
    # Update organization's logo_url
    organization.logo_url = logo_url
    db.commit()
    
    return schemas.ImageUploadResponse(url=logo_url)


@router.delete("/organizations/{organization_id}/logo", tags=["Organizations"])
async def delete_organization_logo(
    organization_id: uuid.UUID,
    current_user: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Remove the logo for an organization.
    Only admins of the organization or super admins can remove logos.
    """
    # Check if organization exists
    organization = db.query(models.Organization).filter(models.Organization.id == organization_id).first()
    if not organization:
        raise HTTPException(status_code=404, detail="Organization not found")
    
    # Check permissions
    is_super_admin = permission_checker.is_super_admin(current_user)
    is_org_admin = (
        permission_checker.is_admin(current_user) and 
        current_user.organization_id == organization_id
    )
    
    if not (is_super_admin or is_org_admin):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only organization admins can remove organization logos"
        )
    
    # Delete the file if it exists
    if organization.logo_url:
        file_path = os.path.join("/app", organization.logo_url.lstrip("/"))
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except Exception as e:
                print(f"Failed to delete file: {e}")
    
    organization.logo_url = None
    db.commit()
    
    return {"message": "Organization logo removed successfully"}
