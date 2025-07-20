// frontend/src/pages/InventoryWorkflows.js

import React, { useState, useEffect } from 'react';
import { inventoryWorkflowService } from '../services/inventoryWorkflowService';
import { organizationsService } from '../services/organizationsService';
import StocktakeList from '../components/StocktakeList';
import StocktakeForm from '../components/StocktakeForm';
import InventoryAdjustmentForm from '../components/InventoryAdjustmentForm';
import InventoryAlertsList from '../components/InventoryAlertsList';
import InventoryAnalytics from '../components/InventoryAnalytics';
import Modal from '../components/Modal';
import { useAuth } from '../AuthContext';

const InventoryWorkflows = () => {
  const { user } = useAuth();
  const [activeTab, setActiveTab] = useState('stocktakes');
  const [stocktakes, setStocktakes] = useState([]);
  const [alerts, setAlerts] = useState([]);
  const [organizations, setOrganizations] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [showStocktakeModal, setShowStocktakeModal] = useState(false);
  const [showAdjustmentModal, setShowAdjustmentModal] = useState(false);
  const [selectedStocktake, setSelectedStocktake] = useState(null);

  // Filters
  const [filters, setFilters] = useState({
    organization_id: user?.role === 'super_admin' ? '' : user?.organization_id || '',
    warehouse_id: '',
    status: '',
    alert_type: '',
    severity: ''
  });

  useEffect(() => {
    fetchData();
    if (user?.role === 'super_admin') {
      fetchOrganizations();
    }
  }, [activeTab, filters]);

  const fetchData = async () => {
    setLoading(true);
    setError('');
    try {
      if (activeTab === 'stocktakes') {
        const data = await inventoryWorkflowService.getStocktakes(filters);
        setStocktakes(data);
      } else if (activeTab === 'alerts') {
        const data = await inventoryWorkflowService.getInventoryAlerts({
          ...filters,
          active_only: true
        });
        setAlerts(data);
      }
    } catch (err) {
      setError(err.message || 'Failed to fetch data');
    } finally {
      setLoading(false);
    }
  };

  const fetchOrganizations = async () => {
    try {
      const data = await organizationsService.getOrganizations();
      setOrganizations(data);
    } catch (err) {
      console.error('Failed to fetch organizations:', err);
    }
  };

  const handleCreateStocktake = async (stocktakeData) => {
    try {
      await inventoryWorkflowService.createStocktake(stocktakeData);
      setShowStocktakeModal(false);
      fetchData();
    } catch (err) {
      setError(err.message || 'Failed to create stocktake');
    }
  };

  const handleCreateAdjustment = async (adjustmentData) => {
    try {
      await inventoryWorkflowService.createInventoryAdjustment(adjustmentData);
      setShowAdjustmentModal(false);
      // Refresh alerts as adjustments might trigger new ones
      if (activeTab === 'alerts') {
        fetchData();
      }
    } catch (err) {
      setError(err.message || 'Failed to create adjustment');
    }
  };

  const handleGenerateAlerts = async () => {
    try {
      setLoading(true);
      const organizationId = user?.role === 'super_admin' ? filters.organization_id || null : user?.organization_id;
      await inventoryWorkflowService.generateInventoryAlerts(organizationId);
      if (activeTab === 'alerts') {
        fetchData();
      }
    } catch (err) {
      setError(err.message || 'Failed to generate alerts');
    } finally {
      setLoading(false);
    }
  };

  const tabs = [
    { id: 'stocktakes', name: 'Stocktakes', icon: '📋' },
    { id: 'adjustments', name: 'Adjustments', icon: '⚖️' },
    { id: 'alerts', name: 'Alerts', icon: '🚨' },
    { id: 'analytics', name: 'Analytics', icon: '📊' }
  ];

  const canCreateStocktake = user?.role === 'admin' || user?.role === 'super_admin';
  const canCreateAdjustment = user?.role === 'admin' || user?.role === 'super_admin';

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold text-gray-800">Inventory Workflows</h1>
        <div className="flex space-x-2">
          {activeTab === 'stocktakes' && canCreateStocktake && (
            <button
              onClick={() => setShowStocktakeModal(true)}
              className="bg-blue-500 text-white px-4 py-2 rounded-md hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
            >
              New Stocktake
            </button>
          )}
          {activeTab === 'adjustments' && canCreateAdjustment && (
            <button
              onClick={() => setShowAdjustmentModal(true)}
              className="bg-green-500 text-white px-4 py-2 rounded-md hover:bg-green-600 focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2"
            >
              New Adjustment
            </button>
          )}
          {activeTab === 'alerts' && (user?.role === 'admin' || user?.role === 'super_admin') && (
            <button
              onClick={handleGenerateAlerts}
              disabled={loading}
              className="bg-orange-500 text-white px-4 py-2 rounded-md hover:bg-orange-600 focus:outline-none focus:ring-2 focus:ring-orange-500 focus:ring-offset-2 disabled:opacity-50"
            >
              Generate Alerts
            </button>
          )}
        </div>
      </div>

      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded" role="alert">
          <strong className="font-bold">Error: </strong>
          <span>{error}</span>
        </div>
      )}

      {/* Tab Navigation */}
      <div className="border-b border-gray-200">
        <nav className="-mb-px flex space-x-8">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`py-2 px-1 border-b-2 font-medium text-sm ${activeTab === tab.id
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
            >
              <span className="mr-2">{tab.icon}</span>
              {tab.name}
            </button>
          ))}
        </nav>
      </div>

      {/* Filters */}
      <div className="bg-white p-4 rounded-lg shadow-md">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {user?.role === 'super_admin' && (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Organization
              </label>
              <select
                value={filters.organization_id}
                onChange={(e) => setFilters({ ...filters, organization_id: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="">All Organizations</option>
                {organizations.map((org) => (
                  <option key={org.id} value={org.id}>
                    {org.name}
                  </option>
                ))}
              </select>
            </div>
          )}

          {activeTab === 'stocktakes' && (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Status
              </label>
              <select
                value={filters.status}
                onChange={(e) => setFilters({ ...filters, status: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="">All Statuses</option>
                <option value="planned">Planned</option>
                <option value="in_progress">In Progress</option>
                <option value="completed">Completed</option>
                <option value="cancelled">Cancelled</option>
              </select>
            </div>
          )}

          {activeTab === 'alerts' && (
            <>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Alert Type
                </label>
                <select
                  value={filters.alert_type}
                  onChange={(e) => setFilters({ ...filters, alert_type: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  <option value="">All Types</option>
                  <option value="low_stock">Low Stock</option>
                  <option value="stockout">Stockout</option>
                  <option value="excess">Excess</option>
                  <option value="discrepancy">Discrepancy</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Severity
                </label>
                <select
                  value={filters.severity}
                  onChange={(e) => setFilters({ ...filters, severity: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  <option value="">All Severities</option>
                  <option value="low">Low</option>
                  <option value="medium">Medium</option>
                  <option value="high">High</option>
                  <option value="critical">Critical</option>
                </select>
              </div>
            </>
          )}
        </div>
      </div>

      {/* Tab Content */}
      <div className="bg-white rounded-lg shadow-md">
        {loading ? (
          <div className="p-8 text-center">
            <p className="text-gray-600">Loading...</p>
          </div>
        ) : (
          <>
            {activeTab === 'stocktakes' && (
              <StocktakeList
                stocktakes={stocktakes}
                onEdit={setSelectedStocktake}
                onRefresh={fetchData}
              />
            )}
            {activeTab === 'adjustments' && (
              <div className="p-6">
                <p className="text-gray-600">Adjustment history will be displayed here.</p>
              </div>
            )}
            {activeTab === 'alerts' && (
              <InventoryAlertsList
                alerts={alerts}
                onRefresh={fetchData}
              />
            )}
            {activeTab === 'analytics' && (
              <InventoryAnalytics />
            )}
          </>
        )}
      </div>

      {/* Modals */}
      {showStocktakeModal && (
        <Modal
          isOpen={showStocktakeModal}
          onClose={() => setShowStocktakeModal(false)}
          title="Create New Stocktake"
        >
          <StocktakeForm
            onSubmit={handleCreateStocktake}
            onCancel={() => setShowStocktakeModal(false)}
          />
        </Modal>
      )}

      {showAdjustmentModal && (
        <Modal
          isOpen={showAdjustmentModal}
          onClose={() => setShowAdjustmentModal(false)}
          title="Create Inventory Adjustment"
        >
          <InventoryAdjustmentForm
            onSubmit={handleCreateAdjustment}
            onCancel={() => setShowAdjustmentModal(false)}
          />
        </Modal>
      )}
    </div>
  );
};

export default InventoryWorkflows;