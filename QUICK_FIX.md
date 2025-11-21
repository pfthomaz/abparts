# QUICK FIX - Run This Now

The login error is because the database columns don't exist. Here's the fastest way to fix it:

## Step 1: Add the columns manually

Open a new terminal and run these commands ONE AT A TIME:

```bash
docker-compose exec db psql -U abparts_user abparts_dev
```

Then in the PostgreSQL prompt, run:

```sql
ALTER TABLE organizations ADD COLUMN logo_url VARCHAR(500);
ALTER TABLE users ADD COLUMN profile_photo_url VARCHAR(500);
\q
```

## Step 2: Restart the API

```bash
docker-compose restart api
```

## Step 3: Test login

Try logging in again. It should work now.

## If you still get errors:

Check if the columns were actually added:

```bash
docker-compose exec db psql -U abparts_user abparts_dev -c "\d users"
```

Look for `profile_photo_url` in the output.

```bash
docker-compose exec db psql -U abparts_user abparts_dev -c "\d organizations"
```

Look for `logo_url` in the output.
