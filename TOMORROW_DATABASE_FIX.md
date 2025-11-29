# Tomorrow: Fix Database and Stock Adjustments

## Current Situation

1. **Local dev database** - Partially restored from production, missing some columns
2. **Migration system** - Has conflicts (multiple heads) that need resolving
3. **Stock adjustments** - Not appearing in history (original issue)
4. **Production** - Working fine, don't touch it!

## Priority 1: Get Local Dev Working (30 min)

The quickest path is to match your local schema to production:

```bash
# Option A: Run missing migrations (if we can fix the heads)
docker-compose exec api alembic stamp heads  # Mark all as applied
docker-compose exec api alembic current      # Verify

# Option B: Manual schema sync (safer)
# Add missing columns manually to match production
docker-compose exec db psql -U abparts_user -d abparts_dev << 'SQL'
-- Add missing columns
ALTER TABLE customer_orders ADD COLUMN IF NOT EXISTS shipped_by_user_id UUID REFERENCES users(id);
ALTER TABLE transactions ADD COLUMN IF NOT EXISTS customer_order_id UUID REFERENCES customer_orders(id);
ALTER TABLE organizations ADD COLUMN IF NOT EXISTS country VARCHAR(100);
ALTER TABLE parts ADD COLUMN IF NOT EXISTS supplier_part_number VARCHAR(100);
ALTER TABLE users ADD COLUMN IF NOT EXISTS invited_by_user_id UUID REFERENCES users(id);
ALTER TABLE machines ADD COLUMN IF NOT EXISTS purchase_date DATE;
SQL

# Then try logging in
# http://localhost:3000
```

## Priority 2: Investigate Stock Adjustments (1 hour)

Once you can login locally:

1. **Test creating an adjustment**
   - Go to Warehouses
   - Select a warehouse
   - Click "Adjust Stock" on any part
   - Make adjustment (+5 units)
   - Check browser Network tab:
     - POST to `/inventory/warehouse/{id}/adjustment` - status?
     - GET to `/inventory/warehouse/{id}/adjustments` - what returns?

2. **Check database directly**
   ```bash
   # See if adjustment was created
   docker-compose exec db psql -U abparts_user -d abparts_dev -c "SELECT * FROM stock_adjustments ORDER BY created_at DESC LIMIT 5;"
   
   # Check inventory table
   docker-compose exec db psql -U abparts_user -d abparts_dev -c "SELECT id, warehouse_id, part_id FROM inventory LIMIT 5;"
   ```

3. **Check API logs**
   ```bash
   docker-compose logs api | grep -i "stock adjustment"
   ```

## Priority 3: Fix Migration System (2 hours)

This is the root cause of all issues:

1. **Understand the current state**
   ```bash
   docker-compose exec api alembic heads
   docker-compose exec api alembic current
   docker-compose exec api alembic history | head -30
   ```

2. **Clean up migration files**
   - Review `backend/alembic/versions/`
   - Identify duplicate/conflicting migrations
   - Create proper merge migration
   - Test on fresh database

3. **Document the fix** in `DATABASE_MANAGEMENT.md`

## Priority 4: Create Seed Data Script (1 hour)

So we never lose test data again:

```bash
# Create seed_data.sql with:
# - Test organizations
# - Test users
# - Test warehouses
# - Test parts
# - Test inventory

# Then anyone can:
docker-compose down -v
docker-compose up -d
docker-compose exec api alembic upgrade heads
docker-compose exec -T db psql -U abparts_user abparts_dev < seed_data.sql
```

## What NOT to Do

- ❌ Don't run `docker-compose down -v` without backing up first
- ❌ Don't touch production database
- ❌ Don't create new migrations until we fix the existing conflicts
- ❌ Don't try to fix everything at once

## Success Criteria

- [ ] Can login to local dev environment
- [ ] Can create stock adjustment
- [ ] Adjustment appears in history
- [ ] Migration system works cleanly
- [ ] Have seed data for quick resets

## If All Else Fails

Just work on production for testing stock adjustments:
1. Test on production (carefully!)
2. Check production logs
3. Fix the code
4. Deploy fix
5. Deal with local dev environment later

The stock adjustments issue is the business priority - the local dev environment is a developer convenience issue.
