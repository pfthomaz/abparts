// frontend/src/components/TransactionHistory.js

import React, { useState, useEffect, useCallback } from 'react';
import { transactionService } from '../services/transactionService';
import { partsService } from '../services/partsService';
import { warehouseService } from '../services/warehouseService';
import { useAuth } from '../AuthContext';
import PermissionGuard from './PermissionGuard';
import { PERMISSIONS } from '../utils/permissions';

const TransactionHistory = () => {
  const { user } = useAuth();
  const [transactions, setTransactions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filters, setFilters] = useState({
    transaction_type: '',
    part_id: '',
    from_warehouse_id: '',
    to_warehouse_id: '',
    start_date: '',
    end_date: '',
    reference_number: '',
  });
  const [parts, setParts] = useState([]);
  const [warehouses, setWarehouses] = useState([]);
  const [currentPage, setCurrentPage] = useState(0);
  const [hasMore, setHasMore] = useState(true);
  const pageSize = 50;

  // Fetch supporting data
  useEffect(() => {
    const fetchSupportingData = async () => {
      try {
        const [partsData, warehousesData] = await Promise.all([
          partsService.getParts(),
          warehouseService.getWarehouses()
        ]);

        // Handle parts data - API returns {items: [...], total_count: number, has_more: boolean}
        const partsArray = Array.isArray(partsData) ? partsData : (partsData?.items || []);
        setParts(partsArray);

        // Handle warehouses data - API returns {items: [...], total_count: number, has_more: boolean}
        const warehousesArray = Array.isArray(warehousesData) ? warehousesData : (warehousesData?.items || []);
        setWarehouses(warehousesArray);
      } catch (err) {
        console.error('Failed to fetch supporting data:', err);
        // Set empty arrays on error to prevent map errors
        setParts([]);
        setWarehouses([]);
      }
    };

    fetchSupportingData();
  }, []);

  const fetchTransactions = useCallback(async (page = 0, resetData = true) => {
    setLoading(true);
    setError(null);

    try {
      const searchFilters = {
        ...filters,
        start_date: filters.start_date ? new Date(filters.start_date).toISOString() : undefined,
        end_date: filters.end_date ? new Date(filters.end_date).toISOString() : undefined,
      };

      // Remove empty filters
      if (searchFilters && typeof searchFilters === 'object') {
        Object.keys(searchFilters).forEach(key => {
          if (!searchFilters[key]) {
            delete searchFilters[key];
          }
        });
      }

      const data = await transactionService.searchTransactions(
        searchFilters,
        page * pageSize,
        pageSize
      );

      if (resetData) {
        setTransactions(data);
      } else {
        setTransactions(prev => [...prev, ...data]);
      }

      setHasMore(data.length === pageSize);
      setCurrentPage(page);
    } catch (err) {
      setError(err.message || 'Failed to fetch transactions.');
    } finally {
      setLoading(false);
    }
  }, [filters, pageSize]);

  useEffect(() => {
    fetchTransactions(0, true);
  }, [fetchTransactions]);

  const handleFilterChange = (e) => {
    const { name, value } = e.target;
    setFilters(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSearch = () => {
    setCurrentPage(0);
    fetchTransactions(0, true);
  };

  const handleClearFilters = () => {
    setFilters({
      transaction_type: '',
      part_id: '',
      from_warehouse_id: '',
      to_warehouse_id: '',
      start_date: '',
      end_date: '',
      reference_number: '',
    });
  };

  const loadMore = () => {
    if (!loading && hasMore) {
      fetchTransactions(currentPage + 1, false);
    }
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getTransactionTypeColor = (type) => {
    switch (type) {
      case 'creation': return 'text-green-600 bg-green-100';
      case 'transfer': return 'text-blue-600 bg-blue-100';
      case 'consumption': return 'text-red-600 bg-red-100';
      case 'adjustment': return 'text-yellow-600 bg-yellow-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  const getTransactionTypeLabel = (type) => {
    switch (type) {
      case 'creation': return 'Creation';
      case 'transfer': return 'Transfer';
      case 'consumption': return 'Consumption';
      case 'adjustment': return 'Adjustment';
      default: return type;
    }
  };

  return (
    <PermissionGuard permission={PERMISSIONS.VIEW_ORG_TRANSACTIONS}>
      <div className="space-y-6">
        <div className="flex justify-between items-center">
          <h2 className="text-2xl font-bold text-gray-800">Transaction History</h2>
        </div>

        {/* Filters */}
        <div className="bg-white p-6 rounded-lg shadow-md">
          <h3 className="text-lg font-semibold text-gray-800 mb-4">Filters</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            <div>
              <label htmlFor="transaction_type" className="block text-sm font-medium text-gray-700 mb-1">
                Transaction Type
              </label>
              <select
                id="transaction_type"
                name="transaction_type"
                value={filters.transaction_type}
                onChange={handleFilterChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="">All Types</option>
                <option value="creation">Creation</option>
                <option value="transfer">Transfer</option>
                <option value="consumption">Consumption</option>
                <option value="adjustment">Adjustment</option>
              </select>
            </div>

            <div>
              <label htmlFor="part_id" className="block text-sm font-medium text-gray-700 mb-1">
                Part
              </label>
              <select
                id="part_id"
                name="part_id"
                value={filters.part_id}
                onChange={handleFilterChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="">All Parts</option>
                {Array.isArray(parts) && parts.map(part => (
                  <option key={part.id} value={part.id}>
                    {part.name} ({part.part_number})
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label htmlFor="from_warehouse_id" className="block text-sm font-medium text-gray-700 mb-1">
                From Warehouse
              </label>
              <select
                id="from_warehouse_id"
                name="from_warehouse_id"
                value={filters.from_warehouse_id}
                onChange={handleFilterChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="">All Warehouses</option>
                {Array.isArray(warehouses) && warehouses.map(warehouse => (
                  <option key={warehouse.id} value={warehouse.id}>
                    {warehouse.name}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label htmlFor="to_warehouse_id" className="block text-sm font-medium text-gray-700 mb-1">
                To Warehouse
              </label>
              <select
                id="to_warehouse_id"
                name="to_warehouse_id"
                value={filters.to_warehouse_id}
                onChange={handleFilterChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="">All Warehouses</option>
                {Array.isArray(warehouses) && warehouses.map(warehouse => (
                  <option key={warehouse.id} value={warehouse.id}>
                    {warehouse.name}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label htmlFor="start_date" className="block text-sm font-medium text-gray-700 mb-1">
                Start Date
              </label>
              <input
                type="date"
                id="start_date"
                name="start_date"
                value={filters.start_date}
                onChange={handleFilterChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
              />
            </div>

            <div>
              <label htmlFor="end_date" className="block text-sm font-medium text-gray-700 mb-1">
                End Date
              </label>
              <input
                type="date"
                id="end_date"
                name="end_date"
                value={filters.end_date}
                onChange={handleFilterChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
              />
            </div>

            <div>
              <label htmlFor="reference_number" className="block text-sm font-medium text-gray-700 mb-1">
                Reference Number
              </label>
              <input
                type="text"
                id="reference_number"
                name="reference_number"
                value={filters.reference_number}
                onChange={handleFilterChange}
                placeholder="Enter reference number"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
              />
            </div>
          </div>

          <div className="flex justify-end space-x-3 mt-4">
            <button
              onClick={handleClearFilters}
              className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-200 rounded-md hover:bg-gray-300 focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-offset-2"
            >
              Clear Filters
            </button>
            <button
              onClick={handleSearch}
              className="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
            >
              Search
            </button>
          </div>
        </div>

        {/* Error Display */}
        {error && (
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative" role="alert">
            <strong className="font-bold">Error: </strong>
            <span className="block sm:inline">{error}</span>
          </div>
        )}

        {/* Transaction List */}
        <div className="bg-white rounded-lg shadow-md overflow-hidden">
          {loading && transactions.length === 0 ? (
            <div className="p-6 text-center text-gray-500">Loading transactions...</div>
          ) : transactions.length === 0 ? (
            <div className="p-6 text-center text-gray-500">No transactions found.</div>
          ) : (
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Date
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Type
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Part
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Quantity
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      From
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      To
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Performed By
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Reference
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {transactions.map((transaction) => (
                    <tr key={transaction.id} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {formatDate(transaction.transaction_date)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getTransactionTypeColor(transaction.transaction_type)}`}>
                          {getTransactionTypeLabel(transaction.transaction_type)}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        <div>
                          <div className="font-medium">{transaction.part_name}</div>
                          <div className="text-gray-500">{transaction.part_number}</div>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {transaction.quantity} {transaction.unit_of_measure}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {transaction.from_warehouse_name || '-'}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {transaction.transaction_type === 'consumption' && (transaction.machine_name || transaction.machine_serial)
                          ? `Machine: ${transaction.machine_name || transaction.machine_serial}`
                          : (transaction.to_warehouse_name || '-')}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {transaction.performed_by_username}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {transaction.reference_number || '-'}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          {/* Load More Button */}
          {hasMore && !loading && transactions.length > 0 && (
            <div className="p-4 text-center border-t border-gray-200">
              <button
                onClick={loadMore}
                className="px-4 py-2 text-sm font-medium text-blue-600 bg-blue-50 rounded-md hover:bg-blue-100 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
              >
                Load More
              </button>
            </div>
          )}

          {loading && transactions.length > 0 && (
            <div className="p-4 text-center border-t border-gray-200 text-gray-500">
              Loading more transactions...
            </div>
          )}
        </div>
      </div>
    </PermissionGuard>
  );
};

export default TransactionHistory;