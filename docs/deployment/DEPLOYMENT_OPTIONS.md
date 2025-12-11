# Deployment Options for Part Usage Fix

## Two Deployment Approaches

You have **two options** for deploying the `updated_at` columns fix:

### Option 1: Direct SQL (Faster, Simpler)
**Script**: `deploy_part_usage_fix_production.sh`

**Pros:**
- Faster execution
- Simpler (no Alembic dependency)
- Works even if Alembic has issues

**Cons:**
- Doesn't update Alembic migration history
- Manual tracking of what was applied

**Use when:**
- You want quick deployment
- Alembic is not critical for your workflow
- You track changes manually

### Option 2: Alembic Migration (Proper, Tracked)
**Script**: `deploy_with_alembic_production.sh`

**Pros:**
- Proper migration tracking
- Can rollback with `alembic downgrade`
- Follows best practices
- Migration history is recorded

**Cons:**
- Slightly slower
- Requires Alembic to be working properly

**Use when:**
- You want proper migration tracking
- You follow Alembic best practices
- You want easy rollback capability

## Files Created

### Alembic Migration:
- `backend/alembic/versions/01_add_updated_at_columns.py`
  - Revision ID: `01_add_updated_at`
  - Revises: `00_baseline`
  - Adds `updated_at` to 11 tables
  - Creates auto-update triggers

### Deployment Scripts:
1. `deploy_part_usage_fix_production.sh` - Direct SQL approach
2. `deploy_with_alembic_production.sh` - Alembic migration approach

## Recommendation

**Use Option 2 (Alembic)** if:
- Your Alembic setup is working
- You want proper migration tracking
- You follow database migration best practices

**Use Option 1 (Direct SQL)** if:
- You need quick deployment
- Alembic has issues
- You prefer manual control

## How to Deploy

### Option 1: Direct SQL
```bash
chmod +x deploy_part_usage_fix_production.sh
./deploy_part_usage_fix_production.sh
```

### Option 2: Alembic Migration
```bash
chmod +x deploy_with_alembic_production.sh
./deploy_with_alembic_production.sh
```

## What Gets Deployed (Both Options)

1. **Database Changes:**
   - `updated_at` column added to 11 tables
   - Auto-update triggers created
   - Trigger function `update_updated_at_column()` created

2. **Code Changes:**
   - `backend/app/models.py` - Transaction model updated
   - `frontend/src/components/PartUsageHistory.js` - Page reload after edit/delete

3. **Services:**
   - API container rebuilt
   - Frontend container rebuilt
   - All services restarted

## Tables Modified

Both approaches add `updated_at` to:
1. transactions
2. customer_orders
3. customer_order_items
4. supplier_orders
5. supplier_order_items
6. part_usage
7. part_usage_records
8. part_usage_items
9. machine_sales
10. part_order_requests
11. part_order_items

## Rollback

### Option 1 (Direct SQL):
```bash
# Restore from backup
docker compose -f docker-compose.prod.yml exec -T db psql -U abparts_user -d abparts_prod < backup_before_updated_at_*.sql
```

### Option 2 (Alembic):
```bash
# Rollback migration
docker compose -f docker-compose.prod.yml exec api alembic downgrade -1

# Or restore from backup
docker compose -f docker-compose.prod.yml exec -T db psql -U abparts_user -d abparts_prod < backup_before_alembic_updated_at_*.sql
```

## Verification

After deployment (both options):

```bash
# Check database
docker compose -f docker-compose.prod.yml exec db psql -U abparts_user -d abparts_prod -c "\d transactions"

# Check Alembic version (Option 2 only)
docker compose -f docker-compose.prod.yml exec api alembic current

# Test the application
# 1. Open machine details
# 2. Edit a part usage
# 3. Verify page reloads and inventory updates
```

## My Recommendation

Since you have a proper Alembic setup with a baseline migration, I recommend **Option 2 (Alembic)** because:
- It maintains proper migration history
- It's the standard way to manage schema changes
- It allows easy rollback
- It documents what was changed and when

However, if you encounter any issues with Alembic, **Option 1 (Direct SQL)** will work just as well for the actual database changes.
