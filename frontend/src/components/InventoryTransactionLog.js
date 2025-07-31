// frontend/src/components/InventoryTransactionLog.js

import React, { useState, useEffect, useCallback } from 'react';
import { useAuth } from '../AuthContext';
import { transactionService } from '../services/transactionService';
import { partsService } from '../services/partsService';
import { warehouseService } from '../services/warehouseService';
import { machinesService } from '../services/machinesService';
import PermissionGuard from './PermissionGuard';
import { PERMISSIONS } from '../utils/permissions';

const InventoryTransactionLog = ({
  partId = null,
  warehouseId = null,
  machineId = null,
  showFilters = true,
  maxHeight = '600px',
  onTransactionSelect = null
}) => {
  const [transactions, setTransactions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [currentPage, setCurrentPage] = useState(0);
  const [hasMore, setHasMore] = useState(true);
  const pageSize = 50;

  // Filter state
  const [filters, setFilters] = useState({
    transaction_type: '',
    part_id: partId || '',
    from_warehouse_id: warehouseId || '',
    to_warehouse_id: warehouseId || '',
    machine_id: machineId || '',
    start_date: '',
    end_date: '',
    reference_number: '',
    performed_by_user_id: ''
  });

  // Supporting data for filters
  const [parts, setParts] = useState([]);
  const [warehouses, setWarehouses] = useState([]);
  const [machines, setMachines] = useState([]);

  // Fetch supporting data for filters
  useEffect(() => {
    if (showFilters) {
      fetchSupportingData();
    }
  }, [showFilters]);

  // Set initial filters based on props
  useEffect(() => {
    setFilters(prev => ({
      ...prev,
      part_id: partId || prev.part_id,
      from_warehouse_id: warehouseId || prev.from_warehouse_id,
      to_warehouse_id: warehouseId || prev.to_warehouse_id,
      machine_id: machineId || prev.machine_id
    }));
  }, [partId, warehouseId, machineId]);

  const fetchSupportingData = async () => {
    try {
      const [partsData, warehousesData, machinesData] = await Promise.all([
        partsService.getParts(),
        warehouseService.getWarehouses(),
        machinesService.getMachines()
      ]);

      setParts(partsData);
      setWarehouses(warehousesData);
      setMachines(machinesData);
    } catch (err) {
      console.error('Failed to fetch supporting data:', err);
    }
  };

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
      Object.keys(searchFilters).forEach(key => {
        if (!searchFilters[key]) {
          delete searchFilters[key];
        }
      });

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
      part_id: partId || '',
      from_warehouse_id: warehouseId || '',
      to_warehouse_id: warehouseId || '',
      machine_id: machineId || '',
      start_date: '',
      end_date: '',
      reference_number: '',
      performed_by_user_id: ''
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
      case 'consumption': return 'Usage';
      case 'adjustment': return 'Adjustment';
      default: return type;
    }
  };

  const getTransactionIcon = (type) => {
    switch (type) {
      case 'creation':
        return (
          <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M10 3a1 1 0 011 1v5h5a1 1 0 110 2h-5v5a1 1 0 11-2 0v-5H4a1 1 0 110-2h5V4a1 1 0 011-1z" clipRule="evenodd" />
          </svg>
        );
      case 'transfer':
        return (
          <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M10.293 3.293a1 1 0 011.414 0l6 6a1 1 0 010 1.414l-6 6a1 1 0 01-1.414-1.414L14.586 11H3a1 1 0 110-2h11.586l-4.293-4.293a1 1 0 010-1.414z" clipRule="evenodd" />
          </svg>
        );
      case 'consumption':
        return (
          <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M9 2a1 1 0 000 2h2a1 1 0 100-2H9z" clipRule="evenodd" />
            <path fillRule="evenodd" d="M4 5a2 2 0 012-2h8a2 2 0 012 2v6a2 2 0 01-2 2H6a2 2 0 01-2-2V5zm3 3a1 1 0 000 2h.01a1 1 0 100-2H7zm3 0a1 1 0 000 2h3a1 1 0 100-2h-3z" clipRule="evenodd" />
          </svg>
        );
      case 'adjustment':
        return (
          <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M11.49 3.17c-.38-1.56-2.6-1.56-2.98 0a1.532 1.532 0 01-2.286.948c-1.372-.836-2.942.734-2.106 2.106.54.886.061 2.042-.947 2.287-1.561.379-1.561 2.6 0 2.978a1.532 1.532 0 01.947 2.287c-.836 1.372.734 2.942 2.106 2.106a1.532 1.532 0 012.287.947c.379 1.561 2.6 1.561 2.978 0a1.533 1.533 0 012.287-.947c1.372.836 2.942-.734 2.106-2.106a1.533 1.533 0 01.947-2.287c1.561-.379 1.561-2.6 0-2.978a1.532 1.532 0 01-.947-2.287c.836-1.372-.734-2.942-2.106-2.106a1.532 1.532 0 01-2.287-.947zM10 13a3 3 0 100-6 3 3 0 000 6z" clipRule="evenodd" />
          </svg>
        );
      default:
        return (
          <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.415-1.415L11 9.586V6z" clipRule="evenodd" />
          </svg>
        );
    }
  };

  const handleTransactionClick = (transaction) => {
    if (onTransactionSelect) {
      onTransactionSelect(transaction);
    }
  };

  const renderFilters = () => {
    if (!showFilters) return null;

    return (
      <div className="bg-white p-4 rounded-lg shadow-sm border border-gray-200 mb-4">
        <h3 className="text-sm font-semibold text-gray-800 mb-3">Filters</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
          <div>
            <label htmlFor="transaction_type" className="block text-xs font-medium text-gray-700 mb-1">
              Transaction Type
            </label>
            <select
              id="transaction_type"
              name="transaction_type"
              value={filters.transaction_type}
              onChange={handleFilterChange}
              className="w-full px-2 py-1 text-sm border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="">All Types</option>
              <option value="creation">Creation</option>
              <option value="transfer">Transfer</option>
              <option value="consumption">Usage</option>
              <option value="adjustment">Adjustment</option>
            </select>
          </div>

          {!partId && (
            <div>
              <label htmlFor="part_id" className="block text-xs font-medium text-gray-700 mb-1">
                Part
              </label>
              <select
                id="part_id"
                name="part_id"
                value={filters.part_id}
                onChange={handleFilterChange}
                className="w-full px-2 py-1 text-sm border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="">All Parts</option>
                {parts.map(part => (
                  <option key={part.id} value={part.id}>
                    {part.name} ({part.part_number})
                  </option>
                ))}
              </select>
            </div>
          )}

          {!warehouseId && (
            <>
              <div>
                <label htmlFor="from_warehouse_id" className="block text-xs font-medium text-gray-700 mb-1">
                  From Warehouse
                </label>
                <select
                  id="from_warehouse_id"
                  name="from_warehouse_id"
                  value={filters.from_warehouse_id}
                  onChange={handleFilterChange}
                  className="w-full px-2 py-1 text-sm border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                >
                  <option value="">All Warehouses</option>
                  {warehouses.map(warehouse => (
                    <option key={warehouse.id} value={warehouse.id}>
                      {warehouse.name}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label htmlFor="to_warehouse_id" className="block text-xs font-medium text-gray-700 mb-1">
                  To Warehouse
                </label>
                <select
                  id="to_warehouse_id"
                  name="to_warehouse_id"
                  value={filters.to_warehouse_id}
                  onChange={handleFilterChange}
                  className="w-full px-2 py-1 text-sm border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                >
                  <option value="">All Warehouses</option>
                  {warehouses.map(warehouse => (
                    <option key={warehouse.id} value={warehouse.id}>
                      {warehouse.name}
                    </option>
                  ))}
                </select>
              </div>
            </>
          )}

          {!machineId && (
            <div>
              <label htmlFor="machine_id" className="block text-xs font-medium text-gray-700 mb-1">
                Machine
              </label>
              <select
                id="machine_id"
                name="machine_id"
                value={filters.machine_id}
                onChange={handleFilterChange}
                className="w-full px-2 py-1 text-sm border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="">All Machines</option>
                {machines.map(machine => (
                  <option key={machine.id} value={machine.id}>
                    {machine.serial_number} - {machine.model}
                  </option>
                ))}
              </select>
            </div>
          )}

          <div>
            <label htmlFor="start_date" className="block text-xs font-medium text-gray-700 mb-1">
              Start Date
            </label>
            <input
              type="date"
              id="start_date"
              name="start_date"
              value={filters.start_date}
              onChange={handleFilterChange}
              className="w-full px-2 py-1 text-sm border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
            />
          </div>

          <div>
            <label htmlFor="end_date" className="block text-xs font-medium text-gray-700 mb-1">
              End Date
            </label>
            <input
              type="date"
              id="end_date"
              name="end_date"
              value={filters.end_date}
              onChange={handleFilterChange}
              className="w-full px-2 py-1 text-sm border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
            />
          </div>

          <div>
            <label htmlFor="reference_number" className="block text-xs font-medium text-gray-700 mb-1">
              Reference Number
            </label>
            <input
              type="text"
              id="reference_number"
              name="reference_number"
              value={filters.reference_number}
              onChange={handleFilterChange}
              placeholder="Enter reference"
              className="w-full px-2 py-1 text-sm border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
            />
          </div>
        </div>

        <div className="flex justify-end space-x-2 mt-3">
          <button
            onClick={handleClearFilters}
            className="px-3 py-1 text-xs font-medium text-gray-700 bg-gray-200 rounded-md hover:bg-gray-300 focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-offset-2"
          >
            Clear
          </button>
          <button
            onClick={handleSearch}
            className="px-3 py-1 text-xs font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
          >
            Search
          </button>
        </div>
      </div>
    );
  };

  return (
    <PermissionGuard permission={PERMISSIONS.VIEW_ORG_TRANSACTIONS}>
      <div className="space-y-4">
        {renderFilters()}

        {/* Error Display */}
        {error && (
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative" role="alert">
            <strong className="font-bold">Error: </strong>
            <span className="block sm:inline">{error}</span>
          </div>
        )}

        {/* Transaction Log */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
          <div className="px-4 py-3 bg-gray-50 border-b border-gray-200">
            <h3 className="text-sm font-semibold text-gray-800">
              Transaction Audit Trail
              {transactions.length > 0 && (
                <span className="ml-2 text-xs text-gray-500">
                  ({transactions.length} {transactions.length === 1 ? 'transaction' : 'transactions'})
                </span>
              )}
            </h3>
          </div>

          <div style={{ maxHeight }} className="overflow-y-auto">
            {loading && transactions.length === 0 ? (
              <div className="p-6 text-center text-gray-500">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-2"></div>
                Loading transactions...
              </div>
            ) : transactions.length === 0 ? (
              <div className="p-6 text-center text-gray-500">
                <svg className="w-12 h-12 mx-auto mb-2 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
                No transactions found.
              </div>
            ) : (
              <div className="divide-y divide-gray-200">
                {transactions.map((transaction) => (
                  <div
                    key={transaction.id}
                    className={`p-4 hover:bg-gray-50 transition-colors ${onTransactionSelect ? 'cursor-pointer' : ''
                      }`}
                    onClick={() => handleTransactionClick(transaction)}
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex items-start space-x-3">
                        <div className={`flex-shrink-0 p-2 rounded-full ${getTransactionTypeColor(transaction.transaction_type)}`}>
                          {getTransactionIcon(transaction.transaction_type)}
                        </div>

                        <div className="flex-1 min-w-0">
                          <div className="flex items-center space-x-2 mb-1">
                            <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getTransactionTypeColor(transaction.transaction_type)}`}>
                              {getTransactionTypeLabel(transaction.transaction_type)}
                            </span>
                            <span className="text-sm font-medium text-gray-900">
                              {transaction.part_name}
                            </span>
                            <span className="text-sm text-gray-500">
                              ({transaction.part_number})
                            </span>
                          </div>

                          <div className="text-sm text-gray-600 mb-2">
                            <span className="font-medium">
                              {transaction.quantity} {transaction.unit_of_measure}
                            </span>
                            {transaction.from_warehouse_name && (
                              <span className="ml-2">
                                from <span className="font-medium">{transaction.from_warehouse_name}</span>
                              </span>
                            )}
                            {transaction.to_warehouse_name && (
                              <span className="ml-2">
                                to <span className="font-medium">{transaction.to_warehouse_name}</span>
                              </span>
                            )}
                            {transaction.machine_serial_number && (
                              <span className="ml-2">
                                for machine <span className="font-medium">{transaction.machine_serial_number}</span>
                              </span>
                            )}
                          </div>

                          <div className="flex items-center space-x-4 text-xs text-gray-500">
                            <span>{formatDate(transaction.transaction_date)}</span>
                            <span>by {transaction.performed_by_username}</span>
                            {transaction.reference_number && (
                              <span>ref: {transaction.reference_number}</span>
                            )}
                          </div>

                          {transaction.notes && (
                            <div className="mt-2 text-sm text-gray-600 italic">
                              "{transaction.notes}"
                            </div>
                          )}
                        </div>
                      </div>

                      {onTransactionSelect && (
                        <div className="flex-shrink-0 ml-4">
                          <svg className="w-5 h-5 text-gray-400" fill="currentColor" viewBox="0 0 20 20">
                            <path fillRule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clipRule="evenodd" />
                          </svg>
                        </div>
                      )}
                    </div>
                  </div>
                ))}
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
                <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600 mx-auto mb-2"></div>
                Loading more transactions...
              </div>
            )}
          </div>
        </div>
      </div>
    </PermissionGuard>
  );
};

export default InventoryTransactionLog;