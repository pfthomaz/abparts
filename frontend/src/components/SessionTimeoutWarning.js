// frontend/src/components/SessionTimeoutWarning.js

import React, { useState, useEffect } from 'react';
import { useAuth } from '../AuthContext';

const SessionTimeoutWarning = () => {
  const { token, logout } = useAuth();
  const [showWarning, setShowWarning] = useState(false);
  const [timeLeft, setTimeLeft] = useState(0);
  const [extendingSession, setExtendingSession] = useState(false);

  useEffect(() => {
    if (!token) return;

    // Mock session expiry check - in real implementation this would come from JWT token
    const checkSessionExpiry = () => {
      try {
        // Decode JWT token to get expiry time (simplified mock)
        const tokenPayload = JSON.parse(atob(token.split('.')[1]));
        const expiryTime = tokenPayload.exp * 1000; // Convert to milliseconds
        const currentTime = Date.now();
        const timeUntilExpiry = expiryTime - currentTime;
        const minutesLeft = Math.floor(timeUntilExpiry / (1000 * 60));

        // Show warning when 15 minutes or less remain
        if (minutesLeft <= 15 && minutesLeft > 0) {
          setTimeLeft(minutesLeft);
          setShowWarning(true);
        } else if (minutesLeft <= 0) {
          // Session expired
          logout();
        } else {
          setShowWarning(false);
        }
      } catch (error) {
        // If token parsing fails, assume it's valid for now
        console.error('Error parsing token for expiry check:', error);
      }
    };

    // Check immediately and then every minute
    checkSessionExpiry();
    const interval = setInterval(checkSessionExpiry, 60000);

    return () => clearInterval(interval);
  }, [token, logout]);

  const handleExtendSession = async () => {
    try {
      setExtendingSession(true);
      // In real implementation, this would call a refresh token endpoint
      // await authService.refreshToken();

      // Mock successful extension
      setTimeout(() => {
        setShowWarning(false);
        setExtendingSession(false);
      }, 1000);
    } catch (error) {
      console.error('Failed to extend session:', error);
      setExtendingSession(false);
    }
  };

  const handleLogoutNow = () => {
    logout();
  };

  if (!showWarning) return null;

  return (
    <div className="fixed top-4 right-4 z-50 max-w-sm">
      <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 shadow-lg">
        <div className="flex items-start">
          <div className="flex-shrink-0">
            <span className="text-yellow-600 text-xl">⏰</span>
          </div>
          <div className="ml-3 flex-1">
            <h3 className="text-sm font-medium text-yellow-800">
              Session Expiring Soon
            </h3>
            <p className="text-sm text-yellow-700 mt-1">
              Your session will expire in {timeLeft} minute{timeLeft !== 1 ? 's' : ''}.
              Would you like to extend your session?
            </p>
            <div className="mt-3 flex space-x-2">
              <button
                onClick={handleExtendSession}
                disabled={extendingSession}
                className="px-3 py-1 text-xs bg-yellow-600 text-white rounded hover:bg-yellow-700 focus:outline-none focus:ring-2 focus:ring-yellow-500 disabled:opacity-50"
              >
                {extendingSession ? 'Extending...' : 'Extend Session'}
              </button>
              <button
                onClick={handleLogoutNow}
                className="px-3 py-1 text-xs bg-gray-600 text-white rounded hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-gray-500"
              >
                Logout Now
              </button>
            </div>
          </div>
          <div className="ml-2">
            <button
              onClick={() => setShowWarning(false)}
              className="text-yellow-400 hover:text-yellow-600"
            >
              <span className="sr-only">Close</span>
              <svg className="h-4 w-4" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
              </svg>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SessionTimeoutWarning;