// frontend/src/components/ConfigurationCategoryPanel.js

import React, { useState } from 'react';
import ConfigurationItem from './ConfigurationItem';

const ConfigurationCategoryPanel = ({ category, configurations, onUpdate, isSuperAdmin }) => {
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
        title: 'Organization Management Settings',
        description: 'Configure default settings for organization creation and management',
        icon: '🏢',
        color: 'blue'
      },
      parts: {
        title: 'Parts Management Settings',
        description: 'Configure settings for parts catalog and inventory management',
        icon: '🔧',
        color: 'green'
      },
      user_management: {
        title: 'User Management Settings',
        description: 'Configure user authentication, authorization, and security settings',
        icon: '👥',
        color: 'purple'
      },
      localization: {
        title: 'Localization Settings',
        description: 'Configure language, country, and regional preferences',
        icon: '🌍',
        color: 'yellow'
      },
      system: {
        title: 'System Settings',
        description: 'Advanced system configuration options (superadmin only)',
        icon: '⚙️',
        color: 'red'
      }
    };

    return categoryInfo[categoryName] || {
      title: 'Configuration Settings',
      description: 'System configuration options',
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
              placeholder="Search configurations..."
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
              <span className="ml-2 text-sm text-gray-700">Show system-managed</span>
            </label>
          </div>
        )}
      </div>

      {/* Configuration Count */}
      <div className="mb-4">
        <p className="text-sm text-gray-600">
          Showing {filteredConfigurations.length} of {configurations.length} configurations
        </p>
      </div>

      {/* Configurations List */}
      {filteredConfigurations.length === 0 ? (
        <div className="text-center py-12">
          <div className="text-gray-400 text-6xl mb-4">📋</div>
          <h3 className="text-lg font-medium text-gray-900 mb-2">No configurations found</h3>
          <p className="text-gray-600">
            {searchTerm ? 'Try adjusting your search terms.' : 'No configurations available for this category.'}
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
          Configuration Tips
        </h3>
        <div className="text-sm text-gray-700 space-y-2">
          {category === 'organization' && (
            <>
              <p>• Default country setting affects new organization creation</p>
              <p>• Auto-create warehouse setting determines if warehouses are created automatically</p>
              <p>• Supplier limits help manage organizational complexity</p>
            </>
          )}
          {category === 'parts' && (
            <>
              <p>• Photo limits affect storage requirements and upload performance</p>
              <p>• Supported formats should balance quality and compatibility</p>
              <p>• Inventory thresholds help with stock management</p>
            </>
          )}
          {category === 'user_management' && (
            <>
              <p>• Password requirements affect security and user experience</p>
              <p>• Session timeout balances security with usability</p>
              <p>• Failed login limits help prevent brute force attacks</p>
            </>
          )}
          {category === 'localization' && (
            <>
              <p>• Language settings affect the user interface display</p>
              <p>• Country settings determine date/number formats</p>
              <p>• RTL support is important for Arabic regions</p>
            </>
          )}
          {category === 'system' && (
            <>
              <p>• System settings may require application restart</p>
              <p>• Changes to system-managed settings should be made carefully</p>
              <p>• Always test configuration changes in a development environment first</p>
            </>
          )}
        </div>
      </div>
    </div>
  );
};

export default ConfigurationCategoryPanel;