// frontend/src/components/WarehouseInventoryAggregationView.js

import React, { useState, useEffect } from 'react';
import { inventoryService } from '../services/inventoryService';
import { warehouseService } from '../services/warehouseService';
import { partsService } from '../services/partsService';
import { useAuth } from '../AuthContext';

const WarehouseInventoryAggregationView = ({ organizationId }) => {
  const { user } = useAuth();
  const [aggregatedInventory, setAggregatedInventory] = useState([]);
  const [warehouses, setWarehouses] = useState([]);
  const [parts, setParts] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [searchTerm, setSearchTerm] = useState('');
  const [filterType, setFilterType] = useState('all'); // 'all', 'low_stock', 'out_of_stock'
  const [selectedPart, setSelectedPart] = useState(null);

  useEffect(() => {
    if (organizationId) {
      fetchData();
    }
  }, [organizationId]);

  const fetchData = async () => {
    setLoading(true);
    setError('');
    try {
      const [aggregatedData, warehousesData, partsData] = await Promise.all([
        inventoryService.getOrganizationInventoryAggregation(organizationId),
        warehouseService.getOrganizationWarehouses(organizationId),
        partsService.getParts({ limit: 200 })
      ]);

      setAggregatedInventory(aggregatedData);
      setWarehouses(warehousesData);
      setParts(partsData);
    } catch (err) {
      setError('Failed to fetch aggregated inventory data');
      console.error('Failed to fetch aggregated inventory:', err);
    } finally {
      setLoading(false);
    }
  };

  const getPartDetails = (partId) => {
    return parts.find(p => p.id === partId) || {};
  };

  const getWarehouseName = (warehouseId) => {
    const warehouse = warehouses.find(w => w.id === warehouseId);
    return warehouse ? warehouse.name : 'Unknown Warehouse';
  };

  const filteredInventory = aggregatedInventory.filter(item => {
    const part = getPartDetails(item.part_id);
    const matchesSearch = !searchTerm ||
      part.name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      part.part_number?.toLowerCase().includes(searchTerm.toLowerCase());

    const totalStock = item.total_stock || 0;
    const minStock = item.min_stock_recommendation || 0;

    const matchesFilter = filterType === 'all' ||
      (filterType === 'low_stock' && totalStock <= minStock && totalStock > 0) ||
      (filterType === 'out_of_stock' && totalStock === 0);

    return matchesSearch && matchesFilter;
  });

  const getStockStatus = (totalStock, minStock) => {
    const total = parseFloat(totalStock || 0);
    const minimum = parseFloat(minStock || 0);

    if (total === 0) {
      return { status: 'out_of_stock', color: 'text-red-600', bg: 'bg-red-100' };
    } else if (total <= minimum) {
      return { status: 'low_stock', color: 'text-orange-600', bg: 'bg-orange-100' };
    } else {
      return { status: 'in_stock', color: 'text-green-600', bg: 'bg-green-100' };
    }
  };

  const getStockStatusLabel = (status) => {
    switch (status) {
      case 'out_of_stock': return 'Out of Stock';
      case 'low_stock': return 'Low Stock';
      case 'in_stock': return 'In Stock';
      default: return 'Unknown';
    }
  };

  const showPartDetails = (item) => {
    setSelectedPart(item);
  };

  const closePartDetails = () => {
    setSelectedPart(null);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="text-gray-500">Loading aggregated inventory...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
        {error}
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex justify-between items-center">
        <h3 className="text-lg font-medium text-gray-900">
          Aggregated Inventory Across All Warehouses
        </h3>
        <div className="text-sm text-gray-500">
          {filteredInventory.length} parts
        </div>
      </div>

      {/* Filters */}
      <div className="flex flex-col sm:flex-row gap-4">
        <div className="flex-1">
          <input
            type="text"
            placeholder="Search parts..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>

        <div>
          <select
            value={filterType}
            onChange={(e) => setFilterType(e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="all">All Items</option>
            <option value="low_stock">Low Stock</option>
            <option value="out_of_stock">Out of Stock</option>
          </select>
        </div>
      </div>

      {/* Inventory Table */}
      {filteredInventory.length === 0 ? (
        <div className="bg-gray-50 p-8 rounded-lg text-center">
          <div className="text-gray-500">
            {searchTerm || filterType !== 'all'
              ? 'No inventory items match your filters.'
              : 'No inventory items found.'}
          </div>
        </div>
      ) : (
        <div className="bg-white shadow overflow-hidden sm:rounded-md">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Part
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Total Stock
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Min. Stock
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Status
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Warehouses
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {filteredInventory.map((item) => {
                const part = getPartDetails(item.part_id);
                const stockStatus = getStockStatus(item.total_stock, item.min_stock_recommendation);

                return (
                  <tr key={item.part_id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div>
                        <div className="text-sm font-medium text-gray-900">
                          {part.name || 'Unknown Part'}
                        </div>
                        <div className="text-sm text-gray-500">
                          {part.part_number}
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm font-medium text-gray-900">
                        {parseFloat(item.total_stock || 0).toLocaleString()}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-900">
                        {parseFloat(item.min_stock_recommendation || 0).toLocaleString()}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${stockStatus.bg} ${stockStatus.color}`}>
                        {getStockStatusLabel(stockStatus.status)}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-900">
                        {item.warehouse_count} warehouse{item.warehouse_count !== 1 ? 's' : ''}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                      <button
                        onClick={() => showPartDetails(item)}
                        className="text-blue-600 hover:text-blue-900"
                      >
                        View Details
                      </button>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}

      {/* Summary Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mt-6">
        <div className="bg-white p-4 rounded-lg border border-gray-200">
          <div className="text-sm font-medium text-gray-500">Total Parts</div>
          <div className="text-2xl font-bold text-gray-900">
            {aggregatedInventory.length}
          </div>
        </div>

        <div className="bg-white p-4 rounded-lg border border-gray-200">
          <div className="text-sm font-medium text-gray-500">Total Warehouses</div>
          <div className="text-2xl font-bold text-blue-600">
            {warehouses.length}
          </div>
        </div>

        <div className="bg-white p-4 rounded-lg border border-gray-200">
          <div className="text-sm font-medium text-gray-500">Low Stock Items</div>
          <div className="text-2xl font-bold text-orange-600">
            {aggregatedInventory.filter(item => {
              const total = parseFloat(item.total_stock || 0);
              const min = parseFloat(item.min_stock_recommendation || 0);
              return total <= min && total > 0;
            }).length}
          </div>
        </div>

        <div className="bg-white p-4 rounded-lg border border-gray-200">
          <div className="text-sm font-medium text-gray-500">Out of Stock</div>
          <div className="text-2xl font-bold text-red-600">
            {aggregatedInventory.filter(item => parseFloat(item.total_stock || 0) === 0).length}
          </div>
        </div>
      </div>

      {/* Part Details Modal */}
      {selectedPart && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
          <div className="relative top-20 mx-auto p-5 border w-11/12 md:w-3/4 lg:w-1/2 shadow-lg rounded-md bg-white">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-medium text-gray-900">
                Part Details: {getPartDetails(selectedPart.part_id).name}
              </h3>
              <button
                onClick={closePartDetails}
                className="text-gray-400 hover:text-gray-600"
              >
                <span className="sr-only">Close</span>
                <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>

            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <span className="text-sm font-medium text-gray-500">Part Number:</span>
                  <p className="text-sm text-gray-900">{getPartDetails(selectedPart.part_id).part_number}</p>
                </div>
                <div>
                  <span className="text-sm font-medium text-gray-500">Unit of Measure:</span>
                  <p className="text-sm text-gray-900">{getPartDetails(selectedPart.part_id).unit_of_measure}</p>
                </div>
              </div>

              <div>
                <h4 className="text-md font-medium text-gray-900 mb-2">Warehouse Breakdown</h4>
                <div className="bg-gray-50 rounded-lg p-4">
                  {selectedPart.warehouse_details && selectedPart.warehouse_details.length > 0 ? (
                    <div className="space-y-2">
                      {selectedPart.warehouse_details.map((detail, index) => (
                        <div key={index} className="flex justify-between items-center">
                          <span className="text-sm text-gray-700">
                            {getWarehouseName(detail.warehouse_id)}
                          </span>
                          <span className="text-sm font-medium text-gray-900">
                            {parseFloat(detail.current_stock).toLocaleString()} {getPartDetails(selectedPart.part_id).unit_of_measure}
                          </span>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <p className="text-sm text-gray-500">No warehouse details available</p>
                  )}
                </div>
              </div>
            </div>

            <div className="mt-6 flex justify-end">
              <button
                onClick={closePartDetails}
                className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 border border-gray-300 rounded-md hover:bg-gray-200"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default WarehouseInventoryAggregationView;