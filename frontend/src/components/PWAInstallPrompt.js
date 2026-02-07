// PWA Install Prompt Component
// Prompts users to install the app for better experience
import React from 'react';
import { usePWA } from '../contexts/PWAContext';
import { useTranslation } from '../hooks/useTranslation';

const PWAInstallPrompt = () => {
  const { t } = useTranslation();
  const { showInstallPrompt, installApp, dismissInstallPrompt } = usePWA();

  if (!showInstallPrompt) {
    return null;
  }

  const handleInstall = async () => {
    const installed = await installApp();
    if (installed) {
      // console.log('[PWA Install Prompt] App installed successfully');
    }
  };

  return (
    <div className="fixed bottom-20 left-4 right-4 md:left-auto md:right-4 md:w-96 z-40 bg-white dark:bg-gray-800 rounded-lg shadow-2xl border border-gray-200 dark:border-gray-700 p-4 animate-slide-up">
      <div className="flex items-start space-x-3">
        <div className="flex-shrink-0">
          <img src="/logo.png" alt="ABParts" className="w-12 h-12 rounded-lg" />
        </div>
        <div className="flex-1 min-w-0">
          <h3 className="text-sm font-semibold text-gray-900 dark:text-white mb-1">
            {t('pwa.install.title')}
          </h3>
          <p className="text-xs text-gray-600 dark:text-gray-400 mb-3">
            {t('pwa.install.description')}
          </p>
          <div className="flex space-x-2">
            <button
              onClick={handleInstall}
              className="flex-1 px-3 py-2 bg-blue-600 hover:bg-blue-700 text-white text-xs font-medium rounded-md transition-colors duration-200"
            >
              {t('pwa.install.install')}
            </button>
            <button
              onClick={dismissInstallPrompt}
              className="px-3 py-2 bg-gray-100 hover:bg-gray-200 dark:bg-gray-700 dark:hover:bg-gray-600 text-gray-700 dark:text-gray-300 text-xs font-medium rounded-md transition-colors duration-200"
            >
              {t('pwa.install.later')}
            </button>
          </div>
        </div>
        <button
          onClick={dismissInstallPrompt}
          className="flex-shrink-0 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
          aria-label={t('common.close')}
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>
    </div>
  );
};

export default PWAInstallPrompt;
