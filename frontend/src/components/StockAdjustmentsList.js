// frontend/src/components/StockAdjustmentsList.js

import React from 'react';
import { formatDate } from '../utils';
import { useTranslation } from '../hooks/useTranslation';

const adjustmentTypeColors = {
  stock_take: 'bg-blue-100 text-blue-800',
  damage: 'bg-red-100 text-red-800',
  loss: 'bg-orange-100 text-orange-800',
  found: 'bg-green-100 text-green-800',
  correction: 'bg-yellow-100 text-yellow-800',
  return: 'bg-purple-100 text-purple-800',
  other: 'bg-gray-100 text-gray-800'
};

const StockAdjustmentsList = ({ adjustments, onViewDetails, onEdit, onDelete }) => {
  const { t } = useTranslation();

  if (adjustments.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow p-8 text-center text-gray-500">
        {t('stockAdjustments.noAdjustmentsFound')}
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow overflow-hidden">
      <table className="min-w-full divide-y divide-gray-200">
        <thead className="bg-gray-50">
          <tr>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              {t('stockAdjustments.date')}
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              {t('stockAdjustments.warehouse')}
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              {t('stockAdjustments.type')}
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              {t('stockAdjustments.items')}
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              {t('stockAdjustments.user')}
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              {t('stockAdjustments.reason')}
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              {t('common.actions')}
            </th>
          </tr>
        </thead>
        <tbody className="bg-white divide-y divide-gray-200">
          {adjustments.map((adjustment) => (
            <tr key={adjustment.id} className="hover:bg-gray-50">
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                {formatDate(adjustment.adjustment_date)}
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                {adjustment.warehouse_name}
              </td>
              <td className="px-6 py-4 whitespace-nowrap">
                <span className={`px-2 py-1 text-xs font-medium rounded ${adjustmentTypeColors[adjustment.adjustment_type]}`}>
                  {t(`stockAdjustments.types.${adjustment.adjustment_type.replace('_', '')}`)}
                </span>
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                {adjustment.total_items_adjusted}
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                {adjustment.username}
              </td>
              <td className="px-6 py-4 text-sm text-gray-500 max-w-xs truncate">
                {adjustment.reason || '-'}
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-right space-x-3">
                <button
                  onClick={() => onViewDetails(adjustment.id)}
                  className="text-blue-600 hover:text-blue-900 font-medium"
                >
                  {t('common.view')}
                </button>
                {onEdit && (
                  <button
                    onClick={() => onEdit(adjustment)}
                    className="text-green-600 hover:text-green-900 font-medium"
                  >
                    {t('common.edit')}
                  </button>
                )}
                {onDelete && (
                  <button
                    onClick={() => onDelete(adjustment)}
                    className="text-red-600 hover:text-red-900 font-medium"
                  >
                    {t('common.delete')}
                  </button>
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default StockAdjustmentsList;
