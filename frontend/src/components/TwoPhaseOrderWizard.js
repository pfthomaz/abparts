// frontend/src/components/TwoPhaseOrderWizard.js

import React, { useState, useEffect } from 'react';
import { useAuth } from '../AuthContext';
import { ordersService } from '../services/ordersService';
import { partsService } from '../services/partsService';
import { warehouseService } from '../services/warehouseService';
import { organizationsService } from '../services/organizationsService';
import QuantityInput from './QuantityInput';
import Modal from './Modal';

const TwoPhaseOrderWizard = ({ isOpen, onClose, onOrderComplete }) => {
  const { user } = useAuth();
  const [currentStep, setCurrentStep] = useState(1);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Form data for the order
  const [orderData, setOrderData] = useState({
    supplier_type: 'external_supplier',
    supplier_organization_id: '',
    supplier_name: '',
    priority: 'medium',
    requested_delivery_date: '',
    notes: '',
    items: []
  });

  // Supporting data
  const [suppliers, setSuppliers] = useState([]);
  const [parts, setParts] = useState([]);

  // Current item being added
  const [currentItem, setCurrentItem] = useState({
    part_id: '',
    quantity: '',
    unit_price: '',
    notes: ''
  });

  // Fetch supporting data
  useEffect(() => {
    if (isOpen) {
      fetchSupportingData();
      resetForm();
    }
  }, [isOpen]);

  const fetchSupportingData = async () => {
    try {
      const [suppliersData, partsData] = await Promise.all([
        organizationsService.getOrganizations({ type: 'supplier' }),
        partsService.getParts()
      ]);

      setSuppliers(suppliersData);
      setParts(partsData);
    } catch (err) {
      console.error('Failed to fetch supporting data:', err);
      setError('Failed to load form data. Please try again.');
    }
  };

  const resetForm = () => {
    setCurrentStep(1);
    setOrderData({
      supplier_type: 'external_supplier',
      supplier_organization_id: '',
      supplier_name: '',
      priority: 'medium',
      requested_delivery_date: '',
      notes: '',
      items: []
    });
    setCurrentItem({
      part_id: '',
      quantity: '',
      unit_price: '',
      notes: ''
    });
    setError(null);
  };

  const handleOrderDataChange = (e) => {
    const { name, value } = e.target;
    setOrderData(prev => ({
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

  const addItemToOrder = () => {
    if (!currentItem.part_id || !currentItem.quantity) {
      setError('Please select a part and enter quantity');
      return;
    }

    const selectedPart = parts.find(p => p.id === currentItem.part_id);
    if (!selectedPart) {
      setError('Selected part not found');
      return;
    }

    const newItem = {
      ...currentItem,
      part_name: selectedPart.name,
      part_number: selectedPart.part_number,
      unit_of_measure: selectedPart.unit_of_measure,
      quantity: parseFloat(currentItem.quantity),
      unit_price: currentItem.unit_price ? parseFloat(currentItem.unit_price) : null
    };

    setOrderData(prev => ({
      ...prev,
      items: [...prev.items, newItem]
    }));

    // Reset current item
    setCurrentItem({
      part_id: '',
      quantity: '',
      unit_price: '',
      notes: ''
    });
    setError(null);
  };

  const removeItemFromOrder = (index) => {
    setOrderData(prev => ({
      ...prev,
      items: prev.items.filter((_, i) => i !== index)
    }));
  };

  const validateStep = (step) => {
    switch (step) {
      case 1:
        if (orderData.supplier_type === 'external_supplier' && !orderData.supplier_organization_id && !orderData.supplier_name) {
          setError('Please select a supplier or enter supplier name');
          return false;
        }
        break;
      case 2:
        if (orderData.items.length === 0) {
          setError('Please add at least one item to the order');
          return false;
        }
        break;
      default:
        break;
    }
    setError(null);
    return true;
  };

  const nextStep = () => {
    if (validateStep(currentStep)) {
      setCurrentStep(prev => prev + 1);
    }
  };

  const prevStep = () => {
    setCurrentStep(prev => prev - 1);
    setError(null);
  };

  const submitOrder = async () => {
    if (!validateStep(2)) return;

    setLoading(true);
    setError(null);

    try {
      // Prepare order data for submission
      const orderToSubmit = {
        customer_organization_id: user.organization_id,
        supplier_type: orderData.supplier_type,
        supplier_organization_id: orderData.supplier_organization_id || null,
        supplier_name: orderData.supplier_name || null,
        priority: orderData.priority,
        requested_delivery_date: orderData.requested_delivery_date ?
          new Date(orderData.requested_delivery_date).toISOString() : null,
        notes: orderData.notes || null,
        items: orderData.items.map(item => ({
          part_id: item.part_id,
          quantity: item.quantity,
          unit_price: item.unit_price,
          notes: item.notes || null
        }))
      };

      // Create the order (this will be in "requested" status initially)
      const createdOrder = await ordersService.createSupplierOrder(orderToSubmit);

      if (onOrderComplete) {
        onOrderComplete(createdOrder);
      }

      onClose();
    } catch (err) {
      setError(err.message || 'Failed to create order');
    } finally {
      setLoading(false);
    }
  };

  const renderStepIndicator = () => (
    <div className="flex items-center justify-center mb-6">
      <div className="flex items-center space-x-4">
        {[1, 2, 3].map((step) => (
          <div key={step} className="flex items-center">
            <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium ${step <= currentStep
              ? 'bg-blue-600 text-white'
              : 'bg-gray-200 text-gray-600'
              }`}>
              {step}
            </div>
            {step < 3 && (
              <div className={`w-12 h-0.5 ${step < currentStep ? 'bg-blue-600' : 'bg-gray-200'
                }`} />
            )}
          </div>
        ))}
      </div>
    </div>
  );

  const renderStep1 = () => (
    <div className="space-y-4">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">Order Details</h3>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Supplier Type
        </label>
        <select
          name="supplier_type"
          value={orderData.supplier_type}
          onChange={handleOrderDataChange}
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
          disabled={loading}
        >
          <option value="oraseas_ee">Oraseas EE</option>
          <option value="external_supplier">External Supplier</option>
        </select>
      </div>

      {orderData.supplier_type === 'external_supplier' && (
        <>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Select Supplier
            </label>
            <select
              name="supplier_organization_id"
              value={orderData.supplier_organization_id}
              onChange={handleOrderDataChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
              disabled={loading}
            >
              <option value="">Select from registered suppliers</option>
              {suppliers.map(supplier => (
                <option key={supplier.id} value={supplier.id}>
                  {supplier.name}
                </option>
              ))}
            </select>
          </div>

          <div className="text-center text-gray-500 text-sm">or</div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              New Supplier Name
            </label>
            <input
              type="text"
              name="supplier_name"
              value={orderData.supplier_name}
              onChange={handleOrderDataChange}
              placeholder="Enter supplier name"
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
              disabled={loading}
            />
          </div>
        </>
      )}

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Priority
        </label>
        <select
          name="priority"
          value={orderData.priority}
          onChange={handleOrderDataChange}
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
          disabled={loading}
        >
          <option value="low">Low</option>
          <option value="medium">Medium</option>
          <option value="high">High</option>
          <option value="urgent">Urgent</option>
        </select>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Requested Delivery Date
        </label>
        <input
          type="date"
          name="requested_delivery_date"
          value={orderData.requested_delivery_date}
          onChange={handleOrderDataChange}
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
          disabled={loading}
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Notes
        </label>
        <textarea
          name="notes"
          value={orderData.notes}
          onChange={handleOrderDataChange}
          rows="3"
          placeholder="Additional notes for this order"
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
          disabled={loading}
        />
      </div>
    </div>
  );

  const renderStep2 = () => {
    const selectedPart = parts.find(p => p.id === currentItem.part_id);

    return (
      <div className="space-y-4">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Order Items</h3>

        {/* Add Item Form */}
        <div className="bg-gray-50 p-4 rounded-lg space-y-4">
          <h4 className="font-medium text-gray-900">Add Item</h4>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Part
              </label>
              <select
                name="part_id"
                value={currentItem.part_id}
                onChange={handleItemChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                disabled={loading}
              >
                <option value="">Select a part</option>
                {parts.map(part => (
                  <option key={part.id} value={part.id}>
                    {part.name} ({part.part_number})
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Quantity
                {selectedPart && (
                  <span className="text-sm text-gray-500 ml-2">
                    ({selectedPart.unit_of_measure})
                  </span>
                )}
              </label>
              <QuantityInput
                name="quantity"
                value={currentItem.quantity}
                onChange={handleItemChange}
                partType={selectedPart?.part_type || 'consumable'}
                unitOfMeasure={selectedPart?.unit_of_measure || 'pieces'}
                min={selectedPart?.part_type === 'bulk_material' ? 0.001 : 1}
                disabled={loading}
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Unit Price (Optional)
              </label>
              <input
                type="number"
                name="unit_price"
                value={currentItem.unit_price}
                onChange={handleItemChange}
                step="0.01"
                min="0"
                placeholder="0.00"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                disabled={loading}
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Item Notes (Optional)
              </label>
              <input
                type="text"
                name="notes"
                value={currentItem.notes}
                onChange={handleItemChange}
                placeholder="Notes for this item"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                disabled={loading}
              />
            </div>
          </div>

          <button
            type="button"
            onClick={addItemToOrder}
            className="px-4 py-2 text-sm font-medium text-white bg-green-600 rounded-md hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2"
            disabled={loading}
          >
            Add Item
          </button>
        </div>

        {/* Order Items List */}
        {orderData.items.length > 0 && (
          <div className="space-y-2">
            <h4 className="font-medium text-gray-900">Order Items ({orderData.items.length})</h4>
            <div className="space-y-2">
              {orderData.items.map((item, index) => (
                <div key={index} className="flex items-center justify-between p-3 bg-white border border-gray-200 rounded-md">
                  <div className="flex-1">
                    <div className="font-medium text-gray-900">
                      {item.part_name} ({item.part_number})
                    </div>
                    <div className="text-sm text-gray-500">
                      Quantity: {item.quantity} {item.unit_of_measure}
                      {item.unit_price && ` • Unit Price: $${item.unit_price}`}
                      {item.notes && ` • ${item.notes}`}
                    </div>
                  </div>
                  <button
                    type="button"
                    onClick={() => removeItemFromOrder(index)}
                    className="ml-4 text-red-600 hover:text-red-800"
                    disabled={loading}
                  >
                    <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
                    </svg>
                  </button>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    );
  };

  const renderStep3 = () => (
    <div className="space-y-4">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">Review Order</h3>

      <div className="bg-gray-50 p-4 rounded-lg space-y-3">
        <div>
          <span className="font-medium text-gray-700">Supplier:</span>
          <span className="ml-2 text-gray-900">
            {orderData.supplier_type === 'oraseas_ee'
              ? 'Oraseas EE'
              : (suppliers.find(s => s.id === orderData.supplier_organization_id)?.name || orderData.supplier_name)
            }
          </span>
        </div>

        <div>
          <span className="font-medium text-gray-700">Priority:</span>
          <span className={`ml-2 px-2 py-1 text-xs font-medium rounded-full ${orderData.priority === 'urgent' ? 'bg-red-100 text-red-800' :
            orderData.priority === 'high' ? 'bg-orange-100 text-orange-800' :
              orderData.priority === 'medium' ? 'bg-yellow-100 text-yellow-800' :
                'bg-gray-100 text-gray-800'
            }`}>
            {orderData.priority.charAt(0).toUpperCase() + orderData.priority.slice(1)}
          </span>
        </div>

        {orderData.requested_delivery_date && (
          <div>
            <span className="font-medium text-gray-700">Requested Delivery:</span>
            <span className="ml-2 text-gray-900">
              {new Date(orderData.requested_delivery_date).toLocaleDateString()}
            </span>
          </div>
        )}

        {orderData.notes && (
          <div>
            <span className="font-medium text-gray-700">Notes:</span>
            <span className="ml-2 text-gray-900">{orderData.notes}</span>
          </div>
        )}
      </div>

      <div className="space-y-2">
        <h4 className="font-medium text-gray-900">Items ({orderData.items.length})</h4>
        <div className="space-y-2">
          {orderData.items.map((item, index) => (
            <div key={index} className="p-3 bg-white border border-gray-200 rounded-md">
              <div className="font-medium text-gray-900">
                {item.part_name} ({item.part_number})
              </div>
              <div className="text-sm text-gray-500">
                Quantity: {item.quantity} {item.unit_of_measure}
                {item.unit_price && ` • Unit Price: $${item.unit_price} • Total: $${(item.quantity * item.unit_price).toFixed(2)}`}
                {item.notes && ` • ${item.notes}`}
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="bg-blue-50 p-4 rounded-lg">
        <div className="flex items-start">
          <svg className="w-5 h-5 text-blue-600 mt-0.5 mr-2" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
          </svg>
          <div className="text-sm text-blue-800">
            <p className="font-medium">Two-Phase Order Process</p>
            <p className="mt-1">
              This order will be created in "Requested" status. Once approved and ordered from the supplier,
              you'll be able to record the receipt of items when they arrive.
            </p>
          </div>
        </div>
      </div>
    </div>
  );

  const getStepTitle = () => {
    switch (currentStep) {
      case 1: return 'Order Details';
      case 2: return 'Add Items';
      case 3: return 'Review & Submit';
      default: return 'Create Order';
    }
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title={`Two-Phase Order Wizard - ${getStepTitle()}`}
      size="xl"
    >
      <div className="space-y-6">
        {renderStepIndicator()}

        {error && (
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative" role="alert">
            <strong className="font-bold">Error:</strong>
            <span className="block sm:inline ml-2">{error}</span>
          </div>
        )}

        <div className="min-h-[400px]">
          {currentStep === 1 && renderStep1()}
          {currentStep === 2 && renderStep2()}
          {currentStep === 3 && renderStep3()}
        </div>

        <div className="flex justify-between pt-4 border-t border-gray-200">
          <div>
            {currentStep > 1 && (
              <button
                type="button"
                onClick={prevStep}
                className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-200 rounded-md hover:bg-gray-300 focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-offset-2"
                disabled={loading}
              >
                Previous
              </button>
            )}
          </div>

          <div className="flex space-x-3">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-200 rounded-md hover:bg-gray-300 focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-offset-2"
              disabled={loading}
            >
              Cancel
            </button>

            {currentStep < 3 ? (
              <button
                type="button"
                onClick={nextStep}
                className="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
                disabled={loading}
              >
                Next
              </button>
            ) : (
              <button
                type="button"
                onClick={submitOrder}
                className="px-4 py-2 text-sm font-medium text-white bg-green-600 rounded-md hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2"
                disabled={loading}
              >
                {loading ? 'Creating Order...' : 'Create Order'}
              </button>
            )}
          </div>
        </div>
      </div>
    </Modal>
  );
};

export default TwoPhaseOrderWizard;