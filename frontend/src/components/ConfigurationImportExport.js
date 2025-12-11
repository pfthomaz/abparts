// frontend/src/components/ConfigurationImportExport.js

import React, { useState } from 'react';
import { useAuth } from '../AuthContext';
import { api } from '../services/api';

const ConfigurationImportExport = ({ configurations, onClose, onImportComplete }) => {
  const { token } = useAuth();
  const [activeTab, setActiveTab] = useState('export');
  const [exportData, setExportData] = useState(null);
  const [importData, setImportData] = useState('');
  const [importFile, setImportFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);

  const handleExport = async () => {
    try {
      setLoading(true);
      setError(null);

      const exportResult = await api.get('/configuration/export');
      setExportData(exportResult);
      setSuccess('Configuration data exported successfully!');

    } catch (error) {
      console.error('Error exporting configurations:', error);
      setError('Failed to export configuration data. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleDownloadExport = () => {
    if (!exportData) return;

    const dataStr = JSON.stringify(exportData, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(dataBlob);

    const link = document.createElement('a');
    link.href = url;
    link.download = `abparts-configuration-${new Date().toISOString().split('T')[0]}.json`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);

    URL.revokeObjectURL(url);
  };

  const handleFileUpload = (event) => {
    const file = event.target.files[0];
    if (!file) return;

    setImportFile(file);

    const reader = new FileReader();
    reader.onload = (e) => {
      try {
        const content = e.target.result;
        JSON.parse(content); // Validate JSON
        setImportData(content);
        setError(null);
      } catch (error) {
        setError('Invalid JSON file. Please check the file format.');
        setImportData('');
      }
    };
    reader.readAsText(file);
  };

  const handleImport = async () => {
    if (!importData) {
      setError('Please provide configuration data to import.');
      return;
    }

    try {
      setLoading(true);
      setError(null);

      let configData;
      try {
        configData = JSON.parse(importData);
      } catch (error) {
        throw new Error('Invalid JSON format. Please check your data.');
      }

      const result = await api.post('/configuration/import', {
        configurations: configData.configurations || configData,
        overwrite_existing: true
      });

      if (result.success) {
        setSuccess(`Import completed! ${result.imported_count} configurations imported, ${result.skipped_count} skipped.`);
        onImportComplete();
      } else {
        throw new Error(`Import failed: ${result.failed_imports.length} errors`);
      }

    } catch (error) {
      console.error('Error importing configurations:', error);
      setError(error.message);
    } finally {
      setLoading(false);
    }
  };

  const clearMessages = () => {
    setError(null);
    setSuccess(null);
  };

  return (
    <div className="max-w-4xl mx-auto">
      <div className="mb-6">
        <h3 className="text-xl font-bold text-gray-900 mb-2">Import/Export Configurations</h3>
        <p className="text-gray-600">
          Export current configurations or import configurations from a file.
        </p>
      </div>

      {/* Tab Navigation */}
      <div className="mb-6">
        <div className="border-b border-gray-200">
          <nav className="-mb-px flex space-x-8">
            <button
              onClick={() => { setActiveTab('export'); clearMessages(); }}
              className={`py-2 px-1 border-b-2 font-medium text-sm ${activeTab === 'export'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
            >
              📤 Export
            </button>
            <button
              onClick={() => { setActiveTab('import'); clearMessages(); }}
              className={`py-2 px-1 border-b-2 font-medium text-sm ${activeTab === 'import'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
            >
              📥 Import
            </button>
          </nav>
        </div>
      </div>

      {/* Messages */}
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

      {success && (
        <div className="mb-6 bg-green-50 border border-green-200 rounded-lg p-4">
          <div className="flex">
            <div className="text-green-400 text-xl mr-3">✅</div>
            <div>
              <h3 className="text-green-800 font-medium">Success</h3>
              <p className="text-green-700 mt-1">{success}</p>
            </div>
          </div>
        </div>
      )}

      {/* Export Tab */}
      {activeTab === 'export' && (
        <div className="space-y-6">
          <div className="bg-white border border-gray-200 rounded-lg p-6">
            <h4 className="text-lg font-medium text-gray-900 mb-4">Export Configuration Data</h4>
            <p className="text-gray-600 mb-4">
              Export all current system configurations to a JSON file that can be imported later or used as a backup.
            </p>

            <div className="flex space-x-3">
              <button
                onClick={handleExport}
                disabled={loading}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {loading ? '⏳ Exporting...' : '📤 Export Configurations'}
              </button>

              {exportData && (
                <button
                  onClick={handleDownloadExport}
                  className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
                >
                  💾 Download JSON File
                </button>
              )}
            </div>

            {exportData && (
              <div className="mt-6">
                <h5 className="text-md font-medium text-gray-900 mb-2">Export Summary</h5>
                <div className="bg-gray-50 rounded-lg p-4">
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div>
                      <span className="text-gray-600">Total Configurations:</span>
                      <span className="ml-2 font-medium">{exportData.total_count}</span>
                    </div>
                    <div>
                      <span className="text-gray-600">Export Date:</span>
                      <span className="ml-2 font-medium">
                        {new Date(exportData.export_timestamp).toLocaleString()}
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Import Tab */}
      {activeTab === 'import' && (
        <div className="space-y-6">
          <div className="bg-white border border-gray-200 rounded-lg p-6">
            <h4 className="text-lg font-medium text-gray-900 mb-4">Import Configuration Data</h4>
            <p className="text-gray-600 mb-4">
              Import configurations from a JSON file. This will overwrite existing configurations with the same keys.
            </p>

            {/* File Upload */}
            <div className="mb-6">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Upload Configuration File
              </label>
              <input
                type="file"
                accept=".json"
                onChange={handleFileUpload}
                className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-medium file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
              />
              {importFile && (
                <p className="text-sm text-gray-600 mt-2">
                  Selected file: {importFile.name} ({(importFile.size / 1024).toFixed(1)} KB)
                </p>
              )}
            </div>

            {/* Manual Input */}
            <div className="mb-6">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Or Paste Configuration JSON
              </label>
              <textarea
                value={importData}
                onChange={(e) => setImportData(e.target.value)}
                placeholder="Paste your configuration JSON here..."
                rows={10}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent font-mono text-sm"
              />
            </div>

            {/* Import Actions */}
            <div className="flex space-x-3">
              <button
                onClick={handleImport}
                disabled={loading || !importData}
                className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {loading ? '⏳ Importing...' : '📥 Import Configurations'}
              </button>

              <button
                onClick={() => {
                  setImportData('');
                  setImportFile(null);
                  clearMessages();
                }}
                className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50"
              >
                🗑️ Clear
              </button>
            </div>

            {/* Import Warning */}
            <div className="mt-6 bg-yellow-50 border border-yellow-200 rounded-lg p-4">
              <div className="flex">
                <div className="text-yellow-400 text-xl mr-3">⚠️</div>
                <div>
                  <h3 className="text-yellow-800 font-medium">Important</h3>
                  <p className="text-yellow-700 mt-1 text-sm">
                    Importing configurations will overwrite existing settings with the same keys.
                    Make sure to export your current configurations as a backup before importing.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

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

export default ConfigurationImportExport;