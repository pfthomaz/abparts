#!/usr/bin/env python3
"""
Migrate existing file-based images to database storage.
This script reads images from /app/static/images and stores them in the database.
"""

import os
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / "backend"))

# Import after path is set
from app.database import SessionLocal
from app import models
from PIL import Image
import io


def compress_image(file_path: str, max_size_kb: int = 500) -> bytes:
    """Compress an image file to WebP format"""
    try:
        image = Image.open(file_path)
        
        # Convert RGBA to RGB if necessary
        if image.mode in ('RGBA', 'LA', 'P'):
            background = Image.new('RGB', image.size, (255, 255, 255))
            if image.mode == 'P':
                image = image.convert('RGBA')
            background.paste(image, mask=image.split()[-1] if image.mode in ('RGBA', 'LA') else None)
            image = background
        elif image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Resize if too large
        max_dimension = 1024
        if max(image.size) > max_dimension:
            image.thumbnail((max_dimension, max_dimension), Image.Resampling.LANCZOS)
        
        # Try different quality levels
        for quality in [85, 75, 60, 50, 40]:
            output = io.BytesIO()
            image.save(output, format='WEBP', quality=quality, optimize=True)
            image_bytes = output.getvalue()
            
            size_kb = len(image_bytes) / 1024
            if size_kb <= max_size_kb:
                return image_bytes
        
        # If still too large, return best effort
        print(f"  Warning: Image {file_path} is {size_kb:.1f}KB after compression (max {max_size_kb}KB)")
        return image_bytes
        
    except Exception as e:
        print(f"  Error processing {file_path}: {e}")
        return None


def migrate_images_to_database():
    """Migrate existing file-based images to database storage"""
    db = SessionLocal()
    
    try:
        print("=" * 60)
        print("MIGRATING IMAGES TO DATABASE")
        print("=" * 60)
        
        images_dir = Path("/app/static/images")
        if not images_dir.exists():
            images_dir = Path("backend/static/images")
        
        if not images_dir.exists():
            print(f"Error: Images directory not found at {images_dir}")
            return
        
        print(f"\nScanning directory: {images_dir}")
        
        # Migrate user profile photos
        print("\n1. Migrating User Profile Photos...")
        print("-" * 60)
        users = db.query(models.User).filter(models.User.profile_photo_url.isnot(None)).all()
        user_count = 0
        for user in users:
            if user.profile_photo_data:
                print(f"  ✓ User {user.username} already has binary data, skipping")
                continue
                
            file_path = images_dir / user.profile_photo_url.lstrip("/static/images/")
            if file_path.exists():
                print(f"  Processing: {user.username} ({file_path.name})")
                image_bytes = compress_image(str(file_path))
                if image_bytes:
                    user.profile_photo_data = image_bytes
                    user_count += 1
                    print(f"    ✓ Migrated ({len(image_bytes)/1024:.1f}KB)")
            else:
                print(f"  ✗ File not found: {file_path}")
        
        print(f"\nMigrated {user_count} user profile photos")
        
        # Migrate organization logos
        print("\n2. Migrating Organization Logos...")
        print("-" * 60)
        orgs = db.query(models.Organization).filter(models.Organization.logo_url.isnot(None)).all()
        org_count = 0
        for org in orgs:
            if org.logo_data:
                print(f"  ✓ Organization {org.name} already has binary data, skipping")
                continue
                
            file_path = images_dir / org.logo_url.lstrip("/static/images/")
            if file_path.exists():
                print(f"  Processing: {org.name} ({file_path.name})")
                image_bytes = compress_image(str(file_path))
                if image_bytes:
                    org.logo_data = image_bytes
                    org_count += 1
                    print(f"    ✓ Migrated ({len(image_bytes)/1024:.1f}KB)")
            else:
                print(f"  ✗ File not found: {file_path}")
        
        print(f"\nMigrated {org_count} organization logos")
        
        # Migrate part images
        print("\n3. Migrating Part Images...")
        print("-" * 60)
        parts = db.query(models.Part).filter(models.Part.image_urls.isnot(None)).all()
        part_count = 0
        image_count = 0
        for part in parts:
            if part.image_data:
                print(f"  ✓ Part {part.part_number} already has binary data, skipping")
                continue
                
            image_data_list = []
            for url in (part.image_urls or []):
                file_path = images_dir / url.lstrip("/static/images/")
                if file_path.exists():
                    image_bytes = compress_image(str(file_path))
                    if image_bytes:
                        image_data_list.append(image_bytes)
                        image_count += 1
            
            if image_data_list:
                part.image_data = image_data_list
                part_count += 1
                total_size = sum(len(img) for img in image_data_list)
                print(f"  ✓ Part {part.part_number}: {len(image_data_list)} images ({total_size/1024:.1f}KB total)")
        
        print(f"\nMigrated {image_count} images for {part_count} parts")
        
        # Commit all changes
        print("\n" + "=" * 60)
        print("COMMITTING CHANGES TO DATABASE...")
        db.commit()
        print("✓ Migration completed successfully!")
        print("=" * 60)
        
        print("\nSummary:")
        print(f"  - User profile photos: {user_count}")
        print(f"  - Organization logos: {org_count}")
        print(f"  - Part images: {image_count} images across {part_count} parts")
        print(f"  - Total: {user_count + org_count + image_count} images migrated")
        
    except Exception as e:
        db.rollback()
        print(f"\n✗ Migration failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    migrate_images_to_database()
