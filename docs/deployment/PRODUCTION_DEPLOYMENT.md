# Production Deployment Guide for Stocktake Database Changes

## Overview
This guide covers deploying the stocktake functionality to production, which adds a new **Stocktake Management** area alongside the existing **Warehouse Inventory Management**. This creates the complete stocktake tables (`stocktakes`, `stocktake_items`, `inventory_alerts`, `inventory_adjustments`) without disrupting existing inventory operations.

### What This Deployment Adds:
- **New Stocktake Management page** (`/stocktake`) for formal inventory counting
- **Complementary functionality** to existing Warehouse Inventory Management (`/inventory`)
- **Enhanced audit capabilities** for inventory accuracy verification
- **No changes** to existing inventory management workflows

## Pre-Deployment Checklist

### 1. Backup Production Database
```bash
# Create a backup before making any changes
pg_dump -h your-prod-db-host -U your-prod-user -d your-prod-db > backup_$(date +%Y%m%d_%H%M%S).sql
```

### 2. Test Migration in Staging
```bash
# Apply migration to staging environment first
docker-compose exec api alembic upgrade head
```

### 3. Verify Current Migration Status
```bash
# Check current migration status in production
docker-compose exec api alembic current
docker-compose exec api alembic history --verbose
```

## Deployment Steps

### Step 1: Deploy Code Changes
1. Pull the latest code with the stocktake functionality
2. Build and deploy the updated containers

### Step 2: Apply Database Migration
```bash
# Apply the new migration
docker-compose exec api alembic upgrade head

# Verify the migration was applied
docker-compose exec api alembic current
```

### Step 3: Verify Database Schema
```bash
# Check that the stocktake tables were created
docker-compose exec db psql -U your-prod-user -d your-prod-db -c "\dt stocktake*"

# Check the stocktake_items table structure
docker-compose exec db psql -U your-prod-user -d your-prod-db -c "\d stocktake_items"
```

Expected output should include these tables:
- `stocktakes` - Main stocktake records
- `stocktake_items` - Individual items being counted
- `inventory_alerts` - Inventory alerts system
- `inventory_adjustments` - Inventory adjustment records

The `stocktake_items` table should include:
```
counted_at         | timestamp with time zone |           |        |
counted_by_user_id | uuid                     |           |        |
expected_quantity  | numeric(10,3)            |           | not null |
actual_quantity    | numeric(10,3)            |           |        |
```

### Step 4: Test Functionality

#### Test Existing Inventory Management (should be unchanged):
1. Access inventory page: `https://your-domain.com/inventory`
2. Verify warehouse inventory view works
3. Test stock adjustments and transfers
4. Confirm all existing functionality works

#### Test New Stocktake Management:
1. Access the new stocktake page: `https://your-domain.com/stocktake`
2. Create a test stocktake for a warehouse
3. View stocktake details and count items
4. Update stocktake items with actual counts
5. Verify discrepancy calculations work correctly
6. Complete the stocktake process
7. Verify no JavaScript errors in browser console

## Rollback Plan (if needed)

### If Migration Fails:
```bash
# Rollback to previous migration
docker-compose exec api alembic downgrade add_parts_perf_idx

# Restore from backup if necessary
psql -h your-prod-db-host -U your-prod-user -d your-prod-db < backup_YYYYMMDD_HHMMSS.sql
```

### If Application Issues:
1. Revert to previous code version
2. Restart containers
3. The database columns are nullable, so they won't break existing functionality

## Post-Deployment Verification

### 1. Check API Endpoints
```bash
# Test stocktake creation
curl -X POST "https://your-domain.com/api/inventory-workflows/stocktakes" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"warehouse_id": "WAREHOUSE_ID", "scheduled_date": "2025-10-22T09:00:00Z", "notes": "Test"}'

# Test stocktake item update
curl -X PUT "https://your-domain.com/api/inventory-workflows/stocktake-items/ITEM_ID" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"actual_quantity": 25.0, "notes": "Counted"}'
```

### 2. Check Frontend Functionality
- Navigate to stocktake page
- Create a new stocktake
- Count items and verify discrepancy calculations
- Complete a stocktake

### 3. Monitor Logs
```bash
# Check for any errors
docker-compose logs api --tail=50
docker-compose logs web --tail=50
```

## Environment Variables (if needed)

Ensure these environment variables are set in production:
```env
DATABASE_URL=postgresql://user:pass@host:5432/dbname
REDIS_URL=redis://redis-host:6379/0
ENVIRONMENT=production
```

## Migration Details

The stocktake functionality is created by the `inventory_workflow_001` migration which is included in the migration path to the current head. This migration creates:

### Tables Created:
- `stocktakes` - Main stocktake records with status tracking
- `stocktake_items` - Individual items being counted (includes `counted_at` and `counted_by_user_id`)
- `inventory_alerts` - Inventory alert system for low stock, etc.
- `inventory_adjustments` - Inventory adjustment records

### Enums Created:
- `stocktakestatus` - planned, in_progress, completed, cancelled
- `inventoryalerttype` - low_stock, stockout, expiring, expired, excess, discrepancy
- `inventoryalertseverity` - low, medium, high, critical

The migration is part of the normal upgrade path, so `alembic upgrade head` will automatically apply it.

## Troubleshooting

### Common Issues:

1. **Migration already applied**: The migration uses conditional logic, so it's safe to run multiple times
2. **Foreign key constraint errors**: Ensure the `users` table exists and has the correct structure
3. **Permission errors**: Ensure the database user has ALTER TABLE permissions

### Verification Queries:
```sql
-- Check if columns exist
SELECT column_name, data_type, is_nullable 
FROM information_schema.columns 
WHERE table_name = 'stocktake_items' 
AND column_name IN ('counted_at', 'counted_by_user_id');

-- Check foreign key constraints
SELECT conname, conrelid::regclass, confrelid::regclass 
FROM pg_constraint 
WHERE contype = 'f' AND conrelid = 'stocktake_items'::regclass;
```