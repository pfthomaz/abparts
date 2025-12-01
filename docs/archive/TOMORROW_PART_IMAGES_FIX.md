# Part Images Not Showing - Fix Needed

## Issue
Part images are returning 404 errors in both development and production environments.

## Root Cause
Images are stored in `/app/static/images/` directory inside the Docker container, but:
1. The directory exists (mounted as a volume)
2. The image files themselves are missing (not transferred during database restore)

## Missing Images
- `default_part_sensor_module.jpg`
- `default_part_control_unit.jpg`
- `default_part_filter.jpg`
- `default_part_hydraulic_pump.jpg`
- User-uploaded part images (e.g., `afcd6c4d-5f43-41a7-ac7c-68009311bac7_WHC-006.1.jpg`)

## Solutions

### Option 1: Create Default Placeholder Images
```bash
# Local development
docker compose exec api mkdir -p /app/static/images
# Add actual default images to backend/static/images/ directory
# Then rebuild: docker compose build api
```

### Option 2: Transfer Images from Backup
If you have images backed up:
```bash
# Export from backup location
tar czf part_images.tar.gz /path/to/backup/images/

# Import to Docker volume
docker compose cp part_images.tar.gz api:/tmp/
docker compose exec api tar xzf /tmp/part_images.tar.gz -C /app/static/images/
```

### Option 3: Re-upload Images
Users can re-upload part images through the UI:
- Super Admin: Parts page → Edit part → Upload images
- Customer: Parts catalog → Click part → Upload images

## For Production Server
Same issue exists on Hetzner server. After fixing locally, transfer images:
```bash
# From local
docker compose exec api tar czf /tmp/images.tar.gz -C /app/static images/
docker compose cp api:/tmp/images.tar.gz ./part_images.tar.gz

# Upload to server
scp part_images.tar.gz abparts@46.62.153.166:~/abparts/

# On server
docker compose cp part_images.tar.gz api:/tmp/
docker compose exec api tar xzf /tmp/part_images.tar.gz -C /app/static/
```

## Files to Check
- `backend/app/main.py` - Static files mount configuration (already correct)
- `docker-compose.yml` - Volume configuration for `api_static_images`
- Part image URLs in database - stored as `/static/images/filename.jpg`

## Status
- ✅ Static file serving is configured correctly
- ✅ Volume is mounted properly
- ❌ Image files are missing from the volume
- ❌ Need to populate images directory

## Priority
Medium - Images enhance UX but parts functionality works without them
