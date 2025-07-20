// frontend/src/components/TransactionApprovalWorkflow.js

import React, { useState, useEffect } from 'react';
import { transactionService } from '../services/transactionService';
import { useAuth } from '../AuthContext';
import PermissionGuard from './PermissionGuard';
import { PERMISSIONS, isAdmin } from '../utils/permissions';
import Modal from './Modal';

const TransactionApprovalWorkflow = () => {
  const { user } = useAuth();
  const [pendingTransactions, setPendingTransactions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedTransaction, setSelectedTransaction] = useState(null);
  const [showApprovalModal, setShowApprovalModal] = useState(false);
  const [approvalAction, setApprovalAction] = useState('approve'); // 'approve' or 'reject'
  const [approvalNotes, setApprovalNotes] = useState('');
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    fetchPendingTransactions();
  }, []);

  const fetchPendingTransactions = async () => {
    setLoading(true);
    setError(null);

    try {
      const data = await transactionService.getPendingApprovalTransactions();
      setPendingTransactions(data);
    } catch (err) {
      setError(err.message || 'Failed to fetch pending transactions.');
    } finally {
      setLoading(false);
    }
  };

  const handleApprovalClick = (transaction, action) => {
    setSelectedTransaction(transaction);
    setApprovalAction(action);
    setApprovalNotes('');
    setShowApprovalModal(true);
  };

  const handleApprovalSubmit = async () => {
    if (!selectedTransaction) return;

    setSubmitting(true);
    try {
      await transactionService.approveTransaction({
        transaction_id: selectedTransaction.id,
        action: approvalAction,
        notes: approvalNotes,
        approved_by_user_id: user.id
      });

      // Remove the transaction from the pending list
      setPendingTransactions(prev =>
        prev.filter(t => t.id !== selectedTransaction.id)
      );

      setShowApprovalModal(false);
      setSelectedTransaction(null);
      setApprovalNotes('');
    } catch (err) {
      setError(err.message || 'Failed to process approval.');
    } finally {
      setSubmitting(false);
    }
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

  const getTransactionTypeColor = (type) => {
    switch (type) {
      case 'creation': return 'text-green-600 bg-green-100';
      case 'transfer': return 'text-blue-600 bg-blue-100';
      case 'consumption': return 'text-red-600 bg-red-100';
      case 'adjustment': return 'text-yellow-600 bg-yellow-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  const getTransactionTypeLabel = (type) => {
    switch (type) {
      case 'creation': return 'Creation';
      case 'transfer': return 'Transfer';
      case 'consumption': return 'Consumption';
      case 'adjustment': return 'Adjustment';
      default: return type;
    }
  };

  const getPriorityColor = (value) => {
    if (value >= 1000) return 'text-red-600 bg-red-100';
    if (value >= 500) return 'text-yellow-600 bg-yellow-100';
    return 'text-green-600 bg-green-100';
  };

  const calculateTransactionValue = (transaction) => {
    // This would typically come from the backend with part pricing
    // For now, we'll use a placeholder calculation
    return transaction.quantity * 10; // Placeholder: $10 per unit
  };

  if (!isAdmin(user)) {
    return (
      <div className="bg-white p-6 rounded-lg shadow-md">
        <p className="text-gray-500 text-center">
          Transaction approval is only available to administrators.
        </p>
      </div>
    );
  }

  return (
    <PermissionGuard permission={PERMISSIONS.VIEW_ORG_TRANSACTIONS}>
      <div className="space-y-6">
        <div className="flex justify-between items-center">
          <h2 className="text-2xl font-bold text-gray-800">Transaction Approvals</h2>
          <button
            onClick={fetchPendingTransactions}
            className="px-4 py-2 text-sm font-medium text-blue-600 bg-blue-50 rounded-md hover:bg-blue-100 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
            disabled={loading}
          >
            {loading ? 'Refreshing...' : 'Refresh'}
          </button>
        </div>

        {error && (
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative" role="alert">
            <strong className="font-bold">Error: </strong>
            <span className="block sm:inline">{error}</span>
          </div>
        )}

        {loading && pendingTransactions.length === 0 ? (
          <div className="bg-white p-6 rounded-lg shadow-md">
            <div className="animate-pulse">
              <div className="h-4 bg-gray-200 rounded w-1/4 mb-4"></div>
              <div className="space-y-3">
                <div className="h-4 bg-gray-200 rounded"></div>
                <div className="h-4 bg-gray-200 rounded w-5/6"></div>
                <div className="h-4 bg-gray-200 rounded w-4/6"></div>
              </div>
            </div>
          </div>
        ) : pendingTransactions.length === 0 ? (
          <div className="bg-white p-6 rounded-lg shadow-md">
            <div className="text-center py-8">
              <div className="text-gray-400 text-6xl mb-4">✓</div>
              <h3 className="text-lg font-medium text-gray-900 mb-2">All caught up!</h3>
              <p className="text-gray-500">No transactions pending approval at this time.</p>
            </div>
          </div>
        ) : (
          <div className="bg-white rounded-lg shadow-md overflow-hidden">
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Transaction
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Part
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Quantity
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Value
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Requested By
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Date
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {pendingTransactions.map((transaction) => {
                    const transactionValue = calculateTransactionValue(transaction);
                    return (
                      <tr key={transaction.id} className="hover:bg-gray-50">
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="flex flex-col">
                            <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getTransactionTypeColor(transaction.transaction_type)}`}>
                              {getTransactionTypeLabel(transaction.transaction_type)}
                            </span>
                            {transaction.reference_number && (
                              <span className="text-xs text-gray-500 mt-1">
                                Ref: {transaction.reference_number}
                              </span>
                            )}
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div>
                            <div className="font-medium text-gray-900">{transaction.part_name}</div>
                            <div className="text-sm text-gray-500">{transaction.part_number}</div>
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          {transaction.quantity} {transaction.unit_of_measure}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getPriorityColor(transactionValue)}`}>
                            ${transactionValue.toLocaleString()}
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {transaction.performed_by_username}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {formatDate(transaction.transaction_date)}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium space-x-2">
                          <button
                            onClick={() => handleApprovalClick(transaction, 'approve')}
                            className="text-green-600 hover:text-green-900 bg-green-50 hover:bg-green-100 px-3 py-1 rounded-md transition-colors"
                          >
                            Approve
                          </button>
                          <button
                            onClick={() => handleApprovalClick(transaction, 'reject')}
                            className="text-red-600 hover:text-red-900 bg-red-50 hover:bg-red-100 px-3 py-1 rounded-md transition-colors"
                          >
                            Reject
                          </button>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* Approval Modal */}
        <Modal
          isOpen={showApprovalModal}
          onClose={() => setShowApprovalModal(false)}
          title={`${approvalAction === 'approve' ? 'Approve' : 'Reject'} Transaction`}
        >
          {selectedTransaction && (
            <div className="space-y-4">
              <div className="bg-gray-50 p-4 rounded-lg">
                <h4 className="font-medium text-gray-900 mb-2">Transaction Details</h4>
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <span className="text-gray-500">Type:</span>
                    <span className="ml-2 font-medium">
                      {getTransactionTypeLabel(selectedTransaction.transaction_type)}
                    </span>
                  </div>
                  <div>
                    <span className="text-gray-500">Part:</span>
                    <span className="ml-2 font-medium">{selectedTransaction.part_name}</span>
                  </div>
                  <div>
                    <span className="text-gray-500">Quantity:</span>
                    <span className="ml-2 font-medium">
                      {selectedTransaction.quantity} {selectedTransaction.unit_of_measure}
                    </span>
                  </div>
                  <div>
                    <span className="text-gray-500">Value:</span>
                    <span className="ml-2 font-medium">
                      ${calculateTransactionValue(selectedTransaction).toLocaleString()}
                    </span>
                  </div>
                  <div>
                    <span className="text-gray-500">Requested by:</span>
                    <span className="ml-2 font-medium">{selectedTransaction.performed_by_username}</span>
                  </div>
                  <div>
                    <span className="text-gray-500">Date:</span>
                    <span className="ml-2 font-medium">
                      {formatDate(selectedTransaction.transaction_date)}
                    </span>
                  </div>
                </div>
                {selectedTransaction.notes && (
                  <div className="mt-3">
                    <span className="text-gray-500">Notes:</span>
                    <p className="mt-1 text-sm text-gray-700">{selectedTransaction.notes}</p>
                  </div>
                )}
              </div>

              <div>
                <label htmlFor="approvalNotes" className="block text-sm font-medium text-gray-700 mb-1">
                  {approvalAction === 'approve' ? 'Approval' : 'Rejection'} Notes
                  {approvalAction === 'reject' && <span className="text-red-500 ml-1">*</span>}
                </label>
                <textarea
                  id="approvalNotes"
                  rows="3"
                  value={approvalNotes}
                  onChange={(e) => setApprovalNotes(e.target.value)}
                  placeholder={
                    approvalAction === 'approve'
                      ? 'Optional notes about the approval...'
                      : 'Please provide a reason for rejection...'
                  }
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                  required={approvalAction === 'reject'}
                />
              </div>

              <div className="flex justify-end space-x-3">
                <button
                  onClick={() => setShowApprovalModal(false)}
                  className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-200 rounded-md hover:bg-gray-300 focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-offset-2"
                  disabled={submitting}
                >
                  Cancel
                </button>
                <button
                  onClick={handleApprovalSubmit}
                  className={`px-4 py-2 text-sm font-medium text-white rounded-md focus:outline-none focus:ring-2 focus:ring-offset-2 ${approvalAction === 'approve'
                      ? 'bg-green-600 hover:bg-green-700 focus:ring-green-500'
                      : 'bg-red-600 hover:bg-red-700 focus:ring-red-500'
                    }`}
                  disabled={submitting || (approvalAction === 'reject' && !approvalNotes.trim())}
                >
                  {submitting
                    ? (approvalAction === 'approve' ? 'Approving...' : 'Rejecting...')
                    : (approvalAction === 'approve' ? 'Approve Transaction' : 'Reject Transaction')
                  }
                </button>
              </div>
            </div>
          )}
        </Modal>
      </div>
    </PermissionGuard>
  );
};

export default TransactionApprovalWorkflow;