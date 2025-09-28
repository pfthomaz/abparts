// frontend/src/pages/Warehouses.js

import React, { useState, useEffect, useCallback } from 'react';
import { useAuth } from '../AuthContext';
import { warehouseService } from '../services/warehouseService';
import { organizationsService } from '../services/organizationsService';
import Modal from '../components/Modal';
import WarehouseForm from '../components/WarehouseForm';
import WarehouseSelector from '../components/WarehouseSelector';
import WarehousePerformanceDashboard from '../components/WarehousePerformanceDashboard';
import WarehouseStockAdjustmentForm from '../components/WarehouseStockAdjustmentForm';
import WarehouseDetailedView from '../components/WarehouseDetailedView';
import { inventoryService } from '../services/inventoryService';

const Warehouses = () => {
  const { user } = useAuth();
  const [warehouses, setWarehouses] = useState([]);
  const [organizations, setOrganizations] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedOrganization, setSelectedOrganization] = useState('');
  const [includeInactive, setIncludeInactive] = useState(false);
  const [selectedWarehouse, setSelectedWarehouse] = useState(null);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [showPerformanceModal, setShowPerformanceModal] = useState(false);
  const [showInventoryModal, setShowInventoryModal] = useState(false);
  const [showAdjustmentModal, setShowAdjustmentModal] = useState(false);
  const [editingWarehouse, setEditingWarehouse] = useState(null);
  const [selectedWarehouseForInventory, setSelectedWarehouseForInventory] = useState(null);
  const [formLoading, setFormLoading] = useState(false);
  const [currentView, setCurrentView] = useState('list'); // 'list' or 'performance'



  const fetchOrganizations = useCallback(async () => {
    try {
      const data = await organizationsService.getOrganizations();
      setOrganizations(data);
    } catch (err) {
      console.error('Failed to fetch organizations:', err);
    }
  }, []);

  const handleSearch = useCallback(async () => {
    setLoading(true);
    setError('');
    try {
      const filters = {
        include_inactive: includeInactive
      };

      if (selectedOrganization) {
        filters.organization_id = selectedOrganization;
      }

      let data;
      if (searchQuery.trim()) {
        data = await warehouseService.searchWarehouses(searchQuery, filters);
      } else {
        data = await warehouseService.getWarehouses(filters);
      }

      setWarehouses(data);
    } catch (err) {
      setError(searchQuery.trim() ? 'Failed to search warehouses' : 'Failed to fetch warehouses');
      console.error('Failed to fetch/search warehouses:', err);
    } finally {
      setLoading(false);
    }
  }, [searchQuery, selectedOrganization, includeInactive]);

  useEffect(() => {
    fetchOrganizations();
  }, [fetchOrganizations]);

  useEffect(() => {
    handleSearch();
  }, [handleSearch]);

  const handleCreateWarehouse = async (warehouseData) => {
    setFormLoading(true);
    try {
      await warehouseService.createWarehouse(warehouseData);
      setShowCreateModal(false);
      handleSearch();
    } catch (err) {
      console.error('Failed to create warehouse:', err);
      throw err;
    } finally {
      setFormLoading(false);
    }
  };

  const handleUpdateWarehouse = async (warehouseData) => {
    setFormLoading(true);
    try {
      await warehouseService.updateWarehouse(editingWarehouse.id, warehouseData);
      setShowEditModal(false);
      setEditingWarehouse(null);
      handleSearch();
    } catch (err) {
      console.error('Failed to update warehouse:', err);
      throw err;
    } finally {
      setFormLoading(false);
    }
  };

  const handleToggleWarehouseStatus = async (warehouse) => {
    try {
      if (warehouse.is_active) {
        await warehouseService.deactivateWarehouse(warehouse.id);
      } else {
        await warehouseService.activateWarehouse(warehouse.id);
      }
      handleSearch();
    } catch (err) {
      setError(`Failed to ${warehouse.is_active ? 'deactivate' : 'activate'} warehouse`);
      console.error('Failed to toggle warehouse status:', err);
    }
  };

  const handleDeleteWarehouse = async (warehouse) => {
    if (!window.confirm(`Are you sure you want to delete warehouse "${warehouse.name}"? This action cannot be undone.`)) {
      return;
    }

    try {
      await warehouseService.deleteWarehouse(warehouse.id);
      handleSearch();
    } catch (err) {
      if (err.message && err.message.includes('inventory')) {
        setError(`Cannot delete warehouse "${warehouse.name}" because it has inventory. Please adjust inventory to zero first or transfer items to another warehouse.`);
      } else {
        setError('Failed to delete warehouse. It may have associated inventory or transactions.');
      }
      console.error('Failed to delete warehouse:', err);
    }
  };

  const openEditModal = (warehouse) => {
    setEditingWarehouse(warehouse);
    setShowEditModal(true);
  };

  const openPerformanceModal = (warehouse) => {
    setSelectedWarehouse(warehouse);
    setShowPerformanceModal(true);
  };

  const openInventoryModal = (warehouse) => {
    setSelectedWarehouseForInventory(warehouse);
    setShowInventoryModal(true);
  };

  const openAdjustmentModal = (warehouse) => {
    setSelectedWarehouseForInventory(warehouse);
    setShowAdjustmentModal(true);
  };

  const handleStockAdjustment = async (adjustmentData) => {
    try {
      await inventoryService.createWarehouseStockAdjustment(selectedWarehouseForInventory.id, adjustmentData);
      setShowAdjustmentModal(false);
      setSelectedWarehouseForInventory(null);
      // Optionally refresh data or show success message
    } catch (err) {
      console.error("Error creating stock adjustment:", err);
      throw err;
    }
  };

  const getOrganizationName = (organizationId) => {
    const org = organizations.find(o => o.id === organizationId);
    return org ? org.name : 'Unknown Organization';
  };

  // Filter organizations for super_admin view
  const availableOrganizations = user?.role === 'super_admin'
    ? organizations
    : organizations.filter(org => org.id === user?.organization_id);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Warehouse Management</h1>
          <p className="text-gray-600">Manage warehouse locations and monitor performance</p>
        </div>

        <div className="flex items-center space-x-3">
          {/* View Toggle */}
          <div className="flex bg-gray-100 rounded-lg p-1">
            <button
              onClick={() => setCurrentView('list')}
              className={`px-3 py-1 rounded text-sm font-medium ${currentView === 'list'
                ? 'bg-white text-gray-900 shadow-sm'
                : 'text-gray-600 hover:text-gray-900'
                }`}
            >
              List View
            </button>
            <button
              onClick={() => setCurrentView('performance')}
              className={`px-3 py-1 rounded text-sm font-medium ${currentView === 'performance'
                ? 'bg-white text-gray-900 shadow-sm'
                : 'text-gray-600 hover:text-gray-900'
                }`}
            >
              Performance
            </button>
          </div>

          <button
            onClick={() => setShowCreateModal(true)}
            className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            Add Warehouse
          </button>
        </div>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
          {error}
        </div>
      )}

      {/* Performance View */}
      {currentView === 'performance' && (
        <div className="space-y-4">
          <div className="bg-white p-4 rounded-lg border border-gray-200">
            <div className="flex items-center space-x-4">
              <div className="flex-1">
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Select Warehouse for Performance Analysis
                </label>
                <WarehouseSelector
                  selectedWarehouseId={selectedWarehouse?.id}
                  onWarehouseChange={(warehouseId, warehouse) => setSelectedWarehouse(warehouse)}
                  organizationId={selectedOrganization}
                  includeInactive={includeInactive}
                  placeholder="Choose a warehouse to view performance"
                />
              </div>
            </div>
          </div>

          {selectedWarehouse && (
            <WarehousePerformanceDashboard
              warehouseId={selectedWarehouse.id}
              warehouse={selectedWarehouse}
            />
          )}
        </div>
      )}

      {/* List View */}
      {currentView === 'list' && (
        <>
          {/* Filters */}
          <div className="bg-white p-4 rounded-lg border border-gray-200">
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Search Warehouses
                </label>
                <input
                  type="text"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  placeholder="Search by name, location..."
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              {user?.role === 'super_admin' && (
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Organization
                  </label>
                  <select
                    value={selectedOrganization}
                    onChange={(e) => setSelectedOrganization(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="">All Organizations</option>
                    {availableOrganizations.map(org => (
                      <option key={org.id} value={org.id}>
                        {org.name} ({org.organization_type})
                      </option>
                    ))}
                  </select>
                </div>
              )}

              <div className="flex items-center">
                <input
                  type="checkbox"
                  id="includeInactive"
                  checked={includeInactive}
                  onChange={(e) => setIncludeInactive(e.target.checked)}
                  className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                />
                <label htmlFor="includeInactive" className="ml-2 block text-sm text-gray-700">
                  Include inactive warehouses
                </label>
              </div>
            </div>
          </div>

          {/* Warehouses Table */}
          <div className="bg-white shadow overflow-hidden sm:rounded-md">
            {loading ? (
              <div className="p-8 text-center">
                <div className="text-gray-500">Loading warehouses...</div>
              </div>
            ) : warehouses.length === 0 ? (
              <div className="p-8 text-center">
                <div className="text-gray-500">
                  {searchQuery ? 'No warehouses found matching your search.' : 'No warehouses found.'}
                </div>
              </div>
            ) : (
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Warehouse
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Organization
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Location
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Status
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {warehouses.map((warehouse) => (
                    <tr key={warehouse.id} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div>
                          <div className="text-sm font-medium text-gray-900">
                            {warehouse.name}
                          </div>
                          {warehouse.description && (
                            <div className="text-sm text-gray-500">
                              {warehouse.description}
                            </div>
                          )}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-900">
                          {getOrganizationName(warehouse.organization_id)}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-900">
                          {warehouse.location || 'Not specified'}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${warehouse.is_active
                          ? 'bg-green-100 text-green-800'
                          : 'bg-red-100 text-red-800'
                          }`}>
                          {warehouse.is_active ? 'Active' : 'Inactive'}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                        <div className="flex flex-wrap gap-2">
                          <button
                            onClick={() => openInventoryModal(warehouse)}
                            className="text-purple-600 hover:text-purple-900"
                            title="View inventory"
                          >
                            Inventory
                          </button>
                          <button
                            onClick={() => openAdjustmentModal(warehouse)}
                            className="text-green-600 hover:text-green-900"
                            title="Adjust stock levels"
                          >
                            Adjust Stock
                          </button>
                          <button
                            onClick={() => openPerformanceModal(warehouse)}
                            className="text-blue-600 hover:text-blue-900"
                          >
                            Performance
                          </button>
                          <button
                            onClick={() => openEditModal(warehouse)}
                            className="text-indigo-600 hover:text-indigo-900"
                          >
                            Edit
                          </button>
                          <button
                            onClick={() => handleToggleWarehouseStatus(warehouse)}
                            className={`${warehouse.is_active
                              ? 'text-orange-600 hover:text-orange-900'
                              : 'text-green-600 hover:text-green-900'
                              }`}
                          >
                            {warehouse.is_active ? 'Deactivate' : 'Activate'}
                          </button>
                          <button
                            onClick={() => handleDeleteWarehouse(warehouse)}
                            className="text-red-600 hover:text-red-900"
                          >
                            Delete
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        </>
      )}

      {/* Create Warehouse Modal */}
      <Modal
        isOpen={showCreateModal}
        onClose={() => setShowCreateModal(false)}
        title="Create New Warehouse"
        size="lg"
      >
        <WarehouseForm
          onSubmit={handleCreateWarehouse}
          onCancel={() => setShowCreateModal(false)}
          loading={formLoading}
        />
      </Modal>

      {/* Edit Warehouse Modal */}
      <Modal
        isOpen={showEditModal}
        onClose={() => {
          setShowEditModal(false);
          setEditingWarehouse(null);
        }}
        title="Edit Warehouse"
        size="lg"
      >
        <WarehouseForm
          warehouse={editingWarehouse}
          onSubmit={handleUpdateWarehouse}
          onCancel={() => {
            setShowEditModal(false);
            setEditingWarehouse(null);
          }}
          loading={formLoading}
        />
      </Modal>

      {/* Performance Modal */}
      <Modal
        isOpen={showPerformanceModal}
        onClose={() => {
          setShowPerformanceModal(false);
          setSelectedWarehouse(null);
        }}
        title="Warehouse Performance"
        size="xl"
      >
        {selectedWarehouse && (
          <WarehousePerformanceDashboard
            warehouseId={selectedWarehouse.id}
            warehouse={selectedWarehouse}
          />
        )}
      </Modal>

      {/* Inventory Modal */}
      <Modal
        isOpen={showInventoryModal}
        onClose={() => {
          setShowInventoryModal(false);
          setSelectedWarehouseForInventory(null);
        }}
        title={`Inventory - ${selectedWarehouseForInventory?.name}`}
        size="xl"
      >
        {selectedWarehouseForInventory && (
          <WarehouseDetailedView
            warehouseId={selectedWarehouseForInventory.id}
            warehouse={selectedWarehouseForInventory}
          />
        )}
      </Modal>

      {/* Stock Adjustment Modal */}
      <Modal
        isOpen={showAdjustmentModal}
        onClose={() => {
          setShowAdjustmentModal(false);
          setSelectedWarehouseForInventory(null);
        }}
        title={`Adjust Stock - ${selectedWarehouseForInventory?.name}`}
        size="lg"
      >
        {selectedWarehouseForInventory && (
          <WarehouseStockAdjustmentForm
            warehouseId={selectedWarehouseForInventory.id}
            warehouse={selectedWarehouseForInventory}
            onSubmit={handleStockAdjustment}
            onCancel={() => {
              setShowAdjustmentModal(false);
              setSelectedWarehouseForInventory(null);
            }}
          />
        )}
      </Modal>
    </div>
  );
};

export default Warehouses;