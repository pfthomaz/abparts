import { api } from './api';

/**
 * Fetches all users.
 */
const getUsers = () => {
  return api.get('/users');
};

/**
 * Creates a new user.
 * @param {object} userData The data for the new user.
 */
const createUser = (userData) => {
  return api.post('/users', userData);
};

/**
 * Updates an existing user.
 * @param {string} userId The ID of the user to update.
 * @param {object} userData The updated data for the user.
 */
const updateUser = (userId, userData) => {
  return api.put(`/users/${userId}`, userData);
};

/**
 * Deactivates (deletes) a user.
 * @param {string} userId The ID of the user to deactivate.
 */
const deactivateUser = (userId) => {
  return api.delete(`/users/${userId}`);
};

/**
 * Reactivates a user.
 * @param {string} userId The ID of the user to reactivate.
 */
const reactivateUser = (userId) => {
  return api.post(`/users/${userId}/reactivate`);
};

export const userService = {
  getUsers,
  createUser,
  updateUser,
  deactivateUser,
  reactivateUser,
};