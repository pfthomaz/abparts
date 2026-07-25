# CRITICAL SECURITY IMPLEMENTATION PLAN

## Security Requirement
**ALL data filtering MUST be based on backend-enforced organization_id and user role, NEVER on cached or frontend-stored data.**

## Current Security Issues

### 1. Frontend Caching Bypasses Backend Security
- **Issue**: IndexedDB caches data without user/org context
- **Risk**: User A's cached data shown to User B after login
- **Severity**: CRITICAL

### 2. No User Context in Cache Keys
- **Issue**: Cache keys don't include user_id or organization_id
- **Risk**: Cross-user data leakage
- **Severity**: CRITICAL

### 3. Offline Mode Security Gap
- **Issue**: Offline DB doesn't store user context for filtering
- **Risk**: Cannot enforce org-scoped filtering offline
- **Severity**: HIGH

## Implementation Plan

### Phase 1: Backend Security Verification (IMMEDIATE)
Verify ALL backend endpoints enforce organization-scoped filtering.

**Endpoints to Audit:**
- ✅ `/machines/` - Already filters by organization_id
- ❓ `/parts/` - Need to verify
- ❓ `/warehouses/` - Need to verify
- ❓ `/inventory/` - Need to verify
- ❓ `/customer_orders/` - Need to verify
- ❓ `/supplier_orders/` - Need to verify
- ❓ `/stock_adjustments/` - Need to verify
- ❓ `/transactions/` - Need to verify
- ❓ `/maintenance_protocols/` - Need to verify
- ❓ `/maintenance_executions/` - Need to verify
- ❓ `/net_cleaning_records/` - Need to verify
- ❓ `/farm_sites/` - Need to verify
- ❓ `/nets/` - Need to verify

**Action Items:**
1. Audit each endpoint's CRUD functions
2. Ensure `current_user.organization_id` is used for filtering
3. Ensure super_admin check is correct: `if not is_super_admin(user)`
4. Add logging to track organization filtering

### Phase 2: User-Scoped Cache Keys (HIGH PRIORITY)
Add user context to all cache operations.

**Changes Required:**

#### A. Update IndexedDB Cache Functions
```javascript
// frontend/src/db/indexedDB.js

// Add user context to cache keys
function getCacheKey(storeName, userId, organizationId) {
  return `${storeName}_${userId}_${organizationId}`;
}

// Update cacheData function
export async function cacheData(storeName, data, userId, organizationId) {
  const cacheKey = getCacheKey(storeName, userId, organizationId);
  // Store with user-scoped key
}

// Update getCachedData function
export async function getCachedData(storeName, userId, organizationId) {
  const cacheKey = getCacheKey(storeName, userId, organizationId);
  // Retrieve with user-scoped key
}
```

#### B. Update All Service Functions
Every service that uses caching must pass user context:

```javascript
// frontend/src/services/machinesService.js
const getMachines = async (forceRefresh = false) => {
  const { user } = useAuth(); // Get current user
  
  // Pass user context to cache functions
  const cached = await getCachedData(
    STORES.MACHINES, 
    user.id, 
    user.organization_id
  );
  
  // Cache with user context
  await cacheData(
    STORES.MACHINES, 
    data, 
    user.id, 
    user.organization_id
  );
};
```

**Services to Update:**
- machinesService.js
- partsService.js
- warehousesService.js
- ordersService.js
- maintenanceProtocolsService.js
- netCleaningRecordsService.js
- farmSitesService.js
- netsService.js

### Phase 3: Clear Cache on User Change (HIGH PRIORITY)
Automatically clear cache when user changes.

```javascript
// frontend/src/AuthContext.js

useEffect(() => {
  // When user changes, clear all cached data
  if (user && previousUser && user.id !== previousUser.id) {
    import('./db/indexedDB')
      .then(({ clearAllOfflineData }) => clearAllOfflineData())
      .catch(error => console.warn('Failed to clear cache:', error));
  }
}, [user]);
```

### Phase 4: Offline Mode Security (HIGH PRIORITY)
Store user context in offline DB for filtering.

#### A. Add User Context Table
```javascript
// frontend/src/db/indexedDB.js

const USER_CONTEXT_STORE = 'user_context';

// Store current user context
export async function storeUserContext(user) {
  const db = await getDB();
  const tx = db.transaction(USER_CONTEXT_STORE, 'readwrite');
  await tx.store.put({
    id: 'current',
    user_id: user.id,
    organization_id: user.organization_id,
    role: user.role,
    timestamp: Date.now()
  });
}

// Get current user context
export async function getUserContext() {
  const db = await getDB();
  const tx = db.transaction(USER_CONTEXT_STORE, 'readonly');
  return await tx.store.get('current');
}
```

#### B. Filter Offline Data by Organization
```javascript
// frontend/src/services/machinesService.js

const getMachines = async (forceRefresh = false) => {
  const online = isOnline();
  
  if (!online) {
    const userContext = await getUserContext();
    const cached = await getCachedData(STORES.MACHINES);
    
    // CRITICAL: Filter by organization even offline
    if (userContext.role !== 'super_admin') {
      return cached.filter(
        m => m.customer_organization_id === userContext.organization_id
      );
    }
    return cached;
  }
  
  // Online: backend handles filtering
  const data = await api.get('/machines/');
  return data;
};
```

### Phase 5: Remove Frontend Filtering (CRITICAL)
Remove ALL client-side organization filtering that could be bypassed.

**Files to Update:**
- frontend/src/pages/Machines.js - Remove filterOrgId logic
- frontend/src/pages/Parts.js - Remove org filtering
- frontend/src/pages/Warehouses.js - Remove org filtering
- frontend/src/pages/Orders.js - Remove org filtering

**Principle:** 
- Backend ALWAYS returns only authorized data
- Frontend NEVER filters by organization (except offline mode with stored context)
- Frontend only filters by search terms, status, etc.

### Phase 6: Security Testing (REQUIRED)
Test cross-user data isolation.

**Test Cases:**
1. Login as super admin → See all machines
2. Logout → Login as org admin → See ONLY org machines
3. Check browser cache/IndexedDB → Should be cleared or user-scoped
4. Go offline → Verify org filtering still works
5. Switch users without logout → Verify cache is cleared

**Test Script:**
```bash
# Test 1: Super admin sees all
curl -H "Authorization: Bearer $SUPER_ADMIN_TOKEN" \
  http://localhost:8000/machines/ | jq 'length'
# Expected: 11 machines

# Test 2: Org admin sees only their org
curl -H "Authorization: Bearer $ORG_ADMIN_TOKEN" \
  http://localhost:8000/machines/ | jq 'length'
# Expected: 5 machines (Kefalonia)

# Test 3: Verify org_id in response
curl -H "Authorization: Bearer $ORG_ADMIN_TOKEN" \
  http://localhost:8000/machines/ | \
  jq '.[].customer_organization_id' | sort -u
# Expected: Only one org_id
```

## Implementation Priority

### IMMEDIATE (Today)
1. ✅ Clear Redis rate limits
2. Audit backend endpoints for org filtering
3. Add user-scoped cache keys to IndexedDB
4. Update machinesService with user-scoped caching

### HIGH (This Week)
1. Update all services with user-scoped caching
2. Implement cache clearing on user change
3. Add user context storage for offline mode
4. Remove frontend org filtering logic

### MEDIUM (Next Week)
1. Comprehensive security testing
2. Add security logging/monitoring
3. Document security architecture
4. Create security audit checklist

## Security Principles

### 1. Zero Trust Frontend
- **Never trust cached data**
- **Never trust localStorage/sessionStorage**
- **Always verify with backend when online**

### 2. Backend is Source of Truth
- **Backend enforces ALL access control**
- **Backend filters by organization_id**
- **Backend validates user permissions**

### 3. Offline Mode Security
- **Store user context in offline DB**
- **Filter offline data by stored context**
- **Sync only authorized data**

### 4. Cache Isolation
- **User-scoped cache keys**
- **Clear cache on user change**
- **Never share cache between users**

## Monitoring & Auditing

### Add Security Logging
```python
# backend/app/routers/machines.py

logger.info(
    f"User {current_user.username} (org: {current_user.organization_id}) "
    f"accessed machines endpoint. Is super_admin: {is_super_admin(current_user)}"
)
```

### Track Data Access
- Log which user accessed which organization's data
- Alert on cross-organization access attempts
- Monitor for unusual access patterns

## Compliance

### Data Protection Requirements
- ✅ Organization data isolation
- ✅ Role-based access control
- ✅ Audit trail of data access
- ⚠️ Cache security (IN PROGRESS)
- ⚠️ Offline mode security (IN PROGRESS)

## Next Steps

1. **IMMEDIATE**: I will audit all backend endpoints
2. **IMMEDIATE**: I will implement user-scoped cache keys
3. **TODAY**: Test the security fixes
4. **THIS WEEK**: Complete offline mode security

Would you like me to start with the backend audit or the cache key implementation?
