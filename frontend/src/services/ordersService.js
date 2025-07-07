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

export const ordersService = {
  getSupplierOrders,
  getCustomerOrders,
  createSupplierOrder,
  createCustomerOrder,
};