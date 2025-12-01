#!/bin/bash
echo "🗄️  Running Database Migration via Docker..."
echo "=" * 50

# Run the migration SQL directly through Docker
docker-compose exec db psql -U abparts_user -d abparts_dev << 'EOF'
-- Create country enum
DO $$ 
BEGIN
    CREATE TYPE countrycode AS ENUM ('GR', 'UK', 'NO', 'CA', 'NZ', 'TR');
    RAISE NOTICE 'Created countrycode enum';
EXCEPTION
    WHEN duplicate_object THEN 
        RAISE NOTICE 'countrycode enum already exists';
END $$;

-- Add country column
DO $$ 
BEGIN
    ALTER TABLE organizations ADD COLUMN country countrycode;
    RAISE NOTICE 'Added country column';
EXCEPTION
    WHEN duplicate_column THEN 
        RAISE NOTICE 'country column already exists';
END $$;

-- Update existing organizations
UPDATE organizations SET country = 'GR' WHERE country IS NULL;

-- Create index
CREATE INDEX IF NOT EXISTS idx_organizations_country ON organizations(country);

-- Verify success
SELECT 'Migration completed successfully!' as status;
SELECT name, organization_type, country FROM organizations ORDER BY name;
EOF

echo "Migration completed!"