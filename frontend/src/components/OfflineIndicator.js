// OfflineIndicator Component
// Visual indicator showing offline status and sync information

import React from 'react';
import { useNetworkStatus } from '../hooks/useNetworkStatus';
import { useTranslation } from '../hooks/useTranslation';

const OfflineIndicator = ({ showWhenOnline = false, pendingCount = 0 }) => {
  const { isOnline, offlineDuration } = useNetworkStatus();
  const { t } = useTranslation();

  // Don't show anything if online and showWhenOnline is false
  if (isOnline && !showWhenOnline && pendingCount === 0) {
    return null;
  }

  // Format offline duration
  const formatDuration = (ms) => {
    const seconds = Math.floor(ms / 1000);
    const minutes = Math.floor(seconds / 60);
    const hours = Math.floor(minutes / 60);

    if (hours > 0) {
      return `${hours}h ${minutes % 60}m`;
    } else if (minutes > 0) {
      return `${minutes}m ${seconds % 60}s`;
    } else {
      return `${seconds}s`;
    }
  };

  // Offline state
  if (!isOnline) {
    return (
      <div className="fixed top-0 left-0 right-0 z-50 bg-yellow-500 text-white px-4 py-2 shadow-lg">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div className="flex items-center space-x-3">
            {/* Offline Icon */}
            <svg 
              className="w-5 h-5 animate-pulse" 
              fill="none" 
              stroke="currentColor" 
              viewBox="0 0 24 24"
            >
              <path 
                strokeLinecap="round" 
                strokeLinejoin="round" 
                strokeWidth={2} 
                d="M18.364 5.636a9 9 0 010 12.728m0 0l-2.829-2.829m2.829 2.829L21 21M15.536 8.464a5 5 0 010 7.072m0 0l-2.829-2.829m-4.243 2.829a4.978 4.978 0 01-1.414-2.83m-1.414 5.658a9 9 0 01-2.167-9.238m7.824 2.167a1 1 0 111.414 1.414m-1.414-1.414L3 3" 
              />
            </svg>
            
            <div>
              <p className="font-semibold text-sm">
                {t('offline.indicator.title', 'Offline Mode')}
              </p>
              <p className="text-xs opacity-90">
                {t('offline.indicator.message', 'Working offline - data will sync when connection is restored')}
              </p>
            </div>
          </div>

          {/* Pending operations count */}
          {pendingCount > 0 && (
            <div className="bg-white bg-opacity-20 rounded-full px-3 py-1">
              <span className="text-xs font-medium">
                {pendingCount} {t('offline.indicator.pending', 'pending')}
              </span>
            </div>
          )}
        </div>
      </div>
    );
  }

  // Online with pending operations
  if (pendingCount > 0) {
    return (
      <div className="fixed top-0 left-0 right-0 z-50 bg-blue-500 text-white px-4 py-2 shadow-lg">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div className="flex items-center space-x-3">
            {/* Syncing Icon */}
            <svg 
              className="w-5 h-5 animate-spin" 
              fill="none" 
              stroke="currentColor" 
              viewBox="0 0 24 24"
            >
              <path 
                strokeLinecap="round" 
                strokeLinejoin="round" 
                strokeWidth={2} 
                d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" 
              />
            </svg>
            
            <div>
              <p className="font-semibold text-sm">
                {t('offline.indicator.syncing', 'Syncing...')}
              </p>
              <p className="text-xs opacity-90">
                {t('offline.indicator.syncingMessage', 'Uploading offline data')}
              </p>
            </div>
          </div>

          <div className="bg-white bg-opacity-20 rounded-full px-3 py-1">
            <span className="text-xs font-medium">
              {pendingCount} {t('offline.indicator.remaining', 'remaining')}
            </span>
          </div>
        </div>
      </div>
    );
  }

  // Recently back online (show for a few seconds)
  if (showWhenOnline && offlineDuration > 0) {
    return (
      <div className="fixed top-0 left-0 right-0 z-50 bg-green-500 text-white px-4 py-2 shadow-lg">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div className="flex items-center space-x-3">
            {/* Online Icon */}
            <svg 
              className="w-5 h-5" 
              fill="none" 
              stroke="currentColor" 
              viewBox="0 0 24 24"
            >
              <path 
                strokeLinecap="round" 
                strokeLinejoin="round" 
                strokeWidth={2} 
                d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" 
              />
            </svg>
            
            <div>
              <p className="font-semibold text-sm">
                {t('offline.indicator.backOnline', 'Back Online')}
              </p>
              <p className="text-xs opacity-90">
                {t('offline.indicator.wasOffline', 'Was offline for')} {formatDuration(offlineDuration)}
              </p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return null;
};

/**
 * Compact offline indicator for mobile/small screens
 */
export const CompactOfflineIndicator = ({ pendingCount = 0 }) => {
  const { isOnline } = useNetworkStatus();
  const { t } = useTranslation();

  if (isOnline && pendingCount === 0) {
    return null;
  }

  return (
    <div className={`fixed bottom-4 right-4 z-50 rounded-full shadow-lg px-4 py-2 flex items-center space-x-2 ${
      isOnline ? 'bg-blue-500' : 'bg-yellow-500'
    } text-white`}>
      {!isOnline ? (
        <>
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M18.364 5.636a9 9 0 010 12.728m0 0l-2.829-2.829m2.829 2.829L21 21M15.536 8.464a5 5 0 010 7.072m0 0l-2.829-2.829m-4.243 2.829a4.978 4.978 0 01-1.414-2.83m-1.414 5.658a9 9 0 01-2.167-9.238m7.824 2.167a1 1 0 111.414 1.414m-1.414-1.414L3 3" />
          </svg>
          <span className="text-sm font-medium">{t('offline.indicator.offline', 'Offline')}</span>
        </>
      ) : (
        <>
          <svg className="w-4 h-4 animate-spin" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
          <span className="text-sm font-medium">{pendingCount}</span>
        </>
      )}
    </div>
  );
};

/**
 * Inline offline badge for use within other components
 */
export const OfflineBadge = ({ className = '' }) => {
  const { isOnline } = useNetworkStatus();
  const { t } = useTranslation();

  if (isOnline) {
    return null;
  }

  return (
    <span className={`inline-flex items-center px-2 py-1 rounded text-xs font-medium bg-yellow-100 text-yellow-800 ${className}`}>
      <svg className="w-3 h-3 mr-1" fill="currentColor" viewBox="0 0 20 20">
        <path fillRule="evenodd" d="M13.477 14.89A6 6 0 015.11 6.524l8.367 8.368zm1.414-1.414L6.524 5.11a6 6 0 018.367 8.367zM18 10a8 8 0 11-16 0 8 8 0 0116 0z" clipRule="evenodd" />
      </svg>
      {t('offline.badge.offline', 'Offline')}
    </span>
  );
};

/**
 * Sync status badge showing pending operations
 */
export const SyncStatusBadge = ({ pendingCount = 0, className = '' }) => {
  const { isOnline } = useNetworkStatus();
  const { t } = useTranslation();

  if (pendingCount === 0) {
    return null;
  }

  return (
    <span className={`inline-flex items-center px-2 py-1 rounded text-xs font-medium ${
      isOnline ? 'bg-blue-100 text-blue-800' : 'bg-yellow-100 text-yellow-800'
    } ${className}`}>
      {isOnline ? (
        <svg className="w-3 h-3 mr-1 animate-spin" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
        </svg>
      ) : (
        <svg className="w-3 h-3 mr-1" fill="currentColor" viewBox="0 0 20 20">
          <path d="M10 2a6 6 0 00-6 6v3.586l-.707.707A1 1 0 004 14h12a1 1 0 00.707-1.707L16 11.586V8a6 6 0 00-6-6zM10 18a3 3 0 01-3-3h6a3 3 0 01-3 3z" />
        </svg>
      )}
      {pendingCount} {t('offline.badge.pending', 'pending')}
    </span>
  );
};

export default OfflineIndicator;
