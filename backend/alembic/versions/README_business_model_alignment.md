# Business Model Alignment Database Migration

## Overview

This migration (`31e87319dc9a_business_model_alignment_schema_updates.py`) implements comprehensive database schema changes to align the ABParts application with the actual business model of Oraseas EE's AutoBoss parts distribution system.

## Migration Summary

### 1. New Enum Types Created

- **OrganizationType**: `oraseas_ee`, `bossaqua`, `customer`, `supplier`
- **PartType**: `consumable`, `bulk_material`
- **UserRole**: `user`, `admin`, `super_admin`
- **UserStatus**: `active`, `inactive`, `pending_invitation`, `locked`
- **TransactionType**: `creation`, `transfer`, `consumption`, `adjustment`

### 2. Schema Changes by Table

#### Organizations Table
- **Added**: `organization_type` enum field (replaces generic `type` field)
- **Added**: `parent_organization_id` for supplier relationships
- **Added**: Business rule constraints for singleton organizations (Oraseas EE, BossAqua)
- **Added**: Constraint ensuring suppliers have parent organizations

#### Users Table
- **Updated**: `role` field to use new UserRole enum (`user`, `admin`, `super_admin`)
- **Added**: `user_status` enum field for account status management
- **Added**: Security fields: `failed_login_attempts`, `locked_until`, `last_login`
- **Added**: Invitation system fields: `invitation_token`, `invitation_expires_at`
- **Added**: Password reset fields: `password_reset_token`, `password_reset_expires_at`
- **Added**: Constraint ensuring super_admin users belong to Oraseas EE only

#### Parts Table
- **Added**: `part_type` enum field (`consumable`, `bulk_material`)
- **Added**: `unit_of_measure` field for proper quantity tracking
- **Updated**: Enhanced proprietary parts tracking

#### Warehouses Table (NEW)
- **Purpose**: Enable multiple warehouses per organization
- **Fields**: `id`, `organization_id`, `name`, `location`, `description`, `is_active`
- **Constraints**: Unique warehouse names per organization

#### Inventory Table (RESTRUCTURED)
- **Changed**: Now links to `warehouse_id` instead of `organization_id`
- **Updated**: `current_stock` changed to DECIMAL(10,3) for bulk materials
- **Added**: `unit_of_measure` field
- **Added**: `last_updated` timestamp for real-time tracking

#### Transactions Table (NEW)
- **Purpose**: Comprehensive audit trail for all parts movements
- **Types**: Creation, Transfer, Consumption, Adjustment
- **Fields**: Transaction type, part, warehouses, machine, quantity, user, date, notes
- **Relationships**: Links to parts, warehouses, machines, and users

#### Machines Table
- **Updated**: `customer_organization_id` field for proper ownership tracking
- **Enhanced**: Better relationship with customer organizations

### 3. Business Rule Enforcement

#### Database Constraints
- **Unique Oraseas EE**: Only one organization can have type 'oraseas_ee'
- **Unique BossAqua**: Only one organization can have type 'bossaqua'
- **Super Admin Restriction**: Super admin users can only belong to Oraseas EE
- **Supplier Parent**: Supplier organizations must have a parent organization

#### Automated Functions and Triggers

##### Inventory Update Function
- **Purpose**: Automatically update inventory based on transaction records
- **Trigger**: Executes after each transaction insert
- **Logic**:
  - **Creation**: Increases inventory in destination warehouse
  - **Transfer**: Decreases from source, increases in destination
  - **Consumption**: Decreases inventory in source warehouse
  - **Adjustment**: Adjusts inventory in specified warehouse

##### Inventory Balance Check Function
- **Purpose**: Prevent negative inventory (configurable)
- **Trigger**: Executes before inventory updates
- **Logic**: Raises exception if stock would become negative

### 4. Data Model Alignment with Business Requirements

#### Organization Hierarchy
```
Oraseas EE (App Owner & Distributor)
├── BossAqua (Manufacturer)
├── Customer Organizations
│   └── Supplier Organizations (Customer-specific)
└── Supplier Organizations (Oraseas EE suppliers)
```

#### User Access Control
- **Super Admin**: Full access across all organizations (Oraseas EE only)
- **Admin**: Full management within own organization
- **User**: Basic operations within own organization

#### Parts Flow Tracking
```
Creation → Transfer → Consumption
    ↓        ↓         ↓
Inventory Updates (Automatic via Triggers)
```

### 5. Performance Optimizations

#### Indexes Created
- `ix_organizations_name`: Organization name lookup
- `ix_users_org_role`: User role-based queries
- `ix_machines_customer`: Machine ownership queries
- `ix_inventory_warehouse_part`: Inventory lookups
- `ix_transactions_date`: Transaction date queries
- `ix_transactions_part`: Part transaction history
- `ix_transactions_warehouse`: Warehouse transfer queries

### 6. Migration Safety

#### Rollback Support
- Complete downgrade function provided
- Drops all new tables, constraints, functions, and triggers
- Removes all enum types
- Safe rollback to previous schema state

#### Data Integrity
- Foreign key constraints ensure referential integrity
- Check constraints enforce business rules
- Unique constraints prevent data duplication
- Triggers maintain inventory consistency

### 7. Requirements Mapping

This migration addresses the following requirements from the specification:

- **Req 1.1-1.5**: Organization type management and hierarchy
- **Req 2.1-2.7**: Comprehensive user management system
- **Req 3.1-3.5**: Warehouse management system
- **Req 4.1-4.5**: Enhanced parts classification
- **Req 5.1-5.5**: Machine registration and management
- **Req 6.1-6.4**: Transaction workflow support
- **Req 7.1-7.6**: Part ordering and fulfillment
- **Req 8.1-8.5**: Part usage tracking
- **Req 9.1-9.6**: Inventory tracking and reporting
- **Req 10.1-10.5**: Data access and security model

### 8. Post-Migration Steps

After running this migration:

1. **Update Application Models**: Modify SQLAlchemy models to match new schema
2. **Update API Endpoints**: Adjust endpoints for new data relationships
3. **Data Migration**: Migrate existing data to new structure (if any)
4. **Test Business Rules**: Verify constraints and triggers work correctly
5. **Update Frontend**: Modify UI to support new organization and warehouse concepts

### 9. Testing the Migration

```bash
# Check migration syntax
python validate_migration.py

# Run migration (requires database)
alembic upgrade head

# Rollback if needed
alembic downgrade -1
```

### 10. Monitoring and Maintenance

- Monitor trigger performance on high-volume transaction inserts
- Review inventory balance check trigger if negative inventory is needed
- Consider partitioning transactions table as data grows
- Regular maintenance of indexes for optimal performance

This migration provides a solid foundation for the ABParts business model alignment while maintaining data integrity and system performance.