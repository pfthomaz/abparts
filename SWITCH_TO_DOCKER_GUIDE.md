# Switch to Full Docker Setup

## Current Setup (Hybrid)
- Host nginx serves frontend from `/home/abparts/abparts/frontend/build/`
- Docker containers run but web container is unused
- Manual file copying needed for updates

## New Setup (Full Docker)
- Host nginx only handles SSL/HTTPS
- Docker web container serves frontend
- All services in Docker
- Updates via `docker compose build && up`

## Benefits
✅ Consistent environments (dev = prod)
✅ Easy updates (one command)
✅ Easy rollback (use previous image)
✅ No manual file copying
✅ Better isolation
✅ Simpler deployment workflow

## Migration Steps

### 1. Copy files to server

```bash
# From your local machine
scp nginx-docker-proxy.conf diogo@46.62.153.166:/tmp/
scp switch_to_docker_proxy.sh diogo@46.62.153.166:/tmp/
```

### 2. SSH into server and run migration

```bash
ssh diogo@46.62.153.166

# Move files
sudo mv /tmp/nginx-docker-proxy.conf ~/abparts/
sudo mv /tmp/switch_to_docker_proxy.sh ~/abparts/

cd ~/abparts

# Make script executable
chmod +x switch_to_docker_proxy.sh

# Run the migration
./switch_to_docker_proxy.sh
```

### 3. Verify it works

```bash
# Check containers are running
sudo docker ps

# Test the site
curl -I https://abparts.oraseas.com/

# Open in browser
# https://abparts.oraseas.com
```

## What Changed

**Before:**
```
Browser → Host Nginx → Filesystem (/home/abparts/abparts/frontend/build/)
        → Host Nginx → Docker API (for /api/ requests)
```

**After:**
```
Browser → Host Nginx (SSL only) → Docker Web Container (frontend)
                                 → Docker API Container (backend via /api/)
```

## Future Updates

### Update Frontend
```bash
cd ~/abparts
git pull
sudo docker compose -f docker-compose.prod.yml build web
sudo docker compose -f docker-compose.prod.yml up -d web
```

### Update Backend
```bash
cd ~/abparts
git pull
sudo docker compose -f docker-compose.prod.yml build api
sudo docker compose -f docker-compose.prod.yml up -d api
```

### Update Both
```bash
cd ~/abparts
git pull
sudo docker compose -f docker-compose.prod.yml build
sudo docker compose -f docker-compose.prod.yml up -d
```

## Rollback

If something goes wrong:

```bash
# Restore old nginx config
sudo cp /etc/nginx/sites-enabled/abparts.oraseas.com.backup.* /etc/nginx/sites-enabled/abparts.oraseas.com
sudo systemctl reload nginx
```

## Cleanup (Optional)

After verifying everything works, you can remove the old build directory:

```bash
# Backup first
sudo mv /home/abparts/abparts/frontend/build /home/abparts/abparts/frontend/build.old

# Later, if everything is fine, delete it
# sudo rm -rf /home/abparts/abparts/frontend/build.old
```

## Architecture Diagram

```
┌─────────────────────────────────────────────────┐
│                   Internet                       │
│                  (HTTPS 443)                     │
└────────────────────┬────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────┐
│              Host Nginx (SSL)                    │
│         /etc/nginx/sites-enabled/                │
│                                                   │
│  - SSL termination                               │
│  - Proxy to Docker containers                    │
└────────────────────┬────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────┐
│            Docker Network                        │
│                                                   │
│  ┌──────────────────────────────────────────┐   │
│  │  web (nginx + React)                     │   │
│  │  Port: 3001                              │   │
│  │  - Serves frontend                       │   │
│  │  - Proxies /api/ to api container        │   │
│  └──────────────────────────────────────────┘   │
│                                                   │
│  ┌──────────────────────────────────────────┐   │
│  │  api (FastAPI)                           │   │
│  │  Port: 8000                              │   │
│  │  - Backend API                           │   │
│  │  - Connects to db and redis              │   │
│  └──────────────────────────────────────────┘   │
│                                                   │
│  ┌──────────────────────────────────────────┐   │
│  │  db (PostgreSQL)                         │   │
│  │  Port: 5432                              │   │
│  └──────────────────────────────────────────┘   │
│                                                   │
│  ┌──────────────────────────────────────────┐   │
│  │  redis                                   │   │
│  │  Port: 6379                              │   │
│  └──────────────────────────────────────────┘   │
└─────────────────────────────────────────────────┘
```
