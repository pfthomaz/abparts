// frontend/src/components/SuperAdminPartsManager.js

import React, { useState, useEffect } from 'react';
import { useAuth } from '../AuthContext';
import { partsService } from '../services/partsService';
import { isSuperAdmin } from '../utils/permissions';
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
    hasImages: 'all',
    stockStatus: 'all'
  });

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

    setLoading(true);
    setError(null);

    try {
      // Fetch ALL parts for SuperAdmin interface (use max API limit)
      const response = await partsService.getPartsWithInventory({ limit: 1000 });
      console.log('Fetched parts response:', response); // Debug log

      // Handle the new response format
      const partsData = response.items || response;
      const totalCount = response.total_count || partsData.length;

      setParts(partsData);
      calculateAnalytics(partsData, totalCount);
    } catch (err) {
      console.error('Error fetching parts:', err); // Debug log
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
          console.log('Bulk toggle proprietary for:', selectedParts);
          break;
        case 'export':
          // Export selected parts
          console.log('Export parts:', selectedParts);
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
      if (editingPart) {
        await partsService.updatePart(editingPart.id, partData);
      } else {
        await partsService.createPart(partData);
      }

      // Small delay to ensure backend processing is complete
      await new Promise(resolve => setTimeout(resolve, 200));

      // Reset filters first to ensure new part is visible
      setFilters({
        search: '',
        partType: 'all',
        proprietary: 'all',
        manufacturer: 'all',
        hasImages: 'all',
        stockStatus: 'all'
      });

      // Reset to first page
      setCurrentPage(1);

      // Clear current parts to force a fresh load
      setParts([]);

      // Force refresh the parts data with a fresh API call
      await fetchParts();

      console.log('Parts refreshed after creation/update'); // Debug log

      setShowModal(false);
      setEditingPart(null);
    } catch (err) {
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

  return (
    <div className="superadmin-parts-manager">
      {/* Header */}
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-3xl font-bold text-gray-800">Parts Management</h1>
          <p className="text-gray-600 mt-1">Super Administrator Interface</p>
        </div>
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
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-4">
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
        <div className="bg-white rounded-lg shadow overflow-hidden">
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
                    <div>Unit: {part.unit_of_measure}</div>
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
                      {part.total_stock || 0} {part.unit_of_measure}
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
    </div>
  );
};

export default SuperAdminPartsManager;