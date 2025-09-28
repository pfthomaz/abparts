// frontend/src/components/WarehouseDetailedView.js

import React, { useState, useEffect } from 'react';
import WarehouseInventoryView from './WarehouseInventoryView';
import InventoryTransferHistory from './InventoryTransferHistory';
import WarehouseStockAdjustmentHistory from './WarehouseStockAdjustmentHistory';

const WarehouseDetailedView = ({ warehouseId, warehouse, onInventoryRefresh }) => {
  const [activeTab, setActiveTab] = useState('inventory');
  const [refreshInventory, setRefreshInventory] = useState(null);

  // Pass the refresh function up to the parent when it's available
  useEffect(() => {
    if (refreshInventory && onInventoryRefresh) {
      onInventoryRefresh(refreshInventory);
    }
  }, [refreshInventory, onInventoryRefresh]);

  const tabs = [
    { id: 'inventory', label: 'Current Inventory', icon: '📦' },
    { id: 'transfers', label: 'Transfer History', icon: '🔄' },
    { id: 'adjustments', label: 'Stock Adjustments', icon: '⚖️' }
  ];

  const renderTabContent = () => {
    switch (activeTab) {
      case 'inventory':
        return (
          <WarehouseInventoryView
            warehouseId={warehouseId}
            warehouse={warehouse}
            onRefresh={setRefreshInventory}
          />
        );
      case 'transfers':
        return (
          <InventoryTransferHistory
            warehouseId={warehouseId}
            warehouse={warehouse}
          />
        );
      case 'adjustments':
        return (
          <WarehouseStockAdjustmentHistory
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
              {warehouse?.is_active ? 'Active' : 'Inactive'}
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