// frontend/src/services/netCleaningRecordsService.js

import { api } from './api';

/**
 * Fetches cleaning records with various filters.
 * @param {object} filters Filter options.
 * @param {string} filters.netId Filter by net ID.
 * @param {string} filters.farmSiteId Filter by farm site ID.
 * @param {string} filters.machineId Filter by machine ID.
 * @param {string} filters.operatorName Filter by operator name.
 * @param {string} filters.startDate Filter by start date (YYYY-MM-DD).
 * @param {string} filters.endDate Filter by end date (YYYY-MM-DD).
 * @param {number} skip Number of records to skip.
 * @param {number} limit Maximum number of records to return.
 */
const getCleaningRecords = (filters = {}, skip = 0, limit = 100) => {
  const params = new URLSearchParams();
  params.append('skip', skip);
  params.append('limit', limit);
  
  if (filters.netId) params.append('net_id', filters.netId);
  if (filters.farmSiteId) params.append('farm_site_id', filters.farmSiteId);
  if (filters.machineId) params.append('machine_id', filters.machineId);
  if (filters.operatorName) params.append('operator_name', filters.operatorName);
  if (filters.startDate) params.append('start_date', filters.startDate);
  if (filters.endDate) params.append('end_date', filters.endDate);
  
  return api.get(`/net-cleaning-records/?${params.toString()}`);
};

/**
 * Gets cleaning statistics for the organization.
 * @param {string} startDate Optional start date for statistics (YYYY-MM-DD).
 * @param {string} endDate Optional end date for statistics (YYYY-MM-DD).
 */
const getCleaningStatistics = (startDate = null, endDate = null) => {
  const params = new URLSearchParams();
  if (startDate) params.append('start_date', startDate);
  if (endDate) params.append('end_date', endDate);
  
  const queryString = params.toString();
  return api.get(`/net-cleaning-records/stats${queryString ? '?' + queryString : ''}`);
};

/**
 * Gets most recent cleaning records.
 * @param {number} limit Number of recent records to return.
 */
const getRecentCleaningRecords = (limit = 10) => {
  return api.get(`/net-cleaning-records/recent?limit=${limit}`);
};

/**
 * Fetches a single cleaning record by ID with details.
 * @param {string} recordId The ID of the cleaning record to fetch.
 */
const getCleaningRecord = (recordId) => {
  return api.get(`/net-cleaning-records/${recordId}`);
};

/**
 * Creates a new cleaning record.
 * @param {object} recordData The data for the new cleaning record.
 */
const createCleaningRecord = (recordData) => {
  return api.post('/net-cleaning-records/', recordData);
};

/**
 * Updates an existing cleaning record.
 * @param {string} recordId The ID of the cleaning record to update.
 * @param {object} recordData The updated data for the cleaning record.
 */
const updateCleaningRecord = (recordId, recordData) => {
  return api.put(`/net-cleaning-records/${recordId}`, recordData);
};

/**
 * Deletes a cleaning record.
 * @param {string} recordId The ID of the cleaning record to delete.
 */
const deleteCleaningRecord = (recordId) => {
  return api.delete(`/net-cleaning-records/${recordId}`);
};

/**
 * Gets cleaning records for a specific net.
 * @param {string} netId The ID of the net.
 * @param {number} skip Number of records to skip.
 * @param {number} limit Maximum number of records to return.
 */
const getCleaningRecordsByNet = (netId, skip = 0, limit = 100) => {
  return getCleaningRecords({ netId }, skip, limit);
};

/**
 * Gets cleaning records for a specific farm site.
 * @param {string} farmSiteId The ID of the farm site.
 * @param {number} skip Number of records to skip.
 * @param {number} limit Maximum number of records to return.
 */
const getCleaningRecordsByFarmSite = (farmSiteId, skip = 0, limit = 100) => {
  return getCleaningRecords({ farmSiteId }, skip, limit);
};

/**
 * Gets cleaning records for a specific machine.
 * @param {string} machineId The ID of the machine.
 * @param {number} skip Number of records to skip.
 * @param {number} limit Maximum number of records to return.
 */
const getCleaningRecordsByMachine = (machineId, skip = 0, limit = 100) => {
  return getCleaningRecords({ machineId }, skip, limit);
};

/**
 * Gets cleaning records for a date range.
 * @param {string} startDate Start date (YYYY-MM-DD).
 * @param {string} endDate End date (YYYY-MM-DD).
 * @param {number} skip Number of records to skip.
 * @param {number} limit Maximum number of records to return.
 */
const getCleaningRecordsByDateRange = (startDate, endDate, skip = 0, limit = 100) => {
  return getCleaningRecords({ startDate, endDate }, skip, limit);
};

const netCleaningRecordsService = {
  getCleaningRecords,
  getCleaningStatistics,
  getRecentCleaningRecords,
  getCleaningRecord,
  createCleaningRecord,
  updateCleaningRecord,
  deleteCleaningRecord,
  getCleaningRecordsByNet,
  getCleaningRecordsByFarmSite,
  getCleaningRecordsByMachine,
  getCleaningRecordsByDateRange,
};

export default netCleaningRecordsService;
