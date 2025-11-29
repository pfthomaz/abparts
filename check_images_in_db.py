#!/usr/bin/env python3
"""
Quick check to verify images are in database
"""

import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / "backend"))

from app.database import SessionLocal
from app import models

def check_images():
    db = SessionLocal()
    
    try:
        print("=" * 60)
        print("CHECKING IMAGES IN DATABASE")
        print("=" * 60)
        print()
        
        # Check users
        users_with_photos = db.query(models.User).filter(
            models.User.profile_photo_data.isnot(None)
        ).all()
        
        print(f"1. Users with profile photos in database: {len(users_with_photos)}")
        for user in users_with_photos[:5]:
            size_kb = len(user.profile_photo_data) / 1024 if user.profile_photo_data else 0
            print(f"   - {user.username}: {size_kb:.1f} KB")
        if len(users_with_photos) > 5:
            print(f"   ... and {len(users_with_photos) - 5} more")
        print()
        
        # Check organizations
        orgs_with_logos = db.query(models.Organization).filter(
            models.Organization.logo_data.isnot(None)
        ).all()
        
        print(f"2. Organizations with logos in database: {len(orgs_with_logos)}")
        for org in orgs_with_logos[:5]:
            size_kb = len(org.logo_data) / 1024 if org.logo_data else 0
            print(f"   - {org.name}: {size_kb:.1f} KB")
        if len(orgs_with_logos) > 5:
            print(f"   ... and {len(orgs_with_logos) - 5} more")
        print()
        
        # Check parts
        parts_with_images = db.query(models.Part).filter(
            models.Part.image_data.isnot(None)
        ).all()
        
        print(f"3. Parts with images in database: {len(parts_with_images)}")
        total_part_images = 0
        total_size = 0
        for part in parts_with_images[:5]:
            if part.image_data:
                num_images = len(part.image_data)
                size_kb = sum(len(img) for img in part.image_data) / 1024
                total_part_images += num_images
                total_size += size_kb
                print(f"   - {part.part_number}: {num_images} images, {size_kb:.1f} KB")
        
        # Count all part images
        for part in parts_with_images:
            if part.image_data:
                total_part_images += len(part.image_data)
                total_size += sum(len(img) for img in part.image_data) / 1024
        
        if len(parts_with_images) > 5:
            print(f"   ... and {len(parts_with_images) - 5} more parts")
        print(f"   Total: {total_part_images} images, {total_size:.1f} KB")
        print()
        
        # Summary
        print("=" * 60)
        print("SUMMARY")
        print("=" * 60)
        print(f"✓ {len(users_with_photos)} user profile photos in database")
        print(f"✓ {len(orgs_with_logos)} organization logos in database")
        print(f"✓ {total_part_images} part images in database ({len(parts_with_images)} parts)")
        print()
        
        total_images = len(users_with_photos) + len(orgs_with_logos) + total_part_images
        print(f"Total: {total_images} images stored in PostgreSQL")
        print()
        
        # Check if any still using legacy URLs
        users_with_urls = db.query(models.User).filter(
            models.User.profile_photo_url.isnot(None),
            models.User.profile_photo_data.is_(None)
        ).count()
        
        orgs_with_urls = db.query(models.Organization).filter(
            models.Organization.logo_url.isnot(None),
            models.Organization.logo_data.is_(None)
        ).count()
        
        parts_with_urls = db.query(models.Part).filter(
            models.Part.image_urls.isnot(None),
            models.Part.image_data.is_(None)
        ).count()
        
        if users_with_urls > 0 or orgs_with_urls > 0 or parts_with_urls > 0:
            print("⚠ Legacy file-based images still present:")
            if users_with_urls > 0:
                print(f"  - {users_with_urls} users with URL-based photos")
            if orgs_with_urls > 0:
                print(f"  - {orgs_with_urls} organizations with URL-based logos")
            if parts_with_urls > 0:
                print(f"  - {parts_with_urls} parts with URL-based images")
            print("  Run migration script again to convert them")
        else:
            print("✓ All images migrated to database storage")
        
        print()
        print("=" * 60)
        
    finally:
        db.close()

if __name__ == "__main__":
    check_images()
