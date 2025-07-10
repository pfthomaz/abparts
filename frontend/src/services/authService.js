// c:/abparts/frontend/src/services/authService.js

import { api } from './api';

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000';

/**
 * Logs in a user. This function uses a direct fetch call because the OAuth2
 * token endpoint expects 'application/x-www-form-urlencoded' content type,
 * which differs from the standard JSON API calls handled by the generic client.
 * @param {string} username The user's username.
 * @param {string} password The user's password.
 * @returns {Promise<{access_token: string, token_type: string}>} The token object.
 */
const login = async (username, password) => {
  const formData = new URLSearchParams();
  formData.append('grant_type', 'password');
  formData.append('username', username);
  formData.append('password', password);

  const response = await fetch(`${API_BASE_URL}/token`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
    },
    body: formData.toString(),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({ detail: 'An unknown error occurred.' }));
    const errorMessage = errorData.detail || `Request failed with status ${response.status}`;
    throw new Error(errorMessage);
  }
  return response.json();
};

/**
 * Fetches the details of the currently authenticated user.
 */
const getCurrentUser = () => {
  return api.get('/users/me/');
};

export const authService = {
  login,
  getCurrentUser,
};