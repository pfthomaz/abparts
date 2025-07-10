// c:/abparts/frontend/src/services/machinesService.js

import { api } from './api';

/**
 * Fetches all machines.
 */
const getMachines = () => {
  return api.get('/machines');
};

/**
 * Creates a new machine.
 * @param {object} machineData The data for the new machine.
 */
const createMachine = (machineData) => {
  return api.post('/machines', machineData);
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

export const machinesService = {
  getMachines,
  createMachine,
  updateMachine,
  deleteMachine,
};