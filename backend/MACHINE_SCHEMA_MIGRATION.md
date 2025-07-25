# Machine Schema Migration Documentation

## Overview

This document describes the database migration for machine schema changes implemented to fix machine API endpoints. The migration adds missing columns to the machines table and creates the required enum type.

## Migration Details

**Migration File:** `add_machine_columns.py`
**Revision ID:** `add_machine_columns`
**Parent Revision:** `add_security_session`

## Changes Applied

### 1. Enum Type Creation
- Creates `machinestatus` enum type with values: `active`, `inactive`, `maintenance`, `decommissioned`
- Uses `DO` block to handle duplicate object exception if enum already exists

### 2. Machine Table Columns Added
- `purchase_date` - DateTime with timezone, nullable
- `warranty_expiry_date` - DateTime with timezone, nullable  
- `status` - machinestatus enum, not null, default 'active'
- `last_maintenance_date` - DateTime with timezone, nullable
- `next_maintenance_date` - DateTime with timezone, nullable
- `location` - String(255), nullable
- `notes` - Text, nullable

## Development Environment Testing

### Prerequisites
- Docker and Docker Compose installed
- ABParts development environment running

### Testing Migration

1. **Check current migration status:**
   ```bash
   docker-compose exec api alembic current
   ```

2. **View migration history:**
   ```bash
   docker-compose exec api alembic history
   ```

3. **Test migration rollback (optional):**
   ```bash
   # Rollback to previous revision
   docker-compose exec api alembic downgrade add_security_session
   
   # Verify schema changes are reverted
   docker-compose exec db psql -U abparts_user -d abparts_dev -c "\d machines"
   
   # Re-apply migration
   docker-compose exec api alembic upgrade head
   ```

4. **Verify schema consistency:**
   ```bash
   # Check machines table structure
   docker-compose exec db psql -U abparts_user -d abparts_dev -c "\d machines"
   
   # Verify enum type exists
   docker-compose exec db psql -U abparts_user -d abparts_dev -c "SELECT enumlabel FROM pg_enum WHERE enumtypid = (SELECT oid FROM pg_type WHERE typname = 'machinestatus');"
   ```

## Production Migration Procedures

### Pre-Migration Checklist
- [ ] Backup production database
- [ ] Verify migration in staging environment
- [ ] Schedule maintenance window
- [ ] Notify stakeholders of downtime

### Migration Steps

1. **Create database backup:**
   ```bash
   pg_dump -h <host> -U <user> -d <database> > backup_pre_machine_migration.sql
   ```

2. **Apply migration:**
   ```bash
   # In production environment
   docker-compose exec api alembic upgrade head
   ```

3. **Verify migration success:**
   ```bash
   # Check migration status
   docker-compose exec api alembic current
   
   # Verify schema changes
   docker-compose exec db psql -U <prod_user> -d <prod_db> -c "\d machines"
   ```

4. **Test application functionality:**
   - Test machine API endpoints
   - Verify enum value handling
   - Check machine CRUD operations

### Rollback Procedures (Emergency Only)

1. **Rollback migration:**
   ```bash
   docker-compose exec api alembic downgrade add_security_session
   ```

2. **Restore from backup if needed:**
   ```bash
   psql -h <host> -U <user> -d <database> < backup_pre_machine_migration.sql
   ```

## Validation

### Automated Validation Test
A validation test script is provided to verify migration success:

```bash
# Run the migration validation test
docker-compose exec api python test_machine_migration.py
```

The test validates:
- All expected columns exist in the machines table
- machinestatus enum type has correct values
- Enum values are accessible from Python models
- Default values are properly set
- Basic CRUD operations work with enum handling

### Schema Validation
The migration ensures:
- All model fields have corresponding database columns
- Enum values match between Python and database
- Proper constraints and defaults are applied
- Foreign key relationships are maintained

### Application Validation
After migration:
- Machine API endpoints should return 200 status codes
- Enum serialization should work correctly
- CRUD operations should handle all fields properly
- Error handling should be improved

## Troubleshooting

### Common Issues

1. **Enum type already exists:**
   - Migration handles this with `DO` block and exception handling
   - No action required

2. **Column already exists:**
   - Check if migration was partially applied
   - Use `alembic current` to verify state
   - May need manual intervention

3. **Foreign key constraint errors:**
   - Ensure parent tables exist
   - Check organization table has required records

### Error Resolution
- Check Alembic logs for detailed error messages
- Verify database connectivity
- Ensure proper permissions for schema changes
- Contact database administrator if needed

## Related Files
- `backend/app/models.py` - Machine model definition
- `backend/app/routers/machines.py` - Machine API endpoints
- `backend/app/crud/machines.py` - Machine CRUD operations
- `.kiro/specs/machine-api-endpoints-fix/` - Feature specification