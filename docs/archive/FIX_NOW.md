# Fix Production Issues NOW

## Quick Fix (3 commands)

```bash
# 1. Fix .env configuration
chmod +x auto_fix_env.sh
./auto_fix_env.sh

# 2. Restart services
docker compose restart

# 3. Start web container
docker compose up -d web
```

That's it! Then verify:
```bash
./verify_production_setup.sh
```

## What Each Command Does

### 1. `./auto_fix_env.sh`
- Backs up your current .env
- Sets `CORS_ALLOWED_ORIGINS=https://abparts.oraseas.com`
- Sets `ENVIRONMENT=production`
- Generates secure `SECRET_KEY` and `JWT_SECRET_KEY`
- Updates .env file automatically

### 2. `docker compose restart`
- Restarts all services with new environment variables
- API will pick up new CORS settings
- Database and Redis restart cleanly

### 3. `docker compose up -d web`
- Ensures web container is running
- Starts in detached mode
- Will restart automatically if it crashes

## Verification

After running the fixes:

```bash
./verify_production_setup.sh
```

Expected output:
```
✓ .env file exists
✓ CORS_ALLOWED_ORIGINS set to HTTPS
✓ ENVIRONMENT set to production
✓ SECRET_KEY is set
✓ Web service configured
✓ Web service has restart policy
✓ db is running
✓ redis is running
✓ api is running
✓ web is running
✓ celery_worker is running
✓ API health endpoint responding
✓ API status is healthy
✓ Database is connected
✓ Redis is connected
✓ CORS configuration found in logs
✓ Migration version: <version>

✓ All checks passed!
```

## If Issues Persist

### Web Container Won't Start

```bash
# Check logs
docker compose logs web

# Common issue: Build failed
docker compose build --no-cache web
docker compose up -d web
```

### API Health Check Fails

```bash
# Check API logs
docker compose logs api

# Restart API
docker compose restart api

# Wait and test
sleep 5
docker compose exec api curl http://localhost:8000/health
```

### CORS Still Not Working

```bash
# Verify .env
grep CORS .env

# Should show:
# CORS_ALLOWED_ORIGINS=https://abparts.oraseas.com
# CORS_ALLOW_CREDENTIALS=true

# Restart API to pick up changes
docker compose restart api

# Check logs
docker compose logs api | grep CORS
```

## Manual Alternative

If you prefer to fix manually:

```bash
# 1. Edit .env
nano .env

# Add/update these lines:
ENVIRONMENT=production
CORS_ALLOWED_ORIGINS=https://abparts.oraseas.com
CORS_ALLOW_CREDENTIALS=true

# Generate keys:
python3 -c "import secrets; print('SECRET_KEY=' + secrets.token_urlsafe(32))"
python3 -c "import secrets; print('JWT_SECRET_KEY=' + secrets.token_urlsafe(32))"

# Copy the output and add to .env

# 2. Restart
docker compose restart
docker compose up -d web
```

## After Everything Works

Once all checks pass, you can:

1. **Reset migrations** (one time):
   ```bash
   ./reset_migrations_clean.sh
   ```

2. **Use automated deployment** going forward:
   ```bash
   ./deploy_production_clean.sh
   ```

## Summary

The issues found are all configuration-related and easy to fix:
- ✅ CORS needs HTTPS domain
- ✅ ENVIRONMENT needs to be "production"
- ✅ SECRET_KEY needs to be generated
- ✅ Web container needs to be started

Run the 3 commands at the top and you're done!
