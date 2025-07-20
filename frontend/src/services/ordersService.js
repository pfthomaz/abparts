// c:/abparts/frontend/src/services/ordersService.js

import { api } from './api';

/**
 * Fetches all supplier orders.
 */
const getSupplierOrders = () => {
  return api.get('/supplier_orders');
};

/**
 * Fetches all customer orders.
 */
const getCustomerOrders = () => {
  return api.get('/customer_orders');
};

/**
 * Creates a new supplier order.
 * @param {object} orderData The data for the new supplier order.
 */
const createSupplierOrder = (orderData) => {
  return api.post('/supplier_orders', orderData);
};

/**
 * Creates a new customer order.
 * @param {object} orderData The data for the new customer order.
 */
const createCustomerOrder = (orderData) => {
  return api.post('/customer_orders', orderData);
};

/**
 * Updates a supplier order.
 * @param {string} orderId The ID of the supplier order to update.
 * @param {object} updateData The data to update the supplier order with.
 */
const updateSupplierOrder = (orderId, updateData) => {
  return api.put(`/supplier_orders/${orderId}`, updateData);
};

/**
 * Updates a customer order.
 * @param {string} orderId The ID of the customer order to update.
 * @param {object} updateData The data to update the customer order with.
 */
const updateCustomerOrder = (orderId, updateData) => {
  return api.put(`/customer_orders/${orderId}`, updateData);
};

/**
 * Gets order analytics and statistics.
 */
const getOrderAnalytics = () => {
  return api.get('/orders/analytics');
};

/**
 * Gets order history with filtering options.
 * @param {object} filters Filter options for order history.
 */
const getOrderHistory = (filters = {}) => {
  const params = new URLSearchParams(filters);
  return api.get(`/orders/history?${params}`);
};

/**
 * Creates a new supplier order item.
 * @param {object} itemData The data for the new supplier order item.
 */
const createSupplierOrderItem = (itemData) => {
  return api.post('/supplier_order_items', itemData);
};

/**
 * Creates a new customer order item.
 * @param {object} itemData The data for the new customer order item.
 */
const createCustomerOrderItem = (itemData) => {
  return api.post('/customer_order_items', itemData);
};

export const ordersService = {
  getSupplierOrders,
  getCustomerOrders,
  createSupplierOrder,
  createCustomerOrder,
  updateSupplierOrder,
  updateCustomerOrder,
  getOrderAnalytics,
  getOrderHistory,
  createSupplierOrderItem,
  createCustomerOrderItem,
};