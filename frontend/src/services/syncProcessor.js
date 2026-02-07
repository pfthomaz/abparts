// Sync Processor
// Processes the sync queue and sends offline data to the server

import {
  getPendingOperations,
  markOperationSyncing,
  markOperationCompleted,
  markOperationFailed,
  OPERATION_TYPES,
} from './syncQueueManager';

import {
  getUnsyncedNetCleaningRecords,
  getPhotosForRecord,
  markRecordAsSynced,
  markPhotoAsSynced,
  getUnsyncedMaintenanceExecutions,
  markExecutionAsSynced,
} from '../db/indexedDB';

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000';
const MAX_RETRIES = 3;
const RETRY_DELAY = 2000; // 2 seconds between retries

/**
 * Main sync function - processes all pending operations
 * Called automatically when connection is restored
 * 
 * @returns {Promise<Object>} Sync results summary
 */
export async function processSync() {
  console.log('[SyncProcessor] Starting sync process...');
  
  const results = {
    total: 0,
    succeeded: 0,
    failed: 0,
    errors: [],
  };
  
  try {
    // Get auth token
    const token = localStorage.getItem('authToken');
    if (!token) {
      console.error('[SyncProcessor] No auth token found');
      return results;
    }
    
    // Process net cleaning records first (they're the priority)
    const netCleaningResults = await syncNetCleaningRecords(token);
    results.total += netCleaningResults.total;
    results.succeeded += netCleaningResults.succeeded;
    results.failed += netCleaningResults.failed;
    results.errors.push(...netCleaningResults.errors);
    
    // Process maintenance executions
    const maintenanceResults = await syncMaintenanceExecutions(token);
    results.total += maintenanceResults.total;
    results.succeeded += maintenanceResults.succeeded;
    results.failed += maintenanceResults.failed;
    results.errors.push(...maintenanceResults.errors);
    
    // Process sync queue operations
    const queueResults = await processSyncQueue(token);
    results.total += queueResults.total;
    results.succeeded += queueResults.succeeded;
    results.failed += queueResults.failed;
    results.errors.push(...queueResults.errors);
    
    console.log('[SyncProcessor] Sync complete:', results);
    return results;
    
  } catch (error) {
    console.error('[SyncProcessor] Sync process failed:', error);
    results.errors.push(error.message);
    return results;
  }
}

/**
 * Sync net cleaning records from IndexedDB
 * 
 * @param {string} token - Auth token
 * @returns {Promise<Object>} Sync results
 */
async function syncNetCleaningRecords(token) {
  const results = {
    total: 0,
    succeeded: 0,
    failed: 0,
    errors: [],
  };
  
  try {
    // Get all unsynced records
    const records = await getUnsyncedNetCleaningRecords();
    results.total = records.length;
    
    console.log(`[SyncProcessor] Syncing ${records.length} net cleaning records...`);
    
    for (const record of records) {
      try {
        // Sync the main record
        const serverId = await syncSingleNetCleaningRecord(record, token);
        
        if (serverId) {
          // Mark record as synced
          await markRecordAsSynced(record.tempId, serverId);
          
          // Sync photos for this record
          await syncPhotosForRecord(record.tempId, serverId, token);
          
          results.succeeded++;
          console.log(`[SyncProcessor] Synced record ${record.tempId} -> ${serverId}`);
        } else {
          results.failed++;
          results.errors.push(`Failed to sync record ${record.tempId}`);
        }
        
      } catch (error) {
        console.error(`[SyncProcessor] Failed to sync record ${record.tempId}:`, error);
        results.failed++;
        results.errors.push(`Record ${record.tempId}: ${error.message}`);
      }
    }
    
  } catch (error) {
    console.error('[SyncProcessor] Failed to sync net cleaning records:', error);
    results.errors.push(error.message);
  }
  
  return results;
}

/**
 * Sync a single net cleaning record
 * 
 * @param {Object} record - Record data
 * @param {string} token - Auth token
 * @returns {Promise<string|null>} Server ID or null if failed
 */
async function syncSingleNetCleaningRecord(record, token) {
  try {
    // Prepare data for API (remove temp fields)
    const { tempId, synced, timestamp, ...apiData } = record;
    
    const response = await fetch(`${API_BASE_URL}/net-cleaning-records/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
      },
      body: JSON.stringify(apiData),
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to create record');
    }
    
    const data = await response.json();
    return data.id;
    
  } catch (error) {
    console.error('[SyncProcessor] Failed to sync record:', error);
    throw error;
  }
}

/**
 * Sync photos for a net cleaning record
 * 
 * @param {string} recordTempId - Temporary record ID
 * @param {string} serverId - Server record ID
 * @param {string} token - Auth token
 * @returns {Promise<void>}
 */
async function syncPhotosForRecord(recordTempId, serverId, token) {
  try {
    const photos = await getPhotosForRecord(recordTempId);
    
    console.log(`[SyncProcessor] Syncing ${photos.length} photos for record ${serverId}...`);
    
    for (const photo of photos) {
      try {
        await syncSinglePhoto(serverId, photo, token);
        await markPhotoAsSynced(photo.id);
        console.log(`[SyncProcessor] Synced photo ${photo.id}`);
      } catch (error) {
        console.error(`[SyncProcessor] Failed to sync photo ${photo.id}:`, error);
        // Continue with other photos even if one fails
      }
    }
    
  } catch (error) {
    console.error('[SyncProcessor] Failed to sync photos:', error);
  }
}

/**
 * Sync maintenance executions from IndexedDB
 * 
 * @param {string} token - Auth token
 * @returns {Promise<Object>} Sync results
 */
async function syncMaintenanceExecutions(token) {
  const results = {
    total: 0,
    succeeded: 0,
    failed: 0,
    errors: [],
  };
  
  try {
    // Get all unsynced executions
    const executions = await getUnsyncedMaintenanceExecutions();
    results.total = executions.length;
    
    console.log(`[SyncProcessor] Syncing ${executions.length} maintenance executions...`);
    
    for (const execution of executions) {
      try {
        // Sync the execution
        const serverId = await syncSingleMaintenanceExecution(execution, token);
        
        if (serverId) {
          // Mark execution as synced
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
 * 
 * @param {Object} execution - Execution data
 * @param {string} token - Auth token
 * @returns {Promise<string|null>} Server ID or null if failed
 */
async function syncSingleMaintenanceExecution(execution, token) {
  try {
    // Prepare data for API (remove temp fields, nested objects, and checklist_completions)
    // Keep status, protocol_id, machine_id, machine_hours_at_service, etc.
    const { tempId, synced, timestamp, protocol, machine, checklist_completions, organization_id, created_at, completed_at, ...apiData } = execution;
    
    console.log('[SyncProcessor] Syncing execution with data:', apiData);
    
    // Create execution with the correct status
    const response = await fetch(`${API_BASE_URL}/maintenance-protocols/executions`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
      },
      body: JSON.stringify(apiData),
    });
    
    if (!response.ok) {
      const errorText = await response.text();
      console.error('[SyncProcessor] Server error response:', errorText);
      let errorDetail;
      try {
        const errorJson = JSON.parse(errorText);
        errorDetail = errorJson.detail || errorText;
      } catch {
        errorDetail = errorText;
      }
      throw new Error(errorDetail || 'Failed to create execution');
    }
    
    const data = await response.json();
    const executionId = data.id;
    
    console.log(`[SyncProcessor] Created execution ${executionId} with status: ${apiData.status}`);
    
    // Sync checklist completions if any
    if (checklist_completions && checklist_completions.length > 0) {
      console.log(`[SyncProcessor] Syncing ${checklist_completions.length} checklist completions...`);
      for (const completion of checklist_completions) {
        try {
          await syncChecklistCompletion(executionId, completion, token);
          console.log(`[SyncProcessor] Synced checklist item ${completion.checklist_item_id}`);
        } catch (error) {
          console.error(`[SyncProcessor] Failed to sync checklist completion:`, error);
          // Continue with other completions
        }
      }
    }
    
    return executionId;
    
  } catch (error) {
    console.error('[SyncProcessor] Failed to sync execution:', error);
    throw error;
  }
}

/**
 * Sync a single checklist completion
 * 
 * @param {string} executionId - Server execution ID
 * @param {Object} completion - Completion data
 * @param {string} token - Auth token
 * @returns {Promise<void>}
 */
async function syncChecklistCompletion(executionId, completion, token) {
  try {
    const response = await fetch(
      `${API_BASE_URL}/maintenance-protocols/executions/${executionId}/checklist/${completion.checklist_item_id}/complete`,
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({
          status: completion.status,
          notes: completion.notes,
          actual_quantity_used: completion.actual_quantity_used,
        }),
      }
    );
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to sync checklist completion');
    }
    
  } catch (error) {
    console.error('[SyncProcessor] Failed to sync checklist completion:', error);
    throw error;
  }
}

/**
 * Sync a single photo
 * 
 * @param {string} recordId - Server record ID
 * @param {Object} photo - Photo data with blob
 * @param {string} token - Auth token
 * @returns {Promise<void>}
 */
async function syncSinglePhoto(recordId, photo, token) {
  try {
    // Create FormData for file upload
    const formData = new FormData();
    formData.append('file', photo.blob, photo.filename);
    formData.append('record_id', recordId);
    
    const response = await fetch(`${API_BASE_URL}/net-cleaning-records/${recordId}/photos`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
      },
      body: formData,
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to upload photo');
    }
    
  } catch (error) {
    console.error('[SyncProcessor] Failed to sync photo:', error);
    throw error;
  }
}

/**
 * Process operations from the sync queue
 * 
 * @param {string} token - Auth token
 * @returns {Promise<Object>} Sync results
 */
async function processSyncQueue(token) {
  const results = {
    total: 0,
    succeeded: 0,
    failed: 0,
    errors: [],
  };
  
  try {
    const operations = await getPendingOperations();
    results.total = operations.length;
    
    console.log(`[SyncProcessor] Processing ${operations.length} queue operations...`);
    
    for (const operation of operations) {
      try {
        // Mark as syncing
        await markOperationSyncing(operation.id);
        
        // Process based on type
        let success = false;
        
        switch (operation.type) {
          case OPERATION_TYPES.MAINTENANCE_EXECUTION:
            success = await syncMaintenanceExecution(operation, token);
            break;
            
          case OPERATION_TYPES.MACHINE_HOURS:
            success = await syncMachineHours(operation, token);
            break;
            
          case OPERATION_TYPES.STOCK_ADJUSTMENT:
            success = await syncStockAdjustment(operation, token);
            break;
            
          default:
            console.warn(`[SyncProcessor] Unknown operation type: ${operation.type}`);
            success = false;
        }
        
        if (success) {
          await markOperationCompleted(operation.id);
          results.succeeded++;
          console.log(`[SyncProcessor] Completed operation ${operation.id}`);
        } else {
          await markOperationFailed(operation.id, 'Sync failed');
          results.failed++;
          results.errors.push(`Operation ${operation.id}: Sync failed`);
        }
        
      } catch (error) {
        console.error(`[SyncProcessor] Failed to process operation ${operation.id}:`, error);
        await markOperationFailed(operation.id, error.message);
        results.failed++;
        results.errors.push(`Operation ${operation.id}: ${error.message}`);
      }
    }
    
  } catch (error) {
    console.error('[SyncProcessor] Failed to process sync queue:', error);
    results.errors.push(error.message);
  }
  
  return results;
}

/**
 * Sync a maintenance execution
 * 
 * @param {Object} operation - Queue operation
 * @param {string} token - Auth token
 * @returns {Promise<boolean>} Success status
 */
async function syncMaintenanceExecution(operation, token) {
  try {
    const response = await fetch(`${API_BASE_URL}${operation.endpoint}`, {
      method: operation.method,
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
      },
      body: JSON.stringify(operation.data),
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to sync maintenance execution');
    }
    
    return true;
    
  } catch (error) {
    console.error('[SyncProcessor] Failed to sync maintenance execution:', error);
    
    // Retry logic
    if (operation.retryCount < MAX_RETRIES) {
      console.log(`[SyncProcessor] Retrying operation ${operation.id}...`);
      await new Promise(resolve => setTimeout(resolve, RETRY_DELAY));
      return false; // Will be retried
    }
    
    throw error;
  }
}

/**
 * Sync machine hours update
 * 
 * @param {Object} operation - Queue operation
 * @param {string} token - Auth token
 * @returns {Promise<boolean>} Success status
 */
async function syncMachineHours(operation, token) {
  try {
    const response = await fetch(`${API_BASE_URL}${operation.endpoint}`, {
      method: operation.method,
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
      },
      body: JSON.stringify(operation.data),
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to sync machine hours');
    }
    
    return true;
    
  } catch (error) {
    console.error('[SyncProcessor] Failed to sync machine hours:', error);
    
    if (operation.retryCount < MAX_RETRIES) {
      await new Promise(resolve => setTimeout(resolve, RETRY_DELAY));
      return false;
    }
    
    throw error;
  }
}

/**
 * Sync stock adjustment
 * 
 * @param {Object} operation - Queue operation
 * @param {string} token - Auth token
 * @returns {Promise<boolean>} Success status
 */
async function syncStockAdjustment(operation, token) {
  try {
    const response = await fetch(`${API_BASE_URL}${operation.endpoint}`, {
      method: operation.method,
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
      },
      body: JSON.stringify(operation.data),
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to sync stock adjustment');
    }
    
    return true;
    
  } catch (error) {
    console.error('[SyncProcessor] Failed to sync stock adjustment:', error);
    
    if (operation.retryCount < MAX_RETRIES) {
      await new Promise(resolve => setTimeout(resolve, RETRY_DELAY));
      return false;
    }
    
    throw error;
  }
}

/**
 * Check if sync is needed
 * 
 * @returns {Promise<boolean>} True if there are pending operations
 */
export async function isSyncNeeded() {
  try {
    const records = await getUnsyncedNetCleaningRecords();
    const operations = await getPendingOperations();
    
    const needed = records.length > 0 || operations.length > 0;
    console.log(`[SyncProcessor] Sync needed: ${needed} (${records.length} records, ${operations.length} operations)`);
    
    return needed;
  } catch (error) {
    console.error('[SyncProcessor] Failed to check if sync needed:', error);
    return false;
  }
}

/**
 * Get sync status summary
 * 
 * @returns {Promise<Object>} Status summary
 */
export async function getSyncStatus() {
  try {
    const records = await getUnsyncedNetCleaningRecords();
    const operations = await getPendingOperations();
    
    return {
      netCleaningRecords: records.length,
      queueOperations: operations.length,
      total: records.length + operations.length,
    };
  } catch (error) {
    console.error('[SyncProcessor] Failed to get sync status:', error);
    return {
      netCleaningRecords: 0,
      queueOperations: 0,
      total: 0,
    };
  }
}

export default {
  processSync,
  isSyncNeeded,
  getSyncStatus,
};
