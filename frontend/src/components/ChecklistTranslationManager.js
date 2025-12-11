// frontend/src/components/ChecklistTranslationManager.js

import React, { useState, useEffect } from 'react';
import { useTranslation } from '../hooks/useTranslation';
import translationService from '../services/translationService';

const ChecklistTranslationManager = ({ protocol, languageCode, onSave, onCancel }) => {
  const { t } = useTranslation();
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [checklistItems, setChecklistItems] = useState([]);
  const [translations, setTranslations] = useState({});
  const [errors, setErrors] = useState({});

  const language = translationService.getLanguageByCode(languageCode);

  useEffect(() => {
    loadChecklistData();
  }, [protocol.id, languageCode]);

  const loadChecklistData = async () => {
    try {
      setLoading(true);
      
      // Get localized checklist items (this will show base language items)
      const localizedItems = await translationService.getLocalizedChecklistItems(protocol.id, 'en');
      setChecklistItems(localizedItems);

      // Load existing translations for this language
      const translationPromises = localizedItems.map(async (item) => {
        try {
          const itemTranslations = await translationService.getChecklistItemTranslations(item.id);
          const existing = itemTranslations.find(t => t.language_code === languageCode);
          return { itemId: item.id, translation: existing };
        } catch (error) {
          return { itemId: item.id, translation: null };
        }
      });

      const translationResults = await Promise.all(translationPromises);
      const translationsMap = {};
      
      translationResults.forEach(({ itemId, translation }) => {
        translationsMap[itemId] = {
          description: translation?.description || '',
          notes: translation?.notes || ''
        };
      });

      setTranslations(translationsMap);
    } catch (error) {
      console.error('Failed to load checklist data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleTranslationChange = (itemId, field, value) => {
    setTranslations(prev => ({
      ...prev,
      [itemId]: {
        ...prev[itemId],
        [field]: value
      }
    }));

    // Clear error when user starts typing
    const errorKey = `${itemId}.${field}`;
    if (errors[errorKey]) {
      setErrors(prev => ({
        ...prev,
        [errorKey]: null
      }));
    }
  };

  const validateTranslations = () => {
    const newErrors = {};
    
    checklistItems.forEach(item => {
      const translation = translations[item.id];
      if (!translation?.description?.trim()) {
        newErrors[`${item.id}.description`] = t('translations.errors.descriptionRequired');
      }
    });

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSaveAll = async () => {
    if (!validateTranslations()) {
      return;
    }

    try {
      setSaving(true);
      
      const savePromises = checklistItems.map(async (item) => {
        const translation = translations[item.id];
        if (!translation?.description?.trim()) return;

        const translationData = {
          language_code: languageCode,
          description: translation.description.trim(),
          notes: translation.notes?.trim() || null
        };

        try {
          // Try to get existing translation first
          const existingTranslations = await translationService.getChecklistItemTranslations(item.id);
          const existing = existingTranslations.find(t => t.language_code === languageCode);

          if (existing) {
            return translationService.updateChecklistItemTranslation(
              item.id,
              languageCode,
              translationData
            );
          } else {
            return translationService.createChecklistItemTranslation(
              item.id,
              translationData
            );
          }
        } catch (error) {
          console.error(`Failed to save translation for item ${item.id}:`, error);
          throw error;
        }
      });

      await Promise.all(savePromises);
      onSave();
    } catch (error) {
      console.error('Failed to save translations:', error);
      setErrors({
        submit: error.response?.data?.detail || t('translations.errors.saveFailed')
      });
    } finally {
      setSaving(false);
    }
  };

  const getCompletionStats = () => {
    const totalItems = checklistItems.length;
    const completedItems = checklistItems.filter(item => 
      translations[item.id]?.description?.trim()
    ).length;
    
    return {
      completed: completedItems,
      total: totalItems,
      percentage: totalItems > 0 ? Math.round((completedItems / totalItems) * 100) : 0
    };
  };

  if (loading) {
    return (
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="text-center py-12">
          <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          <p className="mt-2 text-gray-600">{t('common.loading')}</p>
        </div>
      </div>
    );
  }

  const stats = getCompletionStats();

  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Header */}
      <div className="mb-6">
        <button
          onClick={onCancel}
          className="text-blue-600 hover:text-blue-800 mb-4 flex items-center"
        >
          ← {t('common.back')}
        </button>
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">
              {t('translations.translateChecklist')}
            </h1>
            <p className="mt-2 text-gray-600">
              {protocol.name} - {t('translations.translateTo')} {language?.name}
            </p>
          </div>
          <div className="flex items-center space-x-4">
            <div className="text-right">
              <p className="text-sm text-gray-600">{t('translations.progress')}</p>
              <p className="text-2xl font-bold text-blue-600">
                {stats.completed}/{stats.total}
              </p>
            </div>
            <div className="flex items-center space-x-2">
              <span className="text-3xl">{language?.flag}</span>
              <div>
                <p className="font-medium text-gray-900">{language?.name}</p>
                <p className="text-sm text-gray-500">{language?.nativeName}</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Progress Bar */}
      <div className="mb-6 bg-white rounded-lg shadow p-4">
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm font-medium text-gray-700">
            {t('translations.translationProgress')}
          </span>
          <span className="text-sm text-gray-600">{stats.percentage}%</span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-2">
          <div 
            className="bg-blue-600 h-2 rounded-full transition-all duration-300"
            style={{ width: `${stats.percentage}%` }}
          ></div>
        </div>
      </div>

      {/* Checklist Items */}
      <div className="space-y-6">
        {checklistItems.map((item, index) => {
          const translation = translations[item.id] || {};
          const hasTranslation = translation.description?.trim();
          
          return (
            <div key={item.id} className="bg-white rounded-lg shadow">
              <div className="p-6">
                <div className="flex items-start justify-between mb-4">
                  <div className="flex items-center space-x-3">
                    <span className="flex-shrink-0 w-8 h-8 bg-blue-100 text-blue-800 rounded-full flex items-center justify-center text-sm font-medium">
                      {index + 1}
                    </span>
                    <div>
                      <h3 className="text-lg font-medium text-gray-900">
                        {t('translations.checklistItem')} {index + 1}
                      </h3>
                      <p className="text-sm text-gray-600">
                        {t('translations.step')} {item.step_number}
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center space-x-2">
                    {hasTranslation ? (
                      <span className="px-2 py-1 rounded text-xs font-medium bg-green-100 text-green-800">
                        ✅ {t('translations.translated')}
                      </span>
                    ) : (
                      <span className="px-2 py-1 rounded text-xs font-medium bg-gray-100 text-gray-600">
                        ⏳ {t('translations.pending')}
                      </span>
                    )}
                  </div>
                </div>

                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                  {/* Original Content */}
                  <div className="bg-gray-50 rounded-lg p-4">
                    <h4 className="font-medium text-gray-900 mb-3">
                      {t('translations.originalContent')} ({t('translations.baseLanguage')})
                    </h4>
                    
                    <div className="space-y-3">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          {t('maintenanceProtocols.description')}
                        </label>
                        <div className="bg-white p-3 rounded border text-gray-900">
                          {item.description}
                        </div>
                      </div>
                      
                      {item.notes && (
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-1">
                            {t('maintenanceProtocols.notes')}
                          </label>
                          <div className="bg-white p-3 rounded border text-gray-900">
                            {item.notes}
                          </div>
                        </div>
                      )}
                    </div>
                  </div>

                  {/* Translation Form */}
                  <div>
                    <h4 className="font-medium text-gray-900 mb-3">
                      {t('translations.translationContent')} ({language?.name})
                    </h4>
                    
                    <div className="space-y-3">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          {t('maintenanceProtocols.description')} *
                        </label>
                        <textarea
                          value={translation.description || ''}
                          onChange={(e) => handleTranslationChange(item.id, 'description', e.target.value)}
                          rows={3}
                          className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                            errors[`${item.id}.description`] ? 'border-red-500' : 'border-gray-300'
                          }`}
                          placeholder={t('translations.enterTranslation')}
                          dir={languageCode === 'ar' ? 'rtl' : 'ltr'}
                        />
                        {errors[`${item.id}.description`] && (
                          <p className="mt-1 text-sm text-red-600">
                            {errors[`${item.id}.description`]}
                          </p>
                        )}
                      </div>
                      
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          {t('maintenanceProtocols.notes')} ({t('common.optional')})
                        </label>
                        <textarea
                          value={translation.notes || ''}
                          onChange={(e) => handleTranslationChange(item.id, 'notes', e.target.value)}
                          rows={2}
                          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                          placeholder={t('translations.enterTranslation')}
                          dir={languageCode === 'ar' ? 'rtl' : 'ltr'}
                        />
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Actions */}
      <div className="mt-8 bg-white rounded-lg shadow p-6">
        {errors.submit && (
          <div className="mb-4 bg-red-50 border border-red-200 rounded-md p-3">
            <p className="text-sm text-red-600">{errors.submit}</p>
          </div>
        )}
        
        <div className="flex justify-between items-center">
          <div className="text-sm text-gray-600">
            {t('translations.saveAllTranslations')} ({stats.completed}/{stats.total} {t('translations.completed')})
          </div>
          
          <div className="flex space-x-3">
            <button
              onClick={onCancel}
              className="px-4 py-2 text-gray-700 bg-gray-100 rounded-md hover:bg-gray-200"
              disabled={saving}
            >
              {t('common.cancel')}
            </button>
            <button
              onClick={handleSaveAll}
              className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
              disabled={saving || stats.completed === 0}
            >
              {saving ? (
                <div className="flex items-center">
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                  {t('translations.saving')}
                </div>
              ) : (
                `${t('translations.saveAll')} (${stats.completed})`
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ChecklistTranslationManager;