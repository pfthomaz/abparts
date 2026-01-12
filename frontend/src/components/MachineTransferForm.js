// frontend/src/components/MachineTransferForm.js

import React, { useState, useEffect } from 'react';
import { api } from '../services/api';

const MachineTransferForm = ({ machine, onSubmit, onClose }) => {
  const [formData, setFormData] = useState({
    machine_id: machine?.id || '',
    new_customer_organization_id: '',
    transfer_date: new Date().toISOString().split('T')[0],
    transfer_reason: '',
    notes: ''
  });
  const [organizations, setOrganizations] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchOrganizations();
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  const fetchOrganizations = async () => {
    try {
      const data = await api.get('/organizations/');
      // Filter to only show customer organizations (excluding current owner)
      const customerOrgs = data.filter(org =>
        org.organization_type === 'customer' &&
        org.id !== machine?.customer_organization_id
      );
      setOrganizations(customerOrgs);
    } catch (err) {
      setError('Failed to fetch organizations');
    }
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    if (!formData.new_customer_organization_id || !formData.transfer_reason) {
      setError('New organization and transfer reason are required.');
      setLoading(false);
      return;
    }

    try {
      await onSubmit({
        ...formData,
        transfer_date: new Date(formData.transfer_date).toISOString()
      });
    } catch (err) {
      setError(err.message || 'Failed to transfer machine');
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded" role="alert">
          {error}
        </div>
      )}

      {/* Current Machine Info */}
      <div className="bg-gray-50 p-4 rounded-lg">
        <h3 className="font-semibold text-gray-800 mb-2">Machine to Transfer</h3>
        <div className="text-sm text-gray-600">
          <p><strong>Name:</strong> {machine?.name}</p>
          <p><strong>Model:</strong> {machine?.model_type}</p>
          <p><strong>Serial:</strong> {machine?.serial_number}</p>
          <p><strong>Current Owner:</strong> {machine?.customer_organization_name}</p>
        </div>
      </div>

      <div>
        <label htmlFor="new_customer_organization_id" className="block text-sm font-medium text-gray-700">
          New Owner Organization *
        </label>
        <select
          id="new_customer_organization_id"
          name="new_customer_organization_id"
          value={formData.new_customer_organization_id}
          onChange={handleChange}
          className="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm rounded-md"
          required
        >
          <option value="">Select new owner organization</option>
          {organizations.map(org => (
            <option key={org.id} value={org.id}>
              {org.name} ({org.organization_type})
            </option>
          ))}
        </select>
      </div>

      <div>
        <label htmlFor="transfer_date" className="block text-sm font-medium text-gray-700">
          Transfer Date *
        </label>
        <input
          type="date"
          id="transfer_date"
          name="transfer_date"
          value={formData.transfer_date}
          onChange={handleChange}
          className="mt-1 block w-full shadow-sm sm:text-sm border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
          required
        />
      </div>

      <div>
        <label htmlFor="transfer_reason" className="block text-sm font-medium text-gray-700">
          Transfer Reason *
        </label>
        <select
          id="transfer_reason"
          name="transfer_reason"
          value={formData.transfer_reason}
          onChange={handleChange}
          className="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm rounded-md"
          required
        >
          <option value="">Select transfer reason</option>
          <option value="sale">Sale to new customer</option>
          <option value="relocation">Business relocation</option>
          <option value="upgrade">Machine upgrade/replacement</option>
          <option value="lease_transfer">Lease transfer</option>
          <option value="warranty_replacement">Warranty replacement</option>
          <option value="other">Other</option>
        </select>
      </div>

      <div>
        <label htmlFor="notes" className="block text-sm font-medium text-gray-700">
          Transfer Notes
        </label>
        <textarea
          id="notes"
          name="notes"
          rows={3}
          value={formData.notes}
          onChange={handleChange}
          placeholder="Additional notes about the transfer..."
          className="mt-1 block w-full shadow-sm sm:text-sm border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
        />
      </div>

      {/* Warning */}
      <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
        <div className="flex">
          <div className="flex-shrink-0">
            <svg className="h-5 w-5 text-yellow-400" viewBox="0 0 20 20" fill="currentColor">
              <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
            </svg>
          </div>
          <div className="ml-3">
            <h3 className="text-sm font-medium text-yellow-800">
              Transfer Confirmation Required
            </h3>
            <div className="mt-2 text-sm text-yellow-700">
              <p>This action will transfer ownership of the machine to the selected organization.
                All maintenance history and usage records will be transferred as well.
                This action cannot be undone.</p>
            </div>
          </div>
        </div>
      </div>

      <div className="flex justify-end space-x-2 pt-4">
        <button
          type="button"
          onClick={onClose}
          className="bg-gray-200 text-gray-800 py-2 px-4 rounded-md hover:bg-gray-300"
          disabled={loading}
        >
          Cancel
        </button>
        <button
          type="submit"
          className="bg-red-600 text-white py-2 px-4 rounded-md hover:bg-red-700 disabled:opacity-50"
          disabled={loading}
        >
          {loading ? 'Transferring...' : 'Transfer Machine'}
        </button>
      </div>
    </form>
  );
};

export default MachineTransferForm;