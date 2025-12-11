# Production Deployment Log

This document tracks changes that need to be deployed to production.

## Pending Deployments

### 1. Stock Adjustments Fix (In Progress)

**Status:** 🔧 Investigating

**Issue:** Stock adjustments not appearing in Adjustment History

**Changes Needed:**
- [ ] Code fixes (TBD after investigation)
- [ ] Database migration (if schema changes needed)

**Database Changes for Production:**
- TBD after local testing

---

## Completed Deployments

### 2024-11-28: Nginx Location Priority Fix
- **Issue:** Part images returning 404
- **Fix:** Added `^~` modifier to `/static/images/` location in nginx.conf
- **Files Changed:** `frontend/nginx.conf`
- **Deployment:** Rebuild web container
- **Status:** ✅ Deployed

### 2024-11-28: Docker Proxy Setup
- **Issue:** Hybrid setup with host nginx serving from filesystem
- **Fix:** Host nginx now proxies everything to Docker containers
- **Files Changed:** `/etc/nginx/sites-enabled/abparts.oraseas.com`
- **Status:** ✅ Deployed

### 2024-11-28: Frontend API URL Fix
- **Issue:** Frontend hardcoded `localhost:8000` as fallback
- **Fix:** Set `REACT_APP_API_BASE_URL=/api` before build in Dockerfile
- **Files Changed:** `frontend/Dockerfile.frontend`, `frontend/.dockerignore`
- **Status:** ✅ Deployed

### 2024-11-28: CORS Configuration
- **Issue:** CORS blocking HTTPS requests
- **Fix:** Updated CORS_ALLOWED_ORIGINS to include `https://abparts.oraseas.com`
- **Files Changed:** `.env` on server
- **Status:** ✅ Deployed

---

## Deployment Checklist Template

When deploying changes:

1. **Local Testing**
   - [ ] Test in local development environment
   - [ ] Verify database migrations work
   - [ ] Check for any breaking changes

2. **Code Deployment**
   - [ ] Commit changes to git
   - [ ] Push to repository
   - [ ] Pull on production server
   - [ ] Rebuild affected containers

3. **Database Changes**
   - [ ] Create Alembic migration if needed
   - [ ] Test migration on local database
   - [ ] Backup production database
   - [ ] Run migration on production

4. **Verification**
   - [ ] Check application logs
   - [ ] Test affected functionality
   - [ ] Monitor for errors

---

## Quick Commands

### Local Development
```bash
# Start local environment
docker-compose up

# Create migration
docker-compose exec api alembic revision --autogenerate -m "description"

# Run migration
docker-compose exec api alembic upgrade head

# Check database
docker-compose exec db psql -U abparts_user -d abparts_dev
```

### Production Deployment
```bash
# On server
cd ~/abparts
git pull
sudo docker compose -f docker-compose.prod.yml build
sudo docker compose -f docker-compose.prod.yml up -d

# Run migration
sudo docker compose -f docker-compose.prod.yml exec api alembic upgrade head

# Check logs
sudo docker compose -f docker-compose.prod.yml logs api --tail 50
```
