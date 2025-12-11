// frontend/src/components/TransactionReversalInterface.js

import React, { useState, useEffect } from 'react';
import { transactionService } from '../services/transactionService';
import { useAuth } from '../AuthContext';
import PermissionGuard from './PermissionGuard';
import { PERMISSIONS, isAdmin } from '../utils/permissions';
import Modal from './Modal';

const TransactionReversalInterface = () => {
  const { user } = useAuth();
  const [searchTerm, setSearchTerm] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [selectedTransaction, setSelectedTransaction] = useState(null);
  const [showReversalModal, setShowReversalModal] = useState(false);
  const [reversalReason, setReversalReason] = useState('');
  const [reversalType, setReversalType] = useState('full'); // 'full' or 'partial'
  const [partialQuantity, setPartialQuantity] = useState('');
  const [submitting, setSubmitting] = useState(false);

  const searchTransactions = async () => {
    if (!searchTerm.trim()) {
      setSearchResults([]);
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const filters = {
        reference_number: searchTerm.includes('REF') ? searchTerm : undefined,
        part_name: !searchTerm.includes('REF') ? searchTerm : undefined,
      };

      const results = await transactionService.searchTransactions(filters, 0, 20);

      // Filter out already reversed transactions
      const reversibleTransactions = results.filter(t => !t.is_reversed);
      setSearchResults(reversibleTransactions);
    } catch (err) {
      setError(err.message || 'Failed to search transactions.');
      setSearchResults([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    const delayedSearch = setTimeout(() => {
      searchTransactions();
    }, 500);

    return () => clearTimeout(delayedSearch);
  }, [searchTerm]);

  const handleReversalClick = (transaction) => {
    setSelectedTransaction(transaction);
    setReversalReason('');
    setReversalType('full');
    setPartialQuantity('');
    setShowReversalModal(true);
  };

  const handleReversalSubmit = async () => {
    if (!selectedTransaction || !reversalReason.trim()) return;

    setSubmitting(true);
    try {
      const reversalData = {
        transaction_id: selectedTransaction.id,
        reason: reversalReason,
        reversal_type: reversalType,
        performed_by_user_id: user.id,
      };

      if (reversalType === 'partial') {
        reversalData.partial_quantity = parseFloat(partialQuantity);
      }

      await transactionService.reverseTransaction(reversalData);

      // Remove the transaction from search results or mark as reversed
      setSearchResults(prev =>
        prev.map(t =>
          t.id === selectedTransaction.id
            ? { ...t, is_reversed: true }
            : t
        )
      );

      setShowReversalModal(false);
      setSelectedTransaction(null);
      setReversalReason('');
    } catch (err) {
      setError(err.message || 'Failed to reverse transaction.');
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

  const canReverseTransaction = (transaction) => {
    // Business rules for transaction reversal
    const transactionDate = new Date(transaction.transaction_date);
    const daysSinceTransaction = (Date.now() - transactionDate.getTime()) / (1000 * 60 * 60 * 24);

    // Can only reverse transactions within 30 days
    return daysSinceTransaction <= 30 && !transaction.is_reversed;
  };

  if (!isAdmin(user)) {
    return (
      <div className="bg-white p-6 rounded-lg shadow-md">
        <p className="text-gray-500 text-center">
          Transaction reversal is only available to administrators.
        </p>
      </div>
    );
  }

  return (
    <PermissionGuard permission={PERMISSIONS.VIEW_ORG_TRANSACTIONS}>
      <div className="space-y-6">
        <div className="flex justify-between items-center">
          <h2 className="text-2xl font-bold text-gray-800">Transaction Reversal & Correction</h2>
        </div>

        <div className="bg-yellow-50 border border-yellow-200 rounded-md p-4">
          <div className="flex">
            <div className="flex-shrink-0">
              <svg className="h-5 w-5 text-yellow-400" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
              </svg>
            </div>
            <div className="ml-3">
              <h3 className="text-sm font-medium text-yellow-800">Important Notice</h3>
              <div className="mt-2 text-sm text-yellow-700">
                <p>Transaction reversals are permanent and cannot be undone. Only transactions within the last 30 days can be reversed. Use this feature carefully.</p>
              </div>
            </div>
          </div>
        </div>

        {/* Search Interface */}
        <div className="bg-white p-6 rounded-lg shadow-md">
          <h3 className="text-lg font-semibold text-gray-800 mb-4">Search Transactions</h3>
          <div className="flex space-x-4">
            <div className="flex-1">
              <label htmlFor="searchTerm" className="block text-sm font-medium text-gray-700 mb-1">
                Search by Reference Number or Part Name
              </label>
              <input
                type="text"
                id="searchTerm"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                placeholder="Enter reference number (e.g., REF-12345) or part name..."
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
              />
            </div>
          </div>
          <p className="text-sm text-gray-500 mt-2">
            Search for transactions by reference number or part name. Only transactions from the last 30 days that haven't been reversed will be shown.
          </p>
        </div>

        {error && (
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative" role="alert">
            <strong className="font-bold">Error: </strong>
            <span className="block sm:inline">{error}</span>
          </div>
        )}

        {/* Search Results */}
        {loading ? (
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
        ) : searchResults.length > 0 ? (
          <div className="bg-white rounded-lg shadow-md overflow-hidden">
            <div className="px-6 py-4 border-b border-gray-200">
              <h3 className="text-lg font-semibold text-gray-800">
                Search Results ({searchResults.length} transactions found)
              </h3>
            </div>
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Date
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Type
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Part
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Quantity
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Reference
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Status
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {searchResults.map((transaction) => (
                    <tr key={transaction.id} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {formatDate(transaction.transaction_date)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getTransactionTypeColor(transaction.transaction_type)}`}>
                          {getTransactionTypeLabel(transaction.transaction_type)}
                        </span>
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
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {transaction.reference_number || '-'}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        {transaction.is_reversed ? (
                          <span className="inline-flex px-2 py-1 text-xs font-semibold rounded-full text-red-600 bg-red-100">
                            Reversed
                          </span>
                        ) : canReverseTransaction(transaction) ? (
                          <span className="inline-flex px-2 py-1 text-xs font-semibold rounded-full text-green-600 bg-green-100">
                            Reversible
                          </span>
                        ) : (
                          <span className="inline-flex px-2 py-1 text-xs font-semibold rounded-full text-gray-600 bg-gray-100">
                            Not Reversible
                          </span>
                        )}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                        {canReverseTransaction(transaction) ? (
                          <button
                            onClick={() => handleReversalClick(transaction)}
                            className="text-red-600 hover:text-red-900 bg-red-50 hover:bg-red-100 px-3 py-1 rounded-md transition-colors"
                          >
                            Reverse
                          </button>
                        ) : (
                          <span className="text-gray-400">-</span>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        ) : searchTerm && !loading ? (
          <div className="bg-white p-6 rounded-lg shadow-md">
            <div className="text-center py-8">
              <div className="text-gray-400 text-6xl mb-4">🔍</div>
              <h3 className="text-lg font-medium text-gray-900 mb-2">No transactions found</h3>
              <p className="text-gray-500">
                No reversible transactions found matching "{searchTerm}".
                Try a different search term or check if the transaction is older than 30 days.
              </p>
            </div>
          </div>
        ) : null}

        {/* Reversal Modal */}
        <Modal
          isOpen={showReversalModal}
          onClose={() => setShowReversalModal(false)}
          title="Reverse Transaction"
        >
          {selectedTransaction && (
            <div className="space-y-4">
              <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                <div className="flex">
                  <div className="flex-shrink-0">
                    <svg className="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
                      <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                    </svg>
                  </div>
                  <div className="ml-3">
                    <h3 className="text-sm font-medium text-red-800">Warning</h3>
                    <div className="mt-2 text-sm text-red-700">
                      <p>This action will permanently reverse the transaction and cannot be undone. Inventory levels will be adjusted accordingly.</p>
                    </div>
                  </div>
                </div>
              </div>

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
                    <span className="text-gray-500">Date:</span>
                    <span className="ml-2 font-medium">
                      {formatDate(selectedTransaction.transaction_date)}
                    </span>
                  </div>
                  <div>
                    <span className="text-gray-500">Reference:</span>
                    <span className="ml-2 font-medium">
                      {selectedTransaction.reference_number || 'N/A'}
                    </span>
                  </div>
                  <div>
                    <span className="text-gray-500">Performed by:</span>
                    <span className="ml-2 font-medium">{selectedTransaction.performed_by_username}</span>
                  </div>
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Reversal Type
                </label>
                <div className="space-y-2">
                  <label className="flex items-center">
                    <input
                      type="radio"
                      name="reversalType"
                      value="full"
                      checked={reversalType === 'full'}
                      onChange={(e) => setReversalType(e.target.value)}
                      className="mr-2"
                    />
                    <span className="text-sm">Full Reversal - Reverse the entire transaction</span>
                  </label>
                  <label className="flex items-center">
                    <input
                      type="radio"
                      name="reversalType"
                      value="partial"
                      checked={reversalType === 'partial'}
                      onChange={(e) => setReversalType(e.target.value)}
                      className="mr-2"
                    />
                    <span className="text-sm">Partial Reversal - Reverse only a portion of the quantity</span>
                  </label>
                </div>
              </div>

              {reversalType === 'partial' && (
                <div>
                  <label htmlFor="partialQuantity" className="block text-sm font-medium text-gray-700 mb-1">
                    Quantity to Reverse <span className="text-red-500">*</span>
                  </label>
                  <input
                    type="number"
                    id="partialQuantity"
                    value={partialQuantity}
                    onChange={(e) => setPartialQuantity(e.target.value)}
                    min="0.001"
                    max={selectedTransaction.quantity}
                    step={selectedTransaction.part_type === 'bulk_material' ? '0.001' : '1'}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                    placeholder={`Max: ${selectedTransaction.quantity} ${selectedTransaction.unit_of_measure}`}
                    required
                  />
                </div>
              )}

              <div>
                <label htmlFor="reversalReason" className="block text-sm font-medium text-gray-700 mb-1">
                  Reason for Reversal <span className="text-red-500">*</span>
                </label>
                <textarea
                  id="reversalReason"
                  rows="3"
                  value={reversalReason}
                  onChange={(e) => setReversalReason(e.target.value)}
                  placeholder="Please provide a detailed reason for reversing this transaction..."
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                  required
                />
              </div>

              <div className="flex justify-end space-x-3">
                <button
                  onClick={() => setShowReversalModal(false)}
                  className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-200 rounded-md hover:bg-gray-300 focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-offset-2"
                  disabled={submitting}
                >
                  Cancel
                </button>
                <button
                  onClick={handleReversalSubmit}
                  className="px-4 py-2 text-sm font-medium text-white bg-red-600 rounded-md hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2"
                  disabled={
                    submitting ||
                    !reversalReason.trim() ||
                    (reversalType === 'partial' && (!partialQuantity || parseFloat(partialQuantity) <= 0))
                  }
                >
                  {submitting ? 'Reversing...' : 'Reverse Transaction'}
                </button>
              </div>
            </div>
          )}
        </Modal>
      </div>
    </PermissionGuard>
  );
};

export default TransactionReversalInterface;