// c:/abparts/frontend/src/services/inventoryService.js

import { api } from './api';

/**
 * Fetches all inventory items.
 */
const getInventory = () => {
  return api.get('/inventory');
};

/**
 * Creates a new inventory item.
 * @param {object} inventoryData The data for the new item.
 */
const createInventoryItem = (inventoryData) => {
  return api.post('/inventory', inventoryData);
};

/**
 * Updates an existing inventory item.
 * @param {string} inventoryId The ID of the item to update.
 * @param {object} inventoryData The updated data for the item.
 */
const updateInventoryItem = (inventoryId, inventoryData) => {
  return api.put(`/inventory/${inventoryId}`, inventoryData);
};

/**
 * Deletes an inventory item.
 * @param {string} inventoryId The ID of the item to delete.
 */
const deleteInventoryItem = (inventoryId) => {
  return api.delete(`/inventory/${inventoryId}`);
};

export const inventoryService = {
  getInventory,
  createInventoryItem,
  updateInventoryItem,
  deleteInventoryItem,
};