# Hetzner Production Deployment Guide - ABParts
## Server: 46.62.153.166

---

## Pre-Deployment Checklist

- [ ] All changes committed to GitHub
- [ ] Local testing completed successfully
- [ ] Backup plan ready
- [ ] Maintenance window scheduled (if needed)
- [ ] SSH access to server confirmed

---

## Step 1: Connect to Production Server

```bash
# SSH into the Hetzner server as diogo
ssh diogo@46.62.153.166

# Navigate to the application directory
cd ~/abparts
# OR if it's in a different location:
# cd /opt/abparts
# cd /var/www/abparts

# Check where the app is located
ls -la
pwd
```

---

## Step 2: Backup Current State

```bash
# Create backup directory with timestamp
BACKUP_DIR="backup_$(date +%Y%m%d_%H%M%S)"
mkdir -p ~/backups/$BACKUP_DIR

# Backup database
docker-compose exec -T db pg_dump -U abparts_user abparts_dev > ~/backups/$BACKUP_DIR/database_backup.sql

# Verify backup was created
ls -lh ~/backups/$BACKUP_DIR/database_backup.sql

# Backup current code (optional but recommended)
tar -czf ~/backups/$BACKUP_DIR/code_backup.tar.gz .

# Backup static files (if any exist)
if [ -d "backend/static" ]; then
    tar -czf ~/backups/$BACKUP_DIR/static_backup.tar.gz backend/static
fi

echo "✅ Backup completed: ~/backups/$BACKUP_DIR"
```

---

## Step 3: Pull Latest Code from GitHub

```bash
# Check current status
git status

# Stash any local changes (if needed)
git stash

# Pull latest code
git pull origin main

# If you get conflicts, resolve them or:
# git reset --hard origin/main  # WARNING: This discards local changes!

# Verify you have the latest code
git log -1
```

---

## Step 4: Run Database Migration

```bash
# Copy the migration script to a temporary location
cat > /tmp/migration.sql << 'EOF'
-- Add profile photo URL to users table
ALTER TABLE users 
ADD COLUMN IF NOT EXISTS profile_photo_url VARCHAR(500);

-- Add logo URL to organizations table
ALTER TABLE organizations 
ADD COLUMN IF NOT EXISTS logo_url VARCHAR(500);

-- Add shipped_by_user_id to customer_orders
ALTER TABLE customer_orders 
ADD COLUMN IF NOT EXISTS shipped_by_user_id UUID REFERENCES users(id);

-- Verify changes
SELECT 
    column_name, 
    data_type, 
    character_maximum_length,
    is_nullable
FROM information_schema.columns 
WHERE table_name IN ('users', 'organizations', 'customer_orders')
    AND column_name IN ('profile_photo_url', 'logo_url', 'shipped_by_user_id')
ORDER BY table_name, column_name;
EOF

# Run the migration
docker-compose exec -T db psql -U abparts_user -d abparts_dev < /tmp/migration.sql

# Check for errors in the output
# If you see "ALTER TABLE" or "ADD COLUMN", it worked!

# Clean up
rm /tmp/migration.sql
```

**Expected Output:**
```
ALTER TABLE
ALTER TABLE
ALTER TABLE
 column_name        | data_type         | character_maximum_length | is_nullable
--------------------+-------------------+-------------------------+-------------
 logo_url           | character varying | 500                     | YES
 profile_photo_url  | character varying | 500                     | YES
 shipped_by_user_id | uuid              |                         | YES
```

---

## Step 5: Create Static Files Directory

```bash
# Create directory for uploaded images
mkdir -p backend/static/images

# Set proper permissions
chmod 755 backend/static
chmod 755 backend/static/images

# Verify directory was created
ls -la backend/static/
```

---

## Step 6: Rebuild and Restart Docker Containers

```bash
# Stop the application
docker-compose down

# Rebuild containers (to include new code)
docker-compose build --no-cache

# Start the application
docker-compose up -d

# Wait for services to start (about 10-15 seconds)
sleep 15

# Check if all containers are running
docker-compose ps

# Expected output: All services should show "Up"
```

---

## Step 7: Verify Services are Running

```bash
# Check container status
docker-compose ps

# Should show:
# - abparts_db (Up)
# - abparts_api (Up)
# - abparts_web (Up)
# - abparts_redis (Up, if using)

# Check API logs for errors
docker-compose logs api --tail=50

# Check for successful startup message
# Should see: "Application startup complete" or similar

# Check database logs
docker-compose logs db --tail=20

# Check web/frontend logs
docker-compose logs web --tail=20
```

---

## Step 8: Test Database Migration

```bash
# Connect to database and verify columns exist
docker-compose exec db psql -U abparts_user -d abparts_dev -c "
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'users' AND column_name = 'profile_photo_url';
"

# Should return:
#  column_name      | data_type
# ------------------+-------------------
#  profile_photo_url | character varying

# Test a simple query
docker-compose exec db psql -U abparts_user -d abparts_dev -c "
SELECT id, username, profile_photo_url FROM users LIMIT 1;
"
```

---

## Step 9: Test Application Functionality

### 9.1 Test API Health

```bash
# Test API is responding
curl http://localhost:8000/docs

# Should return HTML (Swagger UI)

# Test a simple endpoint
curl http://localhost:8000/

# Should return: {"message": "ABParts API"} or similar
```

### 9.2 Test from Your Local Machine

```bash
# From your local machine (not the server)
curl http://46.62.153.166:8000/

# Should return API response
```

### 9.3 Test in Browser

1. Open browser and go to: `http://46.62.153.166:3000` (or your domain)
2. Login with your credentials
3. Test profile photo upload:
   - Click user icon → "My Profile"
   - Upload a profile photo
   - Verify it appears in the header
4. Test part usage:
   - Go to "Machines" page
   - Click "Use Part" on a machine
   - Complete the workflow
   - Verify transaction appears in Transactions page

---

## Step 10: Monitor for Issues

```bash
# Monitor API logs in real-time
docker-compose logs -f api

# In another terminal, monitor all services
docker-compose logs -f

# Press Ctrl+C to stop monitoring

# Check for any errors
docker-compose logs api | grep -i error
docker-compose logs api | grep -i exception
```

---

## Step 11: Verify Static Files are Accessible

```bash
# Create a test image to verify static serving works
echo "test" > backend/static/images/test.txt

# Test from server
curl http://localhost:8000/static/images/test.txt

# Should return: "test"

# Test from your local machine
curl http://46.62.153.166:8000/static/images/test.txt

# Clean up test file
rm backend/static/images/test.txt
```

---

## Troubleshooting

### Issue: Containers won't start

```bash
# Check logs
docker-compose logs

# Check disk space
df -h

# Check if ports are in use
netstat -tulpn | grep -E ':(3000|8000|5432)'

# Force recreate containers
docker-compose down -v
docker-compose up -d --force-recreate
```

### Issue: Database migration failed

```bash
# Check database logs
docker-compose logs db

# Connect to database manually
docker-compose exec db psql -U abparts_user -d abparts_dev

# Inside psql, check tables:
\dt
\d users
\d organizations

# Exit psql
\q
```

### Issue: Static files not accessible

```bash
# Check directory permissions
ls -la backend/static/

# Should show: drwxr-xr-x (755)

# Fix permissions if needed
chmod -R 755 backend/static/

# Check if API is serving static files
docker-compose logs api | grep static
```

### Issue: Profile photos not uploading

```bash
# Check API logs for upload errors
docker-compose logs api | grep upload

# Check directory is writable
docker-compose exec api ls -la /app/static/images/

# Test write permissions
docker-compose exec api touch /app/static/images/test.txt
docker-compose exec api rm /app/static/images/test.txt
```

---

## Rollback Procedure (If Needed)

### Option 1: Rollback Code Only

```bash
# Stop containers
docker-compose down

# Revert to previous commit
git log  # Find the previous commit hash
git reset --hard <previous-commit-hash>

# Rebuild and restart
docker-compose build --no-cache
docker-compose up -d
```

### Option 2: Full Rollback (Code + Database)

```bash
# Stop containers
docker-compose down

# Restore database backup
BACKUP_DIR="backup_YYYYMMDD_HHMMSS"  # Use your actual backup directory
docker-compose up -d db
sleep 5
docker-compose exec -T db psql -U abparts_user -d abparts_dev < ~/backups/$BACKUP_DIR/database_backup.sql

# Revert code
git reset --hard <previous-commit-hash>

# Rebuild and restart all services
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

---

## Post-Deployment Checklist

- [ ] All containers running (`docker-compose ps`)
- [ ] No errors in logs (`docker-compose logs`)
- [ ] API responding (`curl http://localhost:8000/`)
- [ ] Frontend accessible in browser
- [ ] Can login successfully
- [ ] Profile photo upload works
- [ ] Organization logo upload works
- [ ] Part usage workflow works
- [ ] Transaction history displays correctly
- [ ] No JavaScript errors in browser console (F12)
- [ ] Static files accessible
- [ ] Database migration successful

---

## Maintenance Commands

```bash
# View all logs
docker-compose logs

# View specific service logs
docker-compose logs api
docker-compose logs db
docker-compose logs web

# Restart a specific service
docker-compose restart api

# Restart all services
docker-compose restart

# Check resource usage
docker stats

# Clean up old images (optional)
docker image prune -a

# Check disk space
df -h
du -sh /root/abparts/*
```

---

## Important Notes

1. **Backup Location**: All backups are in `~/backups/backup_YYYYMMDD_HHMMSS/`
2. **Keep at least 3 recent backups** before deleting old ones
3. **Monitor logs** for the first hour after deployment
4. **Test all critical features** before announcing the update
5. **Document any issues** encountered during deployment

---

## Support Contacts

- **Server IP**: 46.62.153.166
- **Application Port**: 3000 (frontend), 8000 (API)
- **Database**: PostgreSQL in Docker
- **Backup Location**: ~/backups/

---

## Quick Reference Commands

```bash
# SSH to server
ssh root@46.62.153.166

# Navigate to app
cd /root/abparts

# Check status
docker-compose ps

# View logs
docker-compose logs -f api

# Restart services
docker-compose restart

# Backup database
docker-compose exec -T db pg_dump -U abparts_user abparts_dev > backup.sql

# Pull latest code
git pull origin main

# Rebuild and restart
docker-compose down && docker-compose build --no-cache && docker-compose up -d
```

---

## Estimated Deployment Time

- **Total Time**: 15-20 minutes
- Backup: 2-3 minutes
- Code pull: 1 minute
- Database migration: 1 minute
- Docker rebuild: 5-8 minutes
- Testing: 5-10 minutes

---

## Success Criteria

✅ All containers running
✅ No errors in logs
✅ Application accessible
✅ Profile photos working
✅ Part usage working
✅ Transaction history correct
✅ No data loss
✅ All existing features working

---

**Deployment Date**: _____________
**Deployed By**: _____________
**Backup Location**: _____________
**Issues Encountered**: _____________
**Resolution**: _____________
