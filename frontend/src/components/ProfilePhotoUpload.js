// frontend/src/components/ProfilePhotoUpload.js

import React, { useState } from 'react';
import { API_BASE_URL } from '../services/api';

const ProfilePhotoUpload = ({ currentPhotoUrl, onPhotoUpdated }) => {
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState(null);
  
  console.log('ProfilePhotoUpload rendered with currentPhotoUrl:', currentPhotoUrl);

  const handleFileSelect = async (event) => {
    console.log('handleFileSelect called', event);
    const file = event.target.files[0];
    console.log('Selected file:', file);
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
      console.log('Uploading photo...');
      const response = await fetch(`${API_BASE_URL}/uploads/users/profile-photo`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        },
        body: formData
      });

      if (!response.ok) {
        throw new Error('Failed to upload photo');
      }

      const data = await response.json();
      console.log('Upload successful, new URL:', data.url);
      onPhotoUpdated(data.url);
    } catch (err) {
      console.error('Upload error:', err);
      setError('Failed to upload photo. Please try again.');
    } finally {
      setUploading(false);
    }
  };

  const handleRemovePhoto = async () => {
    if (!window.confirm('Are you sure you want to remove your profile photo?')) {
      return;
    }

    setUploading(true);
    setError(null);

    try {
      const token = localStorage.getItem('authToken');
      const response = await fetch(`${API_BASE_URL}/uploads/users/profile-photo`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (!response.ok) {
        throw new Error('Failed to remove photo');
      }

      onPhotoUpdated(null);
    } catch (err) {
      console.error('Remove error:', err);
      setError('Failed to remove photo. Please try again.');
    } finally {
      setUploading(false);
    }
  };

  const photoUrl = currentPhotoUrl?.startsWith('/static') 
    ? `${API_BASE_URL}${currentPhotoUrl}`
    : currentPhotoUrl;

  console.log('Rendering preview - currentPhotoUrl:', currentPhotoUrl, 'photoUrl:', photoUrl);

  return (
    <div className="space-y-4">
      <div className="flex items-center space-x-4">
        {/* Photo Preview */}
        <div className="relative">
          {currentPhotoUrl ? (
            <img
              src={photoUrl}
              alt="Profile"
              className="w-24 h-24 rounded-full object-cover border-4 border-gray-200"
              onLoad={() => console.log('Image loaded successfully:', photoUrl)}
              onError={(e) => console.error('Image failed to load:', photoUrl, e)}
            />
          ) : (
            <div className="w-24 h-24 rounded-full bg-blue-500 flex items-center justify-center text-white text-3xl font-bold border-4 border-gray-200">
              ?
            </div>
          )}
          {uploading && (
            <div className="absolute inset-0 bg-black bg-opacity-50 rounded-full flex items-center justify-center">
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
              {currentPhotoUrl ? 'Change Photo' : 'Upload Photo'}
            </span>
          </label>
          
          {currentPhotoUrl && (
            <button
              onClick={handleRemovePhoto}
              disabled={uploading}
              className="bg-red-600 text-white px-4 py-2 rounded-md hover:bg-red-700 disabled:opacity-50 disabled:cursor-not-allowed text-sm font-medium"
            >
              Remove Photo
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
        Recommended: Square image, at least 200x200 pixels. Max size: 5MB.
      </p>
    </div>
  );
};

export default ProfilePhotoUpload;
