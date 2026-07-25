# Offline Operations - Action Plan

## Executive Summary

Implementing offline operations for ABParts to enable field workers on farms to record maintenance, machine hours, and net cleaning data without internet connectivity. Data will sync automatically when connection is restored.

**Target Users**: Mobile/tablet users working on fish farms with unreliable connectivity

**Branch**: `offline-operation`

**Timeline**: 8-10 weeks for MVP, 12-14 weeks for full implementation

## Priority Use Cases

### 1. **Net Cleaning Records** (HIGHEST PRIORITY) ⭐
Workers at fish farms record net cleaning operations - this is THE primary offline use case.

**Workflow**:
1. Worker arrives at farm site (often remote with no connectivity)
2. Opens app - cached farm sites, cages, and nets load
3. Selects farm site → cage → net(s) to clean
4. Records cleaning details:
   - Cleaning date/time
   - Operator name
   - Cleaning method
   - Duration
   - Condition notes
   - Photos of nets (before/after)
5. Submits record (stored locally, queued for sync)
6. Continues to next net/cage
7. When back in office/WiFi range, all records sync automatically with photos

**Why This is Critical**:
- Farm sites are often in remote locations with no cell coverage
- Workers need to record multiple nets per day
- Photos are essential for documentation
- Cannot wait for connectivity to complete work

### 2. **Maintenance Execution Recording** (HIGH PRIORITY)
Field workers complete maintenance protocols on machines.

**Workflow**:
1. Worker opens maintenance protocol (cached from last online session)
2. Completes checklist items offline
3. Records machine hours
4. Submits execution (queued locally)
5. When online, execution syncs automatically

### 3. **Machine Hours Tracking** (MEDIUM PRIORITY)
Quick recording of machine operating hours in the field.

**Workflow**:
1. Worker selects machine (cached list)
2. Enters current hours
3. Saves (queued locally)
4. Syncs when online

## Implementation Phases

### Phase 1: Foundation (Week 1-2)
**Goal**: Set up offline infrastructure

**Tasks**:
1. Create `offline-operation` branch
2. Set up service worker with caching strategies
3. Implement IndexedDB for local storage
4. Add network status detection
5. Create offline indicator UI component

**Deliverables**:
- Service worker active and caching static assets
- Network status visible in UI
- IndexedDB schema created

**Files to Create**:
- `frontend/public/service-worker.js`
- `frontend/public/manifest.json`
- `frontend/src/db/indexedDB.js`
- `frontend/src/hooks/useNetworkStatus.js`
- `frontend/src/components/OfflineIndicator.js`

### Phase 2: Data Caching (Week 3)
**Goal**: Cache critical data for offline viewing - FOCUS ON NET CLEANING

**Tasks**:
1. **Cache farm sites** (with location data)
2. **Cache cages per farm site**
3. **Cache nets per cage** (with net details, status)
4. Cache machines list
5. Cache maintenance protocols
6. Cache parts catalog (read-only)
7. Add "last updated" timestamps to all cached views
8. Implement cache refresh strategy

**Deliverables**:
- Users can view complete farm/cage/net hierarchy offline
- Net cleaning form works with cached data
- Stale data warnings shown after 24 hours
- Cache updates automatically when online

**Files to Modify**:
- `frontend/src/services/farmSitesService.js` ⭐
- `frontend/src/services/netsService.js` ⭐
- `frontend/src/services/api.js`
- `frontend/src/services/machinesService.js`
- `frontend/src/services/maintenanceProtocolsService.js`

### Phase 3: Sync Queue System (Week 4)
**Goal**: Build queue for offline operations

**Tasks**:
1. Create sync queue manager
2. Implement operation queueing
3. Add temporary ID generation
4. Create sync processor with retry logic
5. Add sync status tracking

**Deliverables**:
- Operations can be queued when offline
- Queue persists across app restarts
- Sync processor ready for Phase 4

**Files to Create**:
- `frontend/src/services/syncQueueManager.js`
- `frontend/src/services/syncProcessor.js`
- `frontend/src/contexts/OfflineContext.js`

### Phase 5: Offline Maintenance Execution (Week 7)
**Goal**: Enable offline maintenance recording

**Tasks**:
1. Modify ExecutionForm to detect offline mode
2. Store executions locally with temp IDs
3. Queue checklist completions
4. Update execution history to show pending syncs
5. Handle execution sync with conflict resolution

**Deliverables**:
- Workers can complete maintenance protocols offline
- Executions sync automatically when online
- Clear visual indicators for pending syncs

**Files to Modify**:
- `frontend/src/components/ExecutionForm.js`
- `frontend/src/pages/MaintenanceExecutions.js`
- `frontend/src/components/ExecutionHistory.js`

### Phase 4: Offline Net Cleaning (Week 5-6) ⭐ PRIORITY
**Goal**: Enable complete offline net cleaning workflow

**Tasks**:
1. **Modify NetCleaningRecordForm for offline mode**
   - Detect offline status
   - Load cached farm sites/cages/nets
   - Generate temporary record IDs
   - Show offline indicator
2. **Implement photo handling offline**
   - Capture photos from camera
   - Store photos in IndexedDB (compressed)
   - Queue photos with record
   - Handle multiple photos per record
3. **Store net cleaning records locally**
   - Save complete record with temp ID
   - Link to cached farm/cage/net data
   - Store operator info
   - Track cleaning status
4. **Queue records for sync**
   - Add to sync queue with photos
   - Handle photo upload separately
   - Retry failed uploads
5. **Update net cleaning list UI**
   - Show pending (unsynced) records
   - Visual indicator for offline records
   - Filter by sync status
   - Show sync progress

**Deliverables**:
- Workers can record complete net cleaning operations offline
- Photos captured and stored locally
- Multiple records can be queued
- Records sync automatically with photos when online
- Clear visual feedback on sync status

**Files to Modify**:
- `frontend/src/components/NetCleaningRecordForm.js` ⭐
- `frontend/src/pages/NetCleaningRecords.js` ⭐
- `frontend/src/services/netCleaningRecordsService.js` ⭐
- `frontend/src/db/indexedDB.js` (add photo storage)

**Special Considerations**:
- Photo compression before storage (max 1MB per photo)
- Handle multiple photos per cleaning record
- Batch photo uploads to avoid timeout
- Show upload progress for photos

### Phase 6: Offline Machine Hours (Week 8)
**Goal**: Enable offline machine hours recording

**Tasks**:
1. Modify machine hours form for offline
2. Store hours records locally
3. Queue for sync
4. Handle duplicate detection
5. Update machine details to show pending hours

**Deliverables**:
- Workers can record machine hours offline
- Hours sync automatically
- Conflicts handled gracefully

**Files to Modify**:
- `frontend/src/components/MachineHoursReminderModal.js`
- `frontend/src/components/SimpleMachineHoursButton.js`
- `frontend/src/pages/Machines.js`

### Phase 7: PWA & Mobile Optimization (Week 9-10)
**Goal**: Optimize for mobile installation and use

**Tasks**:
1. Configure PWA manifest
2. Add install prompt
3. Create offline fallback page
4. Optimize UI for mobile offline use
5. Add haptic feedback for sync events

**Deliverables**:
- App can be installed on mobile devices
- Works as standalone app
- Optimized offline experience

**Files to Create/Modify**:
- `frontend/public/manifest.json`
- `frontend/public/offline.html`
- `frontend/src/components/PWAInstallPrompt.js`

### Phase 8: Sync Status & Management (Week 11)
**Goal**: Give users visibility and control over sync

**Tasks**:
1. Create sync status page
2. Add pending operations counter
3. Add manual sync trigger
4. Add retry failed operations
5. Show sync history

**Deliverables**:
- Users can see what's pending sync
- Manual sync control available
- Failed operations can be retried

**Files to Create**:
- `frontend/src/pages/SyncStatus.js`
- `frontend/src/components/SyncStatusCard.js`

### Phase 9: Translations & Polish (Week 12)
**Goal**: Localize and polish the feature

**Tasks**:
1. Add offline mode translations (6 languages)
2. Add sync status translations
3. Add error messages
4. Polish UI/UX
5. Add user documentation

**Deliverables**:
- Full localization support
- Polished user experience
- User guide for offline mode

**Files to Create**:
- `add_offline_mode_translations.py`
- `docs/OFFLINE_MODE_USER_GUIDE.md`

### Phase 10: Testing & Deployment (Week 13-14)
**Goal**: Comprehensive testing and production deployment

**Tasks**:
1. Unit tests for offline services
2. Integration tests for sync
3. Manual testing on mobile devices
4. Test various network conditions
5. Deploy to production

**Deliverables**:
- Comprehensive test coverage
- Tested on iOS and Android
- Production deployment complete

## Technical Architecture

### Storage Strategy

```
IndexedDB Stores:
├── cachedData
│   ├── farmSites (with location, contact info) ⭐
│   ├── cages (per farm site) ⭐
│   ├── nets (per cage, with status, dimensions) ⭐
│   ├── machines
│   ├── protocols
│   └── parts (read-only)
├── syncQueue (pending operations)
├── offlineNetCleaning ⭐
│   ├── records (cleaning details)
│   └── photos (compressed images)
├── offlineExecutions (maintenance executions)
└── offlineMachineHours (machine hours records)
```

### Sync Priority

1. **Highest Priority**: Net cleaning records with photos ⭐
2. **High Priority**: Maintenance executions, machine hours
3. **Medium Priority**: Cache updates
4. **Low Priority**: Analytics, non-critical data

### Conflict Resolution

**Strategy**: Last-write-wins based on timestamp

**Special Cases**:
- Machine hours: Preserve all records, flag duplicates
- Executions: Cannot conflict (unique per session)
- Net cleaning: Cannot conflict (unique per session)

## Mobile-Specific Considerations

### UI/UX for Mobile
- Large touch targets (min 44x44px)
- Swipe gestures for common actions
- Bottom navigation for thumb reach
- Haptic feedback for sync events
- Offline indicator always visible

### Performance
- Lazy load cached data
- Compress photos before storing
- Limit cache to 50MB
- Batch sync operations

### Battery Optimization
- Sync only when charging (optional)
- Reduce background activity
- Efficient IndexedDB queries

## Feature Restrictions When Offline

**Available Offline**:
- ✅ View machines, protocols, farm sites, nets
- ✅ Record maintenance executions
- ✅ Record net cleaning
- ✅ Record machine hours
- ✅ View cached dashboard data

**Requires Internet**:
- ❌ Inventory management
- ❌ Orders (customer/supplier)
- ❌ Stock adjustments
- ❌ AI Assistant
- ❌ User management
- ❌ Organization management

## Success Metrics

**Technical**:
- 95% sync success rate on first attempt
- < 5 second average sync time
- < 1% conflict rate
- < 50MB storage usage

**User Experience**:
- Workers can complete full day offline
- Clear sync status visibility
- No data loss
- 4+ star user satisfaction

## Risk Mitigation

### Risk 1: Data Loss
**Mitigation**: 
- Persist sync queue across app restarts
- Backup to localStorage as fallback
- Warn before clearing browser data

### Risk 2: Sync Conflicts
**Mitigation**:
- Timestamp-based resolution
- Log all conflicts for audit
- Manual review for critical conflicts

### Risk 3: Storage Limits
**Mitigation**:
- Monitor storage usage
- Implement cache eviction
- Warn users before limit

### Risk 4: Browser Compatibility
**Mitigation**:
- Detect service worker support
- Graceful degradation to online-only
- Clear browser requirements

## Getting Started

### Step 1: Create Branch
```bash
git checkout -b offline-operation
```

### Step 2: Install Dependencies
```bash
cd frontend
npm install workbox-webpack-plugin idb
```

### Step 3: Start with Phase 1
Begin with foundation tasks - service worker and IndexedDB setup.

### Step 4: Iterative Development
Complete each phase, test thoroughly, then move to next phase.

## Next Steps

1. **Review this plan** - Confirm priorities and timeline
2. **Create branch** - Set up `offline-operation` branch
3. **Start Phase 1** - Begin with service worker setup
4. **Weekly check-ins** - Review progress and adjust plan

## Questions to Resolve

1. Should we sync only on WiFi or also on cellular?
2. Maximum photo size for offline storage?
3. How long to keep failed sync operations?
4. Should we add offline analytics tracking?
5. Priority order if multiple operations pending?

---

**Ready to start?** Let's begin with Phase 1: Foundation!
