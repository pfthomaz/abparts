// c:/abparts/frontend/src/services/partsService.js

import { api } from './api';

/**
 * Fetches all parts.
 */
const getParts = () => {
  return api.get('/parts');
};

/**
 * Creates a new part.
 * @param {object} partData The data for the new part.
 */
const createPart = (partData) => {
  return api.post('/parts', partData);
};

/**
 * Updates an existing part.
 * @param {string} partId The ID of the part to update.
 * @param {object} partData The updated data for the part.
 */
const updatePart = (partId, partData) => {
  return api.put(`/parts/${partId}`, partData);
};

/**
 * Deletes a part.
 * @param {string} partId The ID of the part to delete.
 */
const deletePart = (partId) => {
  return api.delete(`/parts/${partId}`);
};

export const partsService = {
  getParts,
  createPart,
  updatePart,
  deletePart,
};