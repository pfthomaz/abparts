// frontend/src/services/transactionService.js

import { api } from './api';

/**
 * Fetches all transactions with optional filtering.
 * @param {object} filters Optional filters for transactions
 */
const getTransactions = (filters = {}) => {
  const queryParams = new URLSearchParams();
  if (filters && typeof filters === 'object') {
    Object.keys(filters).forEach(key => {
      if (filters[key] !== undefined && filters[key] !== null && filters[key] !== '') {
        queryParams.append(key, filters[key]);
      }
    });
  }

  const queryString = queryParams.toString();
  const endpoint = queryString ? `/transactions?${queryString}` : '/transactions';
  return api.get(endpoint);
};

/**
 * Get a specific transaction by ID.
 * @param {string} transactionId Transaction ID
 */
const getTransaction = (transactionId) => {
  return api.get(`/transactions/${transactionId}`);
};

/**
 * Create a new transaction.
 * @param {object} transactionData Transaction data
 */
const createTransaction = (transactionData) => {
  return api.post('/transactions', transactionData);
};

/**
 * Search transactions with advanced filters.
 * @param {object} filters Search filters
 * @param {number} skip Number of records to skip
 * @param {number} limit Maximum number of records to return
 */
const searchTransactions = (filters, skip = 0, limit = 100) => {
  const queryParams = new URLSearchParams();
  queryParams.append('skip', skip);
  queryParams.append('limit', limit);

  return api.post(`/transactions/search?${queryParams.toString()}`, filters);
};

/**
 * Reverse a transaction.
 * @param {object} reversalData Reversal data including transaction_id, reason, and performed_by_user_id
 */
const reverseTransaction = (reversalData) => {
  return api.post('/transactions/reverse', reversalData);
};

/**
 * Get transaction summary for a period.
 * @param {number} days Number of days to include in summary
 * @param {string} organizationId Optional organization ID filter
 */
const getTransactionSummary = (days = 30, organizationId = null) => {
  const queryParams = new URLSearchParams();
  queryParams.append('days', days);
  if (organizationId) {
    queryParams.append('organization_id', organizationId);
  }

  return api.get(`/transactions/summary?${queryParams.toString()}`);
};

/**
 * Get warehouse transaction summary.
 * @param {number} days Number of days to include in summary
 * @param {string} organizationId Optional organization ID filter
 */
const getWarehouseTransactionSummary = (days = 30, organizationId = null) => {
  const queryParams = new URLSearchParams();
  queryParams.append('days', days);
  if (organizationId) {
    queryParams.append('organization_id', organizationId);
  }

  return api.get(`/transactions/warehouse-summary?${queryParams.toString()}`);
};

/**
 * Get transaction history for a specific part.
 * @param {string} partId Part ID
 * @param {number} days Number of days to include
 * @param {string} organizationId Optional organization ID filter
 */
const getPartTransactionHistory = (partId, days = 90, organizationId = null) => {
  const queryParams = new URLSearchParams();
  queryParams.append('days', days);
  if (organizationId) {
    queryParams.append('organization_id', organizationId);
  }

  return api.get(`/transactions/part/${partId}/history?${queryParams.toString()}`);
};

/**
 * Create multiple transactions in a batch.
 * @param {object} batchData Batch transaction data
 */
const createTransactionBatch = (batchData) => {
  return api.post('/transactions/batch', batchData);
};

/**
 * Approve or reject a transaction.
 * @param {object} approvalData Approval data
 */
const approveTransaction = (approvalData) => {
  return api.post('/transactions/approval', approvalData);
};

/**
 * Get transactions pending approval.
 * @param {number} skip Number of records to skip
 * @param {number} limit Maximum number of records to return
 * @param {string} organizationId Optional organization ID filter
 */
const getPendingApprovalTransactions = (skip = 0, limit = 100, organizationId = null) => {
  const queryParams = new URLSearchParams();
  queryParams.append('skip', skip);
  queryParams.append('limit', limit);
  if (organizationId) {
    queryParams.append('organization_id', organizationId);
  }

  return api.get(`/transactions/pending-approval?${queryParams.toString()}`);
};

/**
 * Get transaction analytics for a period.
 * @param {number} days Number of days to analyze
 * @param {string} organizationId Optional organization ID filter
 */
const getTransactionAnalytics = async (days = 30, organizationId = null) => {
  const queryParams = new URLSearchParams();
  queryParams.append('days', days);
  if (organizationId) {
    queryParams.append('organization_id', organizationId);
  }

  try {
    // Get transaction summary data
    const summaryData = await api.get(`/transactions/summary?${queryParams.toString()}`);

    // Transform the data to match the expected analytics structure
    const totalTransactions = summaryData.reduce((sum, item) => sum + (item.transaction_count || 0), 0);
    const totalQuantity = summaryData.reduce((sum, item) => sum + parseFloat(item.total_quantity || 0), 0);

    // Transform transaction types for pie chart
    const transactionTypes = summaryData.map(item => ({
      name: item.transaction_type || 'Unknown',
      count: item.transaction_count || 0,
      value: item.transaction_count || 0
    }));

    // Create the expected analytics structure
    return {
      summary: {
        total_transactions: totalTransactions,
        total_value: totalQuantity, // Using quantity as value for now
        most_active_part: {
          name: 'N/A',
          transaction_count: 0
        },
        most_active_warehouse: {
          name: 'N/A',
          transaction_count: 0
        }
      },
      transaction_types: transactionTypes,
      daily_volume: [], // Empty for now
      top_parts: [], // Empty for now
      warehouse_activity: [], // Empty for now
      trends: [] // Empty for now
    };
  } catch (error) {
    console.error('Error fetching transaction analytics:', error);
    throw error;
  }
};

export const transactionService = {
  getTransactions,
  getTransaction,
  createTransaction,
  searchTransactions,
  reverseTransaction,
  getTransactionSummary,
  getWarehouseTransactionSummary,
  getPartTransactionHistory,
  createTransactionBatch,
  approveTransaction,
  getPendingApprovalTransactions,
  getTransactionAnalytics,
};