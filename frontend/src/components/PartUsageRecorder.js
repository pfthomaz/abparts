// frontend/src/components/PartUsageRecorder.js

import React, { useState, useEffect } from 'react';
import { useAuth } from '../AuthContext';
import { transactionService } from '../services/transactionService';
import { partsService } from '../services/partsService';
import { warehouseService } from '../services/warehouseService';
import { machinesService } from '../services/machinesService';
import { inventoryService } from '../services/inventoryService';
import QuantityInput from './QuantityInput';
import Modal from './Modal';

const PartUsageRecorder = ({ isOpen, onClose, onUsageRecorded, initialMachineId = null }) => {
  const { user } = useAuth();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);

  // Form data
  const [formData, setFormData] = useState({
    machine_id: initialMachineId || '',
    part_id: '',
    from_warehouse_id: '',
    quantity: '',
    usage_date: new Date().toISOString().split('T')[0],
    notes: '',
    reference_number: ''
  });

  // Supporting data
  const [machines, setMachines] = useState([]);
  const [parts, setParts] = useState([]);
  const [warehouses, setWarehouses] = useState([]);
  const [selectedPartInventory, setSelectedPartInventory] = useState(null);

  // Fetch supporting data
  useEffect(() => {
    if (isOpen) {
      fetchSupportingData();
      resetForm();
    }
  }, [isOpen, initialMachineId]); // eslint-disable-line react-hooks/exhaustive-deps

  // Fetch available inventory when part and warehouse are selected
  useEffect(() => {
    if (formData.part_id && formData.from_warehouse_id) {
      fetchPartInventory();
    } else {
      setSelectedPartInventory(null);
    }
  }, [formData.part_id, formData.from_warehouse_id]); // eslint-disable-line react-hooks/exhaustive-deps

  const fetchSupportingData = async () => {
    try {
      const [machinesData, partsData, warehousesData] = await Promise.all([
        machinesService.getMachines(),
        partsService.getParts(),
        warehouseService.getWarehouses()
      ]);

      setMachines(machinesData);
      setParts(partsData);
      setWarehouses(warehousesData);
    } catch (err) {
      console.error('Failed to fetch supporting data:', err);
      setError('Failed to load form data. Please try again.');
    }
  };

  const fetchPartInventory = async () => {
    try {
      const inventory = await inventoryService.getInventory({
        part_id: formData.part_id,
        warehouse_id: formData.from_warehouse_id
      });

      if (inventory && inventory.length > 0) {
        setSelectedPartInventory(inventory[0]);
      } else {
        setSelectedPartInventory({ quantity: 0 });
      }
    } catch (err) {
      console.error('Failed to fetch inventory:', err);
      setSelectedPartInventory({ quantity: 0 });
    }
  };

  const resetForm = () => {
    setFormData({
      machine_id: initialMachineId || '',
      part_id: '',
      from_warehouse_id: '',
      quantity: '',
      usage_date: new Date().toISOString().split('T')[0],
      notes: '',
      reference_number: ''
    });
    setSelectedPartInventory(null);
    setError(null);
    setSuccess(null);
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const validateForm = () => {
    if (!formData.machine_id) {
      setError('Please select a machine');
      return false;
    }

    if (!formData.part_id) {
      setError('Please select a part');
      return false;
    }

    if (!formData.from_warehouse_id) {
      setError('Please select a warehouse');
      return false;
    }

    if (!formData.quantity || parseFloat(formData.quantity) <= 0) {
      setError('Please enter a valid quantity');
      return false;
    }

    // Check if sufficient inventory is available
    if (selectedPartInventory && parseFloat(formData.quantity) > selectedPartInventory.quantity) {
      setError(`Insufficient inventory. Available: ${selectedPartInventory.quantity}`);
      return false;
    }

    return true;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!validateForm()) {
      return;
    }

    setLoading(true);
    setError(null);
    setSuccess(null);

    try {
      // Create a consumption transaction
      const transactionData = {
        transaction_type: 'consumption',
        part_id: formData.part_id,
        from_warehouse_id: formData.from_warehouse_id,
        machine_id: formData.machine_id,
        quantity: parseFloat(formData.quantity),
        transaction_date: new Date(formData.usage_date).toISOString(),
        notes: formData.notes || null,
        reference_number: formData.reference_number || null,
        performed_by_user_id: user.id
      };

      const result = await transactionService.createTransaction(transactionData);

      setSuccess('Part usage recorded successfully');

      if (onUsageRecorded) {
        onUsageRecorded(result);
      }

      // Reset form for next entry
      setTimeout(() => {
        resetForm();
        setSuccess(null);
      }, 2000);

    } catch (err) {
      setError(err.message || 'Failed to record part usage');
    } finally {
      setLoading(false);
    }
  };

  const selectedPart = parts.find(p => p.id === formData.part_id);
  const selectedMachine = machines.find(m => m.id === formData.machine_id);
  const selectedWarehouse = warehouses.find(w => w.id === formData.from_warehouse_id);

  // Validate organizational boundaries
  const validateOrganizationalBoundary = () => {
    if (!selectedMachine || !selectedWarehouse) return true;

    // Check if machine and warehouse belong to the same organization
    if (selectedMachine.organization_id !== selectedWarehouse.organization_id) {
      return false;
    }

    // Check if user has access to this organization
    if (user.role !== 'super_admin' && user.organization_id !== selectedMachine.organization_id) {
      return false;
    }

    return true;
  };

  const organizationalBoundaryValid = validateOrganizationalBoundary();

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title="Record Part Usage"
      size="lg"
    >
      <form onSubmit={handleSubmit} className="space-y-4">
        {error && (
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative" role="alert">
            <strong className="font-bold">Error:</strong>
            <span className="block sm:inline ml-2">{error}</span>
          </div>
        )}

        {success && (
          <div className="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded relative" role="alert">
            <strong className="font-bold">Success:</strong>
            <span className="block sm:inline ml-2">{success}</span>
          </div>
        )}

        {!organizationalBoundaryValid && selectedMachine && selectedWarehouse && (
          <div className="bg-yellow-100 border border-yellow-400 text-yellow-700 px-4 py-3 rounded relative" role="alert">
            <strong className="font-bold">Warning:</strong>
            <span className="block sm:inline ml-2">
              Selected machine and warehouse belong to different organizations. Please ensure you have proper authorization.
            </span>
          </div>
        )}

        <div>
          <label htmlFor="machine_id" className="block text-sm font-medium text-gray-700 mb-1">
            Machine <span className="text-red-500">*</span>
          </label>
          <select
            id="machine_id"
            name="machine_id"
            value={formData.machine_id}
            onChange={handleChange}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
            disabled={loading}
            required
          >
            <option value="">Select a machine</option>
            {machines.map(machine => (
              <option key={machine.id} value={machine.id}>
                {machine.serial_number} - {machine.model}
                {machine.name && ` (${machine.name})`}
                {user.role === 'super_admin' && ` - ${machine.organization_name}`}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label htmlFor="part_id" className="block text-sm font-medium text-gray-700 mb-1">
            Part <span className="text-red-500">*</span>
          </label>
          <select
            id="part_id"
            name="part_id"
            value={formData.part_id}
            onChange={handleChange}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
            disabled={loading}
            required
          >
            <option value="">Select a part</option>
            {parts.map(part => (
              <option key={part.id} value={part.id}>
                {part.name} ({part.part_number}) - {part.unit_of_measure}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label htmlFor="from_warehouse_id" className="block text-sm font-medium text-gray-700 mb-1">
            From Warehouse <span className="text-red-500">*</span>
          </label>
          <select
            id="from_warehouse_id"
            name="from_warehouse_id"
            value={formData.from_warehouse_id}
            onChange={handleChange}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
            disabled={loading}
            required
          >
            <option value="">Select source warehouse</option>
            {warehouses.map(warehouse => (
              <option key={warehouse.id} value={warehouse.id}>
                {warehouse.name} ({warehouse.location || 'No location'})
                {user.role === 'super_admin' && ` - ${warehouse.organization_name}`}
              </option>
            ))}
          </select>
        </div>

        {/* Inventory availability display */}
        {selectedPartInventory && formData.part_id && formData.from_warehouse_id && (
          <div className="bg-blue-50 p-3 rounded-md">
            <div className="flex items-center">
              <svg className="w-5 h-5 text-blue-600 mr-2" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
              </svg>
              <span className="text-sm text-blue-800">
                <strong>Available Inventory:</strong> {selectedPartInventory.quantity} {selectedPart?.unit_of_measure}
                {selectedPartInventory.quantity === 0 && (
                  <span className="text-red-600 ml-2">(No stock available)</span>
                )}
              </span>
            </div>
          </div>
        )}

        <div>
          <label htmlFor="quantity" className="block text-sm font-medium text-gray-700 mb-1">
            Quantity Used <span className="text-red-500">*</span>
            {selectedPart && (
              <span className="text-sm text-gray-500 ml-2">
                ({selectedPart.part_type === 'consumable' ? 'Whole units' : 'Decimal quantities allowed'})
              </span>
            )}
          </label>
          <QuantityInput
            name="quantity"
            value={formData.quantity}
            onChange={handleChange}
            partType={selectedPart?.part_type || 'consumable'}
            unitOfMeasure={selectedPart?.unit_of_measure || 'pieces'}
            min={selectedPart?.part_type === 'bulk_material' ? 0.001 : 1}
            max={selectedPartInventory?.quantity}
            required
            disabled={loading}
          />
        </div>

        <div>
          <label htmlFor="usage_date" className="block text-sm font-medium text-gray-700 mb-1">
            Usage Date <span className="text-red-500">*</span>
          </label>
          <input
            type="date"
            id="usage_date"
            name="usage_date"
            value={formData.usage_date}
            onChange={handleChange}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
            disabled={loading}
            required
          />
        </div>

        <div>
          <label htmlFor="reference_number" className="block text-sm font-medium text-gray-700 mb-1">
            Reference Number
          </label>
          <input
            type="text"
            id="reference_number"
            name="reference_number"
            value={formData.reference_number}
            onChange={handleChange}
            placeholder="Work order, service ticket, etc."
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
            disabled={loading}
          />
        </div>

        <div>
          <label htmlFor="notes" className="block text-sm font-medium text-gray-700 mb-1">
            Notes
          </label>
          <textarea
            id="notes"
            name="notes"
            rows="3"
            value={formData.notes}
            onChange={handleChange}
            placeholder="Additional details about this part usage"
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
            disabled={loading}
          />
        </div>

        {/* Summary section */}
        {formData.machine_id && formData.part_id && formData.quantity && (
          <div className="bg-gray-50 p-4 rounded-lg">
            <h4 className="font-medium text-gray-900 mb-2">Usage Summary</h4>
            <div className="text-sm text-gray-700 space-y-1">
              <div>
                <strong>Machine:</strong> {selectedMachine?.serial_number} - {selectedMachine?.model}
              </div>
              <div>
                <strong>Part:</strong> {selectedPart?.name} ({selectedPart?.part_number})
              </div>
              <div>
                <strong>Quantity:</strong> {formData.quantity} {selectedPart?.unit_of_measure}
              </div>
              <div>
                <strong>From:</strong> {selectedWarehouse?.name}
              </div>
              <div>
                <strong>Date:</strong> {new Date(formData.usage_date).toLocaleDateString()}
              </div>
            </div>
          </div>
        )}

        <div className="flex justify-end space-x-3 pt-4 border-t border-gray-200">
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
            className="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50"
            disabled={loading || !organizationalBoundaryValid || (selectedPartInventory && selectedPartInventory.quantity === 0)}
          >
            {loading ? 'Recording...' : 'Record Usage'}
          </button>
        </div>
      </form>
    </Modal>
  );
};

export default PartUsageRecorder;