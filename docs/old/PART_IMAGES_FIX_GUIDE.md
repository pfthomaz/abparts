# Part Images Fix Guide - PRODUCTION

## Problem
Part images are stored in `/var/www/abparts_images/` on the server, but the production Docker configuration was pointing to `/var/lib/abparts/images/` instead.

## Solution: Update Production Docker Configuration

### Step 1: Update docker-compose.prod.yml

The file has been updated. The change was:

**OLD (incorrect):**
```yaml
- /var/lib/abparts/images:/app/static/images
```

**NEW (correct):**
```yaml
- /var/www/abparts_images:/app/static/images:ro
```

The `:ro` flag makes it read-only for safety.

### Step 2: Deploy to Production Server

On your production server, run:

```bash
cd ~/abparts
git pull
sudo docker compose -f docker-compose.prod.yml restart api
```

Or use the automated script:
```bash
bash fix_production_images.sh
```

### Step 3: Verify Images Are Accessible

Check if Docker can see the images:
```bash
sudo docker exec abparts_api_prod ls -lh /app/static/images | head -20
```

You should see your image files listed.

### Step 4: Test Image Access

Try accessing an image directly:
```bash
curl -I https://abparts.oraseas.com/static/images/your-image-filename.jpg
```

Or visit in browser: `https://abparts.oraseas.com/static/images/your-image-filename.jpg`

## Checking Database Image Paths

The database stores image URLs. Check what format they're in:

```bash
sudo docker exec abparts_api_prod python -c "
from app.database import SessionLocal
from app.models import Part
db = SessionLocal()
parts = db.query(Part).filter(Part.image_url.isnot(None)).limit(10).all()
print('Image URLs in database:')
for p in parts:
    print(f'{p.part_number}: {p.image_url}')
db.close()
"
```

### Expected Format

Image URLs should be in one of these formats:
- `/static/images/filename.jpg` ✓ (Correct)
- `http://server/static/images/filename.jpg` ✓ (Also works)
- `/var/www/abparts_images/filename.jpg` ✗ (Wrong - needs fixing)
- `filename.jpg` ✗ (Wrong - needs path prefix)

## If Image Paths Are Wrong in Database

If the database has wrong paths (like `/var/www/abparts_images/filename.jpg`), you need to update them:

```sql
-- Check current paths
SELECT part_number, image_url FROM parts WHERE image_url IS NOT NULL LIMIT 10;

-- Fix paths if they start with /var/www/abparts_images/
UPDATE parts 
SET image_url = REPLACE(image_url, '/var/www/abparts_images/', '/static/images/')
WHERE image_url LIKE '/var/www/abparts_images/%';

-- Or if they're just filenames without path
UPDATE parts 
SET image_url = '/static/images/' || image_url
WHERE image_url IS NOT NULL 
  AND image_url NOT LIKE '/%' 
  AND image_url NOT LIKE 'http%';
```

## Troubleshooting

### Images still not showing?

1. **Check file permissions:**
   ```bash
   ls -la /var/www/abparts_images/
   ```
   Files should be readable (at least `r--` for others)

2. **Check nginx is proxying correctly:**
   ```bash
   docker logs abparts_web | grep static
   ```

3. **Check backend is serving correctly:**
   ```bash
   docker logs abparts_api | grep static
   ```

4. **Test direct backend access:**
   ```bash
   curl -I http://localhost:8000/static/images/your-image.jpg
   ```

5. **Check browser console** for 404 or CORS errors

### Permission Issues?

If Docker can't read the files:
```bash
# Make images readable by all
sudo chmod -R o+r /var/www/abparts_images/
```

## Alternative: Copy Images to Docker Volume

If mounting doesn't work, you can copy images instead:

```bash
# Copy all images to the Docker volume
docker cp /var/www/abparts_images/. abparts_api:/app/static/images/

# Verify
docker exec abparts_api ls -lh /app/static/images
```

**Note:** This copies files, so any new images added to `/var/www/abparts_images/` won't automatically appear. You'd need to copy again or switch to mounting.
