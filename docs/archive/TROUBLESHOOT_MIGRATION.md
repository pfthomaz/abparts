# Troubleshoot Migration Detection Issue

## Problem
Alembic is not detecting the `net_cleaning_001` migration even though the file exists with the correct name.

## Diagnostic Steps

### Step 1: Verify File Exists on Server
```bash
ls -la backend/alembic/versions/net_cleaning_001_add_net_cleaning_tables.py
```
✓ Confirmed - file exists

### Step 2: Check Python Cache
The issue is likely cached Python bytecode. Run:
```bash
# Clear cache
docker compose exec api rm -rf /app/alembic/versions/__pycache__

# Restart API
docker compose restart api

# Wait 5 seconds
sleep 5
```

### Step 3: Verify Alembic Can See the Migration
```bash
docker compose exec api alembic history
```

Expected output should include:
```
ab2c1f16b0b3 -> net_cleaning_001, add_net_cleaning_tables
net_cleaning_001 -> 7b3899138d40, add_status_to_net_cleaning_records_and_make_end_time_nullable
```

### Step 4: Check for Import Errors
```bash
docker compose exec api python -c "from alembic.versions.net_cleaning_001_add_net_cleaning_tables import revision; print(revision)"
```

Should output: `net_cleaning_001`

### Step 5: Check Alembic Heads
```bash
docker compose exec api alembic heads
```

Should show: `7b3899138d40 (head)`

## Solution

If steps 2-3 don't work, try this alternative approach:

### Option A: Manual Stamp (if tables don't exist yet)
```bash
# Run the migration directly
docker compose exec api alembic upgrade net_cleaning_001
docker compose exec api alembic upgrade 7b3899138d40
```

### Option B: Check for Syntax Errors
```bash
# Validate the migration file
docker compose exec api python -m py_compile /app/alembic/versions/net_cleaning_001_add_net_cleaning_tables.py
```

### Option C: Rebuild API Container
If cache clearing doesn't work:
```bash
docker compose build --no-cache api
docker compose up -d api
```

## After Migration Works

Once `alembic upgrade head` succeeds:

1. **Verify tables created:**
```bash
docker compose exec db psql -U abparts_user -d abparts_prod -c "\dt" | grep -E "(farm_sites|nets|net_cleaning)"
```

2. **Check migration status:**
```bash
docker compose exec api alembic current
```
Should show: `7b3899138d40 (head)`

3. **Fix existing data:**
```bash
docker compose exec api python /app/fix_net_cleaning_status.py
```

4. **Rebuild frontend:**
```bash
docker compose build --no-cache web
docker compose restart
```

## Common Issues

### Issue: "Can't locate revision identified by 'net_cleaning_001'"
**Cause:** Python cache not cleared
**Fix:** Run Step 2 above

### Issue: "ImportError" when running migration
**Cause:** Syntax error in migration file
**Fix:** Check the file on server matches the local version

### Issue: Migration runs but tables not created
**Cause:** Database connection issue or transaction rollback
**Fix:** Check API logs: `docker compose logs api --tail=50`
