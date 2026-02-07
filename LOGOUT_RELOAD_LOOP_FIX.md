# Logout Reload Loop Fix

## Problem
After implementing user-scoped caching security, logging out caused a continuous page reload loop, making the login page unusable.

## Root Cause
The cache clearing logic was placed in the `useEffect` that runs when the user state changes. This created an infinite loop:

1. User logs out → `user` becomes `null`
2. `useEffect` detects user change → tries to clear cache
3. Cache clearing triggers state updates
4. State updates trigger `useEffect` again
5. Loop continues infinitely

## Solution
Moved cache clearing to happen ONLY during login, not during logout or user state changes.

### Changes Made

**File: `frontend/src/AuthContext.js`**

**BEFORE (Causing Loop):**
```javascript
useEffect(() => {
  // ... fetch user ...
  
  // This runs on EVERY user change, including logout!
  if (user && (user.id !== userData.id || user.organization_id !== userData.organization_id)) {
    await clearCache(...); // CAUSES LOOP
  }
  
  setUser(userData);
}, [token, logout]);
```

**AFTER (Fixed):**
```javascript
const login = async (username, password) => {
  // Clear cache BEFORE login (not during logout)
  await Promise.all([
    clearCache(STORES.MACHINES),
    clearCache(STORES.PARTS),
    // ... other stores
  ]);
  
  // Then perform login
  const data = await authService.login(username, password);
  // ...
};
```

## Why This Works

1. **Cache clearing on login**: When a new user logs in, we clear ALL cached data BEFORE fetching their data
2. **No cache clearing on logout**: Logout just clears tokens and redirects - no cache operations
3. **No infinite loops**: Cache clearing is a one-time operation during login, not a reactive effect

## Security Maintained

Even though we're not clearing cache on logout, security is still maintained because:

1. **Cache is cleared on next login**: Before any new user's data is fetched
2. **User context required**: All cache reads require valid user context
3. **Organization filtering**: `getCachedData()` filters by organization_id
4. **No user context = no cache**: If user context is missing, caching is skipped

## Testing

1. ✅ Login as user A
2. ✅ Logout (no reload loop)
3. ✅ Login as user B (cache cleared before login)
4. ✅ User B only sees their org's data

## Status

- **Reload Loop**: ✅ FIXED
- **Security**: ✅ MAINTAINED
- **User Experience**: ✅ SMOOTH

---

**Date**: 2026-02-07
**Issue**: Logout causing continuous page reload
**Fix**: Move cache clearing from useEffect to login function
