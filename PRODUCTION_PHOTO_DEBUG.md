# Production Photo/Image Functionality Debug Guide

## Issue
Image saving functionality works in development but not in production environment.

## Potential Causes & Solutions

### 1. Backend Code Not Deployed
**Problem**: The CRUD fixes we made might not be deployed to production containers.

**Solution**: Rebuild and restart production containers
```bash
# Stop production services
docker-compose -f docker-compose.prod.yml down

# Rebuild backend with latest changes
docker-compose -f docker-compose.prod.yml build --no-cache api

# Start services
docker-compose -f docker-compose.prod.yml up -d
```

### 2. Database Schema Differences
**Problem**: Production database might have different schema or missing columns.

**Solution**: Run database migrations in production
```bash
# Connect to production API container
docker exec -it abparts_api_prod bash

# Run migrations
alembic upgrade head

# Exit container
exit
```

### 3. Environment Configuration Issues
**Problem**: Production environment variables might be different.

**Check**: Verify production environment file has correct settings
- Image storage paths
- API base URLs
- CORS settings

### 4. Frontend Build Issues
**Problem**: Frontend production build might not include latest changes.

**Solution**: Rebuild frontend container
```bash
# Rebuild frontend with latest changes
docker-compose -f docker-compose.prod.yml build --no-cache web

# Restart frontend
docker-compose -f docker-compose.prod.yml restart web
```

### 5. Image Storage Path Issues
**Problem**: Production might use different image storage configuration.

**Check**: Verify volume mounts in docker-compose.prod.yml
```yaml
volumes:
  - /var/www/abparts_images:/app/static/images:ro
```

### 6. API Endpoint Differences
**Problem**: Production API might be behind proxy with different paths.

**Check**: Verify REACT_APP_API_BASE_URL in production
- Should be `/api` if behind nginx proxy
- Should be full URL if direct access

## Debug Steps

### Step 1: Check Production Containers
```bash
# Check if containers are running
docker-compose -f docker-compose.prod.yml ps

# Check API logs
docker-compose -f docker-compose.prod.yml logs api

# Check web logs  
docker-compose -f docker-compose.prod.yml logs web
```

### Step 2: Test Production API Directly
```bash
# Test login endpoint
curl -X POST "http://46.62.153.166:8000/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=dthomaz&password=amFT1999!"

# Test parts endpoint (use token from above)
curl -X GET "http://46.62.153.166:8000/parts/with-inventory?limit=3" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

### Step 3: Check Database in Production
```bash
# Connect to production database
docker exec -it abparts_db_prod psql -U abparts_user -d abparts_prod

# Check recent parts
SELECT part_number, name, 
       array_length(image_urls, 1) as url_count,
       created_at 
FROM parts 
ORDER BY created_at DESC 
LIMIT 5;

# Exit database
\q
```

### Step 4: Check Frontend Network Requests
1. Open browser developer tools (F12)
2. Go to Network tab
3. Try creating a part with images
4. Check if API requests are being made
5. Look for any 404, 500, or CORS errors

## Quick Fix Script

Create and run this script on production server:

```bash
#!/bin/bash
# production_image_fix.sh

echo "=== Deploying Image Functionality Fixes to Production ==="

# Stop services
echo "Stopping production services..."
docker-compose -f docker-compose.prod.yml down

# Rebuild containers with latest code
echo "Rebuilding containers..."
docker-compose -f docker-compose.prod.yml build --no-cache api web

# Start services
echo "Starting services..."
docker-compose -f docker-compose.prod.yml up -d

# Wait for services to be ready
echo "Waiting for services to start..."
sleep 30

# Run database migrations
echo "Running database migrations..."
docker exec abparts_api_prod alembic upgrade head

# Check service status
echo "Checking service status..."
docker-compose -f docker-compose.prod.yml ps

echo "=== Deployment Complete ==="
echo "Test the image functionality now."
```

## Expected Behavior After Fix

1. ✅ Parts created with images should appear at top of list
2. ✅ Image count should display correctly  
3. ✅ Success message should appear after creation
4. ✅ API should return parts sorted by creation date
5. ✅ Up to 20 images should be supported per part

## If Still Not Working

1. **Check browser console** for JavaScript errors
2. **Check network tab** for failed API requests
3. **Check API logs** for backend errors
4. **Verify database** has the new parts with images
5. **Test API directly** with curl commands above

The issue is likely that the production containers need to be rebuilt with the latest code changes we made to fix the image functionality.