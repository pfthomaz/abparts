// frontend/src/components/SuperAdminPartsManager.js

import React, { useState, useEffect } from 'react';
import { useAuth } from '../AuthContext';
import { partsService } from '../services/partsService';
import { warehouseService } from '../services/warehouseService';
import { warehouseLocationsService } from '../services/warehouseLocationsService';
import { api } from '../services/api';
import { isSuperAdmin } from '../utils/permissions';
import { formatNumber, getTranslatedUnit } from '../utils';
import { useTranslation } from '../hooks/useTranslation';
import Modal from './Modal';
import PartForm from './PartForm';
import MultilingualPartName from './MultilingualPartName';
import PartCategoryBadge, { PartCategoryFilter } from './PartCategoryBadge';

/**
 * SuperAdminPartsManager - Enhanced parts management interface for superadmin users
 * Provides advanced parts management capabilities including bulk operations,
 * advanced filtering, and comprehensive part analytics
 */
const SuperAdminPartsManager = () => {
  const { user } = useAuth();
  const { t } = useTranslation();

  // Check if user is superadmin - do this check first before any hooks
  const isUserSuperAdmin = isSuperAdmin(user);

  // All hooks must be called unconditionally
  const [parts, setParts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showModal, setShowModal] = useState(false);
  const [editingPart, setEditingPart] = useState(null);
  const [selectedParts, setSelectedParts] = useState([]);
  const [bulkAction, setBulkAction] = useState('');
  const [showBulkModal, setShowBulkModal] = useState(false);

  // Enhanced filtering state
  const [filters, setFilters] = useState({
    search: '',
    partType: 'all',
    proprietary: 'all',
    manufacturer: 'all',
    autobossVersion: 'all',
    hasImages: 'all',
    stockStatus: 'all'
  });

  // Label printing modal state
  const [showLabelModal, setShowLabelModal] = useState(false);
  const [labelQuantities, setLabelQuantities] = useState({});
  const [labelLoading, setLabelLoading] = useState(false);
  const [labelWarehouses, setLabelWarehouses] = useState([]);
  const [labelLocations, setLabelLocations] = useState([]);
  const [selectedWarehouse, setSelectedWarehouse] = useState('');
  const [selectedLocation, setSelectedLocation] = useState('');
  const [locationParts, setLocationParts] = useState(null); // null = show all parts
  const [partStockMap, setPartStockMap] = useState({}); // part_id -> stock quantity

  // Sorting and pagination
  const [sortBy, setSortBy] = useState('name');
  const [sortOrder, setSortOrder] = useState('asc');
  const [currentPage, setCurrentPage] = useState(1);
  const [itemsPerPage] = useState(20);

  // Analytics data
  const [analytics, setAnalytics] = useState({
    totalParts: 0,
    consumableParts: 0,
    bulkMaterialParts: 0,
    proprietaryParts: 0,
    partsWithImages: 0,
    partsWithoutImages: 0,
    manufacturerCount: 0
  });

  // Fetch parts data
  const fetchParts = async () => {
    if (!isUserSuperAdmin) return;

    // console.log('SuperAdminPartsManager: fetchParts called');
    setLoading(true);
    setError(null);

    try {
      // Fetch ALL parts for SuperAdmin interface (use max API limit)
      // console.log('SuperAdminPartsManager: Calling partsService.getPartsWithInventory...');
      const response = await partsService.getPartsWithInventory({ limit: 1000 });
      // console.log('SuperAdminPartsManager: Fetched parts response:', response); // Debug log

      // Handle the new response format
      const partsData = response.items || response;
      const totalCount = response.total_count || partsData.length;

      // console.log(`SuperAdminPartsManager: Setting ${partsData.length} parts in state`);
      setParts(partsData);
      calculateAnalytics(partsData, totalCount);
      
      // console.log('SuperAdminPartsManager: fetchParts completed successfully');
    } catch (err) {
      console.error('SuperAdminPartsManager: Error fetching parts:', err); // Debug log
      setError(err.message || 'Failed to fetch parts');
    } finally {
      setLoading(false);
    }
  };

  // Calculate analytics from parts data
  const calculateAnalytics = (partsData, totalCount = null) => {
    const manufacturers = new Set();
    let consumableCount = 0;
    let bulkMaterialCount = 0;
    let proprietaryCount = 0;
    let withImagesCount = 0;

    partsData.forEach(part => {
      if (part.part_type === 'consumable') consumableCount++;
      if (part.part_type === 'bulk_material') bulkMaterialCount++;
      if (part.is_proprietary) proprietaryCount++;
      if (part.image_urls && part.image_urls.length > 0) withImagesCount++;
      if (part.manufacturer) manufacturers.add(part.manufacturer);
    });

    // Use the actual total count from the API if available
    const actualTotalParts = totalCount !== null ? totalCount : partsData.length;

    setAnalytics({
      totalParts: actualTotalParts,
      consumableParts: consumableCount,
      bulkMaterialParts: bulkMaterialCount,
      proprietaryParts: proprietaryCount,
      partsWithImages: withImagesCount,
      partsWithoutImages: partsData.length - withImagesCount, // This is based on visible parts only
      manufacturerCount: manufacturers.size
    });
  };

  useEffect(() => {
    if (isUserSuperAdmin) {
      fetchParts();
    }
  }, [isUserSuperAdmin]);

  // Filter and sort parts
  const filteredAndSortedParts = React.useMemo(() => {
    if (!isUserSuperAdmin) return [];

    let filtered = parts.filter(part => {
      // Search filter
      if (filters.search) {
        const searchTerm = filters.search.toLowerCase();
        const matchesSearch =
          part.name.toLowerCase().includes(searchTerm) ||
          part.part_number.toLowerCase().includes(searchTerm) ||
          (part.description && part.description.toLowerCase().includes(searchTerm)) ||
          (part.manufacturer && part.manufacturer.toLowerCase().includes(searchTerm)) ||
          (part.part_code && part.part_code.toLowerCase().includes(searchTerm));

        if (!matchesSearch) return false;
      }

      // Part type filter
      if (filters.partType !== 'all' && part.part_type !== filters.partType) {
        return false;
      }

      // Proprietary filter
      if (filters.proprietary !== 'all') {
        const isProprietary = filters.proprietary === 'yes';
        if (part.is_proprietary !== isProprietary) return false;
      }

      // Manufacturer filter
      if (filters.manufacturer !== 'all' && part.manufacturer !== filters.manufacturer) {
        return false;
      }

      // AutoBoss Version filter
      if (filters.autobossVersion !== 'all') {
        const partVersion = part.autoboss_version || 'V3/V4';
        if (partVersion !== filters.autobossVersion) return false;
      }

      // Images filter
      if (filters.hasImages !== 'all') {
        const hasImages = part.image_urls && part.image_urls.length > 0;
        const shouldHaveImages = filters.hasImages === 'yes';
        if (hasImages !== shouldHaveImages) return false;
      }

      // Stock status filter
      if (filters.stockStatus !== 'all') {
        const isLowStock = part.is_low_stock;
        const shouldBeLowStock = filters.stockStatus === 'low';
        if (isLowStock !== shouldBeLowStock) return false;
      }

      return true;
    });

    // Sort filtered results
    filtered.sort((a, b) => {
      let aValue = a[sortBy];
      let bValue = b[sortBy];

      // Handle special sorting cases
      if (sortBy === 'name') {
        // For multilingual names, use the first part for sorting
        aValue = (aValue || '').split('|')[0].trim();
        bValue = (bValue || '').split('|')[0].trim();
      }

      if (typeof aValue === 'string') {
        aValue = aValue.toLowerCase();
        bValue = (bValue || '').toLowerCase();
      }

      if (aValue < bValue) return sortOrder === 'asc' ? -1 : 1;
      if (aValue > bValue) return sortOrder === 'asc' ? 1 : -1;
      return 0;
    });

    return filtered;
  }, [parts, filters, sortBy, sortOrder, isUserSuperAdmin]);

  // Pagination
  const totalPages = Math.ceil(filteredAndSortedParts.length / itemsPerPage);
  const paginatedParts = filteredAndSortedParts.slice(
    (currentPage - 1) * itemsPerPage,
    currentPage * itemsPerPage
  );

  // Get unique manufacturers for filter dropdown
  const manufacturers = React.useMemo(() => {
    if (!isUserSuperAdmin) return [];

    const manufacturerSet = new Set();
    parts.forEach(part => {
      if (part.manufacturer) manufacturerSet.add(part.manufacturer);
    });
    return Array.from(manufacturerSet).sort();
  }, [parts, isUserSuperAdmin]);

  // Handle part selection
  const handlePartSelection = (partId, isSelected) => {
    if (isSelected) {
      setSelectedParts(prev => [...prev, partId]);
    } else {
      setSelectedParts(prev => prev.filter(id => id !== partId));
    }
  };

  // Handle select all
  const handleSelectAll = (isSelected) => {
    if (isSelected) {
      setSelectedParts(paginatedParts.map(part => part.id));
    } else {
      setSelectedParts([]);
    }
  };

  // Handle bulk actions
  const handleBulkAction = async (action) => {
    if (selectedParts.length === 0) return;

    setBulkAction(action);
    setShowBulkModal(true);
  };

  // Execute bulk action
  const executeBulkAction = async () => {
    try {
      switch (bulkAction) {
        case 'delete':
          await Promise.all(selectedParts.map(id => partsService.deletePart(id)));
          break;
        case 'toggle_proprietary':
          // This would need a bulk update endpoint
          // console.log('Bulk toggle proprietary for:', selectedParts);
          break;
        case 'export':
          // Export selected parts
          // console.log('Export parts:', selectedParts);
          break;
        default:
          break;
      }

      await fetchParts();
      setSelectedParts([]);
      setShowBulkModal(false);
    } catch (err) {
      setError(err.message || 'Bulk action failed');
    }
  };

  // Handle part CRUD operations
  const handleCreateOrUpdate = async (partData) => {
    try {
      // console.log('SuperAdminPartsManager: Submitting part data:', partData); // Debug log
      // console.log('SuperAdminPartsManager: Image URLs in part data:', partData.image_urls); // Debug log

      let result;
      if (editingPart) {
        // console.log('SuperAdminPartsManager: Updating existing part:', editingPart.id);
        result = await partsService.updatePart(editingPart.id, partData);
        // console.log('SuperAdminPartsManager: Part updated successfully:', result);
      } else {
        // console.log('SuperAdminPartsManager: Creating new part');
        result = await partsService.createPart(partData);
        // console.log('SuperAdminPartsManager: Part created successfully:', result);
      }

      // Small delay to ensure backend processing is complete
      await new Promise(resolve => setTimeout(resolve, 500));

      // console.log('SuperAdminPartsManager: Refreshing parts list...');

      // Reset filters first to ensure new part is visible
      setFilters({
        search: '',
        partType: 'all',
        proprietary: 'all',
        manufacturer: 'all',
        autobossVersion: 'all',
        hasImages: 'all',
        stockStatus: 'all'
      });

      // Reset to first page
      setCurrentPage(1);

      // Clear current parts to force a fresh load
      setParts([]);

      // Force refresh the parts data with a fresh API call
      await fetchParts();

      // console.log('SuperAdminPartsManager: Parts list refreshed, closing modal');

      setShowModal(false);
      setEditingPart(null);

      // Show success message (you can replace this with a proper toast notification)
      alert(`Part ${editingPart ? 'updated' : 'created'} successfully!`);
      
    } catch (err) {
      console.error('SuperAdminPartsManager: Error in handleCreateOrUpdate:', err);
      throw err; // Re-throw to be handled by form
    }
  };

  const handleDelete = async (partId) => {
    if (!window.confirm("Are you sure you want to delete this part?")) return;

    try {
      await partsService.deletePart(partId);
      await fetchParts();
    } catch (err) {
      setError(err.message || 'Failed to delete part');
    }
  };

  // Early return for non-superadmin users after all hooks have been called
  if (!isUserSuperAdmin) {
    return (
      <div className="text-center py-8">
        <div className="text-red-600 text-lg font-semibold">Access Denied</div>
        <p className="text-gray-600 mt-2">This interface is only available to super administrators.</p>
      </div>
    );
  }

  // Compute which parts to display in the label modal (with stock info)
  const displayedLabelParts = locationParts
    ? locationParts.map(lp => ({ id: lp.part_id, name: lp.part_name, part_number: lp.sku, stock: lp.quantity }))
    : parts.map(p => ({ ...p, stock: partStockMap[p.id] || 0 }));

  return (
    <div className="superadmin-parts-manager">
      {/* Header */}
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-3xl font-bold text-gray-800">Parts Management</h1>
          <p className="text-gray-600 mt-1">Super Administrator Interface</p>
        </div>
        <div className="flex gap-2">
          <button
            onClick={async () => {
              // Initialize quantities: 1 for each part
              const initialQty = {};
              parts.forEach(p => { initialQty[p.id] = 1; });
              setLabelQuantities(initialQty);
              setSelectedWarehouse('');
              setSelectedLocation('');
              setLabelLocations([]);
              setLocationParts(null);
              setPartStockMap({});
              setShowLabelModal(true);
              // Load warehouses for location filter
              try {
                const wh = await warehouseService.getWarehouses();
                setLabelWarehouses(wh || []);
                // Auto-load inventory for first warehouse to show stock
                if (wh && wh.length > 0) {
                  const inv = await api.get(`/inventory/warehouse/${wh[0].id}?limit=500`);
                  const stockMap = {};
                  (inv || []).forEach(item => {
                    stockMap[item.part_id] = (stockMap[item.part_id] || 0) + Number(item.current_stock || 0);
                  });
                  setPartStockMap(stockMap);
                }
              } catch (e) {
                console.error('Failed to load warehouses:', e);
              }
            }}
            className="bg-green-600 text-white py-2 px-4 rounded-md hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2 transition duration-150 ease-in-out font-semibold"
          >
            🏷️ Print Labels
          </button>
          <button
            onClick={() => {
              setEditingPart(null);
              setShowModal(true);
            }}
            className="bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition duration-150 ease-in-out font-semibold"
          >
            Add New Part
          </button>
        </div>
      </div>

      {/* Analytics Dashboard */}
      <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-7 gap-4 mb-6">
        <div className="bg-white p-4 rounded-lg shadow border">
          <div className="text-2xl font-bold text-blue-600">{analytics.totalParts}</div>
          <div className="text-sm text-gray-600">Total Parts</div>
        </div>
        <div className="bg-white p-4 rounded-lg shadow border">
          <div className="text-2xl font-bold text-green-600">{analytics.consumableParts}</div>
          <div className="text-sm text-gray-600">Consumable</div>
        </div>
        <div className="bg-white p-4 rounded-lg shadow border">
          <div className="text-2xl font-bold text-yellow-600">{analytics.bulkMaterialParts}</div>
          <div className="text-sm text-gray-600">Bulk Material</div>
        </div>
        <div className="bg-white p-4 rounded-lg shadow border">
          <div className="text-2xl font-bold text-purple-600">{analytics.proprietaryParts}</div>
          <div className="text-sm text-gray-600">Proprietary</div>
        </div>
        <div className="bg-white p-4 rounded-lg shadow border">
          <div className="text-2xl font-bold text-indigo-600">{analytics.partsWithImages}</div>
          <div className="text-sm text-gray-600">With Images</div>
        </div>
        <div className="bg-white p-4 rounded-lg shadow border">
          <div className="text-2xl font-bold text-red-600">{analytics.partsWithoutImages}</div>
          <div className="text-sm text-gray-600">No Images</div>
        </div>
        <div className="bg-white p-4 rounded-lg shadow border">
          <div className="text-2xl font-bold text-gray-600">{analytics.manufacturerCount}</div>
          <div className="text-sm text-gray-600">Manufacturers</div>
        </div>
      </div>

      {/* Advanced Filters */}
      <div className="bg-white p-6 rounded-lg shadow-md mb-6">
        <h3 className="text-lg font-semibold text-gray-800 mb-4">Advanced Filters</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-7 gap-4">
          {/* Search */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Search</label>
            <input
              type="text"
              placeholder="Name, number, description..."
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500 text-sm"
              value={filters.search}
              onChange={(e) => setFilters(prev => ({ ...prev, search: e.target.value }))}
            />
          </div>

          {/* Part Type */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Category</label>
            <PartCategoryFilter
              value={filters.partType}
              onChange={(value) => setFilters(prev => ({ ...prev, partType: value }))}
              showAll={true}
              className="text-sm"
            />
          </div>

          {/* Proprietary */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Proprietary</label>
            <select
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500 text-sm"
              value={filters.proprietary}
              onChange={(e) => setFilters(prev => ({ ...prev, proprietary: e.target.value }))}
            >
              <option value="all">All</option>
              <option value="yes">Yes</option>
              <option value="no">No</option>
            </select>
          </div>

          {/* Manufacturer */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Manufacturer</label>
            <select
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500 text-sm"
              value={filters.manufacturer}
              onChange={(e) => setFilters(prev => ({ ...prev, manufacturer: e.target.value }))}
            >
              <option value="all">All Manufacturers</option>
              {manufacturers.map(manufacturer => (
                <option key={manufacturer} value={manufacturer}>{manufacturer}</option>
              ))}
            </select>
          </div>

          {/* AutoBoss Version */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">AutoBoss Version</label>
            <select
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500 text-sm"
              value={filters.autobossVersion}
              onChange={(e) => setFilters(prev => ({ ...prev, autobossVersion: e.target.value }))}
            >
              <option value="all">All</option>
              <option value="V3">V3</option>
              <option value="V4">V4</option>
              <option value="V3/V4">V3/V4</option>
            </select>
          </div>

          {/* Has Images */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Images</label>
            <select
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500 text-sm"
              value={filters.hasImages}
              onChange={(e) => setFilters(prev => ({ ...prev, hasImages: e.target.value }))}
            >
              <option value="all">All</option>
              <option value="yes">With Images</option>
              <option value="no">No Images</option>
            </select>
          </div>

          {/* Stock Status */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Stock Status</label>
            <select
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500 text-sm"
              value={filters.stockStatus}
              onChange={(e) => setFilters(prev => ({ ...prev, stockStatus: e.target.value }))}
            >
              <option value="all">All</option>
              <option value="low">Low Stock</option>
              <option value="normal">Normal Stock</option>
            </select>
          </div>
        </div>

        {/* Clear Filters */}
        <div className="mt-4">
          <button
            onClick={() => setFilters({
              search: '',
              partType: 'all',
              proprietary: 'all',
              manufacturer: 'all',
              autobossVersion: 'all',
              hasImages: 'all',
              stockStatus: 'all'
            })}
            className="text-sm text-blue-600 hover:text-blue-800"
          >
            Clear All Filters
          </button>
        </div>
      </div>

      {/* Bulk Actions */}
      {selectedParts.length > 0 && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
          <div className="flex items-center justify-between">
            <div className="text-sm text-blue-800">
              {selectedParts.length} part{selectedParts.length !== 1 ? 's' : ''} selected
            </div>
            <div className="flex space-x-2">
              <button
                onClick={() => handleBulkAction('toggle_proprietary')}
                className="bg-blue-600 text-white px-3 py-1 rounded text-sm hover:bg-blue-700"
              >
                Toggle Proprietary
              </button>
              <button
                onClick={() => handleBulkAction('export')}
                className="bg-green-600 text-white px-3 py-1 rounded text-sm hover:bg-green-700"
              >
                Export
              </button>
              <button
                onClick={() => handleBulkAction('delete')}
                className="bg-red-600 text-white px-3 py-1 rounded text-sm hover:bg-red-700"
              >
                Delete
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Results Summary and Sorting */}
      <div className="flex justify-between items-center mb-4">
        <div className="text-sm text-gray-600">
          Showing {paginatedParts.length} of {filteredAndSortedParts.length} parts
        </div>
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-2">
            <label className="text-sm text-gray-600">Sort by:</label>
            <select
              className="px-3 py-1 border border-gray-300 rounded text-sm"
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value)}
            >
              <option value="name">Name</option>
              <option value="part_number">Part Number</option>
              <option value="part_type">Category</option>
              <option value="manufacturer">Manufacturer</option>
              <option value="created_at">Created Date</option>
            </select>
            <button
              onClick={() => setSortOrder(prev => prev === 'asc' ? 'desc' : 'asc')}
              className="px-2 py-1 border border-gray-300 rounded text-sm hover:bg-gray-50"
            >
              {sortOrder === 'asc' ? '↑' : '↓'}
            </button>
          </div>
        </div>
      </div>

      {/* Parts Table */}
      {loading ? (
        <div className="text-center py-8">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-2"></div>
          <p className="text-gray-500">Loading parts...</p>
        </div>
      ) : error ? (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
          {error}
        </div>
      ) : (
        <div className="bg-white rounded-lg shadow overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left">
                  <input
                    type="checkbox"
                    checked={selectedParts.length === paginatedParts.length && paginatedParts.length > 0}
                    onChange={(e) => handleSelectAll(e.target.checked)}
                    className="rounded border-gray-300"
                  />
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Part
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Category
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Details
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Images
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Stock
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {paginatedParts.map((part) => (
                <tr key={part.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4">
                    <input
                      type="checkbox"
                      checked={selectedParts.includes(part.id)}
                      onChange={(e) => handlePartSelection(part.id, e.target.checked)}
                      className="rounded border-gray-300"
                    />
                  </td>
                  <td className="px-6 py-4">
                    <div>
                      <MultilingualPartName
                        value={part.name}
                        isEditing={false}
                        preferredLanguage="en"
                        className="font-medium text-gray-900"
                      />
                      <div className="text-sm text-gray-500">#{part.part_number}</div>
                    </div>
                  </td>
                  <td className="px-6 py-4">
                    <PartCategoryBadge
                      partType={part.part_type}
                      isProprietaryPart={part.is_proprietary}
                      size="small"
                    />
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-900">
                    {part.manufacturer && <div>Mfg: {part.manufacturer}</div>}
                    {part.part_code && <div>Code: {part.part_code}</div>}
                    <div>Unit: {getTranslatedUnit(part.unit_of_measure, t)}</div>
                  </td>
                  <td className="px-6 py-4">
                    {part.image_urls && part.image_urls.length > 0 ? (
                      <div className="flex items-center">
                        <span className="text-green-600 text-sm">
                          {part.image_urls.length} image{part.image_urls.length !== 1 ? 's' : ''}
                        </span>
                      </div>
                    ) : (
                      <span className="text-gray-400 text-sm">No images</span>
                    )}
                  </td>
                  <td className="px-6 py-4">
                    <div className={`text-sm ${part.is_low_stock ? 'text-red-600' : 'text-green-600'}`}>
                      {formatNumber(part.total_stock || 0, part.unit_of_measure)} {getTranslatedUnit(part.unit_of_measure, t)}
                      {part.is_low_stock && <div className="text-xs text-red-500">LOW STOCK</div>}
                    </div>
                  </td>
                  <td className="px-6 py-4 text-sm font-medium">
                    <div className="flex space-x-2">
                      <button
                        onClick={() => {
                          setEditingPart(part);
                          setShowModal(true);
                        }}
                        className="text-blue-600 hover:text-blue-900"
                      >
                        Edit
                      </button>
                      <button
                        onClick={() => handleDelete(part.id)}
                        className="text-red-600 hover:text-red-900"
                      >
                        Delete
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="flex items-center justify-between mt-6">
          <div className="text-sm text-gray-700">
            Page {currentPage} of {totalPages}
          </div>
          <div className="flex space-x-2">
            <button
              onClick={() => setCurrentPage(prev => Math.max(1, prev - 1))}
              disabled={currentPage === 1}
              className="px-3 py-2 border border-gray-300 rounded-md text-sm disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50"
            >
              Previous
            </button>
            <button
              onClick={() => setCurrentPage(prev => Math.min(totalPages, prev + 1))}
              disabled={currentPage === totalPages}
              className="px-3 py-2 border border-gray-300 rounded-md text-sm disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50"
            >
              Next
            </button>
          </div>
        </div>
      )}

      {/* Part Form Modal */}
      <Modal
        isOpen={showModal}
        onClose={() => {
          setShowModal(false);
          setEditingPart(null);
        }}
        title={editingPart ? "Edit Part" : "Add New Part"}
        size="large"
      >
        <PartForm
          initialData={editingPart || {}}
          onSubmit={handleCreateOrUpdate}
          onClose={() => {
            setShowModal(false);
            setEditingPart(null);
          }}
        />
      </Modal>

      {/* Bulk Action Confirmation Modal */}
      <Modal
        isOpen={showBulkModal}
        onClose={() => setShowBulkModal(false)}
        title="Confirm Bulk Action"
      >
        <div className="p-4">
          <p className="text-gray-700 mb-4">
            Are you sure you want to {bulkAction.replace('_', ' ')} {selectedParts.length} selected part{selectedParts.length !== 1 ? 's' : ''}?
          </p>
          <div className="flex justify-end space-x-3">
            <button
              onClick={() => setShowBulkModal(false)}
              className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-200 rounded-md hover:bg-gray-300"
            >
              Cancel
            </button>
            <button
              onClick={executeBulkAction}
              className="px-4 py-2 text-sm font-medium text-white bg-red-600 rounded-md hover:bg-red-700"
            >
              Confirm
            </button>
          </div>
        </div>
      </Modal>

      {/* Print Labels Modal */}
      <Modal
        isOpen={showLabelModal}
        onClose={() => setShowLabelModal(false)}
        title="🏷️ Print Part Labels"
        size="large"
      >
        <div className="space-y-4">
          <p className="text-sm text-gray-600">
            Set the number of labels to print for each part. Parts with 0 labels will be skipped.
          </p>

          {/* Location filter */}
          {labelWarehouses.length > 0 && (
            <div className="flex gap-2 items-end flex-wrap">
              <div className="flex-1 min-w-[140px]">
                <label className="block text-xs font-medium text-gray-600 mb-1">Warehouse</label>
                <select
                  value={selectedWarehouse}
                  onChange={async (e) => {
                    const whId = e.target.value;
                    setSelectedWarehouse(whId);
                    setSelectedLocation('');
                    setLocationParts(null);
                    if (whId) {
                      try {
                        const locs = await warehouseLocationsService.getLocations(whId);
                        setLabelLocations(locs || []);
                        // Fetch inventory for this warehouse to show stock
                        const inv = await api.get(`/inventory/warehouse/${whId}?limit=500`);
                        const stockMap = {};
                        (inv || []).forEach(item => {
                          stockMap[item.part_id] = (stockMap[item.part_id] || 0) + Number(item.current_stock || 0);
                        });
                        setPartStockMap(stockMap);
                      } catch (err) {
                        setLabelLocations([]);
                      }
                    } else {
                      setLabelLocations([]);
                      // Reload stock for first warehouse
                      if (labelWarehouses.length > 0) {
                        try {
                          const inv = await api.get(`/inventory/warehouse/${labelWarehouses[0].id}?limit=500`);
                          const stockMap = {};
                          (inv || []).forEach(item => {
                            stockMap[item.part_id] = (stockMap[item.part_id] || 0) + Number(item.current_stock || 0);
                          });
                          setPartStockMap(stockMap);
                        } catch (err) { /* ignore */ }
                      }
                    }
                    // Reset quantities to all parts = 1
                    const initialQty = {};
                    parts.forEach(p => { initialQty[p.id] = 1; });
                    setLabelQuantities(initialQty);
                  }}
                  className="w-full px-2 py-1.5 text-sm border border-gray-300 rounded-md focus:ring-2 focus:ring-green-500"
                >
                  <option value="">All parts</option>
                  {labelWarehouses.map(wh => (
                    <option key={wh.id} value={wh.id}>{wh.name}</option>
                  ))}
                </select>
              </div>
              {labelLocations.length > 0 && (
                <div className="flex-1 min-w-[140px]">
                  <label className="block text-xs font-medium text-gray-600 mb-1">Location</label>
                  <select
                    value={selectedLocation}
                    onChange={async (e) => {
                      const locId = e.target.value;
                      setSelectedLocation(locId);
                      if (locId) {
                        try {
                          const locParts = await warehouseLocationsService.getPartsAtLocation(locId);
                          setLocationParts(locParts || []);
                          // Set quantities based on location parts
                          const qty = {};
                          (locParts || []).forEach(p => { qty[p.part_id] = 1; });
                          setLabelQuantities(qty);
                        } catch (err) {
                          setLocationParts([]);
                        }
                      } else {
                        setLocationParts(null);
                        const initialQty = {};
                        parts.forEach(p => { initialQty[p.id] = 1; });
                        setLabelQuantities(initialQty);
                      }
                    }}
                    className="w-full px-2 py-1.5 text-sm border border-gray-300 rounded-md focus:ring-2 focus:ring-green-500"
                  >
                    <option value="">All locations</option>
                    {labelLocations.map(loc => (
                      <option key={loc.id} value={loc.id}>{loc.location_code}{loc.description ? ` — ${loc.description}` : ''}</option>
                    ))}
                  </select>
                </div>
              )}
            </div>
          )}

          {/* Quick actions */}
          <div className="flex gap-2 flex-wrap">
            <button
              onClick={() => {
                const q = {};
                displayedLabelParts.forEach(p => { q[p.id] = 1; });
                setLabelQuantities(q);
              }}
              className="text-xs px-2 py-1 bg-gray-100 rounded hover:bg-gray-200"
            >
              All = 1
            </button>
            <button
              onClick={() => {
                const q = {};
                displayedLabelParts.forEach(p => { q[p.id] = 0; });
                setLabelQuantities(q);
              }}
              className="text-xs px-2 py-1 bg-gray-100 rounded hover:bg-gray-200"
            >
              All = 0
            </button>
          </div>

          {/* Parts list with quantity inputs */}
          <div className="max-h-96 overflow-y-auto border rounded-lg divide-y">
            {displayedLabelParts.length === 0 ? (
              <div className="p-4 text-center text-gray-500 text-sm">No parts at this location.</div>
            ) : (
              displayedLabelParts.map(part => (
                <div key={part.id} className="flex items-center justify-between px-3 py-2 hover:bg-gray-50">
                  <div className="flex-1 min-w-0 mr-3">
                    <span className="text-sm font-medium text-gray-900 truncate block">{part.name}</span>
                    <span className="text-xs text-gray-500 font-mono">{part.part_number || part.sku}</span>
                  </div>
                  <div className="flex items-center gap-3">
                    <span className="text-xs text-gray-500 whitespace-nowrap">
                      Stock: <strong className={part.stock > 0 ? 'text-green-700' : 'text-gray-400'}>{Number(part.stock)}</strong>
                    </span>
                    <input
                      type="number"
                      min="0"
                      max="100"
                      value={labelQuantities[part.id] || 0}
                      onChange={(e) => setLabelQuantities(prev => ({
                        ...prev,
                        [part.id]: Math.max(0, parseInt(e.target.value) || 0)
                      }))}
                      className="w-16 px-2 py-1 text-center border border-gray-300 rounded-md text-sm focus:ring-2 focus:ring-green-500 focus:border-green-500"
                    />
                  </div>
                </div>
              ))
            )}
          </div>

          {/* Summary and actions */}
          <div className="flex items-center justify-between pt-2 border-t">
            <span className="text-sm text-gray-600">
              Total labels: <strong>{Object.values(labelQuantities).reduce((sum, q) => sum + q, 0)}</strong>
            </span>
            <div className="flex gap-2">
              <button
                onClick={() => setShowLabelModal(false)}
                className="px-4 py-2 text-sm text-gray-700 bg-gray-100 rounded-md hover:bg-gray-200"
              >
                Cancel
              </button>
              <button
                onClick={async () => {
                  const totalLabels = Object.values(labelQuantities).reduce((sum, q) => sum + q, 0);
                  if (totalLabels === 0) {
                    alert('Set at least 1 label to print.');
                    return;
                  }
                  // Filter out parts with 0 quantity
                  const quantities = {};
                  Object.entries(labelQuantities).forEach(([id, qty]) => {
                    if (qty > 0) quantities[id] = qty;
                  });
                  setLabelLoading(true);
                  try {
                    await partsService.generatePartLabels([], quantities);
                    setShowLabelModal(false);
                  } catch (err) {
                    console.error('Failed to generate labels:', err);
                    alert(err.message || 'Failed to generate labels');
                  } finally {
                    setLabelLoading(false);
                  }
                }}
                disabled={labelLoading}
                className="px-4 py-2 text-sm font-medium text-white bg-green-600 rounded-md hover:bg-green-700 disabled:opacity-50"
              >
                {labelLoading ? 'Generating...' : '🖨️ Print'}
              </button>
            </div>
          </div>
        </div>
      </Modal>
    </div>
  );
};

export default SuperAdminPartsManager;