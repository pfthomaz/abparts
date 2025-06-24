// frontend/src/components/UserForm.js

import React, { useState, useEffect } from 'react';
import { useAuth } from '../AuthContext';

function UserForm({ organizations = [], initialData = {}, onSubmit, onClose }) {
  const { token, user } = useAuth(); // Get user for authorization logic
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    name: '',
    role: 'Customer User', // Default role
    organization_id: '', // UUID string
    ...initialData, // Pre-fill if initialData is provided (for editing)
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Set default organization for Customer Admins
  useEffect(() => {
    if (user && (user.role === 'Customer Admin' || user.role === 'Customer User')) {
      setFormData(prevData => ({
        ...prevData,
        organization_id: user.organization_id || '', // Automatically set to their org ID
      }));
    } else {
      // For Oraseas Admin, ensure organization_id is selectable or defaults to empty
      if (!initialData.organization_id && organizations.length > 0) {
         setFormData(prevData => ({
            ...prevData,
            organization_id: '' // Clear if not editing and not customer admin
        }));
      }
    }
    // Update form data if initialData changes (e.g., when editing a different user)
    setFormData(prevData => ({
      ...prevData,
      ...initialData,
      // If initialData.organization_id exists, use it. Otherwise, keep existing.
      organization_id: initialData.organization_id || prevData.organization_id || '',
    }));
  }, [initialData, user, organizations]);


  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prevData) => ({
      ...prevData,
      [name]: value,
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      // For creation, password is required. For update, it's optional.
      // Filter out empty password if it's an update and password field is not touched
      const dataToSend = { ...formData };
      if (initialData.id && dataToSend.password === '') {
        delete dataToSend.password; // Don't send empty password on update
      }

      await onSubmit(dataToSend);
      onClose(); // Close modal on successful submission
    } catch (err) {
      setError(err.message || 'An unexpected error occurred.');
    } finally {
      setLoading(false);
    }
  };

  // Determine available roles based on current user's role
  const getAvailableRoles = () => {
    if (!user) return [];
    if (user.role === "Oraseas Admin") {
      return ["Oraseas Admin", "Oraseas Inventory Manager", "Customer Admin", "Customer User", "Supplier User"];
    } else if (user.role === "Customer Admin") {
      return ["Customer Admin", "Customer User"]; // Can only create/manage users within their org
    }
    return []; // Other roles cannot create users
  };

  const availableRoles = getAvailableRoles();

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative" role="alert">
          <strong className="font-bold">Error:</strong>
          <span className="block sm:inline ml-2">{error}</span>
        </div>
      )}
      <div>
        <label htmlFor="username" className="block text-sm font-medium text-gray-700 mb-1">
          Username
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
          Email
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
          Password {initialData.id ? '(Leave blank to keep current)' : ''}
        </label>
        <input
          type="password"
          id="password"
          name="password"
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
          value={formData.password}
          onChange={handleChange}
          required={!initialData.id} // Required only for new users
          disabled={loading}
        />
      </div>
      <div>
        <label htmlFor="name" className="block text-sm font-medium text-gray-700 mb-1">
          Full Name
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
        <label htmlFor="role" className="block text-sm font-medium text-gray-700 mb-1">
          Role
        </label>
        <select
          id="role"
          name="role"
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
          value={formData.role}
          onChange={handleChange}
          required
          disabled={loading || (user && user.role === 'Customer Admin' && !initialData.id)} // Customer Admin cannot change role on existing users
        >
          {availableRoles.map((role) => (
            <option key={role} value={role}>{role}</option>
          ))}
        </select>
      </div>
      <div>
        <label htmlFor="organization_id" className="block text-sm font-medium text-gray-700 mb-1">
          Organization
        </label>
        <select
          id="organization_id"
          name="organization_id"
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
          value={formData.organization_id}
          onChange={handleChange}
          required
          disabled={loading || (user && user.role === 'Customer Admin')} // Customer Admin cannot change org_id
        >
          <option value="">Select an Organization</option>
          {organizations.map((org) => (
            <option key={org.id} value={org.id}>{org.name} ({org.type})</option>
          ))}
        </select>
      </div>
      <div className="flex justify-end space-x-3 mt-6">
        <button
          type="button"
          onClick={onClose}
          className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-200 rounded-md hover:bg-gray-300 focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-offset-2"
          disabled={loading}
        >
          Cancel
        </button>
        <button
          type="submit"
          className="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
          disabled={loading}
        >
          {loading ? 'Submitting...' : (initialData.id ? 'Update User' : 'Create User')}
        </button>
      </div>
    </form>
  );
}

export default UserForm;
