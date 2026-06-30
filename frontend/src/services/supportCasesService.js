// frontend/src/services/supportCasesService.js

/**
 * Service for interacting with the Support Cases API on the AI Assistant microservice.
 */

const getBaseUrl = () => {
  return process.env.NODE_ENV === 'production'
    ? '/ai'
    : (process.env.REACT_APP_AI_ASSISTANT_URL || 'http://localhost:8001');
};

const getHeaders = () => {
  const token = localStorage.getItem('authToken');
  const headers = { 'Content-Type': 'application/json' };
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }
  return headers;
};

const handleResponse = async (response) => {
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: `Request failed with status ${response.status}` }));
    throw new Error(error.detail || `Request failed with status ${response.status}`);
  }
  return response.json();
};

/**
 * Create a new support case.
 */
export const createSupportCase = async (caseData) => {
  const response = await fetch(`${getBaseUrl()}/api/ai/support-cases`, {
    method: 'POST',
    headers: getHeaders(),
    body: JSON.stringify(caseData),
  });
  return handleResponse(response);
};

/**
 * List support cases with optional filters.
 */
export const listSupportCases = async (filters = {}) => {
  const params = new URLSearchParams();
  Object.entries(filters).forEach(([key, value]) => {
    if (value !== null && value !== undefined && value !== '') {
      params.append(key, value);
    }
  });
  const queryString = params.toString();
  const url = `${getBaseUrl()}/api/ai/support-cases${queryString ? `?${queryString}` : ''}`;

  const response = await fetch(url, {
    method: 'GET',
    headers: getHeaders(),
  });
  return handleResponse(response);
};

/**
 * Get a specific support case by ID.
 */
export const getSupportCase = async (caseId) => {
  const response = await fetch(`${getBaseUrl()}/api/ai/support-cases/${caseId}`, {
    method: 'GET',
    headers: getHeaders(),
  });
  return handleResponse(response);
};

/**
 * Update a support case.
 */
export const updateSupportCase = async (caseId, updates) => {
  const response = await fetch(`${getBaseUrl()}/api/ai/support-cases/${caseId}`, {
    method: 'PUT',
    headers: getHeaders(),
    body: JSON.stringify(updates),
  });
  return handleResponse(response);
};

/**
 * Resolve a support case.
 */
export const resolveSupportCase = async (caseId, resolutionData) => {
  const response = await fetch(`${getBaseUrl()}/api/ai/support-cases/${caseId}/resolve`, {
    method: 'POST',
    headers: getHeaders(),
    body: JSON.stringify(resolutionData),
  });
  return handleResponse(response);
};

/**
 * Add a comment to a support case.
 */
export const addComment = async (caseId, commentData) => {
  const response = await fetch(`${getBaseUrl()}/api/ai/support-cases/${caseId}/comments`, {
    method: 'POST',
    headers: getHeaders(),
    body: JSON.stringify(commentData),
  });
  return handleResponse(response);
};

/**
 * List comments for a support case.
 */
export const listComments = async (caseId, includeInternal = true) => {
  const response = await fetch(
    `${getBaseUrl()}/api/ai/support-cases/${caseId}/comments?include_internal=${includeInternal}`,
    {
      method: 'GET',
      headers: getHeaders(),
    }
  );
  return handleResponse(response);
};

/**
 * Get support case statistics.
 */
export const getSupportCaseStats = async () => {
  const response = await fetch(`${getBaseUrl()}/api/ai/support-cases/stats`, {
    method: 'GET',
    headers: getHeaders(),
  });
  return handleResponse(response);
};
