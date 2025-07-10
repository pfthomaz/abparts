// frontend/src/pages/Orders.js

import React, { useState, useEffect, useCallback, useMemo } from 'react';
import { ordersService } from '../services/ordersService';
import Modal from '../components/Modal';
import SupplierOrderForm from '../components/SupplierOrderForm';
import CustomerOrderForm from '../components/CustomerOrderForm';

// A helper service to fetch data needed by forms, could be in its own file.
import { api } from '../services/api';

const Orders = () => {
  const [supplierOrders, setSupplierOrders] = useState([]);
  const [customerOrders, setCustomerOrders] = useState([]);
  const [organizations, setOrganizations] = useState([]);
  const [parts, setParts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showSupplierOrderModal, setShowSupplierOrderModal] = useState(false);
  const [showCustomerOrderModal, setShowCustomerOrderModal] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterStatus, setFilterStatus] = useState('all');
  const [filterOrderType, setFilterOrderType] = useState('all');
  const [expandedOrderId, setExpandedOrderId] = useState(null);

  const fetchData = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      // Fetch all data in parallel for efficiency
      const [
        supplierOrdersData,
        customerOrdersData,
        orgsData,
        partsData,
      ] = await Promise.all([
        ordersService.getSupplierOrders(),
        ordersService.getCustomerOrders(),
        api.get('/organizations'), // Fetching data for forms
        api.get('/parts'),         // Fetching data for forms
      ]);

      setSupplierOrders(supplierOrdersData);
      setCustomerOrders(customerOrdersData);
      setOrganizations(orgsData);
      setParts(partsData);
    } catch (err) {
      setError(err.message || 'Failed to fetch order data.');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const filteredSupplierOrders = useMemo(() => {
    return supplierOrders
      .filter(order => filterStatus === 'all' || order.status === filterStatus)
      .filter(order => {
        if (!searchTerm) return true;
        return order.supplier_name.toLowerCase().includes(searchTerm.toLowerCase());
      });
  }, [supplierOrders, searchTerm, filterStatus]);

  const filteredCustomerOrders = useMemo(() => {
    return customerOrders
      .filter(order => filterStatus === 'all' || order.status === filterStatus)
      .filter(order => {
        if (!searchTerm) return true;
        // The customer_organization can be null, so we need to check for its existence.
        return order.customer_organization?.name.toLowerCase().includes(searchTerm.toLowerCase());
      });
  }, [customerOrders, searchTerm, filterStatus]);

  const noResultsMatch =
    !loading &&
    (filterOrderType === 'all' && filteredSupplierOrders.length === 0 && filteredCustomerOrders.length === 0) ||
    (filterOrderType === 'supplier' && filteredSupplierOrders.length === 0) ||
    (filterOrderType === 'customer' && filteredCustomerOrders.length === 0);

  const toggleOrderItems = (orderId) => {
    setExpandedOrderId(prevId => (prevId === orderId ? null : orderId));
  };

  const handleCreateSupplierOrder = async (orderData) => {
    try {
      await ordersService.createSupplierOrder(orderData);
      await fetchData(); // Refresh all data
      setShowSupplierOrderModal(false);
    } catch (err) {
      console.error("Error creating supplier order:", err);
      // Re-throw to be caught by the form's error handling
      throw err;
    }
  };

  const handleCreateCustomerOrder = async (orderData) => {
    try {
      await ordersService.createCustomerOrder(orderData);
      await fetchData(); // Refresh all data
      setShowCustomerOrderModal(false);
    } catch (err) {
      console.error("Error creating customer order:", err);
      // Re-throw to be caught by the form's error handling
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
            className="bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 mr-2 font-semibold"
          >
            Add Supplier Order
          </button>
          <button
            onClick={() => setShowCustomerOrderModal(true)}
            className="bg-green-600 text-white py-2 px-4 rounded-md hover:bg-green-700 font-semibold"
          >
            Add Customer Order
          </button>
        </div>
      </div>

      {loading && <p className="text-gray-500">Loading orders...</p>}
      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative mb-4" role="alert">
          <strong className="font-bold">Error: </strong>
          <span className="block sm:inline">{error}</span>
        </div>
      )}

      {/* Search and Filter Bar */}
      <div className="bg-white p-4 rounded-lg shadow-md mb-6">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label htmlFor="search" className="block text-sm font-medium text-gray-700">Search by Name</label>
            <input
              type="text"
              id="search"
              placeholder="Supplier or Customer name..."
              className="mt-1 w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </div>
          <div>
            <label htmlFor="filterStatus" className="block text-sm font-medium text-gray-700">Filter by Status</label>
            <select
              id="filterStatus"
              className="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm rounded-md"
              value={filterStatus}
              onChange={(e) => setFilterStatus(e.target.value)}
            >
              <option value="all">All Statuses</option>
              <option value="Pending">Pending</option>
              <option value="Shipped">Shipped</option>
              <option value="Delivered">Delivered</option>
              <option value="Cancelled">Cancelled</option>
            </select>
          </div>
          <div>
            <label htmlFor="filterOrderType" className="block text-sm font-medium text-gray-700">Filter by Order Type</label>
            <select
              id="filterOrderType"
              className="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm rounded-md"
              value={filterOrderType}
              onChange={(e) => setFilterOrderType(e.target.value)}
            >
              <option value="all">All Orders</option>
              <option value="supplier">Supplier Orders</option>
              <option value="customer">Customer Orders</option>
            </select>
          </div>
        </div>
      </div>

      {(filterOrderType === 'all' || filterOrderType === 'supplier') && (
        <div>
          <h2 className="text-2xl font-bold text-gray-700 mt-8 mb-4">Supplier Orders</h2>
          {filteredSupplierOrders.length > 0 ? (
            <div className="flex flex-col space-y-4 mb-12">
              {filteredSupplierOrders.map((order) => (
                <div key={order.id} className="bg-white p-4 rounded-lg shadow-md border border-gray-200 transition-shadow duration-200 hover:shadow-lg">
                  <div className="flex justify-between items-start">
                    <div>
                      <h3 className="text-xl font-semibold text-red-700 mb-2">Order from {order.supplier_name}</h3>
                      <p className="text-gray-600 mb-1 text-sm"><span className="font-medium">Order Date:</span> {new Date(order.order_date).toLocaleDateString()}</p>
                      <p className="text-gray-600 mb-1 text-sm"><span className="font-medium">Status:</span> <span className="font-bold">{order.status}</span></p>
                    </div>
                    <button onClick={() => toggleOrderItems(order.id)} className="text-sm bg-gray-200 hover:bg-gray-300 text-gray-800 font-semibold py-1 px-3 rounded-md transition-colors">
                      {expandedOrderId === order.id ? 'Hide Items' : 'View Items'}
                    </button>
                  </div>
                  {expandedOrderId === order.id && (
                    <div className="mt-4 border-t pt-4">
                      <h4 className="font-semibold text-gray-800 mb-2">Order Items</h4>
                      {order.items && order.items.length > 0 ? (
                        <ul className="list-disc list-inside space-y-1 text-gray-600 pl-2">
                          {order.items.map(item => (
                            <li key={item.id}>
                              {item.quantity} x {item.part.name} ({item.part.part_number})
                            </li>
                          ))}
                        </ul>
                      ) : (
                        <p className="text-gray-500">No items in this order.</p>
                      )}
                    </div>
                  )}
                </div>
              ))}
            </div>
          ) : (
            !loading && supplierOrders.length > 0 && <p className="text-gray-500">No supplier orders match your criteria.</p>
          )}
        </div>
      )}

      {(filterOrderType === 'all' || filterOrderType === 'customer') && (
        <div>
          <h2 className="text-2xl font-bold text-gray-700 mt-8 mb-4">Customer Orders</h2>
          {filteredCustomerOrders.length > 0 ? (
            <div className="flex flex-col space-y-4 mb-12">
              {filteredCustomerOrders.map((order) => (
                <div key={order.id} className="bg-white p-4 rounded-lg shadow-md border border-gray-200 transition-shadow duration-200 hover:shadow-lg">
                  <div className="flex justify-between items-start">
                    <div>
                      <h3 className="text-xl font-semibold text-indigo-700 mb-2">Order for {order.customer_organization?.name || 'Unknown'}</h3>
                      <p className="text-gray-600 mb-1 text-sm"><span className="font-medium">Order Date:</span> {new Date(order.order_date).toLocaleDateString()}</p>
                      <p className="text-gray-600 mb-1 text-sm"><span className="font-medium">Status:</span> <span className="font-bold">{order.status}</span></p>
                    </div>
                    <button onClick={() => toggleOrderItems(order.id)} className="text-sm bg-gray-200 hover:bg-gray-300 text-gray-800 font-semibold py-1 px-3 rounded-md transition-colors">
                      {expandedOrderId === order.id ? 'Hide Items' : 'View Items'}
                    </button>
                  </div>
                  {expandedOrderId === order.id && (
                    <div className="mt-4 border-t pt-4">
                      <h4 className="font-semibold text-gray-800 mb-2">Order Items</h4>
                      {order.items && order.items.length > 0 ? (
                        <ul className="list-disc list-inside space-y-1 text-gray-600 pl-2">
                          {order.items.map(item => (
                            <li key={item.id}>
                              {item.quantity} x {item.part.name} ({item.part.part_number})
                            </li>
                          ))}
                        </ul>
                      ) : (
                        <p className="text-gray-500">No items in this order.</p>
                      )}
                    </div>
                  )}
                </div>
              ))}
            </div>
          ) : (
            !loading && customerOrders.length > 0 && <p className="text-gray-500">No customer orders match your criteria.</p>
          )}
        </div>
      )}

      {noResultsMatch && (
        <div className="text-center py-10 bg-white rounded-lg shadow-md">
          <h3 className="text-xl font-semibold text-gray-700">No Orders Found</h3>
          <p className="text-gray-500 mt-2">
            {supplierOrders.length > 0 || customerOrders.length > 0 ? 'Try adjusting your search or filter criteria.' : 'There are no orders in the system yet.'}
          </p>
        </div>
      )}

      <Modal show={showSupplierOrderModal} onClose={() => setShowSupplierOrderModal(false)} title="Add Supplier Order">
        <SupplierOrderForm onSubmit={handleCreateSupplierOrder} onClose={() => setShowSupplierOrderModal(false)} organizations={organizations} parts={parts} />
      </Modal>

      <Modal show={showCustomerOrderModal} onClose={() => setShowCustomerOrderModal(false)} title="Add Customer Order">
        <CustomerOrderForm onSubmit={handleCreateCustomerOrder} onClose={() => setShowCustomerOrderModal(false)} organizations={organizations} parts={parts} />
      </Modal>
    </div>
  );
};

export default Orders;
