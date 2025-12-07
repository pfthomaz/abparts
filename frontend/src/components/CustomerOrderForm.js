// frontend/src/components/CustomerOrderForm.js

import React, { useState, useEffect, useMemo } from 'react';
import { useAuth } from '../AuthContext';
import { partsService } from '../services/partsService';
import PartSearchSelector from './PartSearchSelector';
import { useTranslation } from '../hooks/useTranslation';

function CustomerOrderForm({ organizations = [], users = [], parts = [], initialData = {}, onSubmit, onClose }) {
  const { t } = useTranslation();
  const { token, user } = useAuth(); // Current logged-in user
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [smartParts, setSmartParts] = useState([]);
  const [partsLoading, setPartsLoading] = useState(false);

  // Initialize form data with a function to avoid recreating the object
  const [formData, setFormData] = useState(() => {
    const baseData = {
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

  // Effect to pre-fill customer data for non-super_admin users
  useEffect(() => {
    if (user && user.role !== 'super_admin' && !initialData.id) {
      setFormData(prevData => ({
        ...prevData,
        customer_organization_id: user.organization_id || '',
        ordered_by_user_id: user.id || ''
      }));
    }
  }, [user, initialData.id]);
  
  // Effect to pre-select current user if not already set
  useEffect(() => {
    if (user && !formData.ordered_by_user_id && !initialData.id) {
      setFormData(prevData => ({
        ...prevData,
        ordered_by_user_id: user.id || ''
      }));
    }
  }, [user, formData.ordered_by_user_id, initialData.id]);

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
      // Build data object with only the fields that should be sent
      const dataToSend = {
        customer_organization_id: formData.customer_organization_id,
        oraseas_organization_id: formData.oraseas_organization_id,
        order_date: formData.order_date ? new Date(formData.order_date).toISOString() : null,
        expected_delivery_date: formData.expected_delivery_date ? new Date(formData.expected_delivery_date).toISOString() : null,
        actual_delivery_date: formData.actual_delivery_date ? new Date(formData.actual_delivery_date).toISOString() : null,
        status: formData.status,
        ordered_by_user_id: formData.ordered_by_user_id || null,
        notes: formData.notes || '',
        // Format items to only include necessary fields
        items: formData.items.map(item => ({
          part_id: item.part_id,
          quantity: item.quantity,
          unit_price: item.unit_price
        }))
      };

      console.log('=== SUBMITTING ORDER DATA ===');
      console.log('Form data items:', formData.items);
      console.log('Items count:', dataToSend.items.length);
      console.log('Items:', JSON.stringify(dataToSend.items, null, 2));
      console.log('Full dataToSend:', JSON.stringify(dataToSend, null, 2));

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
  const filteredUsers = useMemo(() => {
    if (!formData.customer_organization_id) return [];
    const filtered = users.filter(usr => usr.organization_id === formData.customer_organization_id);
    
    // If current user is not in the filtered list but should be, add them
    if (user && user.organization_id === formData.customer_organization_id) {
      const userInList = filtered.find(u => u.id === user.id);
      if (!userInList) {
        filtered.unshift({
          id: user.id,
          name: user.name,
          username: user.username,
          organization_id: user.organization_id
        });
      }
    }
    
    return filtered;
  }, [users, formData.customer_organization_id, user]);

  // Determine if the organization dropdown should be disabled
  // Non-super_admin users can only order for their own organization
  const disableOrgSelection = loading || (user && user.role !== 'super_admin');
  // User dropdown is always enabled (users can change who placed the order)

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
          {t('orders.customerOrganization')}
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
          <option value="">{t('orders.selectCustomerOrganization')}</option>
          {customerOrganizations.map(org => (
            <option key={org.id} value={org.id}>{org.name}</option>
          ))}
        </select>
      </div>

      {/* Oraseas Organization (pre-filled and disabled) */}
      <div>
        <label htmlFor="oraseas_organization_id" className="block text-sm font-medium text-gray-700 mb-1">
          {t('orders.oraseasOrganization')}
        </label>
        <select
          id="oraseas_organization_id"
          name="oraseas_organization_id"
          className="w-full px-3 py-2 border border-gray-300 rounded-md bg-gray-100 cursor-not-allowed"
          value={formData.oraseas_organization_id}
          disabled={true} // Always disabled as it's pre-filled
        >
          {oraseasOrg && <option value={oraseasOrg.id}>{oraseasOrg.name}</option>}
          {!oraseasOrg && <option value="">{t('orders.loadingOraseasEE')}</option>}
        </select>
        {(!oraseasOrg && !loading) && (
          <p className="text-red-500 text-xs mt-1">{t('orders.oraseasNotFound')}</p>
        )}
      </div>

      <div>
        <label htmlFor="order_date" className="block text-sm font-medium text-gray-700 mb-1">
          {t('orders.orderDate')}
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
          {t('orders.expectedDeliveryDate')}
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
          {t('orders.actualDeliveryDate')}
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
          {t('orders.status')}
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
          <option value="Pending">{t('orders.pending')}</option>
          <option value="Shipped">{t('orders.shipped')}</option>
          <option value="Delivered">{t('orders.delivered')}</option>
          <option value="Cancelled">{t('orders.cancelled')}</option>
        </select>
      </div>

      {/* Ordered By User Dropdown */}
      <div>
        <label htmlFor="ordered_by_user_id" className="block text-sm font-medium text-gray-700 mb-1">
          {t('orders.orderedByUser')}
        </label>
        <select
          id="ordered_by_user_id"
          name="ordered_by_user_id"
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
          value={formData.ordered_by_user_id || ''}
          onChange={handleChange}
          disabled={loading}
        >
          <option value="">{t('orders.selectUserOptional')}</option>
          {filteredUsers.map(u => (
            <option key={u.id} value={u.id}>{u.name || u.username}</option>
          ))}
        </select>
      </div>

      {/* Order Items */}
      <div className="bg-gray-50 p-4 rounded-lg">
        <h3 className="text-lg font-semibold text-gray-800 mb-3">{t('orders.orderItems')}</h3>

        {/* Add Item Form */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-4">
          <div>
            <label htmlFor="part_id" className="block text-sm font-medium text-gray-700 mb-1">
              {t('orders.part')}
            </label>
            <PartSearchSelector
              parts={safeParts}
              value={currentItem.part_id}
              onChange={(partId) => setCurrentItem(prev => ({ ...prev, part_id: partId }))}
              disabled={loading || partsLoading}
              placeholder={partsLoading ? t('orders.loadingParts') : t('orders.searchPartPlaceholder')}
            />
            <div className="h-5 mt-1">
              {smartParts.length > 0 && (
                <p className="text-[10px] text-gray-500 leading-tight">
                  ✨ {t('orders.partsSortedNote')}
                </p>
              )}
            </div>
          </div>

          <div>
            <label htmlFor="quantity" className="block text-sm font-medium text-gray-700 mb-1">
              {t('orders.quantity')}
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
              {t('orders.unitPrice')} ({t('common.optional')})
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
              {t('orders.addItem')}
            </button>
            <div className="h-5 mt-1"></div>
          </div>
        </div>

        {/* Items List */}
        {formData.items.length > 0 && (
          <div className="space-y-2">
            <h4 className="font-medium text-gray-800">{t('orders.orderItems')}:</h4>
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
                    {t('orders.removeItem')}
                  </button>
                </div>
                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="block text-xs font-medium text-gray-700 mb-1">
                      {t('orders.quantity')} ({item.part.unit_of_measure})
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
                      {t('orders.unitPrice')} ({t('common.optional')})
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
          {t('orders.notes')}
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
          {t('common.cancel')}
        </button>
        <button
          type="submit"
          className="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
          disabled={loading}
        >
          {loading ? t('orders.submitting') : (initialData.id ? t('orders.updateOrder') : t('orders.createOrder'))}
        </button>
      </div>
    </form>
  );
}

export default CustomerOrderForm;
