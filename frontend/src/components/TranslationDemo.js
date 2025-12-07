// frontend/src/components/TranslationDemo.js
// Demo component to show translations working

import React from 'react';
import { useTranslation } from '../hooks/useTranslation';
import { useLocalization } from '../contexts/LocalizationContext';

const TranslationDemo = () => {
  const { t } = useTranslation();
  const { currentLanguage, updateLanguage, supportedLanguages } = useLocalization();

  return (
    <div className="bg-white p-6 rounded-lg shadow-md max-w-2xl mx-auto my-8">
      <h2 className="text-2xl font-bold mb-4">{t('common.success')} - Translations Working!</h2>
      
      <div className="mb-6">
        <p className="text-gray-600 mb-2">Current Language: <strong>{currentLanguage}</strong></p>
        
        <div className="flex gap-2 mb-4">
          {Object.keys(supportedLanguages).map(lang => (
            <button
              key={lang}
              onClick={() => updateLanguage(lang)}
              className={`px-4 py-2 rounded ${
                currentLanguage === lang 
                  ? 'bg-blue-600 text-white' 
                  : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
              }`}
            >
              {supportedLanguages[lang].nativeName}
            </button>
          ))}
        </div>
      </div>

      <div className="space-y-4">
        <div className="border-t pt-4">
          <h3 className="font-semibold mb-2">Common Buttons:</h3>
          <div className="flex flex-wrap gap-2">
            <button className="px-4 py-2 bg-blue-600 text-white rounded">{t('common.save')}</button>
            <button className="px-4 py-2 bg-gray-600 text-white rounded">{t('common.cancel')}</button>
            <button className="px-4 py-2 bg-red-600 text-white rounded">{t('common.delete')}</button>
            <button className="px-4 py-2 bg-green-600 text-white rounded">{t('common.edit')}</button>
            <button className="px-4 py-2 bg-indigo-600 text-white rounded">{t('common.add')}</button>
          </div>
        </div>

        <div className="border-t pt-4">
          <h3 className="font-semibold mb-2">Navigation Items:</h3>
          <ul className="space-y-1">
            <li>📊 {t('navigation.dashboard')}</li>
            <li>🏢 {t('navigation.organizations')}</li>
            <li>👥 {t('navigation.users')}</li>
            <li>🔧 {t('navigation.parts')}</li>
            <li>📦 {t('navigation.warehouses')}</li>
            <li>🤖 {t('navigation.machines')}</li>
            <li>📋 {t('navigation.orders')}</li>
            <li>🔧 {t('navigation.maintenance')}</li>
          </ul>
        </div>

        <div className="border-t pt-4">
          <h3 className="font-semibold mb-2">User Management:</h3>
          <ul className="space-y-1">
            <li>{t('users.addUser')}</li>
            <li>{t('users.editUser')}</li>
            <li>{t('users.username')}</li>
            <li>{t('users.email')}</li>
            <li>{t('users.preferredLanguage')}</li>
          </ul>
        </div>

        <div className="border-t pt-4">
          <h3 className="font-semibold mb-2">Validation Messages:</h3>
          <ul className="space-y-1">
            <li>❌ {t('validation.required')}</li>
            <li>❌ {t('validation.invalidEmail')}</li>
            <li>❌ {t('validation.minLength', { min: 8 })}</li>
          </ul>
        </div>

        <div className="border-t pt-4">
          <h3 className="font-semibold mb-2">Error Messages:</h3>
          <ul className="space-y-1">
            <li>⚠️ {t('errors.generic')}</li>
            <li>⚠️ {t('errors.unauthorized')}</li>
            <li>⚠️ {t('errors.networkError')}</li>
          </ul>
        </div>
      </div>

      <div className="mt-6 p-4 bg-green-50 border border-green-200 rounded">
        <p className="text-green-800 font-semibold">
          ✅ Translations are working! Change the language above to see the text update.
        </p>
        <p className="text-green-700 text-sm mt-2">
          Your user's preferred language is: <strong>{currentLanguage}</strong>
        </p>
      </div>
    </div>
  );
};

export default TranslationDemo;
