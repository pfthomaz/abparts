-- ABParts SQL Create Table Scripts - Business Model Alignment
-- These SQL commands will create the tables for the ABParts database schema in PostgreSQL
-- aligned with the new business model requirements including organization hierarchy,
-- warehouse management, enhanced user security, and decimal quantity support.

-- Enable UUID-OSSP extension if not already enabled (for UUID generation).
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Drop tables in reverse order of dependency to avoid foreign key constraints errors
DROP TABLE IF EXISTS stock_adjustments CASCADE;
DROP TABLE IF EXISTS transactions CASCADE;
DROP TABLE IF EXISTS part_usage CASCADE;
DROP TABLE IF EXISTS customer_order_items CASCADE;
DROP TABLE IF EXISTS customer_orders CASCADE;
DROP TABLE IF EXISTS supplier_order_items CASCADE;
DROP TABLE IF EXISTS supplier_orders CASCADE;
DROP TABLE IF EXISTS inventory CASCADE;
DROP TABLE IF EXISTS warehouses CASCADE;
DROP TABLE IF EXISTS parts CASCADE;
DROP TABLE IF EXISTS machines CASCADE;
DROP TABLE IF EXISTS users CASCADE;
DROP TABLE IF EXISTS organizations CASCADE;

-- Drop enum types if they exist
DROP TYPE IF EXISTS organizationtype CASCADE;
DROP TYPE IF EXISTS parttype CASCADE;
DROP TYPE IF EXISTS userrole CASCADE;
DROP TYPE IF EXISTS userstatus CASCADE;
DROP TYPE IF EXISTS transactiontype CASCADE;

-- Create enum types for the new business model
CREATE TYPE organizationtype AS ENUM ('oraseas_ee', 'bossaqua', 'customer', 'supplier');
CREATE TYPE parttype AS ENUM ('consumable', 'bulk_material');
CREATE TYPE userrole AS ENUM ('user', 'admin', 'super_admin');
CREATE TYPE userstatus AS ENUM ('active', 'inactive', 'pending_invitation', 'locked');
CREATE TYPE transactiontype AS ENUM ('creation', 'transfer', 'consumption', 'adjustment');

-- 1. organizations Table - Enhanced with hierarchy and business model alignment
CREATE TABLE organizations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL UNIQUE,
    organization_type organizationtype NOT NULL,
    parent_organization_id UUID,
    address TEXT,
    contact_info TEXT,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    FOREIGN KEY (parent_organization_id) REFERENCES organizations(id),
    CONSTRAINT supplier_must_have_parent CHECK (
        organization_type != 'supplier' OR parent_organization_id IS NOT NULL
    )
);

-- Create indexes for organization queries
CREATE INDEX idx_organizations_name ON organizations(name);
CREATE UNIQUE INDEX unique_oraseas_ee ON organizations (organization_type) WHERE organization_type = 'oraseas_ee';
CREATE UNIQUE INDEX unique_bossaqua ON organizations (organization_type) WHERE organization_type = 'bossaqua';

-- 2. warehouses Table - New for warehouse management
CREATE TABLE warehouses (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID NOT NULL,
    name VARCHAR(255) NOT NULL,
    location VARCHAR(500),
    description TEXT,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    UNIQUE (organization_id, name),
    FOREIGN KEY (organization_id) REFERENCES organizations(id)
);

-- 3. users Table - Enhanced with security features
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID NOT NULL,
    username VARCHAR(255) NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    name VARCHAR(255),
    role userrole NOT NULL,
    user_status userstatus NOT NULL DEFAULT 'active',
    failed_login_attempts INTEGER NOT NULL DEFAULT 0,
    locked_until TIMESTAMP WITH TIME ZONE,
    last_login TIMESTAMP WITH TIME ZONE,
    invitation_token VARCHAR(255),
    invitation_expires_at TIMESTAMP WITH TIME ZONE,
    password_reset_token VARCHAR(255),
    password_reset_expires_at TIMESTAMP WITH TIME ZONE,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    FOREIGN KEY (organization_id) REFERENCES organizations(id)
);

-- Create indexes for user queries
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_org_role ON users(organization_id, role);

-- 4. machines Table - Updated with correct foreign key
CREATE TABLE machines (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    customer_organization_id UUID NOT NULL,
    model_type VARCHAR(100) NOT NULL,
    name VARCHAR(255) NOT NULL,
    serial_number VARCHAR(255) NOT NULL UNIQUE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    FOREIGN KEY (customer_organization_id) REFERENCES organizations(id)
);

-- Create index for machine queries
CREATE INDEX idx_machines_customer ON machines(customer_organization_id);

-- 5. parts Table - Enhanced with part types and units
CREATE TABLE parts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    part_number VARCHAR(255) NOT NULL UNIQUE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    part_type parttype NOT NULL DEFAULT 'consumable',
    is_proprietary BOOLEAN NOT NULL DEFAULT FALSE,
    unit_of_measure VARCHAR(50) NOT NULL DEFAULT 'pieces',
    manufacturer_part_number VARCHAR(255),
    manufacturer_delivery_time_days INTEGER,
    local_supplier_delivery_time_days INTEGER,
    image_urls TEXT[],
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- Create index for part queries
CREATE INDEX idx_parts_part_number ON parts(part_number);

-- 6. inventory Table - Updated to use warehouses and decimal quantities
CREATE TABLE inventory (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    warehouse_id UUID NOT NULL,
    part_id UUID NOT NULL,
    current_stock DECIMAL(10,3) NOT NULL DEFAULT 0,
    minimum_stock_recommendation DECIMAL(10,3) NOT NULL DEFAULT 0,
    unit_of_measure VARCHAR(50) NOT NULL,
    reorder_threshold_set_by VARCHAR(50),
    last_recommendation_update TIMESTAMP WITH TIME ZONE,
    last_updated TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    UNIQUE (warehouse_id, part_id),
    FOREIGN KEY (warehouse_id) REFERENCES warehouses(id),
    FOREIGN KEY (part_id) REFERENCES parts(id)
);

-- Create index for inventory queries
CREATE INDEX idx_inventory_warehouse_part ON inventory(warehouse_id, part_id);

-- 7. supplier_orders Table
CREATE TABLE supplier_orders (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    ordering_organization_id UUID NOT NULL,
    supplier_name VARCHAR(255) NOT NULL,
    order_date TIMESTAMP WITH TIME ZONE NOT NULL,
    expected_delivery_date TIMESTAMP WITH TIME ZONE,
    actual_delivery_date TIMESTAMP WITH TIME ZONE,
    status VARCHAR(50) NOT NULL,
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    FOREIGN KEY (ordering_organization_id) REFERENCES organizations(id)
);

-- 8. supplier_order_items Table - Updated with decimal quantities
CREATE TABLE supplier_order_items (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    supplier_order_id UUID NOT NULL,
    part_id UUID NOT NULL,
    quantity DECIMAL(10,3) NOT NULL DEFAULT 1,
    unit_price DECIMAL(10, 2),
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    FOREIGN KEY (supplier_order_id) REFERENCES supplier_orders(id),
    FOREIGN KEY (part_id) REFERENCES parts(id)
);

-- 9. customer_orders Table
CREATE TABLE customer_orders (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    customer_organization_id UUID NOT NULL,
    oraseas_organization_id UUID NOT NULL,
    order_date TIMESTAMP WITH TIME ZONE NOT NULL,
    expected_delivery_date TIMESTAMP WITH TIME ZONE,
    actual_delivery_date TIMESTAMP WITH TIME ZONE,
    status VARCHAR(50) NOT NULL,
    ordered_by_user_id UUID,
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    FOREIGN KEY (customer_organization_id) REFERENCES organizations(id),
    FOREIGN KEY (oraseas_organization_id) REFERENCES organizations(id),
    FOREIGN KEY (ordered_by_user_id) REFERENCES users(id)
);

-- 10. customer_order_items Table - Updated with decimal quantities
CREATE TABLE customer_order_items (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    customer_order_id UUID NOT NULL,
    part_id UUID NOT NULL,
    quantity DECIMAL(10,3) NOT NULL DEFAULT 1,
    unit_price DECIMAL(10, 2),
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    FOREIGN KEY (customer_order_id) REFERENCES customer_orders(id),
    FOREIGN KEY (part_id) REFERENCES parts(id)
);

-- 11. part_usage Table - Updated with decimal quantities
CREATE TABLE part_usage (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    customer_organization_id UUID NOT NULL,
    part_id UUID NOT NULL,
    usage_date TIMESTAMP WITH TIME ZONE NOT NULL,
    quantity_used DECIMAL(10,3) NOT NULL DEFAULT 1,
    machine_id UUID,
    recorded_by_user_id UUID,
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    FOREIGN KEY (customer_organization_id) REFERENCES organizations(id),
    FOREIGN KEY (part_id) REFERENCES parts(id),
    FOREIGN KEY (machine_id) REFERENCES machines(id),
    FOREIGN KEY (recorded_by_user_id) REFERENCES users(id)
);

-- 12. transactions Table - New for comprehensive audit trail
CREATE TABLE transactions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    transaction_type transactiontype NOT NULL,
    part_id UUID NOT NULL,
    from_warehouse_id UUID,
    to_warehouse_id UUID,
    machine_id UUID,
    quantity DECIMAL(10,3) NOT NULL,
    unit_of_measure VARCHAR(50) NOT NULL,
    performed_by_user_id UUID NOT NULL,
    transaction_date TIMESTAMP WITH TIME ZONE NOT NULL,
    notes TEXT,
    reference_number VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    FOREIGN KEY (part_id) REFERENCES parts(id),
    FOREIGN KEY (from_warehouse_id) REFERENCES warehouses(id),
    FOREIGN KEY (to_warehouse_id) REFERENCES warehouses(id),
    FOREIGN KEY (machine_id) REFERENCES machines(id),
    FOREIGN KEY (performed_by_user_id) REFERENCES users(id)
);

-- Create indexes for transaction queries
CREATE INDEX idx_transactions_date ON transactions(transaction_date);
CREATE INDEX idx_transactions_part ON transactions(part_id);
CREATE INDEX idx_transactions_warehouse ON transactions(from_warehouse_id, to_warehouse_id);

-- 13. stock_adjustments Table - New for inventory adjustments
CREATE TABLE stock_adjustments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    inventory_id UUID NOT NULL,
    user_id UUID NOT NULL,
    adjustment_date TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    quantity_adjusted DECIMAL(10,3) NOT NULL,
    reason_code VARCHAR(100) NOT NULL,
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    FOREIGN KEY (inventory_id) REFERENCES inventory(id),
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Create database functions for automatic inventory updates
CREATE OR REPLACE FUNCTION update_inventory_on_transaction()
RETURNS TRIGGER AS $$
BEGIN
    -- Handle different transaction types
    CASE NEW.transaction_type
        WHEN 'creation' THEN
            -- Increase inventory in to_warehouse
            IF NEW.to_warehouse_id IS NOT NULL THEN
                INSERT INTO inventory (warehouse_id, part_id, current_stock, unit_of_measure)
                VALUES (NEW.to_warehouse_id, NEW.part_id, NEW.quantity, NEW.unit_of_measure)
                ON CONFLICT (warehouse_id, part_id)
                DO UPDATE SET 
                    current_stock = inventory.current_stock + NEW.quantity,
                    last_updated = NOW();
            END IF;
            
        WHEN 'transfer' THEN
            -- Decrease from source warehouse
            IF NEW.from_warehouse_id IS NOT NULL THEN
                UPDATE inventory 
                SET current_stock = current_stock - NEW.quantity,
                    last_updated = NOW()
                WHERE warehouse_id = NEW.from_warehouse_id AND part_id = NEW.part_id;
            END IF;
            
            -- Increase in destination warehouse
            IF NEW.to_warehouse_id IS NOT NULL THEN
                INSERT INTO inventory (warehouse_id, part_id, current_stock, unit_of_measure)
                VALUES (NEW.to_warehouse_id, NEW.part_id, NEW.quantity, NEW.unit_of_measure)
                ON CONFLICT (warehouse_id, part_id)
                DO UPDATE SET 
                    current_stock = inventory.current_stock + NEW.quantity,
                    last_updated = NOW();
            END IF;
            
        WHEN 'consumption' THEN
            -- Decrease inventory in from_warehouse
            IF NEW.from_warehouse_id IS NOT NULL THEN
                UPDATE inventory 
                SET current_stock = current_stock - NEW.quantity,
                    last_updated = NOW()
                WHERE warehouse_id = NEW.from_warehouse_id AND part_id = NEW.part_id;
            END IF;
            
        WHEN 'adjustment' THEN
            -- Adjust inventory in specified warehouse
            IF NEW.to_warehouse_id IS NOT NULL THEN
                INSERT INTO inventory (warehouse_id, part_id, current_stock, unit_of_measure)
                VALUES (NEW.to_warehouse_id, NEW.part_id, NEW.quantity, NEW.unit_of_measure)
                ON CONFLICT (warehouse_id, part_id)
                DO UPDATE SET 
                    current_stock = inventory.current_stock + NEW.quantity,
                    last_updated = NOW();
            END IF;
    END CASE;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger to automatically update inventory
CREATE TRIGGER trigger_update_inventory_on_transaction
AFTER INSERT ON transactions
FOR EACH ROW
EXECUTE FUNCTION update_inventory_on_transaction();

-- Create function to prevent negative inventory (optional)
CREATE OR REPLACE FUNCTION check_inventory_balance()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.current_stock < 0 THEN
        RAISE EXCEPTION 'Inventory cannot be negative. Current stock would be: %', NEW.current_stock;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger to check inventory balance
CREATE TRIGGER trigger_check_inventory_balance
BEFORE UPDATE ON inventory
FOR EACH ROW
EXECUTE FUNCTION check_inventory_balance();

-- Seed Data for Initial Setup - Business Model Aligned
DO $$
DECLARE
    ORG_ORASEAS_EE_ID UUID := 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11';
    ORG_BOSSAQUA_ID UUID := 'b0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12';
    ORG_AUTOBOSS_INC_ID UUID := 'b1cdd000-0d1c-1a2b-3c4d-5e6f7a8b9c01';
    ORG_AUTOPARTS_LTD_ID UUID := 'c2dee111-1e2d-2b3c-4d5e-6f7a8b9c0123';
    ORG_CUSTOMER_B_ID UUID := 'd3eff222-2f3e-3c4d-5e6f-7a8b9c012346';
    ORG_CUSTOMER_C_ID UUID := 'e4fac333-3c4f-4d5e-6f7a-8b9c01234568';

    -- Warehouse IDs
    WAREHOUSE_ORASEAS_MAIN_ID UUID := '11eebc99-9c0b-4ef8-bb6d-6bb9bd380a11';
    WAREHOUSE_ORASEAS_SPARE_ID UUID := '22eebc99-9c0b-4ef8-bb6d-6bb9bd380a12';
    WAREHOUSE_AUTOBOSS_MAIN_ID UUID := '33cdd000-0d1c-1a2b-3c4d-5e6f7a8b9c01';
    WAREHOUSE_CUSTOMER_B_ID UUID := '44eff222-2f3e-3c4d-5e6f-7a8b9c012346';

    -- User IDs
    USER_SUPER_ADMIN_ID UUID := 'f6abc555-5b6c-6f7a-8b9c-0d123456789a';
    USER_ORASEAS_ADMIN_ID UUID := 'd3eff222-2f3e-3c4d-5e6f-7a8b9c012345';
    USER_AUTOBOSS_ADMIN_ID UUID := 'f5abc444-4a5b-5e6f-7a8b-9c0123456789';
    USER_AUTOPARTS_LTD_USER_ID UUID := 'b0ccc999-9c0c-0d12-3456-789012345678';
    USER_CUSTOMER_B_USER_ID UUID := 'c1ddd000-0d1d-1e23-4567-890123456789';
    USER_CUSTOMER_C_USER_ID UUID := 'd2eee111-1e2e-2f34-5678-901234567890';

    -- Machine IDs
    MACHINE_V31B_ID UUID := '1a2b3c4d-5e6f-7a8b-9c0d-e1f2a3b4c5d6';
    MACHINE_V40_ID UUID := '6d5c4b3a-2f1e-8b7a-9d0c-e3f4a5b6c7d8';

    -- Part IDs
    PART_ENGINE_FILTER_ID UUID := 'a7aaa666-6a7a-7a8b-9c01-234567890123';
    PART_CONTROL_UNIT_ID UUID := 'b8bbb777-7b8b-8b9c-0123-456789012345';
    PART_HYDRAULIC_PUMP_ID UUID := 'a1b2c3d4-e5f6-7a8b-9c0d-e1f2a3b4c5d7';
    PART_SENSOR_MODULE_ID UUID := 'b1c2d3e4-f5a6-7b8c-9d0e-1f2a3b4c5d6f';
    PART_DRIVE_BELT_ID UUID := 'c1d2e3f4-a5b6-7c8d-9e0f-1a2b3c4d5e70';

BEGIN
    -- Organizations (6) - Updated with new business model
    INSERT INTO organizations (id, name, organization_type, parent_organization_id, address, contact_info) VALUES
    (ORG_ORASEAS_EE_ID, 'Oraseas EE', 'oraseas_ee', NULL, '123 Main St, Auckland, NZ', '+64 9 123 4567'),
    (ORG_BOSSAQUA_ID, 'BossAqua', 'bossaqua', NULL, '456 Manufacturing Ave, Auckland, NZ', '+64 9 234 5678'),
    (ORG_AUTOBOSS_INC_ID, 'Autoboss Inc', 'customer', NULL, '456 Tech Park, Wellington, NZ', '+64 4 987 6543'),
    (ORG_AUTOPARTS_LTD_ID, 'AutoParts Ltd', 'supplier', ORG_ORASEAS_EE_ID, '789 Supply Rd, Christchurch, NZ', '+64 3 234 5678'),
    (ORG_CUSTOMER_B_ID, 'RoboMech Solutions', 'customer', NULL, '101 Automation Drive, Hamilton, NZ', '+64 7 222 3333'),
    (ORG_CUSTOMER_C_ID, 'Industrial Innovators', 'customer', NULL, '202 Factory Rd, Dunedin, NZ', '+64 3 444 5555');

    -- Warehouses (4) - New for warehouse management
    INSERT INTO warehouses (id, organization_id, name, location, description) VALUES
    (WAREHOUSE_ORASEAS_MAIN_ID, ORG_ORASEAS_EE_ID, 'Main Warehouse', 'Building A, 123 Main St, Auckland', 'Primary storage facility'),
    (WAREHOUSE_ORASEAS_SPARE_ID, ORG_ORASEAS_EE_ID, 'Spare Parts Warehouse', 'Building B, 123 Main St, Auckland', 'Specialized spare parts storage'),
    (WAREHOUSE_AUTOBOSS_MAIN_ID, ORG_AUTOBOSS_INC_ID, 'Production Warehouse', '456 Tech Park, Wellington', 'On-site parts storage'),
    (WAREHOUSE_CUSTOMER_B_ID, ORG_CUSTOMER_B_ID, 'RoboMech Storage', '101 Automation Drive, Hamilton', 'Customer parts inventory');

    -- Users (6) - Updated with new role enums
    INSERT INTO users (id, organization_id, username, password_hash, email, name, role) VALUES
    (USER_SUPER_ADMIN_ID, ORG_ORASEAS_EE_ID, 'superadmin', '$2b$12$SloIsiIq.hHt97P4aiYYfeocRRYfoDRdmTm7pcUFvGV77cBqQDoAK', 'superadmin@oraseas.com', 'Super Admin', 'super_admin'),
    (USER_ORASEAS_ADMIN_ID, ORG_ORASEAS_EE_ID, 'oraseasee_admin', '$2b$12$iPjCrXM5KgyxmQ99HA.k2ux95xNuxxHTZFrsE4QXRCe1AZS68H8Uy', 'admin@oraseas.com', 'Oraseas Admin', 'admin'),
    (USER_AUTOBOSS_ADMIN_ID, ORG_AUTOBOSS_INC_ID, 'autoboss_admin', '$2b$12$iPjCrXM5KgyxmQ99HA.k2ux95xNuxxHTZFrsE4QXRCe1AZS68H8Uy', 'admin@autoboss.com', 'Autoboss Admin', 'admin'),
    (USER_AUTOPARTS_LTD_USER_ID, ORG_AUTOPARTS_LTD_ID, 'autoparts_user', '$2b$12$ArVJaYD7kXidYWguYO2Gt.2lI3rV3Pm8dmfTJ8DjSAI2KdpFh1xv2', 'user@autoparts.com', 'AutoParts User', 'user'),
    (USER_CUSTOMER_B_USER_ID, ORG_CUSTOMER_B_ID, 'robomech_user', '$2b$12$ArVJaYD7kXidYWguYO2Gt.2lI3rV3Pm8dmfTJ8DjSAI2KdpFh1xv2', 'user@robomech.com', 'RoboMech User', 'user'),
    (USER_CUSTOMER_C_USER_ID, ORG_CUSTOMER_C_ID, 'industrial_user', '$2b$12$ArVJaYD7kXidYWguYO2Gt.2lI3rV3Pm8dmfTJ8DjSAI2KdpFh1xv2', 'user@industrial.com', 'Industrial User', 'user');

    -- Machines (2) - Updated with correct foreign key
    INSERT INTO machines (id, customer_organization_id, model_type, name, serial_number) VALUES
    (MACHINE_V31B_ID, ORG_AUTOBOSS_INC_ID, 'V3.1B', 'Main Production Line Machine', 'ABV31B-SN001'),
    (MACHINE_V40_ID, ORG_AUTOBOSS_INC_ID, 'V4.0', 'Assembly Robot 2000', 'ABV40-SN002');

    -- Parts (5) - Updated with new part types and units
    INSERT INTO parts (id, part_number, name, description, part_type, is_proprietary, unit_of_measure, manufacturer_part_number, manufacturer_delivery_time_days, local_supplier_delivery_time_days, image_urls) VALUES
    (PART_ENGINE_FILTER_ID, 'PN-001-A', 'Engine Air Filter', 'Standard air filter for combustion engines', 'consumable', FALSE, 'pieces', 'MFG-FILTER-001', NULL, 3, ARRAY['/static/images/default_part_filter.jpg']),
    (PART_CONTROL_UNIT_ID, 'PN-002-B', 'Central Control Unit', 'Advanced control unit for machine operations', 'consumable', TRUE, 'pieces', 'MFG-CTRL-002', 21, NULL, ARRAY['/static/images/default_part_control_unit.jpg']),
    (PART_HYDRAULIC_PUMP_ID, 'PN-003-C', 'Hydraulic Pump', 'High-pressure hydraulic pump assembly', 'consumable', TRUE, 'pieces', 'MFG-PUMP-003', 28, NULL, ARRAY['/static/images/default_part_hydraulic_pump.jpg']),
    (PART_SENSOR_MODULE_ID, 'PN-004-D', 'Proximity Sensor Module', 'Detects object presence and distance', 'consumable', FALSE, 'pieces', 'MFG-SENS-004', NULL, 5, ARRAY['/static/images/default_part_sensor_module.jpg']),
    (PART_DRIVE_BELT_ID, 'PN-005-E', 'Drive Belt', 'Power transmission belt for motion systems', 'bulk_material', FALSE, 'meters', 'MFG-BELT-005', NULL, 2, ARRAY['/static/images/default_part_drive_belt.jpg']);

    -- Inventory (warehouse-based with decimal quantities)
    INSERT INTO inventory (warehouse_id, part_id, current_stock, minimum_stock_recommendation, unit_of_measure, reorder_threshold_set_by) VALUES
    -- Oraseas Main Warehouse
    (WAREHOUSE_ORASEAS_MAIN_ID, PART_ENGINE_FILTER_ID, 150.000, 70.000, 'pieces', 'system'),
    (WAREHOUSE_ORASEAS_MAIN_ID, PART_CONTROL_UNIT_ID, 25.000, 10.000, 'pieces', 'system'),
    (WAREHOUSE_ORASEAS_MAIN_ID, PART_HYDRAULIC_PUMP_ID, 15.000, 7.000, 'pieces', 'user'),
    (WAREHOUSE_ORASEAS_MAIN_ID, PART_SENSOR_MODULE_ID, 200.000, 100.000, 'pieces', 'system'),
    -- Oraseas Spare Parts Warehouse
    (WAREHOUSE_ORASEAS_SPARE_ID, PART_DRIVE_BELT_ID, 500.500, 200.000, 'meters', 'system'),
    (WAREHOUSE_ORASEAS_SPARE_ID, PART_ENGINE_FILTER_ID, 50.000, 25.000, 'pieces', 'user'),
    -- Autoboss Production Warehouse
    (WAREHOUSE_AUTOBOSS_MAIN_ID, PART_ENGINE_FILTER_ID, 30.000, 15.000, 'pieces', 'user'),
    (WAREHOUSE_AUTOBOSS_MAIN_ID, PART_SENSOR_MODULE_ID, 40.000, 20.000, 'pieces', 'system'),
    (WAREHOUSE_AUTOBOSS_MAIN_ID, PART_DRIVE_BELT_ID, 25.750, 10.000, 'meters', 'system'),
    (WAREHOUSE_AUTOBOSS_MAIN_ID, PART_CONTROL_UNIT_ID, 5.000, 2.000, 'pieces', 'user'),
    -- Customer B Warehouse
    (WAREHOUSE_CUSTOMER_B_ID, PART_ENGINE_FILTER_ID, 10.000, 5.000, 'pieces', 'user'),
    (WAREHOUSE_CUSTOMER_B_ID, PART_DRIVE_BELT_ID, 15.250, 8.000, 'meters', 'system'),
    (WAREHOUSE_CUSTOMER_B_ID, PART_SENSOR_MODULE_ID, 5.000, 2.000, 'pieces', 'user'),
    (WAREHOUSE_CUSTOMER_B_ID, PART_HYDRAULIC_PUMP_ID, 2.000, 1.000, 'pieces', 'system');

END $$;