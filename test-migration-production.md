# Testing Migration for Production

## Current Status
- Development has: `stocktakes`, `stocktake_items`, `inventory` tables
- Production needs: All stocktake functionality tables

## Migration Path Verification

The `inventory_workflow_001` migration creates:
1. `stocktakes` table ✅ (exists in dev)
2. `stocktake_items` table with `counted_at` and `counted_by_user_id` ✅ (exists in dev)
3. `inventory_alerts` table ❓ (missing in dev)
4. `inventory_adjustments` table ❓ (missing in dev)

## Production Deployment Strategy

Since the core stocktake functionality (tables `stocktakes` and `stocktake_items`) is working in development, and the migration path includes `inventory_workflow_001`, the production deployment should:

1. **Run `alembic upgrade head`** - This will apply all missing migrations including `inventory_workflow_001`
2. **Create all required tables** - Including the missing `inventory_alerts` and `inventory_adjustments`
3. **Include all necessary columns** - The `stocktake_items` table will have `counted_at` and `counted_by_user_id`

## Verification Steps for Production

After deployment, verify:
```bash
# Check all stocktake-related tables exist
docker-compose exec -T db psql -U $POSTGRES_USER -d $POSTGRES_DB -c "
SELECT table_name 
FROM information_schema.tables 
WHERE table_name LIKE '%stocktake%' OR table_name LIKE '%inventory_a%'
ORDER BY table_name;"

# Check stocktake_items has all required columns
docker-compose exec -T db psql -U $POSTGRES_USER -d $POSTGRES_DB -c "
SELECT column_name, data_type, is_nullable 
FROM information_schema.columns 
WHERE table_name = 'stocktake_items' 
ORDER BY ordinal_position;"
```

Expected tables:
- `stocktakes`
- `stocktake_items` 
- `inventory_alerts`
- `inventory_adjustments`

Expected columns in `stocktake_items`:
- `id`, `stocktake_id`, `part_id`
- `expected_quantity`, `actual_quantity`
- `counted_at`, `counted_by_user_id`
- `notes`, `created_at`, `updated_at`