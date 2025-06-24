// frontend/src/components/OrganizationForm.js

import React, { useState, useEffect } from 'react';
import { useAuth } from '../AuthContext';

function OrganizationForm({ initialData = {}, onSubmit, onClose }) {
  const { token } = useAuth();
  const [formData, setFormData] = useState({
    name: '',
    type: 'Customer', // Default type
    address: '',
    contact_info: '',
    ...initialData, // Pre-fill if initialData is provided (for editing)
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    // Update form data if initialData changes (e.g., when editing a different organization)
    setFormData({
      name: '',
      type: 'Customer',
      address: '',
      contact_info: '',
      ...initialData,
    });
  }, [initialData]);

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
      // Call the onSubmit prop function (passed from App.js)
      // This allows App.js to handle the actual API call and state updates
      await onSubmit(formData);
      onClose(); // Close modal on successful submission
    } catch (err) {
      setError(err.message || 'An unexpected error occurred.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative" role="alert">
          <strong className="font-bold">Error:</strong>
          <span className="block sm:inline ml-2">{error}</span>
        </div>
      )}
      <div>
        <label htmlFor="name" className="block text-sm font-medium text-gray-700 mb-1">
          Organization Name
        </label>
        <input
          type="text"
          id="name"
          name="name"
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
          value={formData.name}
          onChange={handleChange}
          required
          disabled={loading}
        />
      </div>
      <div>
        <label htmlFor="type" className="block text-sm font-medium text-gray-700 mb-1">
          Type
        </label>
        <select
          id="type"
          name="type"
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
          value={formData.type}
          onChange={handleChange}
          required
          disabled={loading}
        >
          <option value="Customer">Customer</option>
          <option value="Warehouse">Warehouse</option>
          <option value="Supplier">Supplier</option>
        </select>
      </div>
      <div>
        <label htmlFor="address" className="block text-sm font-medium text-gray-700 mb-1">
          Address
        </label>
        <textarea
          id="address"
          name="address"
          rows="3"
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
          value={formData.address}
          onChange={handleChange}
          disabled={loading}
        ></textarea>
      </div>
      <div>
        <label htmlFor="contact_info" className="block text-sm font-medium text-gray-700 mb-1">
          Contact Info
        </label>
        <input
          type="text"
          id="contact_info"
          name="contact_info"
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
          value={formData.contact_info}
          onChange={handleChange}
          disabled={loading}
        />
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
          {loading ? 'Submitting...' : (initialData.id ? 'Update Organization' : 'Create Organization')}
        </button>
      </div>
    </form>
  );
}

export default OrganizationForm;
