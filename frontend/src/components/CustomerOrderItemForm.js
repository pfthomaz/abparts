// frontend/src/components/CustomerOrderItemForm.js

import React, { useState, useEffect } from 'react';
import { useAuth } from '../AuthContext';

function CustomerOrderItemForm({ customerOrders = [], parts = [], initialData = {}, onSubmit, onClose }) {
  const { token, user } = useAuth(); // Current logged-in user
  const [formData, setFormData] = useState({
    customer_order_id: '',
    part_id: '',
    quantity: 1,
    unit_price: '', // Using string to allow empty value for optional float
    ...initialData,
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    // Reset form data when initialData changes
    const resetData = {
      customer_order_id: '',
      part_id: '',
      quantity: 1,
      unit_price: '',
    };
    setFormData({ ...resetData, ...initialData });
  }, [initialData]);

  const handleChange = (e) => {
    const { name, value, type } = e.target;
    setFormData((prevData) => ({
      ...prevData,
      [name]: type === 'number' ? parseFloat(value) : value, // Keep number for price, let backend handle int for quantity
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      // Ensure numerical fields are parsed correctly, or set to null if empty string for optional fields
      const dataToSend = {
        ...formData,
        quantity: parseInt(formData.quantity, 10),
        unit_price: formData.unit_price === '' ? null : parseFloat(formData.unit_price),
      };

      await onSubmit(dataToSend);
      onClose(); // Close modal on successful submission
    } catch (err) {
      setError(err.message || 'An unexpected error occurred.');
    } finally {
      setLoading(false);
    }
  };

  // Determine if the form should be editable based on user role
  const canModify = user && (user.role === "Oraseas Admin" || user.role === "Oraseas Inventory Manager" || user.role === "Customer Admin" || user.role === "Customer User");

  // Filter customer orders based on user's organization if they are a customer
  const filteredCustomerOrders = user && (user.role === 'Customer Admin' || user.role === 'Customer User')
    ? customerOrders.filter(order => order.customer_organization_id === user.organization_id)
    : customerOrders;

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative" role="alert">
          <strong className="font-bold">Error:</strong>
          <span className="block sm:inline ml-2">{error}</span>
        </div>
      )}

      <div>
        <label htmlFor="customer_order_id" className="block text-sm font-medium text-gray-700 mb-1">
          Customer Order
        </label>
        <select
          id="customer_order_id"
          name="customer_order_id"
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
          value={formData.customer_order_id}
          onChange={handleChange}
          required
          disabled={loading || !canModify || initialData.id} // Disable on edit, or if not authorized
        >
          <option value="">Select a Customer Order</option>
          {filteredCustomerOrders.map((order) => (
            <option key={order.id} value={order.id}>Order {order.id.substring(0, 8)} - {new Date(order.order_date).toLocaleDateString()}</option>
          ))}
        </select>
      </div>

      <div>
        <label htmlFor="part_id" className="block text-sm font-medium text-gray-700 mb-1">
          Part
        </label>
        <select
          id="part_id"
          name="part_id"
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
          value={formData.part_id}
          onChange={handleChange}
          required
          disabled={loading || !canModify || initialData.id} // Disable on edit, or if not authorized
        >
          <option value="">Select a Part</option>
          {parts.map((part) => (
            <option key={part.id} value={part.id}>{part.name} ({part.part_number})</option>
          ))}
        </select>
      </div>

      <div>
        <label htmlFor="quantity" className="block text-sm font-medium text-gray-700 mb-1">
          Quantity
        </label>
        <input
          type="number"
          id="quantity"
          name="quantity"
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
          value={formData.quantity}
          onChange={handleChange}
          min="1"
          required
          disabled={loading || !canModify}
        />
      </div>

      <div>
        <label htmlFor="unit_price" className="block text-sm font-medium text-gray-700 mb-1">
          Unit Price (Optional)
        </label>
        <input
          type="number"
          id="unit_price"
          name="unit_price"
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
          value={formData.unit_price || ''}
          onChange={handleChange}
          step="0.01"
          min="0"
          disabled={loading || !canModify}
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
          disabled={loading || !canModify}
        >
          {loading ? 'Submitting...' : (initialData.id ? 'Update Item' : 'Add Item to Order')}
        </button>
      </div>
    </form>
  );
}

export default CustomerOrderItemForm;
