// c:/abparts/frontend/src/services/stocktakeService.js

import { api } from './api';

/**
 * Fetches all unique stocktake locations.
 * @returns {Promise<Array<{name: string}>>} A promise that resolves to an array of location objects.
 */
const getLocations = () => {
  return api.get('/stocktake/locations');
};

/**
 * Requests the generation of a stocktake worksheet for a specific location.
 * @param {string} locationName The name of the location for the worksheet.
 * @returns {Promise<{message: string, data: Array<object>}>} A promise that resolves to the worksheet data.
 */
const generateWorksheet = (locationName) => {
  return api.post('/stocktake/worksheet', { name: locationName });
};

export const stocktakeService = {
  getLocations,
  generateWorksheet,
};