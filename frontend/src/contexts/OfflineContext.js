// OfflineContext - Manages offline state and sync operations
// Provides global offline status, pending operations count, and sync functions

import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { useNetworkStatus } from '../hooks/useNetworkStatus';
import {
  getUnsyncedNetCleaningRecords,
  getPendingSyncOperations,
  getStorageEstimate,
} from '../db/indexedDB';
import { processSync } from '../services/syncProcessor';

const OfflineContext = createContext(null);

export const useOffline = () => {
  const context = useContext(OfflineContext);
  if (!context) {
    throw new Error('useOffline must be used within an OfflineProvider');
  }
  return context;
};

export const OfflineProvider = ({ children }) => {
  // Network status from hook
  const { isOnline, wasOffline, offlineDuration } = useNetworkStatus();
  
  // Offline state
  const [pendingCount, setPendingCount] = useState(0);
  const [isSyncing, setIsSyncing] = useState(false);
  const [lastSyncTime, setLastSyncTime] = useState(null);
  const [syncError, setSyncError] = useState(null);
  const [storageInfo, setStorageInfo] = useState(null);
  
  // Track if we should show "back online" message
  const [showBackOnline, setShowBackOnline] = useState(false);

  /**
   * Update pending operations count
   */
  const updatePendingCount = useCallback(async () => {
    try {
      // Get unsynced net cleaning records
      const unsyncedRecords = await getUnsyncedNetCleaningRecords();
      
      // Get unsynced maintenance executions
      const { getUnsyncedMaintenanceExecutions } = await import('../db/indexedDB');
      const unsyncedExecutions = await getUnsyncedMaintenanceExecutions();
      
      // Get pending sync queue operations
      const pendingOps = await getPendingSyncOperations();
      
      // Total pending count
      const total = unsyncedRecords.length + unsyncedExecutions.length + pendingOps.length;
      setPendingCount(total);
      
      // console.log('[OfflineContext] Pending operations:', total);
      // console.log('  - Unsynced net cleaning records:', unsyncedRecords.length);
      // console.log('  - Unsynced maintenance executions:', unsyncedExecutions.length);
      // console.log('  - Pending sync queue operations:', pendingOps.length);
      
      return total;
    } catch (error) {
      // console.error('[OfflineContext] Failed to update pending count:', error);
      return 0;
    }
  }, []);

  /**
   * Update storage information
   */
  const updateStorageInfo = useCallback(async () => {
    try {
      const estimate = await getStorageEstimate();
      setStorageInfo(estimate);
      
      if (estimate) {
        // console.log('[OfflineContext] Storage usage:', { used: `${(estimate.usage / 1024 / 1024).toFixed(2)} MB`, quota: `${(estimate.quota / 1024 / 1024).toFixed(2)} MB`, percent: `${estimate.percentUsed.toFixed(1)}%` });
      }
    } catch (error) {
      // console.error('[OfflineContext] Failed to update storage info:', error);
    }
  }, []);

  /**
   * Trigger sync of offline data
   * This will be called automatically when connection is restored
   */
  const triggerSync = useCallback(async () => {
    if (!isOnline) {
      // console.log('[OfflineContext] Cannot sync while offline');
      return false;
    }

    if (isSyncing) {
      // console.log('[OfflineContext] Sync already in progress');
      return false;
    }

    try {
      setIsSyncing(true);
      setSyncError(null);
      
      // console.log('[OfflineContext] Starting sync...');
      
      // Dispatch custom event that sync services can listen to
      window.dispatchEvent(new CustomEvent('offline-sync-start'));
      
      // Use the sync processor to actually sync data
      const results = await processSync();
      
      // console.log('[OfflineContext] Sync results:', results);
      
      // Update pending count after sync
      await updatePendingCount();
      
      setLastSyncTime(new Date());
      
      // Check if there were any errors
      if (results.failed > 0) {
        setSyncError(`${results.failed} operations failed to sync`);
        console.warn('[OfflineContext] Some operations failed:', results.errors);
      } else {
        // console.log('[OfflineContext] Sync completed successfully');
      }
      
      // Dispatch sync complete event
      window.dispatchEvent(new CustomEvent('offline-sync-complete', {
        detail: results
      }));
      
      return results.failed === 0;
    } catch (error) {
      // console.error('[OfflineContext] Sync failed:', error);
      setSyncError(error.message);
      
      // Dispatch sync error event
      window.dispatchEvent(new CustomEvent('offline-sync-error', {
        detail: { error: error.message }
      }));
      
      return false;
    } finally {
      setIsSyncing(false);
    }
  }, [isOnline, isSyncing, updatePendingCount]);

  /**
   * Force refresh of pending count
   */
  const refreshPendingCount = useCallback(async () => {
    return await updatePendingCount();
  }, [updatePendingCount]);

  /**
   * Check if offline mode is available
   */
  const isOfflineModeAvailable = useCallback(() => {
    // Check if required APIs are available
    const hasIndexedDB = 'indexedDB' in window;
    const hasServiceWorker = 'serviceWorker' in navigator;
    
    return hasIndexedDB && hasServiceWorker;
  }, []);

  // Initialize: Update pending count on mount
  useEffect(() => {
    updatePendingCount();
    updateStorageInfo();
    
    // Set up interval to periodically update counts
    const intervalId = setInterval(() => {
      updatePendingCount();
      updateStorageInfo();
    }, 30000); // Every 30 seconds
    
    return () => clearInterval(intervalId);
  }, [updatePendingCount, updateStorageInfo]);

  // Auto-sync when connection is restored
  useEffect(() => {
    if (isOnline && wasOffline && pendingCount > 0) {
      // console.log('[OfflineContext] Connection restored with pending operations, triggering sync...');
      
      // Show "back online" message
      setShowBackOnline(true);
      setTimeout(() => setShowBackOnline(false), 5000); // Hide after 5 seconds
      
      // Trigger sync after a short delay to ensure connection is stable
      setTimeout(() => {
        triggerSync();
      }, 2000);
    }
  }, [isOnline, wasOffline, pendingCount, triggerSync]);

  // Listen for custom events from other components
  useEffect(() => {
    const handleDataSaved = () => {
      // console.log('[OfflineContext] Data saved offline, updating count...');
      updatePendingCount();
    };

    const handleDataSynced = () => {
      // console.log('[OfflineContext] Data synced, updating count...');
      updatePendingCount();
    };

    window.addEventListener('offline-data-saved', handleDataSaved);
    window.addEventListener('offline-data-synced', handleDataSynced);

    return () => {
      window.removeEventListener('offline-data-saved', handleDataSaved);
      window.removeEventListener('offline-data-synced', handleDataSynced);
    };
  }, [updatePendingCount]);

  const contextValue = {
    // Network status
    isOnline,
    wasOffline,
    offlineDuration,
    showBackOnline,
    
    // Offline state
    pendingCount,
    isSyncing,
    lastSyncTime,
    syncError,
    storageInfo,
    
    // Actions
    triggerSync,
    refreshPendingCount,
    isOfflineModeAvailable,
    
    // Utility
    formatStorageSize: (bytes) => {
      if (!bytes) return '0 B';
      const mb = bytes / 1024 / 1024;
      if (mb < 1) return `${(bytes / 1024).toFixed(1)} KB`;
      return `${mb.toFixed(1)} MB`;
    },
  };

  return (
    <OfflineContext.Provider value={contextValue}>
      {children}
    </OfflineContext.Provider>
  );
};

export default OfflineContext;
