-- ABParts SQL Create Table Scripts
-- These SQL commands will create the tables for the ABParts database schema in PostgreSQL. 
-- They include primary keys, foreign keys, default values, and unique constraints as defined in the schema. This updated script also includes DROP TABLE statements for easy recreation during development and revised initial seed data.

-- Enable UUID-OSSP extension if not already enabled (for UUID generation).
-- You might need superuser privileges to run this.
-- If you're using a managed database service, it might be pre-enabled or configurable via their console.
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Drop tables in reverse order of dependency to avoid foreign key constraints errors
DROP TABLE IF EXISTS part_usage CASCADE;
DROP TABLE IF EXISTS customer_order_items CASCADE;
DROP TABLE IF EXISTS customer_orders CASCADE;
DROP TABLE IF EXISTS supplier_order_items CASCADE;
DROP TABLE IF EXISTS supplier_orders CASCADE;
DROP TABLE IF EXISTS inventory CASCADE;
DROP TABLE IF EXISTS parts CASCADE;
DROP TABLE IF EXISTS machines CASCADE; -- New: Drop machines table
DROP TABLE IF EXISTS users CASCADE;
DROP TABLE IF EXISTS organizations CASCADE;

-- 1. organizations Table
CREATE TABLE organizations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL UNIQUE,
    type VARCHAR(50) NOT NULL,
    address TEXT,
    contact_info TEXT,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- 2. users Table
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID NOT NULL,
    username VARCHAR(255) NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    name VARCHAR(255),
    role VARCHAR(50) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    FOREIGN KEY (organization_id) REFERENCES organizations(id)
);

-- 3. machines Table (New!)
CREATE TABLE machines (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID NOT NULL,
    model_type VARCHAR(100) NOT NULL,
    name VARCHAR(255) NOT NULL,
    serial_number VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    UNIQUE (organization_id, serial_number), -- Ensures serial number is unique within an organization
    FOREIGN KEY (organization_id) REFERENCES organizations(id)
);

-- 4. parts Table
CREATE TABLE parts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    part_number VARCHAR(255) NOT NULL UNIQUE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    is_proprietary BOOLEAN NOT NULL DEFAULT FALSE,
    is_consumable BOOLEAN NOT NULL DEFAULT FALSE,
    manufacturer_delivery_time_days INTEGER,
    local_supplier_delivery_time_days INTEGER,
    image_urls TEXT[], -- Array of text for image URLs
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- 5. inventory Table
CREATE TABLE inventory (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID NOT NULL,
    part_id UUID NOT NULL,
    location VARCHAR(255), -- New: Location of the stock within the organization
    current_stock INTEGER NOT NULL DEFAULT 0,
    minimum_stock_recommendation INTEGER NOT NULL DEFAULT 0,
    reorder_threshold_set_by VARCHAR(50),
    last_recommendation_update TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    UNIQUE (organization_id, part_id),
    FOREIGN KEY (organization_id) REFERENCES organizations(id),
    FOREIGN KEY (part_id) REFERENCES parts(id)
);

-- Add index for location as it will be queried often
CREATE INDEX idx_inventory_location ON inventory(location);

-- 6. supplier_orders Table
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

-- 7. supplier_order_items Table
CREATE TABLE supplier_order_items (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    supplier_order_id UUID NOT NULL,
    part_id UUID NOT NULL,
    quantity INTEGER NOT NULL DEFAULT 1,
    unit_price DECIMAL(10, 2),
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    FOREIGN KEY (supplier_order_id) REFERENCES supplier_orders(id),
    FOREIGN KEY (part_id) REFERENCES parts(id)
);

-- 8. customer_orders Table
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

-- 9. customer_order_items Table
CREATE TABLE customer_order_items (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    customer_order_id UUID NOT NULL,
    part_id UUID NOT NULL,
    quantity INTEGER NOT NULL DEFAULT 1,
    unit_price DECIMAL(10, 2),
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    FOREIGN KEY (customer_order_id) REFERENCES customer_orders(id),
    FOREIGN KEY (part_id) REFERENCES parts(id)
);

-- 10. part_usage Table (machine_id changed to UUID FK!)
CREATE TABLE part_usage (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    customer_organization_id UUID NOT NULL,
    part_id UUID NOT NULL,
    usage_date TIMESTAMP WITH TIME ZONE NOT NULL,
    quantity_used INTEGER NOT NULL DEFAULT 1,
    machine_id UUID, -- Now a UUID Foreign Key!
    recorded_by_user_id UUID,
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    FOREIGN KEY (customer_organization_id) REFERENCES organizations(id),
    FOREIGN KEY (part_id) REFERENCES parts(id),
    FOREIGN KEY (machine_id) REFERENCES machines(id), -- New FK constraint
    FOREIGN KEY (recorded_by_user_id) REFERENCES users(id)
);

-- Seed Data for Initial Setup

-- Define UUIDs for consistent seeding
DO $$
DECLARE
    ORG_ORASEAS_EE_ID UUID := 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11';
    ORG_AUTOBOSS_INC_ID UUID := 'b1cdd000-0d1c-1a2b-3c4d-5e6f7a8b9c01';
    ORG_AUTOPARTS_LTD_ID UUID := 'c2dee111-1e2d-2b3c-4d5e-6f7a8b9c0123';
    ORG_CUSTOMER_B_ID UUID := 'd3eff222-2f3e-3c4d-5e6f-7a8b9c012346';
    ORG_CUSTOMER_C_ID UUID := 'e4fac333-3c4f-4d5e-6f7a-8b9c01234568';

    USER_ORASEAS_ADMIN_ID UUID := 'd3eff222-2f3e-3c4d-5e6f-7a8b9c012345';
    USER_AUTOBOSS_ADMIN_ID UUID := 'f5abc444-4a5b-5e6f-7a8b-9c0123456789';
    USER_AUTOPARTS_LTD_USER_ID UUID := 'b0ccc999-9c0c-0d12-3456-789012345678';
    USER_CUSTOMER_B_USER_ID UUID := 'c1ddd000-0d1d-1e23-4567-890123456789';
    USER_CUSTOMER_C_USER_ID UUID := 'd2eee111-1e2e-2f34-5678-901234567890';
    USER_SUPER_ADMIN_ID UUID := 'f6abc555-5b6c-6f7a-8b9c-0d123456789a';


    MACHINE_V31B_ID UUID := '1a2b3c4d-5e6f-7a8b-9c0d-e1f2a3b4c5d6';
    MACHINE_V40_ID UUID := '6d5c4b3a-2f1e-8b7a-9d0c-e3f4a5b6c7d8';

    PART_ENGINE_FILTER_ID UUID := 'a7aaa666-6a7a-7a8b-9c01-234567890123';
    PART_CONTROL_UNIT_ID UUID := 'b8bbb777-7b8b-8b9c-0123-456789012345';
    PART_HYDRAULIC_PUMP_ID UUID := 'a1b2c3d4-e5f6-7a8b-9c0d-e1f2a3b4c5d7';
    PART_SENSOR_MODULE_ID UUID := 'b1c2d3e4-f5a6-7b8c-9d0e-1f2a3b4c5d6f';
    PART_DRIVE_BELT_ID UUID := 'c1d2e3f4-a5b6-7c8d-9e0f-1a2b3c4d5e70';


    SUPP_ORDER_1_ID UUID := '10aa11bb-22cc-33dd-44ee-55ff66a77b88';
    SUPP_ORDER_2_ID UUID := '20bb22cc-33dd-44ee-55ff-66aa77bb88cc';
    SUPP_ORDER_3_ID UUID := '30cc33dd-44ee-55ff-66aa-77bb88cc99dd';

BEGIN
    -- Organizations (5)
    INSERT INTO organizations (id, name, type, address, contact_info) VALUES
    (ORG_ORASEAS_EE_ID, 'Oraseas EE', 'Warehouse', '123 Main St, Auckland, NZ', '+64 9 123 4567'),
    (ORG_AUTOBOSS_INC_ID, 'Autoboss Inc', 'Customer', '456 Tech Park, Wellington, NZ', '+64 4 987 6543'),
    (ORG_AUTOPARTS_LTD_ID, 'AutoParts Ltd', 'Supplier', '789 Supply Rd, Christchurch, NZ', '+64 3 234 5678'),
    (ORG_CUSTOMER_B_ID, 'RoboMech Solutions', 'Customer', '101 Automation Drive, Hamilton, NZ', '+64 7 222 3333'),
    (ORG_CUSTOMER_C_ID, 'Industrial Innovators', 'Customer', '202 Factory Rd, Dunedin, NZ', '+64 3 444 5555');

    -- Users (1 per organization)
    INSERT INTO users (id, organization_id, username, password_hash, email, name, role) VALUES
    (USER_ORASEAS_ADMIN_ID, ORG_ORASEAS_EE_ID, 'oraseasee_admin', '$2b$12$iPjCrXM5KgyxmQ99HA.k2ux95xNuxxHTZFrsE4QXRCe1AZS68H8Uy', 'admin@oraseas.com', 'Oraseas Admin', 'Oraseas Admin'),
    (USER_AUTOBOSS_ADMIN_ID, ORG_AUTOBOSS_INC_ID, 'autoboss_admin', '$2b$12$iPjCrXM5KgyxmQ99HA.k2ux95xNuxxHTZFrsE4QXRCe1AZS68H8Uy', 'admin@autoboss.com', 'Autoboss Admin', 'Customer Admin'),
    (USER_AUTOPARTS_LTD_USER_ID, ORG_AUTOPARTS_LTD_ID, 'autoparts_user', '$2b$12$ArVJaYD7kXidYWguYO2Gt.2lI3rV3Pm8dmfTJ8DjSAI2KdpFh1xv2', 'user@autoparts.com', 'AutoParts User', 'Supplier User'),
    (USER_CUSTOMER_B_USER_ID, ORG_CUSTOMER_B_ID, 'robomech_user', '$2b$12$ArVJaYD7kXidYWguYO2Gt.2lI3rV3Pm8dmfTJ8DjSAI2KdpFh1xv2', 'user@robomech.com', 'RoboMech User', 'Customer User'),
    (USER_CUSTOMER_C_USER_ID, ORG_CUSTOMER_C_ID, 'industrial_user', '$2b$12$ArVJaYD7kXidYWguYO2Gt.2lI3rV3Pm8dmfTJ8DjSAI2KdpFh1xv2', 'user@industrial.com', 'Industrial User', 'Customer User'),
    (USER_SUPER_ADMIN_ID, ORG_ORASEAS_EE_ID, 'superadmin', '$2b$12$SloIsiIq.hHt97P4aiYYfeocRRYfoDRdmTm7pcUFvGV77cBqQDoAK', 'superadmin@oraseas.com', 'Super Admin', 'Oraseas Admin');

    -- Machines (2)
    INSERT INTO machines (id, organization_id, model_type, name, serial_number) VALUES
    (MACHINE_V31B_ID, ORG_AUTOBOSS_INC_ID, 'V3.1B', 'Main Production Line Machine', 'ABV31B-SN001'),
    (MACHINE_V40_ID, ORG_AUTOBOSS_INC_ID, 'V4.0', 'Assembly Robot 2000', 'ABV40-SN002');

    -- Parts (5)
    INSERT INTO parts (id, part_number, name, description, is_proprietary, is_consumable, manufacturer_delivery_time_days, local_supplier_delivery_time_days, image_urls) VALUES
    (PART_ENGINE_FILTER_ID, 'PN-001-A', 'Engine Air Filter', 'Standard air filter for combustion engines', FALSE, TRUE, NULL, 3, ARRAY['/static/images/default_part_filter.jpg']),
    (PART_CONTROL_UNIT_ID, 'PN-002-B', 'Central Control Unit', 'Advanced control unit for machine operations', TRUE, FALSE, 21, NULL, ARRAY['/static/images/default_part_control_unit.jpg']),
    (PART_HYDRAULIC_PUMP_ID, 'PN-003-C', 'Hydraulic Pump', 'High-pressure hydraulic pump assembly', TRUE, FALSE, 28, NULL, ARRAY['/static/images/default_part_hydraulic_pump.jpg']),
    (PART_SENSOR_MODULE_ID, 'PN-004-D', 'Proximity Sensor Module', 'Detects object presence and distance', FALSE, TRUE, NULL, 5, ARRAY['/static/images/default_part_sensor_module.jpg']),
    (PART_DRIVE_BELT_ID, 'PN-005-E', 'Drive Belt', 'Power transmission belt for motion systems', FALSE, TRUE, NULL, 2, ARRAY['/static/images/default_part_drive_belt.jpg']);

    -- Inventory (4 items per organization, total 20 items)
    -- Oraseas EE Inventory
    INSERT INTO inventory (organization_id, part_id, current_stock, minimum_stock_recommendation, reorder_threshold_set_by) VALUES
    (ORG_ORASEAS_EE_ID, PART_ENGINE_FILTER_ID, 150, 70, 'system'),
    (ORG_ORASEAS_EE_ID, PART_CONTROL_UNIT_ID, 25, 10, 'system'),
    (ORG_ORASEAS_EE_ID, PART_HYDRAULIC_PUMP_ID, 15, 7, 'user'),
    (ORG_ORASEAS_EE_ID, PART_SENSOR_MODULE_ID, 200, 100, 'system');

    -- Autoboss Inc Inventory
    INSERT INTO inventory (organization_id, part_id, current_stock, minimum_stock_recommendation, reorder_threshold_set_by) VALUES
    (ORG_AUTOBOSS_INC_ID, PART_ENGINE_FILTER_ID, 30, 15, 'user'),
    (ORG_AUTOBOSS_INC_ID, PART_SENSOR_MODULE_ID, 40, 20, 'system'),
    (ORG_AUTOBOSS_INC_ID, PART_DRIVE_BELT_ID, 50, 25, 'system'),
    (ORG_AUTOBOSS_INC_ID, PART_CONTROL_UNIT_ID, 5, 2, 'user');

    -- AutoParts Ltd Inventory (Supplier, but might have internal parts for maintenance)
    INSERT INTO inventory (organization_id, part_id, current_stock, minimum_stock_recommendation, reorder_threshold_set_by) VALUES
    (ORG_AUTOPARTS_LTD_ID, PART_ENGINE_FILTER_ID, 100, 50, 'system'),
    (ORG_AUTOPARTS_LTD_ID, PART_HYDRAULIC_PUMP_ID, 10, 5, 'user'),
    (ORG_AUTOPARTS_LTD_ID, PART_DRIVE_BELT_ID, 80, 40, 'system'),
    (ORG_AUTOPARTS_LTD_ID, PART_SENSOR_MODULE_ID, 70, 30, 'system');

    -- RoboMech Solutions Inventory
    INSERT INTO inventory (organization_id, part_id, current_stock, minimum_stock_recommendation, reorder_threshold_set_by) VALUES
    (ORG_CUSTOMER_B_ID, PART_ENGINE_FILTER_ID, 10, 5, 'user'),
    (ORG_CUSTOMER_B_ID, PART_DRIVE_BELT_ID, 20, 10, 'system'),
    (ORG_CUSTOMER_B_ID, PART_SENSOR_MODULE_ID, 5, 2, 'user'),
    (ORG_CUSTOMER_B_ID, PART_HYDRAULIC_PUMP_ID, 2, 1, 'system');

    -- Industrial Innovators Inventory
    INSERT INTO inventory (organization_id, part_id, current_stock, minimum_stock_recommendation, reorder_threshold_set_by) VALUES
    (ORG_CUSTOMER_C_ID, PART_CONTROL_UNIT_ID, 3, 1, 'user'),
    (ORG_CUSTOMER_C_ID, PART_HYDRAULIC_PUMP_ID, 1, 1, 'system'),
    (ORG_CUSTOMER_C_ID, PART_ENGINE_FILTER_ID, 8, 4, 'user'),
    (ORG_CUSTOMER_C_ID, PART_DRIVE_BELT_ID, 15, 7, 'system');

    -- Supplier Orders (3 total)
    INSERT INTO supplier_orders (id, ordering_organization_id, supplier_name, order_date, expected_delivery_date, status, notes) VALUES
    (SUPP_ORDER_1_ID, ORG_ORASEAS_EE_ID, 'AutoParts Ltd', NOW() - INTERVAL '7 days', NOW() + INTERVAL '14 days', 'Pending', 'Initial stock order from AutoParts'),
    (SUPP_ORDER_2_ID, ORG_ORASEAS_EE_ID, 'AutoParts Ltd', NOW() - INTERVAL '10 days', NOW() + INTERVAL '20 days', 'Shipped', 'Order for common parts from AutoParts'),
    (SUPP_ORDER_3_ID, ORG_ORASEAS_EE_ID, 'AutoParts Ltd', NOW() - INTERVAL '2 days', NOW() + INTERVAL '5 days', 'Pending', 'Urgent consumable order');

    -- Supplier Order Items (3 items per supplier order)
    INSERT INTO supplier_order_items (supplier_order_id, part_id, quantity, unit_price) VALUES
    (SUPP_ORDER_1_ID, PART_ENGINE_FILTER_ID, 50, 5.99),
    (SUPP_ORDER_1_ID, PART_DRIVE_BELT_ID, 30, 2.50),
    (SUPP_ORDER_1_ID, PART_SENSOR_MODULE_ID, 20, 15.75),

    (SUPP_ORDER_2_ID, PART_CONTROL_UNIT_ID, 5, 250.00),
    (SUPP_ORDER_2_ID, PART_HYDRAULIC_PUMP_ID, 2, 800.00),
    (SUPP_ORDER_2_ID, PART_ENGINE_FILTER_ID, 10, 6.00), -- Another filter for testing

    (SUPP_ORDER_3_ID, PART_SENSOR_MODULE_ID, 100, 8.20),
    (SUPP_ORDER_3_ID, PART_DRIVE_BELT_ID, 75, 12.00),
    (SUPP_ORDER_3_ID, PART_HYDRAULIC_PUMP_ID, 1, 850.00);

END $$;
