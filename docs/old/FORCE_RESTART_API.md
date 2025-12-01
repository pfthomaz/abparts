# Force Restart API to Load New Code

The API container might be using cached Python bytecode. Here's how to force it to reload:

## Option 1: Stop and Start (Recommended)

```bash
cd abparts
docker-compose stop api
docker-compose start api
```

## Option 2: Recreate the Container

```bash
cd abparts
docker-compose up -d --force-recreate api
```

## Option 3: Full Rebuild (if nothing else works)

```bash
cd abparts
docker-compose down
docker-compose up -d --build
```

## After Restarting

1. Wait 10 seconds for the API to fully start
2. Refresh your browser (F5)
3. Check the console logs again

## Verify the API is Running

```bash
docker-compose ps
```

You should see the `api` container with status "Up".

## Check API Logs

```bash
docker-compose logs api --tail 50
```

Look for any errors during startup.

## Test the Endpoint Directly

In your browser, go to:
```
http://localhost:8000/docs
```

Then:
1. Click on `/users/me/` endpoint
2. Click "Try it out"
3. Click "Execute"
4. Look at the response - it should include an `organization` object

If you see the organization in the Swagger docs but not in your app, the issue is with the frontend caching.
