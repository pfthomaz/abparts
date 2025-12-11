// frontend/src/components/TranslationManager.js

import React, { useState, useEffect } from 'react';
import { useTranslation } from '../hooks/useTranslation';
import translationService from '../services/translationService';
import ProtocolTranslationForm from './ProtocolTranslationForm';
import ChecklistTranslationManager from './ChecklistTranslationManager';

const TranslationManager = ({ protocol, onBack, onUpdate }) => {
  const { t } = useTranslation();
  const [translationStatus, setTranslationStatus] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('overview');
  const [selectedLanguage, setSelectedLanguage] = useState(null);
  const [showProtocolForm, setShowProtocolForm] = useState(false);
  const [showChecklistManager, setShowChecklistManager] = useState(false);

  const supportedLanguages = translationService.getSupportedLanguages();

  useEffect(() => {
    loadTranslationStatus();
  }, [protocol.id]);

  const loadTranslationStatus = async () => {
    try {
      setLoading(true);
      const status = await translationService.getProtocolTranslationStatus(protocol.id);
      setTranslationStatus(status);
    } catch (error) {
      console.error('Failed to load translation status:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleLanguageSelect = (languageCode) => {
    setSelectedLanguage(languageCode);
    setShowProtocolForm(true);
  };

  const handleProtocolTranslationSave = () => {
    setShowProtocolForm(false);
    setSelectedLanguage(null);
    loadTranslationStatus();
    if (onUpdate) onUpdate();
  };

  const handleManageChecklist = (languageCode) => {
    setSelectedLanguage(languageCode);
    setShowChecklistManager(true);
  };

  const handleChecklistTranslationSave = () => {
    setShowChecklistManager(false);
    setSelectedLanguage(null);
    loadTranslationStatus();
    if (onUpdate) onUpdate();
  };

  const renderTranslationOverview = () => {
    if (loading) {
      return (
        <div className="text-center py-12">
          <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          <p className="mt-2 text-gray-600">{t('common.loading')}</p>
        </div>
      );
    }

    if (!translationStatus) {
      return (
        <div className="text-center py-12">
          <p className="text-gray-500">{t('translations.noStatus')}</p>
        </div>
      );
    }

    return (
      <div className="space-y-6">
        {/* Protocol Info */}
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-lg font-medium text-gray-900">{protocol.name}</h3>
              <p className="text-sm text-gray-600">
                {t('translations.baseLanguage')}: {translationStatus.base_language.toUpperCase()}
              </p>
            </div>
            <span className="px-3 py-1 rounded-full text-sm font-medium bg-blue-100 text-blue-800">
              {t(`maintenanceProtocols.types.${protocol.protocol_type}`)}
            </span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <p className="text-sm text-gray-600">{t('translations.totalItems')}</p>
              <p className="text-2xl font-bold text-gray-900">{translationStatus.total_items}</p>
            </div>
            <div>
              <p className="text-sm text-gray-600">{t('translations.completedLanguages')}</p>
              <p className="text-2xl font-bold text-green-600">
                {Object.values(translationStatus.completion_percentage).filter(p => p >= 100).length}
                <span className="text-lg text-gray-500">/{supportedLanguages.length}</span>
              </p>
            </div>
          </div>
        </div>

        {/* Language Status Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {supportedLanguages.map(language => {
            const percentage = translationStatus.completion_percentage[language.code] || 0;
            const isBaseLanguage = language.code === translationStatus.base_language;
            const statusColor = translationService.getTranslationStatusColor(percentage);
            const statusIcon = translationService.getTranslationStatusIcon(percentage);

            return (
              <div key={language.code} className="bg-white rounded-lg shadow p-4">
                <div className="flex items-center justify-between mb-3">
                  <div className="flex items-center space-x-2">
                    <span className="text-2xl">{language.flag}</span>
                    <div>
                      <h4 className="font-medium text-gray-900">{language.name}</h4>
                      <p className="text-sm text-gray-500">{language.nativeName}</p>
                    </div>
                  </div>
                  {isBaseLanguage && (
                    <span className="px-2 py-1 rounded text-xs font-medium bg-purple-100 text-purple-800">
                      {t('translations.baseLanguage')}
                    </span>
                  )}
                </div>

                <div className="mb-3">
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-sm text-gray-600">{t('translations.progress')}</span>
                    <span className={`px-2 py-1 rounded text-xs font-medium ${statusColor}`}>
                      {statusIcon} {percentage.toFixed(0)}%
                    </span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div 
                      className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                      style={{ width: `${percentage}%` }}
                    ></div>
                  </div>
                </div>

                <div className="flex gap-2">
                  <button
                    onClick={() => handleLanguageSelect(language.code)}
                    className="flex-1 bg-blue-50 text-blue-700 px-3 py-2 rounded text-sm hover:bg-blue-100"
                    disabled={isBaseLanguage}
                  >
                    {percentage > 0 ? t('translations.edit') : t('translations.start')}
                  </button>
                  {percentage > 0 && (
                    <button
                      onClick={() => handleManageChecklist(language.code)}
                      className="bg-green-50 text-green-700 px-3 py-2 rounded text-sm hover:bg-green-100"
                    >
                      {t('translations.checklist')}
                    </button>
                  )}
                </div>
              </div>
            );
          })}
        </div>

        {/* Quick Actions */}
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">{t('translations.quickActions')}</h3>
          <div className="flex flex-wrap gap-3">
            <button className="bg-purple-50 text-purple-700 px-4 py-2 rounded hover:bg-purple-100">
              {t('translations.exportTranslations')}
            </button>
            <button className="bg-orange-50 text-orange-700 px-4 py-2 rounded hover:bg-orange-100">
              {t('translations.importTranslations')}
            </button>
            <button className="bg-green-50 text-green-700 px-4 py-2 rounded hover:bg-green-100">
              {t('translations.bulkTranslate')}
            </button>
          </div>
        </div>
      </div>
    );
  };

  if (showProtocolForm) {
    return (
      <ProtocolTranslationForm
        protocol={protocol}
        languageCode={selectedLanguage}
        onSave={handleProtocolTranslationSave}
        onCancel={() => {
          setShowProtocolForm(false);
          setSelectedLanguage(null);
        }}
      />
    );
  }

  if (showChecklistManager) {
    return (
      <ChecklistTranslationManager
        protocol={protocol}
        languageCode={selectedLanguage}
        onSave={handleChecklistTranslationSave}
        onCancel={() => {
          setShowChecklistManager(false);
          setSelectedLanguage(null);
        }}
      />
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Header */}
      <div className="mb-6">
        <button
          onClick={onBack}
          className="text-blue-600 hover:text-blue-800 mb-4 flex items-center"
        >
          ← {t('common.back')}
        </button>
        <h1 className="text-3xl font-bold text-gray-900">{t('translations.manageTranslations')}</h1>
        <p className="mt-2 text-gray-600">
          {t('translations.manageTranslationsDescription')}
        </p>
      </div>

      {/* Tab Navigation */}
      <div className="border-b border-gray-200 mb-6">
        <nav className="-mb-px flex space-x-8">
          <button
            onClick={() => setActiveTab('overview')}
            className={`py-2 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'overview'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            {t('translations.overview')}
          </button>
        </nav>
      </div>

      {/* Content */}
      {activeTab === 'overview' && renderTranslationOverview()}
    </div>
  );
};

export default TranslationManager;