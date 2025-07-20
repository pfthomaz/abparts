// frontend/src/components/SessionsTab.js

import React, { useEffect } from 'react';

const SessionsTab = ({
  sessions,
  loadingSessions,
  fetchSessions,
  handleTerminateSession,
  handleTerminateAllSessions
}) => {
  useEffect(() => {
    fetchSessions();
  }, []);

  const formatDate = (dateString) => {
    if (!dateString) return 'Unknown';
    return new Date(dateString).toLocaleString();
  };

  const getDeviceIcon = (userAgent) => {
    if (!userAgent) return '🖥️';

    const ua = userAgent.toLowerCase();
    if (ua.includes('mobile') || ua.includes('android') || ua.includes('iphone')) {
      return '📱';
    } else if (ua.includes('tablet') || ua.includes('ipad')) {
      return '📱';
    } else {
      return '🖥️';
    }
  };

  const getBrowserName = (userAgent) => {
    if (!userAgent) return 'Unknown Browser';

    const ua = userAgent.toLowerCase();
    if (ua.includes('chrome')) return 'Chrome';
    if (ua.includes('firefox')) return 'Firefox';
    if (ua.includes('safari')) return 'Safari';
    if (ua.includes('edge')) return 'Edge';
    if (ua.includes('opera')) return 'Opera';
    return 'Unknown Browser';
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h3 className="text-lg font-semibold text-gray-800">Active Sessions</h3>
        <div className="space-x-3">
          <button
            onClick={fetchSessions}
            disabled={loadingSessions}
            className="px-4 py-2 bg-gray-600 text-white rounded-md hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-gray-500 disabled:opacity-50"
          >
            {loadingSessions ? 'Refreshing...' : 'Refresh'}
          </button>
          <button
            onClick={handleTerminateAllSessions}
            className="px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-red-500"
          >
            Terminate All Sessions
          </button>
        </div>
      </div>

      <div className="bg-yellow-50 p-4 rounded-lg">
        <div className="flex items-start">
          <div className="flex-shrink-0">
            <span className="text-yellow-600 text-xl">⚠️</span>
          </div>
          <div className="ml-3">
            <h4 className="text-sm font-medium text-yellow-800">Session Management</h4>
            <p className="text-sm text-yellow-700 mt-1">
              Sessions automatically expire after 8 hours of inactivity. Terminating all sessions will log you out immediately.
              If you see any suspicious sessions, terminate them immediately and change your password.
            </p>
          </div>
        </div>
      </div>

      {loadingSessions ? (
        <div className="flex items-center justify-center py-8">
          <p className="text-gray-600">Loading sessions...</p>
        </div>
      ) : sessions.length === 0 ? (
        <div className="text-center py-8">
          <p className="text-gray-600">No active sessions found</p>
        </div>
      ) : (
        <div className="space-y-4">
          {sessions.map((session, index) => (
            <div key={session.token || index} className="bg-white border border-gray-200 rounded-lg p-4">
              <div className="flex justify-between items-start">
                <div className="flex items-start space-x-3">
                  <div className="text-2xl">
                    {getDeviceIcon(session.user_agent)}
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center space-x-2">
                      <h4 className="text-md font-semibold text-gray-800">
                        {getBrowserName(session.user_agent)}
                      </h4>
                      {session.is_current && (
                        <span className="inline-flex px-2 py-1 text-xs font-semibold rounded-full bg-green-100 text-green-800">
                          Current Session
                        </span>
                      )}
                    </div>
                    <div className="mt-1 space-y-1 text-sm text-gray-600">
                      <p>
                        <span className="font-medium">IP Address:</span> {session.ip_address || 'Unknown'}
                      </p>
                      <p>
                        <span className="font-medium">Last Activity:</span> {formatDate(session.last_activity)}
                      </p>
                      <p>
                        <span className="font-medium">Created:</span> {formatDate(session.created_at)}
                      </p>
                      {session.expires_at && (
                        <p>
                          <span className="font-medium">Expires:</span> {formatDate(session.expires_at)}
                        </p>
                      )}
                    </div>
                    {session.user_agent && (
                      <details className="mt-2">
                        <summary className="text-xs text-gray-500 cursor-pointer hover:text-gray-700">
                          View User Agent
                        </summary>
                        <p className="text-xs text-gray-500 mt-1 font-mono bg-gray-50 p-2 rounded">
                          {session.user_agent}
                        </p>
                      </details>
                    )}
                  </div>
                </div>
                <div className="flex flex-col space-y-2">
                  {!session.is_current && (
                    <button
                      onClick={() => handleTerminateSession(session.token)}
                      className="px-3 py-1 text-sm bg-red-600 text-white rounded hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-red-500"
                    >
                      Terminate
                    </button>
                  )}
                  <div className="text-xs text-gray-500 text-right">
                    {session.is_current ? 'This device' : 'Remote device'}
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Session Security Information */}
      <div className="bg-blue-50 p-4 rounded-lg">
        <h4 className="text-md font-semibold text-blue-800 mb-3">Session Security</h4>
        <ul className="space-y-2 text-sm text-blue-700">
          <li className="flex items-start">
            <span className="text-blue-500 mr-2">•</span>
            Sessions are automatically terminated after 8 hours of inactivity
          </li>
          <li className="flex items-start">
            <span className="text-blue-500 mr-2">•</span>
            Changing your password will terminate all other sessions
          </li>
          <li className="flex items-start">
            <span className="text-blue-500 mr-2">•</span>
            If you see unfamiliar sessions, terminate them immediately and change your password
          </li>
          <li className="flex items-start">
            <span className="text-blue-500 mr-2">•</span>
            Always log out when using shared or public computers
          </li>
        </ul>
      </div>
    </div>
  );
};

export default SessionsTab;