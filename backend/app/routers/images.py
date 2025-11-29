# backend/app/routers/images.py

import uuid
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import Response
from sqlalchemy.orm import Session

from .. import models
from ..database import get_db
from ..auth import get_current_user, TokenData

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
    """
    user = db.query(models.User).filter(models.User.id == user_id).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if not user.profile_photo_data:
        raise HTTPException(status_code=404, detail="Profile photo not found")
    
    return Response(
        content=user.profile_photo_data,
        media_type="image/webp",
        headers={
            "Cache-Control": "public, max-age=3600",  # Cache for 1 hour
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
    """
    org = db.query(models.Organization).filter(models.Organization.id == org_id).first()
    
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    
    if not org.logo_data:
        raise HTTPException(status_code=404, detail="Logo not found")
    
    return Response(
        content=org.logo_data,
        media_type="image/webp",
        headers={
            "Cache-Control": "public, max-age=3600",
            "Content-Disposition": f'inline; filename="logo_{org_id}.webp"'
        }
    )


@router.get("/images/parts/{part_id}", tags=["Images"])
async def get_part_image(
    part_id: uuid.UUID,
    index: int = Query(0, ge=0, description="Image index (0-based)"),
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)
):
    """
    Serve part image from database by index.
    Returns WebP image or 404 if not found.
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
    current_user: TokenData = Depends(get_current_user)
):
    """
    Get the number of images available for a part.
    """
    part = db.query(models.Part).filter(models.Part.id == part_id).first()
    
    if not part:
        raise HTTPException(status_code=404, detail="Part not found")
    
    count = len(part.image_data) if part.image_data else 0
    
    return {"part_id": part_id, "image_count": count}
