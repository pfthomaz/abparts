# Quick Fix for Login Error

The login error is happening because the database doesn't have the new columns yet. Here's how to fix it:

## Option 1: Using Docker Compose (Recommended)

Run this command in your terminal:

```bash
docker-compose exec db psql -U abparts_user -d abparts_dev -c "ALTER TABLE organizations ADD COLUMN IF NOT EXISTS logo_url VARCHAR(500);"

docker-compose exec db psql -U abparts_user -d abparts_dev -c "ALTER TABLE users ADD COLUMN IF NOT EXISTS profile_photo_url VARCHAR(500);"
```

## Option 2: Using the SQL file

```bash
docker-compose exec -T db psql -U abparts_user -d abparts_dev < add_images_migration.sql
```

## Option 3: Manual SQL

1. Connect to your database:
```bash
docker-compose exec db psql -U abparts_user -d abparts_dev
```

2. Run these SQL commands:
```sql
ALTER TABLE organizations ADD COLUMN IF NOT EXISTS logo_url VARCHAR(500);
ALTER TABLE users ADD COLUMN IF NOT EXISTS profile_photo_url VARCHAR(500);
```

3. Type `\q` to exit

## After Running Migration

Restart the API container:
```bash
docker-compose restart api
```

Then try logging in again. The error should be resolved!

## Verify Migration

To verify the columns were added:
```bash
docker-compose exec db psql -U abparts_user -d abparts_dev -c "\d users"
docker-compose exec db psql -U abparts_user -d abparts_dev -c "\d organizations"
```

You should see `logo_url` in the organizations table and `profile_photo_url` in the users table.
