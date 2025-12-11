import React, { useState, useEffect } from 'react';
import { useAuth } from '../AuthContext';
import { useTranslation } from '../hooks/useTranslation';

// New role system aligned with business model
const USER_ROLES = {
  user: 'user',
  admin: 'admin',
  super_admin: 'super_admin'
};

const USER_STATUS = {
  active: 'active',
  inactive: 'inactive',
  pending_invitation: 'pending_invitation',
  locked: 'locked'
};

function UserForm({ organizations = [], initialData = {}, onSubmit, onClose, editingSelf }) {
  const { t } = useTranslation();
  const { user } = useAuth();

  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    name: '',
    role: USER_ROLES.user,
    organization_id: '',
    user_status: USER_STATUS.active,
    preferred_language: 'en',
    is_active: true,
  });

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    const defaultState = {
      username: '',
      email: '',
      password: '',
      name: '',
      role: USER_ROLES.user,
      organization_id: (user?.role === 'admin' && !initialData.id) ? user.organization_id : '',
      user_status: USER_STATUS.active,
      preferred_language: 'en',
      is_active: true,
    };

    if (initialData.id) {
      setFormData({
        ...defaultState,
        ...initialData,
        password: '',
        organization_id: initialData.organization_id || defaultState.organization_id,
        role: initialData.role || defaultState.role,
        user_status: initialData.user_status || USER_STATUS.active,
        preferred_language: initialData.preferred_language || 'en',
        is_active: initialData.is_active !== undefined ? initialData.is_active : true,
      });
    } else {
      setFormData(defaultState);
      if (user?.role === 'admin') {
        setFormData(prevState => ({ ...prevState, organization_id: user.organization_id }));
      }
    }
  }, [initialData, user, organizations]);

  const isFieldDisabled = (fieldName) => {
    if (editingSelf) {
      return ['role', 'organization_id', 'is_active', 'user_status'].includes(fieldName);
    }
    if (user?.role === 'admin') {
      return ['organization_id'].includes(fieldName); // Admins can change roles within their org
    }
    return false;
  };

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData((prevData) => ({
      ...prevData,
      [name]: type === 'checkbox' ? checked : value,
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const dataToSend = { ...formData };
      
      // When editing, only include password if it's provided and valid
      if (initialData.id) {
        if (!dataToSend.password || dataToSend.password.length < 8) {
          delete dataToSend.password;
        }
      }

      await onSubmit(dataToSend);
      onClose();
    } catch (err) {
      setError(err.message || t('userForm.unexpectedError'));
    } finally {
      setLoading(false);
    }
  };

  const getAvailableRoles = () => {
    if (!user) return [];

    // Super admins can assign any role
    if (user.role === "super_admin") {
      return [
        { value: USER_ROLES.user, label: t('users.userRole') },
        { value: USER_ROLES.admin, label: t('users.adminRole') },
        { value: USER_ROLES.super_admin, label: t('users.superAdminRole') }
      ];
    }
    // Admins can assign user and admin roles within their organization
    else if (user.role === "admin") {
      return [
        { value: USER_ROLES.user, label: t('users.userRole') },
        { value: USER_ROLES.admin, label: t('users.adminRole') }
      ];
    }
    // Regular users cannot assign roles
    return [{ value: USER_ROLES.user, label: t('users.userRole') }];
  };

  const availableRoles = getAvailableRoles();

  const getAvailableStatuses = () => {
    return [
      { value: USER_STATUS.active, label: t('users.activeStatus') },
      { value: USER_STATUS.inactive, label: t('users.inactiveStatus') },
      { value: USER_STATUS.pending_invitation, label: t('users.pendingInvitationStatus') },
      { value: USER_STATUS.locked, label: t('users.lockedStatus') }
    ];
  };

  const availableStatuses = getAvailableStatuses();

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative" role="alert">
          <strong className="font-bold">{t('userInvitation.error')}</strong>
          <span className="block sm:inline ml-2">{error}</span>
        </div>
      )}
      <div>
        <label htmlFor="username" className="block text-sm font-medium text-gray-700 mb-1">
          {t('userForm.username')}
        </label>
        <input
          type="text"
          id="username"
          name="username"
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
          value={formData.username}
          onChange={handleChange}
          required
          disabled={loading}
        />
      </div>
      <div>
        <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-1">
          {t('users.email')}
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
        />
      </div>
      <div>
        <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-1">
          {t('userForm.password')} {initialData.id ? t('userForm.passwordKeepCurrent') : ''}
        </label>
        <input
          type="password"
          id="password"
          name="password"
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
          value={formData.password}
          onChange={handleChange}
          required={!initialData.id}
          disabled={loading}
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
          value={formData.name || ''}
          onChange={handleChange}
          disabled={loading}
        />
      </div>
      <div>
        <label htmlFor="preferred_language" className="block text-sm font-medium text-gray-700 mb-1">
          {t('userForm.preferredLanguage')}
        </label>
        <select
          id="preferred_language"
          name="preferred_language"
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
          value={formData.preferred_language || 'en'}
          onChange={handleChange}
          disabled={loading}
        >
          <option value="en">🇬🇧 English</option>
          <option value="el">🇬🇷 Ελληνικά (Greek)</option>
          <option value="ar">🇸🇦 العربية (Arabic)</option>
          <option value="es">🇪🇸 Español (Spanish)</option>
          <option value="tr">🇹🇷 Türkçe (Turkish)</option>
          <option value="no">🇳🇴 Norsk (Norwegian)</option>
        </select>
      </div>
      <div>
        <label htmlFor="role" className="block text-sm font-medium text-gray-700 mb-1">
          {t('users.role')}
        </label>
        <select
          id="role"
          name="role"
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
          value={formData.role}
          onChange={handleChange}
          required
          disabled={loading || isFieldDisabled('role')}
        >
          {availableRoles.map((role) => (
            <option key={role.value} value={role.value}>{role.label}</option>
          ))}
        </select>
      </div>
      <div>
        <label htmlFor="organization_id" className="block text-sm font-medium text-gray-700 mb-1">
          {t('users.organization')}
        </label>
        <select
          id="organization_id"
          name="organization_id"
          className="w-full px-4 py-2 border border-gray-300 rounded-md"
          value={formData.organization_id || ''}
          onChange={handleChange}
          required
          disabled={loading || isFieldDisabled('organization_id')}
        >
          <option value="">{t('userInvitation.selectOrganization')}</option>
          {organizations.map(org => (
            <option key={org.id} value={org.id}>{org.name}</option>
          ))}
        </select>
      </div>
      <div>
        <label htmlFor="user_status" className="block text-sm font-medium text-gray-700 mb-1">
          {t('userForm.userStatus')}
        </label>
        <select
          id="user_status"
          name="user_status"
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
          value={formData.user_status}
          onChange={handleChange}
          required
          disabled={loading || isFieldDisabled('user_status')}
        >
          {availableStatuses.map((status) => (
            <option key={status.value} value={status.value}>{status.label}</option>
          ))}
        </select>
      </div>
      <div className="flex items-center">
        <input
          type="checkbox"
          id="is_active"
          name="is_active"
          className="h-4 w-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
          checked={formData.is_active}
          onChange={handleChange}
          disabled={loading || isFieldDisabled('is_active')}
        />
        <label htmlFor="is_active" className="ml-2 block text-sm text-gray-900">
          {t('userForm.active')}
        </label>
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
          {loading ? t('userForm.submitting') : (initialData.id ? t('userForm.updateUser') : t('userForm.createUser'))}
        </button>
      </div>
    </form>
  );
}

export default UserForm;
