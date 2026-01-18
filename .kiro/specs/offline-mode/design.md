# Offline Mode - Design Document

## Overview

ABParts will implement Progressive Web App (PWA) capabilities with offline-first architecture for critical maintenance operations. The system uses service workers for caching, IndexedDB for local data storage, and a sync queue for managing offline operations.

## Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    React Frontend                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │   UI Layer   │  │ Offline      │  │  Network     │ │
│  │              │  │ Indicator    │  │  Detector    │ │
│  └──────────────┘  └──────────────┘  └──────────────┘ │
│  ┌──────────────────────────────────────────────────┐  │
│  │         Offline Service Layer                     │  │
│  │  - Sync Queue Manager                            │  │
│  │  - Cache Manager                                 │  │
│  │  - Conflict Resolver                             │  │
│  └──────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────┐  │
│  │         Storage Layer                             │  │
│  │  - IndexedDB (structured data)                   │  │
│  │  - LocalStorage (preferences)                    │  │
│  └──────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│              Service Worker                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │ Cache First  │  │ Network      │  │ Background   │ │
│  │ Strategy     │  │ First        │  │ Sync         │ │
│  └──────────────┘  └──────────────┘  └──────────────┘ │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│                  FastAPI Backend                         │
│                  (Unchanged)                             │
└─────────────────────────────────────────────────────────┘
```

## Components and Interfaces

### 1. Service Worker (`frontend/public/service-worker.js`)

**Responsibilities:**
- Intercept network requests
- Implement caching strategies
- Handle background sync
- Manage app updates

**Caching Strategies:**
- **Cache First**: Static assets (JS, CSS, images)
- **Network First, Cache Fallback**: API calls for machines, protocols
- **Network Only**: Write operations (POST, PUT, DELETE)

### 2. Offline Service (`frontend/src/services/offlineService.js`)

**Interface:**
```javascript
class OfflineService {
  // Network status
  isOnline(): boolean
  onStatusChange(callback: (online: boolean) => void): void
  
  // Cache management
  cacheData(key: string, data: any): Promise<void>
  getCachedData(key: string): Promise<any>
  clearCache(): Promise<void>
  
  // Sync queue
  queueOperation(operation: OfflineOperation): Promise<string>
  getQueuedOperations(): Promise<OfflineOperation[]>
  processQueue(): Promise<SyncResult[]>
  
  // Conflict resolution
  resolveConflict(local: any, remote: any): any
}
```

### 3. IndexedDB Schema (`frontend/src/db/schema.js`)

**Object Stores:**

```javascript
// Cached Data Store
{
  name: 'cachedData',
  keyPath: 'key',
  indexes: [
    { name: 'timestamp', keyPath: 'timestamp' },
    { name: 'type', keyPath: 'type' }
  ]
}

// Sync Queue Store
{
  name: 'syncQueue',
  keyPath: 'id',
  indexes: [
    { name: 'timestamp', keyPath: 'timestamp' },
    { name: 'status', keyPath: 'status' },
    { name: 'type', keyPath: 'type' }
  ]
}

// Offline Executions Store
{
  name: 'offlineExecutions',
  keyPath: 'tempId',
  indexes: [
    { name: 'machineId', keyPath: 'machineId' },
    { name: 'status', keyPath: 'status' }
  ]
}
```

### 4. Sync Queue Manager (`frontend/src/services/syncQueueManager.js`)

**Operation Types:**
```javascript
type OfflineOperation = {
  id: string;              // UUID
  type: 'execution' | 'machine_hours' | 'part_usage';
  action: 'create' | 'update' | 'delete';
  data: any;
  timestamp: number;
  status: 'pending' | 'syncing' | 'success' | 'failed';
  retryCount: number;
  error?: string;
}
```

**Sync Process:**
1. Sort operations by timestamp
2. Process each operation sequentially
3. On success: Update local record with server ID, remove from queue
4. On failure: Increment retry count, apply exponential backoff
5. After 3 failures: Mark as failed, notify user

### 5. Network Detector (`frontend/src/hooks/useNetworkStatus.js`)

**Hook Interface:**
```javascript
const useNetworkStatus = () => {
  return {
    isOnline: boolean,
    isSlowConnection: boolean,
    connectionType: string,
    lastOnline: Date,
    pendingOperations: number
  }
}
```

### 6. Offline Indicator Component (`frontend/src/components/OfflineIndicator.js`)

**States:**
- Online (green): Normal operation
- Offline (red): No connectivity, showing cached data
- Syncing (yellow): Connectivity restored, syncing in progress
- Sync Failed (orange): Some operations failed to sync

## Data Models

### Cached Data Model
```javascript
{
  key: string,           // e.g., 'machines', 'protocols', 'machine_123'
  type: string,          // 'list' | 'detail'
  data: any,
  timestamp: number,
  expiresAt: number,
  version: string
}
```

### Sync Operation Model
```javascript
{
  id: string,
  type: 'execution' | 'machine_hours' | 'part_usage',
  action: 'create' | 'update' | 'delete',
  endpoint: string,
  method: 'POST' | 'PUT' | 'DELETE',
  data: any,
  tempId: string,        // Temporary ID for local reference
  timestamp: number,
  status: 'pending' | 'syncing' | 'success' | 'failed',
  retryCount: number,
  lastAttempt: number,
  error: string | null,
  dependencies: string[] // IDs of operations that must complete first
}
```

## Error Handling

### Offline Errors
- **Storage Quota Exceeded**: Prompt user to clear cache or sync immediately
- **Sync Failure**: Retry with exponential backoff (1s, 2s, 4s)
- **Conflict Detected**: Apply resolution strategy, log for audit
- **Invalid Data**: Mark operation as failed, notify user with details

### Recovery Strategies
1. **Automatic Retry**: Up to 3 attempts with exponential backoff
2. **Manual Retry**: User can manually trigger sync for failed operations
3. **Conflict Resolution**: Last-write-wins based on timestamp
4. **Data Validation**: Validate before queuing to prevent invalid operations

## Testing Strategy

### Unit Tests
- OfflineService methods (cache, queue, sync)
- Network status detection
- Conflict resolution logic
- IndexedDB operations

### Integration Tests
- Complete offline workflow (record → queue → sync)
- Service worker caching strategies
- Background sync functionality
- Multi-device conflict scenarios

### Manual Testing Scenarios
1. **Basic Offline Flow**:
   - Go offline
   - Record maintenance execution
   - Go online
   - Verify sync completes

2. **Conflict Resolution**:
   - Two users edit same machine hours offline
   - Both sync
   - Verify conflict resolution

3. **Storage Limits**:
   - Fill cache to limit
   - Verify old data is purged
   - Verify critical data preserved

4. **Network Interruption**:
   - Start sync
   - Interrupt network mid-sync
   - Verify partial sync handled correctly

## Implementation Phases

### Phase 1: Foundation (Week 1-2)
- Set up service worker
- Implement IndexedDB schema
- Create OfflineService base
- Add network status detection
- Add offline indicator UI

### Phase 2: Read-Only Offline (Week 3-4)
- Cache machines, protocols, checklist items
- Implement cache-first strategy for reads
- Add stale data warnings
- Test offline viewing

### Phase 3: Offline Recording (Week 5-6)
- Implement sync queue
- Add offline execution recording
- Add offline machine hours recording
- Test queue management

### Phase 4: Synchronization (Week 7-8)
- Implement background sync
- Add conflict resolution
- Add retry logic
- Test sync scenarios

### Phase 5: PWA Features (Week 9-10)
- Add PWA manifest
- Implement install prompt
- Add offline page
- Test installation flow

### Phase 6: Polish & Testing (Week 11-12)
- Add sync status page
- Improve error messages
- Performance optimization
- Comprehensive testing
- User acceptance testing

## Performance Considerations

- **Cache Size**: Limit to 50MB, purge oldest data first
- **Sync Batch Size**: Process max 10 operations per batch
- **Background Sync**: Use Web Background Sync API when available
- **Lazy Loading**: Only cache data when accessed
- **Compression**: Compress cached data to save space

## Security Considerations

- **Authentication**: Store auth token securely, expire after 8 hours
- **Data Encryption**: Encrypt sensitive data in IndexedDB
- **Sync Validation**: Validate all operations server-side
- **Audit Trail**: Log all offline operations for security review
- **User Isolation**: Ensure users can only sync their own data

## Browser Compatibility

**Minimum Requirements:**
- Chrome 67+ (Service Worker, IndexedDB, Background Sync)
- Firefox 61+ (Service Worker, IndexedDB)
- Safari 11.1+ (Service Worker, IndexedDB, limited Background Sync)
- Edge 79+ (Chromium-based)

**Graceful Degradation:**
- Detect service worker support
- Fall back to online-only mode if unsupported
- Show warning about limited offline capability
