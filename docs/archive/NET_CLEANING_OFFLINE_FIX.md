# Net Cleaning Records Offline Fix

## Problem

When trying to register net cleaning records offline, the following error occurred:
```
Cannot fetch machines offline without user context
```

## Root Cause

The `NetCleaningRecords` page was calling `machinesService.getMachines()` without passing the required `userContext` parameter:

```javascript
// BEFORE (BROKEN):
const [recordsData, netsData, farmSitesData, machinesData] = await Promise.all([
  netCleaningRecordsService.getCleaningRecords(),
  netsService.getNets(),
  farmSitesService.getFarmSites(),
  machinesService.getMachines()  // ❌ Missing userContext!
]);
```

The `getMachines()` function requires `userContext` for:
1. **Security**: Filtering cached data by organization
2. **Offline support**: Reading from IndexedDB with proper user scoping

## Solution

Added `userContext` creation and passed it to `getMachines()`:

```javascript
// AFTER (FIXED):
const userContext = {
  userId: user.id,
  organizationId: user.organization_id,
  isSuperAdmin: user.role === 'super_admin'
};

const [recordsData, netsData, farmSitesData, machinesData] = await Promise.all([
  netCleaningRecordsService.getCleaningRecords(),
  netsService.getNets(),
  farmSitesService.getFarmSites(),
  machinesService.getMachines(false, userContext)  // ✅ With userContext!
]);
```

## Changes Made

**File**: `frontend/src/pages/NetCleaningRecords.js`

1. Created `userContext` object with user ID, organization ID, and super admin flag
2. Passed `userContext` as second parameter to `getMachines(false, userContext)`
3. Added `user` to `useCallback` dependencies to ensure context updates

## Deployment

**Commit**: 94d6ccc

The fix is already committed and pushed to GitHub. To deploy:

```bash
cd ~/abparts
git pull origin main
docker compose -f docker-compose.prod.yml build --no-cache web
docker compose -f docker-compose.prod.yml up -d
```

Then clear browser cache and test net cleaning record creation offline.

## Related Issues Fixed

This is part of a series of offline mode fixes:

1. ✅ **Protocols caching** - Fixed undefined STORES constant (commits 18695f0, e8c4baf)
2. ✅ **Protocols loading** - Fixed organization filtering for global stores (commit 88df42f)
3. ✅ **Net cleaning machines** - Fixed missing userContext (commit 94d6ccc)

## Testing

To verify the fix works:

1. Login to the application
2. Wait for offline data preload to complete
3. Go offline (disable network or use browser dev tools)
4. Navigate to Net Cleaning Records page
5. Click "Add New Record"
6. Verify machines dropdown loads without errors
7. Complete and submit the form
8. Record should be queued for sync

## Status

- ✅ Issue identified
- ✅ Fix implemented
- ✅ Code committed and pushed
- ⏳ **WAITING**: Production deployment + browser cache clear

---

**Summary**: Net cleaning records now work offline by passing userContext to getMachines() call.
