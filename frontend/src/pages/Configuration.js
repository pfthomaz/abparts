// frontend/src/pages/Configuration.js

import React, { useState, useEffect } from 'react';
import { useAuth } from '../AuthContext';
import { api } from '../services/api';
import { useTranslation } from '../hooks/useTranslation';
import Modal from '../components/Modal';
import ConfigurationCategoryPanel from '../components/ConfigurationCategoryPanel';
import ConfigurationTemplateSelector from '../components/ConfigurationTemplateSelector';
import ConfigurationImportExport from '../components/ConfigurationImportExport';

const Configuration = () => {
  const { user, token } = useAuth();
  const { t } = useTranslation();
  const [configurations, setConfigurations] = useState([]);
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState('organization');
  const [showTemplateModal, setShowTemplateModal] = useState(false);
  const [showImportExportModal, setShowImportExportModal] = useState(false);

  // Check if user has admin privileges
  const isAdmin = user?.role === 'admin' || user?.role === 'super_admin';
  const isSuperAdmin = user?.role === 'super_admin';

  useEffect(() => {
    if (!isAdmin) {
      setError(t('configuration.noPermission'));
      setLoading(false);
      return;
    }

    fetchConfigurations();
  }, [isAdmin, token]);

  const fetchConfigurations = async () => {
    try {
      setLoading(true);
      setError(null);

      // Fetch configurations by category
      const categoriesData = await api.get('/configuration/system/categories');
      setCategories(categoriesData);

      // Extract all configurations
      const allConfigs = categoriesData.flatMap(category => category.configurations);
      setConfigurations(allConfigs);

    } catch (error) {
      console.error('Error fetching configurations:', error);
      setError(t('configuration.failedToLoad'));
    } finally {
      setLoading(false);
    }
  };

  const handleConfigurationUpdate = async (configId, newValue) => {
    try {
      await api.put(`/configuration/system/${configId}`, { value: newValue });

      // Refresh configurations
      await fetchConfigurations();
      return { success: true };

    } catch (error) {
      console.error('Error updating configuration:', error);
      return { success: false, error: error.message };
    }
  };

  const handleInitializeDefaults = async () => {
    if (!isSuperAdmin) {
      setError(t('configuration.onlySuperadmin'));
      return;
    }

    try {
      const result = await api.post('/configuration/initialize-defaults');
      alert(`Default configurations initialized: ${result.created_count} created, ${result.skipped_count} skipped`);

      // Refresh configurations
      await fetchConfigurations();

    } catch (error) {
      console.error('Error initializing defaults:', error);
      setError(error.message);
    }
  };

  const getCategoryConfigurations = (categoryName) => {
    const category = categories.find(cat => cat.category === categoryName);
    return category ? category.configurations : [];
  };

  const tabs = [
    { id: 'organization', label: t('configuration.tabs.organization'), icon: '🏢' },
    { id: 'parts', label: t('configuration.tabs.parts'), icon: '🔧' },
    { id: 'user_management', label: t('configuration.tabs.userManagement'), icon: '👥' },
    { id: 'localization', label: t('configuration.tabs.localization'), icon: '🌍' },
    ...(isSuperAdmin ? [{ id: 'system', label: t('configuration.tabs.system'), icon: '⚙️' }] : [])
  ];

  if (!isAdmin) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="bg-white p-8 rounded-lg shadow-md max-w-md w-full text-center">
          <div className="text-red-500 text-6xl mb-4">🚫</div>
          <h2 className="text-2xl font-bold text-gray-900 mb-2">{t('configuration.accessDenied')}</h2>
          <p className="text-gray-600">{t('configuration.noPermission')}</p>
        </div>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">{t('configuration.loading')}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">{t('configuration.title')}</h1>
              <p className="text-gray-600 mt-2">
                {t('configuration.subtitle')}
              </p>
            </div>

            {isSuperAdmin && (
              <div className="flex space-x-3">
                <button
                  onClick={() => setShowTemplateModal(true)}
                  className="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 transition-colors"
                >
                  📋 {t('configuration.templates')}
                </button>
                <button
                  onClick={() => setShowImportExportModal(true)}
                  className="bg-purple-600 text-white px-4 py-2 rounded-lg hover:bg-purple-700 transition-colors"
                >
                  📤 {t('configuration.importExport')}
                </button>
                <button
                  onClick={handleInitializeDefaults}
                  className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors"
                >
                  🔄 {t('configuration.initializeDefaults')}
                </button>
              </div>
            )}
          </div>
        </div>

        {/* Error Display */}
        {error && (
          <div className="mb-6 bg-red-50 border border-red-200 rounded-lg p-4">
            <div className="flex">
              <div className="text-red-400 text-xl mr-3">⚠️</div>
              <div>
                <h3 className="text-red-800 font-medium">{t('configuration.error')}</h3>
                <p className="text-red-700 mt-1">{error}</p>
              </div>
            </div>
          </div>
        )}

        {/* Tab Navigation */}
        <div className="mb-6">
          <div className="border-b border-gray-200">
            <nav className="-mb-px flex space-x-8">
              {tabs.map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`py-2 px-1 border-b-2 font-medium text-sm whitespace-nowrap ${activeTab === tab.id
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                    }`}
                >
                  <span className="mr-2">{tab.icon}</span>
                  {tab.label}
                </button>
              ))}
            </nav>
          </div>
        </div>

        {/* Configuration Panels */}
        <div className="bg-white rounded-lg shadow">
          <ConfigurationCategoryPanel
            category={activeTab}
            configurations={getCategoryConfigurations(activeTab)}
            onUpdate={handleConfigurationUpdate}
            isSuperAdmin={isSuperAdmin}
          />
        </div>

        {/* Template Modal */}
        {showTemplateModal && (
          <Modal
            isOpen={showTemplateModal}
            onClose={() => setShowTemplateModal(false)}
            title={t('configuration.modal.templates')}
            size="large"
          >
            <ConfigurationTemplateSelector
              onClose={() => setShowTemplateModal(false)}
              onApplyTemplate={fetchConfigurations}
            />
          </Modal>
        )}

        {/* Import/Export Modal */}
        {showImportExportModal && (
          <Modal
            isOpen={showImportExportModal}
            onClose={() => setShowImportExportModal(false)}
            title={t('configuration.modal.importExport')}
            size="large"
          >
            <ConfigurationImportExport
              configurations={configurations}
              onClose={() => setShowImportExportModal(false)}
              onImportComplete={fetchConfigurations}
            />
          </Modal>
        )}
      </div>
    </div>
  );
};

export default Configuration;