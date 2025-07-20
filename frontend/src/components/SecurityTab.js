// frontend/src/components/SecurityTab.js

import React from 'react';

const SecurityTab = ({
  setShowPasswordModal,
  setShowEmailModal,
  setShowPasswordResetModal
}) => {
  return (
    <div className="space-y-6">
      <h3 className="text-lg font-semibold text-gray-800">Security Settings</h3>

      {/* Password Management */}
      <div className="bg-gray-50 p-4 rounded-lg">
        <h4 className="text-md font-semibold text-gray-800 mb-3">Password Management</h4>
        <div className="space-y-3">
          <div className="flex justify-between items-center">
            <div>
              <p className="text-gray-800 font-medium">Change Password</p>
              <p className="text-sm text-gray-600">
                Update your password to keep your account secure
              </p>
            </div>
            <button
              onClick={() => setShowPasswordModal(true)}
              className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              Change Password
            </button>
          </div>

          <div className="border-t pt-3">
            <div className="flex justify-between items-center">
              <div>
                <p className="text-gray-800 font-medium">Password Reset</p>
                <p className="text-sm text-gray-600">
                  Request a password reset link via email
                </p>
              </div>
              <button
                onClick={() => setShowPasswordResetModal(true)}
                className="px-4 py-2 bg-gray-600 text-white rounded-md hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-gray-500"
              >
                Request Reset
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Email Management */}
      <div className="bg-gray-50 p-4 rounded-lg">
        <h4 className="text-md font-semibold text-gray-800 mb-3">Email Management</h4>
        <div className="flex justify-between items-center">
          <div>
            <p className="text-gray-800 font-medium">Change Email Address</p>
            <p className="text-sm text-gray-600">
              Update your email address with verification
            </p>
          </div>
          <button
            onClick={() => setShowEmailModal(true)}
            className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500"
          >
            Change Email
          </button>
        </div>
      </div>

      {/* Security Tips */}
      <div className="bg-blue-50 p-4 rounded-lg">
        <h4 className="text-md font-semibold text-blue-800 mb-3">Security Tips</h4>
        <ul className="space-y-2 text-sm text-blue-700">
          <li className="flex items-start">
            <span className="text-blue-500 mr-2">•</span>
            Use a strong password with at least 8 characters, including uppercase, lowercase, numbers, and symbols
          </li>
          <li className="flex items-start">
            <span className="text-blue-500 mr-2">•</span>
            Don't share your password with anyone or use the same password for multiple accounts
          </li>
          <li className="flex items-start">
            <span className="text-blue-500 mr-2">•</span>
            Change your password regularly and immediately if you suspect it has been compromised
          </li>
          <li className="flex items-start">
            <span className="text-blue-500 mr-2">•</span>
            Always log out when using shared or public computers
          </li>
          <li className="flex items-start">
            <span className="text-blue-500 mr-2">•</span>
            Keep your email address up to date for important security notifications
          </li>
        </ul>
      </div>
    </div>
  );
};

export default SecurityTab;