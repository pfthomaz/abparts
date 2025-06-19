// frontend/src/App.js

import React, { useState, useEffect } from 'react';
import './index.css'; // Import Tailwind CSS base styles

function App() {
  const [organizations, setOrganizations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Get API base URL from environment variable
  // In a Docker Compose setup, REACT_APP_API_BASE_URL will be set by the 'web' service
  // In production, this would point to your deployed backend API
  const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000';

  useEffect(() => {
    const fetchOrganizations = async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/organizations`);
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        setOrganizations(data);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchOrganizations();
  }, [API_BASE_URL]); // Dependency array includes API_BASE_URL to re-fetch if it changes

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gray-100">
        <p className="text-xl text-gray-700">Loading organizations...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-red-100">
        <p className="text-xl text-red-700">Error: {error}</p>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-100 py-10">
      <div className="container mx-auto p-4 bg-white shadow-lg rounded-lg">
        <h1 className="text-4xl font-bold text-center text-gray-800 mb-8">ABParts Organizations</h1>

        {organizations.length === 0 ? (
          <p className="text-center text-gray-600 text-lg">No organizations found. Try adding some via the API.</p>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {organizations.map((org) => (
              <div key={org.id} className="bg-gray-50 p-6 rounded-lg shadow-md border border-gray-200">
                <h2 className="text-2xl font-semibold text-blue-700 mb-2">{org.name}</h2>
                <p className="text-gray-600 mb-1">
                  <span className="font-medium">Type:</span> {org.type}
                </p>
                {org.address && (
                  <p className="text-gray-600 mb-1">
                    <span className="font-medium">Address:</span> {org.address}
                  </p>
                )}
                {org.contact_info && (
                  <p className="text-gray-600 mb-1">
                    <span className="font-medium">Contact:</span> {org.contact_info}
                  </p>
                )}
                <p className="text-sm text-gray-400 mt-3">ID: {org.id}</p>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

export default App;