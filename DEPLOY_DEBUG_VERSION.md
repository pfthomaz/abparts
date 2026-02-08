# Deploy Debug Version - See What's Wrong

I've added debug logging to see what store name is being passed to the transaction.

## Deploy Now

```bash
# On production server
cd ~/abparts
git pull origin main
docker compose -f docker-compose.prod.yml build --no-cache web
docker compose -f docker-compose.prod.yml up -d web
```

## Check Console Output

1. Open https://abparts.oraseas.com
2. Press F12 (DevTools)
3. Go to Console tab
4. Hard refresh (Cmd+Shift+R)
5. Login

## Look For This Line

```
[IndexedDB] DEBUG: Attempting transaction for store: ??? Available stores: [...]
```

**Copy and paste the ENTIRE console output here** - especially the DEBUG line that shows:
- What store name is being passed
- What stores are available

This will tell us exactly what's wrong.
