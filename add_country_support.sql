-- Add country support to organizations table
-- This migration adds the country field and creates the country enum

-- Create the country enum type
DO $$ BEGIN
    CREATE TYPE countrycode AS ENUM ('GR', 'UK', 'NO', 'CA', 'NZ', 'TR');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- Add country column to organizations table
DO $$ BEGIN
    ALTER TABLE organizations ADD COLUMN country countrycode;
EXCEPTION
    WHEN duplicate_column THEN 
        RAISE NOTICE 'Column country already exists in organizations table';
END $$;

-- Update existing organizations with default countries based on business logic
UPDATE organizations 
SET country = 'GR' 
WHERE country IS NULL 
  AND organization_type IN ('oraseas_ee', 'bossaqua');

-- Add comment to the column
COMMENT ON COLUMN organizations.country IS 'Country code for the organization location';

-- Create index for country-based queries
CREATE INDEX IF NOT EXISTS idx_organizations_country ON organizations(country);

-- Display current organizations with their countries
SELECT 
    name, 
    organization_type, 
    country,
    CASE 
        WHEN country IS NULL THEN 'No country set'
        ELSE 'Country set'
    END as country_status
FROM organizations 
ORDER BY organization_type, name;