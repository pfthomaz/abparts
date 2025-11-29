# Production Deployment Guide

## Overview

Deploy hybrid storage solution to production using git push/pull workflow.

## Prerequisites

- Development tested and working
- SSH access as `diogo` user
- Sudo access on production server
- Git repository set up

## Step 1: Commit and Push Changes

### On Your Local Machine

```bash
# 1. Check what's changed
git status

# 2. Add all changes
git add .

# 3. Commit with descriptive message
git commit -m "feat: implement hybrid storage solution for images

- Store images in PostgreSQL database as binary data
- Automatic WebP compression (max 500KB per image)
- Add image serving endpoints
- Migrate existing file-based images to database
- Add video infrastructure for future use
- Fixes recurring image sync issues between dev/prod

Changes:
- Added binary storage columns to users, organizations, parts tables
- Created image_utils.py for compression
- Created images router for serving from database
- Updated uploads router to use database storage
- Added Pillow dependency
- Created migration scripts and documentation"

# 4. Push to repository
git push origin main  # or your branch name
```

## Step 2: Backup Production Database

### SSH to Production

```bash
# SSH as diogo
ssh diogo@46.62.153.166

# Switch to root
sudo su -

# Navigate to project
cd /root/abparts

# Create backup
docker compose -f docker-compose.prod.yml exec -T db pg_dump -U abparts_user abparts_prod | gzip > /var/backups/abparts_pre_hybrid_$(date +%Y%m%d_%H%M%S).sql.gz

# Verify backup
ls -lh /var/backups/abparts_pre_hybrid_*.sql.gz

# Exit root
exit
```

## Step 3: Pull Changes and Deploy

### Still on Production Server (as diogo)

```bash
# Switch to root
sudo su -

# Navigate to project
cd /root/abparts

# Pull latest changes
git pull origin main

# Stop containers
docker compose -f docker-compose.prod.yml down

# Rebuild API container (includes new dependencies)
docker compose -f docker-compose.prod.yml build --no-cache api

# Start database and redis
docker compose -f docker-compose.prod.yml up -d db redis

# Wait for database
sleep 10

# Start API
docker compose -f docker-compose.prod.yml up -d api

# Wait for API
sleep 10

# Run database migration
docker compose -f docker-compose.prod.yml exec api alembic upgrade heads

# Copy migration script to container
docker compose -f docker-compose.prod.yml cp migrate_images_to_db.py api:/tmp/migrate_images_to_db.py

# Run image migration
docker compose -f docker-compose.prod.yml exec api python /tmp/migrate_images_to_db.py

# Start all services
docker compose -f docker-compose.prod.yml up -d

# Restart nginx
systemctl restart nginx

# Check services
docker compose -f docker-compose.prod.yml ps

# Check logs
docker compose -f docker-compose.prod.yml logs --tail=50 api

# Exit root
exit

# Exit SSH
exit
```

## Step 4: Verify Production Deployment

### From Your Local Machine

```bash
# Test API
curl https://abparts.oraseas.com/docs

# Test image endpoint (if you have a user ID)
curl -I https://abparts.oraseas.com/images/users/{user-id}/profile
```

### In Browser

1. Open https://abparts.oraseas.com
2. Login
3. Check if existing images display
4. Upload a new profile photo
5. Upload a new organization logo
6. Verify images display correctly

## Step 5: Verify Images in Database

### SSH to Production Again

```bash
ssh diogo@46.62.153.166
sudo su -
cd /root/abparts

# Check image counts
docker compose -f docker-compose.prod.yml exec db psql -U abparts_user abparts_prod -c "
SELECT 
  (SELECT COUNT(*) FROM users WHERE profile_photo_data IS NOT NULL) as users_with_photos,
  (SELECT COUNT(*) FROM organizations WHERE logo_data IS NOT NULL) as orgs_with_logos,
  (SELECT COUNT(*) FROM parts WHERE image_data IS NOT NULL) as parts_with_images;
"

# Check database size
docker compose -f docker-compose.prod.yml exec db psql -U abparts_user abparts_prod -c "
SELECT pg_size_pretty(pg_database_size('abparts_prod')) as database_size;
"
```

## Alternative: Automated Script for Diogo User

Create this script on your local machine:

```bash
# deploy_prod_as_diogo.sh
#!/bin/bash

SERVER="diogo@46.62.153.166"

echo "============================================================"
echo "PRODUCTION DEPLOYMENT (via diogo user)"
echo "============================================================"
echo ""

echo "Step 1: Commit and push changes"
echo "------------------------------------------------------------"
read -p "Have you committed and pushed all changes? (yes/no): " confirm
if [ "$confirm" != "yes" ]; then
    echo "Please commit and push first, then run this script again."
    exit 1
fi

echo ""
echo "Step 2: Deploy to production"
echo "------------------------------------------------------------"
ssh $SERVER << 'ENDSSH'
# Switch to root
sudo su - << 'ENDROOT'

cd /root/abparts

# Backup database
echo "Backing up database..."
docker compose -f docker-compose.prod.yml exec -T db pg_dump -U abparts_user abparts_prod | gzip > /var/backups/abparts_pre_hybrid_$(date +%Y%m%d_%H%M%S).sql.gz

# Pull changes
echo "Pulling latest changes..."
git pull origin main

# Stop containers
echo "Stopping containers..."
docker compose -f docker-compose.prod.yml down

# Rebuild
echo "Rebuilding API container..."
docker compose -f docker-compose.prod.yml build --no-cache api

# Start database
echo "Starting database..."
docker compose -f docker-compose.prod.yml up -d db redis
sleep 10

# Start API
echo "Starting API..."
docker compose -f docker-compose.prod.yml up -d api
sleep 10

# Run migration
echo "Running database migration..."
docker compose -f docker-compose.prod.yml exec api alembic upgrade heads

# Migrate images
echo "Migrating images to database..."
docker compose -f docker-compose.prod.yml cp migrate_images_to_db.py api:/tmp/migrate_images_to_db.py
docker compose -f docker-compose.prod.yml exec api python /tmp/migrate_images_to_db.py

# Start all services
echo "Starting all services..."
docker compose -f docker-compose.prod.yml up -d

# Restart nginx
echo "Restarting nginx..."
systemctl restart nginx

# Show status
echo ""
echo "Deployment complete! Services status:"
docker compose -f docker-compose.prod.yml ps

ENDROOT
ENDSSH

echo ""
echo "============================================================"
echo "DEPLOYMENT COMPLETE!"
echo "============================================================"
echo ""
echo "Test at: https://abparts.oraseas.com"
echo ""
```

## Troubleshooting

### Permission Issues

If you get permission errors:
```bash
# Make sure diogo can sudo
ssh diogo@46.62.153.166
sudo -v

# If that works, you're good
```

### Git Pull Fails

```bash
# On production server as root
cd /root/abparts

# Check git status
git status

# If there are local changes, stash them
git stash

# Pull again
git pull origin main

# Reapply stashed changes if needed
git stash pop
```

### Migration Fails

```bash
# Check migration status
docker compose -f docker-compose.prod.yml exec api alembic current

# Check for multiple heads
docker compose -f docker-compose.prod.yml exec api alembic heads

# If multiple heads, merge them
docker compose -f docker-compose.prod.yml exec api alembic merge heads -m "merge_heads"
docker compose -f docker-compose.prod.yml exec api alembic upgrade heads
```

### Images Not Migrating

```bash
# Check if images directory exists
docker compose -f docker-compose.prod.yml exec api ls -la /app/static/images/

# Run migration manually with verbose output
docker compose -f docker-compose.prod.yml exec api python /tmp/migrate_images_to_db.py
```

## Rollback Procedure

If something goes wrong:

```bash
ssh diogo@46.62.153.166
sudo su -
cd /root/abparts

# Stop containers
docker compose -f docker-compose.prod.yml down

# Restore database
gunzip < /var/backups/abparts_pre_hybrid_YYYYMMDD_HHMMSS.sql.gz | \
  docker compose -f docker-compose.prod.yml exec -T db psql -U abparts_user abparts_prod

# Checkout previous version
git log --oneline -5  # Find previous commit
git checkout <previous-commit-hash>

# Restart
docker compose -f docker-compose.prod.yml up -d
systemctl restart nginx
```

## Post-Deployment Checklist

- [ ] All containers running
- [ ] No errors in logs
- [ ] API responding at https://abparts.oraseas.com/docs
- [ ] Frontend loads at https://abparts.oraseas.com
- [ ] Existing images display correctly
- [ ] New uploads work
- [ ] Images stored in database (verified with SQL)
- [ ] No 404 errors in browser console
- [ ] Database backup includes images

## Monitoring

### Check Logs
```bash
ssh diogo@46.62.153.166
sudo su -
cd /root/abparts
docker compose -f docker-compose.prod.yml logs -f api
```

### Check Database
```bash
docker compose -f docker-compose.prod.yml exec db psql -U abparts_user abparts_prod
```

### Check Services
```bash
docker compose -f docker-compose.prod.yml ps
```

## Summary

**Workflow:**
1. Commit and push from local
2. SSH to production as diogo
3. Sudo to root
4. Pull changes
5. Run deployment commands
6. Verify

**Time:** ~10-15 minutes

**Risk:** Low (database backed up, can rollback)
