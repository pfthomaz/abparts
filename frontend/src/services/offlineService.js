// frontend/src/services/offlineService.js

class OfflineService {
  constructor() {
    this.isOnline = navigator.onLine;
    this.syncQueue = [];
    this.listeners = [];

    // Listen for online/offline events
    window.addEventListener('online', this.handleOnline.bind(this));
    window.addEventListener('offline', this.handleOffline.bind(this));

    // Initialize sync queue from localStorage
    this.loadSyncQueue();
  }

  // Event handlers
  handleOnline() {
    this.isOnline = true;
    this.notifyListeners('online');
    this.processSyncQueue();
  }

  handleOffline() {
    this.isOnline = false;
    this.notifyListeners('offline');
  }

  // Listener management
  addListener(callback) {
    this.listeners.push(callback);
    return () => {
      this.listeners = this.listeners.filter(listener => listener !== callback);
    };
  }

  notifyListeners(event) {
    this.listeners.forEach(listener => {
      try {
        listener({ type: event, isOnline: this.isOnline });
      } catch (error) {
        console.error('Error in offline service listener:', error);
      }
    });
  }

  // Sync queue management
  loadSyncQueue() {
    try {
      const stored = localStorage.getItem('abparts_sync_queue');
      this.syncQueue = stored ? JSON.parse(stored) : [];
    } catch (error) {
      console.error('Failed to load sync queue:', error);
      this.syncQueue = [];
    }
  }

  saveSyncQueue() {
    try {
      localStorage.setItem('abparts_sync_queue', JSON.stringify(this.syncQueue));
    } catch (error) {
      console.error('Failed to save sync queue:', error);
    }
  }

  // Add item to sync queue
  addToSyncQueue(item) {
    const queueItem = {
      id: Date.now() + Math.random(),
      timestamp: new Date().toISOString(),
      ...item
    };

    this.syncQueue.push(queueItem);
    this.saveSyncQueue();

    // Try to sync immediately if online
    if (this.isOnline) {
      this.processSyncQueue();
    }

    return queueItem.id;
  }

  // Remove item from sync queue
  removeFromSyncQueue(id) {
    this.syncQueue = this.syncQueue.filter(item => item.id !== id);
    this.saveSyncQueue();
  }

  // Process sync queue
  async processSyncQueue() {
    if (!this.isOnline || this.syncQueue.length === 0) {
      return;
    }

    const itemsToSync = [...this.syncQueue];

    for (const item of itemsToSync) {
      try {
        await this.syncItem(item);
        this.removeFromSyncQueue(item.id);
      } catch (error) {
        console.error('Failed to sync item:', error);
        // Keep item in queue for next sync attempt
      }
    }
  }

  // Sync individual item
  async syncItem(item) {
    switch (item.type) {
      case 'machine_hours':
        return await this.syncMachineHours(item);
      case 'part_usage':
        return await this.syncPartUsage(item);
      case 'inventory_adjustment':
        return await this.syncInventoryAdjustment(item);
      default:
        throw new Error(`Unknown sync item type: ${item.type}`);
    }
  }

  // Specific sync methods
  async syncMachineHours(item) {
    const { machinesService } = await import('./machinesService');
    return await machinesService.recordMachineHours(item.data.machine_id, {
      hours_value: item.data.hours_value,
      recorded_date: item.data.recorded_date,
      notes: item.data.notes
    });
  }

  async syncPartUsage(item) {
    const { transactionService } = await import('./transactionService');
    return await transactionService.recordPartUsage(item.data);
  }

  async syncInventoryAdjustment(item) {
    const { inventoryService } = await import('./inventoryService');
    return await inventoryService.adjustInventory(item.data);
  }

  // Utility methods
  getQueuedItems(type = null) {
    if (type) {
      return this.syncQueue.filter(item => item.type === type);
    }
    return [...this.syncQueue];
  }

  getQueuedItemsCount(type = null) {
    return this.getQueuedItems(type).length;
  }

  clearQueue() {
    this.syncQueue = [];
    this.saveSyncQueue();
  }

  // Storage utilities for specific data types
  saveOfflineData(key, data) {
    try {
      const existing = this.getOfflineData(key);
      existing.push({
        id: Date.now() + Math.random(),
        timestamp: new Date().toISOString(),
        ...data
      });
      localStorage.setItem(`abparts_offline_${key}`, JSON.stringify(existing));
      return true;
    } catch (error) {
      console.error(`Failed to save offline data for ${key}:`, error);
      return false;
    }
  }

  getOfflineData(key) {
    try {
      const stored = localStorage.getItem(`abparts_offline_${key}`);
      return stored ? JSON.parse(stored) : [];
    } catch (error) {
      console.error(`Failed to get offline data for ${key}:`, error);
      return [];
    }
  }

  removeOfflineData(key, id) {
    try {
      const existing = this.getOfflineData(key);
      const filtered = existing.filter(item => item.id !== id);
      localStorage.setItem(`abparts_offline_${key}`, JSON.stringify(filtered));
      return true;
    } catch (error) {
      console.error(`Failed to remove offline data for ${key}:`, error);
      return false;
    }
  }

  clearOfflineData(key) {
    try {
      localStorage.removeItem(`abparts_offline_${key}`);
      return true;
    } catch (error) {
      console.error(`Failed to clear offline data for ${key}:`, error);
      return false;
    }
  }

  // Get storage usage info
  getStorageInfo() {
    try {
      const usage = {
        syncQueue: this.syncQueue.length,
        machineHours: this.getOfflineData('machine_hours').length,
        partUsage: this.getOfflineData('part_usage').length,
        inventoryAdjustments: this.getOfflineData('inventory_adjustments').length
      };

      const totalItems = Object.values(usage).reduce((sum, count) => sum + count, 0);

      return {
        ...usage,
        total: totalItems,
        storageUsed: this.calculateStorageUsage()
      };
    } catch (error) {
      console.error('Failed to get storage info:', error);
      return { total: 0, storageUsed: 0 };
    }
  }

  calculateStorageUsage() {
    try {
      let totalSize = 0;
      for (let key in localStorage) {
        if (key.startsWith('abparts_')) {
          totalSize += localStorage[key].length;
        }
      }
      return Math.round(totalSize / 1024); // Return size in KB
    } catch (error) {
      console.error('Failed to calculate storage usage:', error);
      return 0;
    }
  }
}

// Create singleton instance
const offlineService = new OfflineService();

export default offlineService;