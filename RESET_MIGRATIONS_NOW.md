# Reset Migrations NOW - Quick Guide

## What You're About To Do

Reset your messy migration history to a clean baseline, starting from your current database schema.

## Quick Start

### In Development (Your Mac)

```bash
# 1. Make script executable
chmod +x reset_migrations_clean_dev.sh

# 2. Run the reset
./reset_migrations_clean_dev.sh

# 3. Verify it worked
docker compose exec db psql -U abparts_user -d abparts_dev -c "SELECT * FROM alembic_version;"
# Should show: 00_baseline

# 4. Test your app still works
docker compose restart api
# Then test login, create parts, etc.

# 5. Commit to git
git add backend/alembic/versions/00_baseline_schema.py
git add backend/alembic/baseline_schema.sql
git commit -m "Reset migrations to clean baseline"
git push
```

### In Production (Server)

```bash
# 1. SSH to server
ssh user@your-server
cd ~/abparts

# 2. Pull the baseline migration from git
git pull

# 3. Deploy with baseline
chmod +x deploy_baseline_to_prod.sh
./deploy_baseline_to_prod.sh

# This will:
# - Rebuild API container (includes new baseline migration)
# - Clear migration history
# - Stamp database at 00_baseline
# - Restart all services

# 4. Verify
docker compose -f docker-compose.prod.yml exec db psql -U abparts_user -d abparts_prod -c "SELECT * FROM alembic_version;"
# Should show: 00_baseline

# 5. Test production site
# Visit https://abparts.oraseas.com
```

## What Gets Created

### In Development

1. **`backend/alembic/baseline_schema.sql`**
   - Complete dump of your current database schema
   - Reference for what the baseline looks like

2. **`backend/alembic/versions/00_baseline_schema.py`**
   - The baseline migration file
   - This gets committed to git

3. **`backend/alembic/versions_old_<timestamp>/`**
   - Backup of all your old messy migrations
   - Kept locally, not committed to git

### In Production

1. **`backend/alembic/versions_old_prod_<timestamp>/`**
   - Backup of old production migrations
   - Kept locally on server

## What Changes in Database

### Before Reset
```
alembic_version table:
  version_num: 20241130_merge (or similar messy merge)
```

### After Reset
```
alembic_version table:
  version_num: 00_baseline
```

The actual database schema **doesn't change** - only the migration tracking.

## Future Migrations

From now on, create migrations like this:

```bash
# 1. In development - edit models
nano backend/app/models.py

# 2. Generate migration
docker compose exec api alembic revision --autogenerate -m "add new field"

# 3. Review and test
docker compose exec api alembic upgrade head

# 4. Commit and push
git add backend/app/models.py backend/alembic/versions/<new_migration>.py
git commit -m "Add new field"
git push

# 5. In production - apply migration
git pull
docker compose exec api alembic upgrade head
docker compose restart api
```

## Verification

### Check Migration Status

```bash
# Development
docker compose exec api alembic current

# Production (on server)
docker compose exec api alembic current
```

Both should show: `00_baseline`

### Check Database

```bash
# Development
docker compose exec db psql -U abparts_user -d abparts_dev -c "\dt"

# Production (on server)
docker compose exec db psql -U abparts_user -d abparts_prod -c "\dt"
```

Both should show the same tables.

## Troubleshooting

### Script says "Failed to dump schema"

**Fix**: Make sure database is running
```bash
docker compose ps db
docker compose up -d db
```

### Script says "Baseline migration not found" (Production)

**Fix**: You need to commit and push from development first
```bash
# In development
git add backend/alembic/versions/00_baseline_schema.py
git commit -m "Add baseline"
git push

# In production
git pull
./reset_migrations_clean_prod.sh
```

### Application breaks after reset

**Fix**: The schema shouldn't change, but restart services
```bash
docker compose restart
```

## Safety Notes

- ✅ Your database schema is **not modified**
- ✅ Old migrations are **backed up** before deletion
- ✅ You can **rollback** by restoring from backup
- ✅ This only affects migration tracking, not data

## Need More Details?

See `MIGRATION_RESET_WORKFLOW.md` for complete documentation.

## Ready?

```bash
./reset_migrations_clean_dev.sh
```

Let's do this!
