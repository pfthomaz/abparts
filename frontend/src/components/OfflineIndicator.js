// Offline Indicator Component
// Shows connection status and queued messages count
import React from 'react';
import { usePWA } from '../contexts/PWAContext';
import { useTranslation } from '../hooks/useTranslation';

const OfflineIndicator = () => {
  const { t } = useTranslation();
  const { isOnline, messageQueue, connectionQuality } = usePWA();

  // Don't show anything if online with good connection
  if (isOnline && connectionQuality !== 'poor' && connectionQuality !== 'moderate') {
    return null;
  }

  const getStatusColor = () => {
    if (!isOnline) return 'bg-red-500';
    if (connectionQuality === 'poor') return 'bg-orange-500';
    if (connectionQuality === 'moderate') return 'bg-yellow-500';
    return 'bg-green-500';
  };

  const getStatusText = () => {
    if (!isOnline) {
      return messageQueue.length > 0
        ? t('pwa.offline.withQueue', { count: messageQueue.length })
        : t('pwa.offline.noConnection');
    }
    if (connectionQuality === 'poor') return t('pwa.connection.poor');
    if (connectionQuality === 'moderate') return t('pwa.connection.moderate');
    return t('pwa.connection.good');
  };

  const getStatusIcon = () => {
    if (!isOnline) {
      return (
        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M18.364 5.636a9 9 0 010 12.728m0 0l-2.829-2.829m2.829 2.829L21 21M15.536 8.464a5 5 0 010 7.072m0 0l-2.829-2.829m-4.243 2.829a4.978 4.978 0 01-1.414-2.83m-1.414 5.658a9 9 0 01-2.167-9.238m7.824 2.167a1 1 0 111.414 1.414m-1.414-1.414L3 3" />
        </svg>
      );
    }
    if (connectionQuality === 'poor' || connectionQuality === 'moderate') {
      return (
        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
        </svg>
      );
    }
    return null;
  };

  return (
    <div className={`fixed top-0 left-0 right-0 z-50 ${getStatusColor()} text-white px-4 py-2 shadow-lg`}>
      <div className="max-w-7xl mx-auto flex items-center justify-center space-x-2">
        {getStatusIcon()}
        <span className="text-sm font-medium">{getStatusText()}</span>
        {messageQueue.length > 0 && (
          <span className="ml-2 px-2 py-0.5 bg-white bg-opacity-20 rounded-full text-xs">
            {messageQueue.length} {t('pwa.offline.queued')}
          </span>
        )}
      </div>
    </div>
  );
};

export default OfflineIndicator;
