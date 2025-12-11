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
from ..image_utils import compress_and_optimize_image, validate_image_file, image_to_data_url

router = APIRouter()

# Legacy upload directory (for migration only)
UPLOAD_DIRECTORY = "/app/static/images"
os.makedirs(UPLOAD_DIRECTORY, exist_ok=True)


@router.post("/users/profile-photo", response_model=schemas.ImageUploadResponse, tags=["Users"])
async def upload_user_profile_photo(
    file: UploadFile = File(...),
    current_user: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Upload a profile photo for the current user.
    Image is compressed and stored in database.
    """
    validate_image_file(file)
    
    # Compress and optimize image
    image_bytes = await compress_and_optimize_image(file, max_size_kb=500)
    
    # Update user's profile photo in database
    user = db.query(models.User).filter(models.User.id == current_user.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user.profile_photo_data = image_bytes
    user.profile_photo_url = None  # Clear legacy URL
    db.commit()
    
    # Return data URL for immediate display
    data_url = image_to_data_url(image_bytes)
    return schemas.ImageUploadResponse(url=data_url)


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
    
    user.profile_photo_data = None
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
    Image is compressed and stored in database.
    """
    validate_image_file(file)
    
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
    
    # Compress and optimize image
    image_bytes = await compress_and_optimize_image(file, max_size_kb=500)
    
    # Update organization's logo in database
    organization.logo_data = image_bytes
    organization.logo_url = None  # Clear legacy URL
    db.commit()
    
    # Return data URL for immediate display
    data_url = image_to_data_url(image_bytes)
    return schemas.ImageUploadResponse(url=data_url)


@router.delete("/organizations/{organization_id}/logo", tags=["Organizations"])
async def delete_organization_logo(
    organization_id: uuid.UUID,
    current_user: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Remove the logo for an organization.
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
    
    organization.logo_data = None
    organization.logo_url = None
    db.commit()
    
    return {"message": "Organization logo removed successfully"}
