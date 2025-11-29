# Database Management Guide

## Problem Statement

The current setup has issues:
- Migration conflicts (multiple heads)
- No automated seed data for development
- Inconsistent state between dev and prod
- Easy to accidentally destroy local data

## Proper Docker Database Workflow

### 1. Always Backup Before Destructive Operations

```bash
# Backup local development database
docker-compose exec db pg_dump -U abparts_user abparts_dev > backup_dev_$(date +%Y%m%d_%H%M%S).sql

# Backup production database (from server)
ssh diogo@46.62.153.166 "sudo docker compose -f /home/abparts/abparts/docker-compose.prod.yml exec -T db pg_dump -U abparts_user abparts_prod" > backup_prod_$(date +%Y%m%d_%H%M%S).sql
```

### 2. Restore Database

```bash
# Restore local from backup
docker-compose exec -T db psql -U abparts_user abparts_dev < backup_dev_YYYYMMDD_HHMMSS.sql

# Restore local from production
docker-compose exec -T db psql -U abparts_user abparts_dev < backup_prod_YYYYMMDD_HHMMSS.sql
```

### 3. Fix Current Migration Issues

The error "type organizationtype already exists" means the init script created the enum, but migrations are trying to create it again.

**Option A: Mark migrations as applied (if schema matches)**
```bash
# Check current migration state
docker-compose exec api alembic current

# Stamp to latest without running migrations
docker-compose exec api alembic stamp heads
```

**Option B: Clean slate with proper migrations**
```bash
# 1. Backup first!
docker-compose exec db pg_dump -U abparts_user abparts_dev > backup_before_fix.sql

# 2. Drop and recreate database
docker-compose exec db psql -U abparts_user -c "DROP DATABASE abparts_dev;"
docker-compose exec db psql -U abparts_user -c "CREATE DATABASE abparts_dev;"

# 3. Run ALL migrations from scratch
docker-compose exec api alembic upgrade heads

# 4. Restore data only (not schema)
docker-compose exec -T db pg_restore -U abparts_user -d abparts_dev --data-only backup_before_fix.sql
```

### 4. Proper Development Workflow

**Starting Fresh:**
```bash
# 1. Clone repository
git clone <repo>
cd abparts

# 2. Copy environment file
cp .env.development .env

# 3. Start services
docker-compose up -d

# 4. Wait for database
sleep 10

# 5. Run migrations
docker-compose exec api alembic upgrade heads

# 6. Load seed data (if available)
docker-compose exec -T db psql -U abparts_user abparts_dev < seed_data.sql
```

**Daily Development:**
```bash
# Start
docker-compose up -d

# Stop (preserves data)
docker-compose down

# Restart specific service
docker-compose restart api
```

**Updating Code:**
```bash
# Pull latest code
git pull

# Rebuild containers if Dockerfile changed
docker-compose build

# Run new migrations
docker-compose exec api alembic upgrade heads

# Restart services
docker-compose up -d
```

## Migration Best Practices

### Creating Migrations

```bash
# 1. Make model changes in backend/app/models.py

# 2. Generate migration
docker-compose exec api alembic revision --autogenerate -m "descriptive_name"

# 3. Review the generated migration file
# Edit backend/alembic/versions/XXXXX_descriptive_name.py if needed

# 4. Test migration
docker-compose exec api alembic upgrade head

# 5. Test downgrade
docker-compose exec api alembic downgrade -1

# 6. Test upgrade again
docker-compose exec api alembic upgrade head

# 7. Commit migration file
git add backend/alembic/versions/XXXXX_descriptive_name.py
git commit -m "Add migration: descriptive_name"
```

### Avoiding Migration Conflicts

1. **Always pull before creating migrations**
2. **Never edit old migrations** - create new ones
3. **Merge heads immediately** if they occur
4. **Test migrations on fresh database** before committing

## Seed Data

Create `seed_data.sql` with essential test data:

```sql
-- Organizations
INSERT INTO organizations (id, name, organization_type, email) VALUES
('...uuid...', 'Oraseas EE', 'oraseas_admin', 'admin@oraseas.com'),
('...uuid...', 'Test Customer', 'customer', 'customer@test.com');

-- Users
INSERT INTO users (id, username, email, name, hashed_password, role, organization_id, is_active) VALUES
('...uuid...', 'admin@oraseas.com', 'admin@oraseas.com', 'Admin', '...hash...', 'super_admin', '...org_id...', true);

-- Warehouses, Parts, etc.
```

## Production Deployment Checklist

1. **Backup production database**
   ```bash
   ssh diogo@46.62.153.166 "sudo docker compose -f /home/abparts/abparts/docker-compose.prod.yml exec -T db pg_dump -U abparts_user abparts_prod" > prod_backup_$(date +%Y%m%d_%H%M%S).sql
   ```

2. **Test migrations locally first**
   ```bash
   # Restore prod backup to local
   docker-compose exec -T db psql -U abparts_user abparts_dev < prod_backup_YYYYMMDD.sql
   
   # Test migration
   docker-compose exec api alembic upgrade head
   ```

3. **Deploy to production**
   ```bash
   ssh diogo@46.62.153.166
   cd /home/abparts/abparts
   git pull
   sudo docker compose -f docker-compose.prod.yml exec api alembic upgrade head
   sudo docker compose -f docker-compose.prod.yml restart api
   ```

## Recovery Procedures

### Lost Local Data

```bash
# Restore from production
ssh diogo@46.62.153.166 "sudo docker compose -f /home/abparts/abparts/docker-compose.prod.yml exec -T db pg_dump -U abparts_user abparts_prod" > restore.sql
docker-compose exec -T db psql -U abparts_user abparts_dev < restore.sql
```

### Corrupted Migrations

```bash
# 1. Backup data
docker-compose exec db pg_dump -U abparts_user abparts_dev > backup.sql

# 2. Reset database
docker-compose down -v
docker-compose up -d db
sleep 10

# 3. Run migrations
docker-compose exec api alembic upgrade heads

# 4. Restore data
docker-compose exec -T db pg_restore -U abparts_user -d abparts_dev --data-only backup.sql
```

## TODO: Improvements Needed

1. **Create seed_data.sql** with test data
2. **Fix migration conflicts** - merge all heads
3. **Add database backup script** to run automatically
4. **Document exact dev/prod differences**
5. **Create database reset script** that preserves data
6. **Add pre-commit hook** to check for migration conflicts
