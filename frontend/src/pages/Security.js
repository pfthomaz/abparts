// frontend/src/pages/Security.js

import React, { useState } from 'react';
import { useAuth } from '../AuthContext';
import SecurityDashboard from '../components/SecurityDashboard';
import SecurityTab from '../components/SecurityTab';
import SessionsTab from '../components/SessionsTab';
import Modal from '../components/Modal';
import { userService } from '../services/userService';

const Security = () => {
  const { logout } = useAuth();
  const [activeTab, setActiveTab] = useState('dashboard');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  // Password change state
  const [showPasswordModal, setShowPasswordModal] = useState(false);
  const [passwordForm, setPasswordForm] = useState({
    current_password: '',
    new_password: '',
    confirm_password: ''
  });

  // Email change state
  const [showEmailModal, setShowEmailModal] = useState(false);
  const [emailForm, setEmailForm] = useState({
    new_email: '',
    password: ''
  });

  // Password reset state
  const [showPasswordResetModal, setShowPasswordResetModal] = useState(false);
  const [resetEmail, setResetEmail] = useState('');

  // Sessions state
  const [sessions, setSessions] = useState([]);
  const [loadingSessions, setLoadingSessions] = useState(false);

  const fetchSessions = async () => {
    try {
      setLoadingSessions(true);
      const sessionsData = await userService.getMySessions();
      setSessions(sessionsData);
    } catch (err) {
      console.error('Sessions fetch error:', err);
    } finally {
      setLoadingSessions(false);
    }
  };

  const handlePasswordChange = async (e) => {
    e.preventDefault();
    try {
      setError('');
      setSuccess('');

      if (passwordForm.new_password !== passwordForm.confirm_password) {
        setError('New passwords do not match');
        return;
      }

      if (passwordForm.new_password.length < 8) {
        setError('New password must be at least 8 characters long');
        return;
      }

      await userService.changeMyPassword({
        current_password: passwordForm.current_password,
        new_password: passwordForm.new_password
      });

      setSuccess('Password changed successfully. You will be logged out.');
      setShowPasswordModal(false);
      setPasswordForm({ current_password: '', new_password: '', confirm_password: '' });

      // Log out user after password change for security
      setTimeout(() => {
        logout();
      }, 2000);
    } catch (err) {
      setError(err.message || 'Failed to change password');
    }
  };

  const handleEmailChange = async (e) => {
    e.preventDefault();
    try {
      setError('');
      setSuccess('');

      await userService.requestEmailVerification(emailForm.new_email);
      setSuccess('Email verification sent. Please check your new email address.');
      setShowEmailModal(false);
      setEmailForm({ new_email: '', password: '' });
    } catch (err) {
      setError(err.message || 'Failed to request email change');
    }
  };

  const handlePasswordReset = async (e) => {
    e.preventDefault();
    try {
      setError('');
      setSuccess('');

      await userService.requestPasswordReset(resetEmail);
      setSuccess('Password reset instructions sent to your email');
      setShowPasswordResetModal(false);
      setResetEmail('');
    } catch (err) {
      setError(err.message || 'Failed to request password reset');
    }
  };

  const handleTerminateSession = async (sessionToken) => {
    try {
      await userService.terminateMySession(sessionToken);
      setSuccess('Session terminated successfully');
      await fetchSessions(); // Refresh sessions list
    } catch (err) {
      setError(err.message || 'Failed to terminate session');
    }
  };

  const handleTerminateAllSessions = async () => {
    try {
      await userService.terminateAllMySessions();
      setSuccess('All sessions terminated. You will be logged out.');
      setTimeout(() => {
        logout();
      }, 2000);
    } catch (err) {
      setError(err.message || 'Failed to terminate all sessions');
    }
  };

  return (
    <div className="max-w-6xl mx-auto">
      <div className="bg-white shadow-lg rounded-lg overflow-hidden">
        {/* Header */}
        <div className="bg-red-600 text-white px-6 py-4">
          <h1 className="text-2xl font-bold">Security Center</h1>
          <p className="text-red-100">Manage your account security and monitor activity</p>
        </div>

        {/* Alert Messages */}
        {error && (
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 mx-6 mt-4 rounded">
            {error}
          </div>
        )}
        {success && (
          <div className="bg-green-100 border border-green-400 text-green-700 px-4 py-3 mx-6 mt-4 rounded">
            {success}
          </div>
        )}

        {/* Tab Navigation */}
        <div className="border-b border-gray-200">
          <nav className="flex px-6">
            {[
              { id: 'dashboard', label: 'Security Dashboard', icon: '🛡️' },
              { id: 'security', label: 'Security Settings', icon: '⚙️' },
              { id: 'sessions', label: 'Active Sessions', icon: '💻' }
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`py-4 px-6 text-sm font-medium border-b-2 flex items-center space-x-2 ${activeTab === tab.id
                  ? 'border-red-500 text-red-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }`}
              >
                <span>{tab.icon}</span>
                <span>{tab.label}</span>
              </button>
            ))}
          </nav>
        </div>

        {/* Tab Content */}
        <div className="p-6">
          {activeTab === 'dashboard' && <SecurityDashboard />}

          {activeTab === 'security' && (
            <SecurityTab
              setShowPasswordModal={setShowPasswordModal}
              setShowEmailModal={setShowEmailModal}
              setShowPasswordResetModal={setShowPasswordResetModal}
            />
          )}

          {activeTab === 'sessions' && (
            <SessionsTab
              sessions={sessions}
              loadingSessions={loadingSessions}
              fetchSessions={fetchSessions}
              handleTerminateSession={handleTerminateSession}
              handleTerminateAllSessions={handleTerminateAllSessions}
            />
          )}
        </div>
      </div>

      {/* Password Change Modal */}
      <Modal
        isOpen={showPasswordModal}
        onClose={() => setShowPasswordModal(false)}
        title="Change Password"
      >
        <form onSubmit={handlePasswordChange} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Current Password
            </label>
            <input
              type="password"
              value={passwordForm.current_password}
              onChange={(e) => setPasswordForm({ ...passwordForm, current_password: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-red-500"
              required
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              New Password
            </label>
            <input
              type="password"
              value={passwordForm.new_password}
              onChange={(e) => setPasswordForm({ ...passwordForm, new_password: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-red-500"
              minLength="8"
              required
            />
            <p className="text-xs text-gray-500 mt-1">Minimum 8 characters</p>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Confirm New Password
            </label>
            <input
              type="password"
              value={passwordForm.confirm_password}
              onChange={(e) => setPasswordForm({ ...passwordForm, confirm_password: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-red-500"
              required
            />
          </div>
          <div className="flex justify-end space-x-3 pt-4">
            <button
              type="button"
              onClick={() => setShowPasswordModal(false)}
              className="px-4 py-2 text-gray-600 border border-gray-300 rounded-md hover:bg-gray-50"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700"
            >
              Change Password
            </button>
          </div>
        </form>
      </Modal>

      {/* Email Change Modal */}
      <Modal
        isOpen={showEmailModal}
        onClose={() => setShowEmailModal(false)}
        title="Change Email Address"
      >
        <form onSubmit={handleEmailChange} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              New Email Address
            </label>
            <input
              type="email"
              value={emailForm.new_email}
              onChange={(e) => setEmailForm({ ...emailForm, new_email: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-red-500"
              required
            />
            <p className="text-xs text-gray-500 mt-1">
              A verification email will be sent to this address
            </p>
          </div>
          <div className="flex justify-end space-x-3 pt-4">
            <button
              type="button"
              onClick={() => setShowEmailModal(false)}
              className="px-4 py-2 text-gray-600 border border-gray-300 rounded-md hover:bg-gray-50"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700"
            >
              Send Verification
            </button>
          </div>
        </form>
      </Modal>

      {/* Password Reset Modal */}
      <Modal
        isOpen={showPasswordResetModal}
        onClose={() => setShowPasswordResetModal(false)}
        title="Request Password Reset"
      >
        <form onSubmit={handlePasswordReset} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Email Address
            </label>
            <input
              type="email"
              value={resetEmail}
              onChange={(e) => setResetEmail(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-red-500"
              placeholder="Enter your email address"
              required
            />
            <p className="text-xs text-gray-500 mt-1">
              Password reset instructions will be sent to this email
            </p>
          </div>
          <div className="flex justify-end space-x-3 pt-4">
            <button
              type="button"
              onClick={() => setShowPasswordResetModal(false)}
              className="px-4 py-2 text-gray-600 border border-gray-300 rounded-md hover:bg-gray-50"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700"
            >
              Send Reset Link
            </button>
          </div>
        </form>
      </Modal>
    </div>
  );
};

export default Security;