// frontend/src/components/OrderHistoryView.js

import React, { useState, useEffect } from 'react';
import { ordersService } from '../services/ordersService';

function OrderHistoryView({ onClose }) {
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filters, setFilters] = useState({
    status: 'all',
    date_from: '',
    date_to: '',
    order_type: 'all'
  });

  useEffect(() => {
    fetchOrderHistory();
  }, [filters]); // eslint-disable-line react-hooks/exhaustive-deps

  const fetchOrderHistory = async () => {
    setLoading(true);
    setError(null);
    try {
      // Combine both supplier and customer orders for history
      const [supplierOrders, customerOrders] = await Promise.all([
        ordersService.getSupplierOrders(),
        ordersService.getCustomerOrders()
      ]);

      // Combine and sort by date
      const allOrders = [
        ...supplierOrders.map(order => ({ ...order, type: 'supplier' })),
        ...customerOrders.map(order => ({ ...order, type: 'customer' }))
      ].sort((a, b) => new Date(b.order_date) - new Date(a.order_date));

      // Apply filters
      let filteredOrders = allOrders;

      if (filters.status !== 'all') {
        filteredOrders = filteredOrders.filter(order => order.status === filters.status);
      }

      if (filters.order_type !== 'all') {
        filteredOrders = filteredOrders.filter(order => order.type === filters.order_type);
      }

      if (filters.date_from) {
        const fromDate = new Date(filters.date_from);
        filteredOrders = filteredOrders.filter(order => new Date(order.order_date) >= fromDate);
      }

      if (filters.date_to) {
        const toDate = new Date(filters.date_to);
        filteredOrders = filteredOrders.filter(order => new Date(order.order_date) <= toDate);
      }

      setOrders(filteredOrders);
    } catch (err) {
      setError(err.message || 'Failed to fetch order history');
    } finally {
      setLoading(false);
    }
  };

  const handleFilterChange = (e) => {
    const { name, value } = e.target;
    setFilters(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'Requested': return 'bg-yellow-100 text-yellow-800';
      case 'Pending': return 'bg-blue-100 text-blue-800';
      case 'Shipped': return 'bg-purple-100 text-purple-800';
      case 'Received': return 'bg-green-100 text-green-800';
      case 'Delivered': return 'bg-green-100 text-green-800';
      case 'Cancelled': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getOrderTypeColor = (type) => {
    return type === 'supplier' ? 'bg-red-100 text-red-800' : 'bg-indigo-100 text-indigo-800';
  };

  return (
    <div className="space-y-6">
      {/* Filters */}
      <div className="bg-gray-50 p-4 rounded-lg">
        <h3 className="text-lg font-semibold text-gray-800 mb-3">Filter Order History</h3>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div>
            <label htmlFor="status" className="block text-sm font-medium text-gray-700 mb-1">
              Status
            </label>
            <select
              id="status"
              name="status"
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
              value={filters.status}
              onChange={handleFilterChange}
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
            <label htmlFor="order_type" className="block text-sm font-medium text-gray-700 mb-1">
              Order Type
            </label>
            <select
              id="order_type"
              name="order_type"
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
              value={filters.order_type}
              onChange={handleFilterChange}
            >
              <option value="all">All Types</option>
              <option value="supplier">Supplier Orders</option>
              <option value="customer">Customer Orders</option>
            </select>
          </div>

          <div>
            <label htmlFor="date_from" className="block text-sm font-medium text-gray-700 mb-1">
              From Date
            </label>
            <input
              type="date"
              id="date_from"
              name="date_from"
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
              value={filters.date_from}
              onChange={handleFilterChange}
            />
          </div>

          <div>
            <label htmlFor="date_to" className="block text-sm font-medium text-gray-700 mb-1">
              To Date
            </label>
            <input
              type="date"
              id="date_to"
              name="date_to"
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
              value={filters.date_to}
              onChange={handleFilterChange}
            />
          </div>
        </div>
      </div>

      {/* Order History */}
      <div>
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-lg font-semibold text-gray-800">Order History ({orders.length} orders)</h3>
          <button
            onClick={onClose}
            className="text-gray-500 hover:text-gray-700"
          >
            Close
          </button>
        </div>

        {loading && (
          <div className="text-center py-8">
            <p className="text-gray-500">Loading order history...</p>
          </div>
        )}

        {error && (
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative mb-4" role="alert">
            <strong className="font-bold">Error:</strong>
            <span className="block sm:inline ml-2">{error}</span>
          </div>
        )}

        {!loading && !error && orders.length === 0 && (
          <div className="text-center py-8">
            <p className="text-gray-500">No orders found matching your criteria.</p>
          </div>
        )}

        {!loading && !error && orders.length > 0 && (
          <div className="space-y-3">
            {orders.map((order) => (
              <div key={`${order.type}-${order.id}`} className="bg-white p-4 rounded-lg shadow border border-gray-200">
                <div className="flex justify-between items-start mb-2">
                  <div className="flex-1">
                    <div className="flex items-center space-x-2 mb-1">
                      <span className={`px-2 py-1 text-xs font-semibold rounded-full ${getOrderTypeColor(order.type)}`}>
                        {order.type === 'supplier' ? 'Supplier Order' : 'Customer Order'}
                      </span>
                      <span className={`px-2 py-1 text-xs font-semibold rounded-full ${getStatusColor(order.status)}`}>
                        {order.status}
                      </span>
                    </div>

                    <h4 className="font-semibold text-gray-800">
                      {order.type === 'supplier'
                        ? `Order from ${order.supplier_name}`
                        : `Order for ${order.customer_organization?.name || 'Unknown'}`
                      }
                    </h4>

                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-2 text-sm text-gray-600">
                      <div>
                        <span className="font-medium">Order Date:</span>
                        <br />
                        {new Date(order.order_date).toLocaleDateString()}
                      </div>

                      {order.expected_delivery_date && (
                        <div>
                          <span className="font-medium">Expected:</span>
                          <br />
                          {new Date(order.expected_delivery_date).toLocaleDateString()}
                        </div>
                      )}

                      {order.actual_delivery_date && (
                        <div>
                          <span className="font-medium">Delivered:</span>
                          <br />
                          {new Date(order.actual_delivery_date).toLocaleDateString()}
                        </div>
                      )}

                      <div>
                        <span className="font-medium">Items:</span>
                        <br />
                        {order.items ? order.items.length : 0} items
                      </div>
                    </div>

                    {order.notes && (
                      <div className="mt-2 text-sm text-gray-600">
                        <span className="font-medium">Notes:</span> {order.notes}
                      </div>
                    )}
                  </div>
                </div>

                {/* Order Items */}
                {order.items && order.items.length > 0 && (
                  <div className="mt-3 pt-3 border-t border-gray-200">
                    <h5 className="font-medium text-gray-800 mb-2">Order Items:</h5>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                      {order.items.map((item, index) => (
                        <div key={index} className="text-sm text-gray-600 bg-gray-50 p-2 rounded">
                          <span className="font-medium">{item.part?.name || 'Unknown Part'}</span>
                          <br />
                          <span>Qty: {item.quantity} {item.part?.unit_of_measure || 'units'}</span>
                          {item.unit_price && <span> • Price: ${item.unit_price}</span>}
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

export default OrderHistoryView;