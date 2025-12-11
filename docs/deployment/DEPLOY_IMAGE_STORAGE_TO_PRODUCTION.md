# Deploy Image Storage System to Production

This guide covers deploying the database-backed image storage system (profile photos, organization logos) to production.

## Overview

The new system stores images in the PostgreSQL database instead of the filesystem, with:
- Automatic image compression (WebP format)
- Cache-busting URLs for instant updates
- Public image serving endpoints (no auth required for display)
- Middleware exclusions for `/images/` paths

## Prerequisites

- Production server access (SSH)
- Git repository access
- Docker and docker-compose installed on production
- PostgreSQL database with existing schema

## Deployment Steps

### 1. Pull Latest Code

```bash
# SSH into production server
ssh root@abparts.oraseas.com

# Navigate to project directory
cd /root/abparts

# Pull latest changes
git pull origin main
```

### 2. Check Database Schema

The system uses existing columns that should already be in your database:
- `users.profile_photo_data` (LargeBinary)
- `users.profile_photo_url` (String) - legacy, kept for fallback
- `organizations.logo_data` (LargeBinary)
- `organizations.logo_url` (String) - legacy, kept for fallback

Verify these columns exist:
```bash
docker-compose exec db psql -U abparts_user -d abparts_prod -c "\d users"
docker-compose exec db psql -U abparts_user -d abparts_prod -c "\d organizations"
```

If columns are missing, you'll need to run a migration (contact dev team).

### 3. Update Nginx Configuration

The frontend nginx needs to proxy `/images/` requests to the API:

```bash
# Check if nginx.conf has the /images/ proxy
grep -A 5 "location ^~ /images/" frontend/nginx.conf
```

Should see:
```nginx
location ^~ /images/ {
    proxy_pass http://api:8000/images/;
    ...
}
```

This is already in the code you're pulling, so no manual changes needed.

### 4. Rebuild and Restart Services

```bash
# Rebuild both API and frontend
docker-compose -f docker-compose.prod.yml build api web

# Restart services
docker-compose -f docker-compose.prod.yml up -d api web

# Wait for services to start
sleep 10

# Check services are running
docker-compose -f docker-compose.prod.yml ps
```

### 5. Verify Deployment

#### Test Image Upload Endpoints
```bash
# Check API is responding
curl -I https://abparts.oraseas.com/api/health

# Check image serving endpoint (should return 404 if no images yet)
curl -I https://abparts.oraseas.com/images/users/test/profile
```

#### Test in Browser
1. Log in to https://abparts.oraseas.com
2. Go to Profile → Upload a profile photo
3. Check that photo appears immediately in header
4. Go to Organizations → Edit an organization → Upload logo
5. Check that logo appears on organization card

### 6. Monitor Logs

```bash
# Watch API logs for any errors
docker-compose -f docker-compose.prod.yml logs -f --tail=50 api

# Watch frontend logs
docker-compose -f docker-compose.prod.yml logs -f --tail=50 web
```

Look for:
- ✅ Successful image uploads
- ✅ Image serving requests (GET /images/...)
- ❌ Any 500 errors or exceptions

## Key Changes Deployed

### Backend Changes
1. **Image serving endpoints** (`backend/app/routers/images.py`)
   - `/images/users/{user_id}/profile` - Serve profile photos
   - `/images/organizations/{org_id}/logo` - Serve org logos
   - Public endpoints (no auth required)

2. **Middleware exclusions** (`backend/app/middleware.py`, `backend/app/security_middleware.py`)
   - `/images/` paths excluded from auth checks
   - Allows browser `<img>` tags to load images

3. **Cache-busting URLs** (`backend/app/auth.py`, `backend/app/routers/organizations.py`)
   - URLs include `?v=timestamp` parameter
   - Forces browser to fetch new image when updated

4. **Image compression** (`backend/app/image_utils.py`)
   - Automatic WebP conversion
   - Max 500KB per image
   - Quality optimization

### Frontend Changes
1. **Upload components**
   - `ProfilePhotoUpload.js` - User profile photos
   - `OrganizationLogoUpload.js` - Organization logos
   - Auto-refresh user context after upload

2. **Display components**
   - `Layout.js` - Header shows profile photo and org logo
   - `Organizations.js` - Organization cards show logos
   - `UserProfile.js` - Profile page shows photo

3. **Nginx proxy** (`frontend/nginx.conf`)
   - Routes `/images/*` requests to API backend

## Rollback Plan

If issues occur, rollback to previous version:

```bash
# Stop services
docker-compose -f docker-compose.prod.yml down

# Checkout previous commit
git log --oneline -10  # Find previous commit hash
git checkout <previous-commit-hash>

# Rebuild and restart
docker-compose -f docker-compose.prod.yml build api web
docker-compose -f docker-compose.prod.yml up -d

# Verify services
docker-compose -f docker-compose.prod.yml ps
```

## Troubleshooting

### Images Not Displaying

**Symptom:** Uploaded images don't show in UI

**Check:**
```bash
# 1. Verify nginx proxy is working
docker-compose -f docker-compose.prod.yml logs web | grep "/images/"

# 2. Check API is serving images
docker-compose -f docker-compose.prod.yml logs api | grep "GET /images"

# 3. Test image endpoint directly
curl -I https://abparts.oraseas.com/images/users/<user-id>/profile
```

**Solution:** Ensure nginx.conf has `/images/` proxy and frontend container is restarted.

### 401 Unauthorized on Images

**Symptom:** Browser console shows 401 errors for image requests

**Check:**
```bash
# Verify middleware excludes /images/ paths
docker-compose -f docker-compose.prod.yml exec api grep -A 5 "startswith.*images" /app/app/middleware.py
```

**Solution:** Ensure API container is rebuilt with latest middleware changes.

### Images Not Updating (Cached)

**Symptom:** Old image still shows after uploading new one

**Check:** URL should include `?v=timestamp` parameter

**Solution:** 
- Ensure `updated_at` column exists on users/organizations tables
- Verify cache-busting code in `auth.py` and `organizations.py`
- Hard refresh browser (Ctrl+Shift+R)

### Upload Fails with 500 Error

**Symptom:** Image upload returns 500 Internal Server Error

**Check:**
```bash
# Check API logs for detailed error
docker-compose -f docker-compose.prod.yml logs api | tail -50
```

**Common causes:**
- Database connection issue
- Image too large (>5MB)
- Invalid image format
- Disk space full

## Database Storage Considerations

### Storage Usage
- Each compressed image: ~50-500KB
- Max users: 200 → ~100MB max for profile photos
- Max orgs: 100 → ~50MB max for logos
- **Total: ~150MB** (negligible for PostgreSQL)

### Backup
Images are automatically included in database backups:
```bash
# Regular backup includes image data
docker-compose -f docker-compose.prod.yml exec db pg_dump -U abparts_user abparts_prod > backup.sql
```

### Migration from Old System
If you have existing images in `/static/images/`, they can be migrated:
```bash
# Run migration script (if needed)
docker-compose -f docker-compose.prod.yml exec api python migrate_images_to_db.py
```

## Performance Notes

- **Image serving:** Fast (served directly from database with caching headers)
- **Upload processing:** ~1-2 seconds (includes compression)
- **Browser caching:** 1 year (safe with cache-busting)
- **Database impact:** Minimal (images are small and rarely accessed)

## Success Criteria

✅ Users can upload profile photos  
✅ Photos appear immediately in header  
✅ Organizations can upload logos  
✅ Logos appear on organization cards  
✅ Images update immediately when changed  
✅ No 401/403 errors on image requests  
✅ No performance degradation  

## Support

If issues persist:
1. Check logs: `docker-compose -f docker-compose.prod.yml logs api web`
2. Verify database schema: `\d users` and `\d organizations`
3. Test endpoints manually with curl
4. Contact development team with error logs

---

**Deployment Date:** _____________________  
**Deployed By:** _____________________  
**Status:** ⬜ Success ⬜ Issues ⬜ Rolled Back  
**Notes:** _____________________
