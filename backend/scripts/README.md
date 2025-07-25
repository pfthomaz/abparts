# Database Migration Scripts

This directory contains scripts to help manage database migrations safely across different environments.

## Scripts Overview

### `backup_db.sh`
Creates a timestamped backup of the database before migrations.

```bash
# Backup development database
./scripts/backup_db.sh development

# Backup production database
./scripts/backup_db.sh production
```

### `migrate_prod.sh`
Safely applies migrations to production with multiple confirmation steps.

```bash
./scripts/migrate_prod.sh
```

Features:
- Creates automatic backup
- Shows dry-run of migrations
- Requires explicit confirmation
- Performs health check after migration

### `rollback_migration.sh`
Safely rolls back migrations with backup and confirmation.

```bash
# Rollback 1 migration
./scripts/rollback_migration.sh

# Rollback 3 migrations
./scripts/rollback_migration.sh 3
```

### `check_migrations.py`
Comprehensive migration status checker.

```bash
python scripts/check_migrations.py [environment]
```

Shows:
- Database connection status
- Current migration
- Pending migrations
- Recent migration history
- Migration conflicts

## Quick Reference

### Daily Development Workflow

```bash
# 1. Check current status
python scripts/check_migrations.py

# 2. Make model changes
# Edit backend/app/models.py

# 3. Generate migration
docker-compose exec api alembic revision --autogenerate -m "add_user_profile_fields"

# 4. Review and edit the generated migration file

# 5. Apply migration
docker-compose exec api alembic upgrade head

# 6. Test your changes
```

### Production Deployment

```bash
# 1. Check migration status
python scripts/check_migrations.py production

# 2. Run production migration script
./scripts/migrate_prod.sh

# 3. Monitor application logs
docker-compose logs -f api
```

### Emergency Rollback

```bash
# 1. Create backup
./scripts/backup_db.sh production

# 2. Rollback migration
./scripts/rollback_migration.sh 1

# 3. Verify application works
curl http://localhost:8000/health
```

## Environment Variables

For production deployments, set these environment variables:

```bash
export PROD_DB_HOST="your-prod-host"
export PROD_DB_PORT="5432"
export PROD_DB_NAME="abparts_prod"
export PROD_DB_USER="abparts_user"
export PGPASSWORD="your-password"
```

## Best Practices

1. **Always backup before migrations** - especially in production
2. **Test migrations in staging first** - catch issues early
3. **Review generated migrations** - autogenerate isn't perfect
4. **Use descriptive migration names** - make them searchable
5. **Keep migrations small** - easier to debug and rollback
6. **Plan for rollbacks** - ensure down() functions work

## Troubleshooting

### Common Issues

**Multiple migration heads:**
```bash
docker-compose exec api alembic merge heads -m "merge_heads"
docker-compose exec api alembic upgrade head
```

**Migration fails with data conflict:**
```bash
# Fix data issues first, then retry
docker-compose exec api alembic upgrade head
```

**Need to mark migration as applied without running:**
```bash
docker-compose exec api alembic stamp revision_id
```

### Recovery Procedures

If a migration fails in production:

1. **Don't panic** - assess the situation
2. **Check logs** - understand what failed
3. **Check database state** - see what was applied
4. **Restore from backup if needed**
5. **Fix the issue** - in migration or data
6. **Document the incident** - for future reference

## Monitoring

Set up monitoring for:
- Migration execution time
- Database size changes
- Application errors after migrations
- Performance impact

## Security Notes

- Never commit database passwords to git
- Use environment variables for production credentials
- Restrict database access to necessary users only
- Audit migration changes in production
- Keep backups encrypted and secure