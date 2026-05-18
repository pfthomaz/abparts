// frontend/src/components/BulkLocationAssign.js

import { useState, useEffect } from 'react';
import { warehouseLocationsService } from '../services/warehouseLocationsService';
import { useTranslation } from '../hooks/useTranslation';

/**
 * BulkLocationAssign component - allows assigning multiple inventory items
 * to a single warehouse location at once.
 *
 * Props:
 * - inventoryIds: Array<string> - Selected inventory item UUIDs
 * - warehouseId: string - The warehouse UUID (to fetch available locations)
 * - onSuccess: function - Callback after successful bulk assignment
 * - onCancel: function - Callback to close/cancel the bulk action
 */
const BulkLocationAssign = ({ inventoryIds = [], warehouseId, onSuccess, onCancel }) => {
  const { t } = useTranslation();
  const [locations, setLocations] = useState([]);
  const [selectedLocationId, setSelectedLocationId] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);

  // Fetch available locations for the warehouse
  useEffect(() => {
    const fetchLocations = async () => {
      if (!warehouseId) return;
      try {
        const data = await warehouseLocationsService.getLocations(warehouseId);
        setLocations(Array.isArray(data) ? data : []);
      } catch (err) {
        console.error('Error fetching locations:', err);
        setError(t('warehouseLocations.errorLoadingLocations') || 'Failed to load locations');
      }
    };
    fetchLocations();
  }, [warehouseId, t]);

  const handleBulkAssign = async () => {
    if (!selectedLocationId || inventoryIds.length === 0) return;

    setLoading(true);
    setError(null);
    setSuccess(false);

    try {
      await warehouseLocationsService.assignParts(selectedLocationId, inventoryIds);
      setSuccess(true);

      if (onSuccess) {
        const assignedLocation = locations.find(loc => loc.id === selectedLocationId);
        onSuccess(assignedLocation, inventoryIds);
      }
    } catch (err) {
      console.error('Error bulk assigning:', err);
      setError(err.message || t('warehouseLocations.errorBulkAssign') || 'Failed to assign parts to location');
    } finally {
      setLoading(false);
    }
  };

  if (inventoryIds.length === 0) {
    return (
      <div className="p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
        <p className="text-sm text-yellow-700">
          {t('warehouseLocations.noPartsSelected') || 'No parts selected. Select parts to assign them to a location.'}
        </p>
      </div>
    );
  }

  return (
    <div className="p-4 bg-white border border-gray-200 rounded-lg shadow-sm">
      <div className="flex items-center justify-between mb-3">
        <h4 className="text-sm font-semibold text-gray-900">
          {t('warehouseLocations.bulkAssignTitle') || 'Bulk Assign Location'}
        </h4>
        {onCancel && (
          <button
            onClick={onCancel}
            className="text-gray-400 hover:text-gray-600"
            aria-label="Close"
          >
            ×
          </button>
        )}
      </div>

      <p className="text-sm text-gray-600 mb-3">
        {t('warehouseLocations.bulkAssignDescription', { count: inventoryIds.length }) ||
          `Assign ${inventoryIds.length} selected part(s) to a location:`}
      </p>

      {/* Success Message */}
      {success && (
        <div className="mb-3 p-2 bg-green-50 border border-green-200 rounded text-sm text-green-700">
          ✓ {t('warehouseLocations.bulkAssignSuccess') || 'Parts assigned successfully!'}
        </div>
      )}

      {/* Error Message */}
      {error && (
        <div className="mb-3 p-2 bg-red-50 border border-red-200 rounded text-sm text-red-700">
          {error}
        </div>
      )}

      {/* Location Dropdown + Assign Button */}
      <div className="flex items-center gap-2">
        <select
          value={selectedLocationId}
          onChange={(e) => {
            setSelectedLocationId(e.target.value);
            setSuccess(false);
          }}
          disabled={loading || locations.length === 0}
          className="flex-1 px-3 py-2 border border-gray-300 rounded-md text-sm focus:ring-blue-500 focus:border-blue-500 disabled:opacity-50"
        >
          <option value="">
            {locations.length === 0
              ? (t('warehouseLocations.noLocationsAvailable') || 'No locations available')
              : (t('warehouseLocations.selectLocation') || 'Select a location...')}
          </option>
          {locations.map(loc => (
            <option key={loc.id} value={loc.id}>
              {loc.location_code}{loc.description ? ` - ${loc.description}` : ''}
            </option>
          ))}
        </select>
        <button
          onClick={handleBulkAssign}
          disabled={loading || !selectedLocationId}
          className="px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed whitespace-nowrap"
        >
          {loading
            ? (t('common.loading') || '...')
            : (t('warehouseLocations.assignAll') || 'Assign All')}
        </button>
      </div>

      {/* Item count badge */}
      <div className="mt-2 flex items-center gap-1">
        <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
          {inventoryIds.length} {t('warehouseLocations.partsSelected') || 'parts selected'}
        </span>
      </div>
    </div>
  );
};

export default BulkLocationAssign;
