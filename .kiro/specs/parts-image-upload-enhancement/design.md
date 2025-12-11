# Design Document

## Overview

This design fixes the existing parts image upload system to work properly on the VM using bind mounts instead of named Docker volumes. The current implementation works in the local development environment with named volumes but fails on the VM where bind mounts are used for persistent storage.

The main issue is that the current system assumes a named volume (`api_static_images_prod:/app/static/images`) but the VM uses a bind mount to a specific directory on the host file system. This design addresses the configuration differences and ensures proper file permissions, directory creation, and path handling for the VM environment.

## Architecture

### Current vs Target Architecture

**Current (Working in Dev)**:
```
Local Dev: Named Volume
docker-compose.yml: api_static_images_prod:/app/static/images
Container: /app/static/images/ (managed by Docker)
```

**Target (VM with Bind Mount)**:
```
VM Production: Bind Mount
docker-compose.yml: /host/path/to/images:/app/static/images
Container: /app/static/images/ (mapped to host directory)
Host VM: /host/path/to/images/ (actual file storage)
```

### Directory Structure

The system will use a simple, reliable directory structure:

```
/app/static/images/          # Container path (mapped to host)
├── parts/                   # Parts images directory
│   ├── {uuid1}_{filename}   # Unique filename format
│   ├── {uuid2}_{filename}   # Prevents conflicts
│   └── ...
└── .gitkeep                 # Ensures directory exists
```

### Key Issues to Address

1. **File Permissions**: Ensure container can write to bind-mounted directory
2. **Directory Creation**: Handle directory creation when bind mount is empty
3. **Path Validation**: Verify paths work correctly with bind mounts
4. **Static File Serving**: Ensure FastAPI can serve files from bind mount
5. **Error Handling**: Proper error messages for permission/storage issues

## Components and Interfaces

### 1. Enhanced Upload Directory Management

**Purpose**: Ensure upload directory works with both named volumes and bind mounts

```python
class UploadDirectoryManager:
    def __init__(self, base_path: str = "/app/static/images"):
        self.base_path = Path(base_path)
        self.parts_dir = self.base_path / "parts"
    
    def initialize_directories(self) -> bool:
        """Create necessary directories with proper permissions"""
        try:
            self.base_path.mkdir(parents=True, exist_ok=True)
            self.parts_dir.mkdir(parents=True, exist_ok=True)
            
            # Create .gitkeep to ensure directory persists
            gitkeep = self.base_path / ".gitkeep"
            if not gitkeep.exists():
                gitkeep.touch()
                
            return True
        except PermissionError as e:
            logger.error(f"Permission denied creating directories: {e}")
            return False
        except Exception as e:
            logger.error(f"Failed to create directories: {e}")
            return False
    
    def check_permissions(self) -> Dict[str, bool]:
        """Check read/write permissions on directories"""
        return {
            "base_readable": os.access(self.base_path, os.R_OK),
            "base_writable": os.access(self.base_path, os.W_OK),
            "parts_readable": os.access(self.parts_dir, os.R_OK),
            "parts_writable": os.access(self.parts_dir, os.W_OK),
        }
```

### 2. Improved File Upload Handler

**Purpose**: Handle file uploads with better error handling for VM environment

```python
async def upload_image_enhanced(
    file: UploadFile = File(...),
    current_user: TokenData = Depends(require_super_admin())
):
    """Enhanced image upload with VM compatibility"""
    
    # Initialize directory manager
    dir_manager = UploadDirectoryManager()
    
    # Check if directories exist and are writable
    if not dir_manager.initialize_directories():
        raise HTTPException(
            status_code=500,
            detail="Storage system not available. Check directory permissions."
        )
    
    permissions = dir_manager.check_permissions()
    if not all(permissions.values()):
        raise HTTPException(
            status_code=500,
            detail=f"Insufficient permissions: {permissions}"
        )
    
    # Validate file
    if not file.filename or file.filename.strip() == "":
        raise HTTPException(status_code=400, detail="No file selected")
    
    # Generate unique filename
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in ['.jpg', '.jpeg', '.png', '.webp']:
        raise HTTPException(
            status_code=400, 
            detail=f"Unsupported file type: {file_ext}"
        )
    
    unique_filename = f"{uuid.uuid4()}_{file.filename}"
    file_path = dir_manager.parts_dir / unique_filename
    
    try:
        # Save file with proper error handling
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Verify file was written
        if not file_path.exists():
            raise HTTPException(
                status_code=500,
                detail="File upload failed - file not found after write"
            )
        
        # Get file size
        file_size = file_path.stat().st_size
        
        return {
            "filename": file.filename,
            "stored_filename": unique_filename,
            "content_type": file.content_type,
            "size": file_size,
            "url": f"/static/images/parts/{unique_filename}",
            "storage_path": str(file_path)
        }
        
    except PermissionError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Permission denied writing file: {str(e)}"
        )
    except OSError as e:
        raise HTTPException(
            status_code=507,
            detail=f"Storage error: {str(e)}"
        )
    except Exception as e:
        # Cleanup partial file if it exists
        if file_path.exists():
            try:
                file_path.unlink()
            except:
                pass
        raise HTTPException(
            status_code=500,
            detail=f"Upload failed: {str(e)}"
        )
```

### 3. Static File Serving Configuration

**Purpose**: Ensure static files are served correctly from bind mount

```python
# In main.py - Enhanced static file mounting
from fastapi.staticfiles import StaticFiles
from pathlib import Path

# Verify static directory exists before mounting
STATIC_DIR = Path("/app/static")
IMAGES_DIR = STATIC_DIR / "images"

# Create directories if they don't exist
STATIC_DIR.mkdir(parents=True, exist_ok=True)
IMAGES_DIR.mkdir(parents=True, exist_ok=True)

# Mount static files with error handling
try:
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
    logger.info(f"Static files mounted from: {STATIC_DIR}")
except Exception as e:
    logger.error(f"Failed to mount static files: {e}")
    # Continue without static mounting - will be handled by error responses
```

## Data Models

### Enhanced Schemas

```python
class ImageMetadata(BaseModel):
    id: UUID
    original_filename: str
    stored_filename: str
    file_size: int
    content_type: str
    dimensions: Tuple[int, int]
    upload_timestamp: datetime
    part_id: Optional[UUID]
    thumbnail_path: Optional[str]
    
class ImageUploadResult(BaseModel):
    success: bool
    image_metadata: Optional[ImageMetadata]
    url: Optional[str]
    thumbnail_url: Optional[str]
    errors: List[str] = []

class MultipleImageUploadResult(BaseModel):
    total_files: int
    successful_uploads: int
    failed_uploads: int
    results: List[ImageUploadResult]
    upload_session_id: UUID

class ValidationResult(BaseModel):
    valid: bool
    errors: List[str] = []
    warnings: List[str] = []
    file_info: Optional[Dict[str, Any]] = None
```

### Database Integration

**New database fields for parts table**:
```python
# Add to existing Part model
class Part(Base):
    # ... existing fields ...
    image_urls: List[str] = []  # JSON array of image URLs
    primary_image_url: Optional[str] = None
    image_count: int = 0
    last_image_update: Optional[datetime] = None
```

## Error Handling

### Validation Errors

```python
class ImageValidationError(HTTPException):
    def __init__(self, detail: str, errors: List[str]):
        super().__init__(
            status_code=400,
            detail={
                "message": detail,
                "errors": errors,
                "error_type": "validation_error"
            }
        )

class FileSizeError(ImageValidationError):
    def __init__(self, file_size: int, max_size: int):
        super().__init__(
            f"File too large: {file_size} bytes (max: {max_size} bytes)",
            [f"File size {file_size:,} bytes exceeds maximum {max_size:,} bytes"]
        )
```

### Storage Errors

```python
class StorageError(HTTPException):
    def __init__(self, detail: str):
        super().__init__(
            status_code=507,
            detail={
                "message": "Storage operation failed",
                "detail": detail,
                "error_type": "storage_error"
            }
        )
```

### Error Recovery

- **Partial Upload Failures**: Continue processing valid files, report failures
- **Storage Failures**: Cleanup partial uploads, return detailed error information
- **Validation Failures**: Provide specific feedback for each validation rule
- **Permission Errors**: Log security events, return generic error to user

## Testing Strategy

### Unit Tests

1. **File Validation Tests**
   - Valid image file types (JPEG, PNG, WebP)
   - Invalid file types (PDF, TXT, executable files)
   - File size validation (under/over limits)
   - Corrupted image file handling
   - Malicious file detection

2. **Storage Manager Tests**
   - Directory creation and permissions
   - File storage and retrieval
   - Unique filename generation
   - Cleanup operations
   - Error handling for disk full scenarios

3. **Image Processing Tests**
   - Thumbnail generation for various formats
   - Image optimization quality and size
   - Handling of various image dimensions
   - Error handling for corrupted images

### Integration Tests

1. **API Endpoint Tests**
   - Single image upload workflow
   - Multiple image upload workflow
   - Image replacement workflow
   - Image deletion workflow
   - Error response validation

2. **Database Integration Tests**
   - Part-image relationship management
   - Metadata persistence and retrieval
   - Cleanup of orphaned records

3. **File System Integration Tests**
   - Docker volume mount functionality
   - File persistence across container restarts
   - Directory structure maintenance
   - Static file serving

### Performance Tests

1. **Load Testing**
   - Concurrent image uploads
   - Large file upload handling
   - Multiple file upload performance
   - Static file serving performance

2. **Storage Tests**
   - Disk space monitoring
   - File system performance under load
   - Cleanup operation efficiency

## Security Considerations

### File Validation Security

1. **Content-Type Validation**: Verify actual file content matches declared type
2. **Magic Number Checking**: Use file signatures to detect file type spoofing
3. **Image Content Scanning**: Validate image headers and structure
4. **Filename Sanitization**: Remove dangerous characters and path traversal attempts

### Access Control

1. **Upload Permissions**: Only super_admin users can upload images
2. **View Permissions**: All authenticated users can view images
3. **Delete Permissions**: Only super_admin users can delete images
4. **Directory Traversal Protection**: Validate all file paths

### Storage Security

1. **Unique Filenames**: Prevent filename conflicts and guessing
2. **Secure Directory Structure**: Organize files to prevent unauthorized access
3. **File Permissions**: Set appropriate file system permissions
4. **Cleanup Procedures**: Regular cleanup of temporary and orphaned files

## Performance Optimizations

### File Handling

1. **Streaming Uploads**: Process files without loading entirely into memory
2. **Async Operations**: Use async I/O for file operations
3. **Thumbnail Generation**: Generate thumbnails asynchronously
4. **Image Optimization**: Compress images for web delivery

### Caching Strategy

1. **Static File Caching**: Set appropriate HTTP cache headers
2. **Metadata Caching**: Cache image metadata in Redis
3. **Thumbnail Caching**: Aggressive caching for thumbnail images

### Storage Optimization

1. **Directory Sharding**: Organize files to prevent large directory issues
2. **Cleanup Scheduling**: Regular cleanup of temporary files
3. **Compression**: Use appropriate image compression for storage efficiency

## VM Deployment Configuration

### Docker Compose Changes for VM

**Current (Named Volume)**:
```yaml
volumes:
  - api_static_images_prod:/app/static/images
```

**Target (Bind Mount for VM)**:
```yaml
volumes:
  - /var/lib/abparts/static/images:/app/static/images
```

### Host Directory Setup

**On the VM host, create the directory structure**:
```bash
# Create the host directory
sudo mkdir -p /var/lib/abparts/static/images/parts

# Set proper ownership (assuming container runs as user 1000)
sudo chown -R 1000:1000 /var/lib/abparts/static/images

# Set proper permissions
sudo chmod -R 755 /var/lib/abparts/static/images

# Create .gitkeep to ensure directory persists
sudo touch /var/lib/abparts/static/images/.gitkeep
```

### Environment Variables

```bash
# Static file configuration
STATIC_IMAGES_PATH=/app/static/images
UPLOAD_MAX_SIZE=5242880  # 5MB
ALLOWED_IMAGE_TYPES=jpg,jpeg,png,webp
```

### Dockerfile Considerations

Ensure the Dockerfile creates the directory and sets proper user:
```dockerfile
# In backend/Dockerfile.backend
RUN mkdir -p /app/static/images/parts && \
    chown -R 1000:1000 /app/static && \
    chmod -R 755 /app/static
```

### Health Check Endpoint

Add a health check to verify storage is working:
```python
@app.get("/health/storage")
async def check_storage_health():
    """Check if storage system is working"""
    dir_manager = UploadDirectoryManager()
    
    # Check directory initialization
    dirs_ok = dir_manager.initialize_directories()
    
    # Check permissions
    permissions = dir_manager.check_permissions()
    
    # Try to write a test file
    test_file = dir_manager.base_path / "health_check.tmp"
    write_ok = False
    try:
        test_file.write_text("health check")
        write_ok = test_file.exists()
        test_file.unlink()  # cleanup
    except Exception:
        pass
    
    return {
        "storage_healthy": dirs_ok and all(permissions.values()) and write_ok,
        "directories_created": dirs_ok,
        "permissions": permissions,
        "write_test": write_ok,
        "base_path": str(dir_manager.base_path)
    }
```

### Troubleshooting Guide

**Common Issues and Solutions**:

1. **Permission Denied Errors**:
   ```bash
   # Fix ownership
   sudo chown -R 1000:1000 /var/lib/abparts/static/images
   
   # Fix permissions
   sudo chmod -R 755 /var/lib/abparts/static/images
   ```

2. **Directory Not Found**:
   ```bash
   # Create missing directories
   sudo mkdir -p /var/lib/abparts/static/images/parts
   ```

3. **SELinux Issues (if applicable)**:
   ```bash
   # Set SELinux context for Docker bind mounts
   sudo setsebool -P container_manage_cgroup true
   sudo chcon -Rt svirt_sandbox_file_t /var/lib/abparts/static/images
   ```

This focused design addresses the specific issue of making image uploads work on the VM with bind mounts while maintaining compatibility with the existing development environment.