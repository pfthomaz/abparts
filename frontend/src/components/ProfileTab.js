// frontend/src/components/ProfileTab.js

import React from 'react';
import LanguageSelector from './LanguageSelector';

const ProfileTab = ({
  profile,
  profileForm,
  setProfileForm,
  isEditingProfile,
  setIsEditingProfile,
  handleProfileUpdate
}) => {
  const handleInputChange = (field, value) => {
    setProfileForm(prev => ({ ...prev, [field]: value }));
  };

  return (
    <div className="space-y-6">
      {/* Account Information Display */}
      <div className="bg-gray-50 p-4 rounded-lg">
        <h3 className="text-lg font-semibold text-gray-800 mb-4">Account Information</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-600">Username</label>
            <p className="text-gray-800 font-medium">{profile?.username}</p>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-600">Role</label>
            <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${profile?.role === 'super_admin'
              ? 'bg-purple-100 text-purple-800'
              : profile?.role === 'admin'
                ? 'bg-blue-100 text-blue-800'
                : 'bg-green-100 text-green-800'
              }`}>
              {profile?.role?.replace('_', ' ').toUpperCase()}
            </span>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-600">Organization</label>
            <p className="text-gray-800 font-medium">{profile?.organization?.name}</p>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-600">Account Status</label>
            <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${profile?.user_status === 'active'
              ? 'bg-green-100 text-green-800'
              : profile?.user_status === 'inactive'
                ? 'bg-red-100 text-red-800'
                : profile?.user_status === 'pending_invitation'
                  ? 'bg-yellow-100 text-yellow-800'
                  : 'bg-gray-100 text-gray-800'
              }`}>
              {profile?.user_status?.replace('_', ' ').toUpperCase()}
            </span>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-600">Member Since</label>
            <p className="text-gray-800">
              {profile?.created_at ? new Date(profile.created_at).toLocaleDateString() : 'N/A'}
            </p>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-600">Last Updated</label>
            <p className="text-gray-800">
              {profile?.updated_at ? new Date(profile.updated_at).toLocaleDateString() : 'N/A'}
            </p>
          </div>
        </div>
      </div>

      {/* Profile Information */}
      <div>
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-lg font-semibold text-gray-800">Profile Information</h3>
          {!isEditingProfile && (
            <button
              onClick={() => setIsEditingProfile(true)}
              className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              Edit Profile
            </button>
          )}
        </div>

        {isEditingProfile ? (
          <form onSubmit={handleProfileUpdate} className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Full Name
                </label>
                <input
                  type="text"
                  value={profileForm.name}
                  onChange={(e) => handleInputChange('name', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Enter your full name"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Email Address
                </label>
                <input
                  type="email"
                  value={profileForm.email}
                  onChange={(e) => handleInputChange('email', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Enter your email address"
                />
                <p className="text-xs text-gray-500 mt-1">
                  Email changes require verification
                </p>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Phone Number
                </label>
                <input
                  type="tel"
                  value={profileForm.phone}
                  onChange={(e) => handleInputChange('phone', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Enter your phone number"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Address
                </label>
                <input
                  type="text"
                  value={profileForm.address}
                  onChange={(e) => handleInputChange('address', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Enter your address"
                />
              </div>
            </div>
            <div className="flex justify-end space-x-3 pt-4">
              <button
                type="button"
                onClick={() => {
                  setIsEditingProfile(false);
                  // Reset form to original values
                  setProfileForm({
                    name: profile?.name || '',
                    email: profile?.email || '',
                    phone: profile?.phone || '',
                    address: profile?.address || ''
                  });
                }}
                className="px-4 py-2 text-gray-600 border border-gray-300 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-gray-500"
              >
                Cancel
              </button>
              <button
                type="submit"
                className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                Save Changes
              </button>
            </div>
          </form>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-600">Full Name</label>
              <p className="text-gray-800">{profile?.name || 'Not provided'}</p>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-600">Email Address</label>
              <p className="text-gray-800">{profile?.email || 'Not provided'}</p>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-600">Phone Number</label>
              <p className="text-gray-800">{profile?.phone || 'Not provided'}</p>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-600">Address</label>
              <p className="text-gray-800">{profile?.address || 'Not provided'}</p>
            </div>
          </div>
        )}
      </div>

      {/* Language and Localization Preferences */}
      <div>
        <h3 className="text-lg font-semibold text-gray-800 mb-4">Language & Localization</h3>
        <div className="bg-gray-50 p-4 rounded-lg">
          <LanguageSelector
            showCountrySelector={true}
            showAdvancedOptions={true}
            disabled={false}
          />
        </div>
      </div>
    </div>
  );
};

export default ProfileTab;