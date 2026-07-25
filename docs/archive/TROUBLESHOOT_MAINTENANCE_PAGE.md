# Troubleshooting: Maintenance Executions Page

## Your Current Errors
1. ❌ "Failed to load protocols. Using cached data if available."
2. ❌ Can't see list of machines (dropdown is empty)

## Step-by-Step Troubleshooting

### Step 1: Hard Refresh (DO THIS FIRST!)
**Mac:** `Cmd + Shift + R`
**Windows:** `Ctrl + Shift + R`

**Why?** The new code with caching support needs to be loaded. Your browser is using old cached JavaScript.

---

### Step 2: Verify Backend is Running
```bash
docker-compose ps
```

You should see:
- `abparts-api` - Up
- `abparts-db` - Up
- `abparts-web` - Up

If any are not running:
```bash
docker-compose up -d
```

---

### Step 3: Test Backend Endpoints
```bash
# Run the test script
docker-compose exec api python test_backend_maintenance.py
```

This will check:
- ✅ Database connection
- ✅ Machines in database
- ✅ Protocols in database
- ✅ Active users

**Expected output:**
```
✅ Database connection: OK
✅ Machines in database: X
✅ Maintenance protocols in database: X
✅ Active users in database: X
```

---

### Step 4: Check What's Missing

#### If "No machines in database":
You need to create at least one machine:
1. Go to Machines page in the app
2. Click "Add Machine"
3. Fill in the form and save

#### If "No maintenance protocols in database":
Run the sample protocols script:
```bash
docker-compose exec api python add_sample_protocols.py
```

This will create sample daily and scheduled maintenance protocols.

---

### Step 5: Check Browser Console
1. Open DevTools (F12)
2. Go to Console tab
3. Refresh the Maintenance Executions page
4. Look for error messages

**Good signs (cache working):**
```
[MachinesService] Using cached machines (fresh): 5
[MaintenanceService] Using cached protocols (fresh): 3
```

**First load (populating cache):**
```
[MachinesService] Cached machines: 5
[MaintenanceService] Cached protocols: 3
```

**Bad signs (errors):**
```
Failed to load machines: Error: Request failed with status 500
Failed to load protocols: Error: Request timed out
```

---

### Step 6: Check Network Tab
1. Open DevTools (F12)
2. Go to Network tab
3. Refresh the page
4. Look for failed requests (red)

Check these endpoints:
- `/machines/` - Should return 200 with JSON array
- `/maintenance-protocols/` - Should return 200 with JSON array
- `/maintenance-protocols/executions` - Should return 200 with JSON array

**If you see 401 Unauthorized:**
- Your session expired
- Log out and log back in

**If you see 408 Timeout:**
- Backend is slow or stuck
- Check backend logs: `docker-compose logs api --tail=50`

**If you see 500 Server Error:**
- Backend error
- Check backend logs: `docker-compose logs api --tail=50`

---

### Step 7: Clear IndexedDB (If Needed)
If you're seeing weird caching issues:

1. Open DevTools (F12)
2. Go to Application tab
3. Expand IndexedDB in left sidebar
4. Right-click on `ABPartsOfflineDB`
5. Click "Delete database"
6. Hard refresh the page

---

### Step 8: Check Backend Logs
```bash
# View recent logs
docker-compose logs api --tail=100

# Follow logs in real-time
docker-compose logs -f api
```

Look for:
- Database connection errors
- SQL errors
- Python exceptions
- Timeout errors

---

## Common Issues and Solutions

### Issue: "Failed to load protocols" but machines load fine
**Cause:** Protocols API is timing out or returning error
**Solution:**
1. Check if protocols exist: `docker-compose exec api python test_backend_maintenance.py`
2. If no protocols, run: `docker-compose exec api python add_sample_protocols.py`
3. Check backend logs for errors

### Issue: Both machines and protocols fail to load
**Cause:** Backend is not responding or database is down
**Solution:**
1. Restart backend: `docker-compose restart api`
2. Check database: `docker-compose logs db --tail=50`
3. Check if database is accessible: `docker-compose exec db psql -U abparts_user -d abparts_dev -c "SELECT 1;"`

### Issue: Page loads but dropdowns are empty (no error message)
**Cause:** Data exists but not being displayed
**Solution:**
1. Check browser console for JavaScript errors
2. Verify data exists: `docker-compose exec api python test_backend_maintenance.py`
3. Check if user has permission to view data

### Issue: "No cached data available offline"
**Cause:** You're offline or backend is down, and cache is empty
**Solution:**
1. Connect to internet
2. Ensure backend is running
3. Load the page once while online to populate cache

---

## Quick Reset (Nuclear Option)

If nothing else works:

```bash
# Stop everything
docker-compose down

# Clear browser data
# 1. Open DevTools (F12)
# 2. Application > Clear storage > Clear site data

# Start everything fresh
docker-compose up -d

# Wait for services to start (30 seconds)
sleep 30

# Test backend
docker-compose exec api python test_backend_maintenance.py

# If no protocols, add samples
docker-compose exec api python add_sample_protocols.py

# Hard refresh browser (Cmd+Shift+R or Ctrl+Shift+R)
```

---

## Still Not Working?

Provide this information for further help:

1. **Browser console output:**
   - Open DevTools > Console
   - Copy all error messages

2. **Backend logs:**
   ```bash
   docker-compose logs api --tail=100 > backend_logs.txt
   ```

3. **Test script output:**
   ```bash
   docker-compose exec api python test_backend_maintenance.py > test_output.txt
   ```

4. **Network requests:**
   - Open DevTools > Network
   - Screenshot of failed requests

5. **Docker status:**
   ```bash
   docker-compose ps > docker_status.txt
   ```
