# Final Production Deployment - CORS Fix

## The Problem
The React app was built with `REACT_APP_API_BASE_URL=http://46.62.153.166:8000` hardcoded into the JavaScript bundle, causing CORS errors.

## The Solution
Build the React app with `REACT_APP_API_BASE_URL=/api` so all API calls go through nginx proxy.

## Files Changed
1. `frontend/Dockerfile.frontend` - Added ARG and ENV for build-time API URL
2. `docker-compose.prod.yml` - Added build args to pass API URL during build
3. `frontend/nginx.conf` - Already configured to proxy `/api/` to backend

## Deployment Steps

### On Your Local Machine

1. **Commit and push the changes:**
```bash
git add frontend/Dockerfile.frontend docker-compose.prod.yml frontend/nginx.conf
git commit -m "Fix production CORS by using nginx proxy for API calls"
git push
```

### On Production Server (46.62.153.166)

2. **Pull the latest changes:**
```bash
cd ~/abparts
git pull
```

3. **Update .env file:**
```bash
nano .env
```

Add or update this line:
```
REACT_APP_API_BASE_URL=/api
```

Save and exit (Ctrl+X, Y, Enter)

4. **Run the deployment script:**
```bash
chmod +x deploy_production_fix.sh
./deploy_production_fix.sh
```

OR manually:

```bash
# Stop services
sudo docker compose -f docker-compose.prod.yml down

# Rebuild frontend with new API URL
sudo docker compose -f docker-compose.prod.yml build web --no-cache

# Start services
sudo docker compose -f docker-compose.prod.yml up -d

# Check status
sudo docker ps
```

5. **Verify deployment:**
```bash
# Check containers are running
sudo docker ps | grep abparts

# Check web logs
sudo docker logs abparts_web_prod --tail=20

# Check API logs
sudo docker logs abparts_api_prod --tail=20

# Test API through proxy
curl http://localhost/api/
```

6. **Test in browser:**
- Open: http://46.62.153.166/
- Try to login
- Check browser console (F12) - should see requests to `/api/token` not `:8000/token`

## How It Works Now

### Request Flow:
```
Browser → http://46.62.153.166/api/token
         ↓
    Nginx (port 80)
         ↓
    Proxies to → http://api:8000/token
         ↓
    FastAPI Backend
```

### No CORS Issues Because:
- Browser sees: `http://46.62.153.166/api/token`
- Same origin as frontend: `http://46.62.153.166/`
- Nginx handles the proxying internally

## Troubleshooting

### Still seeing :8000 in browser console?
The old build is cached. Clear browser cache or hard refresh (Ctrl+Shift+R).

### API not responding through /api/?
Check nginx logs:
```bash
sudo docker logs abparts_web_prod
```

### Backend not accessible?
Check backend is running:
```bash
sudo docker logs abparts_api_prod --tail=50
curl http://localhost:8000/
```

### Need to rebuild again?
```bash
sudo docker compose -f docker-compose.prod.yml build web --no-cache
sudo docker compose -f docker-compose.prod.yml up -d web
```

## Environment Variables Summary

**.env file should have:**
```bash
# This tells React to use relative path /api during build
REACT_APP_API_BASE_URL=/api

# Backend CORS should allow the frontend origin
CORS_ALLOWED_ORIGINS=http://46.62.153.166,http://localhost
```

## Port Configuration

- **Port 80**: Nginx (public) - serves frontend and proxies API
- **Port 8000**: FastAPI (internal) - only accessible via nginx proxy
- **Port 5432**: PostgreSQL (internal)
- **Port 6379**: Redis (internal)

Only port 80 needs to be publicly accessible.
