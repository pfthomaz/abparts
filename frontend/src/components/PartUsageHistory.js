// frontend/src/components/PartUsageHistory.js

import React, { useState, useEffect } from 'react';
import { transactionService } from '../services/transactionsService';
import Modal from './Modal';

const PartUsageHistory = ({ machineId, onUsageDeleted }) => {
  const [usageHistory, setUsageHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [deleteConfirm, setDeleteConfirm] = useState(null);
  const [deleting, setDeleting] = useState(false);
  const [editingUsage, setEditingUsage] = useState(null);
  const [editForm, setEditForm] = useState({});
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    if (machineId) {
      fetchUsageHistory();
    }
  }, [machineId]);

  const fetchUsageHistory = async () => {
    try {
      setLoading(true);
      const data = await transactionService.getMachinePartUsage(machineId);
      setUsageHistory(Array.isArray(data) ? data : []);
      setError(null);
    } catch (err) {
      console.error('Failed to fetch usage history:', err);
      setError('Failed to load part usage history');
      setUsageHistory([]);
    } finally {
      setLoading(false);
    }
  };

  const handleEditClick = async (usage) => {
    setEditingUsage(usage);
    
    // Format quantity based on unit of measure
    const isConsumable = usage.unit_of_measure === 'pieces' || 
                        usage.unit_of_measure === 'units' || 
                        usage.unit_of_measure === 'pcs';
    const formattedQuantity = isConsumable 
      ? Math.round(parseFloat(usage.quantity)) 
      : parseFloat(usage.quantity);
    
    setEditForm({
      quantity: formattedQuantity,
      notes: usage.notes || '',
      part_type: usage.part_type || 'consumable'
    });
  };

  const handleEditSave = async () => {
    if (!editingUsage) return;

    try {
      setSaving(true);
      
      // Build update payload with only the fields we want to update
      const updatePayload = {
        transaction_type: editingUsage.transaction_type,
        part_id: editingUsage.part_id,
        from_warehouse_id: editingUsage.from_warehouse_id,
        to_warehouse_id: editingUsage.to_warehouse_id,
        machine_id: editingUsage.machine_id,
        quantity: parseFloat(editForm.quantity),
        unit_of_measure: editingUsage.unit_of_measure,
        transaction_date: editingUsage.transaction_date,
        notes: editForm.notes || null,
        reference_number: editingUsage.reference_number,
        performed_by_user_id: editingUsage.performed_by_user_id
      };
      
      console.log('Updating transaction:', editingUsage.id, updatePayload);
      
      // Update the transaction
      await transactionService.updateTransaction(editingUsage.id, updatePayload);
      
      console.log('Transaction updated successfully');
      
      // Show success message
      alert('Part usage updated successfully. Page will reload to refresh all data.');
      
      // Reload the page to ensure all data (inventory, usage history, etc.) is refreshed
      // This is the most reliable way to ensure consistency across all components
      window.location.reload();
    } catch (err) {
      console.error('Failed to update usage:', err);
      console.error('Error details:', err.response?.data);
      alert('Failed to update part usage: ' + (err.response?.data?.detail || err.message));
    } finally {
      setSaving(false);
    }
  };

  const handleDeleteClick = (usage) => {
    setDeleteConfirm(usage);
  };

  const handleDeleteConfirm = async () => {
    if (!deleteConfirm) return;

    try {
      setDeleting(true);
      await transactionService.deleteTransaction(deleteConfirm.id);
      
      // Show success message
      alert('Part usage deleted successfully. Page will reload to refresh all data.');
      
      // Reload the page to ensure all data (inventory, usage history, etc.) is refreshed
      window.location.reload();
    } catch (err) {
      console.error('Failed to delete usage:', err);
      alert('Failed to delete part usage: ' + (err.response?.data?.detail || err.message));
    } finally {
      setDeleting(false);
    }
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleString();
  };

  const formatQuantity = (quantity, unitOfMeasure) => {
    const qty = parseFloat(quantity);
    // For pieces/units (consumables), show as integer
    if (unitOfMeasure === 'pieces' || unitOfMeasure === 'units' || unitOfMeasure === 'pcs') {
      return Math.round(qty);
    }
    // For other units (liters, kg, etc.), show with decimals
    return qty.toFixed(3).replace(/\.?0+$/, ''); // Remove trailing zeros
  };

  if (loading) {
    return <div className="text-center py-4">Loading usage history...</div>;
  }

  if (error) {
    return <div className="text-red-600 py-4">{error}</div>;
  }

  if (usageHistory.length === 0) {
    return <div className="text-gray-500 py-4">No part usage recorded for this machine yet.</div>;
  }

  return (
    <div className="space-y-4">
      <h3 className="text-lg font-semibold text-gray-900">Part Usage History</h3>
      
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Date</th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Part</th>
              <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">Quantity</th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Warehouse</th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Notes</th>
              <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">Actions</th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {usageHistory.map((usage) => (
              <tr key={usage.id} className="hover:bg-gray-50">
                <td className="px-4 py-3 text-sm text-gray-900">
                  {formatDate(usage.transaction_date)}
                </td>
                <td className="px-4 py-3 text-sm">
                  <div className="font-medium text-gray-900">{usage.part_name || 'Unknown'}</div>
                  <div className="text-gray-500">{usage.part_number || usage.part_id}</div>
                </td>
                <td className="px-4 py-3 text-sm text-gray-900 text-right">
                  {formatQuantity(usage.quantity, usage.unit_of_measure)} {usage.unit_of_measure}
                </td>
                <td className="px-4 py-3 text-sm text-gray-500">
                  {usage.from_warehouse_name || usage.from_warehouse_id}
                </td>
                <td className="px-4 py-3 text-sm text-gray-500">
                  {usage.notes || '-'}
                </td>
                <td className="px-4 py-3 text-sm text-right space-x-3">
                  <button
                    onClick={() => handleEditClick(usage)}
                    className="text-blue-600 hover:text-blue-900 font-medium"
                  >
                    Edit
                  </button>
                  <button
                    onClick={() => handleDeleteClick(usage)}
                    className="text-red-600 hover:text-red-900 font-medium"
                  >
                    Delete
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Edit Modal */}
      <Modal
        isOpen={!!editingUsage}
        onClose={() => !saving && setEditingUsage(null)}
        title="Edit Part Usage"
        size="small"
      >
        {editingUsage && (
          <div className="space-y-3">
            <div className="text-sm">
              <p className="font-medium text-gray-900">{editingUsage.part_name}</p>
              <p className="text-gray-500 text-xs">{formatDate(editingUsage.transaction_date)}</p>
            </div>

            <div>
              <label htmlFor="edit-quantity" className="block text-sm font-medium text-gray-700 mb-1">
                Quantity ({editingUsage.unit_of_measure})
              </label>
              <input
                type="number"
                id="edit-quantity"
                value={editForm.quantity}
                onChange={(e) => setEditForm({ ...editForm, quantity: e.target.value })}
                step={
                  editingUsage.unit_of_measure === 'pieces' || 
                  editingUsage.unit_of_measure === 'units' || 
                  editingUsage.unit_of_measure === 'pcs' 
                    ? '1' 
                    : '0.001'
                }
                min="0"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                disabled={saving}
              />
            </div>

            <div>
              <label htmlFor="edit-notes" className="block text-sm font-medium text-gray-700 mb-1">
                Notes
              </label>
              <textarea
                id="edit-notes"
                value={editForm.notes}
                onChange={(e) => setEditForm({ ...editForm, notes: e.target.value })}
                rows={2}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                disabled={saving}
              />
            </div>

            <div className="flex justify-end space-x-2 pt-2">
              <button
                type="button"
                onClick={() => setEditingUsage(null)}
                disabled={saving}
                className="px-3 py-1.5 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50"
              >
                Cancel
              </button>
              <button
                type="button"
                onClick={handleEditSave}
                disabled={saving || !editForm.quantity || parseFloat(editForm.quantity) <= 0}
                className="px-3 py-1.5 text-sm font-medium text-white bg-blue-600 border border-transparent rounded-md hover:bg-blue-700 disabled:opacity-50"
              >
                {saving ? 'Saving...' : 'Save'}
              </button>
            </div>
          </div>
        )}
      </Modal>

      {/* Delete Confirmation Modal */}
      <Modal
        isOpen={!!deleteConfirm}
        onClose={() => !deleting && setDeleteConfirm(null)}
        title="Delete Part Usage"
        size="small"
      >
        {deleteConfirm && (
          <div className="space-y-4">
            <div className="bg-yellow-50 border border-yellow-200 rounded-md p-4">
              <div className="flex">
                <div className="flex-shrink-0">
                  <svg className="h-5 w-5 text-yellow-400" viewBox="0 0 20 20" fill="currentColor">
                    <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                  </svg>
                </div>
                <div className="ml-3">
                  <h3 className="text-sm font-medium text-yellow-800">
                    Are you sure you want to delete this part usage?
                  </h3>
                  <div className="mt-2 text-sm text-yellow-700">
                    <p>This will remove the usage record and inventory will be automatically recalculated.</p>
                  </div>
                </div>
              </div>
            </div>

            <div className="bg-gray-50 rounded-md p-4">
              <dl className="space-y-2">
                <div>
                  <dt className="text-sm font-medium text-gray-500">Part:</dt>
                  <dd className="text-sm text-gray-900">{deleteConfirm.part_name} ({deleteConfirm.part_number})</dd>
                </div>
                <div>
                  <dt className="text-sm font-medium text-gray-500">Quantity:</dt>
                  <dd className="text-sm text-gray-900">{deleteConfirm.quantity} {deleteConfirm.unit_of_measure}</dd>
                </div>
                <div>
                  <dt className="text-sm font-medium text-gray-500">Date:</dt>
                  <dd className="text-sm text-gray-900">{formatDate(deleteConfirm.transaction_date)}</dd>
                </div>
              </dl>
            </div>

            <div className="flex justify-end space-x-3 pt-4">
              <button
                type="button"
                onClick={() => setDeleteConfirm(null)}
                disabled={deleting}
                className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50"
              >
                Cancel
              </button>
              <button
                type="button"
                onClick={handleDeleteConfirm}
                disabled={deleting}
                className="px-4 py-2 text-sm font-medium text-white bg-red-600 border border-transparent rounded-md hover:bg-red-700 disabled:opacity-50"
              >
                {deleting ? 'Deleting...' : 'Delete Usage'}
              </button>
            </div>
          </div>
        )}
      </Modal>
    </div>
  );
};

export default PartUsageHistory;
