// frontend/src/components/CreateStockAdjustmentModal.js

import React, { useState, useEffect } from 'react';
import { partsService } from '../services/partsService';
import PartSearchSelector from './PartSearchSelector';
import { useTranslation } from '../hooks/useTranslation';

const CreateStockAdjustmentModal = ({ warehouses, onClose, onSubmit, editMode = false, initialData = null }) => {
  const { t } = useTranslation();
  const [formData, setFormData] = useState({
    warehouse_id: '',
    adjustment_type: 'stock_take',
    reason: '',
    notes: '',
    items: []
  });
  const [parts, setParts] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadParts();
  }, []);

  // Initialize form with existing data when editing
  useEffect(() => {
    if (editMode && initialData) {
      setFormData({
        warehouse_id: initialData.warehouse_id,
        adjustment_type: initialData.adjustment_type,
        reason: initialData.reason || '',
        notes: initialData.notes || '',
        items: initialData.items.map(item => ({
          part_id: item.part_id,
          part_number: item.part_number,
          part_name: item.part_name,
          unit_of_measure: item.unit_of_measure || 'units',
          quantity_before: item.quantity_before,
          quantity_after: item.quantity_after,
          reason: item.reason || ''
        }))
      });
    }
  }, [editMode, initialData]);

  const loadParts = async () => {
    try {
      const data = await partsService.getParts();
      // Handle different response formats
      const partsArray = Array.isArray(data) ? data : (data?.items || data?.data || []);
      setParts(partsArray);
    } catch (err) {
      console.error('Failed to load parts:', err);
      setError(t('stockAdjustments.failedToLoadParts'));
      setParts([]); // Ensure parts is always an array
    }
  };

  const handleAddItem = (part) => {
    // Check if part already added
    if (formData.items.some(item => item.part_id === part.id)) {
      setError(t('stockAdjustments.partAlreadyAdded'));
      return;
    }

    setFormData(prev => ({
      ...prev,
      items: [
        ...prev.items,
        {
          part_id: part.id,
          part_number: part.part_number,
          part_name: part.name,
          unit_of_measure: part.unit_of_measure,
          quantity_after: 0,
          reason: ''
        }
      ]
    }));
    setError(null);
  };

  const handleRemoveItem = (index) => {
    setFormData(prev => ({
      ...prev,
      items: prev.items.filter((_, i) => i !== index)
    }));
  };

  const handleItemChange = (index, field, value) => {
    setFormData(prev => ({
      ...prev,
      items: prev.items.map((item, i) => 
        i === index ? { ...item, [field]: value } : item
      )
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!formData.warehouse_id) {
      setError(t('stockAdjustments.pleaseSelectWarehouse'));
      return;
    }
    
    if (formData.items.length === 0) {
      setError(t('stockAdjustments.pleaseAddOneItem'));
      return;
    }

    // Validate all items have quantity_after
    const invalidItems = formData.items.filter(item => !item.quantity_after && item.quantity_after !== 0);
    if (invalidItems.length > 0) {
      setError(t('stockAdjustments.pleaseSetQuantity'));
      return;
    }

    setLoading(true);
    setError(null);

    try {
      // Format data for API
      const submitData = {
        warehouse_id: formData.warehouse_id,
        adjustment_type: formData.adjustment_type,
        reason: formData.reason || null,
        notes: formData.notes || null,
        items: formData.items.map(item => {
          const itemData = {
            part_id: item.part_id,
            quantity_after: parseFloat(item.quantity_after),
            reason: item.reason || null
          };
          // Only include quantity_before in edit mode
          if (editMode && item.quantity_before !== undefined) {
            itemData.quantity_before = parseFloat(item.quantity_before);
          }
          return itemData;
        })
      };

      await onSubmit(submitData);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg max-w-4xl w-full max-h-[90vh] overflow-y-auto">
        <div className="p-6">
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-2xl font-bold">{editMode ? t('stockAdjustments.editAdjustment') : t('stockAdjustments.createAdjustment')}</h2>
            <button
              onClick={onClose}
              className="text-gray-500 hover:text-gray-700"
            >
              ✕
            </button>
          </div>

          {error && (
            <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit}>
            {/* Basic Info */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  {t('stockAdjustments.warehouse')} *
                </label>
                <select
                  value={formData.warehouse_id}
                  onChange={(e) => setFormData(prev => ({ ...prev, warehouse_id: e.target.value }))}
                  className="w-full border border-gray-300 rounded px-3 py-2"
                  required
                >
                  <option value="">{t('stockAdjustments.selectWarehouse')}</option>
                  {warehouses.map(wh => (
                    <option key={wh.id} value={wh.id}>{wh.name}</option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  {t('stockAdjustments.adjustmentType')} *
                </label>
                <select
                  value={formData.adjustment_type}
                  onChange={(e) => setFormData(prev => ({ ...prev, adjustment_type: e.target.value }))}
                  className="w-full border border-gray-300 rounded px-3 py-2"
                  required
                >
                  <option value="stock_take">{t('stockAdjustments.types.stockTake')}</option>
                  <option value="damage">{t('stockAdjustments.types.damage')}</option>
                  <option value="loss">{t('stockAdjustments.types.loss')}</option>
                  <option value="found">{t('stockAdjustments.types.found')}</option>
                  <option value="correction">{t('stockAdjustments.types.correction')}</option>
                  <option value="return">{t('stockAdjustments.types.return')}</option>
                  <option value="other">{t('stockAdjustments.types.other')}</option>
                </select>
              </div>
            </div>

            <div className="mb-6">
              <label className="block text-sm font-medium text-gray-700 mb-1">
                {t('stockAdjustments.reason')}
              </label>
              <input
                type="text"
                value={formData.reason}
                onChange={(e) => setFormData(prev => ({ ...prev, reason: e.target.value }))}
                className="w-full border border-gray-300 rounded px-3 py-2"
                placeholder={t('stockAdjustments.overallReasonPlaceholder')}
              />
            </div>

            <div className="mb-6">
              <label className="block text-sm font-medium text-gray-700 mb-1">
                {t('stockAdjustments.notes')}
              </label>
              <textarea
                value={formData.notes}
                onChange={(e) => setFormData(prev => ({ ...prev, notes: e.target.value }))}
                className="w-full border border-gray-300 rounded px-3 py-2"
                rows="3"
                placeholder={t('stockAdjustments.additionalNotes')}
              />
            </div>

            {/* Items Section */}
            <div className="mb-6">
              <div className="flex justify-between items-center mb-3">
                <h3 className="text-lg font-semibold">{t('stockAdjustments.itemsToAdjust')} *</h3>
              </div>

              {/* Add Part */}
              <div className="mb-4">
                <PartSearchSelector
                  parts={parts}
                  onSelect={handleAddItem}
                  placeholder={t('stockAdjustments.searchAndAddParts')}
                />
              </div>

              {/* Items List */}
              {formData.items.length === 0 ? (
                <div className="text-center py-8 text-gray-500 border-2 border-dashed border-gray-300 rounded">
                  {t('stockAdjustments.noItemsAdded')}
                </div>
              ) : (
                <div className="space-y-3">
                  {formData.items.map((item, index) => (
                    <div key={index} className="border border-gray-300 rounded p-4">
                      <div className="flex justify-between items-start mb-3">
                        <div>
                          <div className="font-medium">{item.part_number}</div>
                          <div className="text-sm text-gray-600">{item.part_name}</div>
                        </div>
                        <button
                          type="button"
                          onClick={() => handleRemoveItem(index)}
                          className="text-red-600 hover:text-red-800"
                        >
                          {t('common.remove')}
                        </button>
                      </div>

                      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-1">
                            {t('stockAdjustments.newQuantity')} *
                          </label>
                          <input
                            type="number"
                            step={item.unit_of_measure === 'units' ? '1' : '0.01'}
                            min="0"
                            value={item.quantity_after}
                            onChange={(e) => {
                              const value = e.target.value;
                              // For consumables, ensure integer values
                              if (item.unit_of_measure === 'units') {
                                handleItemChange(index, 'quantity_after', value ? Math.floor(parseFloat(value)) : 0);
                              } else {
                                handleItemChange(index, 'quantity_after', value);
                              }
                            }}
                            className="w-full border border-gray-300 rounded px-3 py-2"
                            required
                          />
                        </div>

                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-1">
                            {t('stockAdjustments.itemReason')}
                          </label>
                          <input
                            type="text"
                            value={item.reason}
                            onChange={(e) => handleItemChange(index, 'reason', e.target.value)}
                            className="w-full border border-gray-300 rounded px-3 py-2"
                            placeholder={t('stockAdjustments.specificReasonPlaceholder')}
                          />
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Actions */}
            <div className="flex justify-end gap-3">
              <button
                type="button"
                onClick={onClose}
                className="px-4 py-2 border border-gray-300 rounded hover:bg-gray-50"
                disabled={loading}
              >
                {t('common.cancel')}
              </button>
              <button
                type="submit"
                className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:bg-gray-400"
                disabled={loading}
              >
                {loading ? (editMode ? t('stockAdjustments.updating') : t('stockAdjustments.creating')) : (editMode ? t('stockAdjustments.updateAdjustment') : t('stockAdjustments.createAdjustment'))}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

export default CreateStockAdjustmentModal;
