import { api } from './api';

/**
 * Enhanced User Service aligned with new business model
 * Supports comprehensive user management with new role system
 */

// --- Basic User CRUD Operations ---

/**
 * Fetches all users with enhanced filtering
 */
const getUsers = (params = {}) => {
  return api.get('/users/', { params });
};

/**
 * Fetches a single user by ID
 */
const getUser = (userId) => {
  return api.get(`/users/${userId}`);
};

/**
 * Creates a new user
 */
const createUser = (userData) => {
  return api.post('/users/', userData);
};

/**
 * Updates an existing user
 */
const updateUser = (userId, userData) => {
  return api.put(`/users/${userId}`, userData);
};

/**
 * Deactivates a user (soft delete)
 */
const deactivateUser = (userId) => {
  return api.patch(`/users/${userId}/deactivate`);
};

/**
 * Reactivates a user
 */
const reactivateUser = (userId) => {
  return api.patch(`/users/${userId}/reactivate`);
};

// --- Advanced User Administration ---

/**
 * Search users with advanced filtering
 */
const searchUsers = (params = {}) => {
  return api.get('/users/admin/search', { params });
};

/**
 * Get users by organization
 */
const getUsersByOrganization = (organizationId) => {
  return api.get(`/users/organization/${organizationId}/users`);
};

/**
 * Get inactive users (90+ days)
 */
const getInactiveUsers = (daysThreshold = 90) => {
  return api.get('/users/admin/inactive-users', {
    params: { days_threshold: daysThreshold }
  });
};

/**
 * Soft delete a user (prevents deletion if has transactions)
 */
const softDeleteUser = (userId) => {
  return api.delete(`/users/${userId}/soft-delete`);
};

/**
 * Get user management audit logs
 */
const getUserAuditLogs = (userId) => {
  return api.get(`/users/${userId}/audit-logs`);
};

/**
 * Get all user management audit logs
 */
const getAllUserAuditLogs = (params = {}) => {
  return api.get('/users/admin/audit-logs', { params });
};

// --- User Invitation System ---

/**
 * Invite a new user
 */
const inviteUser = (invitationData) => {
  return api.post('/users/invite', invitationData);
};

/**
 * Accept user invitation
 */
const acceptInvitation = (acceptanceData) => {
  return api.post('/users/accept-invitation', acceptanceData);
};

/**
 * Resend user invitation
 */
const resendInvitation = (userId) => {
  return api.post('/users/resend-invitation', { user_id: userId });
};

/**
 * Get pending invitations
 */
const getPendingInvitations = (params = {}) => {
  return api.get('/users/pending-invitations', { params });
};

/**
 * Get invitation audit logs for a user
 */
const getInvitationAuditLogs = (userId) => {
  return api.get(`/users/${userId}/invitation-audit`);
};

// --- User Profile and Self-Service ---

/**
 * Get current user's profile
 */
const getMyProfile = () => {
  return api.get('/users/me/');
};

/**
 * Update current user's profile
 */
const updateMyProfile = (profileData) => {
  return api.put('/users/me/profile', profileData);
};

/**
 * Change current user's password
 */
const changeMyPassword = (passwordData) => {
  return api.post('/users/me/change-password', passwordData);
};

/**
 * Request password reset
 */
const requestPasswordReset = (email) => {
  return api.post('/users/request-password-reset', { email });
};

/**
 * Confirm password reset
 */
const confirmPasswordReset = (resetData) => {
  return api.post('/users/confirm-password-reset', resetData);
};

/**
 * Request email verification
 */
const requestEmailVerification = (newEmail) => {
  return api.post('/users/me/request-email-verification', { new_email: newEmail });
};

/**
 * Confirm email verification
 */
const confirmEmailVerification = (verificationData) => {
  return api.post('/users/confirm-email-verification', verificationData);
};

// --- Session and Security Management ---

/**
 * Get current user's active sessions
 */
const getMySessions = () => {
  return api.get('/users/me/sessions');
};

/**
 * Terminate a specific session
 */
const terminateMySession = (sessionToken) => {
  return api.delete(`/users/me/sessions/${sessionToken}`);
};

/**
 * Terminate all sessions for current user
 */
const terminateAllMySessions = () => {
  return api.delete('/users/me/sessions');
};

/**
 * Logout current user
 */
const logout = () => {
  return api.post('/users/logout');
};

/**
 * Get security events (admin only)
 */
const getSecurityEvents = (params = {}) => {
  return api.get('/users/admin/security-events', { params });
};

/**
 * Terminate all sessions for a specific user (admin only)
 */
const terminateUserSessions = (userId) => {
  return api.delete(`/users/${userId}/sessions`);
};

export const userService = {
  // Basic CRUD
  getUsers,
  getUser,
  createUser,
  updateUser,
  deactivateUser,
  reactivateUser,

  // Advanced Administration
  searchUsers,
  getUsersByOrganization,
  getInactiveUsers,
  softDeleteUser,
  getUserAuditLogs,
  getAllUserAuditLogs,

  // Invitation System
  inviteUser,
  acceptInvitation,
  resendInvitation,
  getPendingInvitations,
  getInvitationAuditLogs,

  // Profile and Self-Service
  getMyProfile,
  updateMyProfile,
  changeMyPassword,
  requestPasswordReset,
  confirmPasswordReset,
  requestEmailVerification,
  confirmEmailVerification,

  // Session and Security
  getMySessions,
  terminateMySession,
  terminateAllMySessions,
  logout,
  getSecurityEvents,
  terminateUserSessions,
};