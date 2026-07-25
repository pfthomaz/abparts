# Quick Fix: Maintenance Executions Page Not Loading

## Current Issue
- Error: "Failed to load protocols. Using cached data if available."
- Machines dropdown is empty
- Can't select machine or protocol

## Root Cause
The API calls are timing out or failing, and there's no cached data yet.

## Immediate Fix Steps

### Step 1: Hard Refresh (CRITICAL)
**Mac:** `Cmd + Shift + R`
**Windows:** `Ctrl + Shift + R`

This loads the new JavaScript code with caching support.

### Step 2: Check Backend is Running
```bash
# Check if API is responding
curl http://localhost:8000/health

# Should return: {"status":"healthy"}
```

If backend is not running:
```bash
docker-compose up api
```

### Step 3: Populate Cache (First Time Only)
The first time you load the page, it needs to fetch data from the API to populate the cache.

1. Open browser DevTools (F12)
2. Go to Console tab
3. Navigate to Maintenance Executions page
4. Look for these log messages:
   - `[MachinesService] Cached machines: X`
   - `[MaintenanceService] Cached protocols: X`

If you see these messages, the cache is populated and subsequent loads will be fast.

### Step 4: Check for Errors in Console
Look for specific error messages:
- **401 Unauthorized** → Your session expired, log in again
- **408 Timeout** → Backend is slow, check backend logs
- **500 Server Error** → Backend error, check backend logs
- **Network Error** → Backend not running or wrong URL

### Step 5: Check Backend Logs
```bash
# View API logs
docker-compose logs api --tail=50

# Look for errors related to:
# - /machines/
# - /maintenance-protocols/
# - Database connection issues
```

## Common Issues and Solutions

### Issue: "No cached data available offline"
**Solution:** You're offline or backend is down. The page needs to load data at least once while online to populate the cache.

### Issue: Machines dropdown is empty but no error
**Solution:** 
1. Check if you have any machines in the database
2. Run: `docker-compose exec api python -c "from app.database import SessionLocal; from app.models import Machine; db = SessionLocal(); print(f'Machines: {db.query(Machine).count()}'); db.close()"`

### Issue: Protocols dropdown is empty but no error
**Solution:**
1. Check if you have any protocols in the database
2. Run the sample protocols script: `docker-compose exec api python add_sample_protocols.py`

### Issue: Page loads but dropdowns are empty
**Solution:** Check browser console for JavaScript errors. You may need to clear IndexedDB:
1. Open DevTools (F12)
2. Go to Application > Storage > IndexedDB
3. Delete `ABPartsOfflineDB`
4. Hard refresh the page

## Verify Fix is Working

After hard refresh, you should see in the console:
```
[MachinesService] Using cached machines (fresh): X
[MaintenanceService] Using cached protocols (fresh): X
```

Or if cache is empty:
```
[MachinesService] Cached machines: X
[MaintenanceService] Cached protocols: X
```

## Still Not Working?

If the page still doesn't load after these steps:

1. **Check your auth token is valid:**
   - Open DevTools > Application > Local Storage
   - Look for `authToken`
   - If missing or expired, log in again

2. **Check backend database connection:**
   ```bash
   docker-compose exec api python -c "from app.database import engine; engine.connect(); print('DB Connected')"
   ```

3. **Restart everything:**
   ```bash
   docker-compose down
   docker-compose up
   ```

4. **Check for port conflicts:**
   ```bash
   lsof -i :8000  # Check if port 8000 is in use
   lsof -i :3000  # Check if port 3000 is in use
   ```

## Need More Help?

Share the following information:
1. Browser console errors (screenshot or copy/paste)
2. Backend logs: `docker-compose logs api --tail=100`
3. Network tab in DevTools showing failed requests
4. Output of: `docker-compose ps`
