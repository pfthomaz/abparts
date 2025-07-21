# ABParts Database Schema Documentation

**Version:** 2.0.0  
**Last Updated:** January 2025  
**Database:** PostgreSQL 15  
**ORM:** SQLAlchemy with Alembic migrations  

---

## 📋 **Schema Overview**

The ABParts database schema has been fully aligned with the AutoBoss parts distribution business model. The schema supports a hierarchical organization structure, warehouse-based inventory management, comprehensive transaction tracking, and role-based access control.

### **Business Model Integration**
The database properly represents the AutoBoss parts ecosystem:
- **Oraseas EE**: Primary distributor and app owner (singleton)
- **BossAqua**: Manufacturer of AutoBoss machines and proprietary parts (singleton)
- **Customers**: Organizations that purchase AutoBoss machines (max 100)
- **Suppliers**: Third-party suppliers with parent organization relationships

### **Scale Requirements**
The schema is optimized for:
- Maximum 100 customer organizations
- Maximum 200 total users across all organizations
- Maximum 200 different parts in catalog
- Maximum 150 AutoBoss machines deployed
- Maximum 150 warehouses across all organizations
- Maximum 7,500 transactions per year

---

## 🏗️ **Core Tables**

### **organizations**
Primary table for managing the organization hierarchy and business relationships.

```sql
CREATE TABLE organizations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) UNIQUE NOT NULL,
    organization_type organization_type_enum NOT NULL,
    parent_organization_id UUID REFERENCES organizations(id),
    address TEXT,
    contact_info TEXT,
    is_active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
);

-- Enums
CREATE TYPE organization_type_enum AS ENUM (
    'oraseas_ee',
    'bossaqua', 
    'customer',
    'supplier'
);

-- Indexes
CREATE INDEX idx_organizations_type ON organizations(organization_type);
CREATE INDEX idx_organizations_parent ON organizations(parent_organization_id);
CREATE INDEX idx_organizations_name ON organizations(name);
CREATE INDEX idx_organizations_active ON organizations(is_active);
```

**Business Rules:**
- Only one organization with type 'oraseas_ee' allowed (enforced by application)
- Only one organization with type 'bossaqua' allowed (enforced by application)
- Suppliers must have a parent_organization_id (enforced by CHECK constraint)
- Organization names must be unique across the system
- Maximum 100 customer organizations (enforced by application)

### **users**
Enhanced user management with comprehensive authentication and security features.

```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL REFERENCES organizations(id),
    username VARCHAR(255) UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255),
    role user_role_enum NOT NULL,
    user_status user_status_enum NOT NULL DEFAULT 'active',
    failed_login_attempts INTEGER NOT NULL DEFAULT 0,
    locked_until TIMESTAMP WITH TIME ZONE,
    last_login TIMESTAMP WITH TIME ZONE,
    invitation_token VARCHAR(255),
    invitation_expires_at TIMESTAMP WITH TIME ZONE,
    invited_by_user_id UUID REFERENCES users(id),
    password_reset_token VARCHAR(255),
    password_reset_expires_at TIMESTAMP WITH TIME ZONE,
    email_verification_token VARCHAR(255),
    email_verification_expires_at TIMESTAMP WITH TIME ZONE,
    pending_email VARCHAR(255),
    is_active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
);

-- Enums
CREATE TYPE user_role_enum AS ENUM ('user', 'admin', 'super_admin');
CREATE TYPE user_status_enum AS ENUM ('active', 'inactive', 'pending_invitation', 'locked');

-- Indexes
CREATE INDEX idx_users_org_role ON users(organization_id, role);
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_status ON users(user_status);
CREATE INDEX idx_users_invitation_token ON users(invitation_token);
```

**Business Rules:**
- Super admins must belong to Oraseas EE organization (enforced by application)
- Each organization must have at least one admin user (enforced by application)
- Maximum 200 total users across all organizations (enforced by application)
- Username and email must be unique across the system
- Account lockout after 5 failed login attempts for 15 minutes

### **warehouses**
Multi-warehouse support for organization-specific inventory management.

```sql
CREATE TABLE warehouses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL REFERENCES organizations(id),
    name VARCHAR(255) NOT NULL,
    location VARCHAR(500),
    description TEXT,
    is_active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
    
    CONSTRAINT _org_warehouse_name_uc UNIQUE (organization_id, name)
);

-- Indexes
CREATE INDEX idx_warehouses_org ON warehouses(organization_id);
CREATE INDEX idx_warehouses_active ON warehouses(is_active);
```

**Business Rules:**
- Warehouse names must be unique within an organization
- Maximum 150 warehouses across all organizations (enforced by application)
- Only active warehouses can receive inventory
- Suppliers typically have only one warehouse

### **parts**
Enhanced parts catalog with proper classification and business attributes.

```sql
CREATE TABLE parts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    part_number VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    part_type part_type_enum NOT NULL DEFAULT 'consumable',
    is_proprietary BOOLEAN NOT NULL DEFAULT false,
    unit_of_measure VARCHAR(50) NOT NULL DEFAULT 'pieces',
    manufacturer_part_number VARCHAR(255),
    manufacturer_delivery_time_days INTEGER,
    local_supplier_delivery_time_days INTEGER,
    image_urls TEXT[],
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
);

-- Enums
CREATE TYPE part_type_enum AS ENUM ('consumable', 'bulk_material');

-- Indexes
CREATE INDEX idx_parts_number ON parts(part_number);
CREATE INDEX idx_parts_type ON parts(part_type);
CREATE INDEX idx_parts_proprietary ON parts(is_proprietary);
CREATE INDEX idx_parts_name ON parts(name);
```

**Business Rules:**
- Part numbers must be unique across the system
- Maximum 200 different parts in catalog (enforced by application)
- Proprietary parts (is_proprietary = true) are manufactured by BossAqua
- Consumable parts tracked in whole units, bulk_material supports decimals

### **inventory**
Warehouse-specific inventory tracking with real-time stock calculations.

```sql
CREATE TABLE inventory (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    warehouse_id UUID NOT NULL REFERENCES warehouses(id),
    part_id UUID NOT NULL REFERENCES parts(id),
    current_stock DECIMAL(10,3) NOT NULL DEFAULT 0,
    minimum_stock_recommendation DECIMAL(10,3) NOT NULL DEFAULT 0,
    unit_of_measure VARCHAR(50) NOT NULL,
    reorder_threshold_set_by VARCHAR(50),
    last_recommendation_update TIMESTAMP WITH TIME ZONE,
    last_updated TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
    
    CONSTRAINT _warehouse_part_uc UNIQUE (warehouse_id, part_id)
);

-- Indexes
CREATE INDEX idx_inventory_warehouse_part ON inventory(warehouse_id, part_id);
CREATE INDEX idx_inventory_stock ON inventory(current_stock);
CREATE INDEX idx_inventory_low_stock ON inventory(current_stock, minimum_stock_recommendation);
```

**Business Rules:**
- One inventory record per warehouse-part combination
- Stock levels calculated from transaction history
- Negative inventory allowed with warnings (configurable)
- Decimal quantities supported for bulk materials

### **machines**
AutoBoss machine registration and ownership tracking.

```sql
CREATE TABLE machines (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    customer_organization_id UUID NOT NULL REFERENCES organizations(id),
    model_type VARCHAR(100) NOT NULL,
    name VARCHAR(255) NOT NULL,
    serial_number VARCHAR(255) UNIQUE NOT NULL,
    purchase_date TIMESTAMP WITH TIME ZONE,
    warranty_expiry_date TIMESTAMP WITH TIME ZONE,
    status machine_status_enum NOT NULL DEFAULT 'active',
    last_maintenance_date TIMESTAMP WITH TIME ZONE,
    next_maintenance_date TIMESTAMP WITH TIME ZONE,
    location VARCHAR(255),
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
);

-- Enums
CREATE TYPE machine_status_enum AS ENUM ('active', 'inactive', 'maintenance', 'decommissioned');

-- Indexes
CREATE INDEX idx_machines_customer ON machines(customer_organization_id);
CREATE INDEX idx_machines_serial ON machines(serial_number);
CREATE INDEX idx_machines_status ON machines(status);
```

**Business Rules:**
- Serial numbers must be unique across all machines
- Maximum 150 AutoBoss machines deployed (enforced by application)
- Only super_admin can register new machines
- Machines can only be owned by customer organizations

### **transactions**
Comprehensive audit trail for all parts movements and inventory changes.

```sql
CREATE TABLE transactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    transaction_type transaction_type_enum NOT NULL,
    part_id UUID NOT NULL REFERENCES parts(id),
    from_warehouse_id UUID REFERENCES warehouses(id),
    to_warehouse_id UUID REFERENCES warehouses(id),
    machine_id UUID REFERENCES machines(id),
    quantity DECIMAL(10,3) NOT NULL,
    unit_of_measure VARCHAR(50) NOT NULL,
    performed_by_user_id UUID NOT NULL REFERENCES users(id),
    transaction_date TIMESTAMP WITH TIME ZONE NOT NULL,
    notes TEXT,
    reference_number VARCHAR(100),
    requires_approval BOOLEAN NOT NULL DEFAULT false,
    approval_status VARCHAR(50),
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
);

-- Enums
CREATE TYPE transaction_type_enum AS ENUM ('creation', 'transfer', 'consumption', 'adjustment');

-- Indexes
CREATE INDEX idx_transactions_date ON transactions(transaction_date);
CREATE INDEX idx_transactions_part ON transactions(part_id);
CREATE INDEX idx_transactions_type ON transactions(transaction_type);
CREATE INDEX idx_transactions_warehouse ON transactions(from_warehouse_id, to_warehouse_id);
CREATE INDEX idx_transactions_machine ON transactions(machine_id);
CREATE INDEX idx_transactions_user ON transactions(performed_by_user_id);
CREATE INDEX idx_transactions_approval ON transactions(requires_approval, approval_status);
```

**Business Rules:**
- All transactions must have a valid performed_by_user
- Consumption transactions must specify from_warehouse
- Transfer transactions must specify both from_warehouse and to_warehouse
- Creation transactions typically have only to_warehouse
- Maximum 7,500 transactions per year (enforced by application)

---

## 🔗 **Supporting Tables**

### **customer_orders**
Orders placed by customers to Oraseas EE for parts.

```sql
CREATE TABLE customer_orders (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    customer_organization_id UUID NOT NULL REFERENCES organizations(id),
    oraseas_organization_id UUID NOT NULL REFERENCES organizations(id),
    order_date TIMESTAMP WITH TIME ZONE NOT NULL,
    expected_delivery_date TIMESTAMP WITH TIME ZONE,
    actual_delivery_date TIMESTAMP WITH TIME ZONE,
    status VARCHAR(50) NOT NULL,
    ordered_by_user_id UUID REFERENCES users(id),
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
);

-- Indexes
CREATE INDEX idx_customer_orders_customer ON customer_orders(customer_organization_id);
CREATE INDEX idx_customer_orders_date ON customer_orders(order_date);
CREATE INDEX idx_customer_orders_status ON customer_orders(status);
```

### **customer_order_items**
Line items for customer orders.

```sql
CREATE TABLE customer_order_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    customer_order_id UUID NOT NULL REFERENCES customer_orders(id),
    part_id UUID NOT NULL REFERENCES parts(id),
    quantity DECIMAL(10,3) NOT NULL DEFAULT 1,
    unit_price DECIMAL(10,2),
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
);

-- Indexes
CREATE INDEX idx_customer_order_items_order ON customer_order_items(customer_order_id);
CREATE INDEX idx_customer_order_items_part ON customer_order_items(part_id);
```

### **supplier_orders**
Orders placed by Oraseas EE to external suppliers.

```sql
CREATE TABLE supplier_orders (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ordering_organization_id UUID NOT NULL REFERENCES organizations(id),
    supplier_name VARCHAR(255) NOT NULL,
    order_date TIMESTAMP WITH TIME ZONE NOT NULL,
    expected_delivery_date TIMESTAMP WITH TIME ZONE,
    actual_delivery_date TIMESTAMP WITH TIME ZONE,
    status VARCHAR(50) NOT NULL,
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
);

-- Indexes
CREATE INDEX idx_supplier_orders_org ON supplier_orders(ordering_organization_id);
CREATE INDEX idx_supplier_orders_date ON supplier_orders(order_date);
CREATE INDEX idx_supplier_orders_status ON supplier_orders(status);
```

### **supplier_order_items**
Line items for supplier orders.

```sql
CREATE TABLE supplier_order_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    supplier_order_id UUID NOT NULL REFERENCES supplier_orders(id),
    part_id UUID NOT NULL REFERENCES parts(id),
    quantity DECIMAL(10,3) NOT NULL DEFAULT 1,
    unit_price DECIMAL(10,2),
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
);

-- Indexes
CREATE INDEX idx_supplier_order_items_order ON supplier_order_items(supplier_order_id);
CREATE INDEX idx_supplier_order_items_part ON supplier_order_items(part_id);
```

### **part_usage**
Records of parts consumed by customers in their machines.

```sql
CREATE TABLE part_usage (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    customer_organization_id UUID NOT NULL REFERENCES organizations(id),
    part_id UUID NOT NULL REFERENCES parts(id),
    usage_date TIMESTAMP WITH TIME ZONE NOT NULL,
    quantity DECIMAL(10,3) NOT NULL DEFAULT 1,
    machine_id UUID REFERENCES machines(id),
    recorded_by_user_id UUID REFERENCES users(id),
    warehouse_id UUID NOT NULL REFERENCES warehouses(id),
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
);

-- Indexes
CREATE INDEX idx_part_usage_customer ON part_usage(customer_organization_id);
CREATE INDEX idx_part_usage_part ON part_usage(part_id);
CREATE INDEX idx_part_usage_date ON part_usage(usage_date);
CREATE INDEX idx_part_usage_machine ON part_usage(machine_id);
```

---

## 🔐 **Security & Audit Tables**

### **security_events**
Comprehensive security event logging for monitoring and audit.

```sql
CREATE TABLE security_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    event_type VARCHAR(50) NOT NULL,
    ip_address VARCHAR(45),
    user_agent TEXT,
    session_id VARCHAR(255),
    details TEXT,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
    risk_level VARCHAR(20) NOT NULL DEFAULT 'low'
);

-- Indexes
CREATE INDEX idx_security_events_user ON security_events(user_id);
CREATE INDEX idx_security_events_type ON security_events(event_type);
CREATE INDEX idx_security_events_timestamp ON security_events(timestamp);
CREATE INDEX idx_security_events_risk ON security_events(risk_level);
```

### **user_sessions**
Active user session tracking for security and management.

```sql
CREATE TABLE user_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id),
    session_token VARCHAR(255) UNIQUE NOT NULL,
    ip_address VARCHAR(45),
    user_agent TEXT,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    last_activity TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
    is_active BOOLEAN NOT NULL DEFAULT true
);

-- Indexes
CREATE INDEX idx_user_sessions_user ON user_sessions(user_id);
CREATE INDEX idx_user_sessions_token ON user_sessions(session_token);
CREATE INDEX idx_user_sessions_expires ON user_sessions(expires_at);
CREATE INDEX idx_user_sessions_active ON user_sessions(is_active);
```

### **invitation_audit_logs**
Audit trail for user invitation activities.

```sql
CREATE TABLE invitation_audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id),
    action VARCHAR(50) NOT NULL,
    performed_by_user_id UUID REFERENCES users(id),
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
    details TEXT
);

-- Indexes
CREATE INDEX idx_invitation_audit_user ON invitation_audit_logs(user_id);
CREATE INDEX idx_invitation_audit_action ON invitation_audit_logs(action);
CREATE INDEX idx_invitation_audit_timestamp ON invitation_audit_logs(timestamp);
```

### **user_management_audit_logs**
Comprehensive audit trail for user management actions.

```sql
CREATE TABLE user_management_audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id),
    action VARCHAR(50) NOT NULL,
    performed_by_user_id UUID NOT NULL REFERENCES users(id),
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
    details TEXT
);

-- Indexes
CREATE INDEX idx_user_mgmt_audit_user ON user_management_audit_logs(user_id);
CREATE INDEX idx_user_mgmt_audit_action ON user_management_audit_logs(action);
CREATE INDEX idx_user_mgmt_audit_timestamp ON user_management_audit_logs(timestamp);
```

---

## 📊 **Inventory Workflow Tables**

### **stock_adjustments**
Detailed logging of all inventory adjustments with reason codes.

```sql
CREATE TABLE stock_adjustments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    inventory_id UUID NOT NULL REFERENCES inventory(id),
    user_id UUID NOT NULL REFERENCES users(id),
    adjustment_date TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
    quantity_adjusted DECIMAL(10,3) NOT NULL,
    reason_code VARCHAR(100) NOT NULL,
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
);

-- Indexes
CREATE INDEX idx_stock_adjustments_inventory ON stock_adjustments(inventory_id);
CREATE INDEX idx_stock_adjustments_user ON stock_adjustments(user_id);
CREATE INDEX idx_stock_adjustments_date ON stock_adjustments(adjustment_date);
CREATE INDEX idx_stock_adjustments_reason ON stock_adjustments(reason_code);
```

### **transaction_approvals**
Approval workflow for high-value or sensitive transactions.

```sql
CREATE TABLE transaction_approvals (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    transaction_id UUID NOT NULL REFERENCES transactions(id),
    approver_id UUID NOT NULL REFERENCES users(id),
    status transaction_approval_status_enum NOT NULL,
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
);

-- Enums
CREATE TYPE transaction_approval_status_enum AS ENUM ('pending', 'approved', 'rejected');

-- Indexes
CREATE INDEX idx_transaction_approvals_transaction ON transaction_approvals(transaction_id);
CREATE INDEX idx_transaction_approvals_approver ON transaction_approvals(approver_id);
CREATE INDEX idx_transaction_approvals_status ON transaction_approvals(status);
```

---

## 🔧 **Performance Optimization**

### **Critical Indexes for Scale**

Given the scale requirements, these indexes are essential for performance:

```sql
-- Organization hierarchy queries
CREATE INDEX idx_organizations_hierarchy ON organizations(parent_organization_id, organization_type);

-- User authentication and authorization
CREATE INDEX idx_users_auth ON users(email, password_hash) WHERE is_active = true;
CREATE INDEX idx_users_org_active ON users(organization_id, is_active, role);

-- Inventory lookups (most frequent queries)
CREATE INDEX idx_inventory_warehouse_stock ON inventory(warehouse_id, current_stock);
CREATE INDEX idx_inventory_part_stock ON inventory(part_id, current_stock);

-- Transaction history (audit trail queries)
CREATE INDEX idx_transactions_date_type ON transactions(transaction_date, transaction_type);
CREATE INDEX idx_transactions_part_date ON transactions(part_id, transaction_date);

-- Machine usage tracking
CREATE INDEX idx_part_usage_machine_date ON part_usage(machine_id, usage_date);

-- Order management
CREATE INDEX idx_customer_orders_org_status ON customer_orders(customer_organization_id, status);
```

### **Database Views for Complex Queries**

```sql
-- Organization hierarchy view
CREATE VIEW organization_hierarchy AS
WITH RECURSIVE org_tree AS (
    SELECT id, name, organization_type, parent_organization_id, 0 as level
    FROM organizations 
    WHERE parent_organization_id IS NULL
    
    UNION ALL
    
    SELECT o.id, o.name, o.organization_type, o.parent_organization_id, ot.level + 1
    FROM organizations o
    JOIN org_tree ot ON o.parent_organization_id = ot.id
)
SELECT * FROM org_tree;

-- Inventory summary view
CREATE VIEW inventory_summary AS
SELECT 
    i.warehouse_id,
    w.name as warehouse_name,
    w.organization_id,
    o.name as organization_name,
    COUNT(*) as total_parts,
    SUM(CASE WHEN i.current_stock <= i.minimum_stock_recommendation THEN 1 ELSE 0 END) as low_stock_parts,
    SUM(i.current_stock * COALESCE(p.unit_price, 0)) as total_value
FROM inventory i
JOIN warehouses w ON i.warehouse_id = w.id
JOIN organizations o ON w.organization_id = o.id
JOIN parts p ON i.part_id = p.id
WHERE w.is_active = true
GROUP BY i.warehouse_id, w.name, w.organization_id, o.name;

-- Machine usage summary view
CREATE VIEW machine_usage_summary AS
SELECT 
    m.id as machine_id,
    m.name as machine_name,
    m.serial_number,
    m.customer_organization_id,
    o.name as customer_name,
    COUNT(pu.id) as total_usage_records,
    MAX(pu.usage_date) as last_usage_date,
    SUM(pu.quantity) as total_parts_consumed
FROM machines m
JOIN organizations o ON m.customer_organization_id = o.id
LEFT JOIN part_usage pu ON m.id = pu.machine_id
GROUP BY m.id, m.name, m.serial_number, m.customer_organization_id, o.name;
```

---

## 🔒 **Business Rule Constraints**

### **Database-Level Constraints**

```sql
-- Ensure suppliers have parent organizations
ALTER TABLE organizations 
ADD CONSTRAINT supplier_must_have_parent 
CHECK (organization_type != 'supplier' OR parent_organization_id IS NOT NULL);

-- Ensure positive quantities in transactions
ALTER TABLE transactions 
ADD CONSTRAINT positive_quantity 
CHECK (quantity > 0);

-- Ensure valid transaction types have appropriate warehouses
ALTER TABLE transactions 
ADD CONSTRAINT valid_transaction_warehouses 
CHECK (
    (transaction_type = 'creation' AND from_warehouse_id IS NULL AND to_warehouse_id IS NOT NULL) OR
    (transaction_type = 'consumption' AND from_warehouse_id IS NOT NULL AND to_warehouse_id IS NULL) OR
    (transaction_type = 'transfer' AND from_warehouse_id IS NOT NULL AND to_warehouse_id IS NOT NULL) OR
    (transaction_type = 'adjustment')
);

-- Ensure machine ownership by customers only
ALTER TABLE machines 
ADD CONSTRAINT machine_customer_only 
CHECK (customer_organization_id IN (
    SELECT id FROM organizations WHERE organization_type = 'customer'
));
```

### **Application-Level Business Rules**

These rules are enforced by the application layer:

1. **Organization Constraints:**
   - Only one Oraseas EE organization allowed
   - Only one BossAqua organization allowed
   - Maximum 100 customer organizations

2. **User Constraints:**
   - Super admins must belong to Oraseas EE
   - Maximum 200 total users
   - Each organization must have at least one admin

3. **Inventory Constraints:**
   - Stock calculations based on transaction history
   - Negative inventory warnings (configurable)
   - Maximum 150 warehouses total

4. **Transaction Constraints:**
   - Maximum 7,500 transactions per year
   - High-value transactions require approval
   - Machine usage must be recorded by organization members

---

## 🔄 **Migration Strategy**

### **Migration Scripts Location**
All database migrations are managed through Alembic and stored in:
```
backend/alembic/versions/
```

### **Key Migration Files**
- `001_initial_schema.py` - Initial database schema
- `002_business_model_alignment.py` - Business model alignment changes
- `003_enhanced_user_management.py` - User management enhancements
- `004_warehouse_inventory_system.py` - Warehouse-based inventory
- `005_transaction_tracking.py` - Comprehensive transaction system
- `006_security_enhancements.py` - Security and audit features

### **Migration Commands**
```bash
# Apply all pending migrations
docker-compose exec api alembic upgrade head

# Create new migration
docker-compose exec api alembic revision --autogenerate -m "description"

# Rollback one migration
docker-compose exec api alembic downgrade -1

# View migration history
docker-compose exec api alembic history
```

---

## 📊 **Performance Monitoring**

### **Key Metrics to Monitor**

1. **Query Performance:**
   - Average query response time < 100ms
   - Slow query threshold: > 1 second
   - Index usage efficiency > 95%

2. **Connection Management:**
   - Active connections < 80% of pool size
   - Connection wait time < 100ms
   - Connection pool efficiency > 90%

3. **Storage Metrics:**
   - Database size growth rate
   - Table bloat percentage < 20%
   - Index bloat percentage < 15%

### **Monitoring Queries**

```sql
-- Check slow queries
SELECT query, mean_time, calls, total_time
FROM pg_stat_statements 
ORDER BY mean_time DESC 
LIMIT 10;

-- Check index usage
SELECT schemaname, tablename, attname, n_distinct, correlation
FROM pg_stats 
WHERE schemaname = 'public' 
ORDER BY n_distinct DESC;

-- Check database size
SELECT pg_size_pretty(pg_database_size(current_database()));

-- Check table sizes
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
FROM pg_tables 
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

---

**Last Updated:** January 2025  
**Version:** 2.0.0  
**Next Review:** February 2025