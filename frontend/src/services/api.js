// c:/abparts/frontend/src/services/api.js

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000';

/**
 * A generic request handler that abstracts the fetch API.
 * It automatically adds the Authorization header if a token is available.
 * @param {string} endpoint The API endpoint to call (e.g., '/users/me').
 * @param {string} [method='GET'] The HTTP method.
 * @param {object} [body=null] The request body for POST/PUT requests.
 * @returns {Promise<any>} The JSON response from the API.
 * @throws {Error} Throws an error if the network request fails or the API returns a non-OK status.
 */
const request = async (endpoint, method = 'GET', body = null) => {
  const token = localStorage.getItem('authToken');
  const headers = new Headers({
    'Content-Type': 'application/json',
  });

  if (token) {
    headers.append('Authorization', `Bearer ${token}`);
  }

  const config = {
    method,
    headers,
  };

  if (body) {
    config.body = JSON.stringify(body);
  }

  const response = await fetch(`${API_BASE_URL}${endpoint}`, config);

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({ detail: 'An unknown error occurred.' }));
    const errorMessage = errorData.detail || `Request failed with status ${response.status}`;
    throw new Error(errorMessage);
  }

  // Handle responses that might not have a body (e.g., 204 No Content)
  if (response.status === 204) {
    return null;
  }
  return response.json();
};

// Helper methods for common HTTP verbs
export const api = {
  get: (endpoint) => request(endpoint, 'GET'),
  post: (endpoint, body) => request(endpoint, 'POST', body),
  put: (endpoint, body) => request(endpoint, 'PUT', body),
  delete: (endpoint) => request(endpoint, 'DELETE'),
};