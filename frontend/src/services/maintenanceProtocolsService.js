// frontend/src/services/maintenanceProtocolsService.js

const API_BASE_URL = '/api';

// Get auth token from localStorage
const getAuthHeader = () => {
  const token = localStorage.getItem('authToken');
  return token ? { 'Authorization': `Bearer ${token}` } : {};
};

// Protocol Management

export const listProtocols = async (filters = {}) => {
  const params = new URLSearchParams();
  if (filters.protocol_type) params.append('protocol_type', filters.protocol_type);
  if (filters.machine_model) params.append('machine_model', filters.machine_model);
  if (filters.is_active !== undefined) params.append('is_active', filters.is_active);
  if (filters.search) params.append('search', filters.search);
  
  const response = await fetch(
    `${API_BASE_URL}/maintenance-protocols?${params}`,
    {
      headers: {
        ...getAuthHeader(),
        'Content-Type': 'application/json',
      },
    }
  );
  
  if (!response.ok) {
    throw new Error(`Failed to fetch protocols: ${response.statusText}`);
  }
  
  return response.json();
};

export const getProtocol = async (protocolId) => {
  const response = await fetch(
    `${API_BASE_URL}/maintenance-protocols/${protocolId}`,
    {
      headers: {
        ...getAuthHeader(),
        'Content-Type': 'application/json',
      },
    }
  );
  
  if (!response.ok) {
    throw new Error(`Failed to fetch protocol: ${response.statusText}`);
  }
  
  return response.json();
};

export const createProtocol = async (protocolData) => {
  const response = await fetch(
    `${API_BASE_URL}/maintenance-protocols`,
    {
      method: 'POST',
      headers: {
        ...getAuthHeader(),
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(protocolData),
    }
  );
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to create protocol');
  }
  
  return response.json();
};

export const updateProtocol = async (protocolId, protocolData) => {
  const response = await fetch(
    `${API_BASE_URL}/maintenance-protocols/${protocolId}`,
    {
      method: 'PUT',
      headers: {
        ...getAuthHeader(),
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(protocolData),
    }
  );
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to update protocol');
  }
  
  return response.json();
};

export const deleteProtocol = async (protocolId) => {
  const response = await fetch(
    `${API_BASE_URL}/maintenance-protocols/${protocolId}`,
    {
      method: 'DELETE',
      headers: {
        ...getAuthHeader(),
      },
    }
  );
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to delete protocol');
  }
};

export const duplicateProtocol = async (protocolId, duplicateData) => {
  const response = await fetch(
    `${API_BASE_URL}/maintenance-protocols/${protocolId}/duplicate`,
    {
      method: 'POST',
      headers: {
        ...getAuthHeader(),
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(duplicateData),
    }
  );
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to duplicate protocol');
  }
  
  return response.json();
};

// Checklist Item Management

export const getChecklistItems = async (protocolId) => {
  const response = await fetch(
    `${API_BASE_URL}/maintenance-protocols/${protocolId}/checklist-items`,
    {
      headers: {
        ...getAuthHeader(),
        'Content-Type': 'application/json',
      },
    }
  );
  
  if (!response.ok) {
    throw new Error(`Failed to fetch checklist items: ${response.statusText}`);
  }
  
  return response.json();
};

export const createChecklistItem = async (protocolId, itemData) => {
  const response = await fetch(
    `${API_BASE_URL}/maintenance-protocols/${protocolId}/checklist-items`,
    {
      method: 'POST',
      headers: {
        ...getAuthHeader(),
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(itemData),
    }
  );
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to create checklist item');
  }
  
  return response.json();
};

export const updateChecklistItem = async (protocolId, itemId, itemData) => {
  const response = await fetch(
    `${API_BASE_URL}/maintenance-protocols/${protocolId}/checklist-items/${itemId}`,
    {
      method: 'PUT',
      headers: {
        ...getAuthHeader(),
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(itemData),
    }
  );
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to update checklist item');
  }
  
  return response.json();
};

export const deleteChecklistItem = async (protocolId, itemId) => {
  const response = await fetch(
    `${API_BASE_URL}/maintenance-protocols/${protocolId}/checklist-items/${itemId}`,
    {
      method: 'DELETE',
      headers: {
        ...getAuthHeader(),
      },
    }
  );
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to delete checklist item');
  }
};

export const reorderChecklistItems = async (protocolId, itemOrders) => {
  const response = await fetch(
    `${API_BASE_URL}/maintenance-protocols/${protocolId}/checklist-items/reorder`,
    {
      method: 'POST',
      headers: {
        ...getAuthHeader(),
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ item_orders: itemOrders }),
    }
  );
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to reorder checklist items');
  }
  
  return response.json();
};

// User-facing endpoints

export const getProtocolsForMachine = async (machineId) => {
  const response = await fetch(
    `${API_BASE_URL}/maintenance-protocols/for-machine/${machineId}`,
    {
      headers: {
        ...getAuthHeader(),
        'Content-Type': 'application/json',
      },
    }
  );
  
  if (!response.ok) {
    throw new Error(`Failed to fetch protocols for machine: ${response.statusText}`);
  }
  
  return response.json();
};

export const getExecutions = async (skip = 0, limit = 100) => {
  const response = await fetch(
    `${API_BASE_URL}/maintenance-protocols/executions?skip=${skip}&limit=${limit}`,
    {
      headers: {
        ...getAuthHeader(),
        'Content-Type': 'application/json',
      },
    }
  );
  
  if (!response.ok) {
    throw new Error(`Failed to fetch executions: ${response.statusText}`);
  }
  
  return response.json();
};

export const createExecution = async (executionData) => {
  const response = await fetch(
    `${API_BASE_URL}/maintenance-protocols/executions`,
    {
      method: 'POST',
      headers: {
        ...getAuthHeader(),
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(executionData),
    }
  );
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to create execution');
  }
  
  return response.json();
};

export const completeChecklistItem = async (executionId, itemId, completionData) => {
  const response = await fetch(
    `${API_BASE_URL}/maintenance-protocols/executions/${executionId}/checklist/${itemId}/complete`,
    {
      method: 'POST',
      headers: {
        ...getAuthHeader(),
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(completionData),
    }
  );
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to complete checklist item');
  }
  
  return response.json();
};

export const completeExecution = async (executionId) => {
  const response = await fetch(
    `${API_BASE_URL}/maintenance-protocols/executions/${executionId}/complete`,
    {
      method: 'PUT',
      headers: {
        ...getAuthHeader(),
        'Content-Type': 'application/json',
      },
    }
  );
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to complete execution');
  }
  
  return response.json();
};

export const getExecutionsForMachine = async (machineId, skip = 0, limit = 50) => {
  const response = await fetch(
    `${API_BASE_URL}/maintenance-protocols/executions/machine/${machineId}?skip=${skip}&limit=${limit}`,
    {
      headers: {
        ...getAuthHeader(),
        'Content-Type': 'application/json',
      },
    }
  );
  
  if (!response.ok) {
    throw new Error(`Failed to fetch executions: ${response.statusText}`);
  }
  
  return response.json();
};

export const getPendingReminders = async () => {
  const response = await fetch(
    `${API_BASE_URL}/maintenance-protocols/reminders/pending`,
    {
      headers: {
        ...getAuthHeader(),
        'Content-Type': 'application/json',
      },
    }
  );
  
  if (!response.ok) {
    throw new Error(`Failed to fetch reminders: ${response.statusText}`);
  }
  
  return response.json();
};

export const acknowledgeReminder = async (reminderId) => {
  const response = await fetch(
    `${API_BASE_URL}/maintenance-protocols/reminders/${reminderId}/acknowledge`,
    {
      method: 'PUT',
      headers: {
        ...getAuthHeader(),
        'Content-Type': 'application/json',
      },
    }
  );
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to acknowledge reminder');
  }
  
  return response.json();
};
