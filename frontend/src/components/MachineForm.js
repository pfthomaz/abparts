// c:/abparts/frontend/src/components/MachineForm.js

import React, { useState, useEffect } from 'react';

const MachineForm = ({ initialData = {}, organizations = [], onSubmit, onClose }) => {
  const [formData, setFormData] = useState({
    customer_organization_id: '',
    model_type: '',
    name: '',
    serial_number: '',
    purchase_date: '',
    warranty_expiry_date: '',
    status: 'active'
  });
  const [error, setError] = useState('');

  useEffect(() => {
    if (initialData.id) {
      setFormData({
        customer_organization_id: initialData.customer_organization_id || '',
        model_type: initialData.model_type || '',
        name: initialData.name || '',
        serial_number: initialData.serial_number || '',
        purchase_date: initialData.purchase_date ?
          new Date(initialData.purchase_date).toISOString().split('T')[0] : '',
        warranty_expiry_date: initialData.warranty_expiry_date ?
          new Date(initialData.warranty_expiry_date).toISOString().split('T')[0] : '',
        status: initialData.status || 'active'
      });
    } else {
      // Reset for new entry
      setFormData({
        customer_organization_id: '',
        model_type: '',
        name: '',
        serial_number: '',
        purchase_date: '',
        warranty_expiry_date: '',
        status: 'active'
      });
    }
  }, [initialData]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    if (!formData.customer_organization_id || !formData.model_type || !formData.name || !formData.serial_number) {
      setError('Customer organization, model type, name, and serial number are required.');
      return;
    }
    try {
      // Convert dates to ISO format for API
      const submitData = {
        ...formData,
        purchase_date: formData.purchase_date ? new Date(formData.purchase_date).toISOString() : null,
        warranty_expiry_date: formData.warranty_expiry_date ? new Date(formData.warranty_expiry_date).toISOString() : null
      };
      await onSubmit(submitData);
    } catch (err) {
      setError(err.message || 'An unexpected error occurred.');
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {error && <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded" role="alert">{error}</div>}

      <div>
        <label htmlFor="customer_organization_id" className="block text-sm font-medium text-gray-700">
          Customer Organization *
        </label>
        <select
          id="customer_organization_id"
          name="customer_organization_id"
          value={formData.customer_organization_id}
          onChange={handleChange}
          className="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm rounded-md"
          required
        >
          <option value="">Select customer organization</option>
          {organizations.map(org => (
            <option key={org.id} value={org.id}>{org.name}</option>
          ))}
        </select>
      </div>

      <div>
        <label htmlFor="name" className="block text-sm font-medium text-gray-700">Machine Name</label>
        <input type="text" id="name" name="name" value={formData.name} onChange={handleChange} className="mt-1 block w-full shadow-sm sm:text-sm border-gray-300 rounded-md" required />
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label htmlFor="model_type" className="block text-sm font-medium text-gray-700">
            Model Type *
          </label>
          <select
            id="model_type"
            name="model_type"
            value={formData.model_type}
            onChange={handleChange}
            className="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm rounded-md"
            required
          >
            <option value="">Select model type</option>
            <option value="V3.1B">V3.1B</option>
            <option value="V4.0">V4.0</option>
          </select>
        </div>

        <div>
          <label htmlFor="status" className="block text-sm font-medium text-gray-700">
            Status
          </label>
          <select
            id="status"
            name="status"
            value={formData.status}
            onChange={handleChange}
            className="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm rounded-md"
          >
            <option value="active">Active</option>
            <option value="inactive">Inactive</option>
            <option value="maintenance">Under Maintenance</option>
            <option value="decommissioned">Decommissioned</option>
          </select>
        </div>
      </div>

      <div>
        <label htmlFor="serial_number" className="block text-sm font-medium text-gray-700">
          Serial Number *
        </label>
        <input
          type="text"
          id="serial_number"
          name="serial_number"
          value={formData.serial_number}
          onChange={handleChange}
          className="mt-1 block w-full shadow-sm sm:text-sm border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
          required
        />
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label htmlFor="purchase_date" className="block text-sm font-medium text-gray-700">
            Purchase Date
          </label>
          <input
            type="date"
            id="purchase_date"
            name="purchase_date"
            value={formData.purchase_date}
            onChange={handleChange}
            className="mt-1 block w-full shadow-sm sm:text-sm border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
          />
        </div>

        <div>
          <label htmlFor="warranty_expiry_date" className="block text-sm font-medium text-gray-700">
            Warranty Expiry Date
          </label>
          <input
            type="date"
            id="warranty_expiry_date"
            name="warranty_expiry_date"
            value={formData.warranty_expiry_date}
            onChange={handleChange}
            className="mt-1 block w-full shadow-sm sm:text-sm border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
          />
        </div>
      </div>

      <div className="flex justify-end space-x-2 pt-4">
        <button type="button" onClick={onClose} className="bg-gray-200 text-gray-800 py-2 px-4 rounded-md hover:bg-gray-300">
          Cancel
        </button>
        <button type="submit" className="bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700">
          Save Machine
        </button>
      </div>
    </form>
  );
};

export default MachineForm;