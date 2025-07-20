// frontend/src/pages/Orders.js

import React, { useState, useEffect, useCallback, useMemo } from 'react';
import { ordersService } from '../services/ordersService';
import { useAuth } from '../AuthContext';
import Modal from '../components/Modal';
import SupplierOrderForm from '../components/SupplierOrderForm';
import CustomerOrderForm from '../components/CustomerOrderForm';
import EnhancedPartOrderForm from '../components/EnhancedPartOrderForm';
import OrderHistoryView from '../components/OrderHistoryView';

// A helper service to fetch data needed by forms, could be in its own file.
import { api } from '../services/api';

const Orders = () => {
  const { user } = useAuth();
  const [supplierOrders, setSupplierOrders] = useState([]);
  const [customerOrders, setCustomerOrders] = useState([]);
  const [organizations, setOrganizations] = useState([]);
  const [parts, setParts] = useState([]);
  const [warehouses, setWarehouses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showSupplierOrderModal, setShowSupplierOrderModal] = useState(false);
  const [showCustomerOrderModal, setShowCustomerOrderModal] = useState(false);
  const [showEnhancedOrderModal, setShowEnhancedOrderModal] = useState(false);
  const [showFulfillmentModal, setShowFulfillmentModal] = useState(false);
  const [showOrderHistoryModal, setShowOrderHistoryModal] = useState(false);
  const [selectedOrderForFulfillment, setSelectedOrderForFulfillment] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterStatus, setFilterStatus] = useState('all');
  const [filterOrderType, setFilterOrderType] = useState('all');
  const [expandedOrderId, setExpandedOrderId] = useState(null);
  const [showAnalytics, setShowAnalytics] = useState(false);

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
        warehousesData,
      ] = await Promise.all([
        ordersService.getSupplierOrders(),
        ordersService.getCustomerOrders(),
        api.get('/organizations'), // Fetching data for forms
        api.get('/parts'),         // Fetching data for forms
        api.get('/warehouses'),    // Fetching warehouses for fulfillment
      ]);

      setSupplierOrders(supplierOrdersData);
      setCustomerOrders(customerOrdersData);
      setOrganizations(orgsData);
      setParts(partsData);
      setWarehouses(warehousesData);
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
    ((filterOrderType === 'all' && filteredSupplierOrders.length === 0 && filteredCustomerOrders.length === 0) ||
      (filterOrderType === 'supplier' && filteredSupplierOrders.length === 0) ||
      (filterOrderType === 'customer' && filteredCustomerOrders.length === 0));

  // Order analytics calculations
  const orderAnalytics = useMemo(() => {
    const allOrders = [...supplierOrders, ...customerOrders];
    const totalOrders = allOrders.length;
    const pendingOrders = allOrders.filter(order => order.status === 'Requested' || order.status === 'Pending').length;
    const completedOrders = allOrders.filter(order => order.status === 'Received' || order.status === 'Delivered').length;
    const overdueOrders = allOrders.filter(order => {
      if (!order.expected_delivery_date) return false;
      const expectedDate = new Date(order.expected_delivery_date);
      const today = new Date();
      return expectedDate < today && (order.status === 'Requested' || order.status === 'Pending' || order.status === 'Shipped');
    }).length;

    return {
      totalOrders,
      pendingOrders,
      completedOrders,
      overdueOrders,
      completionRate: totalOrders > 0 ? ((completedOrders / totalOrders) * 100).toFixed(1) : 0
    };
  }, [supplierOrders, customerOrders]);

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

  const handleCreateEnhancedOrder = async (orderData) => {
    try {
      // Determine order type based on supplier selection
      if (orderData.supplier_type === 'oraseas_ee') {
        // Create customer order (ordering from Oraseas EE)
        const customerOrderData = {
          customer_organization_id: orderData.customer_organization_id,
          oraseas_organization_id: orderData.supplier_organization_id,
          order_date: orderData.order_date,
          expected_delivery_date: orderData.expected_delivery_date,
          status: orderData.status,
          ordered_by_user_id: user.id,
          notes: orderData.notes
        };

        const createdOrder = await ordersService.createCustomerOrder(customerOrderData);

        // Create order items
        for (const item of orderData.items) {
          await ordersService.createCustomerOrderItem({
            customer_order_id: createdOrder.id,
            part_id: item.part_id,
            quantity: item.quantity,
            unit_price: item.unit_price
          });
        }
      } else {
        // Create supplier order (ordering from own suppliers)
        const supplierOrderData = {
          ordering_organization_id: orderData.customer_organization_id,
          supplier_name: organizations.find(org => org.id === orderData.supplier_organization_id)?.name || 'Unknown',
          order_date: orderData.order_date,
          expected_delivery_date: orderData.expected_delivery_date,
          status: orderData.status,
          notes: orderData.notes
        };

        const createdOrder = await ordersService.createSupplierOrder(supplierOrderData);

        // Create order items
        for (const item of orderData.items) {
          await ordersService.createSupplierOrderItem({
            supplier_order_id: createdOrder.id,
            part_id: item.part_id,
            quantity: item.quantity,
            unit_price: item.unit_price
          });
        }
      }

      await fetchData(); // Refresh all data
      setShowEnhancedOrderModal(false);
    } catch (err) {
      console.error("Error creating enhanced order:", err);
      throw err;
    }
  };

  const handleOrderStatusUpdate = async (orderId, orderType, newStatus, fulfillmentData = null) => {
    try {
      const updateData = { status: newStatus };

      if (fulfillmentData) {
        updateData.actual_delivery_date = fulfillmentData.actual_delivery_date;
        updateData.receiving_warehouse_id = fulfillmentData.receiving_warehouse_id;
        updateData.notes = fulfillmentData.notes;
      }

      if (orderType === 'supplier') {
        await ordersService.updateSupplierOrder(orderId, updateData);
      } else {
        await ordersService.updateCustomerOrder(orderId, updateData);
      }

      await fetchData(); // Refresh all data
      setShowFulfillmentModal(false);
      setSelectedOrderForFulfillment(null);
    } catch (err) {
      console.error("Error updating order status:", err);
      throw err;
    }
  };

  const handleFulfillOrder = (order, orderType) => {
    setSelectedOrderForFulfillment({ ...order, orderType });
    setShowFulfillmentModal(true);
  };

  const canFulfillOrder = (order) => {
    return order.status === 'Requested' || order.status === 'Pending' || order.status === 'Shipped';
  };

  const canApproveOrder = (order) => {
    return user && (user.role === 'admin' || user.role === 'super_admin') &&
      (order.status === 'Requested' || order.status === 'Pending');
  };

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-3xl font-bold text-gray-800">Orders</h1>
          <p className="text-gray-600 mt-1">Manage part orders and fulfillment workflow</p>
        </div>
        <div className="flex space-x-2">
          <button
            onClick={() => setShowAnalytics(!showAnalytics)}
            className="bg-purple-600 text-white py-2 px-4 rounded-md hover:bg-purple-700 font-semibold"
          >
            {showAnalytics ? 'Hide Analytics' : 'Show Analytics'}
          </button>
          <button
            onClick={() => setShowOrderHistoryModal(true)}
            className="bg-gray-600 text-white py-2 px-4 rounded-md hover:bg-gray-700 font-semibold"
          >
            Order History
          </button>
          <button
            onClick={() => setShowEnhancedOrderModal(true)}
            className="bg-indigo-600 text-white py-2 px-4 rounded-md hover:bg-indigo-700 font-semibold"
          >
            Create Part Order
          </button>
          <button
            onClick={() => setShowSupplierOrderModal(true)}
            className="bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 font-semibold"
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

      {/* Order Analytics Dashboard */}
      {showAnalytics && (
        <div className="bg-white p-6 rounded-lg shadow-md mb-6">
          <h2 className="text-xl font-bold text-gray-800 mb-4">Order Analytics</h2>
          <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
            <div className="bg-blue-50 p-4 rounded-lg">
              <h3 className="text-sm font-medium text-blue-600">Total Orders</h3>
              <p className="text-2xl font-bold text-blue-800">{orderAnalytics.totalOrders}</p>
            </div>
            <div className="bg-yellow-50 p-4 rounded-lg">
              <h3 className="text-sm font-medium text-yellow-600">Pending Orders</h3>
              <p className="text-2xl font-bold text-yellow-800">{orderAnalytics.pendingOrders}</p>
            </div>
            <div className="bg-green-50 p-4 rounded-lg">
              <h3 className="text-sm font-medium text-green-600">Completed Orders</h3>
              <p className="text-2xl font-bold text-green-800">{orderAnalytics.completedOrders}</p>
            </div>
            <div className="bg-red-50 p-4 rounded-lg">
              <h3 className="text-sm font-medium text-red-600">Overdue Orders</h3>
              <p className="text-2xl font-bold text-red-800">{orderAnalytics.overdueOrders}</p>
            </div>
            <div className="bg-indigo-50 p-4 rounded-lg">
              <h3 className="text-sm font-medium text-indigo-600">Completion Rate</h3>
              <p className="text-2xl font-bold text-indigo-800">{orderAnalytics.completionRate}%</p>
            </div>
          </div>
        </div>
      )}

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
              <option value="Requested">Requested</option>
              <option value="Pending">Pending</option>
              <option value="Shipped">Shipped</option>
              <option value="Received">Received</option>
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
                    <div className="flex-1">
                      <div className="flex items-center justify-between mb-2">
                        <h3 className="text-xl font-semibold text-red-700">Order from {order.supplier_name}</h3>
                        <div className="flex items-center space-x-2">
                          <span className={`px-2 py-1 text-xs font-semibold rounded-full ${order.status === 'Requested' ? 'bg-yellow-100 text-yellow-800' :
                            order.status === 'Pending' ? 'bg-blue-100 text-blue-800' :
                              order.status === 'Shipped' ? 'bg-purple-100 text-purple-800' :
                                order.status === 'Received' ? 'bg-green-100 text-green-800' :
                                  order.status === 'Delivered' ? 'bg-green-100 text-green-800' :
                                    'bg-red-100 text-red-800'
                            }`}>
                            {order.status}
                          </span>
                        </div>
                      </div>
                      <div className="grid grid-cols-2 gap-4 text-sm text-gray-600">
                        <p><span className="font-medium">Order Date:</span> {new Date(order.order_date).toLocaleDateString()}</p>
                        {order.expected_delivery_date && (
                          <p><span className="font-medium">Expected:</span> {new Date(order.expected_delivery_date).toLocaleDateString()}</p>
                        )}
                        {order.actual_delivery_date && (
                          <p><span className="font-medium">Delivered:</span> {new Date(order.actual_delivery_date).toLocaleDateString()}</p>
                        )}
                      </div>
                    </div>
                    <div className="flex space-x-2 ml-4">
                      {canFulfillOrder(order) && (
                        <button
                          onClick={() => handleFulfillOrder(order, 'supplier')}
                          className="text-sm bg-green-600 hover:bg-green-700 text-white font-semibold py-1 px-3 rounded-md transition-colors"
                        >
                          Fulfill Order
                        </button>
                      )}
                      <button
                        onClick={() => toggleOrderItems(order.id)}
                        className="text-sm bg-gray-200 hover:bg-gray-300 text-gray-800 font-semibold py-1 px-3 rounded-md transition-colors"
                      >
                        {expandedOrderId === order.id ? 'Hide Items' : 'View Items'}
                      </button>
                    </div>
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
                    <div className="flex-1">
                      <div className="flex items-center justify-between mb-2">
                        <h3 className="text-xl font-semibold text-indigo-700">Order for {order.customer_organization?.name || 'Unknown'}</h3>
                        <div className="flex items-center space-x-2">
                          <span className={`px-2 py-1 text-xs font-semibold rounded-full ${order.status === 'Requested' ? 'bg-yellow-100 text-yellow-800' :
                            order.status === 'Pending' ? 'bg-blue-100 text-blue-800' :
                              order.status === 'Shipped' ? 'bg-purple-100 text-purple-800' :
                                order.status === 'Received' ? 'bg-green-100 text-green-800' :
                                  order.status === 'Delivered' ? 'bg-green-100 text-green-800' :
                                    'bg-red-100 text-red-800'
                            }`}>
                            {order.status}
                          </span>
                        </div>
                      </div>
                      <div className="grid grid-cols-2 gap-4 text-sm text-gray-600">
                        <p><span className="font-medium">Order Date:</span> {new Date(order.order_date).toLocaleDateString()}</p>
                        {order.expected_delivery_date && (
                          <p><span className="font-medium">Expected:</span> {new Date(order.expected_delivery_date).toLocaleDateString()}</p>
                        )}
                        {order.actual_delivery_date && (
                          <p><span className="font-medium">Delivered:</span> {new Date(order.actual_delivery_date).toLocaleDateString()}</p>
                        )}
                        {order.ordered_by_user_id && (
                          <p><span className="font-medium">Ordered by:</span> User ID {order.ordered_by_user_id}</p>
                        )}
                      </div>
                    </div>
                    <div className="flex space-x-2 ml-4">
                      {canApproveOrder(order) && (
                        <button
                          onClick={() => handleOrderStatusUpdate(order.id, 'customer', 'Pending')}
                          className="text-sm bg-blue-600 hover:bg-blue-700 text-white font-semibold py-1 px-3 rounded-md transition-colors"
                        >
                          Approve
                        </button>
                      )}
                      {canFulfillOrder(order) && (
                        <button
                          onClick={() => handleFulfillOrder(order, 'customer')}
                          className="text-sm bg-green-600 hover:bg-green-700 text-white font-semibold py-1 px-3 rounded-md transition-colors"
                        >
                          Fulfill Order
                        </button>
                      )}
                      <button
                        onClick={() => toggleOrderItems(order.id)}
                        className="text-sm bg-gray-200 hover:bg-gray-300 text-gray-800 font-semibold py-1 px-3 rounded-md transition-colors"
                      >
                        {expandedOrderId === order.id ? 'Hide Items' : 'View Items'}
                      </button>
                    </div>
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

      <Modal show={showEnhancedOrderModal} onClose={() => setShowEnhancedOrderModal(false)} title="Create Part Order">
        <EnhancedPartOrderForm
          onSubmit={handleCreateEnhancedOrder}
          onClose={() => setShowEnhancedOrderModal(false)}
          organizations={organizations}
          parts={parts}
          warehouses={warehouses}
        />
      </Modal>

      {/* Order Fulfillment Modal */}
      <Modal
        show={showFulfillmentModal}
        onClose={() => {
          setShowFulfillmentModal(false);
          setSelectedOrderForFulfillment(null);
        }}
        title="Fulfill Order"
      >
        {selectedOrderForFulfillment && (
          <OrderFulfillmentForm
            order={selectedOrderForFulfillment}
            warehouses={warehouses}
            onSubmit={handleOrderStatusUpdate}
            onClose={() => {
              setShowFulfillmentModal(false);
              setSelectedOrderForFulfillment(null);
            }}
          />
        )}
      </Modal>

      {/* Order History Modal */}
      <Modal
        show={showOrderHistoryModal}
        onClose={() => setShowOrderHistoryModal(false)}
        title="Order History & Analytics"
      >
        <OrderHistoryView onClose={() => setShowOrderHistoryModal(false)} />
      </Modal>
    </div>
  );
};

// Order Fulfillment Form Component
const OrderFulfillmentForm = ({ order, warehouses, onSubmit, onClose }) => {
  const [formData, setFormData] = useState({
    actual_delivery_date: new Date().toISOString().split('T')[0],
    receiving_warehouse_id: '',
    notes: ''
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

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
      await onSubmit(order.id, order.orderType, 'Received', formData);
    } catch (err) {
      setError(err.message || 'Failed to fulfill order');
    } finally {
      setLoading(false);
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

      <div className="bg-gray-50 p-4 rounded-lg">
        <h3 className="font-semibold text-gray-800 mb-2">Order Details</h3>
        <p className="text-sm text-gray-600">
          <span className="font-medium">Order from:</span> {order.supplier_name || order.customer_organization?.name}
        </p>
        <p className="text-sm text-gray-600">
          <span className="font-medium">Order Date:</span> {new Date(order.order_date).toLocaleDateString()}
        </p>
        <p className="text-sm text-gray-600">
          <span className="font-medium">Current Status:</span> {order.status}
        </p>
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
          value={formData.actual_delivery_date}
          onChange={handleChange}
          required
          disabled={loading}
        />
      </div>

      <div>
        <label htmlFor="receiving_warehouse_id" className="block text-sm font-medium text-gray-700 mb-1">
          Receiving Warehouse
        </label>
        <select
          id="receiving_warehouse_id"
          name="receiving_warehouse_id"
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
          value={formData.receiving_warehouse_id}
          onChange={handleChange}
          required
          disabled={loading}
        >
          <option value="">Select Warehouse</option>
          {warehouses.map(warehouse => (
            <option key={warehouse.id} value={warehouse.id}>
              {warehouse.name} - {warehouse.organization?.name}
            </option>
          ))}
        </select>
      </div>

      <div>
        <label htmlFor="notes" className="block text-sm font-medium text-gray-700 mb-1">
          Fulfillment Notes
        </label>
        <textarea
          id="notes"
          name="notes"
          rows="3"
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
          value={formData.notes}
          onChange={handleChange}
          placeholder="Any notes about the fulfillment..."
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
          className="px-4 py-2 text-sm font-medium text-white bg-green-600 rounded-md hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2"
          disabled={loading}
        >
          {loading ? 'Fulfilling...' : 'Mark as Received'}
        </button>
      </div>
    </form>
  );
};

export default Orders;
