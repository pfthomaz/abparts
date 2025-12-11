// frontend/src/services/stocktakeService.js

import { api } from './api';

/**
 * Modern stocktake service using the comprehensive inventory workflows API
 */

// Stocktake management
const getStocktakes = (params = {}) => {
  const queryParams = new URLSearchParams();
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== '') {
      queryParams.append(key, value);
    }
  });
  const queryString = queryParams.toString();
  return api.get(`/inventory-workflows/stocktakes${queryString ? `?${queryString}` : ''}`);
};

const getStocktake = (stocktakeId) => {
  return api.get(`/inventory-workflows/stocktakes/${stocktakeId}`);
};

const createStocktake = (stocktakeData) => {
  return api.post('/inventory-workflows/stocktakes', stocktakeData);
};

const updateStocktake = (stocktakeId, updateData) => {
  return api.put(`/inventory-workflows/stocktakes/${stocktakeId}`, updateData);
};

const deleteStocktake = (stocktakeId) => {
  return api.delete(`/inventory-workflows/stocktakes/${stocktakeId}`);
};

const completeStocktake = (stocktakeId, applyAdjustments = false) => {
  return api.post(`/inventory-workflows/stocktakes/${stocktakeId}/complete?apply_adjustments=${applyAdjustments}`);
};

// Stocktake items
const getStocktakeItems = (stocktakeId) => {
  return api.get(`/inventory-workflows/stocktakes/${stocktakeId}/items`);
};

const updateStocktakeItem = (itemId, updateData) => {
  return api.put(`/inventory-workflows/stocktake-items/${itemId}`, updateData);
};

const batchUpdateStocktakeItems = (stocktakeId, items) => {
  return api.put(`/inventory-workflows/stocktakes/${stocktakeId}/items/batch`, { items });
};

// Legacy methods for backward compatibility (if needed)
const getLocations = () => {
  return api.get('/stocktake/locations');
};

const generateWorksheet = (locationName) => {
  return api.post('/stocktake/worksheet', { name: locationName });
};

export const stocktakeService = {
  // Modern API
  getStocktakes,
  getStocktake,
  createStocktake,
  updateStocktake,
  deleteStocktake,
  completeStocktake,
  getStocktakeItems,
  updateStocktakeItem,
  batchUpdateStocktakeItems,

  // Legacy API (for backward compatibility)
  getLocations,
  generateWorksheet,
};