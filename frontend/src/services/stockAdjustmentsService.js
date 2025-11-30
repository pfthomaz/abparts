// frontend/src/services/stockAdjustmentsService.js

import { api } from './api';

export const stockAdjustmentsService = {
  // List stock adjustments with optional filters
  list(filters = {}) {
    const params = new URLSearchParams();
    if (filters.warehouse_id) params.append('warehouse_id', filters.warehouse_id);
    if (filters.adjustment_type) params.append('adjustment_type', filters.adjustment_type);
    if (filters.start_date) params.append('start_date', filters.start_date);
    if (filters.end_date) params.append('end_date', filters.end_date);
    if (filters.user_id) params.append('user_id', filters.user_id);
    
    const queryString = params.toString();
    const endpoint = `/stock-adjustments${queryString ? '?' + queryString : ''}`;
    
    return api.get(endpoint);
  },

  // Get a specific stock adjustment by ID
  getById(id) {
    return api.get(`/stock-adjustments/${id}`);
  },

  // Create a new stock adjustment
  create(adjustmentData) {
    return api.post('/stock-adjustments', adjustmentData);
  },

  // Delete a stock adjustment
  delete(id) {
    return api.delete(`/stock-adjustments/${id}`);
  }
};
