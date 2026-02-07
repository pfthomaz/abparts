// c:/abparts/frontend/src/services/machinesService.js

import { api } from './api';
import { isOnline } from '../hooks/useNetworkStatus';
import { 
  cacheData, 
  getCachedData, 
  isCacheStale, 
  STORES 
} from '../db/indexedDB';

/**
 * Fetches all machines with caching support.
 */
const getMachines = async (forceRefresh = false) => {
  const online = isOnline();
  
  // If offline, use cache immediately
  if (!online) {
    const cached = await getCachedData(STORES.MACHINES);
    if (cached.length > 0) {
      console.log('[MachinesService] Using cached machines (offline):', cached.length);
      return cached;
    }
    throw new Error('No cached data available offline');
  }
  
  // Check cache staleness with timeout to prevent blocking
  let cacheStale = true;
  try {
    const staleCheckPromise = isCacheStale(STORES.MACHINES);
    const timeoutPromise = new Promise((resolve) => setTimeout(() => resolve(true), 1000));
    cacheStale = await Promise.race([staleCheckPromise, timeoutPromise]);
  } catch (error) {
    console.warn('[MachinesService] Cache staleness check failed:', error);
    cacheStale = true; // Assume stale on error
  }
  
  // Use cache if fresh and not forcing refresh
  if (!cacheStale && !forceRefresh) {
    const cached = await getCachedData(STORES.MACHINES);
    if (cached.length > 0) {
      console.log('[MachinesService] Using cached machines (fresh):', cached.length);
      return cached;
    }
  }
  
  // Fetch from API with timeout
  try {
    const data = await api.get('/machines/');
    
    // Map latest_hours to current_hours for frontend compatibility
    const mappedData = data.map(machine => ({
      ...machine,
      current_hours: machine.latest_hours // Map backend field to frontend field
    }));
    
    // Cache the mapped response
    await cacheData(STORES.MACHINES, mappedData);
    console.log('[MachinesService] Cached machines:', mappedData.length);
    
    return mappedData;
  } catch (error) {
    // Fallback to cache on error
    console.warn('[MachinesService] API failed, attempting cache fallback:', error.message);
    const cached = await getCachedData(STORES.MACHINES);
    if (cached.length > 0) {
      console.log('[MachinesService] Using cached machines (fallback):', cached.length);
      return cached;
    }
    
    throw error;
  }
};

/**
 * Fetches a single machine by ID.
 * @param {string} machineId The ID of the machine to fetch.
 */
const getMachine = (machineId) => {
  return api.get(`/machines/${machineId}`);
};

/**
 * Creates a new machine.
 * @param {object} machineData The data for the new machine.
 */
const createMachine = (machineData) => {
  return api.post('/machines/', machineData);
};

/**
 * Updates an existing machine.
 * @param {string} machineId The ID of the machine to update.
 * @param {object} machineData The updated data for the machine.
 */
const updateMachine = (machineId, machineData) => {
  return api.put(`/machines/${machineId}`, machineData);
};

/**
 * Deletes a machine.
 * @param {string} machineId The ID of the machine to delete.
 */
const deleteMachine = (machineId) => {
  return api.delete(`/machines/${machineId}`);
};

/**
 * Transfers a machine to a new customer organization.
 * @param {object} transferData The transfer data including machine_id and new_customer_organization_id.
 */
const transferMachine = (transferData) => {
  return api.post('/machines/transfer', transferData);
};

/**
 * Gets maintenance history for a specific machine.
 * @param {string} machineId The ID of the machine.
 * @param {number} skip Number of records to skip.
 * @param {number} limit Maximum number of records to return.
 */
const getMaintenanceHistory = (machineId, skip = 0, limit = 100) => {
  return api.get(`/machines/${machineId}/maintenance?skip=${skip}&limit=${limit}`);
};

/**
 * Creates a new maintenance record for a machine.
 * @param {string} machineId The ID of the machine.
 * @param {object} maintenanceData The maintenance record data.
 */
const createMaintenanceRecord = (machineId, maintenanceData) => {
  return api.post(`/machines/${machineId}/maintenance`, maintenanceData);
};

/**
 * Adds a part to a maintenance record.
 * @param {string} machineId The ID of the machine.
 * @param {string} maintenanceId The ID of the maintenance record.
 * @param {object} partUsageData The part usage data.
 */
const addPartToMaintenance = (machineId, maintenanceId, partUsageData) => {
  return api.post(`/machines/${machineId}/maintenance/${maintenanceId}/parts`, partUsageData);
};

/**
 * Gets compatible parts for a specific machine.
 * @param {string} machineId The ID of the machine.
 * @param {number} skip Number of records to skip.
 * @param {number} limit Maximum number of records to return.
 */
const getCompatibleParts = (machineId, skip = 0, limit = 100) => {
  return api.get(`/machines/${machineId}/compatible-parts?skip=${skip}&limit=${limit}`);
};

/**
 * Adds a compatible part to a machine.
 * @param {string} machineId The ID of the machine.
 * @param {object} compatibilityData The compatibility data.
 */
const addCompatiblePart = (machineId, compatibilityData) => {
  return api.post(`/machines/${machineId}/compatible-parts`, compatibilityData);
};

/**
 * Removes a compatible part from a machine.
 * @param {string} machineId The ID of the machine.
 * @param {string} partId The ID of the part to remove.
 */
const removeCompatiblePart = (machineId, partId) => {
  return api.delete(`/machines/${machineId}/compatible-parts/${partId}`);
};

/**
 * Gets part usage history for a specific machine.
 * @param {string} machineId The ID of the machine.
 * @param {number} skip Number of records to skip.
 * @param {number} limit Maximum number of records to return.
 */
const getUsageHistory = (machineId, skip = 0, limit = 100) => {
  return api.get(`/machines/${machineId}/usage-history?skip=${skip}&limit=${limit}`);
};

/**
 * Records machine hours for a specific machine.
 * @param {string} machineId The ID of the machine.
 * @param {object} hoursData The hours data to record.
 */
const recordMachineHours = (machineId, hoursData) => {
  return api.post(`/machines/${machineId}/hours`, hoursData);
};

/**
 * Gets machine hours history for a specific machine.
 * @param {string} machineId The ID of the machine.
 * @param {number} skip Number of records to skip.
 * @param {number} limit Maximum number of records to return.
 */
const getMachineHours = (machineId, skip = 0, limit = 100) => {
  return api.get(`/machines/${machineId}/hours?skip=${skip}&limit=${limit}`);
};

/**
 * Updates machine name (admin only).
 * @param {string} machineId The ID of the machine.
 * @param {string} name The new machine name.
 */
const updateMachineName = (machineId, name) => {
  return api.put(`/machines/${machineId}/name`, { name });
};

export const machinesService = {
  getMachines,
  getMachine,
  createMachine,
  updateMachine,
  deleteMachine,
  transferMachine,
  getMaintenanceHistory,
  createMaintenanceRecord,
  addPartToMaintenance,
  getCompatibleParts,
  addCompatiblePart,
  removeCompatiblePart,
  getUsageHistory,
  recordMachineHours,
  getMachineHours,
  updateMachineName,
};