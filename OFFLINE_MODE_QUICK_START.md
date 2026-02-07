# Offline Mode - Quick Start Guide

## TL;DR

Enable field workers to record maintenance, net cleaning, and machine hours on mobile devices without internet. Data syncs automatically when connection returns.

## Create Branch

```bash
git checkout -b offline-operation
git push -u origin offline-operation
```

## Phase 1: Foundation (Start Here!)

### 1. Install Dependencies

```bash
cd frontend
npm install workbox-webpack-plugin idb localforage
```

### 2. Create Service Worker

Create `frontend/public/service-worker.js`:

```javascript
// Basic service worker for offline support
const CACHE_NAME = 'abparts-v1';
const urlsToCache = [
  '/',
  '/static/css/main.css',
  '/static/js/main.js'
];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => cache.addAll(urlsToCache))
  );
});

self.addEventListener('fetch', (event) => {
  event.respondWith(
    caches.match(event.request)
      .then((response) => response || fetch(event.request))
  );
});
```

### 3. Register Service Worker

Update `frontend/src/index.js`:

```javascript
// Add after ReactDOM.render()

if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('/service-worker.js')
      .then(registration => {
        console.log('SW registered:', registration);
      })
      .catch(error => {
        console.log('SW registration failed:', error);
      });
  });
}
```

### 4. Create PWA Manifest

Create `frontend/public/manifest.json`:

```json
{
  "short_name": "ABParts",
  "name": "ABParts - Maintenance & Operations",
  "icons": [
    {
      "src": "favicon.ico",
      "sizes": "64x64 32x32 24x24 16x16",
      "type": "image/x-icon"
    },
    {
      "src": "logo192.png",
      "type": "image/png",
      "sizes": "192x192"
    },
    {
      "src": "logo512.png",
      "type": "image/png",
      "sizes": "512x512"
    }
  ],
  "start_url": ".",
  "display": "standalone",
  "theme_color": "#3b82f6",
  "background_color": "#ffffff",
  "orientation": "portrait"
}
```

### 5. Add PWA Meta Tags

Update `frontend/public/index.html` in `<head>`:

```html
<link rel="manifest" href="%PUBLIC_URL%/manifest.json" />
<meta name="theme-color" content="#3b82f6" />
<meta name="apple-mobile-web-app-capable" content="yes" />
<meta name="apple-mobile-web-app-status-bar-style" content="default" />
<meta name="apple-mobile-web-app-title" content="ABParts" />
```

### 6. Create Network Status Hook

Create `frontend/src/hooks/useNetworkStatus.js`:

```javascript
import { useState, useEffect } from 'react';

export const useNetworkStatus = () => {
  const [isOnline, setIsOnline] = useState(navigator.onLine);
  const [lastOnline, setLastOnline] = useState(new Date());

  useEffect(() => {
    const handleOnline = () => {
      setIsOnline(true);
      setLastOnline(new Date());
    };

    const handleOffline = () => {
      setIsOnline(false);
    };

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);

  return { isOnline, lastOnline };
};
```

### 7. Create Offline Indicator

Create `frontend/src/components/OfflineIndicator.js`:

```javascript
import React from 'react';
import { useNetworkStatus } from '../hooks/useNetworkStatus';

const OfflineIndicator = () => {
  const { isOnline } = useNetworkStatus();

  if (isOnline) return null;

  return (
    <div className="fixed top-0 left-0 right-0 bg-red-600 text-white px-4 py-2 text-center z-50">
      <span className="font-medium">📡 Offline Mode</span>
      <span className="ml-2 text-sm">Changes will sync when connection returns</span>
    </div>
  );
};

export default OfflineIndicator;
```

### 8. Add to Layout

Update `frontend/src/components/Layout.js`:

```javascript
import OfflineIndicator from './OfflineIndicator';

// Add at the top of the layout
<OfflineIndicator />
```

### 9. Test Phase 1

```bash
# Start development server
npm start

# Test offline mode:
# 1. Open DevTools > Network tab
# 2. Check "Offline" checkbox
# 3. Verify offline indicator appears
# 4. Uncheck "Offline"
# 5. Verify indicator disappears
```

## Phase 2: IndexedDB Setup

### 1. Create IndexedDB Wrapper

Create `frontend/src/db/indexedDB.js`:

```javascript
import { openDB } from 'idb';

const DB_NAME = 'abparts-offline';
const DB_VERSION = 1;

export const initDB = async () => {
  return openDB(DB_NAME, DB_VERSION, {
    upgrade(db) {
      // Cached data store
      if (!db.objectStoreNames.contains('cachedData')) {
        const cachedStore = db.createObjectStore('cachedData', { keyPath: 'key' });
        cachedStore.createIndex('timestamp', 'timestamp');
        cachedStore.createIndex('type', 'type');
      }

      // Sync queue store
      if (!db.objectStoreNames.contains('syncQueue')) {
        const queueStore = db.createObjectStore('syncQueue', { keyPath: 'id' });
        queueStore.createIndex('timestamp', 'timestamp');
        queueStore.createIndex('status', 'status');
        queueStore.createIndex('type', 'type');
      }

      // Offline executions store
      if (!db.objectStoreNames.contains('offlineExecutions')) {
        const execStore = db.createObjectStore('offlineExecutions', { keyPath: 'tempId' });
        execStore.createIndex('machineId', 'machineId');
        execStore.createIndex('status', 'status');
      }
    },
  });
};

// Cache operations
export const cacheData = async (key, data) => {
  const db = await initDB();
  await db.put('cachedData', {
    key,
    data,
    timestamp: Date.now(),
    expiresAt: Date.now() + (24 * 60 * 60 * 1000) // 24 hours
  });
};

export const getCachedData = async (key) => {
  const db = await initDB();
  const cached = await db.get('cachedData', key);
  
  if (!cached) return null;
  
  // Check if expired
  if (cached.expiresAt < Date.now()) {
    await db.delete('cachedData', key);
    return null;
  }
  
  return cached.data;
};

// Sync queue operations
export const addToSyncQueue = async (operation) => {
  const db = await initDB();
  await db.add('syncQueue', {
    ...operation,
    id: `${Date.now()}-${Math.random()}`,
    timestamp: Date.now(),
    status: 'pending',
    retryCount: 0
  });
};

export const getSyncQueue = async () => {
  const db = await initDB();
  return db.getAllFromIndex('syncQueue', 'status', 'pending');
};

export const removeSyncOperation = async (id) => {
  const db = await initDB();
  await db.delete('syncQueue', id);
};
```

### 2. Create Offline Context

Create `frontend/src/contexts/OfflineContext.js`:

```javascript
import React, { createContext, useContext, useState, useEffect } from 'react';
import { useNetworkStatus } from '../hooks/useNetworkStatus';
import { getSyncQueue } from '../db/indexedDB';

const OfflineContext = createContext();

export const useOffline = () => {
  const context = useContext(OfflineContext);
  if (!context) {
    throw new Error('useOffline must be used within OfflineProvider');
  }
  return context;
};

export const OfflineProvider = ({ children }) => {
  const { isOnline } = useNetworkStatus();
  const [pendingOperations, setPendingOperations] = useState(0);
  const [isSyncing, setIsSyncing] = useState(false);

  useEffect(() => {
    const updatePendingCount = async () => {
      const queue = await getSyncQueue();
      setPendingOperations(queue.length);
    };

    updatePendingCount();
    const interval = setInterval(updatePendingCount, 5000);

    return () => clearInterval(interval);
  }, []);

  const value = {
    isOnline,
    pendingOperations,
    isSyncing,
    setIsSyncing
  };

  return (
    <OfflineContext.Provider value={value}>
      {children}
    </OfflineContext.Provider>
  );
};
```

### 3. Add Provider to App

Update `frontend/src/App.js`:

```javascript
import { OfflineProvider } from './contexts/OfflineContext';

// Wrap your app
<OfflineProvider>
  {/* existing app content */}
</OfflineProvider>
```

### 4. Test Phase 2

```javascript
// Test in browser console
import { cacheData, getCachedData } from './db/indexedDB';

// Cache some data
await cacheData('test', { message: 'Hello offline!' });

// Retrieve it
const data = await getCachedData('test');
console.log(data); // Should show: { message: 'Hello offline!' }
```

## Next Steps

After completing Phase 1 & 2:

1. **Test thoroughly** - Verify service worker and IndexedDB work
2. **Commit progress** - `git commit -m "Phase 1-2: Offline foundation"`
3. **Move to Phase 3** - Implement sync queue manager
4. **Review action plan** - Check `OFFLINE_OPERATIONS_ACTION_PLAN.md`

## Common Issues

### Service Worker Not Registering
- Check browser console for errors
- Ensure HTTPS (or localhost)
- Clear browser cache and reload

### IndexedDB Not Working
- Check browser support (all modern browsers)
- Check storage quota
- Clear IndexedDB in DevTools

### Offline Indicator Not Showing
- Check network status in DevTools
- Verify component is imported in Layout
- Check z-index conflicts

## Testing Offline Mode

### Chrome DevTools
1. Open DevTools (F12)
2. Go to Network tab
3. Check "Offline" checkbox
4. Test app functionality

### Mobile Testing
1. Enable airplane mode
2. Open app (should work if previously loaded)
3. Test offline features
4. Disable airplane mode
5. Verify sync occurs

## Resources

- **Service Worker API**: https://developer.mozilla.org/en-US/docs/Web/API/Service_Worker_API
- **IndexedDB**: https://developer.mozilla.org/en-US/docs/Web/API/IndexedDB_API
- **PWA Guide**: https://web.dev/progressive-web-apps/
- **idb Library**: https://github.com/jakearchibald/idb

## Questions?

Check the full action plan: `OFFLINE_OPERATIONS_ACTION_PLAN.md`

---

**Ready to build!** Start with Phase 1 and work through each step systematically.
