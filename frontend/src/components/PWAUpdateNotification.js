// PWA Update Notification Component
// Notifies users when a new version is available
import React from 'react';
import { usePWA } from '../contexts/PWAContext';
import { useTranslation } from '../hooks/useTranslation';

const PWAUpdateNotification = () => {
  const { t } = useTranslation();
  const { updateAvailable, updateApp } = usePWA();

  if (!updateAvailable) {
    return null;
  }

  return (
    <div className="fixed top-4 left-4 right-4 md:left-auto md:right-4 md:w-96 z-50 bg-blue-600 text-white rounded-lg shadow-2xl p-4 animate-slide-down">
      <div className="flex items-start space-x-3">
        <div className="flex-shrink-0">
          <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
        </div>
        <div className="flex-1 min-w-0">
          <h3 className="text-sm font-semibold mb-1">
            {t('pwa.update.title')}
          </h3>
          <p className="text-xs opacity-90 mb-3">
            {t('pwa.update.description')}
          </p>
          <button
            onClick={updateApp}
            className="w-full px-3 py-2 bg-white text-blue-600 hover:bg-blue-50 text-xs font-medium rounded-md transition-colors duration-200"
          >
            {t('pwa.update.reload')}
          </button>
        </div>
      </div>
    </div>
  );
};

export default PWAUpdateNotification;
