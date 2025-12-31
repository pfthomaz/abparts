# Migration Reset Execution Plan

## Overview
We'll reset the migration history using production as the source of truth, but test everything in development first.

## Phase 1: Preparation (Run on Production Server)

### Step 1: Check Current Status
```bash
# On production server
./check_migration_status.sh
```

### Step 2: Create Production Backup
```bash
# On production server - create a full backup first
docker exec abparts_db_prod pg_dump -U abparts_user abparts_prod > production_backup_$(date +%Y%m%d_%H%M%S).sql

# Verify backup size
ls -lh production_backup_*.sql
```

## Phase 2: Generate New Baseline (Run on Production Server)

### Step 3: Run the Schema Reset
```bash
# On production server - this is the main reset command
./reset_database_schema.sh
```

**What this does:**
- ✅ Backs up your production database
- ✅ Backs up existing migration files  
- ✅ Generates new baseline migration from current production schema
- ✅ Updates production's alembic_version table
- ✅ **No data is touched - only migration metadata**

## Phase 3: Test in Development (Run on Development Server)

### Step 4: Copy New Migration Files to Dev
```bash
# On development server - pull the new migration files
git pull origin main

# Or manually copy if not using git yet:
# scp production_server:/path/to/abparts/backend/alembic/versions/*.py backend/alembic/versions/
```

### Step 5: Test Fresh Database Creation
```bash
# On development server - test building database from scratch

# 1. Create a fresh test database
docker exec abparts_db_dev createdb -U abparts_user abparts_test_fresh

# 2. Run migrations on fresh database
docker exec abparts_api_dev alembic -x database_url=postgresql://abparts_user:password@db:5432/abparts_test_fresh upgrade head

# 3. Verify it worked
docker exec abparts_db_dev psql -U abparts_user -d abparts_test_fresh -c "\dt"
```

### Step 6: Test with Production Data Copy
```bash
# On development server - test with production data

# 1. Create test database with production data
docker exec abparts_db_dev createdb -U abparts_user abparts_test_prod_copy

# 2. Copy production backup to dev server and restore
scp production_server:/path/to/production_backup_*.sql ./
docker exec -i abparts_db_dev psql -U abparts_user abparts_test_prod_copy < production_backup_*.sql

# 3. Check alembic status on the copy
docker exec abparts_api_dev alembic -x database_url=postgresql://abparts_user:password@db:5432/abparts_test_prod_copy current

# 4. Test creating new migrations
docker exec abparts_api_dev alembic revision -m "test_migration_after_reset"

# 5. Clean up test migration
rm backend/alembic/versions/*test_migration_after_reset*.py
```

## Phase 4: Verification (Run on Production Server)

### Step 7: Final Production Verification
```bash
# On production server - verify everything is working

# 1. Check current status
docker exec abparts_api_prod alembic current

# 2. Verify no pending migrations
docker exec abparts_api_prod alembic check

# 3. Test creating a new migration (then delete it)
docker exec abparts_api_prod alembic revision -m "test_new_migration"
rm backend/alembic/versions/*test_new_migration*.py
```

## Phase 5: Team Coordination

### Step 8: Update Team
```bash
# Commit the new migration files
git add backend/alembic/versions/
git commit -m "Reset migrations to production baseline $(date +%Y%m%d)"
git push origin main

# Notify team members to:
# 1. Pull the new migration files
# 2. Update their local development databases
```

---

## Quick Reference Commands

### Production Server Commands:
```bash
# Check status
./check_migration_status.sh

# Create backup
docker exec abparts_db_prod pg_dump -U abparts_user abparts_prod > backup.sql

# Run the reset (main command)
./reset_database_schema.sh

# Verify after reset
docker exec abparts_api_prod alembic current
```

### Development Server Commands:
```bash
# Pull new migration files
git pull origin main

# Test fresh database
docker exec abparts_db_dev createdb -U abparts_user test_fresh
docker exec abparts_api_dev alembic upgrade head

# Test with production data
docker exec -i abparts_db_dev psql -U abparts_user test_db < production_backup.sql
```

---

## Container Name Reference

Make sure you're using the correct container names:

**Production:**
- Database: `abparts_db_prod`
- API: `abparts_api_prod`

**Development:**
- Database: `abparts_db_dev` 
- API: `abparts_api_dev`

**Check your actual container names:**
```bash
docker ps --format "table {{.Names}}\t{{.Status}}"
```

---

## Safety Notes

1. **Production data is never at risk** - we only modify migration files and the alembic_version table
2. **Always backup first** - the script does this automatically
3. **Test in dev first** - verify the new migrations work before applying to production
4. **Rollback available** - see DATABASE_SCHEMA_RESET_GUIDE.md for rollback instructions

---

## Troubleshooting

**If containers have different names:**
Edit the scripts and change these variables:
```bash
PROD_CONTAINER="your_actual_db_container_name"
API_CONTAINER="your_actual_api_container_name"
```

**If you get permission errors:**
```bash
chmod +x *.sh
```

**If database connection fails:**
Check your container names and database credentials in the scripts.