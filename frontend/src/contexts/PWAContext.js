// PWA Context - Manages offline status, notifications, and PWA features
import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import {
  register as registerSW,
  requestNotificationPermission,
  subscribeToPushNotifications,
  isStandalone,
  getOnlineStatus,
  addConnectivityListeners,
  sendMessageToSW
} from '../utils/serviceWorkerRegistration';

const PWAContext = createContext();

export const usePWA = () => {
  const context = useContext(PWAContext);
  if (!context) {
    throw new Error('usePWA must be used within a PWAProvider');
  }
  return context;
};

export const PWAProvider = ({ children }) => {
  const [isOnline, setIsOnline] = useState(getOnlineStatus());
  const [isInstalled, setIsInstalled] = useState(isStandalone());
  const [swRegistration, setSwRegistration] = useState(null);
  const [notificationPermission, setNotificationPermission] = useState(
    'Notification' in window ? Notification.permission : 'unsupported'
  );
  const [updateAvailable, setUpdateAvailable] = useState(false);
  const [messageQueue, setMessageQueue] = useState([]);
  const [showInstallPrompt, setShowInstallPrompt] = useState(false);
  const [deferredPrompt, setDeferredPrompt] = useState(null);

  // Register service worker on mount
  useEffect(() => {
    registerSW({
      onSuccess: (registration) => {
        console.log('[PWA] Service worker registered successfully');
        setSwRegistration(registration);
      },
      onUpdate: (registration) => {
        console.log('[PWA] New version available');
        setUpdateAvailable(true);
        setSwRegistration(registration);
      }
    });
  }, []);

  // Listen for connectivity changes
  useEffect(() => {
    const handleOnline = () => {
      console.log('[PWA] Connection restored');
      setIsOnline(true);
      
      // Trigger background sync if available
      if (swRegistration && 'sync' in swRegistration) {
        swRegistration.sync.register('sync-ai-messages').catch((err) => {
          console.error('[PWA] Background sync registration failed:', err);
        });
      }
      
      // Process queued messages
      if (messageQueue.length > 0) {
        console.log(`[PWA] Processing ${messageQueue.length} queued messages`);
        // Notify listeners that messages should be sent
        window.dispatchEvent(new CustomEvent('pwa-process-queue', {
          detail: { messages: messageQueue }
        }));
      }
    };

    const handleOffline = () => {
      console.log('[PWA] Connection lost');
      setIsOnline(false);
    };

    const cleanup = addConnectivityListeners(handleOnline, handleOffline);
    return cleanup;
  }, [swRegistration, messageQueue]);

  // Listen for service worker messages
  useEffect(() => {
    if (!('serviceWorker' in navigator)) return;

    const handleMessage = (event) => {
      console.log('[PWA] Message from service worker:', event.data);
      
      if (event.data && event.data.type === 'SYNC_MESSAGES') {
        // Trigger message sync
        window.dispatchEvent(new CustomEvent('pwa-sync-messages'));
      }
    };

    navigator.serviceWorker.addEventListener('message', handleMessage);
    return () => {
      navigator.serviceWorker.removeEventListener('message', handleMessage);
    };
  }, []);

  // Listen for install prompt
  useEffect(() => {
    const handleBeforeInstallPrompt = (e) => {
      // Prevent the mini-infobar from appearing on mobile
      e.preventDefault();
      // Stash the event so it can be triggered later
      setDeferredPrompt(e);
      // Show install prompt to user
      setShowInstallPrompt(true);
      console.log('[PWA] Install prompt available');
    };

    window.addEventListener('beforeinstallprompt', handleBeforeInstallPrompt);

    return () => {
      window.removeEventListener('beforeinstallprompt', handleBeforeInstallPrompt);
    };
  }, []);

  // Listen for app installed event
  useEffect(() => {
    const handleAppInstalled = () => {
      console.log('[PWA] App installed');
      setIsInstalled(true);
      setShowInstallPrompt(false);
      setDeferredPrompt(null);
    };

    window.addEventListener('appinstalled', handleAppInstalled);

    return () => {
      window.removeEventListener('appinstalled', handleAppInstalled);
    };
  }, []);

  // Request notification permission
  const requestNotifications = useCallback(async () => {
    const permission = await requestNotificationPermission();
    setNotificationPermission(permission);
    
    if (permission === 'granted' && swRegistration) {
      // Subscribe to push notifications
      const subscription = await subscribeToPushNotifications(swRegistration);
      if (subscription) {
        console.log('[PWA] Subscribed to push notifications');
        // TODO: Send subscription to backend
      }
    }
    
    return permission;
  }, [swRegistration]);

  // Show local notification
  const showNotification = useCallback((title, options = {}) => {
    if (notificationPermission !== 'granted') {
      console.log('[PWA] Notification permission not granted');
      return;
    }

    if (swRegistration) {
      swRegistration.showNotification(title, {
        icon: '/logo.png',
        badge: '/favicon.ico',
        vibrate: [200, 100, 200],
        ...options
      });
    } else if ('Notification' in window) {
      new Notification(title, {
        icon: '/logo.png',
        ...options
      });
    }
  }, [notificationPermission, swRegistration]);

  // Update the app
  const updateApp = useCallback(() => {
    if (swRegistration && swRegistration.waiting) {
      // Tell the service worker to skip waiting
      sendMessageToSW({ type: 'SKIP_WAITING' });
      
      // Reload the page after a short delay
      setTimeout(() => {
        window.location.reload();
      }, 500);
    }
  }, [swRegistration]);

  // Install the app
  const installApp = useCallback(async () => {
    if (!deferredPrompt) {
      console.log('[PWA] No install prompt available');
      return false;
    }

    // Show the install prompt
    deferredPrompt.prompt();
    
    // Wait for the user to respond to the prompt
    const { outcome } = await deferredPrompt.userChoice;
    console.log(`[PWA] User response to install prompt: ${outcome}`);
    
    // Clear the deferred prompt
    setDeferredPrompt(null);
    setShowInstallPrompt(false);
    
    return outcome === 'accepted';
  }, [deferredPrompt]);

  // Dismiss install prompt
  const dismissInstallPrompt = useCallback(() => {
    setShowInstallPrompt(false);
  }, []);

  // Queue message for later sending (when offline)
  const queueMessage = useCallback((message) => {
    setMessageQueue((prev) => [...prev, { ...message, timestamp: Date.now() }]);
    console.log('[PWA] Message queued for later sending');
  }, []);

  // Clear message queue
  const clearMessageQueue = useCallback(() => {
    setMessageQueue([]);
  }, []);

  // Get connection quality estimate
  const getConnectionQuality = useCallback(() => {
    if (!isOnline) return 'offline';
    
    // Use Network Information API if available
    if ('connection' in navigator) {
      const connection = navigator.connection;
      const effectiveType = connection.effectiveType;
      
      // Map effective types to quality levels
      const qualityMap = {
        'slow-2g': 'poor',
        '2g': 'poor',
        '3g': 'moderate',
        '4g': 'good'
      };
      
      return qualityMap[effectiveType] || 'unknown';
    }
    
    return 'unknown';
  }, [isOnline]);

  const value = {
    // Status
    isOnline,
    isInstalled,
    isStandalone: isInstalled,
    updateAvailable,
    showInstallPrompt,
    notificationPermission,
    connectionQuality: getConnectionQuality(),
    
    // Message queue
    messageQueue,
    queueMessage,
    clearMessageQueue,
    
    // Actions
    requestNotifications,
    showNotification,
    updateApp,
    installApp,
    dismissInstallPrompt,
    
    // Service worker
    swRegistration
  };

  return <PWAContext.Provider value={value}>{children}</PWAContext.Provider>;
};
