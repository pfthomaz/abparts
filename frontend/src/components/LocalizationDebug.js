import React, { useEffect } from 'react';
import { useAuth } from '../AuthContext';
import { useLocalization } from '../contexts/LocalizationContext';
import { useTranslation } from '../hooks/useTranslation';

const LocalizationDebug = () => {
  const { user } = useAuth();
  const { currentLanguage } = useLocalization();
  const { t } = useTranslation();

  useEffect(() => {
    console.log('=== LOCALIZATION DEBUG ===');
    console.log('User object:', user);
    console.log('User preferred_language:', user?.preferred_language);
    console.log('Current language from context:', currentLanguage);
    console.log('Test translation (common.save):', t('common.save'));
    console.log('Test translation (dailyOperations.title):', t('dailyOperations.title'));
    console.log('========================');
  }, [user, currentLanguage, t]);

  return (
    <div className="fixed bottom-4 right-4 bg-yellow-100 border-2 border-yellow-500 p-4 rounded shadow-lg text-xs max-w-sm">
      <h3 className="font-bold mb-2">🐛 Localization Debug</h3>
      <div className="space-y-1">
        <div><strong>User:</strong> {user?.username || 'Not logged in'}</div>
        <div><strong>User preferred_language:</strong> {user?.preferred_language || 'Not set'}</div>
        <div><strong>Current language:</strong> {currentLanguage}</div>
        <div><strong>Translation test:</strong> {t('common.save')}</div>
        <div><strong>Daily Ops title:</strong> {t('dailyOperations.title')}</div>
      </div>
    </div>
  );
};

export default LocalizationDebug;
