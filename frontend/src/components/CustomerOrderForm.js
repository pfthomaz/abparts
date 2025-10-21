// frontend/src/components/CustomerOrderForm.js

import React, { useState, useEffect, useMemo } from 'react';
import { useAuth } from '../AuthContext';
import { partsService } from '../services/partsService';

function CustomerOrderForm({ organizations = [], users = [], parts = [], initialData = {}, onSubmit, onClose }) {
  const { token, user } = useAuth(); // Current logged-in user
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [smartParts, setSmartParts] = useState([]);
  const [partsLoading, setPartsLoading] = useState(false);

  // Initialize form data with a function to avoid recreating the object
  const [formData, setFormData] = useState(() => ({
    customer_organization_id: '',
    oraseas_organization_id: '',
    order_date: new Date().toISOString().split('T')[0],
    expected_delivery_date: '',
    actual_delivery_date: '',
    status: 'Pending',
    ordered_by_user_id: '',
    notes: '',
    items: [],
    ...initialData,
  }));

  // State for adding new items
  const [currentItem, setCurrentItem] = useState({
    part_id: '',
    quantity: 1,
    unit_price: ''
  });

  // Use smart parts if available, otherwise fallback to provided parts
  const safeParts = smartParts.length > 0 ? smartParts : (Array.isArray(parts) ? parts : []);

  // Use useMemo to prevent recalculation on every render
  const oraseasOrg = useMemo(() => {
    return organizations.find(org => org.name === 'Oraseas EE' && org.organization_type === 'oraseas_ee');
  }, [organizations]);

  // Simple effect to update organization ID when oraseasOrg becomes available
  useEffect(() => {
    if (oraseasOrg && formData.oraseas_organization_id === '') {
      setFormData(prevData => ({
        ...prevData,
        oraseas_organization_id: oraseasOrg.id
      }));
    }
  }, [oraseasOrg, formData.oraseas_organization_id]);

  // Effect to pre-fill customer data for customer users
  useEffect(() => {
    if (user && (user.role === 'Customer Admin' || user.role === 'Customer User')) {
      setFormData(prevData => ({
        ...prevData,
        customer_organization_id: user.organization_id || '',
        ordered_by_user_id: user.id || ''
      }));
    }
  }, [user]);

  // Effect to load smart-sorted parts when customer organization changes
  useEffect(() => {
    const loadSmartParts = async () => {
      if (!formData.customer_organization_id) {
        setSmartParts([]);
        return;
      }

      setPartsLoading(true);
      try {
        const sortedParts = await partsService.getPartsForOrders(
          formData.customer_organization_id,
          'customer',
          { limit: 1000 } // Get a large number of parts for the dropdown
        );
        setSmartParts(sortedParts);
      } catch (error) {
        console.warn('Failed to load smart-sorted parts, using fallback:', error);
        // Keep using the provided parts as fallback
        setSmartParts([]);
      } finally {
        setPartsLoading(false);
      }
    };

    loadSmartParts();
  }, [formData.customer_organization_id]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prevData) => ({
      ...prevData,
      [name]: value,
    }));
  };

  const handleItemChange = (e) => {
    const { name, value } = e.target;
    setCurrentItem(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const addItem = () => {
    if (!currentItem.part_id || !currentItem.quantity) {
      setError('Please select a part and enter quantity');
      return;
    }

    const part = safeParts.find(p => p.id === currentItem.part_id);
    if (!part) {
      setError('Selected part not found');
      return;
    }

    const newItem = {
      ...currentItem,
      part,
      quantity: parseFloat(currentItem.quantity),
      unit_price: currentItem.unit_price ? parseFloat(currentItem.unit_price) : null
    };

    setFormData(prev => ({
      ...prev,
      items: [...prev.items, newItem]
    }));

    setCurrentItem({
      part_id: '',
      quantity: 1,
      unit_price: ''
    });
    setError(null);
  };

  const removeItem = (index) => {
    setFormData(prev => ({
      ...prev,
      items: prev.items.filter((_, i) => i !== index)
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    if (formData.items.length === 0) {
      setError('Please add at least one item to the order');
      setLoading(false);
      return;
    }

    try {
      // Convert date strings to ISO 8601 format or set to null if empty
      const dataToSend = {
        ...formData,
        order_date: formData.order_date ? new Date(formData.order_date).toISOString() : null,
        expected_delivery_date: formData.expected_delivery_date ? new Date(formData.expected_delivery_date).toISOString() : null,
        actual_delivery_date: formData.actual_delivery_date ? new Date(formData.actual_delivery_date).toISOString() : null,
        // Ensure ordered_by_user_id is null if empty string
        ordered_by_user_id: formData.ordered_by_user_id || null,
      };

      await onSubmit(dataToSend);
      onClose(); // Close modal on successful submission
    } catch (err) {
      setError(err.message || 'An unexpected error occurred.');
    } finally {
      setLoading(false);
    }
  };

  const selectedPart = safeParts.find(p => p.id === currentItem.part_id);

  // Filter organizations: only 'customer' type can be selected as customer_organization_id
  const customerOrganizations = useMemo(() => {
    return organizations.filter(org => org.organization_type === 'customer');
  }, [organizations]);

  // Filter users based on the selected customer_organization_id
  const filteredUsers = users.filter(usr => usr.organization_id === formData.customer_organization_id);

  // Determine if the organization dropdown should be disabled
  const disableOrgSelection = loading || (user && (user.role === 'Customer Admin' || user.role === 'Customer User'));
  // Determine if the user dropdown should be disabled
  const disableUserSelection = loading || (user && (user.role === 'Customer Admin' || user.role === 'Customer User'));

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative" role="alert">
          <strong className="font-bold">Error:</strong>
          <span className="block sm:inline ml-2">{error}</span>
        </div>
      )}

      {/* Customer Organization Dropdown */}
      <div>
        <label htmlFor="customer_organization_id" className="block text-sm font-medium text-gray-700 mb-1">
          Customer Organization
        </label>
        <select
          id="customer_organization_id"
          name="customer_organization_id"
          className={`w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500 ${disableOrgSelection ? 'bg-gray-100 cursor-not-allowed' : ''}`}
          value={formData.customer_organization_id}
          onChange={handleChange}
          required
          disabled={disableOrgSelection}
        >
          <option value="">Select Customer Organization</option>
          {customerOrganizations.map(org => (
            <option key={org.id} value={org.id}>{org.name}</option>
          ))}
        </select>
      </div>

      {/* Oraseas Organization (pre-filled and disabled) */}
      <div>
        <label htmlFor="oraseas_organization_id" className="block text-sm font-medium text-gray-700 mb-1">
          Oraseas Organization (Receiving Order)
        </label>
        <select
          id="oraseas_organization_id"
          name="oraseas_organization_id"
          className="w-full px-3 py-2 border border-gray-300 rounded-md bg-gray-100 cursor-not-allowed"
          value={formData.oraseas_organization_id}
          disabled={true} // Always disabled as it's pre-filled
        >
          {oraseasOrg && <option value={oraseasOrg.id}>{oraseasOrg.name}</option>}
          {!oraseasOrg && <option value="">Loading Oraseas EE...</option>}
        </select>
        {(!oraseasOrg && !loading) && (
          <p className="text-red-500 text-xs mt-1">Oraseas EE organization not found. Please ensure it exists.</p>
        )}
      </div>

      <div>
        <label htmlFor="order_date" className="block text-sm font-medium text-gray-700 mb-1">
          Order Date
        </label>
        <input
          type="date"
          id="order_date"
          name="order_date"
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
          value={formData.order_date}
          onChange={handleChange}
          required
          disabled={loading}
        />
      </div>

      <div>
        <label htmlFor="expected_delivery_date" className="block text-sm font-medium text-gray-700 mb-1">
          Expected Delivery Date
        </label>
        <input
          type="date"
          id="expected_delivery_date"
          name="expected_delivery_date"
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
          value={formData.expected_delivery_date || ''}
          onChange={handleChange}
          disabled={loading}
        />
      </div>

      <div>
        <label htmlFor="actual_delivery_date" className="block text-sm font-medium text-gray-700 mb-1">
          Actual Delivery Date
        </label>
        <input
          type="date"
          id="actual_delivery_date"
          name="actual_delivery_date"
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
          value={formData.actual_delivery_date || ''}
          onChange={handleChange}
          disabled={loading}
        />
      </div>

      <div>
        <label htmlFor="status" className="block text-sm font-medium text-gray-700 mb-1">
          Status
        </label>
        <select
          id="status"
          name="status"
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
          value={formData.status}
          onChange={handleChange}
          required
          disabled={loading}
        >
          <option value="Pending">Pending</option>
          <option value="Shipped">Shipped</option>
          <option value="Delivered">Delivered</option>
          <option value="Cancelled">Cancelled</option>
        </select>
      </div>

      {/* Ordered By User Dropdown */}
      <div>
        <label htmlFor="ordered_by_user_id" className="block text-sm font-medium text-gray-700 mb-1">
          Ordered By User (Optional)
        </label>
        <select
          id="ordered_by_user_id"
          name="ordered_by_user_id"
          className={`w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500 ${disableUserSelection ? 'bg-gray-100 cursor-not-allowed' : ''}`}
          value={formData.ordered_by_user_id || ''}
          onChange={handleChange}
          disabled={disableUserSelection}
        >
          <option value="">Select User (Optional)</option>
          {filteredUsers.map(u => (
            <option key={u.id} value={u.id}>{u.name || u.username}</option>
          ))}
        </select>
      </div>

      {/* Order Items */}
      <div className="bg-gray-50 p-4 rounded-lg">
        <h3 className="text-lg font-semibold text-gray-800 mb-3">Order Items</h3>

        {/* Add Item Form */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-4">
          <div>
            <label htmlFor="part_id" className="block text-sm font-medium text-gray-700 mb-1">
              Part
            </label>
            <select
              id="part_id"
              name="part_id"
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
              value={currentItem.part_id}
              onChange={handleItemChange}
              disabled={loading || partsLoading}
            >
              <option value="">
                {partsLoading ? 'Loading parts...' : 'Select Part'}
              </option>
              {safeParts.map(part => (
                <option key={part.id} value={part.id}>
                  {part.name} ({part.part_number})
                </option>
              ))}
            </select>
            <div className="h-5 mt-1">
              {smartParts.length > 0 && (
                <p className="text-xs text-gray-500">
                  Parts sorted by order frequency for this customer
                </p>
              )}
            </div>
          </div>

          <div>
            <label htmlFor="quantity" className="block text-sm font-medium text-gray-700 mb-1">
              Quantity
            </label>
            <input
              type="number"
              id="quantity"
              name="quantity"
              step={selectedPart?.part_type === 'bulk_material' ? '0.001' : '1'}
              min="0"
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
              value={currentItem.quantity}
              onChange={handleItemChange}
              disabled={loading}
            />
            <div className="h-5 mt-1">
              {selectedPart && (
                <p className="text-xs text-gray-500">
                  Unit: {selectedPart.unit_of_measure}
                </p>
              )}
            </div>
          </div>

          <div>
            <label htmlFor="unit_price" className="block text-sm font-medium text-gray-700 mb-1">
              Unit Price (Optional)
            </label>
            <input
              type="number"
              id="unit_price"
              name="unit_price"
              step="0.01"
              min="0"
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
              value={currentItem.unit_price}
              onChange={handleItemChange}
              disabled={loading}
            />
            <div className="h-5 mt-1"></div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">&nbsp;</label>
            <button
              type="button"
              onClick={addItem}
              className="w-full bg-green-600 text-white py-2 px-4 rounded-md hover:bg-green-700 font-semibold"
              disabled={loading}
            >
              Add Item
            </button>
            <div className="h-5 mt-1"></div>
          </div>
        </div>

        {/* Items List */}
        {formData.items.length > 0 && (
          <div className="space-y-2">
            <h4 className="font-medium text-gray-800">Order Items:</h4>
            {formData.items.map((item, index) => (
              <div key={index} className="flex items-center justify-between bg-white p-3 rounded border">
                <div className="flex-1">
                  <span className="font-medium">{item.part.name}</span>
                  <span className="text-gray-500 ml-2">({item.part.part_number})</span>
                  <div className="text-sm text-gray-600">
                    Quantity: {item.quantity} {item.part.unit_of_measure}
                    {item.unit_price && ` • Price: ${item.unit_price}`}
                  </div>
                </div>
                <button
                  type="button"
                  onClick={() => removeItem(index)}
                  className="text-red-600 hover:text-red-800 font-semibold"
                  disabled={loading}
                >
                  Remove
                </button>
              </div>
            ))}
          </div>
        )}
      </div>

      <div>
        <label htmlFor="notes" className="block text-sm font-medium text-gray-700 mb-1">
          Notes
        </label>
        <textarea
          id="notes"
          name="notes"
          rows="3"
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
          value={formData.notes || ''}
          onChange={handleChange}
          disabled={loading}
        ></textarea>
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
          {loading ? 'Submitting...' : (initialData.id ? 'Update Order' : 'Create Order')}
        </button>
      </div>
    </form>
  );
}

export default CustomerOrderForm;
