// Sync Queue Manager
// Manages the queue of offline operations waiting to be synced

import {
  addToSyncQueue,
  getPendingSyncOperations,
  updateSyncOperationStatus,
  deleteSyncOperation,
} from '../db/indexedDB';

/**
 * Operation types that can be queued for sync
 */
export const OPERATION_TYPES = {
  NET_CLEANING_RECORD: 'net_cleaning_record',
  NET_CLEANING_PHOTO: 'net_cleaning_photo',
  MAINTENANCE_EXECUTION: 'maintenance_execution',
  MACHINE_HOURS: 'machine_hours',
  STOCK_ADJUSTMENT: 'stock_adjustment',
};

/**
 * Operation status values
 */
export const OPERATION_STATUS = {
  PENDING: 'pending',
  SYNCING: 'syncing',
  COMPLETED: 'completed',
  FAILED: 'failed',
};

/**
 * Add a net cleaning record to sync queue
 * 
 * @param {string} tempId - Temporary ID of the offline record
 * @param {Object} data - Record data to sync
 * @returns {Promise<number>} Queue item ID
 */
export async function queueNetCleaningRecord(tempId, data) {
  try {
    const operation = {
      type: OPERATION_TYPES.NET_CLEANING_RECORD,
      endpoint: '/net-cleaning-records',
      method: 'POST',
      data,
      tempId,
      priority: 1, // Higher priority for main records
    };
    
    const id = await addToSyncQueue(operation);
    // console.log('[SyncQueue] Queued net cleaning record:', id);
    
    // Dispatch event to notify UI
    window.dispatchEvent(new CustomEvent('offline-data-saved'));
    
    return id;
  } catch (error) {
    console.error('[SyncQueue] Failed to queue net cleaning record:', error);
    throw error;
  }
}

/**
 * Add a net cleaning photo to sync queue
 * 
 * @param {string} recordTempId - Temporary ID of the parent record
 * @param {Blob} photoBlob - Photo blob data
 * @param {string} filename - Photo filename
 * @returns {Promise<number>} Queue item ID
 */
export async function queueNetCleaningPhoto(recordTempId, photoBlob, filename) {
  try {
    const operation = {
      type: OPERATION_TYPES.NET_CLEANING_PHOTO,
      endpoint: '/net-cleaning-records/photos',
      method: 'POST',
      data: {
        recordTempId,
        photoBlob,
        filename,
      },
      tempId: `photo_${recordTempId}_${Date.now()}`,
      priority: 2, // Lower priority than main records
    };
    
    const id = await addToSyncQueue(operation);
    // console.log('[SyncQueue] Queued net cleaning photo:', id);
    
    return id;
  } catch (error) {
    console.error('[SyncQueue] Failed to queue net cleaning photo:', error);
    throw error;
  }
}

/**
 * Add a maintenance execution to sync queue
 * 
 * @param {string} tempId - Temporary ID of the offline execution
 * @param {Object} data - Execution data to sync
 * @returns {Promise<number>} Queue item ID
 */
export async function queueMaintenanceExecution(tempId, data) {
  try {
    const operation = {
      type: OPERATION_TYPES.MAINTENANCE_EXECUTION,
      endpoint: '/maintenance-protocols/executions',
      method: 'POST',
      data,
      tempId,
      priority: 1,
    };
    
    const id = await addToSyncQueue(operation);
    // console.log('[SyncQueue] Queued maintenance execution:', id);
    
    window.dispatchEvent(new CustomEvent('offline-data-saved'));
    
    return id;
  } catch (error) {
    console.error('[SyncQueue] Failed to queue maintenance execution:', error);
    throw error;
  }
}

/**
 * Add machine hours update to sync queue
 * 
 * @param {string} tempId - Temporary ID of the offline hours record
 * @param {Object} data - Hours data to sync
 * @returns {Promise<number>} Queue item ID
 */
export async function queueMachineHours(tempId, data) {
  try {
    const operation = {
      type: OPERATION_TYPES.MACHINE_HOURS,
      endpoint: '/machines/hours',
      method: 'POST',
      data,
      tempId,
      priority: 3, // Lower priority
    };
    
    const id = await addToSyncQueue(operation);
    // console.log('[SyncQueue] Queued machine hours:', id);
    
    window.dispatchEvent(new CustomEvent('offline-data-saved'));
    
    return id;
  } catch (error) {
    console.error('[SyncQueue] Failed to queue machine hours:', error);
    throw error;
  }
}

/**
 * Get all pending operations from the queue
 * Sorted by priority (higher first) and timestamp (older first)
 * 
 * @returns {Promise<Array>} Array of pending operations
 */
export async function getPendingOperations() {
  try {
    const operations = await getPendingSyncOperations();
    
    // Sort by priority (descending) then timestamp (ascending)
    operations.sort((a, b) => {
      if (a.priority !== b.priority) {
        return b.priority - a.priority; // Higher priority first
      }
      return a.timestamp - b.timestamp; // Older first
    });
    
    // console.log(`[SyncQueue] Retrieved ${operations.length} pending operations`);
    return operations;
  } catch (error) {
    console.error('[SyncQueue] Failed to get pending operations:', error);
    return [];
  }
}

/**
 * Mark an operation as syncing
 * 
 * @param {number} id - Queue item ID
 * @returns {Promise<void>}
 */
export async function markOperationSyncing(id) {
  try {
    await updateSyncOperationStatus(id, OPERATION_STATUS.SYNCING);
    // console.log('[SyncQueue] Marked operation as syncing:', id);
  } catch (error) {
    console.error('[SyncQueue] Failed to mark operation as syncing:', error);
  }
}

/**
 * Mark an operation as completed and remove from queue
 * 
 * @param {number} id - Queue item ID
 * @returns {Promise<void>}
 */
export async function markOperationCompleted(id) {
  try {
    await deleteSyncOperation(id);
    // console.log('[SyncQueue] Marked operation as completed and removed:', id);
    
    // Dispatch event to update UI
    window.dispatchEvent(new CustomEvent('offline-data-synced'));
  } catch (error) {
    console.error('[SyncQueue] Failed to mark operation as completed:', error);
  }
}

/**
 * Mark an operation as failed
 * 
 * @param {number} id - Queue item ID
 * @param {string} error - Error message
 * @returns {Promise<void>}
 */
export async function markOperationFailed(id, error) {
  try {
    await updateSyncOperationStatus(id, OPERATION_STATUS.FAILED, error);
    // console.log('[SyncQueue] Marked operation as failed:', id, error);
  } catch (error) {
    console.error('[SyncQueue] Failed to mark operation as failed:', error);
  }
}

/**
 * Retry a failed operation by resetting its status to pending
 * 
 * @param {number} id - Queue item ID
 * @returns {Promise<void>}
 */
export async function retryOperation(id) {
  try {
    await updateSyncOperationStatus(id, OPERATION_STATUS.PENDING);
    // console.log('[SyncQueue] Reset operation to pending for retry:', id);
  } catch (error) {
    console.error('[SyncQueue] Failed to retry operation:', error);
  }
}

/**
 * Get count of pending operations by type
 * 
 * @returns {Promise<Object>} Count by operation type
 */
export async function getPendingCountByType() {
  try {
    const operations = await getPendingSyncOperations();
    
    const counts = operations.reduce((acc, op) => {
      acc[op.type] = (acc[op.type] || 0) + 1;
      return acc;
    }, {});
    
    // console.log('[SyncQueue] Pending counts by type:', counts);
    return counts;
  } catch (error) {
    console.error('[SyncQueue] Failed to get pending counts:', error);
    return {};
  }
}

/**
 * Clear all completed operations from queue
 * (Normally they're deleted immediately, but this is a cleanup function)
 * 
 * @returns {Promise<number>} Number of operations cleared
 */
export async function clearCompletedOperations() {
  try {
    const operations = await getPendingSyncOperations();
    let cleared = 0;
    
    for (const op of operations) {
      if (op.status === OPERATION_STATUS.COMPLETED) {
        await deleteSyncOperation(op.id);
        cleared++;
      }
    }
    
    // console.log(`[SyncQueue] Cleared ${cleared} completed operations`);
    return cleared;
  } catch (error) {
    console.error('[SyncQueue] Failed to clear completed operations:', error);
    return 0;
  }
}

/**
 * Get operations that have failed too many times (max retries exceeded)
 * 
 * @param {number} maxRetries - Maximum retry count (default: 3)
 * @returns {Promise<Array>} Array of operations that exceeded max retries
 */
export async function getFailedOperations(maxRetries = 3) {
  try {
    const operations = await getPendingSyncOperations();
    
    const failed = operations.filter(op => 
      op.status === OPERATION_STATUS.FAILED && 
      op.retryCount >= maxRetries
    );
    
    // console.log(`[SyncQueue] Found ${failed.length} operations that exceeded max retries`);
    return failed;
  } catch (error) {
    console.error('[SyncQueue] Failed to get failed operations:', error);
    return [];
  }
}

/**
 * Remove an operation from the queue
 * Use with caution - typically only for manual cleanup
 * 
 * @param {number} id - Queue item ID
 * @returns {Promise<void>}
 */
export async function removeOperation(id) {
  try {
    await deleteSyncOperation(id);
    // console.log('[SyncQueue] Removed operation from queue:', id);
    
    window.dispatchEvent(new CustomEvent('offline-data-synced'));
  } catch (error) {
    console.error('[SyncQueue] Failed to remove operation:', error);
  }
}

/**
 * Get summary of sync queue status
 * 
 * @returns {Promise<Object>} Queue status summary
 */
export async function getQueueStatus() {
  try {
    const operations = await getPendingSyncOperations();
    
    const status = {
      total: operations.length,
      pending: operations.filter(op => op.status === OPERATION_STATUS.PENDING).length,
      syncing: operations.filter(op => op.status === OPERATION_STATUS.SYNCING).length,
      failed: operations.filter(op => op.status === OPERATION_STATUS.FAILED).length,
      byType: {},
    };
    
    // Count by type
    operations.forEach(op => {
      status.byType[op.type] = (status.byType[op.type] || 0) + 1;
    });
    
    // console.log('[SyncQueue] Queue status:', status);
    return status;
  } catch (error) {
    console.error('[SyncQueue] Failed to get queue status:', error);
    return {
      total: 0,
      pending: 0,
      syncing: 0,
      failed: 0,
      byType: {},
    };
  }
}

export default {
  // Queue operations
  queueNetCleaningRecord,
  queueNetCleaningPhoto,
  queueMaintenanceExecution,
  queueMachineHours,
  
  // Get operations
  getPendingOperations,
  getPendingCountByType,
  getFailedOperations,
  getQueueStatus,
  
  // Update operations
  markOperationSyncing,
  markOperationCompleted,
  markOperationFailed,
  retryOperation,
  removeOperation,
  
  // Cleanup
  clearCompletedOperations,
  
  // Constants
  OPERATION_TYPES,
  OPERATION_STATUS,
};
