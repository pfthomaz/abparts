# Migration Reset Workflow - Dev to Production

## Overview

This workflow resets your migration history to a clean baseline, starting from your current database schema. You'll do this in development first, then deploy to production.

## Prerequisites

- Development database is up-to-date with all schema changes
- Production database has the same schema as development
- You have git access to commit and push changes

## Step-by-Step Process

### Part 1: Development (Your Local Machine)

#### 1. Make Scripts Executable

```bash
chmod +x reset_migrations_clean_dev.sh reset_migrations_clean_prod.sh
```

#### 2. Run Development Reset

```bash
./reset_migrations_clean_dev.sh
```

This will:
- Dump your current dev database schema to `backend/alembic/baseline_schema.sql`
- Backup old migrations to `backend/alembic/versions_old_<timestamp>/`
- Clear migration history in dev database
- Create `backend/alembic/versions/00_baseline_schema.py`
- Stamp dev database at `00_baseline`

#### 3. Verify Development

```bash
# Check migration status
docker compose exec db psql -U abparts_user -d abparts_dev -c "SELECT * FROM alembic_version;"

# Should show: 00_baseline
```

#### 4. Test Development Still Works

```bash
# Restart API
docker compose restart api

# Test application
# Login, create parts, etc.
```

#### 5. Commit to Git

```bash
# Add the baseline migration
git add backend/alembic/versions/00_baseline_schema.py
git add backend/alembic/baseline_schema.sql

# Optionally add the backup directory to .gitignore
echo "backend/alembic/versions_old*" >> .gitignore
git add .gitignore

# Commit
git commit -m "Reset migrations to clean baseline

- Created baseline migration from current schema
- All future migrations will be incremental from this point
- Old migrations backed up locally"

# Push to repository
git push
```

### Part 2: Production (Server)

#### 1. SSH to Production Server

```bash
ssh user@your-production-server
cd ~/abparts
```

#### 2. Pull Latest Code

```bash
git pull
```

This brings in:
- `backend/alembic/versions/00_baseline_schema.py`
- `backend/alembic/baseline_schema.sql`
- `reset_migrations_clean_prod.sh`

#### 3. Make Script Executable

```bash
chmod +x reset_migrations_clean_prod.sh
```

#### 4. Run Production Reset

```bash
./reset_migrations_clean_prod.sh
```

This will:
- Verify baseline migration exists
- Backup any old migrations
- Clear production migration history
- Stamp production database at `00_baseline`

#### 5. Verify Production

```bash
# Check migration status
docker compose exec db psql -U abparts_user -d abparts_prod -c "SELECT * FROM alembic_version;"

# Should show: 00_baseline
```

#### 6. Restart Production Services

```bash
docker compose restart api
```

#### 7. Test Production

Visit your production site and verify everything works.

## Future Migration Workflow

Now that you have a clean baseline, here's how to handle future schema changes:

### 1. Make Changes in Development

```bash
# Edit models
nano backend/app/models.py

# Example: Add a new field
# class Part(Base):
#     ...
#     new_field = Column(String(100))
```

### 2. Create Migration in Development

```bash
# Generate migration
docker compose exec api alembic revision --autogenerate -m "add new_field to parts"

# This creates: backend/alembic/versions/<timestamp>_add_new_field_to_parts.py
```

### 3. Review Migration

```bash
# Open and review the generated migration
nano backend/alembic/versions/<timestamp>_add_new_field_to_parts.py

# Make sure it looks correct
```

### 4. Apply in Development

```bash
# Apply migration
docker compose exec api alembic upgrade head

# Restart API
docker compose restart api

# Test the changes
```

### 5. Commit and Push

```bash
git add backend/app/models.py
git add backend/alembic/versions/<timestamp>_add_new_field_to_parts.py
git commit -m "Add new_field to parts table"
git push
```

### 6. Deploy to Production

```bash
# SSH to production
ssh user@your-production-server
cd ~/abparts

# Pull changes
git pull

# Apply migration
docker compose exec api alembic upgrade head

# Restart API
docker compose restart api

# Verify
docker compose exec db psql -U abparts_user -d abparts_prod -c "SELECT * FROM alembic_version;"
```

## Verification Commands

### Check Current Migration Version

```bash
# Development
docker compose exec db psql -U abparts_user -d abparts_dev -c "SELECT * FROM alembic_version;"

# Production
docker compose exec db psql -U abparts_user -d abparts_prod -c "SELECT * FROM alembic_version;"
```

### List All Migrations

```bash
docker compose exec api alembic history
```

### Check Migration Status

```bash
docker compose exec api alembic current
```

### Show Pending Migrations

```bash
docker compose exec api alembic heads
```

## Troubleshooting

### Issue: "Baseline migration not found" in Production

**Solution**: You forgot to commit and push from development.

```bash
# In development
git add backend/alembic/versions/00_baseline_schema.py
git commit -m "Add baseline migration"
git push

# In production
git pull
./reset_migrations_clean_prod.sh
```

### Issue: Migration fails with "column already exists"

**Solution**: The migration is trying to create something that already exists.

```bash
# Option 1: Fake the migration (if schema is already correct)
docker compose exec api alembic stamp head

# Option 2: Edit the migration to check if column exists first
nano backend/alembic/versions/<migration_file>.py
```

### Issue: Development and production schemas are different

**Solution**: Manually sync the schemas first.

```bash
# Dump production schema
docker compose exec -T db pg_dump -U abparts_user -d abparts_prod --schema-only > prod_schema.sql

# Compare with development
docker compose exec -T db pg_dump -U abparts_user -d abparts_dev --schema-only > dev_schema.sql
diff dev_schema.sql prod_schema.sql

# Fix differences manually, then run reset scripts
```

## Benefits of This Approach

1. **Clean History**: No more merge conflicts in migrations
2. **Single Source of Truth**: Baseline represents actual database state
3. **Easy to Understand**: All future migrations are incremental
4. **Git-Friendly**: Baseline migration is committed to repository
5. **Reproducible**: Can recreate database from baseline + migrations

## Summary

- ✅ Run `reset_migrations_clean_dev.sh` in development
- ✅ Commit and push baseline migration
- ✅ Run `reset_migrations_clean_prod.sh` in production
- ✅ Future migrations are created in dev, tested, then deployed to prod
- ✅ Clean, linear migration history going forward
