# Production Frontend Rebuild Instructions

## 🚨 Issue
The auto-translation feature is still getting 404 errors because the frontend JavaScript bundle in production contains the old API endpoint paths. The frontend needs to be rebuilt with the corrected API calls.

## 🔧 Solution
Rebuild and redeploy the frontend container with the updated code.

## 📋 Steps to Fix

### 1. Stop the Frontend Container
```bash
docker-compose -f docker-compose.prod.yml stop web
```

### 2. Rebuild the Frontend Container
```bash
# Force rebuild without cache to ensure latest code
docker-compose -f docker-compose.prod.yml build --no-cache web
```

### 3. Start the Frontend Container
```bash
docker-compose -f docker-compose.prod.yml up -d web
```

### 4. Verify the Fix
1. Wait for the container to fully start (check logs)
2. Navigate to Protocol Translations page
3. Try the auto-translate feature
4. Should now work without 404 errors

## 🔍 Alternative: Full Restart (if needed)
If the above doesn't work, do a full restart:

```bash
# Stop all services
docker-compose -f docker-compose.prod.yml down

# Rebuild frontend (and optionally backend if needed)
docker-compose -f docker-compose.prod.yml build --no-cache web

# Start all services
docker-compose -f docker-compose.prod.yml up -d
```

## 🧪 Verification
After rebuilding, the browser should make calls to:
- ✅ `/api/translations/auto-translate/status` (instead of `/api/protocol-translations/auto-translate/status`)
- ✅ `/api/translations/protocols/{id}/auto-translate-complete` (instead of `/api/protocol-translations/protocols/{id}/auto-translate-complete`)

## 📝 What Changed
The frontend `translationService.js` was updated to use the correct API endpoints:
- `/translations/` prefix instead of `/protocol-translations/`
- This matches the backend router registration at `/translations`

## ⚠️ Important Notes
- The rebuild will take a few minutes as it needs to compile the React app
- Users may need to refresh their browsers to get the new JavaScript bundle
- The API backend doesn't need to be rebuilt (only frontend)

## 🎯 Expected Result
After the rebuild, the auto-translation feature should work correctly:
1. Service status check will succeed
2. Auto-translation requests will reach the backend
3. Users can successfully translate protocols using AI