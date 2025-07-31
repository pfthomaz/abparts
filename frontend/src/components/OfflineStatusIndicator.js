// frontend/src/components/OfflineStatusIndicator.js

import React, { useState, useEffect } from 'react';
import offlineService from '../services/offlineService';

const OfflineStatusIndicator = ({ className = '' }) => {
  const [isOnline, setIsOnline] = useState(navigator.onLine);
  const [queuedItems, setQueuedItems] = useState(0);
  const [showDetails, setShowDetails] = useState(false);
  const [storageInfo, setStorageInfo] = useState({ total: 0, storageUsed: 0 });

  useEffect(() => {
    // Listen for online/offline changes
    const unsubscribe = offlineService.addListener((event) => {
      setIsOnline(event.isOnline);
      updateQueueInfo();
    });

    // Initial load
    updateQueueInfo();

    // Update queue info periodically
    const interval = setInterval(updateQueueInfo, 5000);

    return () => {
      unsubscribe();
      clearInterval(interval);
    };
  }, []);

  const updateQueueInfo = () => {
    const count = offlineService.getQueuedItemsCount();
    const storage = offlineService.getStorageInfo();
    setQueuedItems(count);
    setStorageInfo(storage);
  };

  const handleSync = async () => {
    if (isOnline) {
      await offlineService.processSyncQueue();
      updateQueueInfo();
    }
  };

  const clearOfflineData = () => {
    if (window.confirm('Are you sure you want to clear all offline data? This cannot be undone.')) {
      offlineService.clearQueue();
      updateQueueInfo();
    }
  };

  // Don't show if online and no queued items
  if (isOnline && queuedItems === 0) {
    return null;
  }

  return (
    <>
      {/* Status Bar */}
      <div className={`${className} ${isOnline ? 'bg-green-50 border-green-200' : 'bg-orange-50 border-orange-200'} 
        border-b px-4 py-2 lg:hidden`}>
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            {/* Status Indicator */}
            <div className={`w-2 h-2 rounded-full ${isOnline ? 'bg-green-500' : 'bg-orange-500'}`}></div>

            {/* Status Text */}
            <span className={`text-sm font-medium ${isOnline ? 'text-green-700' : 'text-orange-700'}`}>
              {isOnline ? 'Online' : 'Offline'}
            </span>

            {/* Queued Items */}
            {queuedItems > 0 && (
              <span className={`text-xs px-2 py-1 rounded-full ${isOnline ? 'bg-green-100 text-green-700' : 'bg-orange-100 text-orange-700'
                }`}>
                {queuedItems} pending
              </span>
            )}
          </div>

          {/* Actions */}
          <div className="flex items-center space-x-2">
            {isOnline && queuedItems > 0 && (
              <button
                onClick={handleSync}
                className="text-xs text-green-600 hover:text-green-800 font-medium"
              >
                Sync Now
              </button>
            )}

            <button
              onClick={() => setShowDetails(!showDetails)}
              className={`text-xs font-medium ${isOnline ? 'text-green-600 hover:text-green-800' : 'text-orange-600 hover:text-orange-800'}`}
            >
              {showDetails ? 'Hide' : 'Details'}
            </button>
          </div>
        </div>

        {/* Expanded Details */}
        {showDetails && (
          <div className="mt-3 pt-3 border-t border-gray-200 space-y-2">
            <div className="grid grid-cols-2 gap-4 text-xs text-gray-600">
              <div>
                <div className="font-medium">Offline Data:</div>
                <div>Machine Hours: {storageInfo.machineHours || 0}</div>
                <div>Part Usage: {storageInfo.partUsage || 0}</div>
                <div>Adjustments: {storageInfo.inventoryAdjustments || 0}</div>
              </div>
              <div>
                <div className="font-medium">Storage:</div>
                <div>Total Items: {storageInfo.total}</div>
                <div>Used: {storageInfo.storageUsed} KB</div>
                <div>Sync Queue: {storageInfo.syncQueue}</div>
              </div>
            </div>

            {/* Actions */}
            <div className="flex space-x-3 pt-2">
              {isOnline && queuedItems > 0 && (
                <button
                  onClick={handleSync}
                  className="flex-1 bg-green-600 text-white text-xs py-2 px-3 rounded-md hover:bg-green-700 transition-colors"
                >
                  Sync All Data
                </button>
              )}

              {storageInfo.total > 0 && (
                <button
                  onClick={clearOfflineData}
                  className="flex-1 bg-red-600 text-white text-xs py-2 px-3 rounded-md hover:bg-red-700 transition-colors"
                >
                  Clear Offline Data
                </button>
              )}
            </div>

            {!isOnline && (
              <div className="text-xs text-orange-600 bg-orange-100 p-2 rounded">
                <strong>Offline Mode:</strong> Your data is being saved locally and will sync automatically when connection is restored.
              </div>
            )}
          </div>
        )}
      </div>

      {/* Floating Status Indicator for Desktop */}
      {(!isOnline || queuedItems > 0) && (
        <div className="hidden lg:block fixed bottom-4 right-4 z-40">
          <div className={`${isOnline ? 'bg-green-500' : 'bg-orange-500'} text-white px-4 py-2 rounded-lg shadow-lg flex items-center space-x-2`}>
            <div className={`w-2 h-2 rounded-full ${isOnline ? 'bg-green-200' : 'bg-orange-200'}`}></div>
            <span className="text-sm font-medium">
              {isOnline ? 'Online' : 'Offline'}
              {queuedItems > 0 && ` (${queuedItems} pending)`}
            </span>

            {isOnline && queuedItems > 0 && (
              <button
                onClick={handleSync}
                className="text-xs bg-white bg-opacity-20 hover:bg-opacity-30 px-2 py-1 rounded transition-colors"
              >
                Sync
              </button>
            )}
          </div>
        </div>
      )}
    </>
  );
};

export default OfflineStatusIndicator;