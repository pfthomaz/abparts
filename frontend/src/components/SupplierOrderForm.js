// frontend/src/components/SupplierOrderForm.js

import React, { useState, useEffect, useMemo } from 'react';
import { useAuth } from '../AuthContext';
import { partsService } from '../services/partsService';

function SupplierOrderForm({ organizations = [], parts = [], initialData = {}, onSubmit, onClose }) {
  const { token, user } = useAuth();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [smartParts, setSmartParts] = useState([]);
  const [partsLoading, setPartsLoading] = useState(false);

  // Initialize form data with a function to avoid recreating the object
  const [formData, setFormData] = useState(() => {
    const baseData = {
      ordering_organization_id: '',
      supplier_name: '',
      order_date: new Date().toISOString().split('T')[0],
      expected_delivery_date: '',
      actual_delivery_date: '',
      status: 'Pending',
      notes: '',
      items: [],
      ...initialData,
    };
    
    // Format dates for input fields (YYYY-MM-DD format)
    if (initialData.order_date) {
      baseData.order_date = new Date(initialData.order_date).toISOString().split('T')[0];
    }
    if (initialData.expected_delivery_date) {
      baseData.expected_delivery_date = new Date(initialData.expected_delivery_date).toISOString().split('T')[0];
    }
    if (initialData.actual_delivery_date) {
      baseData.actual_delivery_date = new Date(initialData.actual_delivery_date).toISOString().split('T')[0];
    }
    
    // Normalize items if they exist in initialData
    // API returns items with nested part object, but form expects part at same level
    if (initialData.items && initialData.items.length > 0) {
      baseData.items = initialData.items.map(item => {
        const unitOfMeasure = item.part?.unit_of_measure || item.unit_of_measure || 'units';
        const quantity = unitOfMeasure === 'units' 
          ? Math.floor(parseFloat(item.quantity)) 
          : parseFloat(item.quantity);
        
        return {
          part_id: item.part_id,
          quantity: quantity,
          unit_price: item.unit_price,
          part: item.part || {
            id: item.part_id,
            name: item.part_name || 'Unknown Part',
            part_number: item.part_number || '',
            unit_of_measure: unitOfMeasure
          }
        };
      });
    }
    
    return baseData;
  });

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
    console.log('Organizations data:', organizations);
    const found = organizations.find(org => {
      console.log('Checking org:', org.name, org.organization_type);
      return org.name === 'Oraseas EE' && org.organization_type === 'oraseas_ee';
    });
    console.log('Found Oraseas org:', found);
    return found;
  }, [organizations]);

  const supplierOrganizations = useMemo(() => {
    const suppliers = organizations.filter(org => org.organization_type === 'supplier');
    console.log('Supplier organizations:', suppliers);
    return suppliers;
  }, [organizations]);

  // Simple effect to update organization ID when oraseasOrg becomes available
  useEffect(() => {
    if (oraseasOrg && formData.ordering_organization_id === '') {
      setFormData(prevData => ({
        ...prevData,
        ordering_organization_id: oraseasOrg.id
      }));
    }
  }, [oraseasOrg, formData.ordering_organization_id]);

  // Effect to load smart-sorted parts when ordering organization changes
  useEffect(() => {
    const loadSmartParts = async () => {
      if (!formData.ordering_organization_id) {
        setSmartParts([]);
        return;
      }

      setPartsLoading(true);
      try {
        const sortedParts = await partsService.getPartsForOrders(
          formData.ordering_organization_id,
          'supplier',
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
  }, [formData.ordering_organization_id]);

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
      // Build data object with only the fields that should be sent
      const dataToSend = {
        ordering_organization_id: formData.ordering_organization_id,
        supplier_name: formData.supplier_name,
        order_date: formData.order_date ? new Date(formData.order_date).toISOString() : null,
        expected_delivery_date: formData.expected_delivery_date ? new Date(formData.expected_delivery_date).toISOString() : null,
        actual_delivery_date: formData.actual_delivery_date ? new Date(formData.actual_delivery_date).toISOString() : null,
        status: formData.status,
        notes: formData.notes || '',
        // Format items to only include necessary fields
        items: formData.items.map(item => ({
          part_id: item.part_id,
          quantity: item.quantity,
          unit_price: item.unit_price
        }))
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

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative" role="alert">
          <strong className="font-bold">Error:</strong>
          <span className="block sm:inline ml-2">{error}</span>
        </div>
      )}

      {/* Ordering Organization (pre-filled and disabled for Oraseas EE) */}
      <div>
        <label htmlFor="ordering_organization_id" className="block text-sm font-medium text-gray-700 mb-1">
          Ordering Organization
        </label>
        <select
          id="ordering_organization_id"
          name="ordering_organization_id"
          className="w-full px-3 py-2 border border-gray-300 rounded-md bg-gray-100 cursor-not-allowed"
          value={formData.ordering_organization_id}
          disabled={true} // Always disabled as it's pre-filled
        >
          {oraseasOrg && <option value={oraseasOrg.id}>{oraseasOrg.name}</option>}
          {!oraseasOrg && <option value="">Loading Oraseas EE...</option>}
        </select>
        {(!oraseasOrg && organizations.length > 0) && (
          <p className="text-red-500 text-xs mt-1">
            Oraseas EE organization not found. Please ensure it exists.
            <br />
            <small>Available organizations: {organizations.map(org => `${org.name} (${org.organization_type})`).join(', ')}</small>
          </p>
        )}
      </div>

      {/* Supplier Name Dropdown */}
      <div>
        <label htmlFor="supplier_name" className="block text-sm font-medium text-gray-700 mb-1">
          Supplier Name
        </label>
        <select
          id="supplier_name"
          name="supplier_name"
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
          value={formData.supplier_name}
          onChange={handleChange}
          required
          disabled={loading}
        >
          <option value="">Select a Supplier</option>
          {supplierOrganizations.map(supplier => (
            <option key={supplier.id} value={supplier.name}>{supplier.name}</option>
          ))}
        </select>
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
                  Parts sorted by order frequency for this supplier
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
              <div key={index} className="bg-white p-3 rounded border">
                <div className="flex items-start justify-between mb-2">
                  <div className="flex-1">
                    <span className="font-medium">{item.part.name}</span>
                    <span className="text-gray-500 ml-2">({item.part.part_number})</span>
                  </div>
                  <button
                    type="button"
                    onClick={() => removeItem(index)}
                    className="text-red-600 hover:text-red-800 font-semibold ml-2"
                    disabled={loading}
                  >
                    Remove
                  </button>
                </div>
                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="block text-xs font-medium text-gray-700 mb-1">
                      Quantity ({item.part.unit_of_measure})
                    </label>
                    <input
                      type="number"
                      step={item.part.part_type === 'bulk_material' ? '0.001' : '1'}
                      min="0"
                      value={item.part.part_type === 'bulk_material' ? item.quantity : Math.floor(item.quantity)}
                      onChange={(e) => {
                        const newItems = [...formData.items];
                        if (item.part.part_type === 'bulk_material') {
                          newItems[index].quantity = parseFloat(e.target.value) || 0;
                        } else {
                          newItems[index].quantity = parseInt(e.target.value) || 0;
                        }
                        setFormData(prev => ({ ...prev, items: newItems }));
                      }}
                      className="w-full px-2 py-1 border border-gray-300 rounded-md text-sm focus:ring-blue-500 focus:border-blue-500"
                      disabled={loading}
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-medium text-gray-700 mb-1">
                      Unit Price (optional)
                    </label>
                    <input
                      type="number"
                      step="0.01"
                      min="0"
                      value={item.unit_price || ''}
                      onChange={(e) => {
                        const newItems = [...formData.items];
                        newItems[index].unit_price = e.target.value ? parseFloat(e.target.value) : null;
                        setFormData(prev => ({ ...prev, items: newItems }));
                      }}
                      className="w-full px-2 py-1 border border-gray-300 rounded-md text-sm focus:ring-blue-500 focus:border-blue-500"
                      disabled={loading}
                    />
                  </div>
                </div>
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

export default SupplierOrderForm;
