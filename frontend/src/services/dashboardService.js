// c:/abparts/frontend/src/services/dashboardService.js

import { api } from './api';

/**
 * Fetches dashboard metrics.
 * @returns {Promise<object>} A promise that resolves to the dashboard metrics object.
 */
const getMetrics = () => {
  return api.get('/dashboard/metrics');
};

/**
 * Fetches data for the low stock by organization chart.
 * @returns {Promise<Array<object>>} A promise that resolves to the chart data.
 */
const getLowStockByOrg = () => {
  return api.get('/dashboard/low-stock-by-org');
};

export const dashboardService = {
  getMetrics,
  getLowStockByOrg,
};