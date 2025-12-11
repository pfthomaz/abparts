// frontend/src/components/StocktakeList.js

import React, { useState } from 'react';
import { inventoryWorkflowService } from '../services/inventoryWorkflowService';
import StocktakeDetails from './StocktakeDetails';
import Modal from './Modal';

const StocktakeList = ({ stocktakes, onEdit, onRefresh }) => {
  const [selectedStocktake, setSelectedStocktake] = useState(null);
  const [showDetailsModal, setShowDetailsModal] = useState(false);
  const [loading, setLoading] = useState(false);

  const handleViewDetails = async (stocktake) => {
    try {
      setLoading(true);
      const detailedStocktake = await inventoryWorkflowService.getStocktake(stocktake.id);
      setSelectedStocktake(detailedStocktake);
      setShowDetailsModal(true);
    } catch (error) {
      console.error('Failed to fetch stocktake details:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCompleteStocktake = async (stocktakeId, applyAdjustments = false) => {
    try {
      setLoading(true);
      await inventoryWorkflowService.completeStocktake(stocktakeId, applyAdjustments);
      onRefresh();
      setShowDetailsModal(false);
    } catch (error) {
      console.error('Failed to complete stocktake:', error);
    } finally {
      setLoading(false);
    }
  };

  const getStatusBadge = (status) => {
    const statusConfig = {
      planned: { bg: 'bg-blue-100', text: 'text-blue-800', label: 'Planned' },
      in_progress: { bg: 'bg-yellow-100', text: 'text-yellow-800', label: 'In Progress' },
      completed: { bg: 'bg-green-100', text: 'text-green-800', label: 'Completed' },
      cancelled: { bg: 'bg-red-100', text: 'text-red-800', label: 'Cancelled' }
    };

    const config = statusConfig[status] || statusConfig.planned;

    return (
      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${config.bg} ${config.text}`}>
        {config.label}
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

  if (stocktakes.length === 0) {
    return (
      <div className="p-8 text-center">
        <p className="text-gray-600">No stocktakes found.</p>
      </div>
    );
  }

  return (
    <>
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Warehouse
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Scheduled Date
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Status
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Progress
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Discrepancies
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Scheduled By
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Actions
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {stocktakes.map((stocktake) => (
              <tr key={stocktake.id} className="hover:bg-gray-50">
                <td className="px-6 py-4 whitespace-nowrap">
                  <div>
                    <div className="text-sm font-medium text-gray-900">
                      {stocktake.warehouse_name}
                    </div>
                    <div className="text-sm text-gray-500">
                      {stocktake.organization_name}
                    </div>
                  </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  {formatDate(stocktake.scheduled_date)}
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  {getStatusBadge(stocktake.status)}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  <div className="flex items-center">
                    <div className="flex-1">
                      <div className="text-sm font-medium">
                        {stocktake.items_counted} / {stocktake.total_items}
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-2 mt-1">
                        <div
                          className="bg-blue-600 h-2 rounded-full"
                          style={{
                            width: `${stocktake.total_items > 0 ? (stocktake.items_counted / stocktake.total_items) * 100 : 0}%`
                          }}
                        ></div>
                      </div>
                    </div>
                  </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  {stocktake.discrepancy_count > 0 ? (
                    <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800">
                      {stocktake.discrepancy_count} issues
                    </span>
                  ) : (
                    <span className="text-sm text-gray-500">None</span>
                  )}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  {stocktake.scheduled_by_username}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                  <button
                    onClick={() => handleViewDetails(stocktake)}
                    disabled={loading}
                    className="text-blue-600 hover:text-blue-900 mr-3 disabled:opacity-50"
                  >
                    View Details
                  </button>
                  {stocktake.status === 'planned' && (
                    <button
                      onClick={() => onEdit(stocktake)}
                      className="text-green-600 hover:text-green-900"
                    >
                      Edit
                    </button>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Stocktake Details Modal */}
      {showDetailsModal && selectedStocktake && (
        <Modal
          isOpen={showDetailsModal}
          onClose={() => setShowDetailsModal(false)}
          title={`Stocktake Details - ${selectedStocktake.warehouse_name}`}
          size="xl"
        >
          <StocktakeDetails
            stocktake={selectedStocktake}
            onComplete={handleCompleteStocktake}
            onClose={() => setShowDetailsModal(false)}
            loading={loading}
          />
        </Modal>
      )}
    </>
  );
};

export default StocktakeList;