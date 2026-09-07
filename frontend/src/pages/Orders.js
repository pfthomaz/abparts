// frontend/src/pages/Orders.js

import React, { useState, useEffect, useCallback, useMemo } from 'react';
import { ordersService } from '../services/ordersService';
import { organizationsService } from '../services/organizationsService';
import { inventoryService } from '../services/inventoryService';
import { useAuth } from '../AuthContext';
import { useTranslation } from '../hooks/useTranslation';
import Modal from '../components/Modal';
import SupplierOrderForm from '../components/SupplierOrderForm';
import CustomerOrderForm from '../components/CustomerOrderForm';
import OrderHistoryView from '../components/OrderHistoryView';
import OrderCalendarView from '../components/OrderCalendarView';

// A helper service to fetch data needed by forms, could be in its own file.
import { api } from '../services/api';

const Orders = () => {
  const { t } = useTranslation();
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
  const [showOrderHistoryModal, setShowOrderHistoryModal] = useState(false);
  const [showShipOrderModal, setShowShipOrderModal] = useState(false);
  const [showConfirmReceiptModal, setShowConfirmReceiptModal] = useState(false);
  const [showWriteOffModal, setShowWriteOffModal] = useState(false);
  const [showSupplierReceiveModal, setShowSupplierReceiveModal] = useState(false);
  const [showSupplierWriteOffModal, setShowSupplierWriteOffModal] = useState(false);
  const [selectedOrderForShipping, setSelectedOrderForShipping] = useState(null);
  const [selectedOrderForReceipt, setSelectedOrderForReceipt] = useState(null);
  const [selectedOrderForWriteOff, setSelectedOrderForWriteOff] = useState(null);
  const [selectedSupplierOrderForReceive, setSelectedSupplierOrderForReceive] = useState(null);
  const [selectedSupplierOrderForWriteOff, setSelectedSupplierOrderForWriteOff] = useState(null);
  const [editingOrder, setEditingOrder] = useState(null);
  const [editOrderType, setEditOrderType] = useState(null);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [orderToDelete, setOrderToDelete] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterStatus, setFilterStatus] = useState('all');
  const [filterOrderType, setFilterOrderType] = useState('all');
  const [expandedOrderId, setExpandedOrderId] = useState(null);
  const [showAnalytics, setShowAnalytics] = useState(false);
  const [activeView, setActiveView] = useState('list'); // 'list' or 'calendar'
  const [stockAvailability, setStockAvailability] = useState(null);
  const [showStockWarningModal, setShowStockWarningModal] = useState(false);
  const [selectedOrderMissingParts, setSelectedOrderMissingParts] = useState(null);

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
        api.get('/parts/'),         // Fetching data for forms
        api.get('/warehouses/'),    // Fetching warehouses for fulfillment
      ]);
      // console.log('orders... :', ordersService.getCustomerOrders());
      setSupplierOrders(supplierOrdersData);
      setCustomerOrders(customerOrdersData);
      setOrganizations(orgsData);
      // Handle paginated response format for parts
      const partsArray = partsData?.items || partsData || [];
      setParts(Array.isArray(partsArray) ? partsArray : []);
      setWarehouses(warehousesData);

      // Fetch stock availability (non-critical, silently handle errors)
      try {
        const stockData = await ordersService.checkStockAvailability();
        setStockAvailability(stockData);
      } catch (stockErr) {
        // Silently ignore - user may not have permission (non-Oraseas users)
        console.debug('Stock availability check skipped:', stockErr.message);
      }
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

  // Build a lookup: order_id -> items_short from stock availability check
  const unfulfillableOrderMap = useMemo(() => {
    if (!stockAvailability || !stockAvailability.orders) return {};
    const map = {};
    for (const order of stockAvailability.orders) {
      map[order.order_id] = order.items_short;
    }
    return map;
  }, [stockAvailability]);

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
        // console.log('All customer1 orders:', order.customer_organization_name?.toLowerCase().includes(searchTerm.toLowerCase()));
        return order.customer_organization_name?.toLowerCase().includes(searchTerm.toLowerCase());
      });
  }, [customerOrders, searchTerm, filterStatus]);
  // console.log('All customer2 orders:', filteredCustomerOrders);

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

  const handleUpdateSupplierOrder = async (orderData) => {
    try {
      await ordersService.updateSupplierOrder(editingOrder.id, orderData);
      await fetchData(); // Refresh all data
      setShowSupplierOrderModal(false);
      setEditingOrder(null);
      setEditOrderType(null);
    } catch (err) {
      console.error("Error updating supplier order:", err);
      throw err;
    }
  };

  const handleUpdateCustomerOrder = async (orderData) => {
    try {
      await ordersService.updateCustomerOrder(editingOrder.id, orderData);
      await fetchData(); // Refresh all data
      setShowCustomerOrderModal(false);
      setEditingOrder(null);
      setEditOrderType(null);
    } catch (err) {
      console.error("Error updating customer order:", err);
      throw err;
    }
  };



  const handleReceiveSupplierOrder = (order) => {
    setSelectedSupplierOrderForReceive(order);
    setShowSupplierReceiveModal(true);
  };

  const handleSupplierOrderReceived = async (orderId, receiveData) => {
    try {
      await ordersService.receiveSupplierOrderItems(orderId, receiveData);
      await fetchData(); // Refresh all data
      setShowSupplierReceiveModal(false);
      setSelectedSupplierOrderForReceive(null);
    } catch (err) {
      console.error("Error receiving supplier order:", err);
      throw err;
    }
  };

  const handleWriteOffSupplierOrder = (order) => {
    setSelectedSupplierOrderForWriteOff(order);
    setShowSupplierWriteOffModal(true);
  };

  const handleSupplierOrderWrittenOff = async (orderId, writeOffData) => {
    try {
      await ordersService.writeOffSupplierOrderItems(orderId, writeOffData);
      await fetchData(); // Refresh all data
      setShowSupplierWriteOffModal(false);
      setSelectedSupplierOrderForWriteOff(null);
    } catch (err) {
      console.error("Error writing off supplier order items:", err);
      throw err;
    }
  };

  const handleShipOrder = (order) => {
    setSelectedOrderForShipping(order);
    setShowShipOrderModal(true);
  };

  const handleConfirmReceipt = (order) => {
    setSelectedOrderForReceipt(order);
    setShowConfirmReceiptModal(true);
  };

  const handleWriteOff = (order) => {
    setSelectedOrderForWriteOff(order);
    setShowWriteOffModal(true);
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

  const handleWriteOffSubmitted = async (orderId, writeOffData) => {
    try {
      await ordersService.writeOffCustomerOrderItems(orderId, writeOffData);
      await fetchData(); // Refresh all data
      setShowWriteOffModal(false);
      setSelectedOrderForWriteOff(null);
    } catch (err) {
      console.error("Error writing off order items:", err);
      throw err;
    }
  };

  const handleEditOrder = (order, orderType) => {
    setEditingOrder(order);
    setEditOrderType(orderType);
    if (orderType === 'customer') {
      setShowCustomerOrderModal(true);
    } else {
      setShowSupplierOrderModal(true);
    }
  };

  const handleDeleteOrder = (order, orderType) => {
    setOrderToDelete({ order, orderType });
    setShowDeleteConfirm(true);
  };

  const confirmDeleteOrder = async () => {
    if (!orderToDelete) return;
    
    try {
      const { order, orderType } = orderToDelete;
      if (orderType === 'customer') {
        await ordersService.deleteCustomerOrder(order.id);
      } else {
        await ordersService.deleteSupplierOrder(order.id);
      }
      await fetchData(); // Refresh all data
      setShowDeleteConfirm(false);
      setOrderToDelete(null);
    } catch (err) {
      console.error("Error deleting order:", err);
      setError(err.message || "Failed to delete order");
    }
  };

  const cancelDelete = () => {
    setShowDeleteConfirm(false);
    setOrderToDelete(null);
  };

  const canReceiveSupplierOrder = (order) => {
    // Can receive as long as anything ordered is still outstanding (neither received nor
    // written off yet). Repeatable, so successive partial deliveries can each be recorded.
    if (!user) return false;
    const hasOutstanding = (order.items || []).some(item =>
      Number(item.quantity || 0) - Number(item.quantity_received || 0) - Number(item.quantity_written_off || 0) > 0
    );
    if (!hasOutstanding) return false;
    if (user.role === 'super_admin') return true;
    return user.role === 'admin' && order.ordering_organization_id === user.organization_id;
  };

  const canWriteOffSupplierOrder = (order) => {
    return canReceiveSupplierOrder(order);
  };

  const canShipOrder = (order) => {
    // Receiver organization (Oraseas EE, BossServe, BossAqua) can ship an order as long as
    // it still has any unshipped quantity remaining (can be called repeatedly for partial shipments).
    // Check if current user's organization is the receiver (oraseas_organization_id)
    return user &&
      (user.role === 'admin' || user.role === 'super_admin') &&
      order.oraseas_organization_id === user.organization_id &&
      ['Requested', 'Pending', 'Partially Shipped'].includes(order.status);
  };

  const canConfirmReceipt = (order) => {
    // Customer organization can confirm receipt as long as anything shipped is still
    // awaiting receipt (can be called repeatedly as successive partial shipments arrive).
    // Check if current user's organization is the customer (customer_organization_id)
    return user &&
      order.customer_organization_id === user.organization_id &&
      ['Shipped', 'Partially Received'].includes(order.status);
  };

  const canWriteOffOrder = (order) => {
    // Oraseas EE admin can write off a shipped quantity that's still outstanding
    // (shipped but neither received nor already written off).
    return user &&
      (user.role === 'admin' || user.role === 'super_admin') &&
      order.oraseas_organization_id === user.organization_id &&
      (order.items || []).some(item =>
        Number(item.quantity_shipped || 0) - Number(item.quantity_received || 0) - Number(item.quantity_written_off || 0) > 0
      );
  };

  const canEditOrder = (order) => {
    // Super admins can edit orders at any stage. Admins of the Oraseas org that
    // owns the order can also edit at any stage (including after it ships);
    // other admins only while the order is still Pending.
    if (!user) return false;
    if (user.role === 'super_admin') return true;
    if (user.role !== 'admin') return false;
    if (order.oraseas_organization_id === user.organization_id) return true;
    return order.status === 'Pending';
  };

  const canDeleteOrder = (order) => {
    // Super admins can delete orders at any stage; regular admins only Requested/Pending
    if (!user) return false;
    if (user.role === 'super_admin') return true;
    return user.role === 'admin' && (order.status === 'Requested' || order.status === 'Pending');
  };

  const getOrderStatusBadgeClasses = (status) => {
    switch (status) {
      case 'Requested': return 'bg-yellow-100 text-yellow-800';
      case 'Pending': return 'bg-blue-100 text-blue-800';
      case 'Partially Shipped': return 'bg-indigo-100 text-indigo-800';
      case 'Shipped': return 'bg-purple-100 text-purple-800';
      case 'Partially Received': return 'bg-teal-100 text-teal-800';
      case 'Received': return 'bg-green-100 text-green-800';
      case 'Delivered': return 'bg-green-100 text-green-800';
      default: return 'bg-red-100 text-red-800';
    }
  };

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-3xl font-bold text-gray-800">{t('orders.title')}</h1>
          <p className="text-gray-600 mt-1">{t('orders.subtitle')}</p>
        </div>
        <div className="flex space-x-2">
          <button
            onClick={() => setShowAnalytics(!showAnalytics)}
            className="bg-purple-600 text-white py-2 px-4 rounded-md hover:bg-purple-700 font-semibold"
          >
            {t('orders.toggleAnalytics')}
          </button>
          <button
            onClick={() => setShowOrderHistoryModal(true)}
            className="bg-gray-600 text-white py-2 px-4 rounded-md hover:bg-gray-700 font-semibold"
          >
            {t('orders.viewHistory')}
          </button>

          {/* Only show Add Supplier Order for Oraseas EE users and super admins */}
          {(user?.role === 'super_admin' ||
            organizations.find(org => org.id === user?.organization_id)?.organization_type === 'oraseas_ee') && (
              <button
                onClick={() => setShowSupplierOrderModal(true)}
                className="bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 font-semibold"
              >
                {t('orders.createSupplierOrder')}
              </button>
            )}
          <button
            onClick={() => setShowCustomerOrderModal(true)}
            className="bg-green-600 text-white py-2 px-4 rounded-md hover:bg-green-700 font-semibold"
          >
            {t('orders.createCustomerOrder')}
          </button>
        </div>
      </div>

      {/* Tab Navigation */}
      <div className="bg-white rounded-lg shadow-md mb-6">
        <div className="border-b border-gray-200">
          <nav className="-mb-px flex space-x-8 px-6">
            <button
              onClick={() => setActiveView('list')}
              className={`py-4 px-1 border-b-2 font-medium text-sm ${
                activeView === 'list'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              📋 {t('orders.listView')}
            </button>
            <button
              onClick={() => setActiveView('calendar')}
              className={`py-4 px-1 border-b-2 font-medium text-sm ${
                activeView === 'calendar'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              📅 {t('orders.calendarView')}
            </button>
          </nav>
        </div>
      </div>

      {/* Order Analytics Dashboard */}
      {showAnalytics && (
        <div className="bg-white p-6 rounded-lg shadow-md mb-6">
          <h2 className="text-xl font-bold text-gray-800 mb-4">{t('orders.orderAnalytics')}</h2>
          <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
            <div className="bg-blue-50 p-4 rounded-lg">
              <h3 className="text-sm font-medium text-blue-600">{t('orders.totalOrders')}</h3>
              <p className="text-2xl font-bold text-blue-800">{orderAnalytics.totalOrders}</p>
            </div>
            <div className="bg-yellow-50 p-4 rounded-lg">
              <h3 className="text-sm font-medium text-yellow-600">{t('orders.pendingOrders')}</h3>
              <p className="text-2xl font-bold text-yellow-800">{orderAnalytics.pendingOrders}</p>
            </div>
            <div className="bg-green-50 p-4 rounded-lg">
              <h3 className="text-sm font-medium text-green-600">{t('orders.completedOrders')}</h3>
              <p className="text-2xl font-bold text-green-800">{orderAnalytics.completedOrders}</p>
            </div>
            <div className="bg-red-50 p-4 rounded-lg">
              <h3 className="text-sm font-medium text-red-600">{t('orders.overdueOrders')}</h3>
              <p className="text-2xl font-bold text-red-800">{orderAnalytics.overdueOrders}</p>
            </div>
            <div className="bg-indigo-50 p-4 rounded-lg">
              <h3 className="text-sm font-medium text-indigo-600">{t('orders.completionRate')}</h3>
              <p className="text-2xl font-bold text-indigo-800">{orderAnalytics.completionRate}%</p>
            </div>
          </div>
        </div>
      )}

      {loading && <p className="text-gray-500">{t('orders.loadingOrders')}</p>}
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
            <label htmlFor="search" className="block text-sm font-medium text-gray-700">{t('orders.searchByName')}</label>
            <input
              type="text"
              id="search"
              placeholder={t('orders.searchByName')}
              className="mt-1 w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </div>
          <div>
            <label htmlFor="filterStatus" className="block text-sm font-medium text-gray-700">{t('orders.filterByStatus')}</label>
            <select
              id="filterStatus"
              className="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm rounded-md"
              value={filterStatus}
              onChange={(e) => setFilterStatus(e.target.value)}
            >
              <option value="all">{t('orders.allStatuses')}</option>
              <option value="Requested">{t('orders.requested')}</option>
              <option value="Pending">{t('orders.pending')}</option>
              <option value="Shipped">{t('orders.shipped')}</option>
              <option value="Received">{t('orders.received')}</option>
              <option value="Delivered">{t('orders.delivered')}</option>
              <option value="Cancelled">{t('orders.cancelled')}</option>
            </select>
          </div>
          <div>
            <label htmlFor="filterOrderType" className="block text-sm font-medium text-gray-700">{t('orders.filterByOrderType')}</label>
            <select
              id="filterOrderType"
              className="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm rounded-md"
              value={filterOrderType}
              onChange={(e) => setFilterOrderType(e.target.value)}
            >
              <option value="all">{t('orders.allOrders')}</option>
              <option value="supplier">{t('orders.supplierOrders')}</option>
              <option value="customer">{t('orders.customerOrders')}</option>
            </select>
          </div>
        </div>
      </div>

      {/* Calendar View */}
      {activeView === 'calendar' && (
        <OrderCalendarView
          orders={[...filteredCustomerOrders, ...filteredSupplierOrders]}
          onOrderClick={(order) => {
            setExpandedOrderId(order.id === expandedOrderId ? null : order.id);
          }}
        />
      )}

      {/* List View */}
      {activeView === 'list' && (
        <>
          {(filterOrderType === 'all' || filterOrderType === 'supplier') && (
            <div>
              <h2 className="text-2xl font-bold text-gray-700 mt-8 mb-4">{t('orders.supplierOrders')}</h2>
          {filteredSupplierOrders.length > 0 ? (
            <div className="flex flex-col space-y-4 mb-12">
              {filteredSupplierOrders.map((order) => (
                <div key={order.id} className="bg-white p-4 rounded-lg shadow-md border border-gray-200 transition-shadow duration-200 hover:shadow-lg">
                  <div className="flex justify-between items-start">
                    <div className="flex-1">
                      <div className="flex items-center justify-between mb-2">
                        <h3 className="text-xl font-semibold text-red-700">{t('orders.orderFrom')} {order.supplier_name}</h3>
                        <div className="flex items-center space-x-2">
                          <span className={`px-2 py-1 text-xs font-semibold rounded-full ${getOrderStatusBadgeClasses(order.status)}`}>
                            {order.status}
                          </span>
                        </div>
                      </div>
                      <div className="grid grid-cols-2 gap-4 text-sm text-gray-600">
                        <p><span className="font-medium">{t('orders.orderDate')}:</span> {new Date(order.order_date).toLocaleDateString()}</p>
                        {order.expected_delivery_date && (
                          <p><span className="font-medium">{t('orders.expected')}:</span> {new Date(order.expected_delivery_date).toLocaleDateString()}</p>
                        )}
                        {order.actual_delivery_date && (
                          <p><span className="font-medium">{t('orders.delivered')}:</span> {new Date(order.actual_delivery_date).toLocaleDateString()}</p>
                        )}
                      </div>
                    </div>
                    <div className="flex space-x-2 ml-4">
                      {canReceiveSupplierOrder(order) && (
                        <button
                          onClick={() => handleReceiveSupplierOrder(order)}
                          className="text-sm bg-green-600 hover:bg-green-700 text-white font-semibold py-1 px-3 rounded-md transition-colors"
                        >
                          Receive
                        </button>
                      )}
                      {canWriteOffSupplierOrder(order) && (
                        <button
                          onClick={() => handleWriteOffSupplierOrder(order)}
                          className="text-sm bg-orange-600 hover:bg-orange-700 text-white font-semibold py-1 px-3 rounded-md transition-colors"
                        >
                          Report Loss
                        </button>
                      )}
                      {canEditOrder(order) && (
                        <button
                          onClick={() => handleEditOrder(order, 'supplier')}
                          className="text-sm bg-blue-600 hover:bg-blue-700 text-white font-semibold py-1 px-3 rounded-md transition-colors"
                        >
                          {t('common.edit')}
                        </button>
                      )}
                      {canDeleteOrder(order) && (
                        <button
                          onClick={() => handleDeleteOrder(order, 'supplier')}
                          className="text-sm bg-red-600 hover:bg-red-700 text-white font-semibold py-1 px-3 rounded-md transition-colors"
                        >
                          {t('common.delete')}
                        </button>
                      )}
                      <button
                        onClick={() => toggleOrderItems(order.id)}
                        className="text-sm bg-gray-200 hover:bg-gray-300 text-gray-800 font-semibold py-1 px-3 rounded-md transition-colors"
                      >
                        {expandedOrderId === order.id ? t('orders.collapseDetails') : t('orders.viewDetails')}
                      </button>
                    </div>
                  </div>
                  {expandedOrderId === order.id && (
                    <div className="mt-4 border-t pt-4">
                      <h4 className="font-semibold text-gray-800 mb-2">{t('orders.orderItems')}</h4>
                      {order.items && order.items.length > 0 ? (
                        <ul className="list-disc list-inside space-y-1 text-gray-600 pl-2">
                          {order.items.map(item => (
                            <li key={item.id}>
                              {item.quantity} x {item.part_name} ({item.part_number})
                              {(Number(item.quantity_received) > 0 || Number(item.quantity_written_off) > 0) && (
                                <span className="text-xs text-gray-500 ml-1">
                                  &mdash; {item.quantity_received || 0} received
                                  {Number(item.quantity_written_off) > 0 && (
                                    <>, <span className="text-orange-600">{item.quantity_written_off} written off</span></>
                                  )}
                                </span>
                              )}
                            </li>
                          ))}
                        </ul>
                      ) : (
                        <p className="text-gray-500">{t('orders.noItemsInOrder')}</p>
                      )}
                    </div>
                  )}
                </div>
              ))}
            </div>
          ) : (
            !loading && supplierOrders.length > 0 && <p className="text-gray-500">{t('orders.noOrdersMatch')}</p>
          )}
        </div>
      )}

      {(filterOrderType === 'all' || filterOrderType === 'customer') && (
        <div>
          <h2 className="text-2xl font-bold text-gray-700 mt-8 mb-4">{t('orders.customerOrders')}</h2>
          {filteredCustomerOrders.length > 0 ? (
            <div className="flex flex-col space-y-4 mb-12">
              {filteredCustomerOrders.map((order) => (
                <div key={order.id} className={`bg-white p-4 rounded-lg shadow-md border transition-shadow duration-200 hover:shadow-lg ${unfulfillableOrderMap[order.id] ? 'border-orange-300' : 'border-gray-200'}`}>
                  <div className="flex flex-col sm:flex-row sm:justify-between sm:items-start">
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center justify-between mb-2">
                        <h3 className="text-lg sm:text-xl font-semibold text-indigo-700 truncate">{t('orders.orderFor')} {order.customer_organization_name || 'Unknown'}</h3>
                        <div className="flex items-center space-x-2 flex-shrink-0 ml-2">
                          {/* Stock warning indicator */}
                          {unfulfillableOrderMap[order.id] && (
                            <button
                              onClick={() => {
                                setSelectedOrderMissingParts({
                                  order_id: order.id,
                                  customer_organization_name: order.customer_organization_name,
                                  items_short: unfulfillableOrderMap[order.id],
                                });
                                setShowStockWarningModal(true);
                              }}
                              className="flex items-center space-x-1 px-2 py-1 text-xs font-semibold rounded-full bg-orange-100 text-orange-800 hover:bg-orange-200 transition-colors cursor-pointer"
                              title={t('orders.insufficientStock', { fallback: 'Insufficient stock to fulfill this order' })}
                            >
                              <svg className="w-3.5 h-3.5" fill="currentColor" viewBox="0 0 20 20">
                                <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                              </svg>
                              <span>{t('orders.missingParts', { count: unfulfillableOrderMap[order.id].length, fallback: `${unfulfillableOrderMap[order.id].length} missing` })}</span>
                            </button>
                          )}
                          <span className={`px-2 py-1 text-xs font-semibold rounded-full ${getOrderStatusBadgeClasses(order.status)}`}>
                            {order.status}
                          </span>
                        </div>
                      </div>
                      <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 sm:gap-4 text-sm text-gray-600">
                        <p><span className="font-medium">{t('orders.orderDate')}:</span> {new Date(order.order_date).toLocaleDateString()}</p>
                        {order.expected_delivery_date && (
                          <p><span className="font-medium">{t('orders.expected')}:</span> {new Date(order.expected_delivery_date).toLocaleDateString()}</p>
                        )}
                        {order.shipped_date && (
                          <p><span className="font-medium">{t('orders.shipped')}:</span> {new Date(order.shipped_date).toLocaleDateString()}</p>
                        )}
                        {order.actual_delivery_date && (
                          <p><span className="font-medium">{t('orders.received')}:</span> {new Date(order.actual_delivery_date).toLocaleDateString()}</p>
                        )}
                        {order.ordered_by_username && (
                          <p><span className="font-medium">{t('orders.orderedBy')}:</span> {order.ordered_by_username}</p>
                        )}
                        {order.receiving_warehouse_name && ['Received', 'Delivered', 'Partially Received'].includes(order.status) && (
                          <p><span className="font-medium">Warehouse:</span> {order.receiving_warehouse_name}</p>
                        )}
                      </div>
                    </div>
                    <div className="flex flex-wrap gap-2 mt-3 sm:mt-0 sm:ml-4 sm:flex-nowrap">
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
                      {canWriteOffOrder(order) && (
                        <button
                          onClick={() => handleWriteOff(order)}
                          className="text-sm bg-orange-600 hover:bg-orange-700 text-white font-semibold py-1 px-3 rounded-md transition-colors"
                        >
                          Report Loss
                        </button>
                      )}
                      {canEditOrder(order) && (
                        <button
                          onClick={() => handleEditOrder(order, 'customer')}
                          className="text-sm bg-blue-600 hover:bg-blue-700 text-white font-semibold py-1 px-3 rounded-md transition-colors"
                        >
                          Edit
                        </button>
                      )}
                      {canDeleteOrder(order) && (
                        <button
                          onClick={() => handleDeleteOrder(order, 'customer')}
                          className="text-sm bg-red-600 hover:bg-red-700 text-white font-semibold py-1 px-3 rounded-md transition-colors"
                        >
                          Delete
                        </button>
                      )}
                      <button
                        onClick={() => toggleOrderItems(order.id)}
                        className="text-sm bg-gray-200 hover:bg-gray-300 text-gray-800 font-semibold py-1 px-3 rounded-md transition-colors"
                      >
                        {expandedOrderId === order.id ? t('orders.collapseDetails') : t('orders.viewDetails')}
                      </button>
                    </div>
                  </div>
                  {expandedOrderId === order.id && (
                    <div className="mt-4 border-t pt-4">
                      <h4 className="font-semibold text-gray-800 mb-2">{t('orders.orderItems')}</h4>
                      {order.items && order.items.length > 0 ? (
                        <ul className="list-disc list-inside space-y-1 text-gray-600 pl-2">
                          {order.items.map(item => (
                            <li key={item.id}>
                              {item.quantity} x {item.part_name} ({item.part_number})
                              {Number(item.quantity_shipped) > 0 && (
                                <span className="text-xs text-gray-500 ml-1">
                                  &mdash; {item.quantity_shipped} {t('orders.shipped', { fallback: 'shipped' })}, {item.quantity_received} {t('orders.received', { fallback: 'received' })}
                                  {Number(item.quantity_written_off) > 0 && (
                                    <>, <span className="text-orange-600">{item.quantity_written_off} written off</span></>
                                  )}
                                </span>
                              )}
                            </li>
                          ))}
                        </ul>
                      ) : (
                        <p className="text-gray-500">{t('orders.noItemsInOrder')}</p>
                      )}
                    </div>
                  )}
                </div>
              ))}
            </div>
          ) : (
            !loading && customerOrders.length > 0 && <p className="text-gray-500">{t('orders.noOrdersMatch')}</p>
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
        </>
      )}

      <Modal 
        isOpen={showSupplierOrderModal} 
        onClose={() => {
          setShowSupplierOrderModal(false);
          setEditingOrder(null);
          setEditOrderType(null);
        }} 
        title={editingOrder && editOrderType === 'supplier' ? t('orders.editOrder') : t('orders.createSupplierOrder')} 
        size="xl"
      >
        <SupplierOrderForm 
          onSubmit={editingOrder && editOrderType === 'supplier' ? handleUpdateSupplierOrder : handleCreateSupplierOrder} 
          onClose={() => {
            setShowSupplierOrderModal(false);
            setEditingOrder(null);
            setEditOrderType(null);
          }} 
          organizations={organizations} 
          parts={parts}
          initialData={(editingOrder && editOrderType === 'supplier') ? editingOrder : {}}
          editMode={!!(editingOrder && editOrderType === 'supplier')}
        />
      </Modal>

      <Modal 
        isOpen={showCustomerOrderModal} 
        onClose={() => {
          setShowCustomerOrderModal(false);
          setEditingOrder(null);
          setEditOrderType(null);
        }} 
        title={editingOrder && editOrderType === 'customer' ? t('orders.editOrder') : t('orders.createCustomerOrder')} 
        size="xl"
      >
        <CustomerOrderForm 
          onSubmit={editingOrder && editOrderType === 'customer' ? handleUpdateCustomerOrder : handleCreateCustomerOrder} 
          onClose={() => {
            setShowCustomerOrderModal(false);
            setEditingOrder(null);
            setEditOrderType(null);
          }} 
          organizations={organizations} 
          parts={parts}
          initialData={(editingOrder && editOrderType === 'customer') ? editingOrder : {}}
          editMode={!!(editingOrder && editOrderType === 'customer')}
        />
      </Modal>

      {/* Delete Confirmation Modal */}
      <Modal
        isOpen={showDeleteConfirm}
        onClose={cancelDelete}
        title="Confirm Delete"
      >
        <div className="p-4">
          <p className="text-gray-700 mb-4">
            Are you sure you want to delete this order? This action cannot be undone.
          </p>
          {orderToDelete && (
            <div className="bg-gray-50 p-3 rounded mb-4">
              <p className="text-sm"><span className="font-medium">Order Type:</span> {orderToDelete.orderType === 'customer' ? 'Customer Order' : 'Supplier Order'}</p>
              <p className="text-sm"><span className="font-medium">Status:</span> {orderToDelete.order.status}</p>
              <p className="text-sm"><span className="font-medium">Date:</span> {new Date(orderToDelete.order.order_date).toLocaleDateString()}</p>
            </div>
          )}
          <div className="flex justify-end space-x-2">
            <button
              onClick={cancelDelete}
              className="px-4 py-2 bg-gray-200 hover:bg-gray-300 text-gray-800 rounded-md transition-colors"
            >
              Cancel
            </button>
            <button
              onClick={confirmDeleteOrder}
              className="px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-md transition-colors"
            >
              Delete Order
            </button>
          </div>
        </div>
      </Modal>



      {/* Supplier Order Receive Modal */}
      <Modal
        isOpen={showSupplierReceiveModal}
        onClose={() => {
          setShowSupplierReceiveModal(false);
          setSelectedSupplierOrderForReceive(null);
        }}
        title="Receive Supplier Order"
      >
        {selectedSupplierOrderForReceive && (
          <SupplierOrderReceiveForm
            order={selectedSupplierOrderForReceive}
            warehouses={warehouses}
            onSubmit={handleSupplierOrderReceived}
            onClose={() => {
              setShowSupplierReceiveModal(false);
              setSelectedSupplierOrderForReceive(null);
            }}
          />
        )}
      </Modal>

      {/* Supplier Order Write Off Modal */}
      <Modal
        isOpen={showSupplierWriteOffModal}
        onClose={() => {
          setShowSupplierWriteOffModal(false);
          setSelectedSupplierOrderForWriteOff(null);
        }}
        title="Report Loss"
      >
        {selectedSupplierOrderForWriteOff && (
          <SupplierOrderWriteOffForm
            order={selectedSupplierOrderForWriteOff}
            onSubmit={handleSupplierOrderWrittenOff}
            onClose={() => {
              setShowSupplierWriteOffModal(false);
              setSelectedSupplierOrderForWriteOff(null);
            }}
          />
        )}
      </Modal>

      {/* Order History Modal */}
      <Modal
        isOpen={showOrderHistoryModal}
        onClose={() => setShowOrderHistoryModal(false)}
        title={t('orders.viewHistory')}
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
            warehouses={warehouses}
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

      {/* Write Off Modal */}
      <Modal
        isOpen={showWriteOffModal}
        onClose={() => {
          setShowWriteOffModal(false);
          setSelectedOrderForWriteOff(null);
        }}
        title="Report Loss"
      >
        {selectedOrderForWriteOff && (
          <WriteOffForm
            order={selectedOrderForWriteOff}
            onSubmit={handleWriteOffSubmitted}
            onClose={() => {
              setShowWriteOffModal(false);
              setSelectedOrderForWriteOff(null);
            }}
          />
        )}
      </Modal>

      {/* Stock Warning Modal - Missing Parts Detail */}
      <Modal
        isOpen={showStockWarningModal}
        onClose={() => {
          setShowStockWarningModal(false);
          setSelectedOrderMissingParts(null);
        }}
        title={t('orders.missingPartsTitle', { fallback: 'Insufficient Stock for Order' })}
        size="lg"
      >
        {selectedOrderMissingParts && (
          <div className="p-4">
            <div className="mb-4">
              <p className="text-sm text-gray-600">
                {t('orders.missingPartsDesc', { fallback: 'The following parts in this order exceed available stock in Oraseas warehouses:' })}
              </p>
              <p className="text-sm font-medium text-gray-800 mt-1">
                {t('orders.customerLabel', { fallback: 'Customer' })}: {selectedOrderMissingParts.customer_organization_name}
              </p>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full text-sm border-collapse">
                <thead>
                  <tr className="bg-gray-50 border-b border-gray-200">
                    <th className="text-left py-2 px-3 font-medium text-gray-600">{t('common.part', { fallback: 'Part' })}</th>
                    <th className="text-right py-2 px-3 font-medium text-gray-600">{t('dashboard.inStock', { fallback: 'In Stock' })}</th>
                    <th className="text-right py-2 px-3 font-medium text-gray-600">{t('orders.inThisOrder', { fallback: 'In This Order' })}</th>
                    <th className="text-right py-2 px-3 font-medium text-gray-600">{t('orders.totalAllActiveOrders', { fallback: 'Total All Active Orders' })}</th>
                  </tr>
                </thead>
                <tbody>
                  {selectedOrderMissingParts.items_short.map((item, idx) => (
                    <tr key={idx} className="border-b border-gray-100 last:border-0 hover:bg-gray-50">
                      <td className="py-2 px-3">
                        <span className="font-medium text-gray-800">{item.part_name}</span>
                        <span className="text-xs text-gray-500 ml-1">({item.part_number})</span>
                      </td>
                      <td className="text-right py-2 px-3 text-gray-700">{item.quantity_in_stock}</td>
                      <td className="text-right py-2 px-3 font-semibold text-red-600">{item.quantity_in_this_order}</td>
                      <td className="text-right py-2 px-3 text-orange-600">{item.total_quantity_all_active_orders}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            <div className="mt-4 flex justify-end">
              <button
                onClick={() => {
                  setShowStockWarningModal(false);
                  setSelectedOrderMissingParts(null);
                }}
                className="px-4 py-2 bg-gray-200 hover:bg-gray-300 text-gray-800 rounded-md transition-colors text-sm"
              >
                {t('common.close', { fallback: 'Close' })}
              </button>
            </div>
          </div>
        )}
      </Modal>
    </div>
  );
};

// Ship Order Form Component
const ShipOrderForm = ({ order, warehouses, onSubmit, onClose }) => {
  const [formData, setFormData] = useState({
    shipped_date: new Date().toISOString().split('T')[0],
    tracking_number: '',
    notes: ''
  });
  const [itemQuantities, setItemQuantities] = useState({});
  const [availableStock, setAvailableStock] = useState({});
  const [stockLoading, setStockLoading] = useState(true);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Only items with something left to ship. Falls back to the full quantity
  // for orders created before partial-shipment tracking existed.
  const shippableItems = (order.items || []).filter(
    item => Number(item.quantity) - Number(item.quantity_shipped || 0) > 0
  );

  // Mirrors the backend's default: first warehouse belonging to the Oraseas organization.
  const sourceWarehouse = (warehouses || []).find(
    w => w.organization_id === order.oraseas_organization_id
  );

  useEffect(() => {
    let cancelled = false;

    const loadStock = async () => {
      if (!sourceWarehouse) {
        setStockLoading(false);
        return;
      }
      setStockLoading(true);
      try {
        const inventoryItems = await inventoryService.getWarehouseInventory(sourceWarehouse.id);
        if (cancelled) return;
        const stockByPart = {};
        (inventoryItems || []).forEach(inv => {
          stockByPart[inv.part_id] = Number(inv.current_stock) || 0;
        });
        setAvailableStock(stockByPart);

        const initialQuantities = {};
        shippableItems.forEach(item => {
          const remaining = Number(item.quantity) - Number(item.quantity_shipped || 0);
          const available = stockByPart[item.part_id] || 0;
          initialQuantities[item.id] = Math.max(0, Math.min(remaining, available));
        });
        setItemQuantities(initialQuantities);
      } finally {
        if (!cancelled) setStockLoading(false);
      }
    };

    loadStock();
    return () => { cancelled = true; };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [order.id, sourceWarehouse && sourceWarehouse.id]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleQuantityChange = (itemId, value) => {
    setItemQuantities(prev => ({ ...prev, [itemId]: value }));
  };

  const isQuantityValid = (item) => {
    const qty = Number(itemQuantities[item.id]);
    const remaining = Number(item.quantity) - Number(item.quantity_shipped || 0);
    const available = availableStock[item.part_id] || 0;
    return !isNaN(qty) && qty >= 0 && qty <= remaining && qty <= available;
  };

  const hasAnythingToShip = shippableItems.some(item => Number(itemQuantities[item.id]) > 0);
  const allValid = shippableItems.every(isQuantityValid);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!sourceWarehouse) {
      setError('No source warehouse available to ship from');
      return;
    }
    setLoading(true);
    setError(null);

    try {
      const items = shippableItems
        .filter(item => Number(itemQuantities[item.id]) > 0)
        .map(item => ({ customer_order_item_id: item.id, quantity: Number(itemQuantities[item.id]) }));

      await onSubmit(order.id, { ...formData, items });
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
        {sourceWarehouse && (
          <p className="text-sm text-gray-600">
            <span className="font-medium">Shipping from:</span> {sourceWarehouse.name}
          </p>
        )}
        {!sourceWarehouse && (
          <p className="text-sm text-red-600 mt-1">No warehouse found for the Oraseas organization</p>
        )}
      </div>

      <div>
        <h3 className="font-semibold text-gray-800 mb-2">Items to Ship</h3>
        {stockLoading ? (
          <p className="text-sm text-gray-500">Loading available stock...</p>
        ) : shippableItems.length === 0 ? (
          <p className="text-sm text-gray-500">Everything on this order has already been shipped.</p>
        ) : (
          <div className="space-y-2">
            {shippableItems.map(item => {
              const remaining = Number(item.quantity) - Number(item.quantity_shipped || 0);
              const available = availableStock[item.part_id] || 0;
              const valid = isQuantityValid(item);
              return (
                <div key={item.id} className="flex items-center justify-between gap-3 border border-gray-200 rounded-md p-2">
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-gray-800 truncate">{item.part_name} ({item.part_number})</p>
                    <p className="text-xs text-gray-500">Remaining to ship: {remaining} &middot; Available in warehouse: {available}</p>
                  </div>
                  <input
                    type="number"
                    min="0"
                    max={Math.min(remaining, available)}
                    step="0.001"
                    className={`w-24 px-2 py-1 border rounded-md text-sm ${valid ? 'border-gray-300' : 'border-red-400'}`}
                    value={itemQuantities[item.id] ?? 0}
                    onChange={(e) => handleQuantityChange(item.id, e.target.value)}
                    disabled={loading}
                  />
                </div>
              );
            })}
          </div>
        )}
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
          className="px-4 py-2 text-sm font-medium text-white bg-purple-600 rounded-md hover:bg-purple-700 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:ring-offset-2 disabled:opacity-50"
          disabled={loading || stockLoading || !hasAnythingToShip || !allValid}
        >
          {loading ? 'Shipping...' : 'Ship Selected Items'}
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

  // Only items with something shipped but not yet received or written off. Falls back
  // to the full quantity for orders created before partial-shipment tracking existed.
  const receivableItems = (order.items || []).filter(
    item => Number(item.quantity_shipped || 0) - Number(item.quantity_received || 0) - Number(item.quantity_written_off || 0) > 0
  );

  const [itemQuantities, setItemQuantities] = useState(() => {
    const initial = {};
    receivableItems.forEach(item => {
      initial[item.id] = Number(item.quantity_shipped || 0) - Number(item.quantity_received || 0) - Number(item.quantity_written_off || 0);
    });
    return initial;
  });

  // Filter warehouses to only show those belonging to the customer organization
  const customerWarehouses = warehouses.filter(
    w => w.organization_id === order.customer_organization_id
  );

  // Auto-select warehouse if there's only one
  useEffect(() => {
    if (customerWarehouses.length === 1 && !formData.receiving_warehouse_id) {
      setFormData(prev => ({
        ...prev,
        receiving_warehouse_id: customerWarehouses[0].id
      }));
    }
  }, [customerWarehouses, formData.receiving_warehouse_id]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleQuantityChange = (itemId, value) => {
    setItemQuantities(prev => ({ ...prev, [itemId]: value }));
  };

  const isQuantityValid = (item) => {
    const qty = Number(itemQuantities[item.id]);
    const remaining = Number(item.quantity_shipped || 0) - Number(item.quantity_received || 0) - Number(item.quantity_written_off || 0);
    return !isNaN(qty) && qty >= 0 && qty <= remaining;
  };

  const hasAnythingToReceive = receivableItems.some(item => Number(itemQuantities[item.id]) > 0);
  const allValid = receivableItems.every(isQuantityValid);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const items = receivableItems
        .filter(item => Number(itemQuantities[item.id]) > 0)
        .map(item => ({ customer_order_item_id: item.id, quantity: Number(itemQuantities[item.id]) }));

      await onSubmit(order.id, { ...formData, items });
    } catch (err) {
      setError(err.message || 'Failed to confirm receipt');
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
        <h3 className="font-semibold text-gray-800 mb-2">Items to Receive</h3>
        {receivableItems.length === 0 ? (
          <p className="text-sm text-gray-500">Nothing shipped is currently awaiting receipt.</p>
        ) : (
          <div className="space-y-2">
            {receivableItems.map(item => {
              const remaining = Number(item.quantity_shipped || 0) - Number(item.quantity_received || 0) - Number(item.quantity_written_off || 0);
              const valid = isQuantityValid(item);
              return (
                <div key={item.id} className="flex items-center justify-between gap-3 border border-gray-200 rounded-md p-2">
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-gray-800 truncate">{item.part_name} ({item.part_number})</p>
                    <p className="text-xs text-gray-500">Shipped and awaiting receipt: {remaining}</p>
                  </div>
                  <input
                    type="number"
                    min="0"
                    max={remaining}
                    step="0.001"
                    className={`w-24 px-2 py-1 border rounded-md text-sm ${valid ? 'border-gray-300' : 'border-red-400'}`}
                    value={itemQuantities[item.id] ?? 0}
                    onChange={(e) => handleQuantityChange(item.id, e.target.value)}
                    disabled={loading}
                  />
                </div>
              );
            })}
          </div>
        )}
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
          className="px-4 py-2 text-sm font-medium text-white bg-green-600 rounded-md hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2 disabled:opacity-50"
          disabled={loading || !hasAnythingToReceive || !allValid}
        >
          {loading ? 'Confirming...' : 'Confirm Selected Items'}
        </button>
      </div>
    </form>
  );
};

// Write Off Form Component - declares a shipped-but-outstanding quantity lost/damaged in transit
const WRITE_OFF_REASONS = [
  'Lost in transit',
  'Damaged in transit',
  'Carrier/courier error',
  'Other'
];

const SUPPLIER_WRITE_OFF_REASONS = [
  'Backordered - cancelled',
  'Discontinued by supplier',
  'Lost in transit',
  'Damaged in transit',
  'Other'
];

const WriteOffForm = ({ order, onSubmit, onClose }) => {
  const [notes, setNotes] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Only items with something shipped but neither received nor already written off.
  const outstandingItems = (order.items || []).filter(
    item => Number(item.quantity_shipped || 0) - Number(item.quantity_received || 0) - Number(item.quantity_written_off || 0) > 0
  );

  const [itemQuantities, setItemQuantities] = useState(() => {
    const initial = {};
    outstandingItems.forEach(item => { initial[item.id] = 0; });
    return initial;
  });
  const [itemReasons, setItemReasons] = useState(() => {
    const initial = {};
    outstandingItems.forEach(item => { initial[item.id] = ''; });
    return initial;
  });

  const getRemaining = (item) =>
    Number(item.quantity_shipped || 0) - Number(item.quantity_received || 0) - Number(item.quantity_written_off || 0);

  const handleQuantityChange = (itemId, value) => {
    setItemQuantities(prev => ({ ...prev, [itemId]: value }));
  };

  const handleReasonChange = (itemId, value) => {
    setItemReasons(prev => ({ ...prev, [itemId]: value }));
  };

  const isItemValid = (item) => {
    const qty = Number(itemQuantities[item.id]);
    if (qty <= 0) return true; // not being written off, nothing to validate
    return qty <= getRemaining(item) && !!itemReasons[item.id];
  };

  const selectedItems = outstandingItems.filter(item => Number(itemQuantities[item.id]) > 0);
  const hasAnythingSelected = selectedItems.length > 0;
  const allValid = outstandingItems.every(isItemValid);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const items = selectedItems.map(item => ({
        customer_order_item_id: item.id,
        quantity: Number(itemQuantities[item.id]),
        reason: itemReasons[item.id]
      }));

      await onSubmit(order.id, { notes, items });
    } catch (err) {
      setError(err.message || 'Failed to write off items');
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
          <span className="font-medium">Current Status:</span> {order.status}
        </p>
        <p className="text-xs text-gray-500 mt-1">
          Only enter a quantity for items that are confirmed lost or damaged in transit — this closes the
          tracking gap without adding anything to the customer's inventory.
        </p>
      </div>

      <div>
        <h3 className="font-semibold text-gray-800 mb-2">Items to Write Off</h3>
        {outstandingItems.length === 0 ? (
          <p className="text-sm text-gray-500">Nothing shipped is currently outstanding.</p>
        ) : (
          <div className="space-y-3">
            {outstandingItems.map(item => {
              const remaining = getRemaining(item);
              const valid = isItemValid(item);
              const qty = Number(itemQuantities[item.id]);
              return (
                <div key={item.id} className="border border-gray-200 rounded-md p-2 space-y-2">
                  <div className="flex items-center justify-between gap-3">
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium text-gray-800 truncate">{item.part_name} ({item.part_number})</p>
                      <p className="text-xs text-gray-500">Shipped and still outstanding: {remaining}</p>
                    </div>
                    <input
                      type="number"
                      min="0"
                      max={remaining}
                      step="0.001"
                      className={`w-24 px-2 py-1 border rounded-md text-sm ${valid ? 'border-gray-300' : 'border-red-400'}`}
                      value={itemQuantities[item.id] ?? 0}
                      onChange={(e) => handleQuantityChange(item.id, e.target.value)}
                      disabled={loading}
                    />
                  </div>
                  {qty > 0 && (
                    <select
                      className={`w-full px-2 py-1 border rounded-md text-sm ${itemReasons[item.id] ? 'border-gray-300' : 'border-red-400'}`}
                      value={itemReasons[item.id]}
                      onChange={(e) => handleReasonChange(item.id, e.target.value)}
                      disabled={loading}
                    >
                      <option value="">Select a reason...</option>
                      {WRITE_OFF_REASONS.map(reason => (
                        <option key={reason} value={reason}>{reason}</option>
                      ))}
                    </select>
                  )}
                </div>
              );
            })}
          </div>
        )}
      </div>

      <div>
        <label htmlFor="write_off_notes" className="block text-sm font-medium text-gray-700 mb-1">
          Notes
        </label>
        <textarea
          id="write_off_notes"
          name="notes"
          rows="3"
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-orange-500 focus:border-orange-500"
          value={notes}
          onChange={(e) => setNotes(e.target.value)}
          placeholder="Any additional context (carrier claim number, etc.)..."
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
          className="px-4 py-2 text-sm font-medium text-white bg-orange-600 rounded-md hover:bg-orange-700 focus:outline-none focus:ring-2 focus:ring-orange-500 focus:ring-offset-2 disabled:opacity-50"
          disabled={loading || !hasAnythingSelected || !allValid}
        >
          {loading ? 'Reporting...' : 'Report Loss'}
        </button>
      </div>
    </form>
  );
};

// Supplier Order Receive Form Component - per-item partial receiving
const SupplierOrderReceiveForm = ({ order, warehouses, onSubmit, onClose }) => {
  const [formData, setFormData] = useState({
    actual_delivery_date: new Date().toISOString().split('T')[0],
    receiving_warehouse_id: '',
    notes: ''
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const orderingWarehouses = warehouses.filter(
    w => w.organization_id === order.ordering_organization_id
  );

  // Only items with something ordered but neither received nor written off.
  const outstandingItems = (order.items || []).filter(
    item => Number(item.quantity || 0) - Number(item.quantity_received || 0) - Number(item.quantity_written_off || 0) > 0
  );

  const [itemQuantities, setItemQuantities] = useState(() => {
    const initial = {};
    outstandingItems.forEach(item => {
      initial[item.id] = Number(item.quantity || 0) - Number(item.quantity_received || 0) - Number(item.quantity_written_off || 0);
    });
    return initial;
  });

  // Auto-select warehouse if there's only one
  useEffect(() => {
    if (orderingWarehouses.length === 1 && !formData.receiving_warehouse_id) {
      setFormData(prev => ({
        ...prev,
        receiving_warehouse_id: orderingWarehouses[0].id
      }));
    }
  }, [orderingWarehouses, formData.receiving_warehouse_id]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleQuantityChange = (itemId, value) => {
    setItemQuantities(prev => ({ ...prev, [itemId]: value }));
  };

  const getRemaining = (item) =>
    Number(item.quantity || 0) - Number(item.quantity_received || 0) - Number(item.quantity_written_off || 0);

  const isQuantityValid = (item) => {
    const qty = Number(itemQuantities[item.id]);
    return !isNaN(qty) && qty >= 0 && qty <= getRemaining(item);
  };

  const hasAnythingToReceive = outstandingItems.some(item => Number(itemQuantities[item.id]) > 0);
  const allValid = outstandingItems.every(isQuantityValid);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const items = outstandingItems
        .filter(item => Number(itemQuantities[item.id]) > 0)
        .map(item => ({ supplier_order_item_id: item.id, quantity: Number(itemQuantities[item.id]) }));

      await onSubmit(order.id, { ...formData, items });
    } catch (err) {
      setError(err.message || 'Failed to receive order');
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
          <span className="font-medium">Order from:</span> {order.supplier_name}
        </p>
        <p className="text-sm text-gray-600">
          <span className="font-medium">Order Date:</span> {new Date(order.order_date).toLocaleDateString()}
        </p>
        <p className="text-sm text-gray-600">
          <span className="font-medium">Current Status:</span> {order.status}
        </p>
      </div>

      <div>
        <h3 className="font-semibold text-gray-800 mb-2">Items to Receive</h3>
        {outstandingItems.length === 0 ? (
          <p className="text-sm text-gray-500">Nothing is currently outstanding on this order.</p>
        ) : (
          <div className="space-y-2">
            {outstandingItems.map(item => {
              const remaining = getRemaining(item);
              const valid = isQuantityValid(item);
              return (
                <div key={item.id} className="flex items-center justify-between gap-3 border border-gray-200 rounded-md p-2">
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-gray-800 truncate">{item.part_name} ({item.part_number})</p>
                    <p className="text-xs text-gray-500">Ordered and still outstanding: {remaining}</p>
                  </div>
                  <input
                    type="number"
                    min="0"
                    max={remaining}
                    step="0.001"
                    className={`w-24 px-2 py-1 border rounded-md text-sm ${valid ? 'border-gray-300' : 'border-red-400'}`}
                    value={itemQuantities[item.id] ?? 0}
                    onChange={(e) => handleQuantityChange(item.id, e.target.value)}
                    disabled={loading}
                  />
                </div>
              );
            })}
          </div>
        )}
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
          {orderingWarehouses.map(warehouse => (
            <option key={warehouse.id} value={warehouse.id}>
              {warehouse.name}
            </option>
          ))}
        </select>
        {orderingWarehouses.length === 0 && (
          <p className="mt-1 text-sm text-red-600">No warehouses found for your organization</p>
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
          placeholder="Any notes about this delivery..."
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
          className="px-4 py-2 text-sm font-medium text-white bg-green-600 rounded-md hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2 disabled:opacity-50"
          disabled={loading || !hasAnythingToReceive || !allValid}
        >
          {loading ? 'Receiving...' : 'Receive Selected Items'}
        </button>
      </div>
    </form>
  );
};

// Supplier Order Write Off Form Component - declares an outstanding ordered-but-never-received quantity
const SupplierOrderWriteOffForm = ({ order, onSubmit, onClose }) => {
  const [notes, setNotes] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const outstandingItems = (order.items || []).filter(
    item => Number(item.quantity || 0) - Number(item.quantity_received || 0) - Number(item.quantity_written_off || 0) > 0
  );

  const [itemQuantities, setItemQuantities] = useState(() => {
    const initial = {};
    outstandingItems.forEach(item => { initial[item.id] = 0; });
    return initial;
  });
  const [itemReasons, setItemReasons] = useState(() => {
    const initial = {};
    outstandingItems.forEach(item => { initial[item.id] = ''; });
    return initial;
  });

  const getRemaining = (item) =>
    Number(item.quantity || 0) - Number(item.quantity_received || 0) - Number(item.quantity_written_off || 0);

  const handleQuantityChange = (itemId, value) => {
    setItemQuantities(prev => ({ ...prev, [itemId]: value }));
  };

  const handleReasonChange = (itemId, value) => {
    setItemReasons(prev => ({ ...prev, [itemId]: value }));
  };

  const isItemValid = (item) => {
    const qty = Number(itemQuantities[item.id]);
    if (qty <= 0) return true;
    return qty <= getRemaining(item) && !!itemReasons[item.id];
  };

  const selectedItems = outstandingItems.filter(item => Number(itemQuantities[item.id]) > 0);
  const hasAnythingSelected = selectedItems.length > 0;
  const allValid = outstandingItems.every(isItemValid);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const items = selectedItems.map(item => ({
        supplier_order_item_id: item.id,
        quantity: Number(itemQuantities[item.id]),
        reason: itemReasons[item.id]
      }));

      await onSubmit(order.id, { notes, items });
    } catch (err) {
      setError(err.message || 'Failed to write off items');
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
          <span className="font-medium">Order from:</span> {order.supplier_name}
        </p>
        <p className="text-sm text-gray-600">
          <span className="font-medium">Current Status:</span> {order.status}
        </p>
        <p className="text-xs text-gray-500 mt-1">
          Only enter a quantity for items that are confirmed never coming (backordered and cancelled,
          discontinued, etc.) — this closes the tracking gap.
        </p>
      </div>

      <div>
        <h3 className="font-semibold text-gray-800 mb-2">Items to Write Off</h3>
        {outstandingItems.length === 0 ? (
          <p className="text-sm text-gray-500">Nothing is currently outstanding on this order.</p>
        ) : (
          <div className="space-y-3">
            {outstandingItems.map(item => {
              const remaining = getRemaining(item);
              const valid = isItemValid(item);
              const qty = Number(itemQuantities[item.id]);
              return (
                <div key={item.id} className="border border-gray-200 rounded-md p-2 space-y-2">
                  <div className="flex items-center justify-between gap-3">
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium text-gray-800 truncate">{item.part_name} ({item.part_number})</p>
                      <p className="text-xs text-gray-500">Ordered and still outstanding: {remaining}</p>
                    </div>
                    <input
                      type="number"
                      min="0"
                      max={remaining}
                      step="0.001"
                      className={`w-24 px-2 py-1 border rounded-md text-sm ${valid ? 'border-gray-300' : 'border-red-400'}`}
                      value={itemQuantities[item.id] ?? 0}
                      onChange={(e) => handleQuantityChange(item.id, e.target.value)}
                      disabled={loading}
                    />
                  </div>
                  {qty > 0 && (
                    <select
                      className={`w-full px-2 py-1 border rounded-md text-sm ${itemReasons[item.id] ? 'border-gray-300' : 'border-red-400'}`}
                      value={itemReasons[item.id]}
                      onChange={(e) => handleReasonChange(item.id, e.target.value)}
                      disabled={loading}
                    >
                      <option value="">Select a reason...</option>
                      {SUPPLIER_WRITE_OFF_REASONS.map(reason => (
                        <option key={reason} value={reason}>{reason}</option>
                      ))}
                    </select>
                  )}
                </div>
              );
            })}
          </div>
        )}
      </div>

      <div>
        <label htmlFor="supplier_write_off_notes" className="block text-sm font-medium text-gray-700 mb-1">
          Notes
        </label>
        <textarea
          id="supplier_write_off_notes"
          name="notes"
          rows="3"
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-orange-500 focus:border-orange-500"
          value={notes}
          onChange={(e) => setNotes(e.target.value)}
          placeholder="Any additional context..."
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
          className="px-4 py-2 text-sm font-medium text-white bg-orange-600 rounded-md hover:bg-orange-700 focus:outline-none focus:ring-2 focus:ring-orange-500 focus:ring-offset-2 disabled:opacity-50"
          disabled={loading || !hasAnythingSelected || !allValid}
        >
          {loading ? 'Reporting...' : 'Report Loss'}
        </button>
      </div>
    </form>
  );
};

export default Orders;
