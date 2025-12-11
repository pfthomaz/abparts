// frontend/src/services/api.js

import { processError } from '../utils/errorHandling';

// Use relative path in production (works with nginx proxy), absolute in development
export const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 
  (window.location.hostname === 'localhost' ? 'http://localhost:8000' : '/api');

/**
 * A generic request handler that abstracts the fetch API.
 * It automatically adds the Authorization header if a token is available.
 * @param {string} endpoint The API endpoint to call (e.g., '/users/me').
 * @param {string} [method='GET'] The HTTP method.
 * @param {object} [body=null] The request body for POST/PUT requests.
 * @param {number} [timeout=30000] Request timeout in milliseconds.
 * @returns {Promise<any>} The JSON response from the API.
 * @throws {Error} Throws an error if the network request fails or the API returns a non-OK status.
 */
const request = async (endpoint, method = 'GET', body = null, timeout = 30000) => {
  const token = localStorage.getItem('authToken');
  const headers = new Headers();

  if (!(body instanceof FormData)) {
    headers.append('Content-Type', 'application/json');
  }

  if (token) {
    headers.append('Authorization', `Bearer ${token}`);
  }

  const config = {
    method,
    headers,
  };

  if (body) {
    config.body = body instanceof FormData ? body : JSON.stringify(body);
  }

  // Create an AbortController for timeout handling
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), timeout);
  config.signal = controller.signal;

  try {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, config);
    clearTimeout(timeoutId);

    if (!response.ok) {
      // Try to parse error response as JSON
      const errorData = await response.json().catch(() => ({
        detail: `Request failed with status ${response.status}`
      }));

      // Create an error object with additional properties for better error handling
      const error = new Error(errorData.detail || `Request failed with status ${response.status}`);
      error.response = {
        status: response.status,
        data: errorData,
        headers: response.headers
      };
      throw error;
    }

    // Handle responses that might not have a body (e.g., 204 No Content)
    if (response.status === 204) {
      return null;
    }

    return response.json();
  } catch (error) {
    clearTimeout(timeoutId);

    // Handle abort/timeout
    if (error.name === 'AbortError') {
      const timeoutError = new Error('Request timed out');
      timeoutError.code = 'ECONNABORTED';
      timeoutError.request = true;
      throw timeoutError;
    }

    // Handle network errors
    if (!error.response) {
      error.request = true;
    }

    // Log the error for debugging
    console.error(`API Error (${endpoint}):`, error);

    // Rethrow the original error to preserve structure for proper error handling
    throw error;
  }
};

// Helper methods for common HTTP verbs
export const api = {
  get: (endpoint) => request(endpoint, 'GET'),
  post: (endpoint, body) => request(endpoint, 'POST', body),
  put: (endpoint, body) => request(endpoint, 'PUT', body),
  patch: (endpoint, body) => request(endpoint, 'PATCH', body),
  delete: (endpoint) => request(endpoint, 'DELETE'),
};