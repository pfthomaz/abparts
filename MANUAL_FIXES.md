# Manual Fixes for Production Issues

Based on the verification output, here are the issues and how to fix them:

## Issue 1: CORS_ALLOWED_ORIGINS not set to HTTPS

**Current**: Probably set to `http://` or localhost
**Required**: `https://abparts.oraseas.com`

**Fix**:
```bash
# Edit .env file
nano .env

# Find the line with CORS_ALLOWED_ORIGINS and change it to:
CORS_ALLOWED_ORIGINS=https://abparts.oraseas.com

# Or if you have multiple domains:
CORS_ALLOWED_ORIGINS=https://abparts.oraseas.com,https://www.abparts.oraseas.com
```

## Issue 2: ENVIRONMENT not set to production

**Fix**:
```bash
# Edit .env file
nano .env

# Add or change this line:
ENVIRONMENT=production
```

## Issue 3: SECRET_KEY is missing or too short

**Fix**:
```bash
# Generate a secure key
python3 -c "import secrets; print(secrets.token_urlsafe(32))"

# Copy the output and add to .env:
nano .env

# Add this line (replace with your generated key):
SECRET_KEY=<paste_generated_key_here>

# Also generate JWT_SECRET_KEY:
python3 -c "import secrets; print(secrets.token_urlsafe(32))"

# Add to .env:
JWT_SECRET_KEY=<paste_generated_key_here>
```

## Issue 4: Web service missing restart policy

**Status**: FALSE POSITIVE - The restart policy IS in docker-compose.prod.yml
The verification script has a bug. You can ignore this.

## Issue 5: Web is not running

**Fix**:
```bash
# Start the web container
docker compose -f docker-compose.prod.yml up -d web

# Check if it's running
docker compose ps web
```

## Issue 6: API health endpoint not responding

**Fix**:
```bash
# Restart the API
docker compose restart api

# Wait a few seconds
sleep 5

# Test health endpoint
docker compose exec api curl http://localhost:8000/health
```

## Issue 7: Could not retrieve migration version

**Fix**:
```bash
# Check if you're using the right database name
docker compose exec db psql -U abparts_user -d abparts_prod -c "SELECT version_num FROM alembic_version;"

# If it says "relation does not exist", run migrations:
docker compose exec api alembic upgrade head
```

## Complete Fix Script

Run these commands in order:

```bash
# 1. Edit .env file
nano .env

# Add/update these lines:
# ENVIRONMENT=production
# CORS_ALLOWED_ORIGINS=https://abparts.oraseas.com
# CORS_ALLOW_CREDENTIALS=true
# SECRET_KEY=<generate with: python3 -c "import secrets; print(secrets.token_urlsafe(32))">
# JWT_SECRET_KEY=<generate with: python3 -c "import secrets; print(secrets.token_urlsafe(32))">

# 2. Restart all services
docker compose -f docker-compose.prod.yml restart

# 3. Start web if not running
docker compose -f docker-compose.prod.yml up -d web

# 4. Wait for services to be ready
sleep 10

# 5. Run verification again
./verify_production_setup.sh
```

## Quick One-Liner Fix

If you want to fix everything at once:

```bash
# Generate keys
echo "SECRET_KEY=$(python3 -c 'import secrets; print(secrets.token_urlsafe(32))')" >> .env.new
echo "JWT_SECRET_KEY=$(python3 -c 'import secrets; print(secrets.token_urlsafe(32))')" >> .env.new
echo "ENVIRONMENT=production" >> .env.new
echo "CORS_ALLOWED_ORIGINS=https://abparts.oraseas.com" >> .env.new
echo "CORS_ALLOW_CREDENTIALS=true" >> .env.new

# Review and merge with existing .env
cat .env.new
# Then manually add these to your .env file

# Restart services
docker compose -f docker-compose.prod.yml restart
docker compose -f docker-compose.prod.yml up -d web
```

## After Fixing

Run the verification script again:
```bash
./verify_production_setup.sh
```

All checks should pass!
