# Database Migration Instructions

## Current Status
✅ **Organizations page is working** - Country field temporarily disabled
✅ **Countries endpoint updated** - Will return new countries after migration
✅ **Configuration updated** - New countries in system config

## To Enable New Countries (UK, NO, CA, NZ, TR)

### Option 1: Using pgAdmin (Recommended)

1. **Open pgAdmin**: http://localhost:8080
2. **Connect to database**: abparts_dev
3. **Open Query Tool** (Tools → Query Tool)
4. **Copy and paste this SQL**:

```sql
-- Create country enum
DO $$ 
BEGIN
    CREATE TYPE countrycode AS ENUM ('GR', 'UK', 'NO', 'CA', 'NZ', 'TR');
EXCEPTION
    WHEN duplicate_object THEN 
        RAISE NOTICE 'countrycode enum already exists';
END $$;

-- Add country column
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

-- Verify the migration
SELECT 'Migration completed successfully!' as status;
```

5. **Execute the query** (F5 or Execute button)
6. **Verify success** - Should see "Migration completed successfully!"

### Option 2: Using Docker Command Line

```bash
docker-compose exec db psql -U abparts_user -d abparts_dev -f /path/to/quick_migration.sql
```

## After Migration

1. **Uncomment country fields** in the code:
   - In `backend/app/models.py`: Uncomment the country Column
   - In `backend/app/schemas.py`: Uncomment the country field
2. **API will restart automatically**
3. **Frontend will show new countries**:
   - Greece (GR)
   - United Kingdom (UK) 
   - Norway (NO)
   - Canada (CA)
   - New Zealand (NZ)
   - Turkey (TR)

## Verification

Test the countries endpoint:
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" http://localhost:8000/organizations/countries
```

Should return: `["GR", "UK", "NO", "CA", "NZ", "TR"]`

## Rollback (if needed)

If something goes wrong:
```sql
-- Remove country column
ALTER TABLE organizations DROP COLUMN IF EXISTS country;
-- Remove enum type
DROP TYPE IF EXISTS countrycode;
```