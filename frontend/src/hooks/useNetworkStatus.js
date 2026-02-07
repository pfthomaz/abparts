// useNetworkStatus Hook
// Detects and tracks online/offline network status

import { useState, useEffect } from 'react';

/**
 * Custom hook to track network connectivity status
 * 
 * @returns {Object} Network status object
 * @returns {boolean} isOnline - Current online status
 * @returns {boolean} wasOffline - Whether the app was offline before
 * @returns {Date|null} lastOnlineTime - Timestamp of last online event
 * @returns {Date|null} lastOfflineTime - Timestamp of last offline event
 * @returns {number} offlineDuration - Duration of offline period in milliseconds
 */
export function useNetworkStatus() {
  // Initialize with current navigator.onLine status
  const [isOnline, setIsOnline] = useState(() => {
    if (typeof navigator !== 'undefined' && typeof navigator.onLine === 'boolean') {
      return navigator.onLine;
    }
    return true; // Assume online if can't detect
  });
  
  const [wasOffline, setWasOffline] = useState(false);
  const [lastOnlineTime, setLastOnlineTime] = useState(null);
  const [lastOfflineTime, setLastOfflineTime] = useState(null);
  const [offlineDuration, setOfflineDuration] = useState(0);

  useEffect(() => {
    // Handler for when connection is restored
    const handleOnline = () => {
      const now = new Date();
      // console.log('[Network] Connection restored at', now.toISOString());
      
      setIsOnline(true);
      setLastOnlineTime(now);
      
      // Calculate offline duration if we have a last offline time
      if (lastOfflineTime) {
        const duration = now.getTime() - lastOfflineTime.getTime();
        setOfflineDuration(duration);
        // console.log(`[Network] Was offline for ${Math.round(duration / 1000)} seconds`);
      }
      
      // Mark that we were offline (for triggering sync)
      if (!isOnline) {
        setWasOffline(true);
      }
    };

    // Handler for when connection is lost
    const handleOffline = () => {
      const now = new Date();
      // console.log('[Network] Connection lost at', now.toISOString());
      
      setIsOnline(false);
      setLastOfflineTime(now);
      setWasOffline(false); // Reset when going offline
    };

    // Add event listeners
    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    // Log initial status
    // console.log('[Network] Initial status:', isOnline ? 'Online' : 'Offline');

    // Cleanup event listeners on unmount
    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, [isOnline, lastOfflineTime]);

  return {
    isOnline,
    wasOffline,
    lastOnlineTime,
    lastOfflineTime,
    offlineDuration,
  };
}

/**
 * Hook to execute a callback when network status changes
 * 
 * @param {Function} onOnline - Callback when connection is restored
 * @param {Function} onOffline - Callback when connection is lost
 */
export function useNetworkStatusCallback(onOnline, onOffline) {
  useEffect(() => {
    const handleOnline = () => {
      // console.log('[Network] Online callback triggered');
      if (onOnline) onOnline();
    };

    const handleOffline = () => {
      // console.log('[Network] Offline callback triggered');
      if (onOffline) onOffline();
    };

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, [onOnline, onOffline]);
}

/**
 * Hook to check if network connection is stable
 * Performs a simple fetch test to verify actual connectivity
 * 
 * @param {number} interval - Check interval in milliseconds (default: 30000 = 30 seconds)
 * @returns {Object} Connection stability status
 * @returns {boolean} isStable - Whether connection is stable
 * @returns {boolean} isChecking - Whether currently checking
 * @returns {Date|null} lastCheck - Timestamp of last check
 */
export function useNetworkStability(interval = 30000) {
  const [isStable, setIsStable] = useState(true);
  const [isChecking, setIsChecking] = useState(false);
  const [lastCheck, setLastCheck] = useState(null);

  useEffect(() => {
    // Don't check if offline
    if (!navigator.onLine) {
      setIsStable(false);
      return;
    }

    const checkConnection = async () => {
      setIsChecking(true);
      
      try {
        // Try to fetch a small resource from the API
        // Using a HEAD request to minimize data transfer
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 5000); // 5 second timeout
        
        const response = await fetch('/api/health', {
          method: 'HEAD',
          signal: controller.signal,
        });
        
        clearTimeout(timeoutId);
        
        const stable = response.ok;
        setIsStable(stable);
        setLastCheck(new Date());
        
        // console.log('[Network] Stability check:', stable ? 'Stable' : 'Unstable');
      } catch (error) {
        console.warn('[Network] Stability check failed:', error.message);
        setIsStable(false);
        setLastCheck(new Date());
      } finally {
        setIsChecking(false);
      }
    };

    // Initial check
    checkConnection();

    // Set up interval for periodic checks
    const intervalId = setInterval(checkConnection, interval);

    return () => {
      clearInterval(intervalId);
    };
  }, [interval]);

  return {
    isStable,
    isChecking,
    lastCheck,
  };
}

/**
 * Hook to get network connection type and speed estimate
 * Uses Network Information API if available
 * 
 * @returns {Object} Connection information
 * @returns {string|null} effectiveType - Connection type (slow-2g, 2g, 3g, 4g)
 * @returns {number|null} downlink - Downlink speed in Mbps
 * @returns {boolean} saveData - Whether user has data saver enabled
 */
export function useNetworkInfo() {
  const [networkInfo, setNetworkInfo] = useState({
    effectiveType: null,
    downlink: null,
    saveData: false,
  });

  useEffect(() => {
    // Check if Network Information API is available
    const connection = navigator.connection || 
                      navigator.mozConnection || 
                      navigator.webkitConnection;

    if (!connection) {
      // console.log('[Network] Network Information API not available');
      return;
    }

    const updateNetworkInfo = () => {
      setNetworkInfo({
        effectiveType: connection.effectiveType || null,
        downlink: connection.downlink || null,
        saveData: connection.saveData || false,
      });
      
      // console.log('[Network] Connection type:', connection.effectiveType);
      // console.log('[Network] Downlink speed:', connection.downlink, 'Mbps');
    };

    // Initial update
    updateNetworkInfo();

    // Listen for changes
    connection.addEventListener('change', updateNetworkInfo);

    return () => {
      connection.removeEventListener('change', updateNetworkInfo);
    };
  }, []);

  return networkInfo;
}

/**
 * Utility function to check if currently online
 * Can be used outside of React components
 * 
 * @returns {boolean} Current online status
 */
export function isOnline() {
  return typeof navigator !== 'undefined' && navigator.onLine;
}

/**
 * Utility function to wait for online status
 * Returns a promise that resolves when connection is restored
 * 
 * @param {number} timeout - Maximum time to wait in milliseconds (default: 60000 = 1 minute)
 * @returns {Promise<boolean>} Resolves to true when online, false if timeout
 */
export function waitForOnline(timeout = 60000) {
  return new Promise((resolve) => {
    // Already online
    if (navigator.onLine) {
      resolve(true);
      return;
    }

    let timeoutId;
    
    const handleOnline = () => {
      clearTimeout(timeoutId);
      window.removeEventListener('online', handleOnline);
      resolve(true);
    };

    // Set up timeout
    timeoutId = setTimeout(() => {
      window.removeEventListener('online', handleOnline);
      resolve(false);
    }, timeout);

    // Wait for online event
    window.addEventListener('online', handleOnline);
  });
}

export default useNetworkStatus;
