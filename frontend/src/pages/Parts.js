// frontend/src/pages/Parts.js

import { useState, useEffect, useCallback, useMemo } from 'react';
import { partsService } from '../services/partsService';
import Modal from '../components/Modal';
import PartForm from '../components/PartForm';
import PermissionGuard from '../components/PermissionGuard';
import { PERMISSIONS, isSuperAdmin } from '../utils/permissions';
import { useAuth } from '../AuthContext';
import SuperAdminPartsManager from '../components/SuperAdminPartsManager';
import PartCard from '../components/PartCard';
import PartsSearchFilter from '../components/PartsSearchFilter';
import ProgressiveLoader from '../components/ProgressiveLoader';
import VirtualizedPartsList from '../components/VirtualizedPartsList';
import { useDebounceSearch } from '../hooks/useDebounce';
import { usePerformanceMonitor } from '../hooks/usePerformanceMonitor';
import {
  formatErrorForDisplay,
  isRetryableError,
  getRetryDelay,
  MAX_RETRY_ATTEMPTS,
  USER_GUIDANCE,
  DISPLAY_CONSTANTS
} from '../utils';

const Parts = () => {
  const { user } = useAuth();

  // Check if user is superadmin first
  const isUserSuperAdmin = isSuperAdmin(user);

  // All hooks must be called unconditionally
  const [parts, setParts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [retryCount, setRetryCount] = useState(0);
  const [showModal, setShowModal] = useState(false);
  const [editingPart, setEditingPart] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterProprietary, setFilterProprietary] = useState('all');
  const [filterPartType, setFilterPartType] = useState('all');

  // Debounced search with loading state
  const { debouncedSearchTerm, isSearching } = useDebounceSearch(searchTerm, 300);

  // Performance monitoring
  const { renderTime } = usePerformanceMonitor('Parts');

  const fetchParts = useCallback(async (isRetry = false) => {
    if (isUserSuperAdmin) return; // Don't fetch if superadmin (they use different component)

    setLoading(true);
    if (!isRetry) {
      setError(null);
      setRetryCount(0);
    }

    try {
      // Fetch more parts for better user experience (up to 1000)
      const response = await partsService.getPartsWithInventory({ limit: 1000 });
      console.log('Fetched parts response:', response); // Debug log

      // Handle the new response format
      const partsData = response.items || response;
      setParts(partsData);
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
  }, [retryCount, isUserSuperAdmin]);

  useEffect(() => {
    if (!isUserSuperAdmin) {
      fetchParts();
    }
  }, [fetchParts, isUserSuperAdmin]);

  const handleRetry = useCallback(async () => {
    if (retryCount >= MAX_RETRY_ATTEMPTS || isUserSuperAdmin) {
      return;
    }

    // Add delay for retries to prevent overwhelming the server
    if (retryCount > 0 && error && isRetryableError(error.originalError || error)) {
      const delay = getRetryDelay(retryCount);
      await new Promise(resolve => setTimeout(resolve, delay));
    }

    await fetchParts(true);
  }, [fetchParts, retryCount, error, isUserSuperAdmin]);

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

  // Optimized filtering with debounced search term
  const filteredParts = useMemo(() => {
    if (isUserSuperAdmin) return [];

    return parts
      .filter(part => {
        if (!debouncedSearchTerm) return true;
        const term = debouncedSearchTerm.toLowerCase();
        return (
          part.name.toLowerCase().includes(term) ||
          part.part_number.toLowerCase().includes(term) ||
          (part.description && part.description.toLowerCase().includes(term)) ||
          (part.manufacturer && part.manufacturer.toLowerCase().includes(term)) ||
          (part.part_code && part.part_code.toLowerCase().includes(term)) ||
          (part.manufacturer_part_number && part.manufacturer_part_number.toLowerCase().includes(term))
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
  }, [parts, debouncedSearchTerm, filterProprietary, filterPartType, isUserSuperAdmin]);

  // Use virtualized rendering for large datasets (>100 parts)
  const useVirtualization = filteredParts.length > 100;

  // Memoized handlers to prevent unnecessary re-renders
  const handleEditPart = useCallback((part) => {
    setEditingPart(part);
    setShowModal(true);
  }, []);

  const handleDeletePart = useCallback(async (partId) => {
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
  }, [fetchParts]);

  const handleSearchChange = useCallback((value) => {
    setSearchTerm(value);
  }, []);

  const handleProprietaryChange = useCallback((value) => {
    setFilterProprietary(value);
  }, []);

  const handlePartTypeChange = useCallback((value) => {
    setFilterPartType(value);
  }, []);

  const handleCreateOrUpdate = async (partData) => {
    try {
      if (editingPart) {
        await partsService.updatePart(editingPart.id, partData);
      } else {
        await partsService.createPart(partData);
      }

      // Small delay to ensure backend processing is complete
      await new Promise(resolve => setTimeout(resolve, 200));

      // Clear search and filters first to ensure new part is visible
      setSearchTerm('');
      setFilterProprietary('all');
      setFilterPartType('all');

      // Clear current parts to force a fresh load
      setParts([]);

      // Force refresh the parts data with a fresh API call
      await fetchParts();

      setShowModal(false);
      setEditingPart(null);
    } catch (err) {
      console.error("Error creating/updating part:", err);
      // Re-throw to be caught by the form's error handling
      throw err;
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

  // Show SuperAdminPartsManager for superadmin users after all hooks have been called
  if (isUserSuperAdmin) {
    return <SuperAdminPartsManager />;
  }

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

      <ProgressiveLoader
        isLoading={loading}
        isSearching={isSearching}
        totalItems={parts.length}
        displayedItems={filteredParts.length}
        itemType="parts"
      />

      <ErrorDisplay
        error={error}
        onRetry={handleRetry}
        retryCount={retryCount}
      />

      {/* Optimized Search and Filter Bar */}
      <PartsSearchFilter
        searchTerm={searchTerm}
        onSearchChange={handleSearchChange}
        filterProprietary={filterProprietary}
        onProprietaryChange={handleProprietaryChange}
        filterPartType={filterPartType}
        onPartTypeChange={handlePartTypeChange}
        isSearching={isSearching}
        resultCount={filteredParts.length}
      />

      {!loading && !error && filteredParts.length > 0 && (
        <>
          {/* Performance indicator for development */}
          {process.env.NODE_ENV === 'development' && (
            <div className="mb-4 p-2 bg-blue-50 border border-blue-200 rounded text-sm text-blue-700">
              Performance: {filteredParts.length} parts, {renderTime}ms render
              {useVirtualization && <span className="ml-2 font-semibold">(Virtualized)</span>}
            </div>
          )}

          {useVirtualization ? (
            <VirtualizedPartsList
              parts={filteredParts}
              onEdit={handleEditPart}
              onDelete={handleDeletePart}
              containerHeight={600}
              itemHeight={400}
            />
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-12">
              {filteredParts.map((part) => (
                <PartCard
                  key={part.id}
                  part={part}
                  onEdit={handleEditPart}
                  onDelete={handleDeletePart}
                />
              ))}
            </div>
          )}
        </>
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
        isOpen={showModal}
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
