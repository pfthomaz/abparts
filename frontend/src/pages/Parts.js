// frontend/src/pages/Parts.js

import React, { useState, useEffect, useCallback, useMemo } from 'react';
import { partsService } from '../services/partsService';
import { API_BASE_URL } from '../services/api';
import Modal from '../components/Modal';
import PartForm from '../components/PartForm';
import PermissionGuard from '../components/PermissionGuard';
import { PERMISSIONS } from '../utils/permissions';
import {
  formatErrorForDisplay,
  isRetryableError,
  getRetryDelay,
  MAX_RETRY_ATTEMPTS,
  USER_GUIDANCE,
  DISPLAY_CONSTANTS
} from '../utils';

const Parts = () => {
  const [parts, setParts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [retryCount, setRetryCount] = useState(0);
  const [showModal, setShowModal] = useState(false);
  const [editingPart, setEditingPart] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterProprietary, setFilterProprietary] = useState('all');
  const [filterPartType, setFilterPartType] = useState('all');

  const fetchParts = useCallback(async (isRetry = false) => {
    setLoading(true);
    if (!isRetry) {
      setError(null);
      setRetryCount(0);
    }

    try {
      const data = await partsService.getPartsWithInventory();
      setParts(data);
      setError(null);
      setRetryCount(0);
    } catch (err) {
      console.error('Error fetching parts:', err);

      // The service layer processes the error and throws a new Error with a user-friendly message
      // We need to format this for display
      const formattedError = formatErrorForDisplay(err, retryCount);
      setError(formattedError);

      if (isRetry) {
        setRetryCount(prev => prev + 1);
      }
    } finally {
      setLoading(false);
    }
  }, [retryCount]);

  useEffect(() => {
    fetchParts();
  }, [fetchParts]);

  const handleRetry = useCallback(async () => {
    if (retryCount >= MAX_RETRY_ATTEMPTS) {
      return;
    }

    // Add delay for retries to prevent overwhelming the server
    if (retryCount > 0 && error && isRetryableError(error.originalError || error)) {
      const delay = getRetryDelay(retryCount);
      await new Promise(resolve => setTimeout(resolve, delay));
    }

    await fetchParts(true);
  }, [fetchParts, retryCount, error]);

  // Enhanced error display component
  const ErrorDisplay = ({ error, onRetry, retryCount }) => {
    if (!error) return null;

    // Ensure we have a proper error message
    let errorMessage = 'An unexpected error occurred';

    if (typeof error === 'string') {
      errorMessage = error;
    } else if (error && typeof error === 'object') {
      if (error.message && typeof error.message === 'string') {
        errorMessage = error.message;
      } else if (error.toString && typeof error.toString === 'function') {
        const stringified = error.toString();
        if (stringified !== '[object Object]') {
          errorMessage = stringified;
        }
      }
    }

    const canRetry = error && error.isRetryable && retryCount < MAX_RETRY_ATTEMPTS;
    const showGuidance = error && (error.showRetryGuidance || retryCount > 2);
    const errorType = error && error.type;

    return (
      <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative mb-4" role="alert">
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <div className="flex items-center">
              <strong className="font-bold">Error: </strong>
              <span className="ml-2">{errorMessage}</span>
            </div>

            {showGuidance && (
              <div className="mt-2 text-sm">
                <p>{USER_GUIDANCE.MULTIPLE_FAILURES}</p>
                {errorType === 'network' && (
                  <p className="mt-1">{USER_GUIDANCE.NETWORK_ISSUES}</p>
                )}
                {errorType === 'server' && (
                  <p className="mt-1">{USER_GUIDANCE.SERVER_ISSUES}</p>
                )}
                {(errorType === 'auth' || errorType === 'permission') && (
                  <p className="mt-1">{USER_GUIDANCE.PERMISSION_ISSUES}</p>
                )}
              </div>
            )}

            {retryCount > 0 && (
              <p className="text-sm mt-1 text-red-600">
                Retry attempt {retryCount} of {MAX_RETRY_ATTEMPTS}
              </p>
            )}
          </div>

          {canRetry && (
            <button
              onClick={onRetry}
              disabled={loading}
              className="bg-red-600 text-white px-3 py-1 rounded text-sm hover:bg-red-700 disabled:opacity-50 disabled:cursor-not-allowed ml-4"
            >
              {loading ? 'Retrying...' : 'Retry'}
            </button>
          )}
        </div>
      </div>
    );
  };

  const filteredParts = useMemo(() => {
    return parts
      .filter(part => {
        if (!searchTerm) return true;
        const term = searchTerm.toLowerCase();
        return (
          part.name.toLowerCase().includes(term) ||
          part.part_number.toLowerCase().includes(term)
        );
      })
      .filter(part => {
        if (filterProprietary === 'all') return true;
        return part.is_proprietary === (filterProprietary === 'yes');
      })
      .filter(part => {
        if (filterPartType === 'all') return true;
        return part.part_type === filterPartType;
      });
  }, [parts, searchTerm, filterProprietary, filterPartType]);

  const handleCreateOrUpdate = async (partData) => {
    try {
      if (editingPart) {
        await partsService.updatePart(editingPart.id, partData);
      } else {
        await partsService.createPart(partData);
      }

      await fetchParts();
      setShowModal(false);
      setEditingPart(null);
    } catch (err) {
      console.error("Error creating/updating part:", err);
      // Re-throw to be caught by the form's error handling
      throw err;
    }
  };

  const handleDelete = async (partId) => {
    if (!window.confirm("Are you sure you want to delete this part?")) {
      return;
    }

    setError(null);
    try {
      await partsService.deletePart(partId);
      await fetchParts();
    } catch (err) {
      console.error('Error deleting part:', err);
      const formattedError = formatErrorForDisplay(err, 0);
      setError(formattedError);
    }
  };

  const openModal = (part = null) => {
    setEditingPart(part);
    setShowModal(true);
  };

  const closeModal = () => {
    setShowModal(false);
    setEditingPart(null);
  };

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold text-gray-800">Parts</h1>
        <PermissionGuard permission={PERMISSIONS.MANAGE_PARTS} hideIfNoPermission={true}>
          <button
            onClick={() => openModal()}
            className="bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition duration-150 ease-in-out font-semibold"
          >
            Add Part
          </button>
        </PermissionGuard>
      </div>

      {loading && (
        <div className="flex items-center justify-center py-8">
          <div className="text-gray-500">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-2"></div>
            <p>{DISPLAY_CONSTANTS.LOADING_MESSAGE}</p>
          </div>
        </div>
      )}

      <ErrorDisplay
        error={error}
        onRetry={handleRetry}
        retryCount={retryCount}
      />

      {/* Search and Filter Bar */}
      <div className="bg-white p-4 rounded-lg shadow-md mb-6">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="md:col-span-1">
            <label htmlFor="search" className="block text-sm font-medium text-gray-700">Search</label>
            <input
              type="text"
              id="search"
              placeholder="By name or number..."
              className="mt-1 w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </div>
          <div>
            <label htmlFor="filterProprietary" className="block text-sm font-medium text-gray-700">Proprietary</label>
            <select
              id="filterProprietary"
              className="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm rounded-md"
              value={filterProprietary}
              onChange={(e) => setFilterProprietary(e.target.value)}
            >
              <option value="all">All</option>
              <option value="yes">Yes</option>
              <option value="no">No</option>
            </select>
          </div>
          <div>
            <label htmlFor="filterPartType" className="block text-sm font-medium text-gray-700">Part Type</label>
            <select
              id="filterPartType"
              className="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm rounded-md"
              value={filterPartType}
              onChange={(e) => setFilterPartType(e.target.value)}
            >
              <option value="all">All Types</option>
              <option value="consumable">Consumable</option>
              <option value="bulk_material">Bulk Material</option>
            </select>
          </div>
        </div>
      </div>

      {!loading && !error && filteredParts.length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-12">
          {filteredParts.map((part) => (
            <div key={part.id} className="bg-gray-50 p-6 rounded-lg shadow-md border border-gray-200">
              <h3 className="text-2xl font-semibold text-purple-700 mb-2">{part.name}</h3>
              <p className="text-gray-600 mb-1"><span className="font-medium">Part #:</span> {part.part_number}</p>
              {part.description && <p className="text-gray-600 mb-1"><span className="font-medium">Description:</span> {part.description}</p>}
              <p className="text-gray-600 mb-1">
                <span className="font-medium">Type:</span> {part.part_type === 'consumable' ? 'Consumable' : 'Bulk Material'}
              </p>
              <p className="text-gray-600 mb-1">
                <span className="font-medium">Unit:</span> {part.unit_of_measure}
              </p>
              <p className="text-gray-600 mb-1">
                <span className="font-medium">Proprietary:</span> {part.is_proprietary ? 'Yes' : 'No'}
              </p>
              {part.manufacturer_part_number && (
                <p className="text-gray-600 mb-1">
                  <span className="font-medium">Mfg Part #:</span> {part.manufacturer_part_number}
                </p>
              )}

              {/* Inventory Information */}
              <div className="mt-3 p-3 bg-gray-100 rounded-md">
                <div className="flex justify-between items-center mb-2">
                  <span className="font-medium text-gray-700">Total Stock:</span>
                  <span className={`font-semibold ${part.is_low_stock ? 'text-red-600' : 'text-green-600'}`}>
                    {part.total_stock || 0} {part.unit_of_measure}
                    {part.is_low_stock && <span className="ml-1 text-xs">(LOW)</span>}
                  </span>
                </div>

                {part.warehouse_inventory && part.warehouse_inventory.length > 0 && (
                  <div className="space-y-1">
                    <span className="text-sm font-medium text-gray-600">By Warehouse:</span>
                    {part.warehouse_inventory.map((warehouse, idx) => (
                      <div key={idx} className="flex justify-between text-sm">
                        <span className="text-gray-600">{warehouse.warehouse_name}:</span>
                        <span className={warehouse.is_low_stock ? 'text-red-600' : 'text-gray-800'}>
                          {warehouse.current_stock} {warehouse.unit_of_measure}
                          {warehouse.is_low_stock && <span className="ml-1 text-xs">(LOW)</span>}
                        </span>
                      </div>
                    ))}
                  </div>
                )}

                {(!part.warehouse_inventory || part.warehouse_inventory.length === 0) && (
                  <p className="text-sm text-gray-500">No inventory data available</p>
                )}
              </div>

              {part.image_urls && part.image_urls.length > 0 && (
                <div className="mt-3">
                  <span className="font-medium text-gray-600">Images:</span>
                  <div className="grid grid-cols-2 gap-2 mt-1">
                    {part.image_urls.map((imageUrl, imgIndex) => (
                      <img
                        key={imgIndex}
                        src={`${API_BASE_URL}${imageUrl}`}
                        alt={`Part Image ${imgIndex + 1}`}
                        className="w-full h-24 object-cover rounded-md shadow-sm"
                        onError={(e) => {
                          e.target.onerror = null;
                          e.target.src = "https://placehold.co/100x100?text=Image+Error";
                        }}
                      />
                    ))}
                  </div>
                </div>
              )}
              <p className="text-sm text-gray-400 mt-3">ID: {part.id}</p>
              <div className="mt-4 flex space-x-2">
                <PermissionGuard permission={PERMISSIONS.MANAGE_PARTS} hideIfNoPermission={true}>
                  <button
                    onClick={() => openModal(part)}
                    className="bg-yellow-500 text-white py-1 px-3 rounded-md hover:bg-yellow-600 text-sm"
                  >
                    Edit
                  </button>
                </PermissionGuard>
                <PermissionGuard permission={PERMISSIONS.MANAGE_PARTS} hideIfNoPermission={true}>
                  <button
                    onClick={() => handleDelete(part.id)}
                    className="bg-red-500 text-white py-1 px-3 rounded-md hover:bg-red-600 text-sm"
                  >
                    Delete
                  </button>
                </PermissionGuard>
              </div>
            </div>
          ))}
        </div>
      )}

      {!loading && !error && filteredParts.length === 0 && (
        <div className="text-center py-10 bg-white rounded-lg shadow-md">
          <h3 className="text-xl font-semibold text-gray-700">{DISPLAY_CONSTANTS.EMPTY_STATE_TITLE}</h3>
          <p className="text-gray-500 mt-2">
            {parts.length > 0
              ? 'Try adjusting your search or filter criteria.'
              : DISPLAY_CONSTANTS.EMPTY_STATE_MESSAGE
            }
          </p>
          {parts.length === 0 && (
            <PermissionGuard permission={PERMISSIONS.MANAGE_PARTS} hideIfNoPermission={true}>
              <button
                onClick={() => openModal()}
                className="mt-4 bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition duration-150 ease-in-out font-semibold"
              >
                {DISPLAY_CONSTANTS.ADD_PART_BUTTON_TEXT}
              </button>
            </PermissionGuard>
          )}
        </div>
      )}

      <Modal
        show={showModal}
        onClose={closeModal}
        title={editingPart ? "Edit Part" : "Add New Part"}
      >
        <PartForm
          initialData={editingPart || {}}
          onSubmit={handleCreateOrUpdate}
          onClose={closeModal}
        />
      </Modal>
    </div>
  );
};

export default Parts;
