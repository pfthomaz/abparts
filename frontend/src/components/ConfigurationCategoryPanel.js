// frontend/src/components/ConfigurationCategoryPanel.js

import React, { useState } from 'react';
import { useTranslation } from '../hooks/useTranslation';
import ConfigurationItem from './ConfigurationItem';

const ConfigurationCategoryPanel = ({ category, configurations, onUpdate, isSuperAdmin }) => {
  const { t } = useTranslation();
  const [searchTerm, setSearchTerm] = useState('');
  const [showSystemManaged, setShowSystemManaged] = useState(false);

  // Filter configurations based on search term and system managed setting
  const filteredConfigurations = configurations.filter(config => {
    const matchesSearch = config.key.toLowerCase().includes(searchTerm.toLowerCase()) ||
      (config.description && config.description.toLowerCase().includes(searchTerm.toLowerCase()));

    const matchesSystemManaged = showSystemManaged || !config.is_system_managed;

    return matchesSearch && matchesSystemManaged;
  });

  const getCategoryInfo = (categoryName) => {
    const categoryInfo = {
      organization: {
        title: t('configuration.category.organization.title'),
        description: t('configuration.category.organization.description'),
        icon: '🏢',
        color: 'blue'
      },
      parts: {
        title: t('configuration.category.parts.title'),
        description: t('configuration.category.parts.description'),
        icon: '🔧',
        color: 'green'
      },
      user_management: {
        title: t('configuration.category.userManagement.title'),
        description: t('configuration.category.userManagement.description'),
        icon: '👥',
        color: 'purple'
      },
      localization: {
        title: t('configuration.category.localization.title'),
        description: t('configuration.category.localization.description'),
        icon: '🌍',
        color: 'yellow'
      },
      system: {
        title: t('configuration.category.system.title'),
        description: t('configuration.category.system.description'),
        icon: '⚙️',
        color: 'red'
      }
    };

    return categoryInfo[categoryName] || {
      title: t('configuration.category.default.title'),
      description: t('configuration.category.default.description'),
      icon: '⚙️',
      color: 'gray'
    };
  };

  const categoryInfo = getCategoryInfo(category);

  return (
    <div className="p-6">
      {/* Category Header */}
      <div className="mb-6">
        <div className="flex items-center mb-2">
          <span className="text-3xl mr-3">{categoryInfo.icon}</span>
          <div>
            <h2 className="text-2xl font-bold text-gray-900">{categoryInfo.title}</h2>
            <p className="text-gray-600">{categoryInfo.description}</p>
          </div>
        </div>
      </div>

      {/* Search and Filters */}
      <div className="mb-6 flex flex-col sm:flex-row gap-4">
        <div className="flex-1">
          <div className="relative">
            <input
              type="text"
              placeholder={t('configuration.search.placeholder')}
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <span className="text-gray-400">🔍</span>
            </div>
          </div>
        </div>

        {isSuperAdmin && (
          <div className="flex items-center">
            <label className="flex items-center">
              <input
                type="checkbox"
                checked={showSystemManaged}
                onChange={(e) => setShowSystemManaged(e.target.checked)}
                className="rounded border-gray-300 text-blue-600 shadow-sm focus:border-blue-300 focus:ring focus:ring-blue-200 focus:ring-opacity-50"
              />
              <span className="ml-2 text-sm text-gray-700">{t('configuration.showSystemManaged')}</span>
            </label>
          </div>
        )}
      </div>

      {/* Configuration Count */}
      <div className="mb-4">
        <p className="text-sm text-gray-600">
          {t('configuration.showingCount', { 
            count: filteredConfigurations.length, 
            total: configurations.length 
          })}
        </p>
      </div>

      {/* Configurations List */}
      {filteredConfigurations.length === 0 ? (
        <div className="text-center py-12">
          <div className="text-gray-400 text-6xl mb-4">📋</div>
          <h3 className="text-lg font-medium text-gray-900 mb-2">{t('configuration.noConfigurations.title')}</h3>
          <p className="text-gray-600">
            {searchTerm ? t('configuration.noConfigurations.searchMessage') : t('configuration.noConfigurations.emptyMessage')}
          </p>
        </div>
      ) : (
        <div className="space-y-4">
          {filteredConfigurations.map((config) => (
            <ConfigurationItem
              key={config.id}
              configuration={config}
              onUpdate={onUpdate}
              isSuperAdmin={isSuperAdmin}
            />
          ))}
        </div>
      )}

      {/* Category-specific Help */}
      <div className="mt-8 bg-gray-50 rounded-lg p-4">
        <h3 className="text-lg font-medium text-gray-900 mb-2">
          <span className="mr-2">💡</span>
          {t('configuration.tips.title')}
        </h3>
        <div className="text-sm text-gray-700 space-y-2">
          {category === 'organization' && (
            <>
              <p>• {t('configuration.tips.organization.1')}</p>
              <p>• {t('configuration.tips.organization.2')}</p>
              <p>• {t('configuration.tips.organization.3')}</p>
            </>
          )}
          {category === 'parts' && (
            <>
              <p>• {t('configuration.tips.parts.1')}</p>
              <p>• {t('configuration.tips.parts.2')}</p>
              <p>• {t('configuration.tips.parts.3')}</p>
            </>
          )}
          {category === 'user_management' && (
            <>
              <p>• {t('configuration.tips.userManagement.1')}</p>
              <p>• {t('configuration.tips.userManagement.2')}</p>
              <p>• {t('configuration.tips.userManagement.3')}</p>
            </>
          )}
          {category === 'localization' && (
            <>
              <p>• {t('configuration.tips.localization.1')}</p>
              <p>• {t('configuration.tips.localization.2')}</p>
              <p>• {t('configuration.tips.localization.3')}</p>
            </>
          )}
          {category === 'system' && (
            <>
              <p>• {t('configuration.tips.system.1')}</p>
              <p>• {t('configuration.tips.system.2')}</p>
              <p>• {t('configuration.tips.system.3')}</p>
            </>
          )}
        </div>
      </div>
    </div>
  );
};

export default ConfigurationCategoryPanel;