# Production Deployment Fix - CORS and API Access

## Problem
Frontend at port 80 trying to access API directly at port 8000, causing CORS errors.

## Solution
Use nginx as reverse proxy to serve both frontend and API from port 80.

## Steps to Deploy

### 1. Update Environment Variables on Server

```bash
# On the server, edit the .env file
cd ~/abparts
nano .env
```

Add/update this line:
```bash
REACT_APP_API_BASE_URL=http://46.62.153.166/api
```

Make sure CORS is configured:
```bash
CORS_ALLOWED_ORIGINS=http://46.62.153.166,http://localhost
```

### 2. Rebuild and Restart Services

```bash
cd ~/abparts

# Stop services
sudo docker compose -f docker-compose.prod.yml down

# Rebuild frontend with new nginx config
sudo docker compose -f docker-compose.prod.yml build web --no-cache

# Start services
sudo docker compose -f docker-compose.prod.yml up -d

# Check status
sudo docker ps
```

### 3. Verify Services

```bash
# Check logs
sudo docker logs abparts_web_prod --tail=50
sudo docker logs abparts_api_prod --tail=50

# Test API through nginx proxy
curl http://localhost/api/
curl http://46.62.153.166/api/

# Test frontend
curl http://localhost/
curl http://46.62.153.166/
```

### 4. Test Login

Open browser to: http://46.62.153.166

The frontend will now make API calls to:
- `http://46.62.153.166/api/token` (proxied to backend)
- `http://46.62.153.166/api/users/me` (proxied to backend)
- etc.

## How It Works

**Before (broken):**
- Frontend: http://46.62.153.166:80
- API: http://46.62.153.166:8000
- CORS errors because different ports

**After (fixed):**
- Frontend: http://46.62.153.166/ → nginx → React app
- API: http://46.62.153.166/api/ → nginx → backend:8000
- No CORS issues, same origin

## Architecture

```
Browser → http://46.62.153.166/
         ↓
    Nginx (port 80)
         ↓
    ├─ / → React Frontend
    ├─ /api/ → FastAPI Backend (port 8000)
    └─ /static/ → Backend Static Files
```

## Troubleshooting

### If still getting CORS errors:

Check backend CORS configuration:
```bash
sudo docker logs abparts_api_prod | grep CORS
```

### If nginx not proxying:

Check nginx logs:
```bash
sudo docker logs abparts_web_prod
```

### If API not responding:

Check API is running:
```bash
sudo docker ps | grep api
sudo docker logs abparts_api_prod --tail=50
```

Test API directly:
```bash
curl http://localhost:8000/
```

## Port Configuration

- **Port 80**: Nginx (frontend + API proxy) - PUBLIC
- **Port 8000**: FastAPI backend - INTERNAL ONLY (accessed via nginx)
- **Port 5432**: PostgreSQL - INTERNAL ONLY
- **Port 6379**: Redis - INTERNAL ONLY

You can optionally close port 8000 in firewall since all API access goes through nginx.
