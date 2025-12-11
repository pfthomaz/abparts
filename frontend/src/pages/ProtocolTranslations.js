// frontend/src/pages/ProtocolTranslations.js

import React, { useState, useEffect } from 'react';
import { useTranslation } from '../hooks/useTranslation';
import { listProtocols } from '../services/maintenanceProtocolsService';
import translationService from '../services/translationService';
import TranslationManager from '../components/TranslationManager';

const ProtocolTranslations = () => {
  const { t } = useTranslation();
  const [protocols, setProtocols] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedProtocol, setSelectedProtocol] = useState(null);
  const [translationStatuses, setTranslationStatuses] = useState({});
  const [searchTerm, setSearchTerm] = useState('');
  const [filterType, setFilterType] = useState('all');

  const supportedLanguages = translationService.getSupportedLanguages();

  useEffect(() => {
    loadProtocols();
  }, []);

  const loadProtocols = async () => {
    try {
      setLoading(true);
      const data = await listProtocols();
      setProtocols(data);
      
      // Load translation status for each protocol
      const statusPromises = data.map(async (protocol) => {
        try {
          const status = await translationService.getProtocolTranslationStatus(protocol.id);
          return { protocolId: protocol.id, status };
        } catch (error) {
          return { protocolId: protocol.id, status: null };
        }
      });

      const statusResults = await Promise.all(statusPromises);
      const statusMap = {};
      statusResults.forEach(({ protocolId, status }) => {
        statusMap[protocolId] = status;
      });
      setTranslationStatuses(statusMap);
    } catch (error) {
      console.error('Failed to load protocols:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleProtocolSelect = (protocol) => {
    setSelectedProtocol(protocol);
  };

  const handleBackToList = () => {
    setSelectedProtocol(null);
    // Reload translation statuses after potential updates
    loadProtocols();
  };

  const getTranslationCompletionStats = (status) => {
    if (!status || !status.completion_percentage) {
      return { completed: 0, total: supportedLanguages.length, percentage: 0 };
    }

    const completedCount = Object.values(status.completion_percentage).filter(p => p >= 100).length;
    return {
      completed: completedCount,
      total: supportedLanguages.length,
      percentage: Math.round((completedCount / supportedLanguages.length) * 100)
    };
  };

  const getStatusColor = (percentage) => {
    if (percentage >= 100) return 'bg-green-100 text-green-800';
    if (percentage >= 80) return 'bg-yellow-100 text-yellow-800';
    if (percentage >= 50) return 'bg-orange-100 text-orange-800';
    return 'bg-red-100 text-red-800';
  };

  const filteredProtocols = protocols.filter(protocol => {
    const matchesSearch = protocol.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         protocol.description?.toLowerCase().includes(searchTerm.toLowerCase());
    
    if (filterType === 'all') return matchesSearch;
    
    const status = translationStatuses[protocol.id];
    const stats = getTranslationCompletionStats(status);
    
    switch (filterType) {
      case 'completed':
        return matchesSearch && stats.percentage === 100;
      case 'partial':
        return matchesSearch && stats.percentage > 0 && stats.percentage < 100;
      case 'untranslated':
        return matchesSearch && stats.percentage === 0;
      default:
        return matchesSearch;
    }
  });

  if (selectedProtocol) {
    return (
      <TranslationManager
        protocol={selectedProtocol}
        onBack={handleBackToList}
        onUpdate={loadProtocols}
      />
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">{t('translations.manageTranslations')}</h1>
        <p className="mt-2 text-gray-600">
          {t('translations.manageTranslationsDescription')}
        </p>
      </div>

      {/* Stats Overview */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                <span className="text-blue-600 font-semibold">📋</span>
              </div>
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">{t('translations.totalProtocols')}</p>
              <p className="text-2xl font-bold text-gray-900">{protocols.length}</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <div className="w-8 h-8 bg-green-100 rounded-full flex items-center justify-center">
                <span className="text-green-600 font-semibold">✅</span>
              </div>
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">{t('translations.fullyTranslated')}</p>
              <p className="text-2xl font-bold text-green-600">
                {filteredProtocols.filter(p => {
                  const stats = getTranslationCompletionStats(translationStatuses[p.id]);
                  return stats.percentage === 100;
                }).length}
              </p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <div className="w-8 h-8 bg-yellow-100 rounded-full flex items-center justify-center">
                <span className="text-yellow-600 font-semibold">🟡</span>
              </div>
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">{t('translations.partiallyTranslated')}</p>
              <p className="text-2xl font-bold text-yellow-600">
                {filteredProtocols.filter(p => {
                  const stats = getTranslationCompletionStats(translationStatuses[p.id]);
                  return stats.percentage > 0 && stats.percentage < 100;
                }).length}
              </p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <div className="w-8 h-8 bg-gray-100 rounded-full flex items-center justify-center">
                <span className="text-gray-600 font-semibold">⏳</span>
              </div>
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">{t('translations.untranslated')}</p>
              <p className="text-2xl font-bold text-gray-600">
                {filteredProtocols.filter(p => {
                  const stats = getTranslationCompletionStats(translationStatuses[p.id]);
                  return stats.percentage === 0;
                }).length}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Filters and Search */}
      <div className="bg-white rounded-lg shadow p-6 mb-6">
        <div className="flex flex-col sm:flex-row gap-4">
          <div className="flex-1">
            <input
              type="text"
              placeholder={t('common.search')}
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <div className="sm:w-48">
            <select
              value={filterType}
              onChange={(e) => setFilterType(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="all">{t('translations.allProtocols')}</option>
              <option value="completed">{t('translations.fullyTranslated')}</option>
              <option value="partial">{t('translations.partiallyTranslated')}</option>
              <option value="untranslated">{t('translations.untranslated')}</option>
            </select>
          </div>
        </div>
      </div>

      {/* Protocols List */}
      {loading ? (
        <div className="text-center py-12">
          <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          <p className="mt-2 text-gray-600">{t('common.loading')}</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {filteredProtocols.map((protocol) => {
            const status = translationStatuses[protocol.id];
            const stats = getTranslationCompletionStats(status);
            const statusColor = getStatusColor(stats.percentage);

            return (
              <div key={protocol.id} className="bg-white rounded-lg shadow hover:shadow-md transition-shadow">
                <div className="p-6">
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex-1">
                      <h3 className="text-lg font-medium text-gray-900 mb-2">{protocol.name}</h3>
                      <p className="text-sm text-gray-600 mb-3 line-clamp-2">
                        {protocol.description || t('common.noDescription')}
                      </p>
                      <div className="flex items-center space-x-3">
                        <span className="px-3 py-1 rounded-full text-sm font-medium bg-blue-100 text-blue-800">
                          {t(`maintenanceProtocols.types.${protocol.protocol_type}`)}
                        </span>
                        <span className="text-sm text-gray-500">
                          {protocol.checklist_items?.length || 0} {t('translations.checklistItems')}
                        </span>
                      </div>
                    </div>
                    <div className="ml-4 text-right">
                      <span className={`px-3 py-1 rounded-full text-sm font-medium ${statusColor}`}>
                        {stats.percentage}%
                      </span>
                    </div>
                  </div>

                  {/* Translation Progress */}
                  <div className="mb-4">
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-sm font-medium text-gray-700">
                        {t('translations.translationProgress')}
                      </span>
                      <span className="text-sm text-gray-600">
                        {stats.completed}/{stats.total} {t('translations.languages')}
                      </span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div 
                        className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                        style={{ width: `${stats.percentage}%` }}
                      ></div>
                    </div>
                  </div>

                  {/* Language Status */}
                  <div className="flex flex-wrap gap-2 mb-4">
                    {supportedLanguages.slice(0, 6).map(language => {
                      const langPercentage = status?.completion_percentage?.[language.code] || 0;
                      const isComplete = langPercentage >= 100;
                      
                      return (
                        <div
                          key={language.code}
                          className={`flex items-center space-x-1 px-2 py-1 rounded text-xs ${
                            isComplete 
                              ? 'bg-green-100 text-green-800' 
                              : langPercentage > 0 
                                ? 'bg-yellow-100 text-yellow-800'
                                : 'bg-gray-100 text-gray-600'
                          }`}
                          title={`${language.name}: ${langPercentage.toFixed(0)}%`}
                        >
                          <span>{language.flag}</span>
                          <span>{language.code.toUpperCase()}</span>
                          {isComplete && <span>✓</span>}
                        </div>
                      );
                    })}
                  </div>

                  {/* Actions */}
                  <div className="flex justify-end">
                    <button
                      onClick={() => handleProtocolSelect(protocol)}
                      className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 transition-colors"
                    >
                      {stats.percentage > 0 ? t('translations.manageTranslations') : t('translations.startTranslating')}
                    </button>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {filteredProtocols.length === 0 && !loading && (
        <div className="text-center py-12">
          <div className="text-gray-400 text-6xl mb-4">📋</div>
          <h3 className="text-lg font-medium text-gray-900 mb-2">
            {searchTerm || filterType !== 'all' 
              ? t('translations.noProtocolsFound') 
              : t('translations.noProtocolsYet')
            }
          </h3>
          <p className="text-gray-600">
            {searchTerm || filterType !== 'all'
              ? t('translations.tryDifferentSearch')
              : t('translations.createProtocolsFirst')
            }
          </p>
        </div>
      )}
    </div>
  );
};

export default ProtocolTranslations;