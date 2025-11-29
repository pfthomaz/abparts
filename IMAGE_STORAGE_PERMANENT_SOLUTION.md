# Image Storage Permanent Solution

## Problem Analysis

Images are stored as files in `/app/static/images/` directory, causing recurring issues:

1. **Dev/Prod Sync Issues**: Images uploaded in one environment don't automatically appear in the other
2. **Docker Volume Complexity**: Mounting strategies differ between dev and prod
3. **Backup Challenges**: Images aren't included in database backups
4. **Migration Friction**: Moving between environments requires manual file copying

**Current Storage Locations:**
- Part images: `image_urls` (array of paths)
- User profile photos: `profile_photo_url` (single path)
- Organization logos: `logo_url` (single path)

---

## Solution 1: Database Storage (RECOMMENDED)

Store images as Base64-encoded strings or binary data directly in PostgreSQL.

### Advantages
✅ **Single Source of Truth**: Images travel with database backups/restores
✅ **Environment Parity**: Dev/prod sync automatically with database
✅ **Simplified Deployment**: No separate file management needed
✅ **Atomic Operations**: Image uploads/deletes are transactional
✅ **No File System Issues**: No permissions, mounting, or path problems

### Disadvantages
❌ **Database Size**: Increases database storage requirements
❌ **Performance**: Slightly slower for very large images (mitigated by caching)
❌ **Query Overhead**: Images loaded with every query (mitigated by lazy loading)

### Implementation Plan

#### Step 1: Update Database Schema

```sql
-- Add new columns for binary storage
ALTER TABLE parts ADD COLUMN image_data BYTEA[];
ALTER TABLE users ADD COLUMN profile_photo_data BYTEA;
ALTER TABLE organizations ADD COLUMN logo_data BYTEA;

-- Keep URL columns for backward compatibility during migration
-- They can be removed after full migration
```

#### Step 2: Update Backend Models

```python
# backend/app/models.py

class Part(Base):
    __tablename__ = "parts"
    # ... existing columns ...
    image_urls = Column(ARRAY(Text))  # Keep for backward compatibility
    image_data = Column(ARRAY(LargeBinary))  # New: Store actual image bytes
    
class User(Base):
    __tablename__ = "users"
    # ... existing columns ...
    profile_photo_url = Column(String(500), nullable=True)  # Keep for backward compatibility
    profile_photo_data = Column(LargeBinary, nullable=True)  # New: Store actual image bytes
    
class Organization(Base):
    __tablename__ = "organizations"
    # ... existing columns ...
    logo_url = Column(String(500), nullable=True)  # Keep for backward compatibility
    logo_data = Column(LargeBinary, nullable=True)  # New: Store actual image bytes
```

#### Step 3: Update Upload Endpoints

```python
# backend/app/routers/uploads.py

import base64
from io import BytesIO
from PIL import Image

async def save_image_to_db(file: UploadFile, max_size_kb: int = 500) -> bytes:
    """Convert uploaded image to optimized bytes for database storage"""
    validate_image_file(file)
    
    # Read image
    contents = await file.read()
    image = Image.open(BytesIO(contents))
    
    # Optimize: resize if too large, convert to WebP for better compression
    max_dimension = 1024
    if max(image.size) > max_dimension:
        image.thumbnail((max_dimension, max_dimension), Image.Resampling.LANCZOS)
    
    # Convert to WebP format for optimal compression
    output = BytesIO()
    image.save(output, format='WEBP', quality=85, optimize=True)
    image_bytes = output.getvalue()
    
    # Check size
    if len(image_bytes) > max_size_kb * 1024:
        raise HTTPException(
            status_code=400,
            detail=f"Image too large after compression. Max {max_size_kb}KB"
        )
    
    return image_bytes

@router.post("/users/profile-photo", response_model=schemas.ImageUploadResponse)
async def upload_user_profile_photo(
    file: UploadFile = File(...),
    current_user: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload profile photo - stored in database"""
    image_bytes = await save_image_to_db(file, max_size_kb=500)
    
    user = db.query(models.User).filter(models.User.id == current_user.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user.profile_photo_data = image_bytes
    user.profile_photo_url = None  # Clear old URL-based storage
    db.commit()
    
    # Return data URL for immediate display
    base64_image = base64.b64encode(image_bytes).decode('utf-8')
    return schemas.ImageUploadResponse(url=f"data:image/webp;base64,{base64_image}")
```

#### Step 4: Create Image Serving Endpoint

```python
# backend/app/routers/images.py

from fastapi import APIRouter, HTTPException
from fastapi.responses import Response
import uuid

router = APIRouter()

@router.get("/images/users/{user_id}/profile")
async def get_user_profile_photo(user_id: uuid.UUID, db: Session = Depends(get_db)):
    """Serve user profile photo from database"""
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user or not user.profile_photo_data:
        raise HTTPException(status_code=404, detail="Image not found")
    
    return Response(content=user.profile_photo_data, media_type="image/webp")

@router.get("/images/organizations/{org_id}/logo")
async def get_organization_logo(org_id: uuid.UUID, db: Session = Depends(get_db)):
    """Serve organization logo from database"""
    org = db.query(models.Organization).filter(models.Organization.id == org_id).first()
    if not org or not org.logo_data:
        raise HTTPException(status_code=404, detail="Image not found")
    
    return Response(content=org.logo_data, media_type="image/webp")

@router.get("/images/parts/{part_id}/{index}")
async def get_part_image(part_id: uuid.UUID, index: int, db: Session = Depends(get_db)):
    """Serve part image from database"""
    part = db.query(models.Part).filter(models.Part.id == part_id).first()
    if not part or not part.image_data or index >= len(part.image_data):
        raise HTTPException(status_code=404, detail="Image not found")
    
    return Response(content=part.image_data[index], media_type="image/webp")
```

#### Step 5: Update Frontend

```javascript
// frontend/src/services/imagesService.js

export const getImageUrl = (type, id, index = 0) => {
  const baseUrl = process.env.REACT_APP_API_BASE_URL || '';
  
  switch(type) {
    case 'user':
      return `${baseUrl}/images/users/${id}/profile`;
    case 'organization':
      return `${baseUrl}/images/organizations/${id}/logo`;
    case 'part':
      return `${baseUrl}/images/parts/${id}/${index}`;
    default:
      return null;
  }
};

// Usage in components:
// <img src={getImageUrl('user', user.id)} alt="Profile" />
```

#### Step 6: Migration Script

```python
# migrate_images_to_db.py

import os
from pathlib import Path
from sqlalchemy.orm import Session
from backend.app.database import SessionLocal
from backend.app import models

def migrate_images_to_database():
    """Migrate existing file-based images to database storage"""
    db = SessionLocal()
    
    try:
        # Migrate user profile photos
        users = db.query(models.User).filter(models.User.profile_photo_url.isnot(None)).all()
        for user in users:
            file_path = f"/app{user.profile_photo_url}"
            if os.path.exists(file_path):
                with open(file_path, 'rb') as f:
                    user.profile_photo_data = f.read()
                print(f"Migrated profile photo for user {user.username}")
        
        # Migrate organization logos
        orgs = db.query(models.Organization).filter(models.Organization.logo_url.isnot(None)).all()
        for org in orgs:
            file_path = f"/app{org.logo_url}"
            if os.path.exists(file_path):
                with open(file_path, 'rb') as f:
                    org.logo_data = f.read()
                print(f"Migrated logo for organization {org.name}")
        
        # Migrate part images
        parts = db.query(models.Part).filter(models.Part.image_urls.isnot(None)).all()
        for part in parts:
            image_data_list = []
            for url in part.image_urls:
                file_path = f"/app{url}"
                if os.path.exists(file_path):
                    with open(file_path, 'rb') as f:
                        image_data_list.append(f.read())
            if image_data_list:
                part.image_data = image_data_list
                print(f"Migrated {len(image_data_list)} images for part {part.part_number}")
        
        db.commit()
        print("Migration completed successfully!")
        
    except Exception as e:
        db.rollback()
        print(f"Migration failed: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    migrate_images_to_database()
```

---

## Solution 2: Strict File Sync Protocol (ALTERNATIVE)

Keep file-based storage but establish a rigorous sync protocol.

### Implementation

#### Create Sync Scripts

```bash
# sync_images_to_prod.sh
#!/bin/bash

echo "Syncing images from development to production..."

# Backup production images first
ssh root@46.62.153.166 "tar -czf /tmp/images_backup_$(date +%Y%m%d_%H%M%S).tar.gz /var/www/abparts_images/"

# Sync images
rsync -avz --progress \
  ./backend/static/images/ \
  root@46.62.153.166:/var/www/abparts_images/

echo "Sync complete!"
```

```bash
# sync_images_from_prod.sh
#!/bin/bash

echo "Syncing images from production to development..."

# Backup local images first
tar -czf /tmp/images_backup_$(date +%Y%m%d_%H%M%S).tar.gz ./backend/static/images/

# Sync images
rsync -avz --progress \
  root@46.62.153.166:/var/www/abparts_images/ \
  ./backend/static/images/

echo "Sync complete!"
```

#### Update Docker Compose

```yaml
# docker-compose.yml
services:
  api:
    volumes:
      - ./backend/static/images:/app/static/images  # Consistent mounting

# docker-compose.prod.yml
services:
  api:
    volumes:
      - /var/www/abparts_images:/app/static/images:ro  # Read-only in production
```

#### Create Automated Backup

```bash
# backup_images.sh
#!/bin/bash

BACKUP_DIR="/var/backups/abparts_images"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# Backup images
tar -czf $BACKUP_DIR/images_$DATE.tar.gz /var/www/abparts_images/

# Keep only last 7 days of backups
find $BACKUP_DIR -name "images_*.tar.gz" -mtime +7 -delete

echo "Backup created: $BACKUP_DIR/images_$DATE.tar.gz"
```

Add to crontab:
```bash
# Daily backup at 2 AM
0 2 * * * /root/backup_images.sh
```

### Disadvantages
❌ **Manual Process**: Requires running sync scripts
❌ **Sync Conflicts**: Risk of overwriting newer images
❌ **Backup Complexity**: Images separate from database backups
❌ **Human Error**: Easy to forget syncing after uploads

---

## Solution 3: Hybrid Approach (BEST FOR VIDEOS + IMAGES)

Combine database storage for small images with object storage for large videos.

### Architecture

```
Small Images (< 500KB)          Large Videos (> 500KB)
├─ Profile photos        →      Database (PostgreSQL)
├─ Organization logos    →      Database (PostgreSQL)
├─ Part thumbnails       →      Database (PostgreSQL)
└─ Part videos          →      Object Storage (S3/MinIO/Local)
```

### Why Hybrid?

✅ **Best of Both Worlds**: Images sync with DB, videos use efficient storage
✅ **Cost Effective**: Database doesn't bloat with large files
✅ **Performance**: Videos stream efficiently from object storage
✅ **Scalability**: Can easily move to S3/CloudFlare R2 later
✅ **Simple Sync**: Videos stored in dedicated directory, easy to rsync

### Implementation: Local Object Storage

For your scale (max 100 customers), use a dedicated local directory with proper sync:

```
/var/www/abparts_media/
├── videos/
│   ├── support/
│   │   ├── machine_setup_v3.mp4
│   │   ├── maintenance_guide.mp4
│   │   └── troubleshooting.mp4
│   └── parts/
│       ├── {part_id}_demo.mp4
│       └── {part_id}_installation.mp4
└── documents/
    └── manuals/
```

### Updated Database Schema

```sql
-- Images stored in database
ALTER TABLE users ADD COLUMN profile_photo_data BYTEA;
ALTER TABLE organizations ADD COLUMN logo_data BYTEA;
ALTER TABLE parts ADD COLUMN image_data BYTEA[];

-- Videos stored as file references
CREATE TABLE support_videos (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(255) NOT NULL,
    description TEXT,
    category VARCHAR(50) NOT NULL, -- 'machine_setup', 'maintenance', 'troubleshooting'
    file_path VARCHAR(500) NOT NULL, -- Relative path: /videos/support/filename.mp4
    file_size_mb DECIMAL(10,2),
    duration_seconds INTEGER,
    thumbnail_data BYTEA, -- Small thumbnail stored in DB
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE part_videos (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    part_id UUID REFERENCES parts(id) ON DELETE CASCADE,
    video_type VARCHAR(50) NOT NULL, -- 'demo', 'installation', 'maintenance'
    file_path VARCHAR(500) NOT NULL,
    file_size_mb DECIMAL(10,2),
    duration_seconds INTEGER,
    thumbnail_data BYTEA,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_support_videos_category ON support_videos(category);
CREATE INDEX idx_part_videos_part_id ON part_videos(part_id);
```

### Backend Implementation

```python
# backend/app/routers/media.py

import os
import shutil
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import FileResponse, StreamingResponse

router = APIRouter()

MEDIA_ROOT = "/var/www/abparts_media"
VIDEO_EXTENSIONS = {".mp4", ".webm", ".mov"}
MAX_VIDEO_SIZE_MB = 100  # 100MB limit

def validate_video_file(file: UploadFile) -> None:
    """Validate uploaded video file"""
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in VIDEO_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Allowed: {', '.join(VIDEO_EXTENSIONS)}"
        )

async def save_video_file(file: UploadFile, category: str) -> tuple[str, float]:
    """Save video file and return path and size in MB"""
    validate_video_file(file)
    
    # Create directory structure
    video_dir = Path(MEDIA_ROOT) / "videos" / category
    video_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate unique filename
    file_ext = Path(file.filename).suffix.lower()
    filename = f"{uuid.uuid4()}{file_ext}"
    file_path = video_dir / filename
    
    # Save file with size check
    total_size = 0
    with open(file_path, "wb") as buffer:
        while chunk := await file.read(1024 * 1024):  # Read 1MB at a time
            total_size += len(chunk)
            if total_size > MAX_VIDEO_SIZE_MB * 1024 * 1024:
                buffer.close()
                os.remove(file_path)
                raise HTTPException(
                    status_code=400,
                    detail=f"Video too large. Max {MAX_VIDEO_SIZE_MB}MB"
                )
            buffer.write(chunk)
    
    size_mb = total_size / (1024 * 1024)
    relative_path = f"/videos/{category}/{filename}"
    
    return relative_path, size_mb

@router.post("/videos/support", tags=["Media"])
async def upload_support_video(
    title: str,
    category: str,
    file: UploadFile = File(...),
    description: str = None,
    current_user: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload support video (super admin only)"""
    if not permission_checker.is_super_admin(current_user):
        raise HTTPException(status_code=403, detail="Super admin access required")
    
    # Save video file
    file_path, size_mb = await save_video_file(file, "support")
    
    # Create database record
    video = models.SupportVideo(
        title=title,
        description=description,
        category=category,
        file_path=file_path,
        file_size_mb=size_mb
    )
    db.add(video)
    db.commit()
    db.refresh(video)
    
    return {
        "id": video.id,
        "title": video.title,
        "file_path": file_path,
        "size_mb": size_mb
    }

@router.get("/videos/support", tags=["Media"])
async def list_support_videos(
    category: str = None,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)
):
    """List all support videos"""
    query = db.query(models.SupportVideo)
    if category:
        query = query.filter(models.SupportVideo.category == category)
    
    videos = query.order_by(models.SupportVideo.created_at.desc()).all()
    return videos

@router.get("/videos/stream/{video_id}", tags=["Media"])
async def stream_video(
    video_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)
):
    """Stream video file"""
    # Check if it's a support video or part video
    video = db.query(models.SupportVideo).filter(models.SupportVideo.id == video_id).first()
    if not video:
        video = db.query(models.PartVideo).filter(models.PartVideo.id == video_id).first()
    
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
    
    file_path = Path(MEDIA_ROOT) / video.file_path.lstrip("/")
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Video file not found")
    
    return FileResponse(
        file_path,
        media_type="video/mp4",
        headers={
            "Accept-Ranges": "bytes",
            "Content-Disposition": f'inline; filename="{file_path.name}"'
        }
    )
```

### Video Sync Protocol

```bash
# sync_media_to_prod.sh
#!/bin/bash

echo "=== Syncing Media Files to Production ==="

PROD_SERVER="root@46.62.153.166"
PROD_MEDIA_DIR="/var/www/abparts_media"
LOCAL_MEDIA_DIR="./media"

# Create backup on production
echo "Creating backup on production..."
ssh $PROD_SERVER "tar -czf /tmp/media_backup_$(date +%Y%m%d_%H%M%S).tar.gz $PROD_MEDIA_DIR/"

# Sync videos (large files)
echo "Syncing videos..."
rsync -avz --progress \
  --include='videos/***' \
  --exclude='*' \
  $LOCAL_MEDIA_DIR/ \
  $PROD_SERVER:$PROD_MEDIA_DIR/

echo "Sync complete!"
echo "Don't forget to sync the database to include video metadata!"
```

```bash
# sync_media_from_prod.sh
#!/bin/bash

echo "=== Syncing Media Files from Production ==="

PROD_SERVER="root@46.62.153.166"
PROD_MEDIA_DIR="/var/www/abparts_media"
LOCAL_MEDIA_DIR="./media"

# Create local backup
echo "Creating local backup..."
tar -czf /tmp/media_backup_$(date +%Y%m%d_%H%M%S).tar.gz $LOCAL_MEDIA_DIR/

# Sync videos
echo "Syncing videos from production..."
rsync -avz --progress \
  $PROD_SERVER:$PROD_MEDIA_DIR/videos/ \
  $LOCAL_MEDIA_DIR/videos/

echo "Sync complete!"
```

### Docker Configuration

```yaml
# docker-compose.yml (Development)
services:
  api:
    volumes:
      - ./backend:/app
      - ./backend/static/images:/app/static/images  # Small images (will move to DB)
      - ./media:/var/www/abparts_media  # Videos and large files

# docker-compose.prod.yml (Production)
services:
  api:
    volumes:
      - /var/www/abparts_media:/var/www/abparts_media:ro  # Read-only access
```

### Frontend Implementation

```javascript
// frontend/src/components/SupportVideoPlayer.js

import React, { useState, useEffect } from 'react';

const SupportVideoPlayer = ({ videoId }) => {
  const [videoUrl, setVideoUrl] = useState('');
  
  useEffect(() => {
    const baseUrl = process.env.REACT_APP_API_BASE_URL || '';
    setVideoUrl(`${baseUrl}/videos/stream/${videoId}`);
  }, [videoId]);
  
  return (
    <div className="video-container">
      <video 
        controls 
        className="w-full rounded-lg shadow-lg"
        preload="metadata"
      >
        <source src={videoUrl} type="video/mp4" />
        Your browser does not support video playback.
      </video>
    </div>
  );
};

export default SupportVideoPlayer;
```

## Recommendation

**Use Solution 3 (Hybrid Approach)** because:

1. **Automatic Sync for Images**: Database replication handles small images
2. **Efficient Video Storage**: Large files don't bloat database
3. **Simple Video Sync**: Dedicated directory, easy rsync protocol
4. **Future-Proof**: Can migrate videos to S3/R2 later without code changes
5. **Performance**: Videos stream efficiently, images load fast from DB

### Storage Breakdown

- **Profile Photos**: Database (typically 50-200KB compressed)
- **Organization Logos**: Database (typically 20-100KB compressed)
- **Part Images**: Database (typically 100-300KB compressed)
- **Support Videos**: File system (5-50MB each)
- **Part Demo Videos**: File system (2-20MB each)

### Performance Considerations

- **Image Size Limit**: 500KB per image (enforced by compression)
- **Video Size Limit**: 100MB per video (configurable)
- **Caching**: Add Redis caching for frequently accessed images
- **Video Streaming**: Supports range requests for seeking
- **CDN Option**: Can add CloudFlare in front of both endpoints

### Migration Timeline

1. **Week 1**: Add new columns and video tables, update models
2. **Week 2**: Update upload endpoints, create serving endpoints
3. **Week 3**: Run image migration script, set up media directory
4. **Week 4**: Update frontend, add video player components
5. **Week 5**: Deploy to production, establish sync protocol

---

## Quick Start (Hybrid Approach)

```bash
# 1. Create media directory structure
mkdir -p media/videos/{support,parts}
mkdir -p media/documents/manuals

# 2. Create database migration
docker compose exec api alembic revision -m "add_hybrid_media_storage"

# 3. Apply migration
docker compose exec api alembic upgrade head

# 4. Migrate existing images to database
docker compose exec api python migrate_images_to_db.py

# 5. Test image serving (from database)
curl http://localhost:8000/images/users/{user_id}/profile

# 6. Upload test video
curl -X POST http://localhost:8000/videos/support \
  -H "Authorization: Bearer {token}" \
  -F "file=@test_video.mp4" \
  -F "title=Machine Setup Guide" \
  -F "category=machine_setup"

# 7. Test video streaming
curl http://localhost:8000/videos/stream/{video_id}

# 8. Sync videos to production
./sync_media_to_prod.sh
```

---

## Backup Strategy

### Images (Database)
```bash
# Included automatically in database backups
pg_dump -U abparts_user abparts_prod > backup.sql
```

### Videos (File System)
```bash
# Separate backup for media files
tar -czf media_backup_$(date +%Y%m%d).tar.gz /var/www/abparts_media/

# Or use rsync to backup server
rsync -avz root@46.62.153.166:/var/www/abparts_media/ ./backups/media/
```

### Automated Backup Script
```bash
#!/bin/bash
# /root/backup_abparts.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/var/backups/abparts"

# Backup database (includes images)
docker compose exec -T db pg_dump -U abparts_user abparts_prod | gzip > $BACKUP_DIR/db_$DATE.sql.gz

# Backup media files (videos)
tar -czf $BACKUP_DIR/media_$DATE.tar.gz /var/www/abparts_media/

# Keep last 7 days
find $BACKUP_DIR -name "*.gz" -mtime +7 -delete

echo "Backup complete: $DATE"
```

Add to crontab:
```bash
# Daily backup at 2 AM
0 2 * * * /root/backup_abparts.sh
```

---

## Future Scalability: Moving to S3/R2

If you outgrow local storage, migration to cloud object storage is straightforward:

```python
# backend/app/config.py

STORAGE_BACKEND = os.getenv("STORAGE_BACKEND", "local")  # or "s3"
S3_BUCKET = os.getenv("S3_BUCKET")
S3_REGION = os.getenv("S3_REGION")

# backend/app/storage.py

import boto3
from abc import ABC, abstractmethod

class StorageBackend(ABC):
    @abstractmethod
    async def save_video(self, file: UploadFile, path: str) -> str:
        pass
    
    @abstractmethod
    async def get_video_url(self, path: str) -> str:
        pass

class LocalStorage(StorageBackend):
    async def save_video(self, file: UploadFile, path: str) -> str:
        # Current implementation
        pass
    
    async def get_video_url(self, path: str) -> str:
        return f"/videos/stream/{path}"

class S3Storage(StorageBackend):
    def __init__(self):
        self.s3 = boto3.client('s3')
    
    async def save_video(self, file: UploadFile, path: str) -> str:
        self.s3.upload_fileobj(file.file, S3_BUCKET, path)
        return path
    
    async def get_video_url(self, path: str) -> str:
        return self.s3.generate_presigned_url(
            'get_object',
            Params={'Bucket': S3_BUCKET, 'Key': path},
            ExpiresIn=3600
        )

# Factory pattern
def get_storage_backend() -> StorageBackend:
    if STORAGE_BACKEND == "s3":
        return S3Storage()
    return LocalStorage()
```

---

## Conclusion

The hybrid approach gives you the best of both worlds:

1. **Images in Database**: Automatic sync, transactional safety, zero operational overhead
2. **Videos on File System**: Efficient storage, easy streaming, simple sync protocol
3. **Future-Proof**: Can migrate to S3/CloudFlare R2 when needed
4. **Practical**: Solves your immediate problem while scaling with your needs

For your scale (max 100 customers), this is the sweet spot between simplicity and robustness. Images never get out of sync (they're in the database), and videos are easy to manage with simple rsync commands.
