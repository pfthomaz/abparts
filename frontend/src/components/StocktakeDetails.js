// frontend/src/components/StocktakeDetails.js

import React, { useState, useEffect } from 'react';
import { inventoryWorkflowService } from '../services/inventoryWorkflowService';

const StocktakeDetails = ({ stocktake, onComplete, onClose, loading: parentLoading }) => {
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [editingItems, setEditingItems] = useState({});
  const [showCompleteConfirm, setShowCompleteConfirm] = useState(false);
  const [applyAdjustments, setApplyAdjustments] = useState(false);

  useEffect(() => {
    if (stocktake?.items) {
      setItems(stocktake.items);
    }
  }, [stocktake]);

  const handleItemUpdate = async (itemId, actualQuantity, notes = '') => {
    try {
      setLoading(true);
      await inventoryWorkflowService.updateStocktakeItem(itemId, {
        actual_quantity: parseFloat(actualQuantity),
        notes
      });

      // Update local state
      setItems(prevItems =>
        prevItems.map(item =>
          item.id === itemId
            ? {
              ...item,
              actual_quantity: parseFloat(actualQuantity),
              notes,
              discrepancy: parseFloat(actualQuantity) - item.expected_quantity,
              discrepancy_percentage: item.expected_quantity > 0
                ? ((parseFloat(actualQuantity) - item.expected_quantity) / item.expected_quantity) * 100
                : 0
            }
            : item
        )
      );

      // Remove from editing state
      setEditingItems(prev => {
        const newState = { ...prev };
        delete newState[itemId];
        return newState;
      });
    } catch (err) {
      setError(err.message || 'Failed to update item');
    } finally {
      setLoading(false);
    }
  };

  const handleBatchUpdate = async () => {
    try {
      setLoading(true);
      const updates = Object.entries(editingItems).map(([itemId, data]) => ({
        item_id: itemId,
        actual_quantity: parseFloat(data.actual_quantity),
        notes: data.notes || ''
      }));

      if (updates.length > 0) {
        await inventoryWorkflowService.batchUpdateStocktakeItems(stocktake.id, updates);

        // Update local state
        setItems(prevItems =>
          prevItems.map(item => {
            const update = updates.find(u => u.item_id === item.id);
            if (update) {
              return {
                ...item,
                actual_quantity: update.actual_quantity,
                notes: update.notes,
                discrepancy: update.actual_quantity - item.expected_quantity,
                discrepancy_percentage: item.expected_quantity > 0
                  ? ((update.actual_quantity - item.expected_quantity) / item.expected_quantity) * 100
                  : 0
              };
            }
            return item;
          })
        );

        setEditingItems({});
      }
    } catch (err) {
      setError(err.message || 'Failed to update items');
    } finally {
      setLoading(false);
    }
  };

  const handleEditItem = (item) => {
    setEditingItems(prev => ({
      ...prev,
      [item.id]: {
        actual_quantity: item.actual_quantity?.toString() || '',
        notes: item.notes || ''
      }
    }));
  };

  const handleCancelEdit = (itemId) => {
    setEditingItems(prev => {
      const newState = { ...prev };
      delete newState[itemId];
      return newState;
    });
  };

  const handleEditChange = (itemId, field, value) => {
    setEditingItems(prev => ({
      ...prev,
      [itemId]: {
        ...prev[itemId],
        [field]: value
      }
    }));
  };

  const getDiscrepancyBadge = (discrepancy, discrepancyPercentage) => {
    if (discrepancy === null || discrepancy === undefined) return null;

    if (discrepancy === 0) {
      return (
        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
          ✓ Match
        </span>
      );
    }

    const isSignificant = Math.abs(discrepancyPercentage) > 10;
    const bgColor = isSignificant ? 'bg-red-100' : 'bg-yellow-100';
    const textColor = isSignificant ? 'text-red-800' : 'text-yellow-800';

    return (
      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${bgColor} ${textColor}`}>
        {discrepancy > 0 ? '+' : ''}{discrepancy.toFixed(3)} ({discrepancyPercentage.toFixed(1)}%)
      </span>
    );
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const canEdit = stocktake.status === 'planned' || stocktake.status === 'in_progress';
  const canComplete = stocktake.status === 'in_progress' && items.every(item => item.actual_quantity !== null);
  const hasDiscrepancies = items.some(item => item.discrepancy !== null && item.discrepancy !== 0);

  return (
    <div className="space-y-6">
      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded" role="alert">
          <span>{error}</span>
        </div>
      )}

      {/* Stocktake Summary */}
      <div className="bg-gray-50 p-4 rounded-lg">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div>
            <div className="text-sm font-medium text-gray-500">Status</div>
            <div className="text-lg font-semibold text-gray-900 capitalize">
              {stocktake.status.replace('_', ' ')}
            </div>
          </div>
          <div>
            <div className="text-sm font-medium text-gray-500">Progress</div>
            <div className="text-lg font-semibold text-gray-900">
              {stocktake.items_counted} / {stocktake.total_items}
            </div>
          </div>
          <div>
            <div className="text-sm font-medium text-gray-500">Discrepancies</div>
            <div className="text-lg font-semibold text-gray-900">
              {stocktake.discrepancy_count}
            </div>
          </div>
          <div>
            <div className="text-sm font-medium text-gray-500">Scheduled</div>
            <div className="text-lg font-semibold text-gray-900">
              {formatDate(stocktake.scheduled_date)}
            </div>
          </div>
        </div>
      </div>

      {/* Action Buttons */}
      {canEdit && editingItems && Object.keys(editingItems).length > 0 && (
        <div className="flex justify-end space-x-3">
          <button
            onClick={() => setEditingItems({})}
            className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 border border-gray-300 rounded-md hover:bg-gray-200"
          >
            Cancel All Edits
          </button>
          <button
            onClick={handleBatchUpdate}
            disabled={loading}
            className="px-4 py-2 text-sm font-medium text-white bg-blue-600 border border-transparent rounded-md hover:bg-blue-700 disabled:opacity-50"
          >
            {loading ? 'Saving...' : 'Save All Changes'}
          </button>
        </div>
      )}

      {/* Items Table */}
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Part
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Expected
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Actual
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Discrepancy
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Notes
              </th>
              {canEdit && (
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Actions
                </th>
              )}
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {items.map((item) => {
              const isEditing = editingItems[item.id];

              return (
                <tr key={item.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div>
                      <div className="text-sm font-medium text-gray-900">
                        {item.part_number}
                      </div>
                      <div className="text-sm text-gray-500">
                        {item.part_name}
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {item.expected_quantity} {item.unit_of_measure}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    {isEditing ? (
                      <input
                        type="number"
                        step="0.001"
                        value={isEditing.actual_quantity}
                        onChange={(e) => handleEditChange(item.id, 'actual_quantity', e.target.value)}
                        className="w-24 px-2 py-1 text-sm border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
                        placeholder="0.000"
                      />
                    ) : (
                      <span className="text-sm text-gray-900">
                        {item.actual_quantity !== null ? `${item.actual_quantity} ${item.unit_of_measure}` : '-'}
                      </span>
                    )}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    {getDiscrepancyBadge(item.discrepancy, item.discrepancy_percentage)}
                  </td>
                  <td className="px-6 py-4">
                    {isEditing ? (
                      <input
                        type="text"
                        value={isEditing.notes}
                        onChange={(e) => handleEditChange(item.id, 'notes', e.target.value)}
                        className="w-full px-2 py-1 text-sm border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
                        placeholder="Optional notes..."
                      />
                    ) : (
                      <span className="text-sm text-gray-500">
                        {item.notes || '-'}
                      </span>
                    )}
                  </td>
                  {canEdit && (
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                      {isEditing ? (
                        <div className="flex space-x-2">
                          <button
                            onClick={() => handleItemUpdate(item.id, isEditing.actual_quantity, isEditing.notes)}
                            disabled={loading}
                            className="text-green-600 hover:text-green-900 disabled:opacity-50"
                          >
                            Save
                          </button>
                          <button
                            onClick={() => handleCancelEdit(item.id)}
                            className="text-gray-600 hover:text-gray-900"
                          >
                            Cancel
                          </button>
                        </div>
                      ) : (
                        <button
                          onClick={() => handleEditItem(item)}
                          className="text-blue-600 hover:text-blue-900"
                        >
                          {item.actual_quantity !== null ? 'Edit' : 'Count'}
                        </button>
                      )}
                    </td>
                  )}
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      {/* Complete Stocktake */}
      {canComplete && (
        <div className="border-t pt-6">
          <div className="flex justify-between items-center">
            <div>
              <h3 className="text-lg font-medium text-gray-900">Complete Stocktake</h3>
              <p className="text-sm text-gray-500">
                All items have been counted. You can now complete this stocktake.
              </p>
              {hasDiscrepancies && (
                <div className="mt-2">
                  <label className="flex items-center">
                    <input
                      type="checkbox"
                      checked={applyAdjustments}
                      onChange={(e) => setApplyAdjustments(e.target.checked)}
                      className="mr-2"
                    />
                    <span className="text-sm text-gray-700">
                      Apply inventory adjustments for discrepancies
                    </span>
                  </label>
                </div>
              )}
            </div>
            <button
              onClick={() => setShowCompleteConfirm(true)}
              className="px-4 py-2 text-sm font-medium text-white bg-green-600 border border-transparent rounded-md hover:bg-green-700"
            >
              Complete Stocktake
            </button>
          </div>
        </div>
      )}

      {/* Complete Confirmation Modal */}
      {showCompleteConfirm && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
          <div className="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white">
            <div className="mt-3 text-center">
              <h3 className="text-lg font-medium text-gray-900">Complete Stocktake</h3>
              <div className="mt-2 px-7 py-3">
                <p className="text-sm text-gray-500">
                  Are you sure you want to complete this stocktake?
                  {hasDiscrepancies && applyAdjustments && (
                    <span className="block mt-2 text-orange-600 font-medium">
                      This will apply inventory adjustments for all discrepancies.
                    </span>
                  )}
                </p>
              </div>
              <div className="flex justify-center space-x-3 mt-4">
                <button
                  onClick={() => setShowCompleteConfirm(false)}
                  className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 border border-gray-300 rounded-md hover:bg-gray-200"
                >
                  Cancel
                </button>
                <button
                  onClick={() => {
                    onComplete(stocktake.id, applyAdjustments);
                    setShowCompleteConfirm(false);
                  }}
                  disabled={parentLoading}
                  className="px-4 py-2 text-sm font-medium text-white bg-green-600 border border-transparent rounded-md hover:bg-green-700 disabled:opacity-50"
                >
                  {parentLoading ? 'Completing...' : 'Complete'}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default StocktakeDetails;