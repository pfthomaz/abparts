-- Quick migration to add country support
-- Run this in pgAdmin Query Tool

-- Create country enum (ignore error if already exists)
DO $$ 
BEGIN
    CREATE TYPE countrycode AS ENUM ('GR', 'UK', 'NO', 'CA', 'NZ', 'TR');
EXCEPTION
    WHEN duplicate_object THEN 
        RAISE NOTICE 'countrycode enum already exists';
END $$;

-- Add country column (ignore error if already exists)
DO $$ 
BEGIN
    ALTER TABLE organizations ADD COLUMN country countrycode;
EXCEPTION
    WHEN duplicate_column THEN 
        RAISE NOTICE 'country column already exists';
END $$;

-- Update existing organizations with default country
UPDATE organizations SET country = 'GR' WHERE country IS NULL;

-- Create index for performance
CREATE INDEX IF NOT EXISTS idx_organizations_country ON organizations(country);

-- Verify the changes
SELECT 'Migration completed successfully' as status;
SELECT name, organization_type, country FROM organizations ORDER BY name;