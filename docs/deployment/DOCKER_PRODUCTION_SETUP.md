# ABParts Docker Production Setup

## Architecture

```
Internet (HTTPS/443)
    ↓
Host Nginx (SSL Termination)
    ↓
┌─────────────────────────────────────┐
│ Docker Compose Stack                │
│                                     │
│  ┌──────────────┐  ┌─────────────┐ │
│  │ Web (3001)   │  │ API (8000)  │ │
│  │ React + Nginx│←─│ FastAPI     │ │
│  └──────────────┘  └─────────────┘ │
│         ↓                  ↓        │
│  ┌──────────────┐  ┌─────────────┐ │
│  │ PostgreSQL   │  │ Redis       │ │
│  └──────────────┘  └─────────────┘ │
│                                     │
│  Volumes:                           │
│  - db_data_prod (database)          │
│  - /var/www/abparts_images (images) │
└─────────────────────────────────────┘
```

## Components

### 1. Host Nginx (Port 80/443)
- **Purpose:** SSL termination and reverse proxy
- **Config:** `/etc/nginx/sites-available/abparts.oraseas.com`
- **Proxies to:** Docker web container on port 3001

### 2. Docker Web Container (Port 3001)
- **Image:** Built from `frontend/Dockerfile.frontend`
- **Contains:** React production build + nginx
- **Rebuilds:** When frontend code changes
- **Access:** Via host nginx only

### 3. Docker API Container (Port 8000)
- **Image:** Built from `backend/Dockerfile.backend`
- **Contains:** FastAPI application
- **Rebuilds:** When backend code changes
- **Serves:** API endpoints and uploaded images

### 4. Docker Database (Port 5432)
- **Image:** postgres:16
- **Volume:** `db_data_prod` (persistent)
- **Backup:** Included in backup script

### 5. Images Storage
- **Location:** `/var/www/abparts_images/` (host)
- **Mounted to:** `/app/static/images/` (in API container)
- **Contains:** Part images, user photos, org logos
- **Backup:** Included in backup script

## Deployment Workflow

### Initial Setup (One Time)

```bash
# 1. Clone repository
cd ~
git clone <repo-url> abparts
cd abparts

# 2. Create .env file
cp .env.production .env
# Edit .env with your values

# 3. Update host nginx config
sudo cp nginx-production.conf /etc/nginx/sites-available/abparts.oraseas.com
sudo ln -s /etc/nginx/sites-available/abparts.oraseas.com /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx

# 4. Start Docker containers
sudo docker compose -f docker-compose.prod.yml up -d

# 5. Run database migrations
sudo docker exec abparts_api_prod alembic upgrade head
```

### Regular Deployment (Code Updates)

```bash
# Option 1: Use deployment script
bash deploy_production.sh

# Option 2: Manual steps
git pull
sudo docker compose -f docker-compose.prod.yml build web api
sudo docker compose -f docker-compose.prod.yml up -d
```

**That's it!** No need to build locally or copy files.

## Backup & Restore

### Create Backup

```bash
# Run backup script
bash backup_production.sh

# Backup location
ls -lh /var/backups/abparts/
```

**Backup includes:**
- Complete database dump
- All images (parts, users, logos)
- Configuration files
- Docker compose setup

### Restore from Backup

```bash
# On new server
bash restore_production.sh /path/to/backup.tar.gz
```

**Portable!** The backup can be restored on any server with Docker installed.

## Common Operations

### View Logs
```bash
# All services
sudo docker compose -f docker-compose.prod.yml logs -f

# Specific service
sudo docker compose -f docker-compose.prod.yml logs -f web
sudo docker compose -f docker-compose.prod.yml logs -f api
```

### Restart Services
```bash
# All services
sudo docker compose -f docker-compose.prod.yml restart

# Specific service
sudo docker compose -f docker-compose.prod.yml restart web
```

### Rebuild After Code Changes
```bash
# Frontend changes
sudo docker compose -f docker-compose.prod.yml build web
sudo docker compose -f docker-compose.prod.yml up -d web

# Backend changes
sudo docker compose -f docker-compose.prod.yml build api
sudo docker compose -f docker-compose.prod.yml up -d api
```

### Database Operations
```bash
# Access database
sudo docker exec -it abparts_db_prod psql -U abparts_user abparts_prod

# Run migrations
sudo docker exec abparts_api_prod alembic upgrade head

# Create migration
sudo docker exec abparts_api_prod alembic revision --autogenerate -m "description"
```

## Automated Backups

Add to crontab for daily backups:

```bash
# Edit crontab
sudo crontab -e

# Add this line (daily at 2 AM)
0 2 * * * /home/abparts/abparts/backup_production.sh >> /var/log/abparts_backup.log 2>&1
```

## Troubleshooting

### Frontend not updating
```bash
# Force rebuild without cache
sudo docker compose -f docker-compose.prod.yml build --no-cache web
sudo docker compose -f docker-compose.prod.yml up -d web
```

### Images not showing
```bash
# Check mount
sudo docker exec abparts_api_prod ls /app/static/images | wc -l

# Check permissions
ls -la /var/www/abparts_images/
```

### SSL certificate renewal
```bash
# Renew certificates
sudo certbot renew

# Restart nginx
sudo systemctl restart nginx
```

## Benefits of This Setup

✅ **Portable:** Entire app in Docker, easy to move servers
✅ **Consistent:** Same build process everywhere
✅ **Automated:** No manual file copying
✅ **Backupable:** Complete backup/restore scripts
✅ **Scalable:** Easy to add more containers
✅ **Maintainable:** Clear separation of concerns
