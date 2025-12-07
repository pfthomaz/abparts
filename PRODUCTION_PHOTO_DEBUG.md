# Production Profile Photo Debug Steps

## Issue
- Profile photos work in dev
- Don't work in production
- Console shows: `currentPhotoUrl: null`
- Photo data EXISTS in database

## Root Cause
The `/api/users/me/` endpoint is returning `profile_photo_url: null` even though photo data exists.

## Debug Steps

### 1. Check what the API actually returns

In production, open browser console and run:

```javascript
fetch('https://abparts.oraseas.com/api/users/me/', {
  headers: { 'Authorization': 'Bearer ' + localStorage.getItem('authToken') }
})
.then(r => r.json())
.then(d => console.log('API Response:', JSON.stringify(d, null, 2)))
```

**Look for:** Does `profile_photo_url` field exist? Is it null or a URL?

### 2. Check if production code is updated

SSH to production server:

```bash
# Check the actual code in production
grep -A 5 "profile_photo_url.*profile_photo_data" /home/abparts/abparts/backend/app/crud/users.py
```

**Expected:** Should see the line with `f"/images/users/{user.id}/profile" if user.profile_photo_data else None`

**If not found:** Production code is not updated! You need to:
```bash
cd /home/abparts/abparts
git pull
sudo systemctl restart abparts-api
```

### 3. Check if nginx is caching

```bash
# Check nginx cache headers
curl -I https://abparts.oraseas.com/api/users/me/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Look for:** `Cache-Control` headers. If caching is enabled for `/api/users/me/`, disable it.

### 4. Force clear browser cache

In production site:
1. Open DevTools (F12)
2. Right-click refresh button
3. Select "Empty Cache and Hard Reload"
4. Or: DevTools → Network tab → Check "Disable cache"

### 5. Check if photo data exists in production DB

```bash
# On production server
docker-compose exec db psql -U abparts_user -d abparts_prod -c \
  "SELECT id, username, profile_photo_data IS NOT NULL as has_photo FROM users WHERE username = 'your_username';"
```

### 6. Test the image endpoint directly

```bash
# Get your user ID first
USER_ID="your-user-id-from-api"

# Try to fetch the image
curl https://abparts.oraseas.com/api/images/users/$USER_ID/profile -o test.webp

# Check if it worked
file test.webp
```

## Most Likely Issues

### Issue A: Production code not updated
**Solution:** 
```bash
cd /home/abparts/abparts
git pull origin main
sudo systemctl restart abparts-api
```

### Issue B: Nginx not proxying /images/
**Check:** Does your nginx config have this?
```nginx
location /images/ {
    proxy_pass http://localhost:8000/images/;
    # ... proxy headers
}
```

**If missing, add it and reload:**
```bash
sudo nano /etc/nginx/sites-available/abparts
# Add the location block
sudo nginx -t
sudo systemctl reload nginx
```

### Issue C: API returning old cached response
**Solution:**
```bash
# Restart API
sudo systemctl restart abparts-api

# Clear any API-level cache
# (if you have Redis caching enabled)
docker-compose exec redis redis-cli FLUSHALL
```

## Quick Fix Command

Run this on production server:

```bash
cd /home/abparts/abparts && \
git pull && \
sudo systemctl restart abparts-api && \
echo "✅ Code updated and API restarted"
```

Then hard-refresh your browser (Ctrl+Shift+R or Cmd+Shift+R).

## Verify Fix

After applying fix, check in browser console:

```javascript
fetch('https://abparts.oraseas.com/api/users/me/', {
  headers: { 'Authorization': 'Bearer ' + localStorage.getItem('authToken') }
})
.then(r => r.json())
.then(d => console.log('profile_photo_url:', d.profile_photo_url))
```

Should show: `profile_photo_url: "/images/users/xxx-xxx-xxx/profile"`
