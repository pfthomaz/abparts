# Fix Protocols Caching - Quick Start

## The Problem
Protocols are not being cached in IndexedDB because the code needs to be deployed to production.

## The Solution
The fix is already in the repository. You just need to deploy it.

## Run This on Production Server

```bash
cd ~/abparts
./deploy_offline_protocols_fix.sh
```

## Then in Your Browser

1. Go to https://abparts.oraseas.com
2. Press F12 (open DevTools)
3. Go to: Application > Storage > IndexedDB
4. Right-click on "ABPartsOfflineDB" > Delete database
5. Press Cmd+Shift+R (hard refresh)
6. Login
7. Check Console - you should see:
   ```
   [OfflinePreloader] ✓ Cached X protocols
   ```
8. Check IndexedDB > ABPartsOfflineDB > protocols - should have data

## That's It!

The protocols will now cache properly and work offline.

---

**Need more details?** See `OFFLINE_PROTOCOLS_CACHING_FIX.md`
