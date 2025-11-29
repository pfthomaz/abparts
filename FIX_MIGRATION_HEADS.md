# Fix Multiple Migration Heads

## Problem

Alembic is reporting: "Multiple head revisions are present"

This happens when there are multiple migration branches that haven't been merged.

## Solution

### Option 1: Automated Fix (Recommended)

```bash
./fix_and_continue.sh
```

This will:
1. Merge all migration heads
2. Apply all migrations
3. Migrate images to database
4. Complete deployment

### Option 2: Manual Fix

#### Step 1: Check Current Heads

```bash
docker compose exec api alembic heads
```

You'll see something like:
```
20251129_hybrid_storage (head)
20251124_order_txn (head)
```

#### Step 2: Check Current Database Version

```bash
docker compose exec api alembic current
```

#### Step 3: Create Merge Migration

```bash
docker compose exec api alembic merge heads -m "merge_all_heads"
```

This creates a new migration that merges all heads.

#### Step 4: Apply All Migrations

```bash
docker compose exec api alembic upgrade heads
```

This applies all migrations including the merge.

#### Step 5: Verify

```bash
docker compose exec api alembic current
```

Should show a single head now.

#### Step 6: Continue with Image Migration

```bash
# Copy migration script
docker compose cp migrate_images_to_db.py api:/tmp/migrate_images_to_db.py

# Run migration
docker compose exec api python /tmp/migrate_images_to_db.py
```

#### Step 7: Start All Services

```bash
docker compose up -d
```

#### Step 8: Verify Deployment

```bash
# Check services
docker compose ps

# Check image counts
docker compose exec db psql -U abparts_user -d abparts_dev -c "
SELECT 
  (SELECT COUNT(*) FROM users WHERE profile_photo_data IS NOT NULL) as users_with_photos,
  (SELECT COUNT(*) FROM organizations WHERE logo_data IS NOT NULL) as orgs_with_logos,
  (SELECT COUNT(*) FROM parts WHERE image_data IS NOT NULL) as parts_with_images;
"
```

## Why This Happens

Multiple heads occur when:
1. Multiple developers create migrations independently
2. Migrations are created in different branches
3. Database schema changes happen in parallel

## Prevention

Always check for multiple heads before creating new migrations:
```bash
docker compose exec api alembic heads
```

If multiple heads exist, merge them before creating new migrations.

## Alternative: Stamp Specific Revision

If you know which migration should be current:

```bash
# Check available revisions
docker compose exec api alembic history

# Stamp to specific revision (replace with actual revision ID)
docker compose exec api alembic stamp 20251124_order_txn

# Then upgrade to include new migration
docker compose exec api alembic upgrade head
```

## Troubleshooting

### "Can't locate revision identified by 'XXX'"

The database thinks it's at a revision that doesn't exist in your migration files.

**Fix:**
```bash
# Check what database thinks current version is
docker compose exec db psql -U abparts_user -d abparts_dev -c "
SELECT * FROM alembic_version;
"

# Stamp to a known good revision
docker compose exec api alembic stamp 20251124_order_txn

# Then upgrade
docker compose exec api alembic upgrade heads
```

### "Target database is not up to date"

**Fix:**
```bash
# Force upgrade to heads
docker compose exec api alembic upgrade heads --sql > migration.sql
# Review migration.sql
docker compose exec api alembic upgrade heads
```

## Quick Reference

```bash
# Show all heads
docker compose exec api alembic heads

# Show current version
docker compose exec api alembic current

# Show history
docker compose exec api alembic history

# Merge heads
docker compose exec api alembic merge heads -m "merge"

# Upgrade to all heads
docker compose exec api alembic upgrade heads

# Downgrade one step
docker compose exec api alembic downgrade -1

# Stamp to specific revision
docker compose exec api alembic stamp <revision_id>
```
