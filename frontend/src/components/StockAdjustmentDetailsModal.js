// frontend/src/components/StockAdjustmentDetailsModal.js

import React from 'react';
import { formatDate, formatNumber } from '../utils';

const adjustmentTypeLabels = {
  stock_take: 'Stock Take',
  damage: 'Damage',
  loss: 'Loss',
  found: 'Found',
  correction: 'Correction',
  return: 'Return',
  other: 'Other'
};

const StockAdjustmentDetailsModal = ({ adjustment, onClose }) => {
  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg max-w-4xl w-full max-h-[90vh] overflow-y-auto">
        <div className="p-6">
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-2xl font-bold">Stock Adjustment Details</h2>
            <button
              onClick={onClose}
              className="text-gray-500 hover:text-gray-700 text-2xl"
            >
              ✕
            </button>
          </div>

          {/* Header Info */}
          <div className="bg-gray-50 rounded-lg p-4 mb-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <div className="text-sm text-gray-600">Warehouse</div>
                <div className="font-medium">{adjustment.warehouse_name}</div>
              </div>
              <div>
                <div className="text-sm text-gray-600">Type</div>
                <div className="font-medium">{adjustmentTypeLabels[adjustment.adjustment_type]}</div>
              </div>
              <div>
                <div className="text-sm text-gray-600">Date</div>
                <div className="font-medium">{formatDate(adjustment.adjustment_date)}</div>
              </div>
              <div>
                <div className="text-sm text-gray-600">User</div>
                <div className="font-medium">{adjustment.username}</div>
              </div>
              {adjustment.reason && (
                <div className="md:col-span-2">
                  <div className="text-sm text-gray-600">Reason</div>
                  <div className="font-medium">{adjustment.reason}</div>
                </div>
              )}
              {adjustment.notes && (
                <div className="md:col-span-2">
                  <div className="text-sm text-gray-600">Notes</div>
                  <div className="font-medium">{adjustment.notes}</div>
                </div>
              )}
            </div>
          </div>

          {/* Items */}
          <div>
            <h3 className="text-lg font-semibold mb-3">
              Adjusted Items ({adjustment.items.length})
            </h3>
            
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                      Part Number
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                      Part Name
                    </th>
                    <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">
                      Before
                    </th>
                    <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">
                      After
                    </th>
                    <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">
                      Change
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                      Reason
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {adjustment.items.map((item) => {
                    const change = parseFloat(item.quantity_change);
                    const isIncrease = change > 0;
                    const isDecrease = change < 0;
                    const unitOfMeasure = item.unit_of_measure || 'units';
                    
                    return (
                      <tr key={item.id}>
                        <td className="px-4 py-3 text-sm font-medium text-gray-900">
                          {item.part_number}
                        </td>
                        <td className="px-4 py-3 text-sm text-gray-900">
                          {item.part_name}
                        </td>
                        <td className="px-4 py-3 text-sm text-right text-gray-900">
                          {formatNumber(item.quantity_before, unitOfMeasure)}
                        </td>
                        <td className="px-4 py-3 text-sm text-right text-gray-900">
                          {formatNumber(item.quantity_after, unitOfMeasure)}
                        </td>
                        <td className={`px-4 py-3 text-sm text-right font-medium ${
                          isIncrease ? 'text-green-600' : isDecrease ? 'text-red-600' : 'text-gray-900'
                        }`}>
                          {isIncrease && '+'}
                          {formatNumber(item.quantity_change, unitOfMeasure)}
                        </td>
                        <td className="px-4 py-3 text-sm text-gray-600">
                          {item.reason || '-'}
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>

          {/* Summary */}
          <div className="mt-6 pt-6 border-t border-gray-200">
            <div className="flex justify-between items-center">
              <div className="text-sm text-gray-600">
                Created: {formatDate(adjustment.created_at)}
              </div>
              <button
                onClick={onClose}
                className="px-4 py-2 bg-gray-200 text-gray-800 rounded hover:bg-gray-300"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default StockAdjustmentDetailsModal;
