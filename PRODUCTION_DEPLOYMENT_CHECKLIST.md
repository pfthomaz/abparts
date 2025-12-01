# Production Deployment Checklist

## Pre-Deployment Verification

### 1. Environment File (.env)

Check that `.env` exists and contains:

```bash
# View current settings (run on server)
cat .env | grep -E "CORS|ENVIRONMENT|REACT_APP"
```

Required settings:
- [ ] `ENVIRONMENT=production`
- [ ] `CORS_ALLOWED_ORIGINS=https://abparts.oraseas.com` (or your domain)
- [ ] `CORS_ALLOW_CREDENTIALS=true`
- [ ] `REACT_APP_API_BASE_URL=/api`
- [ ] `SECRET_KEY=<secure_value>`
- [ ] `JWT_SECRET_KEY=<secure_value>`
- [ ] `POSTGRES_PASSWORD=<secure_value>`

If missing, create from template:
```bash
cp .env.production.example .env
nano .env  # Edit with actual values
```

### 2. Docker Compose Configuration

Verify `docker-compose.prod.yml` has web service:

```yaml
web:
  build:
    context: ./frontend
    dockerfile: Dockerfile.frontend
    target: production
  container_name: abparts_web_prod
  ports:
    - "3001:80"
  restart: unless-stopped
```

- [ ] Web service exists
- [ ] Port 3001:80 mapping correct
- [ ] restart: unless-stopped set

### 3. Migration Status

Check current migration state:

```bash
docker compose exec db psql -U abparts_user -d abparts_prod -c "SELECT * FROM alembic_version;"
```

- [ ] Migration version recorded
- [ ] If messy history, plan to run `reset_migrations_clean.sh`

## Deployment Steps

### Option A: Automated Deployment (Recommended)

```bash
./deploy_production_clean.sh
```

This script handles everything automatically.

### Option B: Manual Deployment

#### Step 1: Stop Services
```bash
docker compose -f docker-compose.prod.yml down
```

#### Step 2: Build Images
```bash
docker compose -f docker-compose.prod.yml build --no-cache
```

#### Step 3: Start Services
```bash
docker compose -f docker-compose.prod.yml up -d
```

#### Step 4: Check Status
```bash
docker compose -f docker-compose.prod.yml ps
```

## Post-Deployment Verification

### 1. Service Status

```bash
docker compose -f docker-compose.prod.yml ps
```

Expected output:
- [ ] db: Up (healthy)
- [ ] redis: Up (healthy)
- [ ] api: Up
- [ ] web: Up
- [ ] celery_worker: Up

### 2. API Health Check

```bash
curl https://abparts.oraseas.com/api/health
```

Expected: `{"status":"healthy","database":"connected","redis":"connected"}`

- [ ] Status is healthy
- [ ] Database connected
- [ ] Redis connected

### 3. Frontend Access

```bash
curl -I https://abparts.oraseas.com
```

Expected: `HTTP/2 200`

- [ ] Returns 200 OK
- [ ] Page loads in browser

### 4. CORS Configuration

```bash
docker compose logs api | grep "CORS configuration"
```

Expected output should show:
```
CORS configuration loaded:
  Allowed origins: ['https://abparts.oraseas.com']
  Allow credentials: True
```

- [ ] Correct domain in allowed origins
- [ ] Allow credentials is True

### 5. Login Test

1. Open https://abparts.oraseas.com
2. Try to login
3. Check browser console for errors

- [ ] No CORS errors
- [ ] No 500 errors
- [ ] Login works

### 6. API Documentation

Visit https://abparts.oraseas.com/api/docs

- [ ] Swagger UI loads
- [ ] Can see API endpoints
- [ ] No CORS errors

## Troubleshooting

### Web Container Not Starting

**Symptoms**: `docker compose ps` shows web as "Exited" or "Restarting"

**Fix**:
```bash
# Check logs
docker compose logs web

# Rebuild
docker compose build --no-cache web
docker compose up -d web
```

### CORS Errors in Browser

**Symptoms**: Console shows "CORS policy" errors

**Fix**:
```bash
# 1. Check .env has correct domain
grep CORS_ALLOWED_ORIGINS .env

# 2. Should show: CORS_ALLOWED_ORIGINS=https://abparts.oraseas.com

# 3. If wrong, edit .env
nano .env

# 4. Restart API
docker compose restart api

# 5. Verify
docker compose logs api | grep "CORS configuration"
```

### API Returns 500 Errors

**Symptoms**: Login fails with 500 error, logs show "column does not exist"

**Fix**:
```bash
# Check what columns are missing
docker compose logs api | grep "column"

# Run migration reset if needed
./reset_migrations_clean.sh

# Or apply specific fix
docker compose exec -T db psql -U abparts_user -d abparts_prod < fix_missing_hybrid_storage_schema.sql
```

### Database Connection Failed

**Symptoms**: API health check shows database unreachable

**Fix**:
```bash
# Check database is running
docker compose ps db

# Check database logs
docker compose logs db

# Restart database
docker compose restart db

# Wait 10 seconds
sleep 10

# Restart API
docker compose restart api
```

## Maintenance Commands

### View Logs
```bash
# All services
docker compose -f docker-compose.prod.yml logs -f

# Specific service
docker compose logs -f api
docker compose logs -f web
```

### Restart Service
```bash
docker compose restart api
docker compose restart web
```

### Update Code
```bash
# Pull latest code
git pull

# Rebuild and restart
docker compose -f docker-compose.prod.yml up -d --build
```

### Database Backup
```bash
# Backup
docker compose exec -T db pg_dump -U abparts_user abparts_prod > backup_$(date +%Y%m%d).sql

# Restore
docker compose exec -T db psql -U abparts_user abparts_prod < backup_20241201.sql
```

## Migration Management

### Create New Migration
```bash
# 1. Edit models
nano backend/app/models.py

# 2. Generate migration
docker compose exec api alembic revision --autogenerate -m "description"

# 3. Review migration
nano backend/alembic/versions/<new_file>.py

# 4. Apply migration
docker compose exec api alembic upgrade head

# 5. Restart API
docker compose restart api
```

### Check Migration Status
```bash
docker compose exec db psql -U abparts_user -d abparts_prod -c "SELECT * FROM alembic_version;"
```

### Reset to Clean Baseline (One Time)
```bash
./reset_migrations_clean.sh
```

## Security Checklist

- [ ] `.env` file has secure passwords
- [ ] `.env` file is not in git (check `.gitignore`)
- [ ] `SECRET_KEY` is random and secure
- [ ] `JWT_SECRET_KEY` is random and secure
- [ ] `POSTGRES_PASSWORD` is strong
- [ ] CORS only allows your domain
- [ ] HTTPS is enforced (`FORCE_HTTPS=true`)
- [ ] Database port (5432) is not exposed publicly
- [ ] Redis port (6379) is not exposed publicly

## Performance Checklist

- [ ] API runs with multiple workers (`--workers 4`)
- [ ] Celery worker is running
- [ ] Redis is running for caching
- [ ] Static files are served efficiently
- [ ] Database has proper indexes
- [ ] Logs are not filling disk space

## Monitoring

### Check Disk Space
```bash
df -h
```

### Check Container Resources
```bash
docker stats
```

### Check Database Size
```bash
docker compose exec db psql -U abparts_user -d abparts_prod -c "SELECT pg_size_pretty(pg_database_size('abparts_prod'));"
```

### Check Logs Size
```bash
du -sh /var/lib/docker/containers/*/*-json.log
```

## Summary

All three original issues are resolved:

1. ✅ **Migrations**: Clean baseline with `reset_migrations_clean.sh`
2. ✅ **Web Container**: Properly configured in `docker-compose.prod.yml`
3. ✅ **CORS**: Environment-aware via `.env` configuration

The system is production-ready with proper automation and monitoring.
