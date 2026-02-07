# Guide: Apply User-Scoped Caching to Services

## Overview

This guide shows how to apply user-scoped caching to services that handle organization-specific data. This prevents cross-user data leakage.

## Services That Need Fixing

1. ⚠️ `frontend/src/services/partsService.js`
2. ⚠️ `frontend/src/services/farmSitesService.js`
3. ⚠️ `frontend/src/services/netsService.js`
4. ⚠️ `frontend/src/services/maintenanceProtocolsService.js`

## Step-by-Step Implementation

### Step 1: Update Service Function Signature

**Before:**
```javascript
const getItems = async (forceRefresh = false) => {
```

**After:**
```javascript
const getItems = async (forceRefresh = false, userContext = null) => {
```

### Step 2: Add User Context Validation

Add this at the beginning of the function:

```javascript
// SECURITY: Require user context for caching
if (!userContext || !userContext.userId || !userContext.organizationId) {
  console.warn('[ServiceName] SECURITY WARNING: No user context provided, fetching without cache');
  if (!online) {
    throw new Error('Cannot fetch items offline without user context');
  }
  // Fetch directly from API without caching
  const data = await api.get('/endpoint/');
  return data;
}
```

### Step 3: Update Cache Operations

**Before:**
```javascript
await cacheData(STORES.ITEMS, data);
const cached = await getCachedData(STORES.ITEMS);
const stale = await isCacheStale(STORES.ITEMS);
```

**After:**
```javascript
await cacheData(STORES.ITEMS, data, userContext);
const cached = await getCachedData(STORES.ITEMS, userContext);
const stale = await isCacheStale(STORES.ITEMS, userContext);
```

### Step 4: Update Page Component

**Before:**
```javascript
const fetchData = async () => {
  const data = await itemsService.getItems();
  setItems(data);
};
```

**After:**
```javascript
const fetchData = async () => {
  // Create user context
  const userContext = {
    userId: user.id,
    organizationId: user.organization_id,
    isSuperAdmin: user.role === 'super_admin'
  };
  
  // Pass user context to service
  const data = await itemsService.getItems(false, userContext);
  setItems(data);
};
```

## Complete Example: partsService.js

### Current Code (INSECURE):
```javascript
const getParts = async (forceRefresh = false) => {
  const online = isOnline();
  
  if (!online) {
    const cached = await getCachedData(STORES.PARTS);
    return cached;
  }
  
  const response = await api.get('/parts/');
  await cacheData(STORES.PARTS, response);
  return response;
};
```

### Fixed Code (SECURE):
```javascript
const getParts = async (forceRefresh = false, userContext = null) => {
  const online = isOnline();
  
  // SECURITY: Require user context for caching
  if (!userContext || !userContext.userId || !userContext.organizationId) {
    console.warn('[PartsService] SECURITY WARNING: No user context provided');
    if (!online) {
      throw new Error('Cannot fetch parts offline without user context');
    }
    const data = await api.get('/parts/');
    return data;
  }
  
  // If offline, use cache immediately
  if (!online) {
    const cached = await getCachedData(STORES.PARTS, userContext);
    if (cached.length > 0) {
      console.log('[PartsService] Using cached parts (offline):', cached.length);
      return cached;
    }
    throw new Error('No cached data available offline');
  }
  
  // Check cache staleness
  let cacheStale = true;
  try {
    const staleCheckPromise = isCacheStale(STORES.PARTS, userContext);
    const timeoutPromise = new Promise((resolve) => setTimeout(() => resolve(true), 1000));
    cacheStale = await Promise.race([staleCheckPromise, timeoutPromise]);
  } catch (error) {
    console.warn('[PartsService] Cache staleness check failed:', error);
    cacheStale = true;
  }
  
  // Use cache if fresh and not forcing refresh
  if (!cacheStale && !forceRefresh) {
    const cached = await getCachedData(STORES.PARTS, userContext);
    if (cached.length > 0) {
      console.log('[PartsService] Using cached parts (fresh):', cached.length);
      return cached;
    }
  }
  
  // Fetch from API
  try {
    const response = await api.get('/parts/');
    
    // Cache with user context
    await cacheData(STORES.PARTS, response, userContext);
    console.log('[PartsService] Cached parts:', response.length);
    
    return response;
  } catch (error) {
    // Fallback to cache on error
    console.warn('[PartsService] API failed, attempting cache fallback:', error.message);
    const cached = await getCachedData(STORES.PARTS, userContext);
    if (cached.length > 0) {
      console.log('[PartsService] Using cached parts (fallback):', cached.length);
      return cached;
    }
    throw error;
  }
};
```

## Complete Example: Parts.js Page

### Current Code (INSECURE):
```javascript
const fetchParts = async () => {
  try {
    setLoading(true);
    const data = await partsService.getParts();
    setParts(data);
  } catch (error) {
    console.error('Failed to fetch parts:', error);
  } finally {
    setLoading(false);
  }
};
```

### Fixed Code (SECURE):
```javascript
const fetchParts = async () => {
  try {
    setLoading(true);
    
    // Create user context from AuthContext
    const userContext = {
      userId: user.id,
      organizationId: user.organization_id,
      isSuperAdmin: user.role === 'super_admin'
    };
    
    // Pass user context to service
    const data = await partsService.getParts(false, userContext);
    setParts(data);
  } catch (error) {
    console.error('Failed to fetch parts:', error);
  } finally {
    setLoading(false);
  }
};
```

## Testing Checklist

For each service you fix:

- [ ] Service accepts `userContext` parameter
- [ ] Service validates user context before caching
- [ ] Service passes user context to all cache operations
- [ ] Page creates user context object
- [ ] Page passes user context to service
- [ ] Test: Super admin sees all data
- [ ] Test: Org admin sees only their org's data
- [ ] Test: Logout → Login as different user → No cross-contamination

## Reference Implementation

Use `frontend/src/services/machinesService.js` and `frontend/src/pages/Machines.js` as the reference implementation. They are already fixed and working correctly.

## Security Validation

After fixing each service, verify:

1. **Cache keys include user context:**
   - Open browser DevTools → Application → IndexedDB → ABPartsOfflineDB → cacheMetadata
   - Keys should be: `items_user_{userId}_org_{organizationId}`

2. **Data is filtered by organization:**
   - Login as super admin → See all data
   - Logout → Login as org admin → See only org data
   - Verify org admin does NOT see super admin's cached data

3. **No errors in console:**
   - Check for "SECURITY WARNING" messages
   - Check for "No user context" errors

## Common Mistakes to Avoid

❌ **Don't forget to pass userContext in ALL cache operations:**
```javascript
// WRONG - Missing userContext
await cacheData(STORES.ITEMS, data);

// CORRECT - Includes userContext
await cacheData(STORES.ITEMS, data, userContext);
```

❌ **Don't forget to validate userContext:**
```javascript
// WRONG - No validation
const getItems = async (forceRefresh = false, userContext = null) => {
  await cacheData(STORES.ITEMS, data, userContext);
}

// CORRECT - Validates before using
const getItems = async (forceRefresh = false, userContext = null) => {
  if (!userContext || !userContext.userId) {
    console.warn('No user context');
    // Handle appropriately
  }
  await cacheData(STORES.ITEMS, data, userContext);
}
```

❌ **Don't forget to update the page component:**
```javascript
// WRONG - Service updated but page not updated
const data = await itemsService.getItems(); // Missing userContext

// CORRECT - Page passes userContext
const userContext = { userId: user.id, organizationId: user.organization_id, isSuperAdmin: user.role === 'super_admin' };
const data = await itemsService.getItems(false, userContext);
```

## Questions?

Refer to:
- `START_HERE_SECURITY_FIX.md` - Overall status
- `SECURITY_FIX_FINAL_SUMMARY.md` - Technical details
- `frontend/src/services/machinesService.js` - Reference implementation
