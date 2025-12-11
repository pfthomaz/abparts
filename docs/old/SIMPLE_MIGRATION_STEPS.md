# Simple Migration Steps (Docker Method)

Since pgAdmin isn't working, let's use Docker directly:

## Method 1: Single Command Migration

Run this command in your terminal (in the abparts directory):

```bash
docker-compose exec db psql -U abparts_user -d abparts_dev -c "
DO \$\$ 
BEGIN
    CREATE TYPE countrycode AS ENUM ('GR', 'UK', 'NO', 'CA', 'NZ', 'TR');
EXCEPTION
    WHEN duplicate_object THEN null;
END \$\$;

DO \$\$ 
BEGIN
    ALTER TABLE organizations ADD COLUMN country countrycode;
EXCEPTION
    WHEN duplicate_column THEN null;
END \$\$;

UPDATE organizations SET country = 'GR' WHERE country IS NULL;
CREATE INDEX IF NOT EXISTS idx_organizations_country ON organizations(country);
SELECT 'Migration completed!' as result;
"
```

## Method 2: Step by Step Commands

If the above doesn't work, try these individual commands:

### Step 1: Create the enum
```bash
docker-compose exec db psql -U abparts_user -d abparts_dev -c "CREATE TYPE countrycode AS ENUM ('GR', 'UK', 'NO', 'CA', 'NZ', 'TR');"
```

### Step 2: Add the column
```bash
docker-compose exec db psql -U abparts_user -d abparts_dev -c "ALTER TABLE organizations ADD COLUMN country countrycode;"
```

### Step 3: Update existing data
```bash
docker-compose exec db psql -U abparts_user -d abparts_dev -c "UPDATE organizations SET country = 'GR' WHERE country IS NULL;"
```

### Step 4: Create index
```bash
docker-compose exec db psql -U abparts_user -d abparts_dev -c "CREATE INDEX idx_organizations_country ON organizations(country);"
```

### Step 5: Verify
```bash
docker-compose exec db psql -U abparts_user -d abparts_dev -c "SELECT name, organization_type, country FROM organizations;"
```

## Expected Output

You should see:
- "CREATE TYPE" (for the enum)
- "ALTER TABLE" (for the column)
- "UPDATE X" (where X is the number of organizations updated)
- "CREATE INDEX" (for the index)
- A table showing your organizations with country values

## After Success

Once you see the migration completed successfully, let me know and I'll:
1. Uncomment the country fields in the code
2. The API will restart automatically
3. You'll see the new countries in the frontend dropdown

## If You Get Errors

Common errors and solutions:
- **"type already exists"** → That's OK, means it's already created
- **"column already exists"** → That's OK, means it's already added
- **"permission denied"** → Make sure Docker is running
- **"database not found"** → Check that the containers are running with `docker-compose ps`