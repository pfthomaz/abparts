# Maintenance Protocols Migration Guide

## Overview

This guide walks you through running the database migration to add the Maintenance Protocols feature to ABParts.

## What This Migration Does

The migration creates 5 new tables:
1. **maintenance_protocols** - Protocol definitions (daily, weekly, scheduled)
2. **protocol_checklist_items** - Checklist items for each protocol
3. **maintenance_executions** - Records of completed maintenance
4. **maintenance_checklist_completions** - Individual item completions
5. **maintenance_reminders** - Upcoming maintenance reminders

It also adds:
- `machine_model` field to the `machines` table
- `execution_id` field to the `machine_maintenance` table
- Proper indexes for performance
- Foreign key relationships

## Prerequisites

- Docker containers must be running
- Database must be accessible
- You must have the latest code pulled

## Step 1: Verify Containers Are Running

```bash
docker compose ps
```

You should see containers for `api`, `db`, `redis`, and `web` in "Up" status.

If not running, start them:
```bash
docker compose up -d
```

## Step 2: Check Current Migration Status

```bash
docker compose exec api alembic current
```

This should show: `01_add_updated_at (head)`

## Step 3: Validate the Migration File

Optional but recommended:
```bash
python3 validate_migration.py
```

This checks that the migration file is properly formatted.

## Step 4: Run the Migration

```bash
docker compose exec api alembic upgrade head
```

You should see output like:
```
INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
INFO  [alembic.runtime.migration] Will assume transactional DDL.
INFO  [alembic.runtime.migration] Running upgrade 01_add_updated_at -> add_maintenance_protocols, add maintenance protocols and service management
```

## Step 5: Verify Tables Were Created

```bash
docker compose exec db psql -U abparts_user -d abparts_dev -c "\dt maintenance*"
```

You should see:
```
                          List of relations
 Schema |               Name                | Type  |     Owner     
--------+-----------------------------------+-------+---------------
 public | maintenance_checklist_completions | table | abparts_user
 public | maintenance_executions            | table | abparts_user
 public | maintenance_protocols             | table | abparts_user
 public | maintenance_reminders             | table | abparts_user
 public | protocol_checklist_items          | table | abparts_user
```

## Step 6: Verify Machine Model Field

```bash
docker compose exec db psql -U abparts_user -d abparts_dev -c "\d machines"
```

Look for the `machine_model` column in the output.

## Step 7: Test the API

1. Restart the API container to load new models:
```bash
docker compose restart api
```

2. Visit the API docs:
```
http://localhost:8000/docs
```

3. Look for the new `/maintenance-protocols` endpoints

## Troubleshooting

### Migration Already Applied

If you see:
```
INFO  [alembic.runtime.migration] Running upgrade  -> add_maintenance_protocols
ERROR [alembic.util.messaging] Target database is not up to date.
```

Check current version:
```bash
docker compose exec api alembic current
```

### Tables Already Exist

If tables already exist, you can:

1. **Drop and recreate** (DEVELOPMENT ONLY):
```bash
docker compose exec db psql -U abparts_user -d abparts_dev -c "
DROP TABLE IF EXISTS maintenance_checklist_completions CASCADE;
DROP TABLE IF EXISTS maintenance_executions CASCADE;
DROP TABLE IF EXISTS maintenance_reminders CASCADE;
DROP TABLE IF EXISTS protocol_checklist_items CASCADE;
DROP TABLE IF EXISTS maintenance_protocols CASCADE;
"
```

Then run the migration again.

2. **Mark as applied** (if tables are correct):
```bash
docker compose exec api alembic stamp add_maintenance_protocols
```

### Connection Errors

If you can't connect to the database:

1. Check containers are running:
```bash
docker compose ps
```

2. Check database logs:
```bash
docker compose logs db
```

3. Restart containers:
```bash
docker compose restart
```

### Import Errors

If you see Python import errors:

1. Check the models are properly defined:
```bash
docker compose exec api python -c "from app import models; print('Models loaded successfully')"
```

2. Restart the API container:
```bash
docker compose restart api
```

## Rollback (If Needed)

To rollback the migration:

```bash
docker compose exec api alembic downgrade -1
```

This will:
- Drop all 5 maintenance tables
- Remove the `machine_model` field from machines
- Remove the `execution_id` field from machine_maintenance

## Production Deployment

### Before Running in Production:

1. **Backup the database:**
```bash
docker compose exec db pg_dump -U abparts_user abparts_prod > backup_$(date +%Y%m%d_%H%M%S).sql
```

2. **Test in staging first**

3. **Schedule maintenance window** (migration should be fast, but plan for 5-10 minutes)

4. **Notify users** of brief downtime

### Production Migration Steps:

1. Put application in maintenance mode
2. Backup database
3. Run migration:
```bash
docker compose exec api alembic upgrade head
```
4. Verify tables created
5. Restart API container
6. Test critical endpoints
7. Remove maintenance mode

### Verification Queries:

```sql
-- Check table counts
SELECT 'maintenance_protocols' as table_name, COUNT(*) FROM maintenance_protocols
UNION ALL
SELECT 'protocol_checklist_items', COUNT(*) FROM protocol_checklist_items
UNION ALL
SELECT 'maintenance_executions', COUNT(*) FROM maintenance_executions
UNION ALL
SELECT 'maintenance_checklist_completions', COUNT(*) FROM maintenance_checklist_completions
UNION ALL
SELECT 'maintenance_reminders', COUNT(*) FROM maintenance_reminders;

-- Check indexes
SELECT tablename, indexname 
FROM pg_indexes 
WHERE tablename LIKE 'maintenance%' 
ORDER BY tablename, indexname;

-- Check foreign keys
SELECT
    tc.table_name, 
    kcu.column_name, 
    ccu.table_name AS foreign_table_name,
    ccu.column_name AS foreign_column_name 
FROM information_schema.table_constraints AS tc 
JOIN information_schema.key_column_usage AS kcu
  ON tc.constraint_name = kcu.constraint_name
JOIN information_schema.constraint_column_usage AS ccu
  ON ccu.constraint_name = tc.constraint_name
WHERE tc.constraint_type = 'FOREIGN KEY' 
  AND tc.table_name LIKE 'maintenance%';
```

## Next Steps After Migration

1. **Create sample protocols** (via API or super admin UI)
2. **Test protocol execution** with a test machine
3. **Configure reminders** for scheduled maintenance
4. **Train users** on the new maintenance features

## Support

If you encounter issues:
1. Check the logs: `docker compose logs api`
2. Review the migration file: `backend/alembic/versions/add_maintenance_protocols.py`
3. Check the models: `backend/app/models.py`
4. Verify schemas: `backend/app/schemas.py`

## Quick Reference

```bash
# Check migration status
docker compose exec api alembic current

# Run migration
docker compose exec api alembic upgrade head

# Rollback migration
docker compose exec api alembic downgrade -1

# View migration history
docker compose exec api alembic history

# Verify tables
docker compose exec db psql -U abparts_user -d abparts_dev -c "\dt maintenance*"

# Restart API
docker compose restart api

# View API docs
open http://localhost:8000/docs
```
