// frontend/src/components/LocalizationDebugger.js

import React, { useState, useEffect } from 'react';
import { useAuth } from '../AuthContext';
import { getLocalizedProtocols } from '../services/maintenanceProtocolsService';
import translationService from '../services/translationService';

const LocalizationDebugger = () => {
  const { user } = useAuth();
  const [debugInfo, setDebugInfo] = useState({});
  const [loading, setLoading] = useState(false);

  const runDebugTest = async () => {
    setLoading(true);
    const info = {};
    
    try {
      // Check user info
      info.user = {
        id: user?.id,
        username: user?.username,
        preferred_language: user?.preferred_language,
        name: user?.name
      };
      
      // Test localized protocols
      // console.log('🧪 Starting localization debug test...');
      const protocols = await getLocalizedProtocols({}, user?.preferred_language);
      info.protocols = protocols.map(p => ({
        id: p.id,
        name: p.name,
        isTranslated: p.isTranslated,
        original_name: p.original_name
      }));
      
      // Test translation service directly
      if (protocols.length > 0) {
        const firstProtocol = protocols[0];
        try {
          const directTranslation = await translationService.getLocalizedProtocol(
            firstProtocol.id, 
            user?.preferred_language
          );
          info.directTranslation = directTranslation;
        } catch (error) {
          info.directTranslationError = error.message;
        }
      }
      
    } catch (error) {
      info.error = error.message;
    }
    
    setDebugInfo(info);
    setLoading(false);
  };

  useEffect(() => {
    if (user) {
      runDebugTest();
    }
  }, [user]);

  if (!user) {
    return <div className="p-4 bg-yellow-100 rounded">Please log in to test localization</div>;
  }

  return (
    <div className="p-6 bg-white rounded-lg shadow-lg max-w-4xl mx-auto">
      <h2 className="text-2xl font-bold mb-4">🔍 Localization Debug Info</h2>
      
      <div className="space-y-4">
        <div className="p-4 bg-blue-50 rounded">
          <h3 className="font-bold text-blue-900">User Info:</h3>
          <pre className="text-sm mt-2">{JSON.stringify(debugInfo.user, null, 2)}</pre>
        </div>

        {debugInfo.protocols && (
          <div className="p-4 bg-green-50 rounded">
            <h3 className="font-bold text-green-900">Protocols ({debugInfo.protocols.length}):</h3>
            <div className="text-sm mt-2 space-y-2">
              {debugInfo.protocols.map(p => (
                <div key={p.id} className="p-2 bg-white rounded border">
                  <div><strong>Name:</strong> {p.name}</div>
                  <div><strong>ID:</strong> {p.id}</div>
                  <div><strong>Translated:</strong> {p.isTranslated ? '✅ Yes' : '❌ No'}</div>
                </div>
              ))}
            </div>
          </div>
        )}

        {debugInfo.directTranslation && (
          <div className="p-4 bg-purple-50 rounded">
            <h3 className="font-bold text-purple-900">Direct Translation Test:</h3>
            <pre className="text-sm mt-2">{JSON.stringify(debugInfo.directTranslation, null, 2)}</pre>
          </div>
        )}

        {debugInfo.directTranslationError && (
          <div className="p-4 bg-red-50 rounded">
            <h3 className="font-bold text-red-900">Translation Error:</h3>
            <p className="text-sm mt-2">{debugInfo.directTranslationError}</p>
          </div>
        )}

        {debugInfo.error && (
          <div className="p-4 bg-red-50 rounded">
            <h3 className="font-bold text-red-900">General Error:</h3>
            <p className="text-sm mt-2">{debugInfo.error}</p>
          </div>
        )}

        <button
          onClick={runDebugTest}
          disabled={loading}
          className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:bg-gray-400"
        >
          {loading ? 'Testing...' : 'Run Debug Test'}
        </button>
      </div>

      <div className="mt-6 p-4 bg-gray-50 rounded">
        <h3 className="font-bold text-gray-900">Instructions:</h3>
        <ol className="list-decimal list-inside text-sm mt-2 space-y-1">
          <li>Make sure your user has preferred_language set to 'el' (Greek)</li>
          <li>Check that translations exist for the protocols you're testing</li>
          <li>Open browser console to see detailed logs</li>
          <li>Look for any API errors in the Network tab</li>
        </ol>
      </div>
    </div>
  );
};

export default LocalizationDebugger;