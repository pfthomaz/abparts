// frontend/src/components/WarehouseStockAdjustmentForm.js

import React, { useState, useEffect } from 'react';
import { partsService } from '../services/partsService';
import { inventoryService } from '../services/inventoryService';
import { useTranslation } from '../hooks/useTranslation';

const WarehouseStockAdjustmentForm = ({ warehouseId, warehouse, onSubmit, onCancel }) => {
  const { t } = useTranslation();
  const [formData, setFormData] = useState({
    part_id: '',
    quantity_change: '',
    reason: '',
    notes: ''
  });
  const [parts, setParts] = useState([]);
  const [warehouseInventory, setWarehouseInventory] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    if (warehouseId) {
      fetchParts();
      fetchWarehouseInventory();
    }
  }, [warehouseId]);

  const fetchParts = async () => {
    try {
      const response = await partsService.getPartsWithInventory({ limit: 1000 });
      // Handle paginated response format
      const partsData = response?.items || response || [];
      setParts(Array.isArray(partsData) ? partsData : []);
    } catch (err) {
      setError(t('warehouses.failedToFetchParts'));
      console.error('Failed to fetch parts:', err);
      setParts([]); // Ensure parts is always an array
    }
  };

  const fetchWarehouseInventory = async () => {
    try {
      const data = await inventoryService.getWarehouseInventory(warehouseId);
      setWarehouseInventory(data);
    } catch (err) {
      console.error('Failed to fetch warehouse inventory:', err);
      setWarehouseInventory([]);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    const quantityChange = parseFloat(formData.quantity_change);
    if (isNaN(quantityChange)) {
      setError(t('warehouses.quantityMustBeValid'));
      setLoading(false);
      return;
    }

    // Check if negative adjustment would result in negative stock
    if (quantityChange < 0) {
      const currentStock = getCurrentStock(formData.part_id);
      if (Math.abs(quantityChange) > currentStock) {
        setError(t('warehouses.cannotReduceStock', { quantity: Math.abs(quantityChange), currentStock }));
        setLoading(false);
        return;
      }
    }

    try {
      const submitData = {
        ...formData,
        quantity_change: quantityChange
      };

      await onSubmit(submitData);

      // Immediately update local state to reflect the change
      setWarehouseInventory(prevInventory =>
        prevInventory.map(item =>
          item.part_id === formData.part_id
            ? { ...item, current_stock: (parseFloat(item.current_stock) + quantityChange).toString() }
            : item
        )
      );

      // Also refresh from server to ensure consistency
      setTimeout(async () => {
        await fetchWarehouseInventory();
      }, 500);

    } catch (err) {
      setError(err.message || t('warehouses.failedToCreateAdjustment'));
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const getCurrentStock = (partId) => {
    const inventoryItem = warehouseInventory.find(item => item.part_id === partId);
    return inventoryItem ? parseFloat(inventoryItem.current_stock) : 0;
  };

  const getPartDetails = (partId) => {
    if (!Array.isArray(parts)) {
      return null;
    }
    return parts.find(p => p.id === partId);
  };

  const filteredParts = Array.isArray(parts) ? parts.filter(part =>
    part.part_number.toLowerCase().includes(searchTerm.toLowerCase()) ||
    part.name.toLowerCase().includes(searchTerm.toLowerCase())
  ) : [];

  const reasonOptions = [
    { key: 'stocktakeAdjustment', value: 'Stocktake adjustment' },
    { key: 'damagedGoods', value: 'Damaged goods' },
    { key: 'expiredItems', value: 'Expired items' },
    { key: 'foundItems', value: 'Found items' },
    { key: 'lostItems', value: 'Lost items' },
    { key: 'transferCorrection', value: 'Transfer correction' },
    { key: 'systemErrorCorrection', value: 'System error correction' },
    { key: 'initialStockEntry', value: 'Initial stock entry' },
    { key: 'returnToVendor', value: 'Return to vendor' },
    { key: 'customerReturnResalable', value: 'Customer return - resalable' },
    { key: 'customerReturnDamaged', value: 'Customer return - damaged' },
    { key: 'other', value: 'Other' }
  ];

  return (
    <div className="space-y-4">
      <div className="bg-blue-50 p-4 rounded-lg">
        <h3 className="text-lg font-medium text-blue-900">
          {t('warehouses.stockAdjustmentForm.title')}
        </h3>
        <p className="text-sm text-blue-700 mt-1">
          {t('warehouses.warehouse')}: {warehouse?.name || t('warehouses.unknownWarehouse')}
          {warehouse?.location && ` - ${warehouse.location}`}
        </p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-4">
        {error && (
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded" role="alert">
            <span>{error}</span>
          </div>
        )}

        <div>
          <label htmlFor="part_search" className="block text-sm font-medium text-gray-700 mb-1">
            {t('warehouses.stockAdjustmentForm.searchParts')}
          </label>
          <input
            type="text"
            id="part_search"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            placeholder={t('warehouses.stockAdjustmentForm.searchPlaceholder')}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        </div>

        <div>
          <label htmlFor="part_id" className="block text-sm font-medium text-gray-700 mb-1">
            {t('warehouses.stockAdjustmentForm.part')} *
          </label>
          <select
            id="part_id"
            name="part_id"
            value={formData.part_id}
            onChange={handleChange}
            required
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            size={Math.min(filteredParts.length + 1, 8)}
          >
            <option value="">{t('warehouses.stockAdjustmentForm.selectPart')}</option>
            {filteredParts.map((part) => {
              const currentStock = getCurrentStock(part.id);
              return (
                <option key={part.id} value={part.id}>
                  {part.part_number} - {part.name} ({t('warehouses.stockAdjustmentForm.current')}: {currentStock} {part.unit_of_measure})
                </option>
              );
            })}
          </select>
        </div>

        {formData.part_id && (
          <div className="bg-gray-50 p-3 rounded-md">
            <p className="text-sm text-gray-700">
              <span className="font-medium">{t('warehouses.stockAdjustmentForm.currentStock')}:</span> {getCurrentStock(formData.part_id)} {getPartDetails(formData.part_id)?.unit_of_measure}
            </p>
          </div>
        )}

        <div>
          <label htmlFor="quantity_change" className="block text-sm font-medium text-gray-700 mb-1">
            {t('warehouses.stockAdjustmentForm.quantityChange')} *
          </label>
          <input
            type="number"
            step="0.001"
            id="quantity_change"
            name="quantity_change"
            value={formData.quantity_change}
            onChange={handleChange}
            required
            placeholder={t('warehouses.stockAdjustmentForm.quantityPlaceholder')}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
          <p className="text-xs text-gray-500 mt-1">
            {t('warehouses.stockAdjustmentForm.quantityHint')}
          </p>
          {formData.part_id && formData.quantity_change && (
            <p className="text-xs text-blue-600 mt-1">
              {t('warehouses.stockAdjustmentForm.newStockLevel')}: {getCurrentStock(formData.part_id) + parseFloat(formData.quantity_change || 0)} {getPartDetails(formData.part_id)?.unit_of_measure}
            </p>
          )}
        </div>

        <div>
          <label htmlFor="reason" className="block text-sm font-medium text-gray-700 mb-1">
            {t('warehouses.stockAdjustmentForm.reason')} *
          </label>
          <select
            id="reason"
            name="reason"
            value={formData.reason}
            onChange={handleChange}
            required
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="">{t('warehouses.stockAdjustmentForm.selectReason')}</option>
            {reasonOptions.map((reason) => (
              <option key={reason.key} value={reason.value}>
                {t(`warehouses.stockAdjustmentForm.reasons.${reason.key}`)}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label htmlFor="notes" className="block text-sm font-medium text-gray-700 mb-1">
            {t('warehouses.stockAdjustmentForm.notes')}
          </label>
          <textarea
            id="notes"
            name="notes"
            value={formData.notes}
            onChange={handleChange}
            rows={3}
            placeholder={t('warehouses.stockAdjustmentForm.notesPlaceholder')}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        </div>

        <div className="flex justify-end space-x-3 pt-4">
          <button
            type="button"
            onClick={onCancel}
            className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 border border-gray-300 rounded-md hover:bg-gray-200 focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-offset-2"
          >
            {t('common.cancel')}
          </button>
          <button
            type="submit"
            disabled={loading}
            className="px-4 py-2 text-sm font-medium text-white bg-green-600 border border-transparent rounded-md hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2 disabled:opacity-50"
          >
            {loading ? t('warehouses.stockAdjustmentForm.creatingAdjustment') : t('warehouses.stockAdjustmentForm.createAdjustment')}
          </button>
        </div>
      </form>
    </div>
  );
};

export default WarehouseStockAdjustmentForm;