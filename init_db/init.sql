-- init.sql
-- This script will be executed by PostgreSQL when the container starts for the first time
-- (due to the volume mount ./init_db:/docker-entrypoint-initdb.d in docker-compose.yml)

-- Drop tables if they exist to ensure a clean slate during development
-- Order matters for foreign key dependencies, dropping children before parents.
-- CASCADE also helps to drop dependent objects (like foreign key constraints) automatically.
DROP TABLE IF EXISTS part_usage CASCADE;
DROP TABLE IF EXISTS customer_order_items CASCADE;
DROP TABLE IF EXISTS customer_orders CASCADE;
DROP TABLE IF EXISTS supplier_order_items CASCADE;
DROP TABLE IF EXISTS supplier_orders CASCADE;
DROP TABLE IF EXISTS inventory CASCADE;
DROP TABLE IF EXISTS users CASCADE;
DROP TABLE IF EXISTS parts CASCADE;
DROP TABLE IF EXISTS organizations CASCADE;

-- Enable UUID-OSSP extension for UUID generation
-- This extension needs to be created in the database where you want to use uuid_generate_v4().
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

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
    password_hash TEXT NOT NULL, -- In a real app, this would be securely hashed
    email VARCHAR(255) NOT NULL UNIQUE,
    name VARCHAR(255),
    role VARCHAR(50) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    FOREIGN KEY (organization_id) REFERENCES organizations(id)
);

-- 3. parts Table
CREATE TABLE parts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    part_number VARCHAR(255) NOT NULL UNIQUE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    is_proprietary BOOLEAN NOT NULL DEFAULT FALSE,
    is_consumable BOOLEAN NOT NULL DEFAULT FALSE,
    manufacturer_delivery_time_days INTEGER,
    local_supplier_delivery_time_days INTEGER,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- 4. inventory Table
CREATE TABLE inventory (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID NOT NULL,
    part_id UUID NOT NULL,
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

-- 5. supplier_orders Table
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

-- 6. supplier_order_items Table
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

-- 7. customer_orders Table
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

-- 8. customer_order_items Table
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

-- 9. part_usage Table
CREATE TABLE part_usage (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    customer_organization_id UUID NOT NULL,
    part_id UUID NOT NULL,
    usage_date TIMESTAMP WITH TIME ZONE NOT NULL,
    quantity_used INTEGER NOT NULL DEFAULT 1,
    machine_id VARCHAR(255),
    recorded_by_user_id UUID,
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    FOREIGN KEY (customer_organization_id) REFERENCES organizations(id),
    FOREIGN KEY (part_id) REFERENCES parts(id),
    FOREIGN KEY (recorded_by_user_id) REFERENCES users(id)
);

-- Seed initial data for organizations table (10 organizations)
INSERT INTO organizations (name, type, address, contact_info) VALUES
('Oraseas EE', 'Warehouse', '123 Main St, Lisbon, Portugal', 'info@oraseas.com'),
('NZ Manufacturer', 'Supplier', 'Manufacturer HQ, Auckland, New Zealand', 'sales@nzman.com'),
('AutoBoss Customer A', 'Customer', '456 Oak Ave, Porto, Portugal', 'contact@customera.com'),
('Global Repair Solutions', 'Customer', '789 Pine Rd, Coimbra, Portugal', 'support@globalrepair.com'),
('MechFix Services', 'Customer', '101 Tech Way, Faro, Portugal', 'info@mechfix.com'),
('Prime Auto Care', 'Customer', '202 Repair Blvd, Aveiro, Portugal', 'contact@primeauto.com'),
('Swift Mechanics', 'Customer', '303 Gear St, Braga, Portugal', 'swift@mechanics.com'),
('Elite Repair Group', 'Customer', '404 Engine Ln, Setúbal, Portugal', 'elite@repair.com'),
('Innovate Machines', 'Customer', '505 Circuit Dr, Leiria, Portugal', 'innovate@machines.com'),
('Reliable AutoTech', 'Customer', '606 Spanner Sq, Viseu, Portugal', 'info@reliable.com');

-- Seed initial data for parts table (20 parts)
INSERT INTO parts (part_number, name, description, is_proprietary, is_consumable, manufacturer_delivery_time_days, local_supplier_delivery_time_days) VALUES
('AB-ENG-001', 'AutoBoss Engine Filter', 'High-performance engine air filter', FALSE, TRUE, NULL, 3),
('AB-TRN-005', 'Transmission Fluid Pump', 'Proprietary fluid pump for AutoBoss transmission', TRUE, FALSE, 20, NULL),
('AB-BRA-010', 'Brake Pad Set (Front)', 'Standard front brake pads', FALSE, TRUE, NULL, 2),
('AB-ELE-015', 'Control Unit Processor', 'Proprietary main control unit processor', TRUE, FALSE, 30, NULL),
('AB-SUS-020', 'Suspension Bushing Kit', 'Complete kit for suspension bushings', FALSE, FALSE, NULL, 5),
('AB-BAT-025', 'High-Capacity Battery', 'Rechargeable battery for electrical systems', FALSE, FALSE, NULL, 7),
('AB-HYD-030', 'Hydraulic Hose Assembly', 'Heavy-duty hydraulic hose', FALSE, TRUE, NULL, 4),
('AB-COO-035', 'Coolant Pump Impeller', 'Proprietary impeller for cooling system pump', TRUE, FALSE, 25, NULL),
('AB-FIL-040', 'Fuel Injector Nozzle', 'Precision fuel injector nozzle', FALSE, FALSE, NULL, 6),
('AB-EXH-045', 'Exhaust Manifold Gasket', 'Heat-resistant exhaust gasket', FALSE, TRUE, NULL, 2),
('AB-TYR-050', 'All-Terrain Tire', 'Durable all-terrain tire', FALSE, FALSE, NULL, 8),
('AB-SEN-055', 'Oxygen Sensor', 'Exhaust oxygen sensor', FALSE, FALSE, NULL, 3),
('AB-DRV-060', 'Drive Shaft Coupling', 'Flexible coupling for drive shaft', FALSE, FALSE, NULL, 5),
('AB-LUB-065', 'Engine Oil Seal Kit', 'Comprehensive oil seal kit for engine', FALSE, TRUE, NULL, 2),
('AB-STE-070', 'Steering Rack Bushing', 'Bushing for power steering rack', FALSE, FALSE, NULL, 4),
('AB-WIP-075', 'Windshield Wiper Blades', 'Premium wiper blades', FALSE, TRUE, NULL, 1),
('AB-FAN-080', 'Radiator Fan Motor', 'Motor for cooling fan assembly', FALSE, FALSE, NULL, 6),
('AB-LGT-085', 'LED Headlight Assembly', 'Complete LED headlight unit', FALSE, FALSE, NULL, 10),
('AB-ACC-090', 'Accelerator Pedal Sensor', 'Proprietary sensor for accelerator pedal', TRUE, FALSE, 22, NULL),
('AB-DOC-095', 'Maintenance Manual', 'Digital maintenance manual access code', FALSE, FALSE, NULL, 1);


-- Seed initial data for users table (1 user per organization)
INSERT INTO users (organization_id, username, password_hash, email, name, role)
SELECT
    o.id AS organization_id,
    LOWER(REPLACE(o.name, ' ', '')) || '_user' AS username,
    -- CORRECTED: password_hash to match the stub logic (plain_password + "_hashed")
    'password_123_hashed' AS password_hash,
    LOWER(REPLACE(o.name, ' ', '')) || '@example.com' AS email,
    CASE
        WHEN o.type = 'Warehouse' THEN 'Oraseas Admin'
        WHEN o.type = 'Supplier' THEN 'Supplier Contact'
        ELSE o.name || ' User'
    END AS name,
    CASE
        WHEN o.type = 'Warehouse' THEN 'Oraseas Admin'
        WHEN o.type = 'Supplier' THEN 'Supplier User'
        ELSE 'Customer Admin'
    END AS role
FROM organizations o;


-- Seed initial data for inventory table (approx 3-5 items per relevant organization)
-- Using subqueries to get organization and part IDs dynamically
-- Oraseas EE Inventory
INSERT INTO inventory (organization_id, part_id, current_stock, minimum_stock_recommendation, reorder_threshold_set_by) VALUES
((SELECT id FROM organizations WHERE name = 'Oraseas EE'), (SELECT id FROM parts WHERE part_number = 'AB-ENG-001'), 150, 100, 'system'),
((SELECT id FROM organizations WHERE name = 'Oraseas EE'), (SELECT id FROM parts WHERE part_number = 'AB-TRN-005'), 50, 20, 'system'),
((SELECT id FROM organizations WHERE name = 'Oraseas EE'), (SELECT id FROM parts WHERE part_number = 'AB-BRA-010'), 200, 150, 'system'),
((SELECT id FROM organizations WHERE name = 'Oraseas EE'), (SELECT id FROM parts WHERE part_number = 'AB-ELE-015'), 30, 10, 'system'),
((SELECT id FROM organizations WHERE name = 'Oraseas EE'), (SELECT id FROM parts WHERE part_number = 'AB-SUS-020'), 80, 50, 'system'),
((SELECT id FROM organizations WHERE name = 'Oraseas EE'), (SELECT id FROM parts WHERE part_number = 'AB-BAT-025'), 60, 40, 'system'),
((SELECT id FROM organizations WHERE name = 'Oraseas EE'), (SELECT id FROM parts WHERE part_number = 'AB-HYD-030'), 120, 80, 'system'),
((SELECT id FROM organizations WHERE name = 'Oraseas EE'), (SELECT id FROM parts WHERE part_number = 'AB-COO-035'), 40, 15, 'system'),
((SELECT id FROM organizations WHERE name = 'Oraseas EE'), (SELECT id FROM parts WHERE part_number = 'AB-FIL-040'), 90, 60, 'system'),
((SELECT id FROM organizations WHERE name = 'Oraseas EE'), (SELECT id FROM parts WHERE part_number = 'AB-EXH-045'), 180, 130, 'system');

-- AutoBoss Customer A Inventory
INSERT INTO inventory (organization_id, part_id, current_stock, minimum_stock_recommendation, reorder_threshold_set_by) VALUES
((SELECT id FROM organizations WHERE name = 'AutoBoss Customer A'), (SELECT id FROM parts WHERE part_number = 'AB-ENG-001'), 5, 3, 'system'),
((SELECT id FROM organizations WHERE name = 'AutoBoss Customer A'), (SELECT id FROM parts WHERE part_number = 'AB-TRN-005'), 2, 1, 'system'),
((SELECT id FROM organizations WHERE name = 'AutoBoss Customer A'), (SELECT id FROM parts WHERE part_number = 'AB-BRA-010'), 8, 5, 'system'),
((SELECT id FROM organizations WHERE name = 'AutoBoss Customer A'), (SELECT id FROM parts WHERE part_number = 'AB-SUS-020'), 3, 2, 'system'),
((SELECT id FROM organizations WHERE name = 'AutoBoss Customer A'), (SELECT id FROM parts WHERE part_number = 'AB-EXH-045'), 10, 7, 'system');

-- Global Repair Solutions Inventory
INSERT INTO inventory (organization_id, part_id, current_stock, minimum_stock_recommendation, reorder_threshold_set_by) VALUES
((SELECT id FROM organizations WHERE name = 'Global Repair Solutions'), (SELECT id FROM parts WHERE part_number = 'AB-ELE-015'), 1, 1, 'user'),
((SELECT id FROM organizations WHERE name = 'Global Repair Solutions'), (SELECT id FROM parts WHERE part_number = 'AB-BAT-025'), 4, 2, 'system'),
((SELECT id FROM organizations WHERE name = 'Global Repair Solutions'), (SELECT id FROM parts WHERE part_number = 'AB-HYD-030'), 7, 5, 'system'),
((SELECT id FROM organizations WHERE name = 'Global Repair Solutions'), (SELECT id FROM parts WHERE part_number = 'AB-FIL-040'), 6, 4, 'system');

-- MechFix Services Inventory
INSERT INTO inventory (organization_id, part_id, current_stock, minimum_stock_recommendation, reorder_threshold_set_by) VALUES
((SELECT id FROM organizations WHERE name = 'MechFix Services'), (SELECT id FROM parts WHERE part_number = 'AB-SEN-055'), 2, 1, 'system'),
((SELECT id FROM organizations WHERE name = 'MechFix Services'), (SELECT id FROM parts WHERE part_number = 'AB-DRV-060'), 1, 1, 'user'),
((SELECT id FROM organizations WHERE name = 'MechFix Services'), (SELECT id FROM parts WHERE part_number = 'AB-WIP-075'), 15, 10, 'system');

-- Prime Auto Care Inventory
INSERT INTO inventory (organization_id, part_id, current_stock, minimum_stock_recommendation, reorder_threshold_set_by) VALUES
((SELECT id FROM organizations WHERE name = 'Prime Auto Care'), (SELECT id FROM parts WHERE part_number = 'AB-LGT-085'), 1, 1, 'system'),
((SELECT id FROM organizations WHERE name = 'Prime Auto Care'), (SELECT id FROM parts WHERE part_number = 'AB-ACC-090'), 1, 1, 'user');

-- Swift Mechanics Inventory
INSERT INTO inventory (organization_id, part_id, current_stock, minimum_stock_recommendation, reorder_threshold_set_by) VALUES
((SELECT id FROM organizations WHERE name = 'Swift Mechanics'), (SELECT id FROM parts WHERE part_number = 'AB-TYR-050'), 4, 2, 'system'),
((SELECT id FROM organizations WHERE name = 'Swift Mechanics'), (SELECT id FROM parts WHERE part_number = 'AB-FAN-080'), 2, 1, 'system');

-- Elite Repair Group Inventory
INSERT INTO inventory (organization_id, part_id, current_stock, minimum_stock_recommendation, reorder_threshold_set_by) VALUES
((SELECT id FROM organizations WHERE name = 'Elite Repair Group'), (SELECT id FROM parts WHERE part_number = 'AB-ENG-001'), 3, 2, 'system'),
((SELECT id FROM organizations WHERE name = 'Elite Repair Group'), (SELECT id FROM parts WHERE part_number = 'AB-TRN-005'), 1, 1, 'user');

-- Innovate Machines Inventory
INSERT INTO inventory (organization_id, part_id, current_stock, minimum_stock_recommendation, reorder_threshold_set_by) VALUES
((SELECT id FROM organizations WHERE name = 'Innovate Machines'), (SELECT id FROM parts WHERE part_number = 'AB-LUB-065'), 7, 5, 'system'),
((SELECT id FROM organizations WHERE name = 'Innovate Machines'), (SELECT id FROM parts WHERE part_number = 'AB-STE-070'), 3, 2, 'system');

-- Reliable AutoTech Inventory
INSERT INTO inventory (organization_id, part_id, current_stock, minimum_stock_recommendation, reorder_threshold_set_by) VALUES
((SELECT id FROM organizations WHERE name = 'Reliable AutoTech'), (SELECT id FROM parts WHERE part_number = 'AB-COO-035'), 2, 1, 'system'),
((SELECT id FROM organizations WHERE name = 'Reliable AutoTech'), (SELECT id FROM parts WHERE part_number = 'AB-DOC-095'), 1, 1, 'user');
