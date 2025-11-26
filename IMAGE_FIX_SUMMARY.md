# Part Images Fix - Summary

## The Problem
Part images weren't displaying in production because the Docker container was looking in the wrong directory.

- **Images are stored:** `/var/www/abparts_images/` (on server)
- **Docker was looking:** `/var/lib/abparts/images/` (wrong location)
- **URLs in app:** `/static/images/filename.jpg` (correct)

## The Solution
Updated `docker-compose.prod.yml` to mount the correct directory:

```yaml
# Line 66 in docker-compose.prod.yml
volumes:
  - /var/www/abparts_images:/app/static/images:ro
```

## How It Works

1. **Physical files:** `/var/www/abparts_images/image.jpg` (on server)
2. **Docker mount:** Makes them available at `/app/static/images/image.jpg` (in container)
3. **Backend serves:** `http://api:8000/static/images/image.jpg`
4. **Nginx proxies:** `https://abparts.oraseas.com/static/images/image.jpg`
5. **Frontend displays:** `<img src="/static/images/image.jpg" />`

## Files Changed
- ✅ `docker-compose.prod.yml` - Updated volume mount

## Deployment
See `DEPLOY_IMAGE_FIX.md` for step-by-step deployment instructions.

## Quick Deploy
```bash
# On your local machine
git add docker-compose.prod.yml
git commit -m "Fix: Mount correct images directory in production"
git push

# On production server
cd ~/abparts
git pull
sudo docker compose -f docker-compose.prod.yml restart api
```

## Verification
```bash
# Check images are accessible
sudo docker exec abparts_api_prod ls /app/static/images | head -20

# Test in browser
https://abparts.oraseas.com/static/images/your-image.jpg
```

That's it! The fix is simple - just pointing Docker to the right directory.
