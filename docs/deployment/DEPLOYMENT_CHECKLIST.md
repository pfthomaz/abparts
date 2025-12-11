# Hybrid Storage Deployment Checklist

## Pre-Deployment

### Development Environment
- [ ] All code changes committed
- [ ] No uncommitted changes in working directory
- [ ] Docker is running
- [ ] Sufficient disk space (check with `df -h`)

### Production Environment
- [ ] SSH access to production server working
- [ ] Production database is accessible
- [ ] Sufficient disk space on production server
- [ ] Backup directory exists: `/var/backups/`

## Development Deployment

### Step 1: Backup
- [ ] Development database backed up
- [ ] Backup location noted

### Step 2: Deploy
- [ ] Run `./deploy_hybrid_storage.sh`
- [ ] Script completes without errors
- [ ] All containers started successfully

### Step 3: Verify Migration
- [ ] Check migration logs for errors
- [ ] Verify image counts in database
- [ ] Check database size increase

### Step 4: Test Functionality
- [ ] API responds at http://localhost:8000/docs
- [ ] Frontend loads at http://localhost:3000
- [ ] Login works
- [ ] Profile photo upload works
- [ ] Profile photo displays correctly
- [ ] Organization logo upload works
- [ ] Organization logo displays correctly
- [ ] Part images display correctly
- [ ] New part image upload works

### Step 5: Verify Endpoints
- [ ] `/images/users/{id}/profile` returns image
- [ ] `/images/organizations/{id}/logo` returns image
- [ ] `/images/parts/{id}?index=0` returns image
- [ ] No 404 errors in browser console

### Step 6: Database Verification
```bash
# Run these commands and verify results
docker compose exec db psql -U abparts_user -d abparts_dev -c "
SELECT 
  (SELECT COUNT(*) FROM users WHERE profile_photo_data IS NOT NULL) as users_with_photos,
  (SELECT COUNT(*) FROM organizations WHERE logo_data IS NOT NULL) as orgs_with_logos,
  (SELECT COUNT(*) FROM parts WHERE image_data IS NOT NULL) as parts_with_images;
"
```
- [ ] User photo count matches expected
- [ ] Organization logo count matches expected
- [ ] Part image count matches expected

## Production Deployment

### Pre-Production Checks
- [ ] Development testing complete and successful
- [ ] All tests passed
- [ ] No known issues
- [ ] Team notified of deployment
- [ ] Maintenance window scheduled (if needed)

### Step 1: Final Backup
- [ ] Production database backed up
- [ ] Backup verified and accessible
- [ ] Backup location: `/var/backups/abparts_pre_hybrid_prod_YYYYMMDD_HHMMSS.sql.gz`

### Step 2: Deploy to Production
- [ ] Run `./deploy_to_production.sh`
- [ ] Confirm deployment when prompted
- [ ] Script completes without errors
- [ ] All containers started successfully

### Step 3: Verify Production Migration
- [ ] Check migration logs for errors
- [ ] Verify image counts in production database
- [ ] Check production database size

### Step 4: Test Production
- [ ] API responds at https://abparts.oraseas.com/docs
- [ ] Frontend loads at https://abparts.oraseas.com
- [ ] SSL certificate valid
- [ ] Login works
- [ ] All existing images display correctly
- [ ] Profile photo upload works
- [ ] Organization logo upload works
- [ ] Part image upload works
- [ ] No 404 errors in browser console
- [ ] No errors in browser developer tools

### Step 5: Production Verification Commands
```bash
# SSH to production
ssh root@46.62.153.166

# Check container status
cd /root/abparts
docker compose -f docker-compose.prod.yml ps

# Check logs
docker compose -f docker-compose.prod.yml logs --tail=100 api

# Check database
docker compose -f docker-compose.prod.yml exec db psql -U abparts_user abparts_prod -c "
SELECT 
  (SELECT COUNT(*) FROM users WHERE profile_photo_data IS NOT NULL) as users_with_photos,
  (SELECT COUNT(*) FROM organizations WHERE logo_data IS NOT NULL) as orgs_with_logos,
  (SELECT COUNT(*) FROM parts WHERE image_data IS NOT NULL) as parts_with_images;
"
```
- [ ] All containers running
- [ ] No errors in logs
- [ ] Image counts correct

### Step 6: Nginx Verification
```bash
# Check nginx status
systemctl status nginx

# Check nginx logs
tail -f /var/log/nginx/error.log
```
- [ ] Nginx running
- [ ] No errors in nginx logs
- [ ] SSL working correctly

## Post-Deployment

### Immediate (0-1 hour)
- [ ] Monitor application for errors
- [ ] Check user reports/feedback
- [ ] Verify all critical functions work
- [ ] Monitor server resources (CPU, memory, disk)

### Short-term (1-24 hours)
- [ ] Monitor error logs
- [ ] Check database performance
- [ ] Verify backup includes images
- [ ] Test database restore (in dev)
- [ ] Monitor disk space usage

### Medium-term (1-7 days)
- [ ] Verify no image-related issues reported
- [ ] Confirm dev/prod sync working
- [ ] Test new image uploads
- [ ] Verify image compression working
- [ ] Check database size growth

## Rollback Procedure (If Needed)

### Development Rollback
- [ ] Stop containers: `docker compose down`
- [ ] Restore database from backup
- [ ] Restart containers: `docker compose up -d`
- [ ] Verify rollback successful

### Production Rollback
- [ ] SSH to production server
- [ ] Stop containers
- [ ] Restore database from backup
- [ ] Restart containers
- [ ] Restart nginx
- [ ] Verify rollback successful
- [ ] Notify team

## Success Criteria

### Development
✅ All tests passed
✅ No errors in logs
✅ Images display correctly
✅ New uploads work
✅ Database migration successful

### Production
✅ Zero downtime deployment
✅ All existing images display
✅ New uploads work
✅ No 404 errors
✅ Database backup successful
✅ No performance degradation

## Sign-off

### Development Deployment
- [ ] Deployed by: ________________
- [ ] Date/Time: ________________
- [ ] All tests passed: Yes / No
- [ ] Issues found: ________________
- [ ] Ready for production: Yes / No

### Production Deployment
- [ ] Deployed by: ________________
- [ ] Date/Time: ________________
- [ ] All tests passed: Yes / No
- [ ] Issues found: ________________
- [ ] Rollback needed: Yes / No
- [ ] Deployment successful: Yes / No

## Notes

### Development Deployment Notes
```
[Add any notes, issues, or observations here]
```

### Production Deployment Notes
```
[Add any notes, issues, or observations here]
```

## Contact Information

### In Case of Issues
- Developer: [Your contact]
- Server Admin: [Server admin contact]
- Database Admin: [DBA contact]

### Escalation
1. Check logs first
2. Review troubleshooting guide
3. Contact developer
4. Consider rollback if critical
