# Offline Maintenance Services Implementation Plan

## 🎯 Goal
Enable field workers to record maintenance executions (daily operations and scheduled maintenance) offline. Data syncs automatically when connectivity returns.

**Current Status**: Net cleaning offline mode is complete (Tasks 1-22). Now extending to maintenance services.

---

## 📋 What Needs Offline Support

### 1. **Maintenance Executions** (Primary)
- Start maintenance execution offline
- Complete checklist items offline
- Record quantities used offline
- Add notes offline
- Finish execution offline

### 2. **Machine Hours Recording**
- Record machine hours when starting maintenance
- Skip hours option (already works)

### 3. **Data Dependencies** (Need to Cache)
- ✅ Machines - Already cached in IndexedDB
- ✅ Protocols - Already in IndexedDB schema
- ⏳ Checklist Items - Need to cache
- ⏳ Parts - Already in IndexedDB schema (need service caching)

---

## 🏗️ Architecture Overview

**Existing Infrastructure** (from Net Cleaning):
- ✅ IndexedDB with `maintenanceExecutions` store
- ✅ Sync queue manager with `MAINTENANCE_EXECUTION` type
- ✅ Sync processor with `syncMaintenanceExecution()` function
- ✅ OfflineContext for state management
- ✅ Network status detection
- ✅ Auto-sync on reconnect

**What We Need to Add**:
1. Cache maintenance protocols and checklist items
2. Modify ExecutionForm for offline support
3. Modify MaintenanceExecutions page for pending executions
4. Add offline translations for maintenance

---

## 📝 Implementation Tasks

### ✅ Task M1: Cache Maintenance Protocols Service

**What**: Add caching to maintenance protocols service

**Why**: Workers need protocol list offline

**Files to Modify**:
- `frontend/src/services/maintenanceProtocolsService.js`

**Implementation**:
```javascript
// Add caching similar to farmSitesService and netsService
import { isOnline } from '../hooks/useNetworkStatus';
import { 
  cacheData, 
  getCachedData, 
  isCacheStale, 
  STORES 
} from '../db/indexedDB';

export async function getLocalizedProtocols(filters = {}, language = 'en', forceRefresh = false) {
  const online = isOnline();
  const cacheStale = await isCacheStale(STORES.PROTOCOLS);
  
  // Use cache if offline OR cache is fresh
  if (!online || (!cacheStale && !forceRefresh)) {
    const cached = await getCachedData(STORES.PROTOCOLS);
    if (cached.length > 0) {
      console.log('[MaintenanceService] Using cached protocols:', cached.length);
      // Apply filters to cached data
      return cached.filter(p => {
        if (filters.is_active !== undefined && p.is_active !== filters.is_active) return false;
        if (filters.protocol_type && p.protocol_type !== filters.protocol_type) return false;
        return true;
      });
    }
  }
  
  // Fetch from API
  try {
    const data = await api.get('/maintenance-protocols/', { params: { language, ...filters } });
    
    // Cache the response
    await cacheData(STORES.PROTOCOLS, data);
    
    return data;
  } catch (error) {
    // Fallback to cache on error
    const cached = await getCachedData(STORES.PROTOCOLS);
    if (cached.length > 0) {
      console.log('[MaintenanceService] API failed, using cached protocols');
      return cached;
    }
    throw error;
  }
}

// Similar for getLocalizedChecklistItems()
```

---

### ✅ Task M2: Cache Parts Service

**What**: Add caching to parts service for quantity tracking

**Why**: Need parts list for quantity used in checklist items

**Files to Modify**:
- `frontend/src/services/partsService.js`

**Implementation**:
```javascript
// Add caching for parts (similar pattern)
export async function getParts(filters = {}, forceRefresh = false) {
  const online = isOnline();
  const cacheStale = await isCacheStale(STORES.PARTS);
  
  if (!online || (!cacheStale && !forceRefresh)) {
    const cached = await getCachedData(STORES.PARTS);
    if (cached.length > 0) {
      console.log('[PartsService] Using cached parts:', cached.length);
      return cached;
    }
  }
  
  try {
    const data = await api.get('/parts/', { params: filters });
    await cacheData(STORES.PARTS, data);
    return data;
  } catch (error) {
    const cached = await getCachedData(STORES.PARTS);
    if (cached.length > 0) {
      console.log('[PartsService] API failed, using cached parts');
      return cached;
    }
    throw error;
  }
}
```

---

### ✅ Task M3: Modify ExecutionForm for Offline

**What**: Enable offline maintenance execution recording

**Why**: PRIMARY USE CASE - record maintenance offline

**Files to Modify**:
- `frontend/src/components/ExecutionForm.js`

**Implementation**:

1. **Add Offline Detection**:
```javascript
import { useOffline } from '../contexts/OfflineContext';

const ExecutionForm = ({ machine, protocol, existingExecution, onComplete, onCancel }) => {
  const { isOnline } = useOffline();
  // ... existing code
```

2. **Offline Save Logic**:
```javascript
const initializeExecution = async (hours) => {
  if (!isOnline) {
    // Save offline
    const tempId = `temp_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    
    const offlineExecution = {
      tempId,
      protocol_id: protocol.id,
      machine_id: machine.id,
      machine_hours_at_service: hours > 0 ? hours : null,
      status: 'in_progress',
      checklist_completions: [],
      created_at: new Date().toISOString(),
      synced: false,
      organization_id: user.organization_id
    };
    
    // Save to IndexedDB
    await saveOfflineMaintenanceExecution(offlineExecution);
    
    // Queue for sync
    await queueMaintenanceExecution(offlineExecution);
    
    setExecutionId(tempId);
    setShowHoursInput(false);
    
    alert(t('maintenance.savedOffline'));
    return;
  }
  
  // Online logic (existing code)
  // ...
};
```

3. **Offline Checklist Completion**:
```javascript
const handleItemComplete = async (item, itemData) => {
  if (!executionId) return;
  
  if (!isOnline) {
    // Save offline
    const completion = {
      checklist_item_id: item.id,
      status: itemData.completed ? 'completed' : 'skipped',
      notes: itemData.notes || null,
      actual_quantity_used: itemData.quantity ? parseFloat(itemData.quantity) : null,
      completed_at: new Date().toISOString()
    };
    
    // Update offline execution in IndexedDB
    await updateOfflineExecutionCompletion(executionId, completion);
    
    setCompletedItems(prev => ({
      ...prev,
      [item.id]: { ...itemData, saved: true }
    }));
    
    return;
  }
  
  // Online logic (existing code)
  // ...
};
```

4. **Offline Warning Banner**:
```javascript
{!isOnline && (
  <div className="bg-yellow-50 border-l-4 border-yellow-400 p-4 mb-4">
    <div className="flex">
      <div className="flex-shrink-0">
        <svg className="h-5 w-5 text-yellow-400" viewBox="0 0 20 20" fill="currentColor">
          <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
        </svg>
      </div>
      <div className="ml-3">
        <p className="text-sm text-yellow-700">
          {t('maintenance.offlineMode')} - {t('maintenance.offlineModeHelp')}
        </p>
      </div>
    </div>
  </div>
)}
```

---

### ✅ Task M4: Add IndexedDB Helper Functions

**What**: Add helper functions for offline maintenance executions

**Why**: Need to save/retrieve offline executions

**Files to Modify**:
- `frontend/src/db/indexedDB.js`

**Implementation**:
```javascript
/**
 * Save offline maintenance execution
 */
export async function saveOfflineMaintenanceExecution(execution) {
  try {
    const db = await getDB();
    const tempId = execution.tempId || `temp_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    
    const offlineExecution = {
      ...execution,
      tempId,
      synced: false,
      timestamp: Date.now(),
    };
    
    await db.put(STORES.MAINTENANCE_EXECUTIONS, offlineExecution);
    console.log('[IndexedDB] Saved offline maintenance execution:', tempId);
    
    return tempId;
  } catch (error) {
    console.error('[IndexedDB] Failed to save offline maintenance execution:', error);
    throw error;
  }
}

/**
 * Update offline execution with checklist completion
 */
export async function updateOfflineExecutionCompletion(tempId, completion) {
  try {
    const db = await getDB();
    const execution = await db.get(STORES.MAINTENANCE_EXECUTIONS, tempId);
    
    if (execution) {
      if (!execution.checklist_completions) {
        execution.checklist_completions = [];
      }
      
      // Find existing completion or add new
      const existingIndex = execution.checklist_completions.findIndex(
        c => c.checklist_item_id === completion.checklist_item_id
      );
      
      if (existingIndex >= 0) {
        execution.checklist_completions[existingIndex] = completion;
      } else {
        execution.checklist_completions.push(completion);
      }
      
      await db.put(STORES.MAINTENANCE_EXECUTIONS, execution);
      console.log('[IndexedDB] Updated offline execution completion:', tempId);
    }
  } catch (error) {
    console.error('[IndexedDB] Failed to update offline execution:', error);
    throw error;
  }
}

/**
 * Get all unsynced maintenance executions
 */
export async function getUnsyncedMaintenanceExecutions() {
  try {
    const db = await getDB();
    const tx = db.transaction(STORES.MAINTENANCE_EXECUTIONS, 'readonly');
    const store = tx.objectStore(STORES.MAINTENANCE_EXECUTIONS);
    const allExecutions = await store.getAll();
    
    const unsyncedExecutions = allExecutions.filter(exec => exec.synced === false);
    return unsyncedExecutions;
  } catch (error) {
    console.error('[IndexedDB] Failed to get unsynced executions:', error);
    return [];
  }
}

/**
 * Mark maintenance execution as synced
 */
export async function markExecutionAsSynced(tempId, serverId) {
  try {
    const db = await getDB();
    const execution = await db.get(STORES.MAINTENANCE_EXECUTIONS, tempId);
    
    if (execution) {
      execution.synced = true;
      execution.serverId = serverId;
      execution.syncedAt = Date.now();
      await db.put(STORES.MAINTENANCE_EXECUTIONS, execution);
      console.log('[IndexedDB] Marked execution as synced:', tempId);
    }
  } catch (error) {
    console.error('[IndexedDB] Failed to mark execution as synced:', error);
  }
}
```

---

### ✅ Task M5: Update Sync Processor for Maintenance

**What**: Enhance sync processor to handle maintenance executions

**Why**: Need to sync offline executions to server

**Files to Modify**:
- `frontend/src/services/syncProcessor.js`

**Implementation**:
```javascript
/**
 * Sync maintenance executions from IndexedDB
 */
async function syncMaintenanceExecutions(token) {
  const results = {
    total: 0,
    succeeded: 0,
    failed: 0,
    errors: [],
  };
  
  try {
    const executions = await getUnsyncedMaintenanceExecutions();
    results.total = executions.length;
    
    console.log(`[SyncProcessor] Syncing ${executions.length} maintenance executions...`);
    
    for (const execution of executions) {
      try {
        const serverId = await syncSingleMaintenanceExecution(execution, token);
        
        if (serverId) {
          await markExecutionAsSynced(execution.tempId, serverId);
          results.succeeded++;
          console.log(`[SyncProcessor] Synced execution ${execution.tempId} -> ${serverId}`);
        } else {
          results.failed++;
          results.errors.push(`Failed to sync execution ${execution.tempId}`);
        }
      } catch (error) {
        console.error(`[SyncProcessor] Failed to sync execution ${execution.tempId}:`, error);
        results.failed++;
        results.errors.push(`Execution ${execution.tempId}: ${error.message}`);
      }
    }
  } catch (error) {
    console.error('[SyncProcessor] Failed to sync maintenance executions:', error);
    results.errors.push(error.message);
  }
  
  return results;
}

/**
 * Sync a single maintenance execution
 */
async function syncSingleMaintenanceExecution(execution, token) {
  try {
    const { tempId, synced, timestamp, ...apiData } = execution;
    
    // Create execution
    const response = await fetch(`${API_BASE_URL}/maintenance-protocols/executions`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
      },
      body: JSON.stringify(apiData),
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to create execution');
    }
    
    const data = await response.json();
    return data.id;
  } catch (error) {
    console.error('[SyncProcessor] Failed to sync execution:', error);
    throw error;
  }
}

// Update processSync() to include maintenance executions
export async function processSync() {
  // ... existing code
  
  // Process maintenance executions
  const maintenanceResults = await syncMaintenanceExecutions(token);
  results.total += maintenanceResults.total;
  results.succeeded += maintenanceResults.succeeded;
  results.failed += maintenanceResults.failed;
  results.errors.push(...maintenanceResults.errors);
  
  // ... rest of code
}
```

---

### ✅ Task M6: Update MaintenanceExecutions Page for Pending

**What**: Show pending (unsynced) executions in list

**Why**: Users need to see what's waiting to sync

**Files to Modify**:
- `frontend/src/pages/MaintenanceExecutions.js`

**Implementation**:
```javascript
import { getUnsyncedMaintenanceExecutions } from '../db/indexedDB';
import { useOffline } from '../contexts/OfflineContext';

const MaintenanceExecutions = () => {
  const [offlineExecutions, setOfflineExecutions] = useState([]);
  const { isOnline, pendingCount } = useOffline();
  
  // Load offline executions
  useEffect(() => {
    const loadOfflineExecutions = async () => {
      const unsynced = await getUnsyncedMaintenanceExecutions();
      setOfflineExecutions(unsynced);
    };
    loadOfflineExecutions();
  }, [pendingCount]);
  
  // Combine online and offline executions
  const allExecutions = [
    ...executions.map(e => ({ ...e, isPending: false })),
    ...offlineExecutions.map(e => ({ ...e, isPending: true }))
  ];
  
  // Show pending count in banner
  {offlineExecutions.length > 0 && (
    <div className="bg-blue-50 border-l-4 border-blue-500 p-4 mb-4">
      <p className="text-sm text-blue-700">
        {t('maintenance.pendingSync', { count: offlineExecutions.length })}
      </p>
    </div>
  )}
  
  // Add pending badge to execution cards
  {execution.isPending && (
    <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-blue-100 text-blue-800">
      {t('maintenance.pendingSync')}
    </span>
  )}
};
```

---

### ✅ Task M7: Add Maintenance Offline Translations

**What**: Add translations for offline maintenance

**Why**: Support all 6 languages

**Files to Create**:
- `add_maintenance_offline_translations.py`

**Translations to Add**:
```python
translations = {
    'en': {
        'maintenance': {
            'offlineMode': 'Offline Mode',
            'offlineModeHelp': 'You are offline. Maintenance will be saved locally and synced when connection is restored.',
            'savedOffline': 'Maintenance saved offline. Will sync when connection restored.',
            'pendingSync': '{count} maintenance execution(s) pending sync',
            'waitingSync': 'Waiting to sync',
            'syncingExecution': 'Syncing maintenance execution...',
        }
    },
    # ... other languages
}
```

---

## 🔄 Complete Offline Workflow

### Scenario: Field Worker at Remote Fish Farm

1. **Worker arrives at farm** (no connectivity)
   - Opens ABParts app on mobile
   - Sees yellow "Offline Mode" indicator

2. **Starts daily maintenance**
   - Goes to Daily Operations
   - Selects machine
   - Selects daily protocol
   - Enters machine hours (or skips)
   - Clicks "Start Maintenance"

3. **Completes checklist offline**
   - Checks off items as completed
   - Enters quantities used
   - Adds notes/observations
   - All saved to IndexedDB automatically

4. **Finishes maintenance**
   - Clicks "Finish Maintenance"
   - Execution saved offline with "Pending Sync" badge
   - Returns to Daily Operations

5. **Worker returns to area with connectivity**
   - App detects connection
   - Auto-sync triggers
   - Maintenance execution uploads to server
   - "Pending Sync" badge disappears
   - Execution now shows in online list

---

## 📊 Implementation Checklist

- [ ] Task M1: Cache Maintenance Protocols Service
- [ ] Task M2: Cache Parts Service
- [ ] Task M3: Modify ExecutionForm for Offline
- [ ] Task M4: Add IndexedDB Helper Functions
- [ ] Task M5: Update Sync Processor for Maintenance
- [ ] Task M6: Update MaintenanceExecutions Page for Pending
- [ ] Task M7: Add Maintenance Offline Translations

---

## 🧪 Testing Plan

### Test Scenario 1: Daily Maintenance Offline
1. Go offline (DevTools Network tab → Offline)
2. Navigate to Daily Operations
3. Select machine and daily protocol
4. Enter machine hours
5. Complete checklist items
6. Finish maintenance
7. Verify execution shows "Pending Sync" badge
8. Check IndexedDB for saved execution
9. Go online
10. Verify auto-sync
11. Check execution appears in backend

### Test Scenario 2: Scheduled Maintenance Offline
1. Go offline
2. Navigate to Maintenance Executions
3. Select machine and scheduled protocol
4. Complete maintenance
5. Verify offline save
6. Go online and verify sync

### Test Scenario 3: Resume Offline Execution
1. Start maintenance offline
2. Complete some items
3. Close app
4. Reopen app (still offline)
5. Resume execution
6. Verify progress preserved
7. Complete and sync

---

## 🎯 Success Criteria

✅ Can start maintenance execution offline  
✅ Can complete checklist items offline  
✅ Can record quantities offline  
✅ Can add notes offline  
✅ Can finish execution offline  
✅ Execution appears with "Pending Sync" badge  
✅ Auto-sync triggers when back online  
✅ Execution syncs to backend successfully  
✅ No data loss  
✅ No console errors  

---

## 📝 Notes

**Reusing Existing Infrastructure**:
- IndexedDB already has `maintenanceExecutions` store
- Sync queue already supports `MAINTENANCE_EXECUTION` type
- Sync processor already has `syncMaintenanceExecution()` function
- Just need to wire up the UI components!

**Estimated Time**: 4-6 hours
- Task M1-M2: 1 hour (caching services)
- Task M3: 2 hours (ExecutionForm modifications)
- Task M4-M5: 1 hour (IndexedDB + sync processor)
- Task M6: 1 hour (MaintenanceExecutions page)
- Task M7: 30 minutes (translations)
- Testing: 30 minutes

**Dependencies**:
- Net cleaning offline mode (already complete)
- Maintenance system (already complete)
- All infrastructure in place

---

Ready to implement? Just say **"Start Task M1"** and I'll begin! 🚀
