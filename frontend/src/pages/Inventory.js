// frontend/src/pages/Inventory.js

import React, { useState, useEffect, useCallback } from 'react';
import { inventoryService } from '../services/inventoryService';
import { warehouseService } from '../services/warehouseService';
import { api } from '../services/api'; // For fetching related data
import { useAuth } from '../AuthContext';
import Modal from '../components/Modal';
import InventoryForm from '../components/InventoryForm';
import InventoryTransferForm from '../components/InventoryTransferForm';
import WarehouseStockAdjustmentForm from '../components/WarehouseStockAdjustmentForm';
import WarehouseInventoryAggregationView from '../components/WarehouseInventoryAggregationView';
import WarehouseInventoryAnalytics from '../components/WarehouseInventoryAnalytics';
import WarehouseInventoryReporting from '../components/WarehouseInventoryReporting';
import WarehouseDetailedView from '../components/WarehouseDetailedView';
import WarehouseSelector from '../components/WarehouseSelector';
import PermissionGuard from '../components/PermissionGuard';
import { PERMISSIONS } from '../utils/permissions';

const Inventory = () => {
  const { user } = useAuth();
  const [organizations, setOrganizations] = useState([]);
  const [warehouses, setWarehouses] = useState([]);
  const [parts, setParts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showModal, setShowModal] = useState(false);
  const [modalType, setModalType] = useState('inventory'); // 'inventory', 'transfer', 'adjustment'
  const [editingInventory, setEditingInventory] = useState(null);
  const [isEditMode, setIsEditMode] = useState(false);
  const [selectedWarehouseId, setSelectedWarehouseId] = useState('');
  const [selectedWarehouse, setSelectedWarehouse] = useState(null);
  const [viewMode, setViewMode] = useState('warehouse'); // 'warehouse', 'aggregated', 'analytics', 'reporting'

  const fetchData = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const filters = {};
      if (selectedWarehouseId) {
        filters.warehouse_id = selectedWarehouseId;
      }

      const [, orgsData, warehousesData, partsData] = await Promise.all([
        inventoryService.getInventory(filters),
        api.get('/organizations'),
        warehouseService.getWarehouses(),
        api.get('/parts'),
      ]);

      setOrganizations(orgsData);
      setWarehouses(warehousesData);
      setParts(partsData);
    } catch (err) {
      setError(err.message || 'Failed to fetch inventory data.');
    } finally {
      setLoading(false);
    }
  }, [selectedWarehouseId]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const handleCreateOrUpdate = async (inventoryData) => {
    try {
      if (editingInventory) {
        await inventoryService.updateInventoryItem(editingInventory.id, inventoryData);
      } else {
        await inventoryService.createInventoryItem(inventoryData);
      }

      await fetchData();
      closeModal();
    } catch (err) {
      console.error("Error creating/updating inventory item:", err);
      // Re-throw to be caught by the form's error handling
      throw err;
    }
  };

  const handleInventoryTransfer = async (transferData) => {
    try {
      await inventoryService.transferInventory(transferData);
      await fetchData();
      closeModal();
    } catch (err) {
      console.error("Error creating inventory transfer:", err);
      throw err;
    }
  };

  const handleStockAdjustment = async (adjustmentData) => {
    try {
      await inventoryService.createWarehouseStockAdjustment(selectedWarehouseId, adjustmentData);
      await fetchData();
      closeModal();
    } catch (err) {
      console.error("Error creating stock adjustment:", err);
      throw err;
    }
  };

  const openModal = (type = 'inventory', inventory = null) => {
    setModalType(type);
    setEditingInventory(inventory);
    setIsEditMode(!!inventory);
    setShowModal(true);
  };

  const closeModal = () => {
    setShowModal(false);
    setModalType('inventory');
    setEditingInventory(null);
    setIsEditMode(false);
  };

  const handleWarehouseChange = (warehouseId, warehouse) => {
    setSelectedWarehouseId(warehouseId);
    setSelectedWarehouse(warehouse);
  };

  const getModalTitle = () => {
    switch (modalType) {
      case 'transfer':
        return 'Transfer Inventory Between Warehouses';
      case 'adjustment':
        return 'Adjust Warehouse Stock';
      default:
        return editingInventory ? "Edit Inventory Item" : "Add New Inventory Item";
    }
  };

  const renderModalContent = () => {
    switch (modalType) {
      case 'transfer':
        return (
          <InventoryTransferForm
            onSubmit={handleInventoryTransfer}
            onCancel={closeModal}
          />
        );
      case 'adjustment':
        return (
          <WarehouseStockAdjustmentForm
            warehouseId={selectedWarehouseId}
            warehouse={selectedWarehouse}
            onSubmit={handleStockAdjustment}
            onCancel={closeModal}
          />
        );
      default:
        return (
          <InventoryForm
            initialData={editingInventory || {}}
            organizations={organizations}
            parts={parts}
            onSubmit={handleCreateOrUpdate}
            onClose={closeModal}
            isEditMode={isEditMode}
          />
        );
    }
  };

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold text-gray-800">Warehouse Inventory Management</h1>
        <div className="flex space-x-2">
          <PermissionGuard permission={PERMISSIONS.ADJUST_INVENTORY} hideIfNoPermission={true}>
            <button
              onClick={() => openModal('transfer')}
              className="bg-green-600 text-white py-2 px-4 rounded-md hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2 transition duration-150 ease-in-out font-semibold"
            >
              Transfer Inventory
            </button>
          </PermissionGuard>
          <PermissionGuard permission={PERMISSIONS.ADJUST_INVENTORY} hideIfNoPermission={true}>
            <button
              onClick={() => openModal('adjustment')}
              disabled={!selectedWarehouseId}
              className="bg-orange-600 text-white py-2 px-4 rounded-md hover:bg-orange-700 focus:outline-none focus:ring-2 focus:ring-orange-500 focus:ring-offset-2 transition duration-150 ease-in-out font-semibold disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Adjust Stock
            </button>
          </PermissionGuard>
          <PermissionGuard permission={PERMISSIONS.ADJUST_INVENTORY} hideIfNoPermission={true}>
            <button
              onClick={() => openModal('inventory')}
              className="bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition duration-150 ease-in-out font-semibold"
            >
              Add Inventory Item
            </button>
          </PermissionGuard>
        </div>
      </div>

      {/* View Mode Selector */}
      <div className="mb-6">
        <div className="flex space-x-1 bg-gray-100 p-1 rounded-lg w-fit">
          <button
            onClick={() => setViewMode('warehouse')}
            className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${viewMode === 'warehouse'
              ? 'bg-white text-blue-600 shadow-sm'
              : 'text-gray-600 hover:text-gray-900'
              }`}
          >
            Warehouse View
          </button>
          <button
            onClick={() => setViewMode('aggregated')}
            className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${viewMode === 'aggregated'
              ? 'bg-white text-blue-600 shadow-sm'
              : 'text-gray-600 hover:text-gray-900'
              }`}
          >
            Aggregated View
          </button>
          <button
            onClick={() => setViewMode('analytics')}
            className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${viewMode === 'analytics'
              ? 'bg-white text-blue-600 shadow-sm'
              : 'text-gray-600 hover:text-gray-900'
              }`}
          >
            Analytics
          </button>
          <button
            onClick={() => setViewMode('reporting')}
            className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${viewMode === 'reporting'
              ? 'bg-white text-blue-600 shadow-sm'
              : 'text-gray-600 hover:text-gray-900'
              }`}
          >
            Reports
          </button>
        </div>
      </div>

      {loading && <p className="text-gray-500">Loading inventory...</p>}
      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative mb-4" role="alert">
          <strong className="font-bold">Error: </strong>
          <span className="block sm:inline">{error}</span>
        </div>
      )}

      {/* Warehouse Selector for Warehouse View */}
      {viewMode === 'warehouse' && (
        <div className="mb-6">
          <div className="bg-white p-4 rounded-lg shadow-md">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Select Warehouse
            </label>
            <WarehouseSelector
              selectedWarehouseId={selectedWarehouseId}
              onWarehouseChange={handleWarehouseChange}
              placeholder="Select a warehouse to view inventory"
            />
          </div>
        </div>
      )}

      {/* Render content based on view mode */}
      {viewMode === 'warehouse' && (
        <>
          {selectedWarehouseId ? (
            <WarehouseDetailedView
              warehouseId={selectedWarehouseId}
              warehouse={selectedWarehouse}
            />
          ) : (
            <div className="text-center py-10 bg-white rounded-lg shadow-md">
              <h3 className="text-xl font-semibold text-gray-700">Select a Warehouse</h3>
              <p className="text-gray-500 mt-2">
                Choose a warehouse from the dropdown above to view its inventory.
              </p>
            </div>
          )}
        </>
      )}

      {viewMode === 'aggregated' && (
        <WarehouseInventoryAggregationView
          organizationId={user.organization_id}
        />
      )}

      {viewMode === 'analytics' && (
        <>
          {selectedWarehouseId ? (
            <WarehouseInventoryAnalytics
              warehouseId={selectedWarehouseId}
              warehouse={selectedWarehouse}
            />
          ) : (
            <div className="mb-6">
              <div className="bg-white p-4 rounded-lg shadow-md">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Select Warehouse for Analytics
                </label>
                <WarehouseSelector
                  selectedWarehouseId={selectedWarehouseId}
                  onWarehouseChange={handleWarehouseChange}
                  placeholder="Select a warehouse to view analytics"
                />
              </div>
              <div className="text-center py-10 bg-white rounded-lg shadow-md mt-4">
                <h3 className="text-xl font-semibold text-gray-700">Select a Warehouse</h3>
                <p className="text-gray-500 mt-2">
                  Choose a warehouse from the dropdown above to view its analytics.
                </p>
              </div>
            </div>
          )}
        </>
      )}

      {viewMode === 'reporting' && (
        <WarehouseInventoryReporting
          organizationId={user.organization_id}
        />
      )}

      <Modal
        isOpen={showModal}
        onClose={closeModal}
        title={getModalTitle()}
      >
        {renderModalContent()}
      </Modal>
    </div>
  );
};

export default Inventory;