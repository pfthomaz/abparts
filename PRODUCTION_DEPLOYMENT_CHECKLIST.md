# Production Deployment Checklist

## Pre-Deployment (Local Machine)

### 1. Verify Development Works
- [ ] Development deployment successful
- [ ] All images display correctly in dev
- [ ] New uploads work in dev
- [ ] No errors in dev logs
- [ ] Images verified in database

### 2. Commit and Push
```bash
# Check status
git status

# Add all changes
git add .

# Commit (use message from GIT_COMMIT_MESSAGE.txt)
git commit -F GIT_COMMIT_MESSAGE.txt

# Push to repository
git push origin main
```

- [ ] All changes committed
- [ ] Pushed to repository
- [ ] Verified push successful

## Production Deployment (SSH as diogo)

### 3. SSH to Production
```bash
ssh diogo@46.62.153.166
```

- [ ] SSH connection successful
- [ ] Can sudo to root: `sudo -v`

### 4. Backup Production Database
```bash
sudo su -
cd /root/abparts

# Backup
docker compose -f docker-compose.prod.yml exec -T db pg_dump -U abparts_user abparts_prod | gzip > /var/backups/abparts_pre_hybrid_$(date +%Y%m%d_%H%M%S).sql.gz

# Verify
ls -lh /var/backups/abparts_pre_hybrid_*.sql.gz
```

- [ ] Backup created
- [ ] Backup file size looks reasonable
- [ ] Backup location noted: `/var/backups/abparts_pre_hybrid_YYYYMMDD_HHMMSS.sql.gz`

### 5. Pull Changes
```bash
# Still as root in /root/abparts
git pull origin main
```

- [ ] Pull successful
- [ ] No merge conflicts
- [ ] New files visible

### 6. Stop Containers
```bash
docker compose -f docker-compose.prod.yml down
```

- [ ] All containers stopped

### 7. Rebuild API Container
```bash
docker compose -f docker-compose.prod.yml build --no-cache api
```

- [ ] Build successful
- [ ] Pillow installed
- [ ] No build errors

### 8. Start Database and Redis
```bash
docker compose -f docker-compose.prod.yml up -d db redis
sleep 10
```

- [ ] Database started
- [ ] Redis started
- [ ] Both healthy

### 9. Start API
```bash
docker compose -f docker-compose.prod.yml up -d api
sleep 10
```

- [ ] API started
- [ ] No immediate errors

### 10. Run Database Migration
```bash
docker compose -f docker-compose.prod.yml exec api alembic upgrade heads
```

- [ ] Migration successful
- [ ] New columns created
- [ ] No migration errors

**If you get "Multiple heads" error:**
```bash
docker compose -f docker-compose.prod.yml exec api alembic merge heads -m "merge_heads"
docker compose -f docker-compose.prod.yml exec api alembic upgrade heads
```

### 11. Migrate Images to Database
```bash
# Copy script
docker compose -f docker-compose.prod.yml cp migrate_images_to_db.py api:/tmp/migrate_images_to_db.py

# Run migration
docker compose -f docker-compose.prod.yml exec api python /tmp/migrate_images_to_db.py
```

- [ ] Migration script ran
- [ ] Images migrated successfully
- [ ] Counts displayed correctly

### 12. Start All Services
```bash
docker compose -f docker-compose.prod.yml up -d
```

- [ ] All services started
- [ ] No errors

### 13. Restart Nginx
```bash
systemctl restart nginx
```

- [ ] Nginx restarted
- [ ] No nginx errors

### 14. Check Services
```bash
docker compose -f docker-compose.prod.yml ps
```

- [ ] All containers "Up"
- [ ] No containers restarting

### 15. Check Logs
```bash
docker compose -f docker-compose.prod.yml logs --tail=50 api
```

- [ ] No errors in logs
- [ ] API started successfully

### 16. Verify Images in Database
```bash
docker compose -f docker-compose.prod.yml exec db psql -U abparts_user abparts_prod -c "
SELECT 
  (SELECT COUNT(*) FROM users WHERE profile_photo_data IS NOT NULL) as users_with_photos,
  (SELECT COUNT(*) FROM organizations WHERE logo_data IS NOT NULL) as orgs_with_logos,
  (SELECT COUNT(*) FROM parts WHERE image_data IS NOT NULL) as parts_with_images;
"
```

- [ ] Image counts displayed
- [ ] Counts match expectations

### 17. Exit SSH
```bash
exit  # Exit root
exit  # Exit SSH
```

## Post-Deployment Verification (Local Machine)

### 18. Test Production API
```bash
curl https://abparts.oraseas.com/docs
```

- [ ] API responds
- [ ] Docs page loads

### 19. Test in Browser
Open https://abparts.oraseas.com

- [ ] Application loads
- [ ] Can login
- [ ] Existing images display
- [ ] Profile photos show
- [ ] Organization logos show
- [ ] Part images show
- [ ] No 404 errors in console

### 20. Test New Uploads
- [ ] Upload profile photo works
- [ ] Upload organization logo works
- [ ] Upload part image works
- [ ] New images display immediately

### 21. Verify Image Endpoints
```bash
# Get a user ID (from browser or database)
curl -I https://abparts.oraseas.com/images/users/{user-id}/profile
```

- [ ] Returns 200 OK
- [ ] Content-Type: image/webp
- [ ] Image displays

## Post-Deployment Monitoring

### 22. Monitor for 1 Hour
- [ ] Check logs periodically
- [ ] Monitor for errors
- [ ] Check user reports
- [ ] Verify performance

### 23. Check Database Size
```bash
ssh diogo@46.62.153.166
sudo su -
cd /root/abparts
docker compose -f docker-compose.prod.yml exec db psql -U abparts_user abparts_prod -c "
SELECT pg_size_pretty(pg_database_size('abparts_prod')) as database_size;
"
```

- [ ] Database size reasonable
- [ ] Size increase expected (images now in DB)

### 24. Verify Backup Includes Images
```bash
# On production server
ls -lh /var/backups/abparts_pre_hybrid_*.sql.gz

# New backup should be larger (includes images)
```

- [ ] Backup size increased
- [ ] Images included in backup

## Success Criteria

✅ **Deployment Successful If:**
- [x] All containers running
- [x] No errors in logs
- [x] API responding
- [x] Frontend loads
- [x] Existing images display
- [x] New uploads work
- [x] Images in database
- [x] No 404 errors
- [x] Performance acceptable

## Rollback (If Needed)

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

# Checkout previous commit
git log --oneline -5
git checkout <previous-commit>

# Restart
docker compose -f docker-compose.prod.yml up -d
systemctl restart nginx
```

## Notes

**Time Required:** 10-15 minutes

**Downtime:** ~2-3 minutes (during container restart)

**Risk Level:** Low (database backed up, can rollback)

**Best Time:** During low-traffic period

## Sign-Off

- [ ] Deployment completed by: ________________
- [ ] Date/Time: ________________
- [ ] All checks passed: Yes / No
- [ ] Issues encountered: ________________
- [ ] Rollback needed: Yes / No
- [ ] Production stable: Yes / No
