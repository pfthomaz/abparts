// frontend/src/components/AutoTranslateModal.js

import React, { useState, useEffect } from 'react';
import { useTranslation } from '../hooks/useTranslation';
import translationService from '../services/translationService';

const AutoTranslateModal = ({ 
  isOpen, 
  onClose, 
  protocol, 
  onTranslationComplete 
}) => {
  const { t } = useTranslation();
  const [selectedLanguages, setSelectedLanguages] = useState([]);
  const [translationType, setTranslationType] = useState('complete'); // 'protocol', 'checklist', 'complete'
  const [isTranslating, setIsTranslating] = useState(false);
  const [translationResults, setTranslationResults] = useState(null);
  const [error, setError] = useState(null);
  const [serviceStatus, setServiceStatus] = useState(null);

  const supportedLanguages = translationService.getSupportedLanguages().filter(lang => lang.code !== 'en');

  useEffect(() => {
    if (isOpen) {
      checkServiceStatus();
      // Pre-select all languages by default
      setSelectedLanguages(supportedLanguages.map(lang => lang.code));
    }
  }, [isOpen]);

  const checkServiceStatus = async () => {
    try {
      const status = await translationService.getAutoTranslateStatus();
      setServiceStatus(status);
      if (!status.service_available) {
        setError(t('translations.autoTranslate.serviceUnavailable'));
      }
    } catch (error) {
      console.error('Failed to check auto-translate status:', error);
      setError(t('translations.autoTranslate.statusCheckFailed'));
    }
  };

  const handleLanguageToggle = (languageCode) => {
    setSelectedLanguages(prev => 
      prev.includes(languageCode)
        ? prev.filter(code => code !== languageCode)
        : [...prev, languageCode]
    );
  };

  const handleSelectAll = () => {
    setSelectedLanguages(supportedLanguages.map(lang => lang.code));
  };

  const handleSelectNone = () => {
    setSelectedLanguages([]);
  };

  const handleStartTranslation = async () => {
    if (selectedLanguages.length === 0) {
      setError(t('translations.autoTranslate.selectLanguages'));
      return;
    }

    setIsTranslating(true);
    setError(null);
    setTranslationResults(null);

    try {
      let result;
      
      switch (translationType) {
        case 'protocol':
          result = await translationService.autoTranslateProtocol(protocol.id, selectedLanguages);
          break;
        case 'checklist':
          result = await translationService.autoTranslateProtocolChecklist(protocol.id, selectedLanguages);
          break;
        case 'complete':
          result = await translationService.autoTranslateCompleteProtocol(protocol.id, selectedLanguages);
          break;
        default:
          throw new Error('Invalid translation type');
      }

      setTranslationResults(result);
      
      // Call completion callback after successful translation
      if (onTranslationComplete) {
        onTranslationComplete(result);
      }

    } catch (error) {
      console.error('Auto-translation failed:', error);
      setError(error.response?.data?.detail || t('translations.autoTranslate.failed'));
    } finally {
      setIsTranslating(false);
    }
  };

  const handleClose = () => {
    if (!isTranslating) {
      setSelectedLanguages([]);
      setTranslationType('complete');
      setTranslationResults(null);
      setError(null);
      onClose();
    }
  };

  const renderTranslationResults = () => {
    if (!translationResults) return null;

    const getResultStats = () => {
      if (translationType === 'complete') {
        const protocolStats = translationResults.protocol_translation;
        const checklistStats = translationResults.checklist_translation;
        return {
          totalSuccessful: translationResults.total_successful_translations,
          totalFailed: translationResults.total_failed_translations,
          protocolSuccessful: protocolStats.successful_translations,
          checklistSuccessful: checklistStats.successful_translations
        };
      } else {
        return {
          totalSuccessful: translationResults.successful_translations,
          totalFailed: translationResults.failed_translations
        };
      }
    };

    const stats = getResultStats();

    return (
      <div className="mt-6 p-4 bg-gray-50 rounded-lg">
        <h4 className="font-medium text-gray-900 mb-3">
          {t('translations.autoTranslate.results')}
        </h4>
        
        <div className="grid grid-cols-2 gap-4 mb-4">
          <div className="text-center">
            <div className="text-2xl font-bold text-green-600">{stats.totalSuccessful}</div>
            <div className="text-sm text-gray-600">{t('translations.autoTranslate.successful')}</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-red-600">{stats.totalFailed}</div>
            <div className="text-sm text-gray-600">{t('translations.autoTranslate.failed')}</div>
          </div>
        </div>

        {translationType === 'complete' && (
          <div className="text-sm text-gray-600 space-y-1">
            <div>• {t('translations.autoTranslate.protocolTranslations')}: {stats.protocolSuccessful}</div>
            <div>• {t('translations.autoTranslate.checklistTranslations')}: {stats.checklistSuccessful}</div>
          </div>
        )}

        <div className="mt-4 text-sm text-gray-600">
          <p>{translationResults.message}</p>
        </div>
      </div>
    );
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full mx-4 max-h-[90vh] overflow-y-auto">
        <div className="p-6">
          {/* Header */}
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-xl font-bold text-gray-900">
              {t('translations.autoTranslate.title')}
            </h2>
            <button
              onClick={handleClose}
              disabled={isTranslating}
              className="text-gray-400 hover:text-gray-600 disabled:opacity-50"
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          {/* Service Status */}
          {serviceStatus && !serviceStatus.service_available && (
            <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
              <div className="flex items-center">
                <svg className="w-5 h-5 text-red-400 mr-2" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                </svg>
                <span className="text-red-800">{t('translations.autoTranslate.serviceUnavailable')}</span>
              </div>
            </div>
          )}

          {/* Protocol Info */}
          <div className="mb-6 p-4 bg-blue-50 rounded-lg">
            <h3 className="font-medium text-blue-900 mb-2">{protocol.name}</h3>
            <p className="text-sm text-blue-700">
              {protocol.description || t('common.noDescription')}
            </p>
            <div className="mt-2 text-sm text-blue-600">
              {protocol.checklist_items?.length || 0} {t('translations.checklistItems')}
            </div>
          </div>

          {/* Translation Type Selection */}
          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-700 mb-3">
              {t('translations.autoTranslate.translationType')}
            </label>
            <div className="space-y-2">
              <label className="flex items-center">
                <input
                  type="radio"
                  name="translationType"
                  value="complete"
                  checked={translationType === 'complete'}
                  onChange={(e) => setTranslationType(e.target.value)}
                  disabled={isTranslating}
                  className="mr-3"
                />
                <div>
                  <div className="font-medium">{t('translations.autoTranslate.completeProtocol')}</div>
                  <div className="text-sm text-gray-600">{t('translations.autoTranslate.completeProtocolDesc')}</div>
                </div>
              </label>
              <label className="flex items-center">
                <input
                  type="radio"
                  name="translationType"
                  value="protocol"
                  checked={translationType === 'protocol'}
                  onChange={(e) => setTranslationType(e.target.value)}
                  disabled={isTranslating}
                  className="mr-3"
                />
                <div>
                  <div className="font-medium">{t('translations.autoTranslate.protocolOnly')}</div>
                  <div className="text-sm text-gray-600">{t('translations.autoTranslate.protocolOnlyDesc')}</div>
                </div>
              </label>
              <label className="flex items-center">
                <input
                  type="radio"
                  name="translationType"
                  value="checklist"
                  checked={translationType === 'checklist'}
                  onChange={(e) => setTranslationType(e.target.value)}
                  disabled={isTranslating}
                  className="mr-3"
                />
                <div>
                  <div className="font-medium">{t('translations.autoTranslate.checklistOnly')}</div>
                  <div className="text-sm text-gray-600">{t('translations.autoTranslate.checklistOnlyDesc')}</div>
                </div>
              </label>
            </div>
          </div>

          {/* Language Selection */}
          <div className="mb-6">
            <div className="flex items-center justify-between mb-3">
              <label className="block text-sm font-medium text-gray-700">
                {t('translations.autoTranslate.selectLanguages')}
              </label>
              <div className="space-x-2">
                <button
                  type="button"
                  onClick={handleSelectAll}
                  disabled={isTranslating}
                  className="text-sm text-blue-600 hover:text-blue-800 disabled:opacity-50"
                >
                  {t('common.selectAll')}
                </button>
                <button
                  type="button"
                  onClick={handleSelectNone}
                  disabled={isTranslating}
                  className="text-sm text-gray-600 hover:text-gray-800 disabled:opacity-50"
                >
                  {t('common.selectNone')}
                </button>
              </div>
            </div>
            
            <div className="grid grid-cols-2 gap-3">
              {supportedLanguages.map(language => (
                <label key={language.code} className="flex items-center p-3 border rounded-lg hover:bg-gray-50">
                  <input
                    type="checkbox"
                    checked={selectedLanguages.includes(language.code)}
                    onChange={() => handleLanguageToggle(language.code)}
                    disabled={isTranslating}
                    className="mr-3"
                  />
                  <div className="flex items-center space-x-2">
                    <span className="text-xl">{language.flag}</span>
                    <div>
                      <div className="font-medium">{language.name}</div>
                      <div className="text-sm text-gray-600">{language.nativeName}</div>
                    </div>
                  </div>
                </label>
              ))}
            </div>
          </div>

          {/* Error Display */}
          {error && (
            <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
              <div className="flex items-center">
                <svg className="w-5 h-5 text-red-400 mr-2" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                </svg>
                <span className="text-red-800">{error}</span>
              </div>
            </div>
          )}

          {/* Translation Results */}
          {renderTranslationResults()}

          {/* Actions */}
          <div className="flex justify-end space-x-3 pt-6 border-t">
            <button
              onClick={handleClose}
              disabled={isTranslating}
              className="px-4 py-2 text-gray-700 bg-gray-100 rounded-md hover:bg-gray-200 disabled:opacity-50"
            >
              {translationResults ? t('common.close') : t('common.cancel')}
            </button>
            
            {!translationResults && (
              <button
                onClick={handleStartTranslation}
                disabled={isTranslating || selectedLanguages.length === 0 || (serviceStatus && !serviceStatus.service_available)}
                className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 flex items-center"
              >
                {isTranslating && (
                  <svg className="animate-spin -ml-1 mr-3 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                )}
                {isTranslating ? t('translations.autoTranslate.translating') : t('translations.autoTranslate.startTranslation')}
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default AutoTranslateModal;