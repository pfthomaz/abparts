// frontend/src/pages/MaintenanceProtocols.js

import React, { useState, useEffect } from 'react';
import { listProtocols, deleteProtocol } from '../services/maintenanceProtocolsService';
import ProtocolForm from '../components/ProtocolForm';
import ChecklistItemManager from '../components/ChecklistItemManager';
import { useTranslation } from '../hooks/useTranslation';

const MaintenanceProtocols = () => {
  const { t } = useTranslation();
  const [protocols, setProtocols] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showProtocolForm, setShowProtocolForm] = useState(false);
  const [editingProtocol, setEditingProtocol] = useState(null);
  const [selectedProtocol, setSelectedProtocol] = useState(null);
  const [filters, setFilters] = useState({
    protocol_type: '',
    machine_model: '',
    is_active: true,
    search: ''
  });

  useEffect(() => {
    loadProtocols();
  }, [filters]);

  const loadProtocols = async () => {
    try {
      setLoading(true);
      const data = await listProtocols(filters);
      setProtocols(data);
      setError(null);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateProtocol = () => {
    setEditingProtocol(null);
    setShowProtocolForm(true);
  };

  const handleEditProtocol = (protocol) => {
    setEditingProtocol(protocol);
    setShowProtocolForm(true);
  };

  const handleDeleteProtocol = async (protocolId) => {
    if (!window.confirm(t('maintenance.protocols.confirmDelete'))) {
      return;
    }

    try {
      await deleteProtocol(protocolId);
      loadProtocols();
    } catch (err) {
      alert(t('maintenance.protocols.deleteFailed') + `: ${err.message}`);
    }
  };

  const handleProtocolSaved = () => {
    setShowProtocolForm(false);
    setEditingProtocol(null);
    loadProtocols();
  };

  const handleManageChecklist = (protocol) => {
    setSelectedProtocol(protocol);
  };

  const getProtocolTypeLabel = (type) => {
    return t(`maintenanceProtocols.types.${type}`) || type;
  };

  const getProtocolTypeBadge = (type) => {
    const colors = {
      daily: 'bg-blue-100 text-blue-800',
      weekly: 'bg-green-100 text-green-800',
      scheduled: 'bg-purple-100 text-purple-800',
      custom: 'bg-gray-100 text-gray-800'
    };
    return colors[type] || colors.custom;
  };

  if (showProtocolForm) {
    return (
      <div className="p-6">
        <ProtocolForm
          protocol={editingProtocol}
          onSave={handleProtocolSaved}
          onCancel={() => {
            setShowProtocolForm(false);
            setEditingProtocol(null);
          }}
        />
      </div>
    );
  }

  if (selectedProtocol) {
    return (
      <div className="p-6">
        <ChecklistItemManager
          protocol={selectedProtocol}
          onBack={() => setSelectedProtocol(null)}
          onUpdate={loadProtocols}
        />
      </div>
    );
  }

  return (
    <div className="p-6">
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900">{t('maintenanceProtocols.title')}</h1>
        <p className="mt-2 text-gray-600">
          {t('maintenanceProtocols.subtitle')}
        </p>
      </div>

      {/* Filters */}
      <div className="bg-white p-4 rounded-lg shadow mb-6">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              {t('maintenanceProtocols.filters.protocolType')}
            </label>
            <select
              value={filters.protocol_type}
              onChange={(e) => setFilters({ ...filters, protocol_type: e.target.value })}
              className="w-full border border-gray-300 rounded-md px-3 py-2"
            >
              <option value="">{t('maintenanceProtocols.filters.allTypes')}</option>
              <option value="daily">{t('maintenanceProtocols.types.daily')}</option>
              <option value="weekly">{t('maintenanceProtocols.types.weekly')}</option>
              <option value="scheduled">{t('maintenanceProtocols.types.scheduled')}</option>
              <option value="custom">{t('maintenanceProtocols.types.custom')}</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              {t('maintenanceProtocols.filters.machineModel')}
            </label>
            <select
              value={filters.machine_model}
              onChange={(e) => setFilters({ ...filters, machine_model: e.target.value })}
              className="w-full border border-gray-300 rounded-md px-3 py-2"
            >
              <option value="">{t('maintenanceProtocols.filters.allModels')}</option>
              <option value="all">{t('maintenanceProtocols.filters.universal')}</option>
              <option value="V3.1B">V3.1B</option>
              <option value="V4.0">V4.0</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              {t('maintenanceProtocols.filters.status')}
            </label>
            <select
              value={filters.is_active}
              onChange={(e) => setFilters({ ...filters, is_active: e.target.value === 'true' })}
              className="w-full border border-gray-300 rounded-md px-3 py-2"
            >
              <option value="true">{t('maintenanceProtocols.filters.activeOnly')}</option>
              <option value="">{t('maintenanceProtocols.filters.all')}</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              {t('maintenanceProtocols.filters.search')}
            </label>
            <input
              type="text"
              value={filters.search}
              onChange={(e) => setFilters({ ...filters, search: e.target.value })}
              placeholder={t('maintenanceProtocols.filters.searchPlaceholder')}
              className="w-full border border-gray-300 rounded-md px-3 py-2"
            />
          </div>
        </div>
      </div>

      {/* Create Button */}
      <div className="mb-6">
        <button
          onClick={handleCreateProtocol}
          className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700"
        >
          + {t('maintenanceProtocols.createNew')}
        </button>
      </div>

      {/* Error Message */}
      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded mb-6">
          {error}
        </div>
      )}

      {/* Loading State */}
      {loading && (
        <div className="text-center py-12">
          <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          <p className="mt-2 text-gray-600">{t('maintenanceProtocols.loading')}</p>
        </div>
      )}

      {/* Protocols List */}
      {!loading && protocols.length === 0 && (
        <div className="text-center py-12 bg-white rounded-lg shadow">
          <p className="text-gray-500">{t('maintenanceProtocols.noProtocols')}</p>
        </div>
      )}

      {!loading && protocols.length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {protocols.map((protocol) => (
            <div key={protocol.id} className="bg-white rounded-lg shadow hover:shadow-lg transition-shadow">
              <div className="p-6">
                <div className="flex items-start justify-between mb-4">
                  <div className="flex-1">
                    <h3 className="text-lg font-semibold text-gray-900 mb-2">
                      {protocol.name}
                    </h3>
                    <div className="flex items-center gap-2 mb-2">
                      <span className={`px-2 py-1 rounded text-xs font-medium ${getProtocolTypeBadge(protocol.protocol_type)}`}>
                        {getProtocolTypeLabel(protocol.protocol_type)}
                      </span>
                      {protocol.machine_model && (
                        <span className="px-2 py-1 rounded text-xs font-medium bg-gray-100 text-gray-700">
                          {protocol.machine_model}
                        </span>
                      )}
                      {!protocol.is_active && (
                        <span className="px-2 py-1 rounded text-xs font-medium bg-red-100 text-red-700">
                          {t('maintenanceProtocols.card.inactive')}
                        </span>
                      )}
                    </div>
                  </div>
                </div>

                {protocol.description && (
                  <p className="text-sm text-gray-600 mb-4 line-clamp-2">
                    {protocol.description}
                  </p>
                )}

                {protocol.service_interval_hours && (
                  <p className="text-sm text-gray-700 mb-4">
                    <span className="font-medium">{t('maintenanceProtocols.card.serviceInterval')}:</span> {protocol.service_interval_hours}{t('maintenanceProtocols.card.hours')}
                  </p>
                )}

                <div className="text-sm text-gray-600 mb-4">
                  <span className="font-medium">{protocol.checklist_items?.length || 0}</span> {t('maintenanceProtocols.card.checklistItems')}
                </div>

                <div className="flex gap-2">
                  <button
                    onClick={() => handleManageChecklist(protocol)}
                    className="flex-1 bg-blue-50 text-blue-700 px-3 py-2 rounded text-sm hover:bg-blue-100"
                  >
                    {t('maintenanceProtocols.card.manageChecklist')}
                  </button>
                  <button
                    onClick={() => handleEditProtocol(protocol)}
                    className="bg-gray-50 text-gray-700 px-3 py-2 rounded text-sm hover:bg-gray-100"
                  >
                    {t('maintenanceProtocols.card.edit')}
                  </button>
                  <button
                    onClick={() => handleDeleteProtocol(protocol.id)}
                    className="bg-red-50 text-red-700 px-3 py-2 rounded text-sm hover:bg-red-100"
                  >
                    {t('maintenanceProtocols.card.delete')}
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default MaintenanceProtocols;
