// frontend/src/components/ProtocolTranslationForm.js

import React, { useState, useEffect } from 'react';
import { useTranslation } from '../hooks/useTranslation';
import translationService from '../services/translationService';

const ProtocolTranslationForm = ({ protocol, languageCode, onSave, onCancel }) => {
  const { t } = useTranslation();
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [existingTranslation, setExistingTranslation] = useState(null);
  const [formData, setFormData] = useState({
    name: '',
    description: ''
  });
  const [errors, setErrors] = useState({});

  const language = translationService.getLanguageByCode(languageCode);

  useEffect(() => {
    loadExistingTranslation();
  }, [protocol.id, languageCode]);

  const loadExistingTranslation = async () => {
    try {
      setLoading(true);
      const translations = await translationService.getProtocolTranslations(protocol.id);
      const existing = translations.find(t => t.language_code === languageCode);
      
      if (existing) {
        setExistingTranslation(existing);
        setFormData({
          name: existing.name || '',
          description: existing.description || ''
        });
      } else {
        // Initialize with base language content for reference
        setFormData({
          name: protocol.name || '',
          description: protocol.description || ''
        });
      }
    } catch (error) {
      console.error('Failed to load existing translation:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
    
    // Clear error when user starts typing
    if (errors[field]) {
      setErrors(prev => ({
        ...prev,
        [field]: null
      }));
    }
  };

  const validateForm = () => {
    const newErrors = {};
    
    if (!formData.name.trim()) {
      newErrors.name = t('translations.errors.nameRequired');
    }
    
    if (!formData.description.trim()) {
      newErrors.description = t('translations.errors.descriptionRequired');
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }

    try {
      setSaving(true);
      
      const translationData = {
        language_code: languageCode,
        name: formData.name.trim(),
        description: formData.description.trim()
      };

      if (existingTranslation) {
        await translationService.updateProtocolTranslation(
          protocol.id, 
          languageCode, 
          translationData
        );
      } else {
        await translationService.createProtocolTranslation(
          protocol.id, 
          translationData
        );
      }

      onSave();
    } catch (error) {
      console.error('Failed to save translation:', error);
      setErrors({
        submit: error.response?.data?.detail || t('translations.errors.saveFailed')
      });
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="text-center py-12">
          <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          <p className="mt-2 text-gray-600">{t('common.loading')}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
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
              {existingTranslation ? t('translations.editTranslation') : t('translations.createTranslation')}
            </h1>
            <p className="mt-2 text-gray-600">
              {t('translations.translateProtocolTo')} {language?.name}
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

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Original Content (Reference) */}
        <div className="bg-gray-50 rounded-lg p-6">
          <h2 className="text-lg font-medium text-gray-900 mb-4">
            {t('translations.originalContent')} ({t('translations.baseLanguage')})
          </h2>
          
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                {t('protocolForm.fields.name')}
              </label>
              <div className="bg-white p-3 rounded border text-gray-900">
                {protocol.name}
              </div>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                {t('protocolForm.fields.description')}
              </label>
              <div className="bg-white p-3 rounded border text-gray-900 min-h-[100px]">
                {protocol.description || t('common.noDescription')}
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                {t('protocolForm.fields.type')}
              </label>
              <div className="bg-white p-3 rounded border">
                <span className="px-3 py-1 rounded-full text-sm font-medium bg-blue-100 text-blue-800">
                  {t(`maintenanceProtocols.types.${protocol.protocol_type}`)}
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* Translation Form */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-medium text-gray-900 mb-4">
            {t('translations.translationContent')} ({language?.name})
          </h2>

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                {t('protocolForm.fields.name')} *
              </label>
              <input
                type="text"
                value={formData.name}
                onChange={(e) => handleInputChange('name', e.target.value)}
                className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                  errors.name ? 'border-red-500' : 'border-gray-300'
                }`}
                placeholder={t('translations.enterTranslation')}
                dir={languageCode === 'ar' ? 'rtl' : 'ltr'}
              />
              {errors.name && (
                <p className="mt-1 text-sm text-red-600">{errors.name}</p>
              )}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                {t('protocolForm.fields.description')} *
              </label>
              <textarea
                value={formData.description}
                onChange={(e) => handleInputChange('description', e.target.value)}
                rows={4}
                className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                  errors.description ? 'border-red-500' : 'border-gray-300'
                }`}
                placeholder={t('translations.enterTranslation')}
                dir={languageCode === 'ar' ? 'rtl' : 'ltr'}
              />
              {errors.description && (
                <p className="mt-1 text-sm text-red-600">{errors.description}</p>
              )}
            </div>

            {errors.submit && (
              <div className="bg-red-50 border border-red-200 rounded-md p-3">
                <p className="text-sm text-red-600">{errors.submit}</p>
              </div>
            )}

            <div className="flex justify-end space-x-3 pt-4">
              <button
                type="button"
                onClick={onCancel}
                className="px-4 py-2 text-gray-700 bg-gray-100 rounded-md hover:bg-gray-200"
                disabled={saving}
              >
                {t('common.cancel')}
              </button>
              <button
                type="submit"
                className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
                disabled={saving}
              >
                {saving ? (
                  <div className="flex items-center">
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                    {t('common.saving')}
                  </div>
                ) : (
                  existingTranslation ? t('common.update') : t('common.create')
                )}
              </button>
            </div>
          </form>
        </div>
      </div>

      {/* Translation Tips */}
      <div className="mt-8 bg-blue-50 rounded-lg p-6">
        <h3 className="text-lg font-medium text-blue-900 mb-3">
          {t('translations.translationTips')}
        </h3>
        <ul className="space-y-2 text-sm text-blue-800">
          <li>• {t('translations.tip1')}</li>
          <li>• {t('translations.tip2')}</li>
          <li>• {t('translations.tip3')}</li>
          <li>• {t('translations.tip4')}</li>
        </ul>
      </div>
    </div>
  );
};

export default ProtocolTranslationForm;