# Manual Deployment Steps - Development

Follow these steps one by one to deploy the hybrid storage solution.

## Prerequisites

- Docker is running
- You're in the project root directory
- Development environment is currently running

## Step 1: Backup Database

```bash
# Create backups directory
mkdir -p ./backups

# Backup current database
docker compose exec -T db pg_dump -U abparts_user abparts_dev | gzip > ./backups/abparts_dev_backup_$(date +%Y%m%d_%H%M%S).sql.gz

# Verify backup was created
ls -lh ./backups/
```

**Expected**: You should see a .sql.gz file in ./backups/

## Step 2: Stop Containers

```bash
docker compose down
```

**Expected**: All containers stop

## Step 3: Rebuild API Container

```bash
# This installs Pillow and other new dependencies
docker compose build api
```

**Expected**: Build completes successfully (may take 2-3 minutes)

## Step 4: Start Database

```bash
# Start just database and redis
docker compose up -d db redis

# Wait for database to be ready
sleep 10

# Check database is running
docker compose ps
```

**Expected**: db and redis containers are "Up"

## Step 5: Run Database Migration

```bash
# Start API
docker compose up -d api

# Wait for API to start
sleep 10

# Run migration
docker compose exec api alembic upgrade head
```

**Expected Output**:
```
INFO  [alembic.runtime.migration] Running upgrade 20251124_order_txn -> 20251129_hybrid_storage, add hybrid media storage
```

**Verify Migration**:
```bash
# Check new columns exist
docker compose exec db psql -U abparts_user -d abparts_dev -c "
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'users' AND column_name = 'profile_photo_data';
"
```

**Expected**: Should show `profile_photo_data | bytea`

## Step 6: Migrate Existing Images

```bash
# Copy migration script to container
docker compose cp migrate_images_to_db.py api:/tmp/migrate_images_to_db.py

# Run migration script
docker compose exec api python /tmp/migrate_images_to_db.py
```

**Expected Output**:
```
============================================================
MIGRATING IMAGES TO DATABASE
============================================================

Scanning directory: /app/static/images

1. Migrating User Profile Photos...
------------------------------------------------------------
  Processing: admin (profile_abc123.png)
    ✓ Migrated (145.2KB)
  ...

Migrated X user profile photos

2. Migrating Organization Logos...
------------------------------------------------------------
  Processing: Oraseas EE (org_logo_xyz789.png)
    ✓ Migrated (89.5KB)
  ...

Migrated X organization logos

3. Migrating Part Images...
------------------------------------------------------------
  ✓ Part PN-001-A: 2 images (234.5KB total)
  ...

Migrated X images for Y parts

============================================================
✓ Migration completed successfully!
============================================================
```

## Step 7: Start All Services

```bash
docker compose up -d
```

**Expected**: All services start successfully

## Step 8: Verify Deployment

### Check Services
```bash
docker compose ps
```

**Expected**: All services "Up"

### Check Image Counts
```bash
docker compose exec db psql -U abparts_user -d abparts_dev -c "
SELECT 
  (SELECT COUNT(*) FROM users WHERE profile_photo_data IS NOT NULL) as users_with_photos,
  (SELECT COUNT(*) FROM organizations WHERE logo_data IS NOT NULL) as orgs_with_logos,
  (SELECT COUNT(*) FROM parts WHERE image_data IS NOT NULL) as parts_with_images;
"
```

**Expected**: Numbers should match your existing images

### Check API
```bash
# Check API is responding
curl http://localhost:8000/docs

# Check logs
docker compose logs --tail=50 api
```

**Expected**: No errors in logs

### Check Frontend
Open http://localhost:3000 in browser

**Expected**: 
- Application loads
- Existing images display correctly
- No 404 errors in browser console

## Step 9: Test New Uploads

1. **Login** to the application
2. **Upload Profile Photo**:
   - Go to user profile
   - Upload a new photo
   - Verify it displays immediately
3. **Upload Organization Logo**:
   - Go to organization settings
   - Upload a logo
   - Verify it displays in header
4. **Upload Part Image**:
   - Create or edit a part
   - Upload an image
   - Verify it displays in parts list

## Step 10: Verify Database Storage

```bash
# Check that new uploads are in database
docker compose exec db psql -U abparts_user -d abparts_dev -c "
SELECT 
  username,
  CASE 
    WHEN profile_photo_data IS NOT NULL THEN 'Yes (' || length(profile_photo_data)/1024 || ' KB)'
    ELSE 'No'
  END as has_photo
FROM users 
WHERE profile_photo_data IS NOT NULL
LIMIT 5;
"
```

**Expected**: Shows users with photo sizes

## Troubleshooting

### Migration Fails

**Check Alembic Status**:
```bash
docker compose exec api alembic current
docker compose exec api alembic history
```

**Manual Migration**:
```bash
# If migration fails, check what went wrong
docker compose logs api | grep -i error

# Try running migration again
docker compose exec api alembic upgrade head
```

### Images Not Migrating

**Check Images Directory**:
```bash
docker compose exec api ls -la /app/static/images/ | head -20
```

**Run Migration with Debug**:
```bash
docker compose exec api python /tmp/migrate_images_to_db.py
```

### Images Not Displaying

**Check Endpoints**:
```bash
# Get a user ID
docker compose exec db psql -U abparts_user -d abparts_dev -c "
SELECT id, username FROM users WHERE profile_photo_data IS NOT NULL LIMIT 1;
"

# Test endpoint (replace USER_ID)
curl http://localhost:8000/images/users/USER_ID/profile -I
```

**Expected**: `HTTP/1.1 200 OK` and `Content-Type: image/webp`

**Check Browser Console**:
- Open browser developer tools (F12)
- Check Console tab for errors
- Check Network tab for failed requests

### API Not Starting

**Check Logs**:
```bash
docker compose logs api
```

**Common Issues**:
- Import errors: Check if Pillow installed
- Database connection: Check if db is running
- Port conflicts: Check if port 8000 is available

## Rollback (If Needed)

```bash
# Stop containers
docker compose down

# Restore database
gunzip < ./backups/abparts_dev_backup_YYYYMMDD_HHMMSS.sql.gz | \
  docker compose exec -T db psql -U abparts_user abparts_dev

# Restart
docker compose up -d
```

## Success Criteria

✅ **Deployment Successful If**:
- [ ] All containers running
- [ ] No errors in logs
- [ ] Existing images display correctly
- [ ] New uploads work
- [ ] Images stored in database (verified with SQL)
- [ ] No 404 errors in browser console

## Next Steps

Once development is working:
1. Monitor for 1-2 hours
2. Test thoroughly
3. Deploy to production using `./deploy_to_production.sh`

## Quick Reference

```bash
# Check services
docker compose ps

# Check logs
docker compose logs -f api

# Check database
docker compose exec db psql -U abparts_user -d abparts_dev

# Restart services
docker compose restart api

# Full restart
docker compose down && docker compose up -d
```
