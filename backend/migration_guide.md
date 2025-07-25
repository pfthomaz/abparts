# Database Migration Guide

This guide explains how to handle database migrations for ABParts across different environments.

## Migration Workflow

### 1. Development Environment

When making model changes in development:

```bash
# 1. Make your model changes in backend/app/models.py

# 2. Generate a new migration
docker-compose exec api alembic revision --autogenerate -m "description_of_changes"

# 3. Review the generated migration file in backend/alembic/versions/
# Make sure it captures all your changes correctly

# 4. Apply the migration
docker-compose exec api alembic upgrade head

# 5. Test your changes
# Run your API tests to ensure everything works

# 6. Commit the migration file along with your model changes
git add backend/alembic/versions/your_new_migration.py backend/app/models.py
git commit -m "Add migration for model changes"
```

### 2. Test Environment

For test databases (CI/CD or staging):

```bash
# Apply all pending migrations
docker-compose exec api alembic upgrade head

# Or if using a different environment
ENVIRONMENT=testing docker-compose exec api alembic upgrade head
```

### 3. Production Environment

For production deployments:

```bash
# 1. ALWAYS backup your production database first
pg_dump -h your-prod-host -U your-user -d your-db > backup_$(date +%Y%m%d_%H%M%S).sql

# 2. Check current migration status
docker-compose exec api alembic current

# 3. Check what migrations will be applied
docker-compose exec api alembic show head

# 4. Apply migrations (preferably during maintenance window)
docker-compose exec api alembic upgrade head

# 5. Verify the migration was successful
docker-compose exec api alembic current
```

## Migration Commands Reference

### Basic Commands

```bash
# Check current migration status
docker-compose exec api alembic current

# Show migration history
docker-compose exec api alembic history

# Show pending migrations
docker-compose exec api alembic show head

# Generate new migration
docker-compose exec api alembic revision --autogenerate -m "description"

# Apply all pending migrations
docker-compose exec api alembic upgrade head

# Apply specific migration
docker-compose exec api alembic upgrade revision_id

# Rollback to previous migration
docker-compose exec api alembic downgrade -1

# Rollback to specific migration
docker-compose exec api alembic downgrade revision_id
```

### Advanced Commands

```bash
# Create empty migration file (for manual changes)
docker-compose exec api alembic revision -m "manual_changes"

# Merge multiple migration heads
docker-compose exec api alembic merge heads -m "merge_heads"

# Show SQL that would be executed (dry run)
docker-compose exec api alembic upgrade head --sql

# Mark migration as applied without running it
docker-compose exec api alembic stamp revision_id
```

## Best Practices

### 1. Migration Safety

- **Always backup production databases** before applying migrations
- **Test migrations thoroughly** in development and staging first
- **Review generated migrations** - autogenerate isn't perfect
- **Use transactions** - most migrations are automatically wrapped in transactions
- **Plan for rollbacks** - ensure your down() functions work

### 2. Migration Content

- **One logical change per migration** - don't mix unrelated changes
- **Use descriptive names** - make it clear what the migration does
- **Add comments** for complex migrations
- **Handle data migrations carefully** - consider performance impact

### 3. Production Deployment

- **Schedule maintenance windows** for large migrations
- **Monitor migration progress** for long-running changes
- **Have rollback plan ready** in case of issues
- **Test with production-like data volumes**

## Handling Migration Conflicts

If you encounter migration conflicts (multiple heads):

```bash
# 1. Check all heads
docker-compose exec api alembic heads

# 2. Merge the heads
docker-compose exec api alembic merge heads -m "merge_migration_heads"

# 3. Apply the merge migration
docker-compose exec api alembic upgrade head
```

## Environment-Specific Considerations

### Development
- Migrations can be more experimental
- OK to drop and recreate tables if needed
- Use `alembic downgrade` freely for testing

### Staging/Test
- Should mirror production migration process
- Use for testing migration performance
- Validate that migrations work with realistic data

### Production
- **NEVER** drop tables or columns without careful planning
- Consider backwards compatibility
- Plan for zero-downtime deployments when possible
- Monitor database performance during migrations

## Troubleshooting

### Common Issues

1. **Migration fails due to data conflicts**
   - Fix data issues first, then retry migration
   - Consider data migration scripts

2. **Multiple migration heads**
   - Use `alembic merge heads` to resolve

3. **Migration partially applied**
   - Check database state manually
   - Use `alembic stamp` if needed to mark as applied

4. **Need to rollback migration**
   - Use `alembic downgrade` with caution
   - Ensure rollback doesn't lose data

### Recovery Steps

If a migration fails in production:

1. **Don't panic** - most issues are recoverable
2. **Check the error message** - often points to the exact issue
3. **Check database state** - see what was actually applied
4. **Fix the issue** - either in migration or data
5. **Resume or rollback** - depending on the situation
6. **Document the incident** - for future reference

## Migration Scripts

See the `scripts/` directory for helpful migration utilities:
- `backup_db.sh` - Database backup script
- `migrate_prod.sh` - Production migration script with safety checks
- `rollback_migration.sh` - Safe rollback script