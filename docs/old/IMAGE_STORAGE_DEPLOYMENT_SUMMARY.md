# Image Storage System - Production Deployment Summary

## What Changed

We've implemented a database-backed image storage system for profile photos and organization logos.

### Key Features
- ✅ Images stored in PostgreSQL (not filesystem)
- ✅ Automatic WebP compression (~90% size reduction)
- ✅ Cache-busting URLs (images update immediately)
- ✅ Public image serving (no auth required for display)
- ✅ Instant UI updates after upload

## Production Deployment Steps

### On Your Local Machine

1. **Commit and push changes:**
```bash
git add .
git commit -m "feat: Add database-backed image storage for profile photos and org logos"
git push origin main
```

### On Production Server

2. **Pull and deploy:**
```bash
# SSH to server
ssh root@abparts.oraseas.com

# Navigate to project
cd /root/abparts

# Pull latest code
git pull origin main

# Run deployment script
chmod +x deploy_images_to_production.sh
./deploy_images_to_production.sh
```

The script will:
- ✅ Check database schema
- ✅ Verify nginx configuration
- ✅ Rebuild API and frontend containers
- ✅ Restart services
- ✅ Verify health

## What to Test

After deployment, test these features:

### 1. Profile Photos
- Go to Profile page
- Upload a profile photo
- ✅ Photo should appear immediately in header
- ✅ Photo should persist after page refresh
- ✅ Changing photo should update immediately

### 2. Organization Logos
- Go to Organizations page
- Edit an organization
- Upload a logo
- ✅ Logo should appear in the modal
- ✅ Logo should appear on organization card
- ✅ Logo should appear in header (if it's your org)
- ✅ Changing logo should update immediately

## Technical Details

### Database Storage
- Images stored in `users.profile_photo_data` and `organizations.logo_data`
- Compressed to WebP format (max 500KB)
- Legacy `*_url` columns kept for fallback

### API Endpoints
- `GET /images/users/{id}/profile` - Serve profile photo
- `GET /images/organizations/{id}/logo` - Serve org logo
- `POST /api/uploads/users/profile-photo` - Upload profile photo
- `POST /api/uploads/organizations/{id}/logo` - Upload org logo

### Nginx Routing
- Frontend nginx proxies `/images/*` to API backend
- Allows browser `<img>` tags to load images without CORS issues

### Cache-Busting
- URLs include `?v=timestamp` parameter
- Timestamp updates when image changes
- Browser fetches new image automatically

## No Database Migration Required

The system uses existing columns:
- `users.profile_photo_data` (already exists)
- `organizations.logo_data` (already exists)

These were added in previous migrations, so no new migration is needed.

## Rollback Plan

If issues occur:

```bash
# On production server
cd /root/abparts

# Find previous commit
git log --oneline -5

# Rollback to previous version
git checkout <previous-commit-hash>

# Rebuild and restart
docker-compose -f docker-compose.prod.yml build api web
docker-compose -f docker-compose.prod.yml up -d
```

## Monitoring

Watch logs during and after deployment:

```bash
# All logs
docker-compose -f docker-compose.prod.yml logs -f api web

# Just errors
docker-compose -f docker-compose.prod.yml logs api | grep -i error

# Image-related logs
docker-compose -f docker-compose.prod.yml logs api | grep "/images/"
```

## Expected Behavior

### Before Upload
- Profile: Shows initials in colored circle
- Organization: Shows "No Logo" placeholder

### After Upload
- Profile: Shows uploaded photo in header
- Organization: Shows logo on card and in header

### After Update
- Old image disappears immediately
- New image appears immediately
- No page refresh needed

## Storage Impact

- ~150MB total for all images (negligible)
- Included in regular database backups
- No filesystem cleanup needed

## Success Criteria

✅ No errors in deployment  
✅ Services start successfully  
✅ Can upload profile photos  
✅ Can upload organization logos  
✅ Images display correctly  
✅ Images update immediately  
✅ No 401/403 errors on images  

## Support

If you encounter issues:

1. **Check logs:** Look for errors in API logs
2. **Verify endpoints:** Test `/images/` URLs directly
3. **Check nginx:** Ensure proxy is configured
4. **Database:** Verify columns exist
5. **Contact dev:** Share error logs if needed

---

**Ready to deploy?** Follow the steps above and test thoroughly!
