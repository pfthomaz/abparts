// frontend/src/components/TransactionForm.js

import React, { useState, useEffect } from 'react';
import { transactionService } from '../services/transactionService';
import { partsService } from '../services/partsService';
import { warehouseService } from '../services/warehouseService';
import { machinesService } from '../services/machinesService';
import { useAuth } from '../AuthContext';
import QuantityInput from './QuantityInput';

const TransactionForm = ({ initialData = {}, onSubmit, onClose }) => {
  const { user } = useAuth();
  const [formData, setFormData] = useState({
    transaction_type: 'creation',
    part_id: '',
    from_warehouse_id: '',
    to_warehouse_id: '',
    machine_id: '',
    quantity: '',
    unit_of_measure: 'pieces',
    transaction_date: new Date().toISOString().split('T')[0],
    notes: '',
    reference_number: '',
    ...initialData,
  });

  const [parts, setParts] = useState([]);
  const [warehouses, setWarehouses] = useState([]);
  const [machines, setMachines] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Fetch supporting data
  useEffect(() => {
    const fetchSupportingData = async () => {
      try {
        const [partsData, warehousesData, machinesData] = await Promise.all([
          partsService.getParts(),
          warehouseService.getWarehouses(),
          machinesService.getMachines()
        ]);

        // Handle parts data - API returns {items: [...], total_count: number, has_more: boolean}
        const partsArray = Array.isArray(partsData) ? partsData : (partsData?.items || []);
        setParts(partsArray);

        // Handle warehouses data - API returns direct array
        const warehousesArray = Array.isArray(warehousesData) ? warehousesData : (warehousesData?.items || []);
        setWarehouses(warehousesArray);

        // Handle machines data - API returns direct array
        const machinesArray = Array.isArray(machinesData) ? machinesData : (machinesData?.items || []);
        setMachines(machinesArray);
      } catch (err) {
        console.error('Failed to fetch supporting data:', err);
        setError('Failed to load form data. Please try again.');
        // Set empty arrays on error to prevent map errors
        setParts([]);
        setWarehouses([]);
        setMachines([]);
      }
    };

    fetchSupportingData();
  }, []);

  // Update unit of measure when part changes
  useEffect(() => {
    const selectedPart = parts.find(part => part.id === formData.part_id);
    if (selectedPart && selectedPart.unit_of_measure !== formData.unit_of_measure) {
      setFormData(prev => ({
        ...prev,
        unit_of_measure: selectedPart.unit_of_measure
      }));
    }
  }, [formData.part_id, parts]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const dataToSend = {
        ...formData,
        quantity: parseFloat(formData.quantity) || 0,
        performed_by_user_id: user.id,
        transaction_date: new Date(formData.transaction_date).toISOString(),
        from_warehouse_id: formData.from_warehouse_id || null,
        to_warehouse_id: formData.to_warehouse_id || null,
        machine_id: formData.machine_id || null,
        notes: formData.notes || null,
        reference_number: formData.reference_number || null,
      };

      await onSubmit(dataToSend);
      onClose();
    } catch (err) {
      setError(err.message || 'Failed to create transaction.');
    } finally {
      setLoading(false);
    }
  };

  const selectedPart = parts.find(part => part.id === formData.part_id);

  const getTransactionTypeDescription = (type) => {
    switch (type) {
      case 'creation':
        return 'Add new inventory (from supplier or manufacturer)';
      case 'transfer':
        return 'Move inventory between warehouses';
      case 'consumption':
        return 'Record parts used in machines';
      case 'adjustment':
        return 'Correct inventory discrepancies';
      default:
        return '';
    }
  };

  const isFieldRequired = (field) => {
    switch (formData.transaction_type) {
      case 'creation':
        return ['part_id', 'to_warehouse_id', 'quantity'].includes(field);
      case 'transfer':
        return ['part_id', 'from_warehouse_id', 'to_warehouse_id', 'quantity'].includes(field);
      case 'consumption':
        return ['part_id', 'from_warehouse_id', 'quantity'].includes(field);
      case 'adjustment':
        return ['part_id', 'to_warehouse_id', 'quantity'].includes(field);
      default:
        return false;
    }
  };

  const isFieldVisible = (field) => {
    switch (formData.transaction_type) {
      case 'creation':
        return !['from_warehouse_id'].includes(field);
      case 'transfer':
        return !['machine_id'].includes(field);
      case 'consumption':
        return !['to_warehouse_id'].includes(field);
      case 'adjustment':
        return !['from_warehouse_id', 'machine_id'].includes(field);
      default:
        return true;
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
        <label htmlFor="transaction_type" className="block text-sm font-medium text-gray-700 mb-1">
          Transaction Type
        </label>
        <select
          id="transaction_type"
          name="transaction_type"
          value={formData.transaction_type}
          onChange={handleChange}
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
          disabled={loading}
          required
        >
          <option value="creation">Creation</option>
          <option value="transfer">Transfer</option>
          <option value="consumption">Consumption</option>
          <option value="adjustment">Adjustment</option>
        </select>
        <p className="text-sm text-gray-500 mt-1">
          {getTransactionTypeDescription(formData.transaction_type)}
        </p>
      </div>

      <div>
        <label htmlFor="part_id" className="block text-sm font-medium text-gray-700 mb-1">
          Part {isFieldRequired('part_id') && <span className="text-red-500">*</span>}
        </label>
        <select
          id="part_id"
          name="part_id"
          value={formData.part_id}
          onChange={handleChange}
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
          disabled={loading}
          required={isFieldRequired('part_id')}
        >
          <option value="">Select a part</option>
          {Array.isArray(parts) && parts.map(part => (
            <option key={part.id} value={part.id}>
              {part.name} ({part.part_number}) - {part.unit_of_measure}
            </option>
          ))}
        </select>
      </div>

      {isFieldVisible('from_warehouse_id') && (
        <div>
          <label htmlFor="from_warehouse_id" className="block text-sm font-medium text-gray-700 mb-1">
            From Warehouse {isFieldRequired('from_warehouse_id') && <span className="text-red-500">*</span>}
          </label>
          <select
            id="from_warehouse_id"
            name="from_warehouse_id"
            value={formData.from_warehouse_id}
            onChange={handleChange}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
            disabled={loading}
            required={isFieldRequired('from_warehouse_id')}
          >
            <option value="">Select source warehouse</option>
            {warehouses.map(warehouse => (
              <option key={warehouse.id} value={warehouse.id}>
                {warehouse.name} ({warehouse.location || 'No location'})
              </option>
            ))}
          </select>
        </div>
      )}

      {isFieldVisible('to_warehouse_id') && (
        <div>
          <label htmlFor="to_warehouse_id" className="block text-sm font-medium text-gray-700 mb-1">
            To Warehouse {isFieldRequired('to_warehouse_id') && <span className="text-red-500">*</span>}
          </label>
          <select
            id="to_warehouse_id"
            name="to_warehouse_id"
            value={formData.to_warehouse_id}
            onChange={handleChange}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
            disabled={loading}
            required={isFieldRequired('to_warehouse_id')}
          >
            <option value="">Select destination warehouse</option>
            {warehouses.map(warehouse => (
              <option key={warehouse.id} value={warehouse.id}>
                {warehouse.name} ({warehouse.location || 'No location'})
              </option>
            ))}
          </select>
        </div>
      )}

      {isFieldVisible('machine_id') && (
        <div>
          <label htmlFor="machine_id" className="block text-sm font-medium text-gray-700 mb-1">
            Machine {isFieldRequired('machine_id') && <span className="text-red-500">*</span>}
          </label>
          <select
            id="machine_id"
            name="machine_id"
            value={formData.machine_id}
            onChange={handleChange}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
            disabled={loading}
            required={isFieldRequired('machine_id')}
          >
            <option value="">Select machine (optional)</option>
            {machines.map(machine => (
              <option key={machine.id} value={machine.id}>
                {machine.serial_number} - {machine.model}
              </option>
            ))}
          </select>
        </div>
      )}

      <div>
        <label htmlFor="quantity" className="block text-sm font-medium text-gray-700 mb-1">
          Quantity {isFieldRequired('quantity') && <span className="text-red-500">*</span>}
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
          unitOfMeasure={formData.unit_of_measure}
          min={selectedPart?.part_type === 'bulk_material' ? 0.001 : 1}
          required={isFieldRequired('quantity')}
          disabled={loading}
        />
      </div>

      <div>
        <label htmlFor="transaction_date" className="block text-sm font-medium text-gray-700 mb-1">
          Transaction Date
        </label>
        <input
          type="date"
          id="transaction_date"
          name="transaction_date"
          value={formData.transaction_date}
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
          placeholder="Order number, invoice, etc."
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
          placeholder="Additional details about this transaction"
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
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
          {loading ? 'Creating...' : 'Create Transaction'}
        </button>
      </div>
    </form>
  );
};

export default TransactionForm;