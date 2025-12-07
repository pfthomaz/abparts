// frontend/src/pages/StockAdjustments.js

import React, { useState, useEffect } from 'react';
import { stockAdjustmentsService } from '../services/stockAdjustmentsService';
import { warehouseService } from '../services/warehouseService';
import StockAdjustmentsList from '../components/StockAdjustmentsList';
import CreateStockAdjustmentModal from '../components/CreateStockAdjustmentModal';
import StockAdjustmentDetailsModal from '../components/StockAdjustmentDetailsModal';
import { useTranslation } from '../hooks/useTranslation';

const StockAdjustments = () => {
  const { t } = useTranslation();
  const [adjustments, setAdjustments] = useState([]);
  const [warehouses, setWarehouses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [selectedAdjustment, setSelectedAdjustment] = useState(null);
  const [editingAdjustment, setEditingAdjustment] = useState(null);
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

  const handleSaveAdjustment = async (adjustmentData) => {
    try {
      if (editingAdjustment) {
        // Update existing adjustment
        await stockAdjustmentsService.update(editingAdjustment.id, adjustmentData);
        setEditingAdjustment(null);
        alert(t('stockAdjustments.updateSuccess'));
        window.location.reload();
      } else {
        // Create new adjustment
        await stockAdjustmentsService.create(adjustmentData);
        setShowCreateModal(false);
        loadData();
      }
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

  const handleEdit = async (adjustment) => {
    try {
      // Fetch full details including items
      const details = await stockAdjustmentsService.getById(adjustment.id);
      setEditingAdjustment(details);
    } catch (err) {
      alert(t('stockAdjustments.loadDetailsFailed') + ': ' + (err.response?.data?.detail || err.message));
    }
  };

  const handleDelete = async (adjustment) => {
    if (!window.confirm(t('stockAdjustments.confirmDelete', { 
      date: adjustment.adjustment_date, 
      warehouse: adjustment.warehouse_name, 
      type: adjustment.adjustment_type 
    }))) {
      return;
    }

    try {
      await stockAdjustmentsService.delete(adjustment.id);
      alert(t('stockAdjustments.deleteSuccess'));
      window.location.reload();
    } catch (err) {
      alert(t('stockAdjustments.deleteFailed') + ': ' + (err.response?.data?.detail || err.message));
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
        <h1 className="text-3xl font-bold">{t('stockAdjustments.title')}</h1>
        <button
          onClick={() => setShowCreateModal(true)}
          className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
        >
          + {t('stockAdjustments.newAdjustment')}
        </button>
      </div>

      {/* Filters */}
      <div className="bg-white rounded-lg shadow p-4 mb-6">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              {t('stockAdjustments.warehouse')}
            </label>
            <select
              value={filters.warehouse_id}
              onChange={(e) => handleFilterChange('warehouse_id', e.target.value)}
              className="w-full border border-gray-300 rounded px-3 py-2"
            >
              <option value="">{t('stockAdjustments.allWarehouses')}</option>
              {warehouses.map(wh => (
                <option key={wh.id} value={wh.id}>{wh.name}</option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              {t('stockAdjustments.type')}
            </label>
            <select
              value={filters.adjustment_type}
              onChange={(e) => handleFilterChange('adjustment_type', e.target.value)}
              className="w-full border border-gray-300 rounded px-3 py-2"
            >
              <option value="">{t('stockAdjustments.allTypes')}</option>
              <option value="stock_take">{t('stockAdjustments.types.stockTake')}</option>
              <option value="damage">{t('stockAdjustments.types.damage')}</option>
              <option value="loss">{t('stockAdjustments.types.loss')}</option>
              <option value="found">{t('stockAdjustments.types.found')}</option>
              <option value="correction">{t('stockAdjustments.types.correction')}</option>
              <option value="return">{t('stockAdjustments.types.return')}</option>
              <option value="other">{t('stockAdjustments.types.other')}</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              {t('stockAdjustments.startDate')}
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
              {t('stockAdjustments.endDate')}
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
            {t('common.clearFilters')}
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
        <div className="text-center py-8">{t('common.loading')}</div>
      ) : (
        <StockAdjustmentsList
          adjustments={adjustments}
          onViewDetails={handleViewDetails}
          onEdit={handleEdit}
          onDelete={handleDelete}
          onRefresh={loadData}
        />
      )}

      {/* Create/Edit Modal */}
      {(showCreateModal || editingAdjustment) && (
        <CreateStockAdjustmentModal
          warehouses={warehouses}
          onClose={() => {
            setShowCreateModal(false);
            setEditingAdjustment(null);
          }}
          onSubmit={handleSaveAdjustment}
          editMode={!!editingAdjustment}
          initialData={editingAdjustment}
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
