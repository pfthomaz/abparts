# Fix Git Conflict on Production

## The Problem

You have local changes to:
- `backend/alembic/versions/20241130_merge_heads.py` (old migration)
- `docker-compose.yml` (dev config)

These conflict with the pull from git.

## Quick Fix

### Option 1: Use Script (Recommended)

```bash
chmod +x resolve_git_conflict.sh
./resolve_git_conflict.sh
```

This will:
- Backup your local changes
- Reset files to remote version
- Pull successfully

### Option 2: Manual Commands

```bash
# Backup files (optional)
cp backend/alembic/versions/20241130_merge_heads.py backend/alembic/versions/20241130_merge_heads.py.backup
cp docker-compose.yml docker-compose.yml.backup

# Reset to remote version
git checkout backend/alembic/versions/20241130_merge_heads.py
git checkout docker-compose.yml

# Pull
git pull
```

## Why It's Safe

1. **20241130_merge_heads.py**: This is the old messy migration that will be replaced by the baseline anyway
2. **docker-compose.yml**: Production uses `docker-compose.prod.yml`, not this file

Both files can be safely reset to the remote version.

## After Resolving

Once git pull succeeds:

```bash
# Deploy the baseline migration
chmod +x deploy_baseline_to_prod.sh
./deploy_baseline_to_prod.sh
```

## If You Want to Keep Local Changes

If you really need to keep your local changes:

```bash
# Stash local changes
git stash

# Pull
git pull

# Try to apply stashed changes
git stash pop

# If conflicts, resolve manually
git status
```

But for production, it's better to just use the remote version.
