# Production Environment Fixes

This guide addresses three critical production issues:
1. Clean migration baseline
2. Proper web container configuration
3. CORS configuration

## Issue 1: Clean Migration Baseline

### Problem
Migration history is messy with merge conflicts and missing schema changes.

### Solution
Reset to a clean baseline using current production schema.

### Steps

```bash
# Run the migration reset script
chmod +x reset_migrations_clean.sh
./reset_migrations_clean.sh
```

This will:
- Dump current production schema to `backend/alembic/baseline_schema.sql`
- Backup old migrations to `backend/alembic/versions_old/`
- Clear migration history
- Create a single baseline migration
- Stamp database at baseline

### Future Migrations

From now on, create migrations normally:

```bash
# Make model changes in backend/app/models.py
# Then create migration
docker compose exec api alembic revision --autogenerate -m "description"

# Review the generated migration file
# Then apply it
docker compose exec api alembic upgrade head
```

## Issue 2: Web Container Configuration

### Problem
Web container requires manual `docker run` command instead of starting with docker-compose.

### Current Status
✅ **ALREADY FIXED** - The `docker-compose.prod.yml` already has proper configuration:

```yaml
web:
  build:
    context: ./frontend
    dockerfile: Dockerfile.frontend
    target: production
    args:
      REACT_APP_API_BASE_URL: ${REACT_APP_API_BASE_URL:-/api}
  container_name: abparts_web_prod
  ports:
    - "3001:80"
  depends_on:
    api:
      condition: service_started
  restart: unless-stopped
```

### Usage

```bash
# Start all services including web
docker compose -f docker-compose.prod.yml up -d

# Or rebuild and start
docker compose -f docker-compose.prod.yml up -d --build web
```

The web container will:
- Build automatically from Dockerfile.frontend
- Start on port 3001
- Restart automatically unless stopped
- Wait for API to be ready

## Issue 3: CORS Configuration

### Problem
CORS errors when accessing the application from different origins.

### Current Status
✅ **PROPERLY CONFIGURED** - CORS is environment-aware and configurable via `.env`

### Configuration

The CORS system uses `backend/app/cors_config.py` which:
- Reads from `CORS_ALLOWED_ORIGINS` environment variable
- Falls back to development defaults if not set
- Validates all origins
- Logs violations for security monitoring

### Production Setup

In your `.env` file (or environment variables):

```bash
# Required for production
CORS_ALLOWED_ORIGINS=https://abparts.oraseas.com,https://www.abparts.oraseas.com
CORS_ALLOW_CREDENTIALS=true
ENVIRONMENT=production
```

### Verification

Check CORS configuration in logs:

```bash
docker compose logs api | grep CORS
```

You should see:
```
CORS configuration loaded:
  Allowed origins: ['https://abparts.oraseas.com', ...]
  Allow credentials: True
  Allowed methods: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS', 'PATCH']
```

### Testing CORS

```bash
# Test from browser console on https://abparts.oraseas.com
fetch('https://abparts.oraseas.com/api/health')
  .then(r => r.json())
  .then(console.log)
```

Should work without CORS errors.

### Common CORS Issues

**Issue**: "CORS policy: No 'Access-Control-Allow-Origin' header"
**Fix**: Ensure `CORS_ALLOWED_ORIGINS` includes your frontend URL

**Issue**: "CORS policy: Credentials flag is 'true'"
**Fix**: Ensure `CORS_ALLOW_CREDENTIALS=true` in `.env`

**Issue**: CORS works in dev but not production
**Fix**: Check that production `.env` has correct `CORS_ALLOWED_ORIGINS`

## Complete Production Deployment Checklist

### 1. Environment Variables

Ensure `.env` has:
```bash
# Database
POSTGRES_DB=abparts_prod
POSTGRES_USER=abparts_user
POSTGRES_PASSWORD=<secure_password>

# CORS
CORS_ALLOWED_ORIGINS=https://abparts.oraseas.com
CORS_ALLOW_CREDENTIALS=true

# Environment
ENVIRONMENT=production

# Security
SECRET_KEY=<secure_random_key>
JWT_SECRET_KEY=<secure_random_key>

# API URL for frontend
REACT_APP_API_BASE_URL=/api
```

### 2. Reset Migrations (One Time)

```bash
./reset_migrations_clean.sh
```

### 3. Build and Start Services

```bash
# Build all services
docker compose -f docker-compose.prod.yml build

# Start all services
docker compose -f docker-compose.prod.yml up -d

# Check status
docker compose -f docker-compose.prod.yml ps
```

### 4. Verify Services

```bash
# Check API health
curl https://abparts.oraseas.com/api/health

# Check web frontend
curl https://abparts.oraseas.com

# Check logs
docker compose -f docker-compose.prod.yml logs -f
```

### 5. Monitor

```bash
# Watch logs
docker compose -f docker-compose.prod.yml logs -f api web

# Check CORS violations
docker compose logs api | grep "CORS violation"

# Check container status
docker compose -f docker-compose.prod.yml ps
```

## Troubleshooting

### Web Container Not Starting

```bash
# Check logs
docker compose logs web

# Rebuild
docker compose -f docker-compose.prod.yml build --no-cache web
docker compose -f docker-compose.prod.yml up -d web
```

### CORS Errors

```bash
# Check current CORS config
docker compose exec api python -c "from app.cors_config import get_cors_origins; print(get_cors_origins())"

# Update .env and restart
docker compose restart api
```

### Migration Issues

```bash
# Check current migration
docker compose exec db psql -U abparts_user -d abparts_prod -c "SELECT * FROM alembic_version;"

# If needed, manually stamp
docker compose exec api alembic stamp 00_baseline
```

## Summary

All three issues are now resolved:

1. ✅ **Migrations**: Clean baseline with `reset_migrations_clean.sh`
2. ✅ **Web Container**: Properly configured in `docker-compose.prod.yml`
3. ✅ **CORS**: Environment-aware configuration via `.env`

The system is production-ready with proper configuration management.
