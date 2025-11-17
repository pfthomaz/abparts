# Step-by-Step Database Migration Guide

## Method 1: Using pgAdmin (Recommended)

### Step 1: Open pgAdmin
1. Go to: **http://localhost:8080**
2. Login with:
   - Email: `admin@admin.com`
   - Password: `admin`

### Step 2: Connect to Database
1. In the left panel, expand **Servers**
2. Expand **PostgreSQL 15**
3. Expand **Databases**
4. Click on **abparts_dev**

### Step 3: Open Query Tool
1. Right-click on **abparts_dev**
2. Select **Query Tool**
3. A new tab will open with a SQL editor

### Step 4: Run Migration SQL
Copy and paste this EXACT SQL into the query editor:

```sql
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

-- Update existing organizations with default country
UPDATE organizations SET country = 'GR' WHERE country IS NULL;

-- Create index for performance
CREATE INDEX IF NOT EXISTS idx_organizations_country ON organizations(country);

-- Verify the migration worked
SELECT 'Migration completed successfully!' as status;
SELECT name, organization_type, country FROM organizations ORDER BY name;
```

### Step 5: Execute
1. Click the **Execute** button (▶️) or press **F5**
2. You should see messages like:
   - "Created countrycode enum" or "countrycode enum already exists"
   - "Added country column" or "country column already exists"
   - "Migration completed successfully!"

### Step 6: Verify Success
You should see a table showing your organizations with the new country column.

## Method 2: Using Docker Command Line

If pgAdmin doesn't work, try this:

1. Save the SQL to a file called `migration.sql`
2. Run this command:

```bash
docker-compose exec db psql -U abparts_user -d abparts_dev -c "
DO \$\$ 
BEGIN
    CREATE TYPE countrycode AS ENUM ('GR', 'UK', 'NO', 'CA', 'NZ', 'TR');
EXCEPTION
    WHEN duplicate_object THEN null;
END \$\$;

ALTER TABLE organizations ADD COLUMN IF NOT EXISTS country countrycode;
UPDATE organizations SET country = 'GR' WHERE country IS NULL;
CREATE INDEX IF NOT EXISTS idx_organizations_country ON organizations(country);
"
```

## After Migration: Enable Country Fields

Once the migration is successful, uncomment these lines in the code:

**In backend/app/models.py:**
```python
country = Column(Enum(CountryCode), nullable=True)  # Uncomment this
```

**In backend/app/schemas.py:**
```python
country: Optional[CountryEnum] = None  # Uncomment this
```

The API will restart automatically and you'll see the new countries!