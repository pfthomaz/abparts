// frontend/src/pages/MaintenanceProtocols.js

import React, { useState, useEffect } from 'react';
import { listProtocols, deleteProtocol } from '../services/maintenanceProtocolsService';
import ProtocolForm from '../components/ProtocolForm';
import ChecklistItemManager from '../components/ChecklistItemManager';

const MaintenanceProtocols = () => {
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
    if (!window.confirm('Are you sure you want to delete this protocol?')) {
      return;
    }

    try {
      await deleteProtocol(protocolId);
      loadProtocols();
    } catch (err) {
      alert(`Failed to delete protocol: ${err.message}`);
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
    const labels = {
      daily: 'Daily',
      weekly: 'Weekly',
      scheduled: 'Scheduled',
      custom: 'Custom'
    };
    return labels[type] || type;
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
        <h1 className="text-3xl font-bold text-gray-900">Maintenance Protocols</h1>
        <p className="mt-2 text-gray-600">
          Manage maintenance protocol templates for machines
        </p>
      </div>

      {/* Filters */}
      <div className="bg-white p-4 rounded-lg shadow mb-6">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Protocol Type
            </label>
            <select
              value={filters.protocol_type}
              onChange={(e) => setFilters({ ...filters, protocol_type: e.target.value })}
              className="w-full border border-gray-300 rounded-md px-3 py-2"
            >
              <option value="">All Types</option>
              <option value="daily">Daily</option>
              <option value="weekly">Weekly</option>
              <option value="scheduled">Scheduled</option>
              <option value="custom">Custom</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Machine Model
            </label>
            <select
              value={filters.machine_model}
              onChange={(e) => setFilters({ ...filters, machine_model: e.target.value })}
              className="w-full border border-gray-300 rounded-md px-3 py-2"
            >
              <option value="">All Models</option>
              <option value="all">Universal (All Models)</option>
              <option value="V3.1B">V3.1B</option>
              <option value="V4.0">V4.0</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Status
            </label>
            <select
              value={filters.is_active}
              onChange={(e) => setFilters({ ...filters, is_active: e.target.value === 'true' })}
              className="w-full border border-gray-300 rounded-md px-3 py-2"
            >
              <option value="true">Active Only</option>
              <option value="">All</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Search
            </label>
            <input
              type="text"
              value={filters.search}
              onChange={(e) => setFilters({ ...filters, search: e.target.value })}
              placeholder="Search protocols..."
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
          + Create New Protocol
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
          <p className="mt-2 text-gray-600">Loading protocols...</p>
        </div>
      )}

      {/* Protocols List */}
      {!loading && protocols.length === 0 && (
        <div className="text-center py-12 bg-white rounded-lg shadow">
          <p className="text-gray-500">No protocols found. Create your first protocol to get started.</p>
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
                          Inactive
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
                    <span className="font-medium">Service Interval:</span> {protocol.service_interval_hours}h
                  </p>
                )}

                <div className="text-sm text-gray-600 mb-4">
                  <span className="font-medium">{protocol.checklist_items?.length || 0}</span> checklist items
                </div>

                <div className="flex gap-2">
                  <button
                    onClick={() => handleManageChecklist(protocol)}
                    className="flex-1 bg-blue-50 text-blue-700 px-3 py-2 rounded text-sm hover:bg-blue-100"
                  >
                    Manage Checklist
                  </button>
                  <button
                    onClick={() => handleEditProtocol(protocol)}
                    className="bg-gray-50 text-gray-700 px-3 py-2 rounded text-sm hover:bg-gray-100"
                  >
                    Edit
                  </button>
                  <button
                    onClick={() => handleDeleteProtocol(protocol.id)}
                    className="bg-red-50 text-red-700 px-3 py-2 rounded text-sm hover:bg-red-100"
                  >
                    Delete
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
