# ABParts Data Migration

This directory contains comprehensive data migration tools for aligning ABParts with the actual business model. The migration system provides data validation, integrity checking, rollback capabilities, and progress tracking.

## Overview

The migration transforms the existing ABParts database to properly represent:
- Organization types and business relationships
- Enhanced user management with proper roles
- Warehouse-based inventory management
- Comprehensive transaction tracking
- Business rule enforcement

## Migration Components

### Core Files

- **`migration_manager.py`** - Main migration orchestrator with step-by-step execution
- **`data_validator.py`** - Comprehensive data validation and integrity checking
- **`migration_tester.py`** - Testing utilities for production data samples
- **`run_migration.py`** - Command-line interface for migration operations

### Directory Structure

```
backend/data_migration/
├── migration_manager.py      # Main migration logic
├── data_validator.py         # Data validation utilities
├── migration_tester.py       # Testing and sample data generation
├── run_migration.py          # CLI interface
├── README.md                 # This documentation
├── backups/                  # Migration backups for rollback
├── reports/                  # Migration and validation reports
└── logs/                     # Migration execution logs
```

## Migration Process

The migration follows a structured 11-step process:

1. **Validate Current Schema** - Check existing data integrity
2. **Backup Existing Data** - Create rollback-capable backups
3. **Migrate Organizations** - Update organization types and relationships
4. **Create Default Warehouses** - Establish warehouse structure
5. **Migrate Users** - Update user roles and security features
6. **Migrate Parts** - Implement part classification system
7. **Migrate Machines** - Update machine-customer relationships
8. **Migrate Inventory** - Convert to warehouse-based inventory
9. **Create Initial Transactions** - Generate transaction audit trail
10. **Validate Migrated Data** - Comprehensive post-migration validation
11. **Cleanup Old Data** - Optimize database and clean temporary data

## Usage

### Prerequisites

1. Ensure the database is running:
   ```bash
   docker-compose up db
   ```

2. Install Python dependencies:
   ```bash
   pip install -r backend/requirements.txt
   ```

### Command Line Interface

Navigate to the migration directory:
```bash
cd backend/data_migration
```

#### 1. Data Validation

Run comprehensive data validation:
```bash
python run_migration.py validate
```

This checks for:
- Missing required fields
- Duplicate records
- Referential integrity issues
- Business rule violations

#### 2. Migration Execution

**Recommended approach (with validation and dry run):**
```bash
python run_migration.py migrate
```

This will:
1. Run pre-migration validation
2. Execute a dry run to test the migration
3. Ask for confirmation
4. Run the actual migration
5. Run post-migration validation

**Quick migration (skip confirmations):**
```bash
python run_migration.py migrate --yes
```

**Dry run only:**
```bash
python run_migration.py migrate --dry-run
```

**Force migration (skip validation and dry run):**
```bash
python run_migration.py migrate --force --yes
```

#### 3. Testing

**Test rollback capability:**
```bash
python run_migration.py test --type rollback
```

**Test with specific data sample:**
```bash
python run_migration.py test --type sample --sample-size medium_sample
```

Available sample sizes:
- `minimal_sample` - 3 orgs, 5 users, 10 parts
- `small_sample` - 10 orgs, 25 users, 50 parts
- `medium_sample` - 25 orgs, 75 users, 100 parts
- `large_sample` - 50 orgs, 150 users, 200 parts
- `production_scale` - 100 orgs, 200 users, 200 parts

**Comprehensive testing:**
```bash
python run_migration.py test --type comprehensive
```

### Python API Usage

#### Direct Migration Manager Usage

```python
from migration_manager import DataMigrationManager

# Create migration manager
manager = DataMigrationManager()

# Run dry run
dry_run_report = manager.run_migration(dry_run=True)

if dry_run_report.status == MigrationStatus.COMPLETED:
    # Run actual migration
    actual_report = manager.run_migration(dry_run=False)
    print(f"Migration status: {actual_report.status.value}")
```

#### Data Validation

```python
from data_validator import run_validation

# Run validation
report = run_validation()

print(f"Validation: {report.summary}")
if not report.is_valid:
    for result in report.results:
        if result.severity.value in ['error', 'critical']:
            print(f"Issue: {result}")
```

#### Testing

```python
from migration_tester import MigrationTester

# Create tester
tester = MigrationTester()

# Test with specific sample
samples = tester.create_test_samples()
small_sample = next(s for s in samples if s.name == 'small_sample')
result = tester.test_migration_with_sample(small_sample)

print(f"Test result: {'PASSED' if result.success else 'FAILED'}")
```

## Migration Features

### Data Validation

The validator performs comprehensive checks:

- **Structure Validation**: Required fields, data types, constraints
- **Business Rules**: Organization types, user roles, relationships
- **Referential Integrity**: Foreign key relationships, orphaned records
- **Data Consistency**: Unit of measure matching, inventory calculations

### Rollback Capability

The migration system provides rollback capabilities:

1. **Automatic Backup**: Creates JSON backup before migration
2. **Failure Recovery**: Automatic rollback attempt on migration failure
3. **Manual Rollback**: Restore from backup files if needed

Backup files are stored in `backups/` directory with format:
`migration_backup_{migration_id}.json`

### Progress Tracking

Migration progress is tracked at multiple levels:

- **Step-level Progress**: Each migration step reports progress
- **Record-level Tracking**: Number of records processed per step
- **Time Tracking**: Duration for each step and overall migration
- **Error Tracking**: Detailed error messages and affected records

### Reporting

Comprehensive reports are generated:

- **Migration Reports**: Complete migration execution details
- **Validation Reports**: Data integrity and business rule compliance
- **Test Reports**: Performance and reliability test results

Reports are saved in `reports/` directory in JSON format.

## Business Model Changes

### Organization Structure

**Before:**
- Generic organizations without business type differentiation
- No hierarchy or parent-child relationships

**After:**
- Typed organizations: `oraseas_ee`, `bossaqua`, `customer`, `supplier`
- Hierarchical relationships with parent organization support
- Business rule enforcement (single Oraseas EE, suppliers need parents)

### User Management

**Before:**
- Basic user roles without business context
- Limited security features

**After:**
- Business-aligned roles: `user`, `admin`, `super_admin`
- Enhanced security: session management, account lockout, invitation system
- Organization-scoped permissions with super_admin cross-organization access

### Inventory Management

**Before:**
- Organization-based inventory tracking
- Limited part classification

**After:**
- Warehouse-based inventory with multiple warehouses per organization
- Enhanced part classification: `consumable` vs `bulk_material`
- Decimal quantity support for bulk materials
- Unit of measure validation and consistency

### Transaction Tracking

**Before:**
- Limited transaction history
- No comprehensive audit trail

**After:**
- Complete transaction audit trail for all parts movements
- Transaction types: `creation`, `transfer`, `consumption`, `adjustment`
- Automatic inventory updates based on transactions
- Machine-specific usage tracking

## Troubleshooting

### Common Issues

1. **Migration Fails at Organization Step**
   - Check for duplicate organization names
   - Ensure organization types are properly set
   - Verify parent-child relationships

2. **User Migration Issues**
   - Check for duplicate usernames/emails
   - Ensure all users have valid organization references
   - Verify role assignments

3. **Inventory Migration Problems**
   - Ensure all parts have proper classifications
   - Check warehouse-organization relationships
   - Verify unit of measure consistency

4. **Validation Errors**
   - Review validation report for specific issues
   - Fix data integrity problems before migration
   - Use `--skip-validation` only if issues are acceptable

### Recovery Procedures

1. **Migration Failure Recovery**
   ```bash
   # Check migration logs
   tail -f logs/migration.log
   
   # Review migration report
   cat reports/migration_report_*.json
   
   # Run validation to identify issues
   python run_migration.py validate
   ```

2. **Manual Rollback**
   ```bash
   # Locate backup file
   ls backups/migration_backup_*.json
   
   # Restore from backup (manual process)
   # Contact system administrator for assistance
   ```

3. **Data Repair**
   ```bash
   # Run validation to identify specific issues
   python run_migration.py validate
   
   # Fix identified issues in database
   # Re-run migration
   python run_migration.py migrate
   ```

## Performance Considerations

### Expected Performance

Based on testing with different data sizes:

- **Small datasets** (< 100 records): < 10 seconds
- **Medium datasets** (< 1000 records): < 30 seconds  
- **Large datasets** (< 10000 records): < 2 minutes
- **Production scale** (ABParts max): < 5 minutes

### Optimization Tips

1. **Run during low-traffic periods**
2. **Ensure adequate database resources**
3. **Monitor disk space for backups**
4. **Use dry run to estimate duration**

## Security Considerations

1. **Backup Security**: Backup files contain sensitive data
2. **Access Control**: Limit migration tool access to administrators
3. **Audit Trail**: All migration activities are logged
4. **Validation**: Comprehensive validation prevents data corruption

## Support

For migration issues or questions:

1. Check the logs in `logs/migration.log`
2. Review validation reports in `reports/`
3. Run diagnostic validation: `python run_migration.py validate`
4. Contact the development team with migration ID and error details

## Version History

- **v1.0** - Initial migration implementation with comprehensive validation and rollback
- **v1.1** - Added testing framework and sample data generation
- **v1.2** - Enhanced CLI interface and progress tracking