# Machine Security Issue - Cache Fix

## Issue Summary
Admin users in customer organizations were seeing all machines from all organizations instead of only their organization's machines.

## Root Cause
**Frontend IndexedDB Caching Issue**

The application uses IndexedDB to cache data for offline functionality. When a user logged out and a different user logged in, the cached machines data from the previous user was still being served, bypassing the backend's organization-scoped filtering.

### Why This Happened:
1. The `logout()` function in `AuthContext.js` was NOT clearing the IndexedDB cache
2. The `getMachines()` function in `machinesService.js` uses cached data when it's "fresh" (not stale)
3. When switching from super admin → regular admin, the cached "all machines" data was still being used
4. The backend permission checking was working correctly, but the frontend never made a fresh API call

## Backend Verification
The backend code in `backend/app/routers/machines.py` was working correctly:
- Line 313-318: Properly checks `if not permission_checker.is_super_admin(current_user)`
- Correctly filters by `current_user.organization_id` for non-super-admins
- The `permission_checker.is_super_admin()` function correctly checks `user.role == "super_admin"`

## Fixes Applied

### 1. Clear Cache on Logout (`frontend/src/AuthContext.js`)
Updated the `logout()` function to clear all IndexedDB cached data:

```javascript
const logout = useCallback(async () => {
  setToken(null);
  setUser(null);
  
  // Clear all authentication and user-specific data from localStorage
  localStorage.removeItem('authToken');
  localStorage.removeItem('token');
  localStorage.removeItem('selectedOrganizationId');
  localStorage.removeItem('localizationPreferences');
  
  // Clear session storage completely
  sessionStorage.clear();
  
  // Clear IndexedDB cache to prevent data leakage between users
  try {
    const { clearAllOfflineData } = await import('./db/indexedDB');
    await clearAllOfflineData();
    console.log('[AuthContext] Cleared all cached data on logout');
  } catch (error) {
    console.warn('[AuthContext] Failed to clear cache on logout:', error);
  }
  
  // Force a hard reload to clear any cached React state
  window.location.href = '/';
}, []);
```

### 2. Force Refresh on Machines Page Load (`frontend/src/pages/Machines.js`)
Updated the initial data fetch to force a fresh API call:

```javascript
const fetchData = useCallback(async (forceRefresh = false) => {
  setLoading(true);
  setError(null);
  try {
    const [machinesData, orgsData] = await Promise.all([
      machinesService.getMachines(forceRefresh), // Pass forceRefresh flag
      api.get('/organizations/'),
    ]);
    setMachines(machinesData);
    setOrganizations(orgsData);
  } catch (err) {
    setError(err.message || 'Failed to fetch data.');
  } finally {
    setLoading(false);
  }
}, []);

useEffect(() => {
  // Force refresh on initial mount to ensure fresh data for current user
  fetchData(true);
}, []);
```

## Testing Instructions

1. **Log out completely** from the application
2. **Close the browser tab** (to clear any in-memory state)
3. **Open a new browser tab** and navigate to http://localhost:3000
4. **Log in as a Kefalonia admin user** (e.g., "lefteris", "thomas", or "Zisis")
5. **Navigate to the Machines page**
6. **Verify** you only see the 5 machines from Kefalonia Fisheries SA

Expected Results:
- Kefalonia admin users should see only 5 machines (KEF-1 through KEF-5)
- Super admin users should see all 11 machines across all organizations
- No cached data from previous users should appear

## Database Verification

Kefalonia Fisheries SA users in database:
- Username: lefteris, Role: admin
- Username: thomas, Role: admin
- Username: Worker, Role: user
- Username: Zisis, Role: admin

Total machines in database:
- 5 machines in Kefalonia Fisheries SA
- 2 machines in AquaFarms Ltd
- 1 machine each in: Tharawat Seas LLC, Mare Magnum, Leros Fishfarming SA, Kito Fishfarming SA
- **Total: 11 machines**

## Security Impact

This was a **HIGH SEVERITY** security issue:
- **Data Leakage**: Users could see data from other organizations due to caching
- **Privacy Violation**: Organization-scoped data was not properly isolated between user sessions
- **Compliance Risk**: Violates data access control requirements

## Prevention

To prevent similar issues in the future:
1. Always clear user-specific cached data on logout
2. Force refresh sensitive data on page load
3. Consider adding user ID or organization ID to cache keys
4. Implement cache versioning tied to user sessions
5. Add automated tests for cross-user data isolation

## Files Modified

1. `frontend/src/AuthContext.js` - Added cache clearing on logout
2. `frontend/src/pages/Machines.js` - Added force refresh on initial load
3. `backend/app/routers/machines.py` - Added debug logging (can be removed after verification)

## Status

✅ **FIXED** - Ready for testing
