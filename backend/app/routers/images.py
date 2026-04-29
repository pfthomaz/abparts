# backend/app/routers/images.py

import uuid
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import Response
from sqlalchemy.orm import Session

from .. import models
from ..database import get_db
from ..auth import get_current_user, TokenData
from ..permissions import (
    permission_checker,
    require_permission,
    ResourceType,
    PermissionType,
    check_organization_access
)

router = APIRouter()


@router.get("/images/users/{user_id}/profile", tags=["Images"])
async def get_user_profile_photo(
    user_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)
):
    """
    Serve user profile photo from database.
    Returns WebP image or 404 if not found.
    Requires the requesting user to own the profile or have admin/super-admin rights.
    """
    user = db.query(models.User).filter(models.User.id == user_id).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if not user.profile_photo_data:
        raise HTTPException(status_code=404, detail="Profile photo not found")

    if user.id != current_user.user_id:
        same_org = user.organization_id and current_user.organization_id == user.organization_id
        if not (permission_checker.is_super_admin(current_user) or (permission_checker.is_admin(current_user) and same_org)):
            raise HTTPException(status_code=403, detail="Not authorized to view this profile photo")
    
    return Response(
        content=user.profile_photo_data,
        media_type="image/webp",
        headers={
            "Cache-Control": "public, max-age=31536000, immutable",  # Cache for 1 year (safe with cache-busting)
            "Content-Disposition": f'inline; filename="profile_{user_id}.webp"'
        }
    )


@router.get("/images/organizations/{org_id}/logo", tags=["Images"])
async def get_organization_logo(
    org_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)
):
    """
    Serve organization logo from database.
    Returns WebP image or 404 if not found.
    Only accessible to users with organization access or super-admin privileges.
    """
    org = db.query(models.Organization).filter(models.Organization.id == org_id).first()
    
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    
    if not org.logo_data:
        raise HTTPException(status_code=404, detail="Logo not found")

    if not (permission_checker.is_super_admin(current_user) or check_organization_access(current_user, org_id, db)):
        raise HTTPException(status_code=403, detail="Not authorized to view this organization logo")
    
    return Response(
        content=org.logo_data,
        media_type="image/webp",
        headers={
            "Cache-Control": "public, max-age=31536000, immutable",  # Cache for 1 year (safe with cache-busting)
            "Content-Disposition": f'inline; filename="logo_{org_id}.webp"'
        }
    )


@router.get("/images/parts/{part_id}", tags=["Images"])
async def get_part_image(
    part_id: uuid.UUID,
    index: int = Query(0, ge=0, description="Image index (0-based)"),
    db: Session = Depends(get_db),
    _current_user: TokenData = Depends(require_permission(ResourceType.PART, PermissionType.READ))
):
    """
    Serve part image from database by index.
    Returns WebP image or 404 if not found.
    Uses the existing parts READ permission checks for authorization.
    """
    part = db.query(models.Part).filter(models.Part.id == part_id).first()
    
    if not part:
        raise HTTPException(status_code=404, detail="Part not found")
    
    if not part.image_data or index >= len(part.image_data):
        raise HTTPException(status_code=404, detail="Image not found")
    
    return Response(
        content=part.image_data[index],
        media_type="image/webp",
        headers={
            "Cache-Control": "public, max-age=86400",  # Cache for 24 hours
            "Content-Disposition": f'inline; filename="part_{part_id}_{index}.webp"'
        }
    )


@router.get("/images/parts/{part_id}/count", tags=["Images"])
async def get_part_image_count(
    part_id: uuid.UUID,
    db: Session = Depends(get_db),
    _current_user: TokenData = Depends(require_permission(ResourceType.PART, PermissionType.READ))
):
    """
    Get the number of images available for a part.
    Uses the existing parts READ permission checks for authorization.
    """
    part = db.query(models.Part).filter(models.Part.id == part_id).first()
    
    if not part:
        raise HTTPException(status_code=404, detail="Part not found")
    
    count = len(part.image_data) if part.image_data else 0
    
    return {"part_id": part_id, "image_count": count}
