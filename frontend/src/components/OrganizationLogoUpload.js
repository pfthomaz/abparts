// frontend/src/components/OrganizationLogoUpload.js

import React, { useState } from 'react';
import { API_BASE_URL } from '../services/api';

const OrganizationLogoUpload = ({ organizationId, currentLogoUrl, onLogoUpdated }) => {
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState(null);

  const handleFileSelect = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    // Validate file type
    if (!file.type.startsWith('image/')) {
      setError('Please select an image file');
      return;
    }

    // Validate file size (5MB max)
    if (file.size > 5 * 1024 * 1024) {
      setError('Image must be smaller than 5MB');
      return;
    }

    setError(null);
    setUploading(true);

    try {
      const formData = new FormData();
      formData.append('file', file);

      const token = localStorage.getItem('authToken');
      const response = await fetch(`${API_BASE_URL}/uploads/organizations/${organizationId}/logo`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        },
        body: formData
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to upload logo');
      }

      const data = await response.json();
      onLogoUpdated(data.url);
    } catch (err) {
      console.error('Upload error:', err);
      setError(err.message || 'Failed to upload logo. Please try again.');
    } finally {
      setUploading(false);
    }
  };

  const handleRemoveLogo = async () => {
    if (!window.confirm('Are you sure you want to remove the organization logo?')) {
      return;
    }

    setUploading(true);
    setError(null);

    try {
      const token = localStorage.getItem('authToken');
      const response = await fetch(`${API_BASE_URL}/uploads/organizations/${organizationId}/logo`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (!response.ok) {
        throw new Error('Failed to remove logo');
      }

      onLogoUpdated(null);
    } catch (err) {
      console.error('Remove error:', err);
      setError('Failed to remove logo. Please try again.');
    } finally {
      setUploading(false);
    }
  };

  const logoUrl = currentLogoUrl;

  return (
    <div className="space-y-4">
      <div className="flex items-center space-x-4">
        {/* Logo Preview */}
        <div className="relative">
          {currentLogoUrl ? (
            <img
              src={logoUrl}
              alt="Organization Logo"
              className="w-24 h-24 rounded-lg object-contain border-2 border-gray-200 bg-white p-2"
            />
          ) : (
            <div className="w-24 h-24 rounded-lg bg-gray-100 flex items-center justify-center text-gray-400 text-xs border-2 border-gray-200">
              No Logo
            </div>
          )}
          {uploading && (
            <div className="absolute inset-0 bg-black bg-opacity-50 rounded-lg flex items-center justify-center">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-white"></div>
            </div>
          )}
        </div>

        {/* Upload/Remove Buttons */}
        <div className="flex flex-col space-y-2">
          <label className="cursor-pointer">
            <input
              type="file"
              accept="image/*"
              onChange={handleFileSelect}
              disabled={uploading}
              className="hidden"
            />
            <span className="inline-block bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed text-sm font-medium">
              {currentLogoUrl ? 'Change Logo' : 'Upload Logo'}
            </span>
          </label>
          
          {currentLogoUrl && (
            <button
              onClick={handleRemoveLogo}
              disabled={uploading}
              className="bg-red-600 text-white px-4 py-2 rounded-md hover:bg-red-700 disabled:opacity-50 disabled:cursor-not-allowed text-sm font-medium"
            >
              Remove Logo
            </button>
          )}
        </div>
      </div>

      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
          {error}
        </div>
      )}

      <p className="text-sm text-gray-500">
        Recommended: Transparent PNG or square logo. Max size: 5MB.
      </p>
    </div>
  );
};

export default OrganizationLogoUpload;
