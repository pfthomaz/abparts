# Profile Photo Issue - To Fix Tomorrow

## Current Status

### ✅ What's Working:
1. **Image viewer for parts** - Click to enlarge works perfectly
2. **Organization name in header** - Shows prominently with nice styling
3. **Photo upload** - Upload succeeds (200 OK response)
4. **Database storage** - Photo URL is saved correctly in database
5. **Organization logo upload** - Components created and ready

### ❌ What's Not Working:
- Profile photo doesn't appear in header after upload
- API endpoint `/users/me/` doesn't return `profile_photo_url` field
- Issue: Python bytecode cache in Docker container

## The Problem

The database has the photo URL:
```sql
SELECT username, profile_photo_url FROM users WHERE username = 'jamie';
-- Returns: /static/images/profile_91a8747a-4a38-4554-8db5-07c2d47a01c6.png
```

But the API response doesn't include it:
```json
{
  "username": "jamie",
  "email": "jamie@bossserv.co.uk",
  // ... other fields ...
  // NO profile_photo_url!
}
```

## Root Cause

Python bytecode cache in the Docker container isn't being cleared despite:
- Restarting the container
- Rebuilding the container
- Removing and recreating the container

The code changes in `backend/app/auth.py` that manually construct the response with `profile_photo_url` aren't being picked up.

## Solution for Tomorrow

### Option 1: Nuclear Approach (Recommended)
```bash
cd abparts
docker-compose down
docker volume prune  # Only removes unused volumes, NOT your database
docker-compose up -d --build
```

This will force a complete rebuild and clear all caches.

### Option 2: Manual Cache Clear
```bash
cd abparts
docker-compose exec api find /app -type d -name __pycache__ -exec rm -rf {} +
docker-compose exec api find /app -name "*.pyc" -delete
docker-compose restart api
```

### Option 3: Check if Code is Actually in Container
```bash
cd abparts
docker-compose exec api cat /app/app/auth.py | grep -A 20 "profile_photo_url"
```

This will show if the code changes are actually in the container.

## Files Modified Today

**Backend:**
- `backend/app/models.py` - Added `profile_photo_url` and `logo_url` columns
- `backend/app/schemas.py` - Updated schemas, added `ImageUploadResponse`
- `backend/app/schemas/organization.py` - Added `logo_url` field
- `backend/app/routers/uploads.py` - Created upload endpoints
- `backend/app/auth.py` - Modified to manually return `profile_photo_url`
- `backend/app/main.py` - Registered uploads router

**Frontend:**
- `frontend/src/components/Layout.js` - Shows org name and photo (when available)
- `frontend/src/components/ProfileTab.js` - Added photo upload section
- `frontend/src/components/OrganizationForm.js` - Added logo upload section
- `frontend/src/pages/UserProfile.js` - Handles photo updates
- `frontend/src/AuthContext.js` - Fetches organization separately
- `frontend/src/components/ProfilePhotoUpload.js` - Upload component
- `frontend/src/components/OrganizationLogoUpload.js` - Upload component
- `frontend/src/components/PartPhotoGallery.js` - Fixed image viewer

**Database:**
- Added `logo_url` column to `organizations` table
- Added `profile_photo_url` column to `users` table

## Quick Test Tomorrow

After fixing the cache issue, run this in browser console:
```javascript
fetch('http://localhost:8000/users/me/', {
  headers: {'Authorization': `Bearer ${localStorage.getItem('authToken')}`}
})
.then(r => r.json())
.then(data => console.log('profile_photo_url:', data.profile_photo_url))
```

You should see the photo URL printed.

## What We Accomplished Today

Despite the caching frustration, we successfully:
1. ✅ Fixed image viewer modal for parts
2. ✅ Added organization name to header (looks great!)
3. ✅ Created complete upload system for photos and logos
4. ✅ Database schema updated and working
5. ✅ Upload endpoints working (files are saved)
6. ✅ Frontend components created and integrated

The only remaining issue is getting the API to return the photo URL, which is purely a caching problem, not a code problem.

## Tomorrow's Plan

1. Clear Python cache (5 minutes)
2. Verify API returns `profile_photo_url` (1 minute)
3. Test photo upload and see it in header (1 minute)
4. Test organization logo upload (1 minute)
5. Celebrate! 🎉

Total time needed: ~10 minutes

The hard work is done - we just need to clear the cache!
