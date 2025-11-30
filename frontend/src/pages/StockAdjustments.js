// frontend/src/pages/StockAdjustments.js

import React, { useState, useEffect } from 'react';
import { stockAdjustmentsService } from '../services/stockAdjustmentsService';
import { warehouseService } from '../services/warehouseService';
import StockAdjustmentsList from '../components/StockAdjustmentsList';
import CreateStockAdjustmentModal from '../components/CreateStockAdjustmentModal';
import StockAdjustmentDetailsModal from '../components/StockAdjustmentDetailsModal';

const StockAdjustments = () => {
  const [adjustments, setAdjustments] = useState([]);
  const [warehouses, setWarehouses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [selectedAdjustment, setSelectedAdjustment] = useState(null);
  const [filters, setFilters] = useState({
    warehouse_id: '',
    adjustment_type: '',
    start_date: '',
    end_date: ''
  });

  useEffect(() => {
    loadData();
  }, [filters]);

  const loadData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const [adjustmentsData, warehousesData] = await Promise.all([
        stockAdjustmentsService.list(filters),
        warehouseService.getWarehouses()
      ]);
      
      setAdjustments(adjustmentsData);
      setWarehouses(warehousesData);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateAdjustment = async (adjustmentData) => {
    try {
      await stockAdjustmentsService.create(adjustmentData);
      setShowCreateModal(false);
      loadData();
    } catch (err) {
      throw err;
    }
  };

  const handleViewDetails = async (adjustmentId) => {
    try {
      const details = await stockAdjustmentsService.getById(adjustmentId);
      setSelectedAdjustment(details);
    } catch (err) {
      setError(err.message);
    }
  };

  const handleFilterChange = (field, value) => {
    setFilters(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const clearFilters = () => {
    setFilters({
      warehouse_id: '',
      adjustment_type: '',
      start_date: '',
      end_date: ''
    });
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold">Stock Adjustments</h1>
        <button
          onClick={() => setShowCreateModal(true)}
          className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
        >
          + New Adjustment
        </button>
      </div>

      {/* Filters */}
      <div className="bg-white rounded-lg shadow p-4 mb-6">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Warehouse
            </label>
            <select
              value={filters.warehouse_id}
              onChange={(e) => handleFilterChange('warehouse_id', e.target.value)}
              className="w-full border border-gray-300 rounded px-3 py-2"
            >
              <option value="">All Warehouses</option>
              {warehouses.map(wh => (
                <option key={wh.id} value={wh.id}>{wh.name}</option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Type
            </label>
            <select
              value={filters.adjustment_type}
              onChange={(e) => handleFilterChange('adjustment_type', e.target.value)}
              className="w-full border border-gray-300 rounded px-3 py-2"
            >
              <option value="">All Types</option>
              <option value="stock_take">Stock Take</option>
              <option value="damage">Damage</option>
              <option value="loss">Loss</option>
              <option value="found">Found</option>
              <option value="correction">Correction</option>
              <option value="return">Return</option>
              <option value="other">Other</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Start Date
            </label>
            <input
              type="date"
              value={filters.start_date}
              onChange={(e) => handleFilterChange('start_date', e.target.value)}
              className="w-full border border-gray-300 rounded px-3 py-2"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              End Date
            </label>
            <input
              type="date"
              value={filters.end_date}
              onChange={(e) => handleFilterChange('end_date', e.target.value)}
              className="w-full border border-gray-300 rounded px-3 py-2"
            />
          </div>
        </div>

        <div className="mt-4">
          <button
            onClick={clearFilters}
            className="text-sm text-blue-600 hover:text-blue-800"
          >
            Clear Filters
          </button>
        </div>
      </div>

      {/* Error Message */}
      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
          {error}
        </div>
      )}

      {/* Adjustments List */}
      {loading ? (
        <div className="text-center py-8">Loading...</div>
      ) : (
        <StockAdjustmentsList
          adjustments={adjustments}
          onViewDetails={handleViewDetails}
          onRefresh={loadData}
        />
      )}

      {/* Create Modal */}
      {showCreateModal && (
        <CreateStockAdjustmentModal
          warehouses={warehouses}
          onClose={() => setShowCreateModal(false)}
          onSubmit={handleCreateAdjustment}
        />
      )}

      {/* Details Modal */}
      {selectedAdjustment && (
        <StockAdjustmentDetailsModal
          adjustment={selectedAdjustment}
          onClose={() => setSelectedAdjustment(null)}
        />
      )}
    </div>
  );
};

export default StockAdjustments;
