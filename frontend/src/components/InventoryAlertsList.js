// frontend/src/components/InventoryAlertsList.js

import React, { useState } from 'react';
import { inventoryWorkflowService } from '../services/inventoryWorkflowService';

const InventoryAlertsList = ({ alerts, onRefresh }) => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleResolveAlert = async (alertId) => {
    try {
      setLoading(true);
      await inventoryWorkflowService.updateInventoryAlert(alertId, {
        is_active: false,
        resolution_notes: 'Resolved by user'
      });
      onRefresh();
    } catch (err) {
      setError(err.message || 'Failed to resolve alert');
    } finally {
      setLoading(false);
    }
  };

  const getAlertIcon = (alertType) => {
    const icons = {
      low_stock: '⚠️',
      stockout: '🚫',
      excess: '📈',
      discrepancy: '❗',
      expiring: '⏰',
      expired: '❌'
    };
    return icons[alertType] || '🔔';
  };

  const getSeverityBadge = (severity) => {
    const severityConfig = {
      low: { bg: 'bg-blue-100', text: 'text-blue-800', label: 'Low' },
      medium: { bg: 'bg-yellow-100', text: 'text-yellow-800', label: 'Medium' },
      high: { bg: 'bg-orange-100', text: 'text-orange-800', label: 'High' },
      critical: { bg: 'bg-red-100', text: 'text-red-800', label: 'Critical' }
    };

    const config = severityConfig[severity] || severityConfig.low;

    return (
      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${config.bg} ${config.text}`}>
        {config.label}
      </span>
    );
  };

  const getAlertTypeBadge = (alertType) => {
    const typeConfig = {
      low_stock: { bg: 'bg-yellow-100', text: 'text-yellow-800', label: 'Low Stock' },
      stockout: { bg: 'bg-red-100', text: 'text-red-800', label: 'Stockout' },
      excess: { bg: 'bg-purple-100', text: 'text-purple-800', label: 'Excess' },
      discrepancy: { bg: 'bg-orange-100', text: 'text-orange-800', label: 'Discrepancy' },
      expiring: { bg: 'bg-blue-100', text: 'text-blue-800', label: 'Expiring' },
      expired: { bg: 'bg-gray-100', text: 'text-gray-800', label: 'Expired' }
    };

    const config = typeConfig[alertType] || typeConfig.low_stock;

    return (
      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${config.bg} ${config.text}`}>
        {getAlertIcon(alertType)} {config.label}
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

  if (alerts.length === 0) {
    return (
      <div className="p-8 text-center">
        <div className="text-6xl mb-4">✅</div>
        <p className="text-gray-600 text-lg">No active alerts</p>
        <p className="text-gray-500 text-sm">All inventory levels are within normal ranges</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded" role="alert">
          <span>{error}</span>
        </div>
      )}

      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Alert
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Part
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Warehouse
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Severity
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Values
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Created
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Actions
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {alerts.map((alert) => (
              <tr key={alert.id} className="hover:bg-gray-50">
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="space-y-2">
                    {getAlertTypeBadge(alert.alert_type)}
                    <div className="text-sm text-gray-900">
                      {alert.message}
                    </div>
                  </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <div>
                    <div className="text-sm font-medium text-gray-900">
                      {alert.part_number}
                    </div>
                    <div className="text-sm text-gray-500">
                      {alert.part_name}
                    </div>
                  </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <div>
                    <div className="text-sm font-medium text-gray-900">
                      {alert.warehouse_name}
                    </div>
                    <div className="text-sm text-gray-500">
                      {alert.organization_name}
                    </div>
                  </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  {getSeverityBadge(alert.severity)}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  <div>
                    <div>Current: {alert.current_value} {alert.unit_of_measure}</div>
                    {alert.threshold_value && (
                      <div className="text-gray-500">
                        Threshold: {alert.threshold_value} {alert.unit_of_measure}
                      </div>
                    )}
                  </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  {formatDate(alert.created_at)}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                  <button
                    onClick={() => handleResolveAlert(alert.id)}
                    disabled={loading}
                    className="text-green-600 hover:text-green-900 disabled:opacity-50"
                  >
                    Resolve
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Summary Stats */}
      <div className="bg-gray-50 p-4 rounded-lg">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="text-center">
            <div className="text-2xl font-bold text-red-600">
              {alerts.filter(a => a.severity === 'critical').length}
            </div>
            <div className="text-sm text-gray-500">Critical</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-orange-600">
              {alerts.filter(a => a.severity === 'high').length}
            </div>
            <div className="text-sm text-gray-500">High</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-yellow-600">
              {alerts.filter(a => a.severity === 'medium').length}
            </div>
            <div className="text-sm text-gray-500">Medium</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-blue-600">
              {alerts.filter(a => a.severity === 'low').length}
            </div>
            <div className="text-sm text-gray-500">Low</div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default InventoryAlertsList;