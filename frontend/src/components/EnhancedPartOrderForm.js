// frontend/src/components/EnhancedPartOrderForm.js

import React, { useState, useEffect } from 'react';
import { useAuth } from '../AuthContext';

function EnhancedPartOrderForm({ organizations = [], parts = [], warehouses = [], onSubmit, onClose }) {
  const { user } = useAuth();
  const [formData, setFormData] = useState({
    supplier_type: 'oraseas_ee', // 'oraseas_ee' or 'own_supplier'
    supplier_organization_id: '',
    customer_organization_id: user?.organization_id || '',
    order_date: new Date().toISOString().split('T')[0],
    expected_delivery_date: '',
    destination_warehouse_id: '',
    notes: '',
    items: []
  });
  const [currentItem, setCurrentItem] = useState({
    part_id: '',
    quantity: 1,
    unit_price: ''
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Find Oraseas EE organization
  const oraseasOrg = organizations.find(org =>
    org.organization_type === 'oraseas_ee' ||
    (org.name === 'Oraseas EE' && org.type === 'Warehouse')
  );

  // Filter suppliers based on selection
  const availableSuppliers = formData.supplier_type === 'oraseas_ee'
    ? [oraseasOrg].filter(Boolean)
    : organizations.filter(org =>
      org.organization_type === 'supplier' &&
      org.parent_organization_id === user?.organization_id
    );

  // Filter warehouses for current user's organization
  const userWarehouses = warehouses.filter(warehouse =>
    warehouse.organization_id === user?.organization_id
  );

  useEffect(() => {
    if (formData.supplier_type === 'oraseas_ee' && oraseasOrg) {
      setFormData(prev => ({
        ...prev,
        supplier_organization_id: oraseasOrg.id
      }));
    } else if (formData.supplier_type === 'own_supplier') {
      setFormData(prev => ({
        ...prev,
        supplier_organization_id: ''
      }));
    }
  }, [formData.supplier_type, oraseasOrg]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
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

    const part = parts.find(p => p.id === currentItem.part_id);
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
      const orderData = {
        ...formData,
        order_date: new Date(formData.order_date).toISOString(),
        expected_delivery_date: formData.expected_delivery_date
          ? new Date(formData.expected_delivery_date).toISOString()
          : null,
        status: 'Requested'
      };

      await onSubmit(orderData);
      onClose();
    } catch (err) {
      setError(err.message || 'Failed to create order');
    } finally {
      setLoading(false);
    }
  };

  const selectedPart = parts.find(p => p.id === currentItem.part_id);

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative" role="alert">
          <strong className="font-bold">Error:</strong>
          <span className="block sm:inline ml-2">{error}</span>
        </div>
      )}

      {/* Supplier Selection */}
      <div className="bg-gray-50 p-4 rounded-lg">
        <h3 className="text-lg font-semibold text-gray-800 mb-3">Supplier Selection</h3>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Supplier Type
            </label>
            <div className="space-y-2">
              <label className="flex items-center">
                <input
                  type="radio"
                  name="supplier_type"
                  value="oraseas_ee"
                  checked={formData.supplier_type === 'oraseas_ee'}
                  onChange={handleChange}
                  className="mr-2"
                  disabled={loading}
                />
                <span className="text-sm">Order from Oraseas EE</span>
              </label>
              <label className="flex items-center">
                <input
                  type="radio"
                  name="supplier_type"
                  value="own_supplier"
                  checked={formData.supplier_type === 'own_supplier'}
                  onChange={handleChange}
                  className="mr-2"
                  disabled={loading}
                />
                <span className="text-sm">Order from my suppliers</span>
              </label>
            </div>
          </div>

          <div>
            <label htmlFor="supplier_organization_id" className="block text-sm font-medium text-gray-700 mb-1">
              Supplier
            </label>
            <select
              id="supplier_organization_id"
              name="supplier_organization_id"
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
              value={formData.supplier_organization_id}
              onChange={handleChange}
              required
              disabled={loading || formData.supplier_type === 'oraseas_ee'}
            >
              <option value="">Select Supplier</option>
              {availableSuppliers.map(supplier => (
                <option key={supplier.id} value={supplier.id}>
                  {supplier.name}
                </option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {/* Order Details */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
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
            value={formData.expected_delivery_date}
            onChange={handleChange}
            disabled={loading}
          />
        </div>
      </div>

      <div>
        <label htmlFor="destination_warehouse_id" className="block text-sm font-medium text-gray-700 mb-1">
          Destination Warehouse
        </label>
        <select
          id="destination_warehouse_id"
          name="destination_warehouse_id"
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
          value={formData.destination_warehouse_id}
          onChange={handleChange}
          required
          disabled={loading}
        >
          <option value="">Select Warehouse</option>
          {userWarehouses.map(warehouse => (
            <option key={warehouse.id} value={warehouse.id}>
              {warehouse.name}
            </option>
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
              disabled={loading}
            >
              <option value="">Select Part</option>
              {parts.map(part => (
                <option key={part.id} value={part.id}>
                  {part.name} ({part.part_number})
                </option>
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
              step={selectedPart?.part_type === 'bulk_material' ? '0.001' : '1'}
              min="0"
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
              value={currentItem.quantity}
              onChange={handleItemChange}
              disabled={loading}
            />
            {selectedPart && (
              <p className="text-xs text-gray-500 mt-1">
                Unit: {selectedPart.unit_of_measure}
              </p>
            )}
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
          </div>

          <div className="flex items-end">
            <button
              type="button"
              onClick={addItem}
              className="w-full bg-green-600 text-white py-2 px-4 rounded-md hover:bg-green-700 font-semibold"
              disabled={loading}
            >
              Add Item
            </button>
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
                    {item.unit_price && ` • Price: $${item.unit_price}`}
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
          value={formData.notes}
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
          {loading ? 'Creating Order...' : 'Create Part Order'}
        </button>
      </div>
    </form>
  );
}

export default EnhancedPartOrderForm;