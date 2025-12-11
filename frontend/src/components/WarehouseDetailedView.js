// frontend/src/components/WarehouseDetailedView.js

import React, { useState, useEffect, useCallback } from 'react';
import { useTranslation } from '../hooks/useTranslation';
import WarehouseInventoryView from './WarehouseInventoryView';
import InventoryTransferHistory from './InventoryTransferHistory';
import WarehouseStockAdjustmentHistory from './WarehouseStockAdjustmentHistory';
import StockResetTab from './StockResetTab';

const WarehouseDetailedView = ({ warehouseId, warehouse, onInventoryRefresh }) => {
  const { t } = useTranslation();
  const [activeTab, setActiveTab] = useState('inventory');
  const [refreshTrigger, setRefreshTrigger] = useState(0);
  const inventoryRefreshFnRef = React.useRef(null);
  
  // Use a callback ref instead of state to avoid re-render issues
  const handleRefreshCallback = useCallback((refreshFn) => {
    inventoryRefreshFnRef.current = refreshFn;
    if (onInventoryRefresh) {
      onInventoryRefresh(refreshFn);
    }
  }, [onInventoryRefresh]);

  const tabs = [
    { id: 'inventory', label: t('warehouses.currentInventory'), icon: '📦' },
    { id: 'adjustments', label: t('warehouses.stockAdjustments'), icon: '⚖️' },
    { id: 'transfers', label: t('warehouses.transferHistory'), icon: '↔️' }
  ];

  const renderTabContent = () => {
    switch (activeTab) {
      case 'inventory':
        return (
          <WarehouseInventoryView
            key={`inventory-${refreshTrigger}`}
            warehouseId={warehouseId}
            warehouse={warehouse}
            onRefresh={handleRefreshCallback}
          />
        );
      case 'adjustments':
        return (
          <StockResetTab
            warehouse={warehouse}
            onSuccess={() => {
              // Trigger inventory refresh
              if (inventoryRefreshFnRef.current) {
                inventoryRefreshFnRef.current();
              }
              // Increment refresh trigger to force re-render
              setRefreshTrigger(prev => prev + 1);
              // Switch to inventory tab to show updated data
              setActiveTab('inventory');
            }}
          />
        );
      case 'transfers':
        return (
          <InventoryTransferHistory
            warehouseId={warehouseId}
            warehouse={warehouse}
          />
        );
      default:
        return null;
    }
  };

  return (
    <div className="space-y-6">
      {/* Warehouse Header */}
      <div className="bg-white p-6 rounded-lg shadow-md border border-gray-200">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold text-gray-900">{warehouse?.name}</h2>
            {warehouse?.location && (
              <p className="text-gray-600 mt-1">📍 {warehouse.location}</p>
            )}
            {warehouse?.description && (
              <p className="text-gray-500 mt-2">{warehouse.description}</p>
            )}
          </div>
          <div className="text-right">
            <div className={`inline-flex px-3 py-1 rounded-full text-sm font-medium ${warehouse?.is_active
              ? 'bg-green-100 text-green-800'
              : 'bg-red-100 text-red-800'
              }`}>
              {warehouse?.is_active ? t('warehouses.active') : t('warehouses.inactive')}
            </div>
          </div>
        </div>
      </div>

      {/* Tab Navigation */}
      <div className="bg-white rounded-lg shadow-md border border-gray-200">
        <div className="border-b border-gray-200">
          <nav className="-mb-px flex space-x-8 px-6" aria-label="Tabs">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`py-4 px-1 border-b-2 font-medium text-sm whitespace-nowrap ${activeTab === tab.id
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

        {/* Tab Content */}
        <div className="p-6">
          {renderTabContent()}
        </div>
      </div>
    </div>
  );
};

export default WarehouseDetailedView;