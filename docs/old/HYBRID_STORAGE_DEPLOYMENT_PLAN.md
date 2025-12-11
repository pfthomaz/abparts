# Hybrid Storage Deployment Plan

## Overview

This deployment implements the hybrid storage solution:
- **Small images (< 500KB)** → PostgreSQL database (automatic compression)
- **Large videos (> 500KB)** → File system (future feature, infrastructure ready)

## What's Been Implemented

### 1. Database Changes
- ✅ Added `profile_photo_data` (BYTEA) to `users` table
- ✅ Added `logo_data` (BYTEA) to `organizations` table  
- ✅ Added `image_data` (BYTEA[]) to `parts` table
- ✅ Created `support_videos` table (ready for future videos)
- ✅ Created `part_videos` table (ready for future videos)

### 2. Backend Changes
- ✅ Updated models with binary storage columns
- ✅ Created `image_utils.py` with automatic compression
- ✅ Updated upload endpoints to store in database
- ✅ Created new `/images/*` endpoints to serve from database
- ✅ Added Pillow dependency for image processing

### 3. Image Compression
- ✅ Automatically converts all images to WebP format
- ✅ Resizes images > 1024px to 1024px max dimension
- ✅ Tries multiple quality levels (85, 75, 60, 50, 40) to meet 500KB limit
- ✅ Handles RGBA/PNG transparency by converting to RGB

### 4. Migration Script
- ✅ `migrate_images_to_db.py` - Migrates existing file-based images to database
- ✅ Processes user profile photos
- ✅ Processes organization logos
- ✅ Processes part images (multiple per part)
- ✅ Shows progress and file sizes

### 5. Deployment Scripts
- ✅ `deploy_hybrid_storage.sh` - Development deployment
- ✅ `deploy_to_production.sh` - Production deployment

## Image Serving Endpoints

### New Endpoints (Database-backed)
```
GET /images/users/{user_id}/profile
GET /images/organizations/{org_id}/logo
GET /images/parts/{part_id}?index=0
GET /images/parts/{part_id}/count
```

### Legacy Endpoints (Still work during transition)
```
POST /uploads/users/profile-photo
POST /uploads/organizations/{org_id}/logo
DELETE /uploads/users/profile-photo
DELETE /uploads/organizations/{org_id}/logo
```

## Deployment Steps

### Phase 1: Development Testing

```bash
# 1. Deploy to development
./deploy_hybrid_storage.sh

# 2. Test image uploads
# - Go to http://localhost:3000
# - Upload a profile photo
# - Upload an organization logo
# - Upload part images

# 3. Verify images display correctly
# - Check user profile
# - Check organization page
# - Check parts list

# 4. Check database
docker compose exec db psql -U abparts_user -d abparts_dev
\dt  # List tables
SELECT id, username, length(profile_photo_data) as photo_size 
FROM users WHERE profile_photo_data IS NOT NULL;
```

### Phase 2: Production Deployment

```bash
# 1. Ensure development testing is complete
# 2. Deploy to production
./deploy_to_production.sh

# 3. Test production
# - Go to https://abparts.oraseas.com
# - Verify all images display
# - Test new uploads
```

## What Happens During Migration

### Development
1. ✅ Backs up database
2. ✅ Stops containers
3. ✅ Rebuilds with new dependencies (Pillow)
4. ✅ Runs Alembic migration (adds new columns)
5. ✅ Runs image migration script
6. ✅ Starts all services

### Production
1. ✅ Backs up production database to `/var/backups/`
2. ✅ Copies code to production server
3. ✅ Stops production containers
4. ✅ Rebuilds containers
5. ✅ Runs database migration
6. ✅ Migrates production images to database
7. ✅ Starts all services
8. ✅ Restarts nginx

## Rollback Plan

If something goes wrong:

```bash
# On production server
ssh root@46.62.153.166

# 1. Stop containers
cd /root/abparts
docker compose -f docker-compose.prod.yml down

# 2. Restore database backup
gunzip < /var/backups/abparts_pre_hybrid_prod_YYYYMMDD_HHMMSS.sql.gz | \
  docker compose -f docker-compose.prod.yml exec -T db psql -U abparts_user abparts_prod

# 3. Checkout previous code version
git checkout <previous-commit>

# 4. Restart containers
docker compose -f docker-compose.prod.yml up -d

# 5. Restart nginx
systemctl restart nginx
```

## Benefits After Deployment

### ✅ No More Image Sync Issues
- Images are in the database
- Database backups include images
- Dev/prod sync automatically with database restore

### ✅ Automatic Compression
- All images optimized to WebP
- Maximum 500KB per image
- Better performance

### ✅ Simpler Operations
- No separate file management
- No rsync needed for images
- Atomic uploads/deletes

### ✅ Better Performance
- Images cached by browser (Cache-Control headers)
- Smaller file sizes (WebP compression)
- Fast database retrieval

## Frontend Changes Needed (Next Step)

After backend deployment, update frontend to use new endpoints:

```javascript
// OLD (file-based)
<img src="/static/images/profile_abc123.jpg" />

// NEW (database-backed)
<img src={`/images/users/${userId}/profile`} />
<img src={`/images/organizations/${orgId}/logo`} />
<img src={`/images/parts/${partId}?index=0`} />
```

## Monitoring

### Check Image Migration Status
```bash
# Development
docker compose exec db psql -U abparts_user -d abparts_dev -c "
SELECT 
  (SELECT COUNT(*) FROM users WHERE profile_photo_data IS NOT NULL) as users_with_photos,
  (SELECT COUNT(*) FROM organizations WHERE logo_data IS NOT NULL) as orgs_with_logos,
  (SELECT COUNT(*) FROM parts WHERE image_data IS NOT NULL) as parts_with_images;
"

# Production
ssh root@46.62.153.166
docker compose -f docker-compose.prod.yml exec db psql -U abparts_user abparts_prod -c "
SELECT 
  (SELECT COUNT(*) FROM users WHERE profile_photo_data IS NOT NULL) as users_with_photos,
  (SELECT COUNT(*) FROM organizations WHERE logo_data IS NOT NULL) as orgs_with_logos,
  (SELECT COUNT(*) FROM parts WHERE image_data IS NOT NULL) as parts_with_images;
"
```

### Check Database Size
```bash
docker compose exec db psql -U abparts_user -d abparts_dev -c "
SELECT pg_size_pretty(pg_database_size('abparts_dev')) as db_size;
"
```

## Troubleshooting

### Images not displaying
1. Check if migration ran: `docker compose logs api | grep -i migrate`
2. Check database: `SELECT COUNT(*) FROM users WHERE profile_photo_data IS NOT NULL;`
3. Check API logs: `docker compose logs -f api`

### Image too large error
- Images are automatically compressed
- If still too large, user needs to use a smaller source image
- Maximum after compression: 500KB

### Migration script fails
1. Check if images directory exists
2. Check file permissions
3. Run manually: `docker compose exec api python /app/../migrate_images_to_db.py`

## Success Criteria

- ✅ All existing images migrated to database
- ✅ New uploads work correctly
- ✅ Images display in frontend
- ✅ No 404 errors for images
- ✅ Database backups include images
- ✅ Dev/prod environments in sync

## Next Steps After Deployment

1. Monitor for 24 hours
2. Verify no image-related errors
3. Update frontend to use new endpoints (optional, both work)
4. Remove old image files after confirming migration (optional)
5. Add video upload feature when needed (infrastructure ready)
