# backend/app/routers/parts.py

import uuid
from typing import List
import os
import shutil # For saving files
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File # New: UploadFile, File
from sqlalchemy.orm import Session

from .. import schemas, crud # Import schemas and CRUD functions
from ..database import get_db # Import DB session dependency
from ..auth import get_current_user, has_role, has_roles, TokenData # Import authentication dependencies

router = APIRouter()

# Define the directory where uploaded images will be stored
# IMPORTANT: In a production environment, this should be a cloud storage service like AWS S3.
# For local Docker, this path needs to be accessible/writable.
UPLOAD_DIRECTORY = "/app/static/images" # This path inside the container

# Ensure the upload directory exists
os.makedirs(UPLOAD_DIRECTORY, exist_ok=True)


# --- Image Upload Endpoint ---
@router.post("/upload-image", response_model=schemas.ImageUploadResponse, tags=["Images"]) # Define a new schema for this response
async def upload_image(
    file: UploadFile = File(...),
    current_user: TokenData = Depends(has_role("Oraseas Admin")) # Only Oraseas Admin can upload images
):
    """
    Uploads an image file and returns its URL.
    This is a temporary local storage solution for development.
    In production, files should be stored on a cloud storage service (e.g., AWS S3).
    """
    try:
        # Generate a unique filename
        filename = f"{uuid.uuid4()}_{file.filename}"
        file_path = os.path.join(UPLOAD_DIRECTORY, filename)

        # Save the file locally
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Construct the URL (assuming /static/images is served)
        # This assumes your FastAPI app serves static files from /static
        image_url = f"/static/images/{filename}"
        return {"url": image_url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Could not upload file: {e}")

# --- Parts CRUD ---
@router.get("/", response_model=List[schemas.PartResponse])
async def get_parts(
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user) # All authenticated users can view parts
):
    parts = crud.parts.get_parts(db)
    return parts

@router.get("/{part_id}", response_model=schemas.PartResponse)
async def get_part(
    part_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user) # All authenticated users can view parts
):
    part = crud.parts.get_part(db, part_id)
    if not part:
        raise HTTPException(status_code=404, detail="Part not found")
    return part

@router.post("/", response_model=schemas.PartResponse, status_code=status.HTTP_201_CREATED)
async def create_part(
    part: schemas.PartCreate, # Now expects image_urls
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(has_role("Oraseas Admin")) # Only Oraseas Admin can create parts
):
    db_part = crud.parts.create_part(db, part)
    if not db_part:
        raise HTTPException(status_code=400, detail="Failed to create part")
    return db_part

@router.put("/{part_id}", response_model=schemas.PartResponse)
async def update_part(
    part_id: uuid.UUID,
    part_update: schemas.PartUpdate, # Now expects image_urls
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(has_role("Oraseas Admin")) # Only Oraseas Admin can update parts
):
    updated_part = crud.parts.update_part(db, part_id, part_update)
    if not updated_part:
        raise HTTPException(status_code=404, detail="Part not found")
    return updated_part

@router.delete("/{part_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_part(
    part_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(has_role("Oraseas Admin")) # Only Oraseas Admin can delete parts
):
    result = crud.parts.delete_part(db, part_id)
    if not result:
        raise HTTPException(status_code=404, detail="Part not found or could not be deleted")
    return result
