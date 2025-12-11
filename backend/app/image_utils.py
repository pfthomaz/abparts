# backend/app/image_utils.py

import io
from PIL import Image
from fastapi import HTTPException, UploadFile

# Allowed image formats
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
MAX_IMAGE_SIZE_KB = 500


async def compress_and_optimize_image(
    file: UploadFile,
    max_size_kb: int = MAX_IMAGE_SIZE_KB,
    max_dimension: int = 1024,
    quality: int = 85
) -> bytes:
    """
    Compress and optimize an uploaded image for database storage.
    
    Args:
        file: The uploaded image file
        max_size_kb: Maximum size in kilobytes (default 500KB)
        max_dimension: Maximum width/height in pixels (default 1024)
        quality: WebP quality 1-100 (default 85)
    
    Returns:
        bytes: Optimized image data in WebP format
    
    Raises:
        HTTPException: If image is invalid or too large after compression
    """
    try:
        # Read the uploaded file
        contents = await file.read()
        
        # Open image with PIL
        image = Image.open(io.BytesIO(contents))
        
        # Convert RGBA to RGB if necessary (for WebP compatibility)
        if image.mode in ('RGBA', 'LA', 'P'):
            background = Image.new('RGB', image.size, (255, 255, 255))
            if image.mode == 'P':
                image = image.convert('RGBA')
            background.paste(image, mask=image.split()[-1] if image.mode in ('RGBA', 'LA') else None)
            image = background
        elif image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Resize if image is too large
        if max(image.size) > max_dimension:
            image.thumbnail((max_dimension, max_dimension), Image.Resampling.LANCZOS)
        
        # Try different quality levels to meet size requirement
        for attempt_quality in [quality, 75, 60, 50, 40]:
            output = io.BytesIO()
            image.save(output, format='WEBP', quality=attempt_quality, optimize=True)
            image_bytes = output.getvalue()
            
            size_kb = len(image_bytes) / 1024
            
            if size_kb <= max_size_kb:
                return image_bytes
        
        # If still too large, raise error
        raise HTTPException(
            status_code=400,
            detail=f"Image too large even after compression. Size: {size_kb:.1f}KB, Max: {max_size_kb}KB. Please use a smaller image."
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid image file: {str(e)}"
        )


def validate_image_file(file: UploadFile) -> None:
    """Validate that the uploaded file is an allowed image type"""
    from pathlib import Path
    
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type '{file_ext}'. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"
        )


def image_to_data_url(image_bytes: bytes, format: str = "webp") -> str:
    """Convert image bytes to data URL for immediate display"""
    import base64
    base64_image = base64.b64encode(image_bytes).decode('utf-8')
    return f"data:image/{format};base64,{base64_image}"
