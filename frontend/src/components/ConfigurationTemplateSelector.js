// frontend/src/components/ConfigurationTemplateSelector.js

import React, { useState, useEffect } from 'react';
import { api } from '../services/api';

const ConfigurationTemplateSelector = ({ onClose, onApplyTemplate }) => {
  const [templates, setTemplates] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [applying, setApplying] = useState(false);

  useEffect(() => {
    fetchTemplates();
  }, []);

  const fetchTemplates = async () => {
    try {
      setLoading(true);
      setError(null);

      const templatesData = await api.get('/configuration/templates');
      setTemplates(templatesData);

    } catch (error) {
      console.error('Error fetching templates:', error);
      setError('Failed to load configuration templates. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleApplyTemplate = async (templateCategory, templateData) => {
    try {
      setApplying(true);
      setError(null);

      // Convert template data to configuration updates
      const configurations = Object.entries(templateData).map(([key, value]) => ({
        key: `${templateCategory}.${key}`,
        value: typeof value === 'object' ? JSON.stringify(value) : String(value)
      }));

      const result = await api.post('/configuration/bulk-update', {
        configurations: configurations
      });

      if (result.success) {
        alert(`Template applied successfully! ${result.updated_count} configurations updated.`);
        onApplyTemplate();
        onClose();
      } else {
        throw new Error(`Template application failed: ${result.failed_updates.length} errors`);
      }

    } catch (error) {
      console.error('Error applying template:', error);
      setError(error.message);
    } finally {
      setApplying(false);
    }
  };

  const renderTemplatePreview = (templateName, templateData) => {
    return (
      <div className="bg-gray-50 rounded-lg p-4 mb-4">
        <h4 className="font-medium text-gray-900 mb-3">{templateName} Template</h4>
        <div className="space-y-2 max-h-40 overflow-y-auto">
          {Object.entries(templateData).map(([key, value]) => (
            <div key={key} className="flex justify-between text-sm">
              <span className="text-gray-600">{key}:</span>
              <span className="font-mono text-gray-900">
                {typeof value === 'object' ? JSON.stringify(value) : String(value)}
              </span>
            </div>
          ))}
        </div>
        <button
          onClick={() => handleApplyTemplate(templateName.toLowerCase().replace(' ', '_'), templateData)}
          disabled={applying}
          className="mt-3 w-full px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {applying ? '⏳ Applying...' : '✅ Apply Template'}
        </button>
      </div>
    );
  };

  if (loading) {
    return (
      <div className="text-center py-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-4"></div>
        <p className="text-gray-600">Loading templates...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center py-8">
        <div className="text-red-500 text-4xl mb-4">⚠️</div>
        <h3 className="text-lg font-medium text-gray-900 mb-2">Error Loading Templates</h3>
        <p className="text-gray-600 mb-4">{error}</p>
        <button
          onClick={fetchTemplates}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
        >
          🔄 Retry
        </button>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto">
      <div className="mb-6">
        <h3 className="text-xl font-bold text-gray-900 mb-2">Configuration Templates</h3>
        <p className="text-gray-600">
          Apply predefined configuration templates to quickly set up common settings.
        </p>
      </div>

      {error && (
        <div className="mb-6 bg-red-50 border border-red-200 rounded-lg p-4">
          <div className="flex">
            <div className="text-red-400 text-xl mr-3">⚠️</div>
            <div>
              <h3 className="text-red-800 font-medium">Error</h3>
              <p className="text-red-700 mt-1">{error}</p>
            </div>
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Organization Management Template */}
        {templates?.organization_management && (
          <div className="border border-gray-200 rounded-lg p-6">
            <div className="flex items-center mb-4">
              <span className="text-2xl mr-3">🏢</span>
              <div>
                <h4 className="text-lg font-semibold text-gray-900">Organization Management</h4>
                <p className="text-sm text-gray-600">Default settings for organization creation and management</p>
              </div>
            </div>
            {renderTemplatePreview('Organization Management', templates.organization_management)}
          </div>
        )}

        {/* Parts Management Template */}
        {templates?.parts_management && (
          <div className="border border-gray-200 rounded-lg p-6">
            <div className="flex items-center mb-4">
              <span className="text-2xl mr-3">🔧</span>
              <div>
                <h4 className="text-lg font-semibold text-gray-900">Parts Management</h4>
                <p className="text-sm text-gray-600">Settings for parts catalog and inventory management</p>
              </div>
            </div>
            {renderTemplatePreview('Parts Management', templates.parts_management)}
          </div>
        )}

        {/* User Management Template */}
        {templates?.user_management && (
          <div className="border border-gray-200 rounded-lg p-6">
            <div className="flex items-center mb-4">
              <span className="text-2xl mr-3">👥</span>
              <div>
                <h4 className="text-lg font-semibold text-gray-900">User Management</h4>
                <p className="text-sm text-gray-600">User authentication and security settings</p>
              </div>
            </div>
            {renderTemplatePreview('User Management', templates.user_management)}
          </div>
        )}

        {/* Localization Template */}
        {templates?.localization && (
          <div className="border border-gray-200 rounded-lg p-6">
            <div className="flex items-center mb-4">
              <span className="text-2xl mr-3">🌍</span>
              <div>
                <h4 className="text-lg font-semibold text-gray-900">Localization</h4>
                <p className="text-sm text-gray-600">Language and regional preference settings</p>
              </div>
            </div>
            {renderTemplatePreview('Localization', templates.localization)}
          </div>
        )}
      </div>

      {/* Action Buttons */}
      <div className="mt-8 flex justify-end space-x-3">
        <button
          onClick={onClose}
          className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50"
        >
          Close
        </button>
      </div>
    </div>
  );
};

export default ConfigurationTemplateSelector;