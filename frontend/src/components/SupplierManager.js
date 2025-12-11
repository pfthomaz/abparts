// frontend/src/components/SupplierManager.js

import React, { useState, useEffect } from 'react';
import { useAuth } from '../AuthContext';
import { organizationsService, ORGANIZATION_TYPE_CONFIG } from '../services/organizationsService';
import { getCountryFlag, getCountryDisplay } from '../utils/countryFlags';
import Modal from './Modal';
import OrganizationForm from './OrganizationForm';

const SupplierManager = ({ organizationId, onSupplierChange }) => {
  const { user } = useAuth();
  const [suppliers, setSuppliers] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [editingSupplier, setEditingSupplier] = useState(null);
  const [includeInactive, setIncludeInactive] = useState(false);

  // Load suppliers for the organization
  const loadSuppliers = async () => {
    if (!organizationId) return;

    setLoading(true);
    setError(null);
    try {
      const response = await organizationsService.getOrganizations({
        organization_type: 'supplier',
        parent_organization_id: organizationId,
        include_inactive: includeInactive
      });
      setSuppliers(response.data || response);
    } catch (err) {
      console.error('Failed to load suppliers:', err);
      setError('Failed to load suppliers. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadSuppliers();
  }, [organizationId, includeInactive]);

  // Handle supplier creation
  const handleCreateSupplier = async (supplierData) => {
    try {
      // Force supplier type and parent organization
      const newSupplierData = {
        ...supplierData,
        organization_type: 'supplier',
        parent_organization_id: organizationId
      };

      await organizationsService.createOrganization(newSupplierData);
      setShowCreateModal(false);
      await loadSuppliers();
      if (onSupplierChange) onSupplierChange();
    } catch (err) {
      console.error('Failed to create supplier:', err);
      throw err; // Let the form handle the error display
    }
  };

  // Handle supplier update
  const handleUpdateSupplier = async (supplierData) => {
    try {
      await organizationsService.updateOrganization(editingSupplier.id, supplierData);
      setEditingSupplier(null);
      await loadSuppliers();
      if (onSupplierChange) onSupplierChange();
    } catch (err) {
      console.error('Failed to update supplier:', err);
      throw err; // Let the form handle the error display
    }
  };

  // Handle supplier activation/deactivation
  const handleToggleSupplierStatus = async (supplier) => {
    try {
      await organizationsService.updateOrganization(supplier.id, {
        is_active: !supplier.is_active
      });
      await loadSuppliers();
      if (onSupplierChange) onSupplierChange();
    } catch (err) {
      console.error('Failed to toggle supplier status:', err);
      setError('Failed to update supplier status. Please try again.');
    }
  };

  // Handle supplier deletion (deactivation)
  const handleDeleteSupplier = async (supplier) => {
    if (!window.confirm(`Are you sure you want to deactivate supplier "${supplier.name}"?`)) {
      return;
    }

    try {
      await organizationsService.updateOrganization(supplier.id, {
        is_active: false
      });
      await loadSuppliers();
      if (onSupplierChange) onSupplierChange();
    } catch (err) {
      console.error('Failed to deactivate supplier:', err);
      setError('Failed to deactivate supplier. Please try again.');
    }
  };

  if (!organizationId) {
    return (
      <div className="text-center py-8 text-gray-500">
        Select an organization to manage its suppliers
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h3 className="text-lg font-medium text-gray-900">Supplier Management</h3>
          <p className="text-sm text-gray-500">
            Manage suppliers for this organization
          </p>
        </div>
        <button
          onClick={() => setShowCreateModal(true)}
          className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
        >
          <svg className="-ml-1 mr-2 h-5 w-5" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
            <path fillRule="evenodd" d="M10 3a1 1 0 011 1v5h5a1 1 0 110 2h-5v5a1 1 0 11-2 0v-5H4a1 1 0 110-2h5V4a1 1 0 011-1z" clipRule="evenodd" />
          </svg>
          Add Supplier
        </button>
      </div>

      {/* Controls */}
      <div className="flex items-center space-x-4">
        <label className="flex items-center">
          <input
            type="checkbox"
            checked={includeInactive}
            onChange={(e) => setIncludeInactive(e.target.checked)}
            className="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded"
          />
          <span className="ml-2 text-sm text-gray-700">Include inactive suppliers</span>
        </label>
      </div>

      {/* Error Display */}
      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative">
          <span className="block sm:inline">{error}</span>
        </div>
      )}

      {/* Loading State */}
      {loading && (
        <div className="flex justify-center py-8">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
        </div>
      )}

      {/* Suppliers List */}
      {!loading && (
        <div className="bg-white shadow overflow-hidden sm:rounded-md">
          {suppliers.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              No suppliers found. Create your first supplier to get started.
            </div>
          ) : (
            <ul className="divide-y divide-gray-200">
              {suppliers.map((supplier) => (
                <li key={supplier.id} className="px-6 py-4">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                      <div className="flex-shrink-0">
                        <span className="text-2xl">
                          {ORGANIZATION_TYPE_CONFIG.supplier.icon}
                        </span>
                      </div>
                      <div className="min-w-0 flex-1">
                        <div className="flex items-center space-x-2">
                          <p className="text-sm font-medium text-gray-900 truncate">
                            {supplier.name}
                          </p>
                          {supplier.country && (
                            <span className="text-sm text-gray-500">
                              {getCountryFlag(supplier.country)}
                            </span>
                          )}
                          {!supplier.is_active && (
                            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800">
                              Inactive
                            </span>
                          )}
                        </div>
                        {supplier.address && (
                          <p className="text-sm text-gray-500 truncate">
                            {supplier.address}
                          </p>
                        )}
                        {supplier.contact_info && (
                          <p className="text-sm text-gray-500 truncate">
                            {supplier.contact_info}
                          </p>
                        )}
                      </div>
                    </div>
                    <div className="flex items-center space-x-2">
                      <button
                        onClick={() => handleToggleSupplierStatus(supplier)}
                        className={`inline-flex items-center px-3 py-1 border border-transparent text-xs font-medium rounded-full ${supplier.is_active
                            ? 'text-red-700 bg-red-100 hover:bg-red-200'
                            : 'text-green-700 bg-green-100 hover:bg-green-200'
                          }`}
                      >
                        {supplier.is_active ? 'Deactivate' : 'Activate'}
                      </button>
                      <button
                        onClick={() => setEditingSupplier(supplier)}
                        className="inline-flex items-center px-3 py-1 border border-gray-300 text-xs font-medium rounded-full text-gray-700 bg-white hover:bg-gray-50"
                      >
                        Edit
                      </button>
                    </div>
                  </div>
                </li>
              ))}
            </ul>
          )}
        </div>
      )}

      {/* Create Supplier Modal */}
      {showCreateModal && (
        <Modal
          isOpen={showCreateModal}
          onClose={() => setShowCreateModal(false)}
          title="Create New Supplier"
        >
          <OrganizationForm
            initialData={{
              organization_type: 'supplier',
              parent_organization_id: organizationId,
              is_active: true
            }}
            onSubmit={handleCreateSupplier}
            onClose={() => setShowCreateModal(false)}
          />
        </Modal>
      )}

      {/* Edit Supplier Modal */}
      {editingSupplier && (
        <Modal
          isOpen={!!editingSupplier}
          onClose={() => setEditingSupplier(null)}
          title="Edit Supplier"
        >
          <OrganizationForm
            initialData={editingSupplier}
            onSubmit={handleUpdateSupplier}
            onClose={() => setEditingSupplier(null)}
          />
        </Modal>
      )}
    </div>
  );
};

export default SupplierManager;