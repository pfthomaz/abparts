// frontend/src/services/maintenanceProtocolsService.js

import { api } from './api';

// Protocol Management

export const listProtocols = async (filters = {}) => {
  const params = new URLSearchParams();
  if (filters.protocol_type) params.append('protocol_type', filters.protocol_type);
  if (filters.machine_model) params.append('machine_model', filters.machine_model);
  if (filters.is_active !== undefined) params.append('is_active', filters.is_active);
  if (filters.search) params.append('search', filters.search);
  
  return api.get(`/maintenance-protocols/?${params}`);
};

export const getProtocol = async (protocolId) => {
  return api.get(`/maintenance-protocols/${protocolId}`);
};

export const createProtocol = async (protocolData) => {
  return api.post('/maintenance-protocols/', protocolData);
};

export const updateProtocol = async (protocolId, protocolData) => {
  return api.put(`/maintenance-protocols/${protocolId}`, protocolData);
};

export const deleteProtocol = async (protocolId) => {
  return api.delete(`/maintenance-protocols/${protocolId}`);
};

export const duplicateProtocol = async (protocolId, duplicateData) => {
  return api.post(`/maintenance-protocols/${protocolId}/duplicate`, duplicateData);
};

// Checklist Item Management

export const getChecklistItems = async (protocolId) => {
  return api.get(`/maintenance-protocols/${protocolId}/checklist-items`);
};

export const createChecklistItem = async (protocolId, itemData) => {
  return api.post(`/maintenance-protocols/${protocolId}/checklist-items`, itemData);
};

export const updateChecklistItem = async (protocolId, itemId, itemData) => {
  return api.put(`/maintenance-protocols/${protocolId}/checklist-items/${itemId}`, itemData);
};

export const deleteChecklistItem = async (protocolId, itemId) => {
  return api.delete(`/maintenance-protocols/${protocolId}/checklist-items/${itemId}`);
};

export const reorderChecklistItems = async (protocolId, itemOrders) => {
  return api.post(`/maintenance-protocols/${protocolId}/checklist-items/reorder`, { item_orders: itemOrders });
};

// User-facing endpoints

export const getProtocolsForMachine = async (machineId) => {
  return api.get(`/maintenance-protocols/for-machine/${machineId}`);
};

export const getExecutions = async (skip = 0, limit = 100) => {
  return api.get(`/maintenance-protocols/executions?skip=${skip}&limit=${limit}`);
};

export const createExecution = async (executionData) => {
  return api.post('/maintenance-protocols/executions', executionData);
};

export const completeChecklistItem = async (executionId, itemId, completionData) => {
  return api.post(`/maintenance-protocols/executions/${executionId}/checklist/${itemId}/complete`, completionData);
};

export const completeExecution = async (executionId) => {
  return api.put(`/maintenance-protocols/executions/${executionId}/complete`);
};

export const getExecutionsForMachine = async (machineId, skip = 0, limit = 50) => {
  return api.get(`/maintenance-protocols/executions/machine/${machineId}?skip=${skip}&limit=${limit}`);
};

export const getPendingReminders = async () => {
  return api.get('/maintenance-protocols/reminders/pending/');
};

export const acknowledgeReminder = async (reminderId) => {
  return api.put(`/maintenance-protocols/reminders/${reminderId}/acknowledge`);
};
