// frontend/src/services/inventoryWorkflowService.js

import { api } from './api';

export const inventoryWorkflowService = {
  // Stocktake operations
  async getStocktakes(params = {}) {
    const queryParams = new URLSearchParams();
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined && value !== null && value !== '') {
        queryParams.append(key, value);
      }
    });
    const queryString = queryParams.toString();
    return api.get(`/inventory-workflows/stocktakes${queryString ? `?${queryString}` : ''}`);
  },

  async getStocktake(stocktakeId) {
    return api.get(`/inventory-workflows/stocktakes/${stocktakeId}`);
  },

  async createStocktake(stocktakeData) {
    return api.post('/inventory-workflows/stocktakes', stocktakeData);
  },

  async updateStocktake(stocktakeId, updateData) {
    return api.put(`/inventory-workflows/stocktakes/${stocktakeId}`, updateData);
  },

  async deleteStocktake(stocktakeId) {
    return api.delete(`/inventory-workflows/stocktakes/${stocktakeId}`);
  },

  async completeStocktake(stocktakeId, applyAdjustments = false) {
    return api.post(`/inventory-workflows/stocktakes/${stocktakeId}/complete?apply_adjustments=${applyAdjustments}`);
  },

  // Stocktake items
  async getStocktakeItems(stocktakeId) {
    return api.get(`/inventory-workflows/stocktakes/${stocktakeId}/items`);
  },

  async updateStocktakeItem(itemId, updateData) {
    return api.put(`/inventory-workflows/stocktake-items/${itemId}`, updateData);
  },

  async batchUpdateStocktakeItems(stocktakeId, items) {
    return api.put(`/inventory-workflows/stocktakes/${stocktakeId}/items/batch`, { items });
  },

  // Inventory adjustments
  async getInventoryAdjustments(params = {}) {
    const queryParams = new URLSearchParams();
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined && value !== null && value !== '') {
        queryParams.append(key, value);
      }
    });
    const queryString = queryParams.toString();
    return api.get(`/inventory-workflows/adjustments${queryString ? `?${queryString}` : ''}`);
  },

  async createInventoryAdjustment(adjustmentData) {
    return api.post('/inventory-workflows/adjustments', adjustmentData);
  },

  async batchCreateInventoryAdjustments(batchData) {
    return api.post('/inventory-workflows/adjustments/batch', batchData);
  },

  // Inventory alerts
  async getInventoryAlerts(params = {}) {
    const queryParams = new URLSearchParams();
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined && value !== null && value !== '') {
        queryParams.append(key, value);
      }
    });
    const queryString = queryParams.toString();
    return api.get(`/inventory-workflows/alerts${queryString ? `?${queryString}` : ''}`);
  },

  async createInventoryAlert(alertData) {
    return api.post('/inventory-workflows/alerts', alertData);
  },

  async updateInventoryAlert(alertId, updateData) {
    return api.put(`/inventory-workflows/alerts/${alertId}`, updateData);
  },

  async generateInventoryAlerts(organizationId = null) {
    const params = organizationId ? `?organization_id=${organizationId}` : '';
    return api.post(`/inventory-workflows/alerts/generate${params}`);
  },

  // Analytics
  async getInventoryAnalytics(analyticsRequest) {
    return api.post('/inventory-workflows/analytics', analyticsRequest);
  }
};