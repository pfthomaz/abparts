// frontend/src/pages/Warehouses.js

import { useState, useEffect, useCallback } from 'react';
import { useAuth } from '../AuthContext';
import { useTranslation } from '../hooks/useTranslation';
import { warehouseService } from '../services/warehouseService';
import { organizationsService } from '../services/organizationsService';
import { inventoryService } from '../services/inventoryService';
import { partsService } from '../services/partsService';
import Modal from '../components/Modal';
import WarehouseForm from '../components/WarehouseForm';
import WarehouseSelector from '../components/WarehouseSelector';
import WarehousePerformanceDashboard from '../components/WarehousePerformanceDashboard';
import WarehouseStockAdjustmentForm from '../components/WarehouseStockAdjustmentForm';
import WarehouseDetailedView from '../components/WarehouseDetailedView';
import WarehouseInventoryAggregationView from '../components/WarehouseInventoryAggregationView';
import WarehouseInventoryReporting from '../components/WarehouseInventoryReporting';
import InventoryTransferForm from '../components/InventoryTransferForm';
import InventoryForm from '../components/InventoryForm';

const Warehouses = () => {
  const { user } = useAuth();
  const { t } = useTranslation();
  const [warehouses, setWarehouses] = useState([]);
  const [warehouseSummaries, setWarehouseSummaries] = useState({});
  const [organizations, setOrganizations] = useState([]);
  const [parts, setParts] = useState([]);
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
  const [showTransferModal, setShowTransferModal] = useState(false);
  const [showAddInventoryModal, setShowAddInventoryModal] = useState(false);
  const [editingWarehouse, setEditingWarehouse] = useState(null);
  const [selectedWarehouseForInventory, setSelectedWarehouseForInventory] = useState(null);
  const [formLoading, setFormLoading] = useState(false);
  const [currentView, setCurrentView] = useState('warehouses'); // 'warehouses', 'aggregated', 'reports', 'performance'

  const fetchOrganizations = useCallback(async () => {
    try {
      const data = await organizationsService.getOrganizations();
      setOrganizations(data);
    } catch (err) {
      console.error('Failed to fetch organizations:', err);
    }
  }, []);

  const fetchParts = useCallback(async () => {
    try {
      const response = await partsService.getPartsWithInventory({ limit: 1000 });
      const partsData = response?.items || response || [];
      setParts(Array.isArray(partsData) ? partsData : []);
    } catch (err) {
      console.error('Failed to fetch parts:', err);
      setParts([]);
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

      // Fetch inventory summaries for each warehouse
      const summaries = {};
      await Promise.all(
        data.map(async (warehouse) => {
          try {
            const summary = await warehouseService.getWarehouseSummary(warehouse.id);
            summaries[warehouse.id] = summary;
          } catch (err) {
            console.error(`Failed to fetch summary for warehouse ${warehouse.id}:`, err);
            summaries[warehouse.id] = { total_inventory_items: 0, total_stock_quantity: 0 };
          }
        })
      );
      setWarehouseSummaries(summaries);

    } catch (err) {
      setError(searchQuery.trim() ? 'Failed to search warehouses' : 'Failed to fetch warehouses');
      console.error('Failed to fetch/search warehouses:', err);
    } finally {
      setLoading(false);
    }
  }, [searchQuery, selectedOrganization, includeInactive]);

  useEffect(() => {
    fetchOrganizations();
    fetchParts();
  }, [fetchOrganizations, fetchParts]);

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
    try {
      const summary = await warehouseService.getWarehouseSummary(warehouse.id);

      if (summary.total_inventory_items > 0) {
        const hasStock = summary.total_stock_quantity > 0;
        const message = hasStock
          ? `Cannot delete warehouse "${warehouse.name}" because it contains ${summary.total_inventory_items} inventory items with stock. Please transfer all inventory first.`
          : `Cannot delete warehouse "${warehouse.name}" because it contains ${summary.total_inventory_items} inventory items. Please remove all inventory items first.`;
        setError(message);
        return;
      }

      if (!window.confirm(`Are you sure you want to delete warehouse "${warehouse.name}"? This action cannot be undone.`)) {
        return;
      }

      await warehouseService.deleteWarehouse(warehouse.id);
      handleSearch();
      setError('');
    } catch (err) {
      console.error('Failed to delete warehouse:', err);
      setError(`Failed to delete warehouse: ${err.response?.data?.detail || err.message}`);
    }
  };

  const handleInventoryTransfer = async (transferData) => {
    try {
      await inventoryService.transferInventory(transferData);
      setShowTransferModal(false);
      handleSearch();
      window.dispatchEvent(new CustomEvent('inventoryUpdated', {
        detail: {
          warehouseId: transferData.from_warehouse_id,
          toWarehouseId: transferData.to_warehouse_id,
          partId: transferData.part_id
        }
      }));
    } catch (err) {
      console.error("Error creating inventory transfer:", err);
      throw err;
    }
  };

  const handleCreateInventory = async (inventoryData) => {
    try {
      await inventoryService.createInventoryItem(inventoryData);
      setShowAddInventoryModal(false);
      handleSearch();
      window.dispatchEvent(new CustomEvent('inventoryUpdated', {
        detail: {
          warehouseId: inventoryData.warehouse_id,
          partId: inventoryData.part_id,
          action: 'create'
        }
      }));
    } catch (err) {
      console.error("Error creating inventory item:", err);
      throw err;
    }
  };

  const handleStockAdjustment = async (adjustmentData) => {
    try {
      await inventoryService.createWarehouseStockAdjustment(selectedWarehouseForInventory.id, adjustmentData);
      setShowAdjustmentModal(false);
      setSelectedWarehouseForInventory(null);
      await handleSearch();
      window.dispatchEvent(new CustomEvent('inventoryUpdated', {
        detail: {
          warehouseId: selectedWarehouseForInventory.id,
          partId: adjustmentData.part_id,
          adjustment: adjustmentData.quantity_change
        }
      }));
    } catch (err) {
      console.error("Error creating stock adjustment:", err);
      throw err;
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

  const getOrganizationName = (organizationId) => {
    const org = organizations.find(o => o.id === organizationId);
    return org ? org.name : 'Unknown Organization';
  };

  const availableOrganizations = user?.role === 'super_admin'
    ? organizations
    : organizations.filter(org => org.id === user?.organization_id);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">{t('warehouses.title')}</h1>
          <p className="text-gray-600">{t('warehouses.subtitle')}</p>
        </div>

        <div className="flex items-center space-x-3">
          <button
            onClick={() => setShowTransferModal(true)}
            className="bg-green-600 text-white px-4 py-2 rounded-md hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500"
          >
            {t('warehouses.transferInventory')}
          </button>
          <button
            onClick={() => setShowAddInventoryModal(true)}
            className="bg-purple-600 text-white px-4 py-2 rounded-md hover:bg-purple-700 focus:outline-none focus:ring-2 focus:ring-purple-500"
          >
            {t('warehouses.addInventoryItem')}
          </button>
          <button
            onClick={() => setShowCreateModal(true)}
            className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            {t('warehouses.addWarehouse')}
          </button>
        </div>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
          {error}
        </div>
      )}

      {/* View Mode Tabs */}
      <div className="bg-white border-b border-gray-200">
        <nav className="-mb-px flex space-x-8 px-6" aria-label="Tabs">
          {[
            { id: 'warehouses', label: t('warehouses.tabs.warehouses'), icon: '🏭' },
            { id: 'aggregated', label: t('warehouses.tabs.aggregated'), icon: '📊' },
            { id: 'reports', label: t('warehouses.tabs.reports'), icon: '📈' },
            { id: 'performance', label: t('warehouses.tabs.performance'), icon: '⚡' }
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setCurrentView(tab.id)}
              className={`py-4 px-1 border-b-2 font-medium text-sm whitespace-nowrap ${currentView === tab.id
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
            >
              <span className="mr-2">{tab.icon}</span>
              {tab.label}
            </button>
          ))}
        </nav>
      </div>

      {/* Warehouses View */}
      {currentView === 'warehouses' && (
        <>
          {/* Filters */}
          <div className="bg-white p-4 rounded-lg border border-gray-200">
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  {t('warehouses.searchWarehouses')}
                </label>
                <input
                  type="text"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  placeholder={t('warehouses.searchPlaceholder')}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              {user?.role === 'super_admin' && (
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    {t('warehouses.organization')}
                  </label>
                  <select
                    value={selectedOrganization}
                    onChange={(e) => setSelectedOrganization(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="">{t('warehouses.allOrganizations')}</option>
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
                  {t('warehouses.includeInactive')}
                </label>
              </div>
            </div>
          </div>

          {/* Warehouses Card Grid */}
          {loading ? (
            <div className="p-8 text-center">
              <div className="text-gray-500">{t('warehouses.loadingWarehouses')}</div>
            </div>
          ) : warehouses.length === 0 ? (
            <div className="p-8 text-center bg-white rounded-lg border border-gray-200">
              <div className="text-gray-500">
                {searchQuery ? t('warehouses.noWarehousesMatch') : t('warehouses.noWarehousesFound')}
              </div>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {warehouses.map((warehouse) => (
                <div
                  key={warehouse.id}
                  className="bg-white rounded-lg border border-gray-200 shadow-sm hover:shadow-md transition-shadow"
                >
                  {/* Card Header */}
                  <div className="p-6 border-b border-gray-200">
                    <div className="flex justify-between items-start mb-2">
                      <h3 className="text-lg font-semibold text-gray-900">
                        {warehouse.name}
                      </h3>
                      <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${warehouse.is_active
                        ? 'bg-green-100 text-green-800'
                        : 'bg-red-100 text-red-800'
                        }`}>
                        {warehouse.is_active ? t('warehouses.active') : t('warehouses.inactive')}
                      </span>
                    </div>
                    {warehouse.description && (
                      <p className="text-sm text-gray-600 mb-2">{warehouse.description}</p>
                    )}
                    <div className="text-sm text-gray-500">
                      <div>📍 {warehouse.location || t('warehouses.notSpecified')}</div>
                      <div>🏢 {getOrganizationName(warehouse.organization_id)}</div>
                    </div>
                  </div>

                  {/* Card Stats */}
                  <div className="px-6 py-4 bg-gray-50 border-b border-gray-200">
                    {warehouseSummaries[warehouse.id] ? (
                      <div className="grid grid-cols-2 gap-4">
                        <div>
                          <div className="text-xs text-gray-500">{t('warehouses.inventoryItems')}</div>
                          <div className="text-lg font-semibold text-gray-900">
                            {warehouseSummaries[warehouse.id].total_inventory_items}
                          </div>
                        </div>
                        <div>
                          <div className="text-xs text-gray-500">{t('warehouses.totalStock')}</div>
                          <div className="text-lg font-semibold text-gray-900">
                            {warehouseSummaries[warehouse.id].total_stock_quantity}
                          </div>
                        </div>
                      </div>
                    ) : (
                      <div className="text-sm text-gray-400">{t('warehouses.loadingStats')}</div>
                    )}
                  </div>

                  {/* Card Actions */}
                  <div className="p-4 space-y-2">
                    <button
                      onClick={() => openInventoryModal(warehouse)}
                      className="w-full px-3 py-2 bg-blue-50 text-blue-700 rounded-md hover:bg-blue-100 text-sm font-medium"
                    >
                      📦 {t('warehouses.viewInventory')}
                    </button>
                    <div className="grid grid-cols-2 gap-2">
                      <button
                        onClick={() => openAdjustmentModal(warehouse)}
                        className="px-3 py-2 bg-green-50 text-green-700 rounded-md hover:bg-green-100 text-sm font-medium"
                      >
                        ⚖️ {t('warehouses.adjustStock')}
                      </button>
                      <button
                        onClick={() => openPerformanceModal(warehouse)}
                        className="px-3 py-2 bg-purple-50 text-purple-700 rounded-md hover:bg-purple-100 text-sm font-medium"
                      >
                        ⚡ {t('warehouses.performance')}
                      </button>
                    </div>
                    <div className="grid grid-cols-3 gap-2 pt-2 border-t border-gray-200">
                      <button
                        onClick={() => openEditModal(warehouse)}
                        className="px-2 py-1 text-indigo-600 hover:text-indigo-900 text-xs"
                      >
                        {t('warehouses.edit')}
                      </button>
                      <button
                        onClick={() => handleToggleWarehouseStatus(warehouse)}
                        className={`px-2 py-1 text-xs ${warehouse.is_active
                          ? 'text-orange-600 hover:text-orange-900'
                          : 'text-green-600 hover:text-green-900'
                          }`}
                      >
                        {warehouse.is_active ? t('warehouses.deactivate') : t('warehouses.activate')}
                      </button>
                      <button
                        onClick={() => handleDeleteWarehouse(warehouse)}
                        disabled={warehouseSummaries[warehouse.id]?.total_inventory_items > 0}
                        className={`px-2 py-1 text-xs ${warehouseSummaries[warehouse.id]?.total_inventory_items > 0
                            ? 'text-gray-400 cursor-not-allowed'
                            : 'text-red-600 hover:text-red-900'
                          }`}
                        title={
                          warehouseSummaries[warehouse.id]?.total_inventory_items > 0
                            ? t('warehouses.cannotDeleteWithInventory')
                            : t('warehouses.deleteWarehouse')
                        }
                      >
                        {t('warehouses.delete')}
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </>
      )}

      {/* Aggregated View */}
      {currentView === 'aggregated' && (
        <WarehouseInventoryAggregationView
          organizationId={user.organization_id}
        />
      )}

      {/* Reports View */}
      {currentView === 'reports' && (
        <WarehouseInventoryReporting
          organizationId={user.organization_id}
        />
      )}

      {/* Performance View */}
      {currentView === 'performance' && (
        <div className="space-y-4">
          <div className="bg-white p-4 rounded-lg border border-gray-200">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              {t('warehouses.selectWarehouseForPerformance')}
            </label>
            <WarehouseSelector
              selectedWarehouseId={selectedWarehouse?.id}
              onWarehouseChange={(_, warehouse) => setSelectedWarehouse(warehouse)}
              organizationId={selectedOrganization}
              includeInactive={includeInactive}
              placeholder={t('warehouses.chooseWarehouse')}
            />
          </div>

          {selectedWarehouse && (
            <WarehousePerformanceDashboard
              warehouseId={selectedWarehouse.id}
              warehouse={selectedWarehouse}
            />
          )}
        </div>
      )}

      {/* Modals */}
      <Modal
        isOpen={showCreateModal}
        onClose={() => setShowCreateModal(false)}
        title={t('warehouses.createNewWarehouse')}
        size="lg"
      >
        <WarehouseForm
          onSubmit={handleCreateWarehouse}
          onCancel={() => setShowCreateModal(false)}
          loading={formLoading}
        />
      </Modal>

      <Modal
        isOpen={showEditModal}
        onClose={() => {
          setShowEditModal(false);
          setEditingWarehouse(null);
        }}
        title={t('warehouses.editWarehouse')}
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

      <Modal
        isOpen={showPerformanceModal}
        onClose={() => {
          setShowPerformanceModal(false);
          setSelectedWarehouse(null);
        }}
        title={t('warehouses.warehousePerformance')}
        size="xl"
      >
        {selectedWarehouse && (
          <WarehousePerformanceDashboard
            warehouseId={selectedWarehouse.id}
            warehouse={selectedWarehouse}
          />
        )}
      </Modal>

      <Modal
        isOpen={showInventoryModal}
        onClose={() => {
          setShowInventoryModal(false);
          setSelectedWarehouseForInventory(null);
        }}
        title={`${t('warehouses.inventoryTitle')} - ${selectedWarehouseForInventory?.name}`}
        size="xl"
      >
        {selectedWarehouseForInventory && (
          <WarehouseDetailedView
            warehouseId={selectedWarehouseForInventory.id}
            warehouse={selectedWarehouseForInventory}
          />
        )}
      </Modal>

      <Modal
        isOpen={showAdjustmentModal}
        onClose={() => {
          setShowAdjustmentModal(false);
          setSelectedWarehouseForInventory(null);
        }}
        title={`${t('warehouses.adjustStockTitle')} - ${selectedWarehouseForInventory?.name}`}
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

      <Modal
        isOpen={showTransferModal}
        onClose={() => setShowTransferModal(false)}
        title={t('warehouses.transferInventoryTitle')}
        size="lg"
      >
        <InventoryTransferForm
          onSubmit={handleInventoryTransfer}
          onCancel={() => setShowTransferModal(false)}
        />
      </Modal>

      <Modal
        isOpen={showAddInventoryModal}
        onClose={() => setShowAddInventoryModal(false)}
        title={t('warehouses.addNewInventoryItem')}
        size="lg"
      >
        <InventoryForm
          initialData={{}}
          organizations={organizations}
          warehouses={warehouses}
          parts={parts}
          onSubmit={handleCreateInventory}
          onClose={() => setShowAddInventoryModal(false)}
          isEditMode={false}
        />
      </Modal>
    </div>
  );
};

export default Warehouses;
