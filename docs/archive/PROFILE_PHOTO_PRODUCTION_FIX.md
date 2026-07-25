# Profile Photo Not Showing in Production - Fix

## How Profile Photos Work

Profile photos are stored **in the database** (not as files) and served via API endpoint:

```
GET /images/users/{user_id}/profile
```

## Why Photos Might Not Show in Production

### 1. **Check the API Response**

In production, check what the `/users/me/` endpoint returns:

```bash
curl -H "Authorization: Bearer YOUR_TOKEN" https://abparts.oraseas.com/api/users/me/
```

Look for `profile_photo_url` field. It should be either:
- `null` (if no photo uploaded)
- A data URL starting with `data:image/webp;base64,...`
- Or a path like `/images/users/{user_id}/profile`

### 2. **Check if Photo Exists in Database**

```sql
-- On production database:
SELECT id, username, profile_photo_data IS NOT NULL as has_photo 
FROM users 
WHERE username = 'your_username';
```

### 3. **Common Issues**

**Issue A: Frontend using wrong URL**
- Frontend might be looking for `/static/images/profile_xxx.png`
- Should use `/images/users/{user_id}/profile` or data URL

**Issue B: CORS/Proxy Issue**
- Nginx might not be proxying `/images/` endpoint correctly
- Check nginx logs: `tail -f /var/log/nginx/abparts_error.log`

**Issue C: Photo not uploaded**
- User needs to upload photo in My Profile page
- Check browser console for upload errors

### 4. **Fix for Nginx (if needed)**

Add to your nginx config if `/images/` endpoint isn't proxied:

```nginx
# In nginx-native-setup.conf, add:
location /images/ {
    proxy_pass http://localhost:8000/images/;
    proxy_http_version 1.1;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
}
```

Then reload nginx:
```bash
sudo nginx -t
sudo systemctl reload nginx
```

### 5. **Test the Endpoint Directly**

```bash
# Get your user ID from /users/me/
USER_ID="your-user-id-here"

# Try to access the photo directly:
curl https://abparts.oraseas.com/api/images/users/$USER_ID/profile -o test_photo.webp

# Check if file was created:
file test_photo.webp
```

### 6. **Check Frontend Component**

The ProfilePhotoUpload component should use:
- Upload endpoint: `POST /uploads/users/profile-photo`
- Display: Data URL from response or `/images/users/{user_id}/profile`

## Quick Diagnostic

Run this in production:

```bash
# 1. Check if API is running
curl http://localhost:8000/docs

# 2. Check if images endpoint exists
curl http://localhost:8000/images/users/YOUR_USER_ID/profile

# 3. Check nginx proxy
curl https://abparts.oraseas.com/api/images/users/YOUR_USER_ID/profile
```

## Most Likely Issue

Based on the nginx config, `/images/` is NOT being proxied! You need to add the proxy configuration above.

Currently your nginx only proxies:
- `/api/` → backend
- `/static/images/` → backend (for part images)

But NOT `/images/` → backend (for profile photos from database)

**Add the `/images/` location block to your nginx config!**
