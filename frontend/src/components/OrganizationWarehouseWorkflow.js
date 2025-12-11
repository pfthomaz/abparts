// frontend/src/components/OrganizationWarehouseWorkflow.js

import React, { useState, useEffect } from 'react';
import { useAuth } from '../AuthContext';
import { organizationsService } from '../services/organizationsService';
import { warehouseService } from '../services/warehouseService';
import { getCountryFlag } from '../utils/countryFlags';

const OrganizationWarehouseWorkflow = ({ organizationId, onWarehouseCreated }) => {
  const { user } = useAuth();
  const [organization, setOrganization] = useState(null);
  const [warehouses, setWarehouses] = useState([]);
  const [loading, setLoading] = useState(false);
  const [creating, setCreating] = useState(false);
  const [error, setError] = useState(null);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [warehouseData, setWarehouseData] = useState({
    name: '',
    location: '',
    description: '',
    is_active: true
  });

  // Load organization and its warehouses
  const loadData = async () => {
    if (!organizationId) return;

    setLoading(true);
    setError(null);
    try {
      // Load organization details
      const orgResponse = await organizationsService.getOrganization(organizationId);
      const orgData = orgResponse.data || orgResponse;
      setOrganization(orgData);

      // Load existing warehouses
      const warehousesResponse = await warehouseService.getOrganizationWarehouses(organizationId);
      setWarehouses(warehousesResponse.data || warehousesResponse);

      // Auto-populate warehouse name with organization name if no warehouses exist
      if ((!warehousesResponse.data || warehousesResponse.data.length === 0) && orgData) {
        setWarehouseData(prev => ({
          ...prev,
          name: `${orgData.name} Main Warehouse`,
          location: orgData.address || '',
          description: `Default warehouse for ${orgData.name}`
        }));
      }
    } catch (err) {
      console.error('Failed to load organization data:', err);
      setError('Failed to load organization data. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [organizationId]);

  // Handle warehouse creation
  const handleCreateWarehouse = async (e) => {
    e.preventDefault();
    if (!organization) return;

    setCreating(true);
    setError(null);
    try {
      const newWarehouseData = {
        ...warehouseData,
        organization_id: organizationId
      };

      const response = await warehouseService.createWarehouse(newWarehouseData);

      // Reset form
      setWarehouseData({
        name: '',
        location: '',
        description: '',
        is_active: true
      });
      setShowCreateForm(false);

      // Reload warehouses
      await loadData();

      if (onWarehouseCreated) {
        onWarehouseCreated(response.data || response);
      }
    } catch (err) {
      console.error('Failed to create warehouse:', err);
      setError(err.response?.data?.detail || 'Failed to create warehouse. Please try again.');
    } finally {
      setCreating(false);
    }
  };

  // Handle auto-create default warehouse
  const handleAutoCreateDefaultWarehouse = async () => {
    if (!organization) return;

    setCreating(true);
    setError(null);
    try {
      const defaultWarehouseData = {
        name: `${organization.name} Main Warehouse`,
        location: organization.address || '',
        description: `Default warehouse for ${organization.name}`,
        organization_id: organizationId,
        is_active: true
      };

      const response = await warehouseService.createWarehouse(defaultWarehouseData);

      // Reload warehouses
      await loadData();

      if (onWarehouseCreated) {
        onWarehouseCreated(response.data || response);
      }
    } catch (err) {
      console.error('Failed to auto-create warehouse:', err);
      setError(err.response?.data?.detail || 'Failed to create default warehouse. Please try again.');
    } finally {
      setCreating(false);
    }
  };

  // Handle form input changes
  const handleInputChange = (e) => {
    const { name, value, type, checked } = e.target;
    setWarehouseData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
  };

  if (!organizationId) {
    return (
      <div className="text-center py-8 text-gray-500">
        Select an organization to manage its warehouses
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h3 className="text-lg font-medium text-gray-900">Warehouse Management</h3>
          <p className="text-sm text-gray-500">
            Manage warehouses for this organization
          </p>
        </div>
      </div>

      {/* Loading State */}
      {loading && (
        <div className="flex justify-center py-8">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
        </div>
      )}

      {/* Error Display */}
      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative">
          <span className="block sm:inline">{error}</span>
        </div>
      )}

      {/* Organization Info */}
      {organization && !loading && (
        <div className="bg-white border border-gray-200 rounded-lg p-4">
          <div className="flex items-center space-x-3">
            <div className="flex-shrink-0">
              <span className="text-2xl">🏢</span>
            </div>
            <div className="flex-1">
              <div className="flex items-center space-x-2">
                <h4 className="text-lg font-medium text-gray-900">{organization.name}</h4>
                {organization.country && (
                  <span className="text-lg">{getCountryFlag(organization.country)}</span>
                )}
              </div>
              <p className="text-sm text-gray-500">{organization.organization_type}</p>
              {organization.address && (
                <p className="text-sm text-gray-600 mt-1">{organization.address}</p>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Warehouse Status */}
      {!loading && organization && (
        <div className="bg-white border border-gray-200 rounded-lg p-6">
          <div className="flex items-center justify-between mb-4">
            <h4 className="text-md font-medium text-gray-900">Warehouse Status</h4>
            <span className="text-sm text-gray-500">
              {warehouses.length} {warehouses.length === 1 ? 'warehouse' : 'warehouses'}
            </span>
          </div>

          {warehouses.length === 0 ? (
            <div className="text-center py-8">
              <div className="mx-auto flex items-center justify-center h-12 w-12 rounded-full bg-yellow-100">
                <svg className="h-6 w-6 text-yellow-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
                </svg>
              </div>
              <h3 className="mt-2 text-sm font-medium text-gray-900">No warehouses found</h3>
              <p className="mt-1 text-sm text-gray-500">
                This organization doesn't have any warehouses yet. Create one to get started.
              </p>
              <div className="mt-6 flex flex-col sm:flex-row gap-3 justify-center">
                <button
                  onClick={handleAutoCreateDefaultWarehouse}
                  disabled={creating}
                  className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50"
                >
                  {creating ? (
                    <>
                      <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                      </svg>
                      Creating...
                    </>
                  ) : (
                    <>
                      <svg className="-ml-1 mr-2 h-5 w-5" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                        <path fillRule="evenodd" d="M10 3a1 1 0 011 1v5h5a1 1 0 110 2h-5v5a1 1 0 11-2 0v-5H4a1 1 0 110-2h5V4a1 1 0 011-1z" clipRule="evenodd" />
                      </svg>
                      Auto-Create Default Warehouse
                    </>
                  )}
                </button>
                <button
                  onClick={() => setShowCreateForm(true)}
                  className="inline-flex items-center px-4 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
                >
                  Custom Warehouse
                </button>
              </div>
            </div>
          ) : (
            <div className="space-y-3">
              {warehouses.map((warehouse) => (
                <div key={warehouse.id} className="flex items-center justify-between p-3 border border-gray-200 rounded-md">
                  <div className="flex items-center space-x-3">
                    <div className="flex-shrink-0">
                      <span className="text-lg">🏪</span>
                    </div>
                    <div>
                      <p className="text-sm font-medium text-gray-900">{warehouse.name}</p>
                      {warehouse.location && (
                        <p className="text-sm text-gray-500">{warehouse.location}</p>
                      )}
                    </div>
                  </div>
                  <div className="flex items-center space-x-2">
                    {warehouse.is_active ? (
                      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                        Active
                      </span>
                    ) : (
                      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800">
                        Inactive
                      </span>
                    )}
                  </div>
                </div>
              ))}
              <div className="pt-3 border-t border-gray-200">
                <button
                  onClick={() => setShowCreateForm(true)}
                  className="inline-flex items-center px-3 py-2 border border-gray-300 shadow-sm text-sm leading-4 font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
                >
                  <svg className="-ml-0.5 mr-2 h-4 w-4" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                    <path fillRule="evenodd" d="M10 3a1 1 0 011 1v5h5a1 1 0 110 2h-5v5a1 1 0 11-2 0v-5H4a1 1 0 110-2h5V4a1 1 0 011-1z" clipRule="evenodd" />
                  </svg>
                  Add Another Warehouse
                </button>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Custom Warehouse Creation Form */}
      {showCreateForm && (
        <div className="bg-white border border-gray-200 rounded-lg p-6">
          <div className="flex justify-between items-center mb-4">
            <h4 className="text-md font-medium text-gray-900">Create Custom Warehouse</h4>
            <button
              onClick={() => setShowCreateForm(false)}
              className="text-gray-400 hover:text-gray-600"
            >
              <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          <form onSubmit={handleCreateWarehouse} className="space-y-4">
            <div>
              <label htmlFor="name" className="block text-sm font-medium text-gray-700">
                Warehouse Name *
              </label>
              <input
                type="text"
                id="name"
                name="name"
                required
                value={warehouseData.name}
                onChange={handleInputChange}
                className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                placeholder="Enter warehouse name"
              />
            </div>

            <div>
              <label htmlFor="location" className="block text-sm font-medium text-gray-700">
                Location
              </label>
              <input
                type="text"
                id="location"
                name="location"
                value={warehouseData.location}
                onChange={handleInputChange}
                className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                placeholder="Enter warehouse location"
              />
            </div>

            <div>
              <label htmlFor="description" className="block text-sm font-medium text-gray-700">
                Description
              </label>
              <textarea
                id="description"
                name="description"
                rows={3}
                value={warehouseData.description}
                onChange={handleInputChange}
                className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                placeholder="Enter warehouse description"
              />
            </div>

            <div className="flex items-center">
              <input
                id="is_active"
                name="is_active"
                type="checkbox"
                checked={warehouseData.is_active}
                onChange={handleInputChange}
                className="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded"
              />
              <label htmlFor="is_active" className="ml-2 block text-sm text-gray-900">
                Warehouse is active
              </label>
            </div>

            <div className="flex justify-end space-x-3 pt-4 border-t border-gray-200">
              <button
                type="button"
                onClick={() => setShowCreateForm(false)}
                className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-200 rounded-md hover:bg-gray-300 focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-offset-2"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={creating}
                className="px-4 py-2 text-sm font-medium text-white bg-indigo-600 rounded-md hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {creating ? (
                  <span className="flex items-center">
                    <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    Creating...
                  </span>
                ) : (
                  'Create Warehouse'
                )}
              </button>
            </div>
          </form>
        </div>
      )}
    </div>
  );
};

export default OrganizationWarehouseWorkflow;