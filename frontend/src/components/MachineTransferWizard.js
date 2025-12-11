// frontend/src/components/MachineTransferWizard.js

import React, { useState, useEffect } from 'react';
import { machinesService } from '../services/machinesService';
import { organizationsService } from '../services/organizationsService';
import { useAuth } from '../AuthContext';

const MachineTransferWizard = ({ machine, onTransferComplete, onClose }) => {
  const { user } = useAuth();
  const [currentStep, setCurrentStep] = useState(1);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [organizations, setOrganizations] = useState([]);
  const [transferData, setTransferData] = useState({
    new_customer_organization_id: '',
    transfer_date: new Date().toISOString().split('T')[0],
    transfer_reason: '',
    notes: ''
  });

  useEffect(() => {
    fetchOrganizations();
  }, []);

  const fetchOrganizations = async () => {
    try {
      const data = await organizationsService.getOrganizations();
      // Filter out current organization and non-customer organizations
      const customerOrgs = data.filter(org =>
        org.id !== machine.customer_organization_id &&
        org.organization_type === 'customer'
      );
      setOrganizations(customerOrgs);
    } catch (err) {
      console.error('Failed to fetch organizations:', err);
      setError('Failed to load organizations');
    }
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setTransferData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleNext = () => {
    if (currentStep === 1) {
      if (!transferData.new_customer_organization_id) {
        setError('Please select a destination organization');
        return;
      }
    }
    setError('');
    setCurrentStep(prev => prev + 1);
  };

  const handleBack = () => {
    setError('');
    setCurrentStep(prev => prev - 1);
  };

  const handleTransfer = async () => {
    setError('');
    setLoading(true);

    try {
      const transferPayload = {
        machine_id: machine.id,
        new_customer_organization_id: transferData.new_customer_organization_id,
        transfer_date: transferData.transfer_date,
        transfer_reason: transferData.transfer_reason.trim() || null,
        notes: transferData.notes.trim() || null
      };

      await machinesService.transferMachine(transferPayload);

      if (onTransferComplete) {
        onTransferComplete();
      }
      if (onClose) {
        onClose();
      }
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to transfer machine');
    } finally {
      setLoading(false);
    }
  };

  const selectedOrganization = organizations.find(org => org.id === transferData.new_customer_organization_id);

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 w-full max-w-2xl max-h-[90vh] overflow-y-auto">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-xl font-semibold">Transfer Machine</h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600"
            disabled={loading}
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* Progress Steps */}
        <div className="mb-6">
          <div className="flex items-center">
            <div className={`flex items-center justify-center w-8 h-8 rounded-full ${currentStep >= 1 ? 'bg-blue-600 text-white' : 'bg-gray-300 text-gray-600'
              }`}>
              1
            </div>
            <div className={`flex-1 h-1 mx-2 ${currentStep >= 2 ? 'bg-blue-600' : 'bg-gray-300'
              }`}></div>
            <div className={`flex items-center justify-center w-8 h-8 rounded-full ${currentStep >= 2 ? 'bg-blue-600 text-white' : 'bg-gray-300 text-gray-600'
              }`}>
              2
            </div>
            <div className={`flex-1 h-1 mx-2 ${currentStep >= 3 ? 'bg-blue-600' : 'bg-gray-300'
              }`}></div>
            <div className={`flex items-center justify-center w-8 h-8 rounded-full ${currentStep >= 3 ? 'bg-blue-600 text-white' : 'bg-gray-300 text-gray-600'
              }`}>
              3
            </div>
          </div>
          <div className="flex justify-between text-xs text-gray-600 mt-2">
            <span>Select Organization</span>
            <span>Transfer Details</span>
            <span>Confirm</span>
          </div>
        </div>

        {error && (
          <div className="mb-4 p-3 bg-red-100 border border-red-400 text-red-700 rounded">
            {error}
          </div>
        )}

        {/* Machine Info */}
        <div className="mb-6 p-4 bg-gray-50 rounded-lg">
          <h3 className="font-medium mb-2">Machine to Transfer</h3>
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div>
              <span className="text-gray-600">Name:</span> {machine.name || 'N/A'}
            </div>
            <div>
              <span className="text-gray-600">Serial:</span> {machine.serial_number}
            </div>
            <div>
              <span className="text-gray-600">Model:</span> {machine.model}
            </div>
            <div>
              <span className="text-gray-600">Current Hours:</span> {machine.current_hours?.toFixed(1) || 'N/A'}
            </div>
          </div>
        </div>

        {/* Step 1: Select Organization */}
        {currentStep === 1 && (
          <div>
            <h3 className="text-lg font-medium mb-4">Select Destination Organization</h3>
            <div className="space-y-3">
              {organizations.length === 0 ? (
                <p className="text-gray-600">No available customer organizations found.</p>
              ) : (
                organizations.map(org => (
                  <label key={org.id} className="flex items-center p-3 border rounded-lg cursor-pointer hover:bg-gray-50">
                    <input
                      type="radio"
                      name="new_customer_organization_id"
                      value={org.id}
                      checked={transferData.new_customer_organization_id === org.id}
                      onChange={handleInputChange}
                      className="mr-3"
                    />
                    <div>
                      <div className="font-medium">{org.name}</div>
                      <div className="text-sm text-gray-600">
                        {org.country} • {org.organization_type}
                      </div>
                    </div>
                  </label>
                ))
              )}
            </div>
          </div>
        )}

        {/* Step 2: Transfer Details */}
        {currentStep === 2 && (
          <div>
            <h3 className="text-lg font-medium mb-4">Transfer Details</h3>
            <div className="space-y-4">
              <div>
                <label htmlFor="transfer_date" className="block text-sm font-medium text-gray-700 mb-2">
                  Transfer Date *
                </label>
                <input
                  type="date"
                  id="transfer_date"
                  name="transfer_date"
                  value={transferData.transfer_date}
                  onChange={handleInputChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  required
                />
              </div>

              <div>
                <label htmlFor="transfer_reason" className="block text-sm font-medium text-gray-700 mb-2">
                  Transfer Reason *
                </label>
                <select
                  id="transfer_reason"
                  name="transfer_reason"
                  value={transferData.transfer_reason}
                  onChange={handleInputChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  required
                >
                  <option value="">Select reason...</option>
                  <option value="sale">Sale</option>
                  <option value="lease_transfer">Lease Transfer</option>
                  <option value="relocation">Relocation</option>
                  <option value="upgrade">Upgrade</option>
                  <option value="other">Other</option>
                </select>
              </div>

              <div>
                <label htmlFor="notes" className="block text-sm font-medium text-gray-700 mb-2">
                  Additional Notes
                </label>
                <textarea
                  id="notes"
                  name="notes"
                  value={transferData.notes}
                  onChange={handleInputChange}
                  rows={3}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Any additional information about this transfer..."
                />
              </div>
            </div>
          </div>
        )}

        {/* Step 3: Confirmation */}
        {currentStep === 3 && (
          <div>
            <h3 className="text-lg font-medium mb-4">Confirm Transfer</h3>
            <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 mb-4">
              <div className="flex">
                <svg className="w-5 h-5 text-yellow-600 mr-2 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                </svg>
                <div>
                  <p className="text-sm text-yellow-800">
                    <strong>Warning:</strong> This action cannot be undone. The machine will be permanently transferred to the selected organization.
                  </p>
                </div>
              </div>
            </div>

            <div className="space-y-3 text-sm">
              <div className="flex justify-between">
                <span className="text-gray-600">Destination Organization:</span>
                <span className="font-medium">{selectedOrganization?.name}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Transfer Date:</span>
                <span className="font-medium">{transferData.transfer_date}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Reason:</span>
                <span className="font-medium">{transferData.transfer_reason}</span>
              </div>
              {transferData.notes && (
                <div>
                  <span className="text-gray-600">Notes:</span>
                  <p className="mt-1 text-gray-800">{transferData.notes}</p>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Navigation Buttons */}
        <div className="flex justify-between mt-6">
          <div>
            {currentStep > 1 && (
              <button
                onClick={handleBack}
                className="px-4 py-2 text-gray-700 bg-gray-200 rounded-md hover:bg-gray-300 disabled:opacity-50"
                disabled={loading}
              >
                Back
              </button>
            )}
          </div>

          <div className="flex space-x-3">
            <button
              onClick={onClose}
              className="px-4 py-2 text-gray-700 bg-gray-200 rounded-md hover:bg-gray-300 disabled:opacity-50"
              disabled={loading}
            >
              Cancel
            </button>

            {currentStep < 3 ? (
              <button
                onClick={handleNext}
                className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
                disabled={loading}
              >
                Next
              </button>
            ) : (
              <button
                onClick={handleTransfer}
                className="px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 disabled:opacity-50"
                disabled={loading}
              >
                {loading ? 'Transferring...' : 'Confirm Transfer'}
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default MachineTransferWizard;