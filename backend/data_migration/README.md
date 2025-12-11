# ABParts Data Migration and Seeding

This directory contains scripts for migrating existing data to comply with the ABParts Business Model Realignment requirements (Task 18).

## Overview

The migration process ensures that:
1. Default organizations (Oraseas EE and BossAqua) exist with proper configuration
2. All organizations have valid country assignments
3. All required organizations have default warehouses
4. Machine model types are validated and corrected
5. Initial machine hours records are created for tracking

## Scripts

### 1. `simple_migration.py` (Recommended)

A standalone migration script that uses direct SQL commands to avoid import dependencies.

**Usage:**
```bash
# Check migration status
docker-compose exec -T api python data_migration/simple_migration.py --status

# Run full migration
docker-compose exec -T api python data_migration/simple_migration.py --migrate
```

**Features:**
- ✅ Creates default organizations (Oraseas EE, BossAqua)
- ✅ Updates organization countries to 'GR' where missing
- ✅ Creates default warehouses for all organizations that need them
- ✅ Validates and fixes machine model types
- ✅ Creates initial machine hours records
- ✅ Validates migration results

### 2. `migrate_existing_data.py`

Comprehensive migration script using SQLAlchemy models (requires proper imports).

**Usage:**
```bash
python backend/data_migration/migrate_existing_data.py
```

### 3. `seed_default_data.py`

Dedicated script for seeding default organizations and warehouses.

**Usage:**
```bash
python backend/data_migration/seed_default_data.py
```

### 4. `validate_schema_compliance.py`

Comprehensive validation script to check schema compliance.

**Usage:**
```bash
python backend/data_migration/validate_schema_compliance.py
```

### 5. `run_migration.py`

Orchestration script that runs all migration tasks in sequence.

**Usage:**
```bash
# Full migration
python backend/data_migration/run_migration.py

# Individual steps
python backend/data_migration/run_migration.py --migrate-only
python backend/data_migration/run_migration.py --seed-only
python backend/data_migration/run_migration.py --validate-only
python backend/data_migration/run_migration.py --status
```

## Migration Process

The migration follows these steps:

### Step 1: Default Organizations
- Ensures exactly one Oraseas EE organization exists
- Ensures exactly one BossAqua organization exists
- Updates organization details (country, address, contact info) if missing

### Step 2: Country Assignment
- Updates all organizations without countries to use 'GR' as default
- Validates that all countries are within allowed values: ['GR', 'KSA', 'ES', 'CY', 'OM']

### Step 3: Default Warehouses
- Creates default warehouses for organizations that don't have any:
  - Oraseas EE: Gets "Main Warehouse" and "Spare Parts Warehouse"
  - BossAqua: Gets "Main Warehouse" and "Quality Control Warehouse"
  - Customer organizations: Get "{Organization Name} Main Warehouse"

### Step 4: Machine Model Validation
- Validates that all machines have valid model types ('V3_1B' or 'V4_0')
- Updates invalid or missing model types to 'V4_0'

### Step 5: Machine Hours Initialization
- Creates initial machine hours records (0.00 hours) for machines without any records
- Uses the superadmin user as the recorder
- Adds explanatory notes about the migration

### Step 6: Validation
- Verifies all migration requirements are met
- Reports any remaining issues

## Database Schema Requirements

The migration ensures compliance with these schema requirements:

### Organizations
- ✅ Exactly one Oraseas EE organization
- ✅ Exactly one BossAqua organization
- ✅ All organizations have valid countries
- ✅ Suppliers have parent organizations
- ✅ All required organizations have warehouses

### Machines
- ✅ All machines have valid model types (V3_1B or V4_0)
- ✅ All machines have initial hours records

### Users
- ✅ Superadmins belong only to Oraseas EE
- ✅ All users have valid roles and statuses

### Data Integrity
- ✅ No orphaned records
- ✅ All foreign key relationships are valid
- ✅ Business rule constraints are enforced

## Validation Results

After running the migration, you should see:

```
📊 Checking Migration Status
==============================
Oraseas EE organizations: 1
BossAqua organizations: 1
Organizations without warehouses: 0
Machine hours records: [number of machines]

✅ Migration appears to be complete
```

## Troubleshooting

### Import Errors
If you encounter import errors with the model-based scripts, use `simple_migration.py` instead, which uses direct SQL commands.

### Database Connection Issues
Ensure the `DATABASE_URL` environment variable is set correctly:
```bash
docker-compose exec -T api env | grep DATABASE_URL
```

### Permission Issues
Make sure you're running the scripts from within the Docker container:
```bash
docker-compose exec -T api python data_migration/simple_migration.py --status
```

### Enum Value Errors
The machine model types use underscores in the database ('V3_1B', 'V4_0') not dots ('V3.1B', 'V4.0').

## Files Created/Modified

The migration process:
- ✅ Creates default organizations if they don't exist
- ✅ Updates existing organization records with missing data
- ✅ Creates warehouse records for organizations without them
- ✅ Creates machine_hours records for machines without them
- ✅ Does not modify existing valid data

## Rollback

The migration is designed to be safe and additive. It:
- Does not delete existing data
- Does not modify existing valid data
- Only adds missing required data
- Only fixes invalid data to comply with constraints

If you need to rollback:
1. The migration creates new records with UUIDs, so they can be identified
2. Use the notes fields to identify migration-created records
3. Manually remove records created during migration if needed

## Requirements Compliance

This migration addresses the following requirements from the ABParts Business Model Realignment:

- **Requirement 1.2**: Default organization seeding (Oraseas EE, BossAqua)
- **Requirement 1.3**: Default warehouse creation for existing customer organizations
- **Requirement 4.2**: Machine model type validation
- **Requirement 4.3**: Machine hours tracking initialization

## Next Steps

After running the migration:
1. Verify all validation checks pass
2. Test the application functionality
3. Run integration tests to ensure everything works correctly
4. Monitor the application for any issues

## Support

If you encounter issues:
1. Check the migration logs for specific error messages
2. Verify database connectivity and permissions
3. Ensure all required environment variables are set
4. Use the `--status` flag to check current migration state