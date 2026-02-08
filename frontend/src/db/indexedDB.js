// IndexedDB Wrapper for Offline Storage
// Handles all offline data storage for field operations

import { openDB } from 'idb';

const DB_NAME = 'ABPartsOfflineDB';
const DB_VERSION = 2; // Incremented to add users store

// Database schema
const STORES = {
  // Cached data from API
  FARM_SITES: 'farmSites',
  NETS: 'nets',
  MACHINES: 'machines',
  PROTOCOLS: 'protocols',
  PARTS: 'parts',
  USERS: 'users', // Added for operator dropdown offline support
  
  // Offline operations queue
  SYNC_QUEUE: 'syncQueue',
  
  // Offline net cleaning records
  NET_CLEANING_RECORDS: 'netCleaningRecords',
  NET_CLEANING_PHOTOS: 'netCleaningPhotos',
  
  // Offline maintenance executions
  MAINTENANCE_EXECUTIONS: 'maintenanceExecutions',
  
  // Offline machine hours
  MACHINE_HOURS: 'machineHours',
  
  // Metadata
  CACHE_METADATA: 'cacheMetadata',
};

/**
 * Initialize and open the IndexedDB database
 */
export async function initDB() {
  try {
    const db = await openDB(DB_NAME, DB_VERSION, {
      upgrade(db, oldVersion, newVersion, transaction) {
        // console.log(`[IndexedDB] Upgrading database from version ${oldVersion} to ${newVersion}`);
        
        // Create object stores if they don't exist
        
        // Cached data stores
        if (!db.objectStoreNames.contains(STORES.FARM_SITES)) {
          const farmSitesStore = db.createObjectStore(STORES.FARM_SITES, { keyPath: 'id' });
          farmSitesStore.createIndex('organization_id', 'organization_id');
          farmSitesStore.createIndex('active', 'active');
        }
        
        if (!db.objectStoreNames.contains(STORES.NETS)) {
          const netsStore = db.createObjectStore(STORES.NETS, { keyPath: 'id' });
          netsStore.createIndex('farm_site_id', 'farm_site_id');
          netsStore.createIndex('active', 'active');
        }
        
        if (!db.objectStoreNames.contains(STORES.MACHINES)) {
          const machinesStore = db.createObjectStore(STORES.MACHINES, { keyPath: 'id' });
          machinesStore.createIndex('organization_id', 'organization_id');
        }
        
        if (!db.objectStoreNames.contains(STORES.PROTOCOLS)) {
          const protocolsStore = db.createObjectStore(STORES.PROTOCOLS, { keyPath: 'id' });
          protocolsStore.createIndex('organization_id', 'organization_id');
        }
        
        if (!db.objectStoreNames.contains(STORES.PARTS)) {
          const partsStore = db.createObjectStore(STORES.PARTS, { keyPath: 'id' });
          partsStore.createIndex('part_number', 'part_number');
        }
        
        if (!db.objectStoreNames.contains(STORES.USERS)) {
          const usersStore = db.createObjectStore(STORES.USERS, { keyPath: 'id' });
          usersStore.createIndex('organization_id', 'organization_id');
          usersStore.createIndex('is_active', 'is_active');
        }
        
        // Sync queue store
        if (!db.objectStoreNames.contains(STORES.SYNC_QUEUE)) {
          const syncQueueStore = db.createObjectStore(STORES.SYNC_QUEUE, { 
            keyPath: 'id', 
            autoIncrement: true 
          });
          syncQueueStore.createIndex('timestamp', 'timestamp');
          syncQueueStore.createIndex('type', 'type');
          syncQueueStore.createIndex('status', 'status');
        }
        
        // Offline net cleaning records
        if (!db.objectStoreNames.contains(STORES.NET_CLEANING_RECORDS)) {
          const netCleaningStore = db.createObjectStore(STORES.NET_CLEANING_RECORDS, { 
            keyPath: 'tempId' 
          });
          netCleaningStore.createIndex('net_id', 'net_id');
          netCleaningStore.createIndex('synced', 'synced');
          netCleaningStore.createIndex('timestamp', 'timestamp');
        }
        
        // Offline net cleaning photos
        if (!db.objectStoreNames.contains(STORES.NET_CLEANING_PHOTOS)) {
          const photosStore = db.createObjectStore(STORES.NET_CLEANING_PHOTOS, { 
            keyPath: 'id',
            autoIncrement: true
          });
          photosStore.createIndex('recordTempId', 'recordTempId');
          photosStore.createIndex('synced', 'synced');
        }
        
        // Offline maintenance executions
        if (!db.objectStoreNames.contains(STORES.MAINTENANCE_EXECUTIONS)) {
          const executionsStore = db.createObjectStore(STORES.MAINTENANCE_EXECUTIONS, { 
            keyPath: 'tempId' 
          });
          executionsStore.createIndex('protocol_id', 'protocol_id');
          executionsStore.createIndex('synced', 'synced');
          executionsStore.createIndex('timestamp', 'timestamp');
        }
        
        // Offline machine hours
        if (!db.objectStoreNames.contains(STORES.MACHINE_HOURS)) {
          const hoursStore = db.createObjectStore(STORES.MACHINE_HOURS, { 
            keyPath: 'tempId' 
          });
          hoursStore.createIndex('machine_id', 'machine_id');
          hoursStore.createIndex('synced', 'synced');
          hoursStore.createIndex('timestamp', 'timestamp');
        }
        
        // Cache metadata store
        if (!db.objectStoreNames.contains(STORES.CACHE_METADATA)) {
          db.createObjectStore(STORES.CACHE_METADATA, { keyPath: 'key' });
        }
        
        // console.log('[IndexedDB] Database upgrade complete');
      },
    });
    
    // console.log('[IndexedDB] Database initialized successfully');
    return db;
  } catch (error) {
    console.error('[IndexedDB] Failed to initialize database:', error);
    throw error;
  }
}

/**
 * Get a reference to the database
 */
export async function getDB() {
  return await initDB();
}

// ============================================================================
// CACHE OPERATIONS WITH USER CONTEXT
// ============================================================================

/**
 * Generate a user-scoped cache key
 * CRITICAL SECURITY: All cached data MUST be scoped to user to prevent cross-user data leakage
 */
function getUserCacheKey(storeName, userId, organizationId) {
  if (!userId || !organizationId) {
    console.error('[IndexedDB] SECURITY ERROR: Missing user context for cache key');
    throw new Error('User context required for caching');
  }
  return `${storeName}_user_${userId}_org_${organizationId}`;
}

/**
 * Save data to a cache store with user context
 * CRITICAL SECURITY: Data is scoped to specific user and organization
 */
export async function cacheData(storeName, data, userContext = null) {
  try {
    // SECURITY CHECK: Require user context for all caching
    if (!userContext || !userContext.userId || !userContext.organizationId) {
      console.warn('[IndexedDB] SECURITY WARNING: Caching without user context - data will not be cached');
      return; // Don't cache without user context
    }
    
    const db = await getDB();
    const tx = db.transaction(storeName, 'readwrite');
    const store = tx.objectStore(storeName);
    
    if (Array.isArray(data)) {
      // Bulk insert
      await Promise.all(data.map(item => store.put(item)));
    } else {
      // Single insert
      await store.put(data);
    }
    
    await tx.done;
    
    // Update cache metadata with user context
    await updateCacheMetadata(storeName, userContext);
    
    // console.log(`[IndexedDB] Cached ${Array.isArray(data) ? data.length : 1} items to ${storeName} for user ${userContext.userId}`);
  } catch (error) {
    console.error(`[IndexedDB] Failed to cache data to ${storeName}:`, error);
    throw error;
  }
}

/**
 * Get all data from a cache store with user context
 * CRITICAL SECURITY: Only returns data for the current user's organization
 */
export async function getCachedData(storeName, userContext = null) {
  try {
    // SECURITY CHECK: Require user context for reading cache
    if (!userContext || !userContext.userId || !userContext.organizationId) {
      console.warn('[IndexedDB] SECURITY WARNING: Reading cache without user context - returning empty array');
      return [];
    }
    
    const db = await getDB();
    const data = await db.getAll(storeName);
    
    // CRITICAL SECURITY: Filter data by organization_id
    // Super admins see all data, regular users only see their org's data
    const filteredData = userContext.isSuperAdmin 
      ? data 
      : data.filter(item => item.organization_id === userContext.organizationId);
    
    // console.log(`[IndexedDB] Retrieved ${filteredData.length} items from ${storeName} for user ${userContext.userId} (org: ${userContext.organizationId})`);
    return filteredData;
  } catch (error) {
    console.error(`[IndexedDB] Failed to get cached data from ${storeName}:`, error);
    return [];
  }
}

/**
 * Get a single item from cache by ID
 */
export async function getCachedItem(storeName, id) {
  try {
    const db = await getDB();
    const item = await db.get(storeName, id);
    return item;
  } catch (error) {
    console.error(`[IndexedDB] Failed to get item from ${storeName}:`, error);
    return null;
  }
}

/**
 * Get items from cache by index
 */
export async function getCachedItemsByIndex(storeName, indexName, value) {
  try {
    const db = await getDB();
    const items = await db.getAllFromIndex(storeName, indexName, value);
    return items;
  } catch (error) {
    console.error(`[IndexedDB] Failed to get items by index from ${storeName}:`, error);
    return [];
  }
}

/**
 * Clear all data from a cache store for a specific user
 */
export async function clearCache(storeName, userContext = null) {
  try {
    const db = await getDB();
    
    if (!userContext) {
      // Clear all cache if no user context (e.g., on logout)
      await db.clear(storeName);
      // console.log(`[IndexedDB] Cleared all cache for ${storeName}`);
    } else {
      // Clear only this user's cached metadata
      const cacheKey = getUserCacheKey(storeName, userContext.userId, userContext.organizationId);
      await db.delete(STORES.CACHE_METADATA, cacheKey);
      // console.log(`[IndexedDB] Cleared cache metadata for ${storeName} user ${userContext.userId}`);
    }
  } catch (error) {
    console.error(`[IndexedDB] Failed to clear cache for ${storeName}:`, error);
  }
}

/**
 * Update cache metadata (last updated timestamp) with user context
 */
async function updateCacheMetadata(storeName, userContext) {
  try {
    const db = await getDB();
    const cacheKey = getUserCacheKey(storeName, userContext.userId, userContext.organizationId);
    await db.put(STORES.CACHE_METADATA, {
      key: cacheKey,
      timestamp: Date.now(),
      userId: userContext.userId,
      organizationId: userContext.organizationId,
    });
  } catch (error) {
    console.error('[IndexedDB] Failed to update cache metadata:', error);
  }
}

/**
 * Get cache metadata with user context
 */
export async function getCacheMetadata(storeName, userContext = null) {
  try {
    if (!userContext || !userContext.userId || !userContext.organizationId) {
      return null;
    }
    
    const db = await getDB();
    const cacheKey = getUserCacheKey(storeName, userContext.userId, userContext.organizationId);
    const metadata = await db.get(STORES.CACHE_METADATA, cacheKey);
    return metadata;
  } catch (error) {
    console.error('[IndexedDB] Failed to get cache metadata:', error);
    return null;
  }
}

/**
 * Check if cache is stale (older than maxAge in milliseconds) for specific user
 */
export async function isCacheStale(storeName, userContext = null, maxAge = 24 * 60 * 60 * 1000) {
  if (!userContext) return true;
  
  const metadata = await getCacheMetadata(storeName, userContext);
  if (!metadata) return true;
  
  const age = Date.now() - metadata.timestamp;
  return age > maxAge;
}

// ============================================================================
// OFFLINE OPERATIONS
// ============================================================================

/**
 * Save offline net cleaning record
 */
export async function saveOfflineNetCleaningRecord(record) {
  try {
    const db = await getDB();
    const tempId = `temp_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    
    const offlineRecord = {
      ...record,
      tempId,
      synced: false,
      timestamp: Date.now(),
    };
    
    await db.put(STORES.NET_CLEANING_RECORDS, offlineRecord);
    // console.log('[IndexedDB] Saved offline net cleaning record:', tempId);
    
    return tempId;
  } catch (error) {
    console.error('[IndexedDB] Failed to save offline net cleaning record:', error);
    throw error;
  }
}

/**
 * Save offline net cleaning photo
 */
export async function saveOfflineNetCleaningPhoto(recordTempId, photoBlob, filename) {
  try {
    const db = await getDB();
    
    const photoRecord = {
      recordTempId,
      blob: photoBlob,
      filename,
      synced: false,
      timestamp: Date.now(),
    };
    
    const id = await db.add(STORES.NET_CLEANING_PHOTOS, photoRecord);
    // console.log('[IndexedDB] Saved offline photo:', id);
    
    return id;
  } catch (error) {
    console.error('[IndexedDB] Failed to save offline photo:', error);
    throw error;
  }
}

/**
 * Get all unsynced net cleaning records
 */
export async function getUnsyncedNetCleaningRecords() {
  try {
    const db = await getDB();
    const tx = db.transaction(STORES.NET_CLEANING_RECORDS, 'readonly');
    const store = tx.objectStore(STORES.NET_CLEANING_RECORDS);
    const allRecords = await store.getAll();
    
    // Filter for unsynced records
    const unsyncedRecords = allRecords.filter(record => record.synced === false);
    return unsyncedRecords;
  } catch (error) {
    console.error('[IndexedDB] Failed to get unsynced records:', error);
    return [];
  }
}

/**
 * Get photos for a net cleaning record
 */
export async function getPhotosForRecord(recordTempId) {
  try {
    const db = await getDB();
    const photos = await db.getAllFromIndex(STORES.NET_CLEANING_PHOTOS, 'recordTempId', recordTempId);
    return photos;
  } catch (error) {
    console.error('[IndexedDB] Failed to get photos for record:', error);
    return [];
  }
}

/**
 * Mark net cleaning record as synced
 */
export async function markRecordAsSynced(tempId, serverId) {
  try {
    const db = await getDB();
    const record = await db.get(STORES.NET_CLEANING_RECORDS, tempId);
    
    if (record) {
      record.synced = true;
      record.serverId = serverId;
      record.syncedAt = Date.now();
      await db.put(STORES.NET_CLEANING_RECORDS, record);
      // console.log('[IndexedDB] Marked record as synced:', tempId);
    }
  } catch (error) {
    console.error('[IndexedDB] Failed to mark record as synced:', error);
  }
}

/**
 * Mark photo as synced
 */
export async function markPhotoAsSynced(photoId) {
  try {
    const db = await getDB();
    const photo = await db.get(STORES.NET_CLEANING_PHOTOS, photoId);
    
    if (photo) {
      photo.synced = true;
      photo.syncedAt = Date.now();
      await db.put(STORES.NET_CLEANING_PHOTOS, photo);
      // console.log('[IndexedDB] Marked photo as synced:', photoId);
    }
  } catch (error) {
    console.error('[IndexedDB] Failed to mark photo as synced:', error);
  }
}

/**
 * Delete synced records older than specified days
 */
export async function cleanupSyncedRecords(daysOld = 7) {
  try {
    const db = await getDB();
    const cutoffTime = Date.now() - (daysOld * 24 * 60 * 60 * 1000);
    
    // Clean up net cleaning records
    const records = await db.getAll(STORES.NET_CLEANING_RECORDS);
    const tx = db.transaction(STORES.NET_CLEANING_RECORDS, 'readwrite');
    
    for (const record of records) {
      if (record.synced && record.syncedAt < cutoffTime) {
        await tx.store.delete(record.tempId);
      }
    }
    
    await tx.done;
    // console.log('[IndexedDB] Cleaned up old synced records');
  } catch (error) {
    console.error('[IndexedDB] Failed to cleanup synced records:', error);
  }
}

// ============================================================================
// OFFLINE MAINTENANCE EXECUTIONS
// ============================================================================

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
    // console.log('[IndexedDB] Saved offline maintenance execution:', tempId);
    
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
      // console.log('[IndexedDB] Updated offline execution completion:', tempId);
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
      // console.log('[IndexedDB] Marked execution as synced:', tempId);
    }
  } catch (error) {
    console.error('[IndexedDB] Failed to mark execution as synced:', error);
  }
}

// ============================================================================
// SYNC QUEUE OPERATIONS
// ============================================================================

/**
 * Add operation to sync queue
 */
export async function addToSyncQueue(operation) {
  try {
    const db = await getDB();
    
    const queueItem = {
      ...operation,
      timestamp: Date.now(),
      status: 'pending',
      retryCount: 0,
    };
    
    const id = await db.add(STORES.SYNC_QUEUE, queueItem);
    // console.log('[IndexedDB] Added operation to sync queue:', id);
    
    return id;
  } catch (error) {
    console.error('[IndexedDB] Failed to add to sync queue:', error);
    throw error;
  }
}

/**
 * Get all pending sync operations
 */
export async function getPendingSyncOperations() {
  try {
    const db = await getDB();
    const operations = await db.getAllFromIndex(STORES.SYNC_QUEUE, 'status', 'pending');
    return operations.sort((a, b) => a.timestamp - b.timestamp);
  } catch (error) {
    console.error('[IndexedDB] Failed to get pending sync operations:', error);
    return [];
  }
}

/**
 * Update sync operation status
 */
export async function updateSyncOperationStatus(id, status, error = null) {
  try {
    const db = await getDB();
    const operation = await db.get(STORES.SYNC_QUEUE, id);
    
    if (operation) {
      operation.status = status;
      operation.lastAttempt = Date.now();
      
      if (error) {
        operation.error = error;
        operation.retryCount = (operation.retryCount || 0) + 1;
      }
      
      await db.put(STORES.SYNC_QUEUE, operation);
      // console.log(`[IndexedDB] Updated sync operation ${id} status to ${status}`);
    }
  } catch (error) {
    console.error('[IndexedDB] Failed to update sync operation status:', error);
  }
}

/**
 * Delete sync operation
 */
export async function deleteSyncOperation(id) {
  try {
    const db = await getDB();
    await db.delete(STORES.SYNC_QUEUE, id);
    // console.log('[IndexedDB] Deleted sync operation:', id);
  } catch (error) {
    console.error('[IndexedDB] Failed to delete sync operation:', error);
  }
}

// ============================================================================
// UTILITY FUNCTIONS
// ============================================================================

/**
 * Get database storage usage estimate
 */
export async function getStorageEstimate() {
  if ('storage' in navigator && 'estimate' in navigator.storage) {
    const estimate = await navigator.storage.estimate();
    return {
      usage: estimate.usage,
      quota: estimate.quota,
      percentUsed: (estimate.usage / estimate.quota) * 100,
    };
  }
  return null;
}

/**
 * Clear all offline data
 */
export async function clearAllOfflineData() {
  try {
    const db = await getDB();
    
    // Clear all stores
    for (const storeName of Object.values(STORES)) {
      await db.clear(storeName);
    }
    
    console.log('[IndexedDB] ✓ Cleared all offline data');
  } catch (error) {
    console.error('[IndexedDB] Failed to clear all offline data:', error);
  }
}

/**
 * Clear all cached data (but keep offline operations)
 * Use this on login to force fresh data from server
 */
export async function clearAllCachedData() {
  try {
    const db = await getDB();
    
    // Clear only cached data stores (not offline operations)
    const cachedStores = [
      STORES.FARM_SITES,
      STORES.NETS,
      STORES.MACHINES,
      STORES.PROTOCOLS,
      STORES.PARTS,
      STORES.USERS,
      STORES.CACHE_METADATA,
    ];
    
    for (const storeName of cachedStores) {
      await db.clear(storeName);
    }
    
    console.log('[IndexedDB] ✓ Cleared all cached data (offline operations preserved)');
  } catch (error) {
    console.error('[IndexedDB] Failed to clear cached data:', error);
  }
}

/**
 * Get cache statistics
 */
export async function getCacheStats() {
  try {
    const db = await getDB();
    const stats = {};
    
    for (const [key, storeName] of Object.entries(STORES)) {
      const count = await db.count(storeName);
      stats[key] = count;
    }
    
    return stats;
  } catch (error) {
    console.error('[IndexedDB] Failed to get cache stats:', error);
    return {};
  }
}

// Export store names for use in other modules
export { STORES };
