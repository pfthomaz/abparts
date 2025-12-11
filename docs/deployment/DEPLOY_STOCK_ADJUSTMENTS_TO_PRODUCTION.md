# Deploy Stock Adjustments to Production

## Pre-Deployment Checklist

### 1. Fix Migration Revision ID (CRITICAL!)

The current migration has a revision ID that's **37 characters** (exceeds 32-char limit):
```
❌ revision = '20241130_redesign_stock_adjustments'  # 37 chars - TOO LONG!
```

**Action Required:** Update the migration file before deploying!

### 2. Verify Down Revision

Check that `down_revision` matches the actual revision ID in production:
```bash
# On production server, check current migration
docker-compose exec api alembic current
```

Expected: `20251124_order_txn` (or similar)

### 3. Check for Multiple Heads

```bash
# On production server
docker-compose exec api alembic heads
```

Should show only ONE head. If multiple heads exist, create a merge migration first.

---

## Step-by-Step Deployment Process

### Phase 1: Pre-Deployment Verification (Development)

**1.1 Fix the Migration File**

Update `backend/alembic/versions/20241130_redesign_stock_adjustments.py`:

```python
# Change line 17 from:
revision = '20241130_redesign_stock_adjustments'  # ❌ 37 chars

# To:
revision = '20241130_stock_adj'  # ✅ 19 chars
```

**1.2 Test Migration Locally**

```bash
# In development environment
cd backend
docker-compose exec api alembic downgrade -1
docker-compose exec api alembic upgrade head

# Verify it works
docker-compose exec api alembic current
# Should show: 20241130_stock_adj (head)
```

**1.3 Test the Application**

```bash
# Run comprehensive test
python test_stock_adjustment_complete.py

# Verify:
# - Can create stock adjustments
# - Can list stock adjustments
# - Can view details
# - Inventory updates correctly
```

**1.4 Commit the Fixed Migration**

```bash
git add backend/alembic/versions/20241130_redesign_stock_adjustments.py
git commit -m "fix: shorten stock adjustment migration revision ID to 19 chars"
git push origin main
```

---

### Phase 2: Production Backup (CRITICAL!)

**2.1 Backup Production Database**

```bash
# SSH to production server
ssh root@abparts.oraseas.com

# Create backup directory
mkdir -p ~/backups/$(date +%Y%m%d)

# Backup database
docker-compose exec -T db pg_dump -U abparts_user abparts_prod > \
  ~/backups/$(date +%Y%m%d)/abparts_pre_stock_adjustments_$(date +%H%M%S).sql

# Verify backup was created
ls -lh ~/backups/$(date +%Y%m%d)/
```

**2.2 Backup Current Code**

```bash
# On production server
cd ~/abparts
git branch backup-before-stock-adjustments-$(date +%Y%m%d)
git log -1 --oneline  # Note current commit
```

---

### Phase 3: Deploy Code Changes

**3.1 Pull Latest Code**

```bash
# On production server
cd ~/abparts

# Stash any local changes
git stash

# Pull latest
git pull origin main

# Verify the migration file has correct revision ID
grep "^revision = " backend/alembic/versions/20241130_redesign_stock_adjustments.py
# Should show: revision = '20241130_stock_adj'
```

**3.2 Check Migration Status**

```bash
# Check current migration in production
docker-compose exec api alembic current

# Check for multiple heads
docker-compose exec api alembic heads

# View migration history
docker-compose exec api alembic history | head -20
```

**3.3 Verify Down Revision Matches**

```bash
# Get current production revision
CURRENT=$(docker-compose exec api alembic current | grep -oP '[a-f0-9_]+' | head -1)
echo "Current production revision: $CURRENT"

# Check migration file
grep "^down_revision = " backend/alembic/versions/20241130_redesign_stock_adjustments.py
# Should match the current revision
```

---

### Phase 4: Run Migration (The Critical Moment!)

**4.1 Stop Application (Optional but Recommended)**

```bash
# Stop API to prevent concurrent writes during migration
docker-compose stop api

# Keep database running
docker-compose ps
```

**4.2 Dry Run Check**

```bash
# Show what will be executed
docker-compose exec api alembic upgrade head --sql > /tmp/migration_preview.sql

# Review the SQL
less /tmp/migration_preview.sql
```

**4.3 Run the Migration**

```bash
# Run migration with output logging
docker-compose exec api alembic upgrade head 2>&1 | tee ~/migration_$(date +%Y%m%d_%H%M%S).log

# Expected output:
# INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
# INFO  [alembic.runtime.migration] Will assume transactional DDL.
# INFO  [alembic.runtime.migration] Running upgrade 20251124_order_txn -> 20241130_stock_adj, redesign stock adjustments system
```

**4.4 Verify Migration Success**

```bash
# Check current version
docker-compose exec api alembic current
# Should show: 20241130_stock_adj (head)

# Check database structure
docker-compose exec db psql -U abparts_user -d abparts_prod -c "\d stock_adjustments"
docker-compose exec db psql -U abparts_user -d abparts_prod -c "\d stock_adjustment_items"

# Verify enum was created
docker-compose exec db psql -U abparts_user -d abparts_prod -c "\dT+ adjustmenttype"
```

---

### Phase 5: Rebuild and Restart Services

**5.1 Rebuild Backend (if needed)**

```bash
# Only if you changed dependencies
docker-compose build api
```

**5.2 Restart Services**

```bash
# Start API
docker-compose up -d api

# Check logs for errors
docker-compose logs -f api --tail=50
```

**5.3 Rebuild Frontend**

```bash
# Rebuild with new stock adjustments components
docker-compose build web
docker-compose up -d web

# Check logs
docker-compose logs -f web --tail=20
```

---

### Phase 6: Post-Deployment Verification

**6.1 Check API Health**

```bash
# Test API is responding
curl -I https://abparts.oraseas.com/api/docs

# Should return 200 OK
```

**6.2 Test Stock Adjustments Endpoint**

```bash
# Get auth token (replace with actual credentials)
TOKEN=$(curl -X POST "https://abparts.oraseas.com/api/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin@oraseas.ee&password=YOUR_PASSWORD" \
  | jq -r '.access_token')

# Test list endpoint
curl -H "Authorization: Bearer $TOKEN" \
  "https://abparts.oraseas.com/api/stock-adjustments/" | jq '.'

# Should return empty list or existing adjustments
```

**6.3 Test Frontend**

1. Open browser: https://abparts.oraseas.com
2. Login as admin
3. Navigate to Inventory → Stock Adjustments
4. Verify page loads without errors
5. Try creating a test stock adjustment
6. Verify it appears in the list
7. Check warehouse inventory was updated

**6.4 Check Database Integrity**

```bash
# Verify tables exist
docker-compose exec db psql -U abparts_user -d abparts_prod -c "
  SELECT table_name 
  FROM information_schema.tables 
  WHERE table_name IN ('stock_adjustments', 'stock_adjustment_items')
  ORDER BY table_name;
"

# Check for any orphaned data
docker-compose exec db psql -U abparts_user -d abparts_prod -c "
  SELECT COUNT(*) as total_adjustments FROM stock_adjustments;
"

docker-compose exec db psql -U abparts_user -d abparts_prod -c "
  SELECT COUNT(*) as total_items FROM stock_adjustment_items;
"
```

---

## Rollback Plan (If Something Goes Wrong)

### Option 1: Rollback Migration

```bash
# Downgrade to previous migration
docker-compose exec api alembic downgrade -1

# Verify
docker-compose exec api alembic current

# Restart services
docker-compose restart api
```

### Option 2: Restore from Backup

```bash
# Stop services
docker-compose down

# Restore database
cat ~/backups/YYYYMMDD/abparts_pre_stock_adjustments_*.sql | \
  docker-compose exec -T db psql -U abparts_user -d abparts_prod

# Restore code
git checkout backup-before-stock-adjustments-YYYYMMDD

# Rebuild and restart
docker-compose build
docker-compose up -d

# Verify
docker-compose exec api alembic current
```

---

## Common Issues and Solutions

### Issue 1: "value too long for type character varying(32)"

**Cause:** Revision ID exceeds 32 characters

**Solution:** Already fixed by changing to `20241130_stock_adj`

### Issue 2: "Multiple head revisions are present"

**Cause:** Branched migration history

**Solution:**
```bash
# Create merge migration
docker-compose exec api alembic merge -m "merge" head1 head2
docker-compose exec api alembic upgrade head
```

### Issue 3: "Revision X not found"

**Cause:** down_revision doesn't match production

**Solution:**
```bash
# Check production revision
docker-compose exec api alembic current

# Update migration file's down_revision to match
# Then re-deploy
```

### Issue 4: Foreign Key Constraint Violation

**Cause:** Existing data references deleted tables

**Solution:**
```bash
# Check for orphaned records
docker-compose exec db psql -U abparts_user -d abparts_prod -c "
  SELECT * FROM stock_adjustments WHERE warehouse_id IS NULL;
"

# Clean up if needed
docker-compose exec db psql -U abparts_user -d abparts_prod -c "
  DELETE FROM stock_adjustments WHERE warehouse_id IS NULL;
"
```

---

## Success Criteria

✅ Migration completes without errors  
✅ `alembic current` shows `20241130_stock_adj (head)`  
✅ Tables `stock_adjustments` and `stock_adjustment_items` exist  
✅ Enum `adjustmenttype` exists  
✅ API responds to `/api/stock-adjustments/` endpoint  
✅ Frontend loads Stock Adjustments page  
✅ Can create new stock adjustment  
✅ Warehouse inventory updates correctly  
✅ No errors in API logs  
✅ No errors in browser console  

---

## Quick Command Reference

```bash
# Check migration status
docker-compose exec api alembic current

# Run migration
docker-compose exec api alembic upgrade head

# Rollback one step
docker-compose exec api alembic downgrade -1

# View migration history
docker-compose exec api alembic history

# Check database tables
docker-compose exec db psql -U abparts_user -d abparts_prod -c "\dt"

# View API logs
docker-compose logs -f api --tail=100

# Restart services
docker-compose restart api web

# Full rebuild
docker-compose down
docker-compose build
docker-compose up -d
```

---

## Timeline Estimate

- Phase 1 (Dev Verification): 15 minutes
- Phase 2 (Backup): 10 minutes
- Phase 3 (Deploy Code): 5 minutes
- Phase 4 (Run Migration): 5 minutes
- Phase 5 (Rebuild Services): 10 minutes
- Phase 6 (Verification): 15 minutes

**Total: ~60 minutes** (with buffer for issues)

---

## Post-Deployment Tasks

1. Monitor application for 24 hours
2. Check error logs daily for first week
3. Verify stock adjustments are being created correctly
4. Train users on new stock adjustment workflow
5. Update user documentation
6. Remove backup files after 30 days (if all is well)

---

**Ready to deploy? Start with Phase 1!**
