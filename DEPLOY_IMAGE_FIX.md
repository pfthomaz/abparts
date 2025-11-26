# Deploy Part Images Fix - Production

## What Changed
Updated `docker-compose.prod.yml` to mount the correct images directory:
- **Old:** `/var/lib/abparts/images:/app/static/images`
- **New:** `/var/www/abparts_images:/app/static/images:ro`

## Deployment Steps

### 1. Commit and Push Changes
```bash
git add docker-compose.prod.yml
git commit -m "Fix: Mount correct images directory in production"
git push
```

### 2. Deploy to Production Server

SSH into your production server and run:

```bash
cd ~/abparts
git pull
sudo docker compose -f docker-compose.prod.yml restart api
```

### 3. Verify the Fix

**Check images are accessible in container:**
```bash
sudo docker exec abparts_api_prod ls -lh /app/static/images | head -20
```

**Check API logs:**
```bash
sudo docker compose -f docker-compose.prod.yml logs api --tail=50
```

**Test image access:**
```bash
# Replace with an actual image filename from your directory
curl -I https://abparts.oraseas.com/static/images/test.jpg
```

**Check database image paths:**
```bash
sudo docker exec abparts_api_prod python -c "
from app.database import SessionLocal
from app.models import Part
db = SessionLocal()
parts = db.query(Part).filter(Part.image_url.isnot(None)).limit(5).all()
print('Sample image URLs:')
for p in parts:
    print(f'{p.part_number}: {p.image_url}')
db.close()
"
```

### 4. Test in Browser

1. Log into your app at https://abparts.oraseas.com
2. Navigate to Parts page
3. Check if part images are now displaying
4. Try uploading a new part image to verify uploads still work

## Expected Results

- ✅ Part images display correctly in the app
- ✅ Image URLs like `/static/images/filename.jpg` work
- ✅ New image uploads save to `/var/www/abparts_images/`
- ✅ No 404 errors for images in browser console

## Troubleshooting

### Images still not showing?

**1. Check file permissions:**
```bash
ls -la /var/www/abparts_images/ | head -20
```
Files should be readable. If not:
```bash
sudo chmod -R o+r /var/www/abparts_images/
```

**2. Check if directory exists:**
```bash
ls -la /var/www/ | grep abparts
```

**3. Verify mount inside container:**
```bash
sudo docker exec abparts_api_prod df -h | grep static
sudo docker exec abparts_api_prod mount | grep static
```

**4. Check nginx is proxying correctly:**
```bash
sudo docker compose -f docker-compose.prod.yml logs web --tail=100 | grep static
```

### Database has wrong image paths?

If images are stored with wrong paths in database (e.g., `/var/www/abparts_images/file.jpg` instead of `/static/images/file.jpg`):

```bash
sudo docker exec abparts_db_prod psql -U abparts_user -d abparts_prod
```

Then run:
```sql
-- Check current paths
SELECT part_number, image_url FROM parts WHERE image_url IS NOT NULL LIMIT 10;

-- Fix if needed
UPDATE parts 
SET image_url = REPLACE(image_url, '/var/www/abparts_images/', '/static/images/')
WHERE image_url LIKE '/var/www/abparts_images/%';
```

## Rollback (if needed)

If something goes wrong:
```bash
cd ~/abparts
git revert HEAD
git push
sudo docker compose -f docker-compose.prod.yml restart api
```
