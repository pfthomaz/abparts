import React, { useState } from 'react';
import { useAuth } from '../AuthContext';
import { useTranslation } from '../hooks/useTranslation';

// Role system aligned with business model
const USER_ROLES = {
  user: 'user',
  admin: 'admin',
  super_admin: 'super_admin'
};

function UserInvitationForm({ organizations = [], onSubmit, onClose }) {
  const { t } = useTranslation();
  const { user } = useAuth();

  const [formData, setFormData] = useState({
    email: '',
    name: '',
    role: USER_ROLES.user,
    organization_id: user?.role === 'admin' ? user.organization_id : '',
  });

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prevData => ({
      ...prevData,
      [name]: value,
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      await onSubmit(formData);
      onClose();
    } catch (err) {
      setError(err.message || t('userInvitation.failedToSendInvitation'));
    } finally {
      setLoading(false);
    }
  };

  const getAvailableRoles = () => {
    if (!user) return [];

    // Super admins can invite users with any role
    if (user.role === "super_admin") {
      return [
        { value: USER_ROLES.user, label: t('users.userRole') },
        { value: USER_ROLES.admin, label: t('users.adminRole') },
        { value: USER_ROLES.super_admin, label: t('users.superAdminRole') }
      ];
    }
    // Admins can invite users and admins within their organization
    else if (user.role === "admin") {
      return [
        { value: USER_ROLES.user, label: t('users.userRole') },
        { value: USER_ROLES.admin, label: t('users.adminRole') }
      ];
    }
    // Regular users cannot send invitations
    return [];
  };

  const availableRoles = getAvailableRoles();

  // Check if user can send invitations
  if (!user || (user.role !== 'admin' && user.role !== 'super_admin')) {
    return (
      <div className="text-center py-8">
        <div className="text-gray-500 mb-4">
          <svg className="w-12 h-12 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
          </svg>
        </div>
        <p className="text-lg font-medium text-gray-900">{t('userInvitation.accessRestricted')}</p>
        <p className="text-sm text-gray-500">{t('userInvitation.accessRestrictedMessage')}</p>
      </div>
    );
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div className="mb-6">
        <h3 className="text-lg font-medium text-gray-900 mb-2">{t('userInvitation.title')}</h3>
        <p className="text-sm text-gray-600">{t('userInvitation.subtitle')}</p>
      </div>

      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative" role="alert">
          <strong className="font-bold">{t('userInvitation.error')}</strong>
          <span className="block sm:inline ml-2">{error}</span>
        </div>
      )}

      <div>
        <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-1">
          {t('userInvitation.emailAddress')} *
        </label>
        <input
          type="email"
          id="email"
          name="email"
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
          value={formData.email}
          onChange={handleChange}
          required
          disabled={loading}
          placeholder={t('userInvitation.emailPlaceholder')}
        />
      </div>

      <div>
        <label htmlFor="name" className="block text-sm font-medium text-gray-700 mb-1">
          {t('userInvitation.fullName')}
        </label>
        <input
          type="text"
          id="name"
          name="name"
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
          value={formData.name}
          onChange={handleChange}
          disabled={loading}
          placeholder={t('userInvitation.namePlaceholder')}
        />
      </div>

      <div>
        <label htmlFor="role" className="block text-sm font-medium text-gray-700 mb-1">
          {t('users.role')} *
        </label>
        <select
          id="role"
          name="role"
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
          value={formData.role}
          onChange={handleChange}
          required
          disabled={loading}
        >
          {availableRoles.map((role) => (
            <option key={role.value} value={role.value}>{role.label}</option>
          ))}
        </select>
      </div>

      <div>
        <label htmlFor="organization_id" className="block text-sm font-medium text-gray-700 mb-1">
          {t('users.organization')} *
        </label>
        <select
          id="organization_id"
          name="organization_id"
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
          value={formData.organization_id}
          onChange={handleChange}
          required
          disabled={loading || (user?.role === 'admin')} // Admins can only invite to their own org
        >
          <option value="">{t('userInvitation.selectOrganization')}</option>
          {organizations.map(org => (
            <option key={org.id} value={org.id}>{org.name}</option>
          ))}
        </select>
      </div>

      <div className="bg-blue-50 border border-blue-200 rounded-md p-4">
        <div className="flex">
          <div className="flex-shrink-0">
            <svg className="h-5 w-5 text-blue-400" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
            </svg>
          </div>
          <div className="ml-3">
            <p className="text-sm text-blue-700">
              {t('userInvitation.invitationNote')}
            </p>
          </div>
        </div>
      </div>

      <div className="flex justify-end space-x-3 mt-6">
        <button
          type="button"
          onClick={onClose}
          className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-200 rounded-md hover:bg-gray-300 focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-offset-2"
          disabled={loading}
        >
          {t('userInvitation.cancel')}
        </button>
        <button
          type="submit"
          className="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
          disabled={loading}
        >
          {loading ? t('userInvitation.sendingInvitation') : t('userInvitation.sendInvitation')}
        </button>
      </div>
    </form>
  );
}

export default UserInvitationForm;