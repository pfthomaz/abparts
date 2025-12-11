// frontend/src/services/transactionsService.js

import { api } from './api';

/**
 * Get all transactions with optional filters
 */
const getTransactions = async (params = {}) => {
  const queryParams = new URLSearchParams();
  
  Object.keys(params).forEach(key => {
    if (params[key] !== undefined && params[key] !== null && params[key] !== '') {
      queryParams.append(key, params[key]);
    }
  });
  
  const queryString = queryParams.toString();
  const endpoint = `/transactions${queryString ? `?${queryString}` : ''}`;
  
  return api.get(endpoint);
};

/**
 * Search transactions with filters
 */
const searchTransactions = async (filters = {}, skip = 0, limit = 100) => {
  return api.post(`/transactions/search?skip=${skip}&limit=${limit}`, filters);
};

/**
 * Get consumption transactions (part usage) for a machine
 */
const getMachinePartUsage = async (machineId, params = {}) => {
  const filters = {
    machine_id: machineId,
    transaction_type: 'consumption',
    ...params
  };
  
  return searchTransactions(filters);
};

/**
 * Delete a transaction
 */
const deleteTransaction = async (transactionId) => {
  return api.delete(`/transactions/${transactionId}`);
};

/**
 * Update a transaction
 */
const updateTransaction = async (transactionId, transactionData) => {
  return api.put(`/transactions/${transactionId}`, transactionData);
};

/**
 * Create a new transaction
 */
const createTransaction = async (transactionData) => {
  return api.post('/transactions', transactionData);
};

export const transactionService = {
  getTransactions,
  searchTransactions,
  getMachinePartUsage,
  deleteTransaction,
  updateTransaction,
  createTransaction
};

export default transactionService;
