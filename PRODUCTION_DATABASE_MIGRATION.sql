-- ============================================================================
-- ABParts Production Database Migration Script
-- Date: November 21, 2024
-- Description: Database changes from the last 2 weeks
-- ============================================================================

-- IMPORTANT: Backup your production database before running this script!
-- pg_dump -U your_user -d your_database > backup_$(date +%Y%m%d_%H%M%S).sql

-- ============================================================================
-- 1. ADD IMAGE/PHOTO COLUMNS
-- ============================================================================

-- Add profile photo URL to users table
ALTER TABLE users 
ADD COLUMN IF NOT EXISTS profile_photo_url VARCHAR(500);

COMMENT ON COLUMN users.profile_photo_url IS 'URL path to user profile photo';

-- Add logo URL to organizations table
ALTER TABLE organizations 
ADD COLUMN IF NOT EXISTS logo_url VARCHAR(500);

COMMENT ON COLUMN organizations.logo_url IS 'URL path to organization logo';

-- ============================================================================
-- 2. ADD SHIPPED_BY_USER_ID TO CUSTOMER_ORDERS
-- ============================================================================

-- Add shipped_by_user_id column to track who marked order as shipped
ALTER TABLE customer_orders 
ADD COLUMN IF NOT EXISTS shipped_by_user_id UUID REFERENCES users(id);

COMMENT ON COLUMN customer_orders.shipped_by_user_id IS 'User who marked the order as shipped';

-- ============================================================================
-- 3. VERIFY EXISTING TABLES AND COLUMNS
-- ============================================================================

-- These tables should already exist from previous migrations:
-- - users (with all user management fields)
-- - organizations (with organization_type enum)
-- - machines (with customer_organization_id, name, serial_number)
-- - warehouses (with organization_id)
-- - parts (with all part fields)
-- - inventory (with current_stock, warehouse_id, part_id)
-- - transactions (with transaction_type, machine_id, from/to warehouse)
-- - customer_orders (with status, shipped_date)
-- - machine_hours (for tracking machine usage)
-- - part_usage_records (for tracking part consumption)
-- - part_usage_items (items in part usage records)

-- ============================================================================
-- 4. VERIFY ENUMS
-- ============================================================================

-- Verify organization_type enum has all values
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_enum 
        WHERE enumlabel = 'oraseas_ee' 
        AND enumtypid = (SELECT oid FROM pg_type WHERE typname = 'organizationtype')
    ) THEN
        ALTER TYPE organizationtype ADD VALUE IF NOT EXISTS 'oraseas_ee';
    END IF;
    
    IF NOT EXISTS (
        SELECT 1 FROM pg_enum 
        WHERE enumlabel = 'bossaqua' 
        AND enumtypid = (SELECT oid FROM pg_type WHERE typname = 'organizationtype')
    ) THEN
        ALTER TYPE organizationtype ADD VALUE IF NOT EXISTS 'bossaqua';
    END IF;
    
    IF NOT EXISTS (
        SELECT 1 FROM pg_enum 
        WHERE enumlabel = 'customer' 
        AND enumtypid = (SELECT oid FROM pg_type WHERE typname = 'organizationtype')
    ) THEN
        ALTER TYPE organizationtype ADD VALUE IF NOT EXISTS 'customer';
    END IF;
    
    IF NOT EXISTS (
        SELECT 1 FROM pg_enum 
        WHERE enumlabel = 'supplier' 
        AND enumtypid = (SELECT oid FROM pg_type WHERE typname = 'organizationtype')
    ) THEN
        ALTER TYPE organizationtype ADD VALUE IF NOT EXISTS 'supplier';
    END IF;
END$$;

-- ============================================================================
-- 5. CREATE STATIC FILES DIRECTORY (Run on server, not in database)
-- ============================================================================

-- Run these commands on your production server:
-- mkdir -p /path/to/backend/static/images
-- chmod 755 /path/to/backend/static/images
-- chown www-data:www-data /path/to/backend/static/images  # or your web server user

-- ============================================================================
-- 6. VERIFICATION QUERIES
-- ============================================================================

-- Verify new columns exist
SELECT 
    column_name, 
    data_type, 
    character_maximum_length,
    is_nullable
FROM information_schema.columns 
WHERE table_name IN ('users', 'organizations', 'customer_orders')
    AND column_name IN ('profile_photo_url', 'logo_url', 'shipped_by_user_id')
ORDER BY table_name, column_name;

-- Check if any users or organizations already have photos/logos
SELECT 
    'users' as table_name,
    COUNT(*) as total_records,
    COUNT(profile_photo_url) as records_with_photo
FROM users
UNION ALL
SELECT 
    'organizations' as table_name,
    COUNT(*) as total_records,
    COUNT(logo_url) as records_with_logo
FROM organizations;

-- ============================================================================
-- ROLLBACK SCRIPT (if needed)
-- ============================================================================

-- ONLY RUN THIS IF YOU NEED TO ROLLBACK THE CHANGES!
-- 
-- ALTER TABLE users DROP COLUMN IF EXISTS profile_photo_url;
-- ALTER TABLE organizations DROP COLUMN IF EXISTS logo_url;
-- ALTER TABLE customer_orders DROP COLUMN IF EXISTS shipped_by_user_id;

-- ============================================================================
-- END OF MIGRATION SCRIPT
-- ============================================================================
