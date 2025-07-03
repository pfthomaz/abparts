// frontend/src/pages/Orders.js

import React, { useState, useEffect, useCallback } from 'react';
import { useAuth } from '../AuthContext';
import Modal from '../components/Modal';
import SupplierOrderForm from '../components/SupplierOrderForm';
import CustomerOrderForm from '../components/CustomerOrderForm';

const Orders = () => {
  const { token } = useAuth();
  const [supplierOrders, setSupplierOrders] = useState([]);
  const [customerOrders, setCustomerOrders] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [showSupplierOrderModal, setShowSupplierOrderModal] = useState(false);
  const [showCustomerOrderModal, setShowCustomerOrderModal] = useState(false);

  const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000';

  const fetchOrders = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const [supplierOrdersRes, customerOrdersRes] = await Promise.all([
        fetch(`${API_BASE_URL}/supplier_orders`, { headers: { 'Authorization': `Bearer ${token}` } }),
        fetch(`${API_BASE_URL}/customer_orders`, { headers: { 'Authorization': `Bearer ${token}` } }),
      ]);

      if (!supplierOrdersRes.ok) {
        throw new Error(`Failed to fetch supplier orders: ${supplierOrdersRes.status}`);
      }
      if (!customerOrdersRes.ok) {
        throw new Error(`Failed to fetch customer orders: ${customerOrdersRes.status}`);
      }

      const supplierOrdersData = await supplierOrdersRes.json();
      const customerOrdersData = await customerOrdersRes.json();

      setSupplierOrders(supplierOrdersData);
      setCustomerOrders(customerOrdersData);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, [token, API_BASE_URL]);

  useEffect(() => {
    fetchOrders();
  }, [fetchOrders]);

  const handleCreateSupplierOrder = async (orderData) => {
    try {
      const response = await fetch(`${API_BASE_URL}/supplier_orders`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify(orderData),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
      }

      await fetchOrders();
      setShowSupplierOrderModal(false);
    } catch (err) {
      console.error("Error creating supplier order:", err);
      throw err;
    }
  };

  const handleCreateCustomerOrder = async (orderData) => {
    try {
      const response = await fetch(`${API_BASE_URL}/customer_orders`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify(orderData),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
      }

      await fetchOrders();
      setShowCustomerOrderModal(false);
    } catch (err) {
      console.error("Error creating customer order:", err);
      throw err;
    }
  };

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold text-gray-800">Orders</h1>
        <div>
          <button
            onClick={() => setShowSupplierOrderModal(true)}
            className="bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 mr-2"
          >
            Add Supplier Order
          </button>
          <button
            onClick={() => setShowCustomerOrderModal(true)}
            className="bg-green-600 text-white py-2 px-4 rounded-md hover:bg-green-700"
          >
            Add Customer Order
          </button>
        </div>
      </div>

      {loading && <p>Loading...</p>}
      {error && <p className="text-red-500">{error}</p>}

      <div>
        <h2 className="text-2xl font-bold text-gray-700 mt-8 mb-4">Supplier Orders</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-12">
          {supplierOrders.map((order) => (
            <div key={order.id} className="bg-gray-50 p-6 rounded-lg shadow-md border border-gray-200">
              <h3 className="text-xl font-semibold text-red-700 mb-2">Order from {order.supplier_name}</h3>
              <p className="text-gray-600 mb-1"><span className="font-medium">Order Date:</span> {new Date(order.order_date).toLocaleDateString()}</p>
              <p className="text-gray-600 mb-1"><span className="font-medium">Status:</span> {order.status}</p>
            </div>
          ))}
        </div>
      </div>

      <div>
        <h2 className="text-2xl font-bold text-gray-700 mt-8 mb-4">Customer Orders</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-12">
          {customerOrders.map((order) => (
            <div key={order.id} className="bg-gray-50 p-6 rounded-lg shadow-md border border-gray-200">
              <h3 className="text-xl font-semibold text-indigo-700 mb-2">Order for {order.customer_organization?.name || 'Unknown'}</h3>
              <p className="text-gray-600 mb-1"><span className="font-medium">Order Date:</span> {new Date(order.order_date).toLocaleDateString()}</p>
              <p className="text-gray-600 mb-1"><span className="font-medium">Status:</span> {order.status}</p>
            </div>
          ))}
        </div>
      </div>

      <Modal show={showSupplierOrderModal} onClose={() => setShowSupplierOrderModal(false)} title="Add Supplier Order">
        <SupplierOrderForm onSubmit={handleCreateSupplierOrder} onClose={() => setShowSupplierOrderModal(false)} />
      </Modal>

      <Modal show={showCustomerOrderModal} onClose={() => setShowCustomerOrderModal(false)} title="Add Customer Order">
        <CustomerOrderForm onSubmit={handleCreateCustomerOrder} onClose={() => setShowCustomerOrderModal(false)} />
      </Modal>
    </div>
  );
};

export default Orders;
