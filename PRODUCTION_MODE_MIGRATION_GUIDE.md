# Production Mode Migration Guide

## Current Status
You're running **development mode** with `docker-compose.yml` (React dev server on port 3000).

## Goal
Switch to **production mode** with `docker-compose.prod.yml` (optimized nginx build on port 3001).

---

## Step-by-Step Migration

### 1. Run the Migration Script

On your production server:

```bash
cd ~/abparts
./switch_to_production_mode.sh
```

When prompted, type `yes` to confirm.

**What it does:**
- Stops dev containers
- Builds production images (takes 3-5 minutes)
- Starts production containers
- Verifies everything is running

**Expected downtime:** ~5 minutes

---

### 2. Clear Browser Cache

After migration completes:

**Option A - Hard Refresh:**
- Press `Ctrl + Shift + R` (Linux/Windows)
- Press `Cmd + Shift + R` (Mac)

**Option B - Clear Cache:**
- Open browser settings
- Clear cache and cookies for abparts.oraseas.com

---

### 3. Test the Application

Visit: https://abparts.oraseas.com

**Test credentials:**
- Username: `dthomaz`
- Password: `amFT1999!`

**What to test:**
- ✅ Login works
- ✅ Translations show actual text (not keys like `aiAssistant.messages.machineSelected`)
- ✅ AI Assistant works
- ✅ All pages load correctly

---

## What Changes in Production Mode

### Before (Development)
- React dev server on port 3000
- Unminified JavaScript
- Hot reload enabled
- Slower performance
- Source maps included

### After (Production)
- Nginx serving static files on port 3001
- Minified, optimized JavaScript
- Translations baked into bundles
- Better performance
- Smaller file sizes
- 4 uvicorn workers for API

---

## Nginx Configuration

**Good news:** Your nginx is already configured correctly!

**File:** `/etc/nginx/sites-available/abparts.oraseas.com`

**Current config (correct):**
```nginx
location / {
    proxy_pass http://localhost:3001;  # ✅ Already pointing to 3001
    ...
}
```

**No changes needed!**

---

## Managing Production Containers

### View Status
```bash
docker compose -f docker-compose.prod.yml ps
```

### View Logs
```bash
# All services
docker compose -f docker-compose.prod.yml logs -f

# Specific service
docker compose -f docker-compose.prod.yml logs -f web
docker compose -f docker-compose.prod.yml logs -f api
docker compose -f docker-compose.prod.yml logs -f ai_assistant
```

### Restart Services
```bash
# All services
docker compose -f docker-compose.prod.yml restart

# Specific service
docker compose -f docker-compose.prod.yml restart web
```

### Stop/Start
```bash
# Stop all
docker compose -f docker-compose.prod.yml down

# Start all
docker compose -f docker-compose.prod.yml up -d
```

---

## Troubleshooting

### Issue: Translation keys still showing

**Solution:**
1. Clear browser cache completely
2. Hard refresh (Ctrl+Shift+R)
3. Check web container logs:
   ```bash
   docker compose -f docker-compose.prod.yml logs web
   ```

### Issue: Web container not starting

**Solution:**
1. Check logs:
   ```bash
   docker compose -f docker-compose.prod.yml logs web
   ```
2. Rebuild:
   ```bash
   docker compose -f docker-compose.prod.yml build --no-cache web
   docker compose -f docker-compose.prod.yml up -d web
   ```

### Issue: API errors

**Solution:**
1. Check API logs:
   ```bash
   docker compose -f docker-compose.prod.yml logs api
   ```
2. Verify database connection:
   ```bash
   docker compose -f docker-compose.prod.yml ps db
   ```

### Issue: Need to rollback to dev mode

**Solution:**
```bash
docker compose -f docker-compose.prod.yml down
docker compose up -d
```

---

## Port Reference

| Service | Dev Port | Prod Port | Notes |
|---------|----------|-----------|-------|
| Frontend | 3000 | 3001 | Nginx proxies both to 443 |
| API | 8000 | 8000 | Same in both modes |
| AI Assistant | 8001 | 8001 | Same in both modes |
| Database | 5432 | 5432 | Same in both modes |
| Redis | 6379 | 6379 | Same in both modes |

---

## Production Benefits

✅ **Performance:** Minified bundles load faster  
✅ **Caching:** Static assets cached for 1 year  
✅ **Scalability:** 4 API workers handle more requests  
✅ **Reliability:** Production-optimized builds  
✅ **Security:** No source code in containers  
✅ **Translations:** Baked into bundles (no runtime loading)

---

## Next Steps After Migration

1. ✅ Run migration script
2. ✅ Clear browser cache
3. ✅ Test application
4. ✅ Monitor logs for 24 hours
5. ✅ Update any documentation referencing port 3000

---

## Questions?

- Check logs: `docker compose -f docker-compose.prod.yml logs -f`
- Check status: `docker compose -f docker-compose.prod.yml ps`
- Restart if needed: `docker compose -f docker-compose.prod.yml restart`
