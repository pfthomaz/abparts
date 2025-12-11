# Quick Start: Hybrid Storage Deployment

## TL;DR

```bash
# 1. Deploy to development and test
./deploy_hybrid_storage.sh

# 2. Test at http://localhost:3000
# - Upload images
# - Verify they display

# 3. Deploy to production
./deploy_to_production.sh

# 4. Test at https://abparts.oraseas.com
```

## What This Does

### Problem Solved
- ✅ Images no longer get out of sync between dev/prod
- ✅ Images automatically included in database backups
- ✅ No more manual file copying
- ✅ Automatic image compression (WebP, max 500KB)

### How It Works
1. **Images → Database**: Profile photos, logos, part images stored as binary data
2. **Automatic Compression**: All images converted to WebP, resized if needed
3. **New Endpoints**: `/images/users/{id}/profile`, `/images/organizations/{id}/logo`, `/images/parts/{id}`
4. **Migration**: Existing file-based images automatically migrated to database

## Step-by-Step

### 1. Development Deployment

```bash
./deploy_hybrid_storage.sh
```

This will:
- Backup database
- Install dependencies (Pillow for image processing)
- Run database migration (add new columns)
- Migrate existing images to database
- Start all services

**Time**: ~5 minutes

### 2. Test in Development

Open http://localhost:3000 and test:

**Upload Tests:**
- [ ] Upload your profile photo
- [ ] Upload an organization logo
- [ ] Upload part images

**Display Tests:**
- [ ] Profile photo shows in header
- [ ] Organization logo shows in header
- [ ] Part images show in parts list

**Database Check:**
```bash
docker compose exec db psql -U abparts_user -d abparts_dev -c "
SELECT 
  (SELECT COUNT(*) FROM users WHERE profile_photo_data IS NOT NULL) as users_with_photos,
  (SELECT COUNT(*) FROM organizations WHERE logo_data IS NOT NULL) as orgs_with_logos,
  (SELECT COUNT(*) FROM parts WHERE image_data IS NOT NULL) as parts_with_images;
"
```

### 3. Production Deployment

Once development testing is complete:

```bash
./deploy_to_production.sh
```

This will:
- Backup production database
- Copy code to production
- Rebuild containers
- Run migration
- Migrate production images
- Restart services

**Time**: ~10 minutes

### 4. Test in Production

Open https://abparts.oraseas.com and verify:
- [ ] All existing images display correctly
- [ ] New uploads work
- [ ] No 404 errors

## Verification Commands

### Check Migration Status
```bash
# Development
docker compose logs api | grep -i "migrat"

# Production
ssh root@46.62.153.166 "cd /root/abparts && docker compose -f docker-compose.prod.yml logs api | grep -i 'migrat'"
```

### Check Image Counts
```bash
# Development
docker compose exec db psql -U abparts_user -d abparts_dev -c "
SELECT 
  'Users' as type, COUNT(*) as with_images 
FROM users WHERE profile_photo_data IS NOT NULL
UNION ALL
SELECT 'Organizations', COUNT(*) 
FROM organizations WHERE logo_data IS NOT NULL
UNION ALL
SELECT 'Parts', COUNT(*) 
FROM parts WHERE image_data IS NOT NULL;
"

# Production
ssh root@46.62.153.166 "docker compose -f docker-compose.prod.yml exec db psql -U abparts_user abparts_prod -c \"
SELECT 
  'Users' as type, COUNT(*) as with_images 
FROM users WHERE profile_photo_data IS NOT NULL
UNION ALL
SELECT 'Organizations', COUNT(*) 
FROM organizations WHERE logo_data IS NOT NULL
UNION ALL
SELECT 'Parts', COUNT(*) 
FROM parts WHERE image_data IS NOT NULL;
\""
```

### Check Database Size
```bash
# Development
docker compose exec db psql -U abparts_user -d abparts_dev -c "
SELECT pg_size_pretty(pg_database_size('abparts_dev')) as database_size;
"

# Production  
ssh root@46.62.153.166 "docker compose -f docker-compose.prod.yml exec db psql -U abparts_user abparts_prod -c \"
SELECT pg_size_pretty(pg_database_size('abparts_prod')) as database_size;
\""
```

## Troubleshooting

### "Image too large" error
- Images are automatically compressed to max 500KB
- If error persists, user needs to use a smaller source image
- Compression tries quality levels: 85, 75, 60, 50, 40

### Images not displaying
1. Check if migration ran successfully
2. Check browser console for errors
3. Check API logs: `docker compose logs -f api`
4. Verify endpoint: `curl http://localhost:8000/images/users/{user-id}/profile`

### Migration script fails
```bash
# Run manually
docker compose exec api python /app/../migrate_images_to_db.py

# Check logs
docker compose logs api
```

## Rollback (If Needed)

### Development
```bash
# Restore from backup
docker compose down
# Restore database from backup
docker compose up -d db
docker compose exec -T db psql -U abparts_user abparts_dev < backup.sql
docker compose up -d
```

### Production
```bash
ssh root@46.62.153.166
cd /root/abparts

# Stop containers
docker compose -f docker-compose.prod.yml down

# Restore database
gunzip < /var/backups/abparts_pre_hybrid_prod_*.sql.gz | \
  docker compose -f docker-compose.prod.yml exec -T db psql -U abparts_user abparts_prod

# Restart
docker compose -f docker-compose.prod.yml up -d
systemctl restart nginx
```

## Success Indicators

✅ **Migration successful if:**
- No errors in deployment scripts
- Image counts match expected numbers
- All images display in frontend
- New uploads work correctly
- No 404 errors in browser console

✅ **Production ready if:**
- Development testing complete
- All images migrated successfully
- Database backup created
- No errors in logs

## What's Next

After successful deployment:

1. **Monitor for 24 hours** - Check for any issues
2. **Verify backups** - Ensure database backups include images
3. **Optional: Update frontend** - Use new image endpoints (both old and new work)
4. **Optional: Clean up** - Remove old image files after confirming migration
5. **Future: Add videos** - Infrastructure is ready when needed

## Support

If you encounter issues:

1. Check logs: `docker compose logs -f api`
2. Check database: `docker compose exec db psql -U abparts_user -d abparts_dev`
3. Review deployment plan: `HYBRID_STORAGE_DEPLOYMENT_PLAN.md`
4. Check implementation: `IMAGE_STORAGE_PERMANENT_SOLUTION.md`
