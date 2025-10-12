// frontend/src/pages/Inventory.js

import React, { useState, useEffect, useCallback } from 'react';
import { inventoryService } from '../services/inventoryService';
import { warehouseService } from '../services/warehouseService';
import { partsService } from '../services/partsService';
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
  const [warehouseInventoryRefresh, setWarehouseInventoryRefresh] = useState(null);



  const fetchData = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const filters = {};
      if (selectedWarehouseId) {
        filters.warehouse_id = selectedWarehouseId;
      }

      // Fetch data with individual error handling to identify which call is failing
      let orgsData = [];
      let warehousesData = [];
      let partsResponse = [];

      try {
        orgsData = await api.get('/organizations');
      } catch (orgError) {
        console.error('Failed to fetch organizations:', orgError);
        orgsData = [];
      }

      try {
        warehousesData = await warehouseService.getWarehouses();
      } catch (warehouseError) {
        console.error('Failed to fetch warehouses:', warehouseError);
        warehousesData = [];
      }

      try {
        partsResponse = await partsService.getPartsWithInventory({ limit: 1000 });
      } catch (partsError) {
        console.error('Failed to fetch parts:', partsError);
        partsResponse = [];
      }



      setOrganizations(orgsData);
      setWarehouses(warehousesData);
      // Handle paginated response format
      const partsData = partsResponse?.items || partsResponse || [];
      setParts(Array.isArray(partsData) ? partsData : []);
    } catch (err) {
      setError(err.message || 'Failed to fetch inventory data.');
    } finally {
      setLoading(false);
    }
  }, [selectedWarehouseId]);

  useEffect(() => {
    fetchData();
  }, []);

  // Auto-refresh every 10 minutes
  useEffect(() => {
    const interval = setInterval(() => {
      fetchData();
    }, 10 * 60 * 1000);

    return () => clearInterval(interval);
  }, []);

  const handleCreateOrUpdate = async (inventoryData) => {
    try {
      if (editingInventory) {
        await inventoryService.updateInventoryItem(editingInventory.id, inventoryData);
      } else {
        await inventoryService.createInventoryItem(inventoryData);
      }

      // Close modal first to avoid any interference
      closeModal();

      // Refresh the main inventory data
      await fetchData();

      // Auto-select the warehouse if we're in warehouse view and it's not already selected
      if (viewMode === 'warehouse' && inventoryData.warehouse_id !== selectedWarehouseId) {
        const targetWarehouse = warehouses.find(w => w.id === inventoryData.warehouse_id);
        if (targetWarehouse) {
          setSelectedWarehouseId(inventoryData.warehouse_id);
          setSelectedWarehouse(targetWarehouse);
        }
      }

      // Dispatch event for any listening components
      const eventDetail = {
        warehouseId: inventoryData.warehouse_id,
        partId: inventoryData.part_id,
        action: editingInventory ? 'update' : 'create'
      };
      window.dispatchEvent(new CustomEvent('inventoryUpdated', { detail: eventDetail }));

      // Force refresh the warehouse inventory view if it's currently displayed
      // Use a longer delay to ensure the warehouse selection has time to update
      setTimeout(async () => {
        if (warehouseInventoryRefresh && typeof warehouseInventoryRefresh === 'function') {
          try {
            await warehouseInventoryRefresh();
          } catch (refreshError) {
            console.error('Error refreshing warehouse inventory:', refreshError);
          }
        }
      }, 300);

      // Additional refresh after warehouse selection should be complete
      setTimeout(async () => {
        if (warehouseInventoryRefresh && typeof warehouseInventoryRefresh === 'function') {
          try {
            await warehouseInventoryRefresh();
          } catch (refreshError) {
            console.error('Error refreshing warehouse inventory:', refreshError);
          }
        }
      }, 2000);

    } catch (err) {
      console.error("Error creating/updating inventory item:", err);
      // Re-throw to be caught by the form's error handling
      throw err;
    }
  };

  const handleInventoryTransfer = async (transferData) => {
    try {
      await inventoryService.transferInventory(transferData);

      // Close modal first to avoid any interference
      closeModal();

      // Refresh the main inventory data
      await fetchData();

      // Dispatch event immediately for any listening components
      const eventDetail = {
        warehouseId: transferData.from_warehouse_id,
        toWarehouseId: transferData.to_warehouse_id,
        partId: transferData.part_id,
        transfer: transferData.quantity
      };
      window.dispatchEvent(new CustomEvent('inventoryUpdated', { detail: eventDetail }));

      // Force refresh the warehouse inventory view with multiple attempts for reliability
      if (warehouseInventoryRefresh && typeof warehouseInventoryRefresh === 'function') {
        // Use multiple refresh attempts to ensure it works
        setTimeout(async () => {
          try {
            await warehouseInventoryRefresh();
          } catch (refreshError) {
            console.error('Error refreshing warehouse inventory:', refreshError);
          }
        }, 100);

        setTimeout(async () => {
          try {
            await warehouseInventoryRefresh();
          } catch (refreshError) {
            console.error('Error refreshing warehouse inventory:', refreshError);
          }
        }, 1000);
      }

    } catch (err) {
      console.error("Error creating inventory transfer:", err);
      throw err;
    }
  };

  const handleStockAdjustment = async (adjustmentData) => {
    try {
      await inventoryService.createWarehouseStockAdjustment(selectedWarehouseId, adjustmentData);

      // Refresh the main inventory data first
      await fetchData();

      // Force refresh the warehouse inventory view with a small delay to ensure backend consistency
      if (warehouseInventoryRefresh && typeof warehouseInventoryRefresh === 'function') {
        // Add a small delay to ensure database consistency
        setTimeout(async () => {
          try {
            await warehouseInventoryRefresh();
          } catch (refreshError) {
            console.error('Error refreshing warehouse inventory:', refreshError);
          }
        }, 500);
      }

      // Also trigger a page-level refresh to ensure all components are updated
      window.dispatchEvent(new CustomEvent('inventoryUpdated', {
        detail: {
          warehouseId: selectedWarehouseId,
          partId: adjustmentData.part_id,
          adjustment: adjustmentData.quantity_change
        }
      }));

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
            warehouses={warehouses}
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
      <>
        {viewMode === 'warehouse' && (
          <>
            {selectedWarehouseId ? (
              <WarehouseDetailedView
                warehouseId={selectedWarehouseId}
                warehouse={selectedWarehouse}
                onInventoryRefresh={setWarehouseInventoryRefresh}
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
      </>

      <Modal
        isOpen={showModal}
        onClose={closeModal}
        title={getModalTitle()}
      >
        {renderModalContent()}
      </Modal>
    </div >
  );
};

export default Inventory;