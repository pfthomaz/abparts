// frontend/src/pages/Orders.js

import React, { useState, useEffect, useCallback, useMemo } from 'react';
import { ordersService } from '../services/ordersService';
import { organizationsService } from '../services/organizationsService';
import { useAuth } from '../AuthContext';
import Modal from '../components/Modal';
import SupplierOrderForm from '../components/SupplierOrderForm';
import CustomerOrderForm from '../components/CustomerOrderForm';
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
  const [showFulfillmentModal, setShowFulfillmentModal] = useState(false);
  const [showOrderHistoryModal, setShowOrderHistoryModal] = useState(false);
  const [showShipOrderModal, setShowShipOrderModal] = useState(false);
  const [showConfirmReceiptModal, setShowConfirmReceiptModal] = useState(false);
  const [selectedOrderForFulfillment, setSelectedOrderForFulfillment] = useState(null);
  const [selectedOrderForShipping, setSelectedOrderForShipping] = useState(null);
  const [selectedOrderForReceipt, setSelectedOrderForReceipt] = useState(null);
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
        organizationsService.getOrganizations({ for_orders: true }), // Fetching data for forms
        api.get('/parts'),         // Fetching data for forms
        api.get('/warehouses'),    // Fetching warehouses for fulfillment
      ]);

      setSupplierOrders(supplierOrdersData);
      setCustomerOrders(customerOrdersData);
      setOrganizations(orgsData);
      // Handle paginated response format for parts
      const partsArray = partsData?.items || partsData || [];
      setParts(Array.isArray(partsArray) ? partsArray : []);
      setWarehouses(warehousesData);
    } catch (err) {
      setError(err.message || 'Failed to fetch order data.');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchData();
  }, []);

  // Auto-refresh every 10 minutes
  useEffect(() => {
    const interval = setInterval(() => {
      fetchData();
    }, 10 * 60 * 1000);

    return () => clearInterval(interval);
  }, []);

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
        // Use the flat customer_organization_name field
        return order.customer_organization_name?.toLowerCase().includes(searchTerm.toLowerCase());
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
      const createdOrder = await ordersService.createSupplierOrder(orderData);

      // Create order items
      for (const item of orderData.items) {
        await ordersService.createSupplierOrderItem({
          supplier_order_id: createdOrder.id,
          part_id: item.part_id,
          quantity: item.quantity,
          unit_price: item.unit_price
        });
      }

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
      const createdOrder = await ordersService.createCustomerOrder(orderData);

      // Create order items
      for (const item of orderData.items) {
        await ordersService.createCustomerOrderItem({
          customer_order_id: createdOrder.id,
          part_id: item.part_id,
          quantity: item.quantity,
          unit_price: item.unit_price
        });
      }

      await fetchData(); // Refresh all data
      setShowCustomerOrderModal(false);
    } catch (err) {
      console.error("Error creating customer order:", err);
      // Re-throw to be caught by the form's error handling
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

  const handleShipOrder = (order) => {
    setSelectedOrderForShipping(order);
    setShowShipOrderModal(true);
  };

  const handleConfirmReceipt = (order) => {
    setSelectedOrderForReceipt(order);
    setShowConfirmReceiptModal(true);
  };

  const handleOrderShipped = async (orderId, shipData) => {
    try {
      await ordersService.shipCustomerOrder(orderId, shipData);
      await fetchData(); // Refresh all data
      setShowShipOrderModal(false);
      setSelectedOrderForShipping(null);
    } catch (err) {
      console.error("Error shipping order:", err);
      throw err;
    }
  };

  const handleReceiptConfirmed = async (orderId, receiptData) => {
    try {
      await ordersService.confirmCustomerOrderReceipt(orderId, receiptData);
      await fetchData(); // Refresh all data
      setShowConfirmReceiptModal(false);
      setSelectedOrderForReceipt(null);
    } catch (err) {
      console.error("Error confirming receipt:", err);
      throw err;
    }
  };

  const canFulfillOrder = (order) => {
    return order.status === 'Requested' || order.status === 'Pending' || order.status === 'Shipped';
  };

  const canApproveOrder = (order) => {
    return user && (user.role === 'admin' || user.role === 'super_admin') &&
      (order.status === 'Requested' || order.status === 'Pending');
  };

  const canShipOrder = (order) => {
    // Oraseas EE users can ship Pending orders
    return user && 
      (user.organization_name?.includes('Oraseas') || user.organization_name?.includes('BossServ')) &&
      (user.role === 'admin' || user.role === 'super_admin') &&
      order.status === 'Pending';
  };

  const canConfirmReceipt = (order) => {
    // Customer users can confirm receipt of Shipped orders
    return user && 
      order.customer_organization_id === user.organization_id &&
      order.status === 'Shipped';
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

          {/* Only show Add Supplier Order for Oraseas EE users and super admins */}
          {(user?.role === 'super_admin' ||
            organizations.find(org => org.id === user?.organization_id)?.organization_type === 'oraseas_ee') && (
              <button
                onClick={() => setShowSupplierOrderModal(true)}
                className="bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 font-semibold"
              >
                Add Supplier Order
              </button>
            )}
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
                              {item.quantity} x {item.part_name} ({item.part_number})
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
                        <h3 className="text-xl font-semibold text-indigo-700">Order for {order.customer_organization_name || 'Unknown'}</h3>
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
                        {order.shipped_date && (
                          <p><span className="font-medium">Shipped:</span> {new Date(order.shipped_date).toLocaleDateString()}</p>
                        )}
                        {order.actual_delivery_date && (
                          <p><span className="font-medium">Received:</span> {new Date(order.actual_delivery_date).toLocaleDateString()}</p>
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
                      {canShipOrder(order) && (
                        <button
                          onClick={() => handleShipOrder(order)}
                          className="text-sm bg-purple-600 hover:bg-purple-700 text-white font-semibold py-1 px-3 rounded-md transition-colors"
                        >
                          Mark as Shipped
                        </button>
                      )}
                      {canConfirmReceipt(order) && (
                        <button
                          onClick={() => handleConfirmReceipt(order)}
                          className="text-sm bg-green-600 hover:bg-green-700 text-white font-semibold py-1 px-3 rounded-md transition-colors"
                        >
                          Confirm Receipt
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
                              {item.quantity} x {item.part_name} ({item.part_number})
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

      <Modal isOpen={showSupplierOrderModal} onClose={() => setShowSupplierOrderModal(false)} title="Add Supplier Order" size="xl">
        <SupplierOrderForm onSubmit={handleCreateSupplierOrder} onClose={() => setShowSupplierOrderModal(false)} organizations={organizations} parts={parts} />
      </Modal>

      <Modal isOpen={showCustomerOrderModal} onClose={() => setShowCustomerOrderModal(false)} title="Add Customer Order" size="xl">
        <CustomerOrderForm onSubmit={handleCreateCustomerOrder} onClose={() => setShowCustomerOrderModal(false)} organizations={organizations} parts={parts} />
      </Modal>



      {/* Order Fulfillment Modal */}
      <Modal
        isOpen={showFulfillmentModal}
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
        isOpen={showOrderHistoryModal}
        onClose={() => setShowOrderHistoryModal(false)}
        title="Order History & Analytics"
      >
        <OrderHistoryView onClose={() => setShowOrderHistoryModal(false)} />
      </Modal>

      {/* Ship Order Modal */}
      <Modal
        isOpen={showShipOrderModal}
        onClose={() => {
          setShowShipOrderModal(false);
          setSelectedOrderForShipping(null);
        }}
        title="Mark Order as Shipped"
      >
        {selectedOrderForShipping && (
          <ShipOrderForm
            order={selectedOrderForShipping}
            onSubmit={handleOrderShipped}
            onClose={() => {
              setShowShipOrderModal(false);
              setSelectedOrderForShipping(null);
            }}
          />
        )}
      </Modal>

      {/* Confirm Receipt Modal */}
      <Modal
        isOpen={showConfirmReceiptModal}
        onClose={() => {
          setShowConfirmReceiptModal(false);
          setSelectedOrderForReceipt(null);
        }}
        title="Confirm Order Receipt"
      >
        {selectedOrderForReceipt && (
          <ConfirmReceiptForm
            order={selectedOrderForReceipt}
            warehouses={warehouses}
            onSubmit={handleReceiptConfirmed}
            onClose={() => {
              setShowConfirmReceiptModal(false);
              setSelectedOrderForReceipt(null);
            }}
          />
        )}
      </Modal>
    </div>
  );
};

// Ship Order Form Component
const ShipOrderForm = ({ order, onSubmit, onClose }) => {
  const [formData, setFormData] = useState({
    shipped_date: new Date().toISOString().split('T')[0],
    tracking_number: '',
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
      await onSubmit(order.id, formData);
    } catch (err) {
      setError(err.message || 'Failed to ship order');
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
          <span className="font-medium">Customer:</span> {order.customer_organization_name}
        </p>
        <p className="text-sm text-gray-600">
          <span className="font-medium">Order Date:</span> {new Date(order.order_date).toLocaleDateString()}
        </p>
        <p className="text-sm text-gray-600">
          <span className="font-medium">Current Status:</span> {order.status}
        </p>
      </div>

      <div>
        <label htmlFor="shipped_date" className="block text-sm font-medium text-gray-700 mb-1">
          Shipped Date
        </label>
        <input
          type="date"
          id="shipped_date"
          name="shipped_date"
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-purple-500 focus:border-purple-500"
          value={formData.shipped_date}
          onChange={handleChange}
          required
          disabled={loading}
        />
      </div>

      <div>
        <label htmlFor="tracking_number" className="block text-sm font-medium text-gray-700 mb-1">
          Tracking Number (Optional)
        </label>
        <input
          type="text"
          id="tracking_number"
          name="tracking_number"
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-purple-500 focus:border-purple-500"
          value={formData.tracking_number}
          onChange={handleChange}
          placeholder="Enter tracking number..."
          disabled={loading}
        />
      </div>

      <div>
        <label htmlFor="notes" className="block text-sm font-medium text-gray-700 mb-1">
          Shipping Notes
        </label>
        <textarea
          id="notes"
          name="notes"
          rows="3"
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-purple-500 focus:border-purple-500"
          value={formData.notes}
          onChange={handleChange}
          placeholder="Any notes about the shipment..."
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
          className="px-4 py-2 text-sm font-medium text-white bg-purple-600 rounded-md hover:bg-purple-700 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:ring-offset-2"
          disabled={loading}
        >
          {loading ? 'Shipping...' : 'Mark as Shipped'}
        </button>
      </div>
    </form>
  );
};

// Confirm Receipt Form Component
const ConfirmReceiptForm = ({ order, warehouses, onSubmit, onClose }) => {
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
      await onSubmit(order.id, formData);
    } catch (err) {
      setError(err.message || 'Failed to confirm receipt');
    } finally {
      setLoading(false);
    }
  };

  // Filter warehouses to only show those belonging to the customer organization
  const customerWarehouses = warehouses.filter(
    w => w.organization_id === order.customer_organization_id
  );

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
          <span className="font-medium">Order from:</span> {order.oraseas_organization_name || 'Oraseas EE'}
        </p>
        <p className="text-sm text-gray-600">
          <span className="font-medium">Order Date:</span> {new Date(order.order_date).toLocaleDateString()}
        </p>
        {order.shipped_date && (
          <p className="text-sm text-gray-600">
            <span className="font-medium">Shipped Date:</span> {new Date(order.shipped_date).toLocaleDateString()}
          </p>
        )}
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
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-green-500 focus:border-green-500"
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
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-green-500 focus:border-green-500"
          value={formData.receiving_warehouse_id}
          onChange={handleChange}
          required
          disabled={loading}
        >
          <option value="">Select Warehouse</option>
          {customerWarehouses.map(warehouse => (
            <option key={warehouse.id} value={warehouse.id}>
              {warehouse.name}
            </option>
          ))}
        </select>
        {customerWarehouses.length === 0 && (
          <p className="text-sm text-red-600 mt-1">No warehouses found for your organization</p>
        )}
      </div>

      <div>
        <label htmlFor="notes" className="block text-sm font-medium text-gray-700 mb-1">
          Receipt Notes
        </label>
        <textarea
          id="notes"
          name="notes"
          rows="3"
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-green-500 focus:border-green-500"
          value={formData.notes}
          onChange={handleChange}
          placeholder="Any notes about the delivery..."
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
          {loading ? 'Confirming...' : 'Confirm Receipt'}
        </button>
      </div>
    </form>
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
