// frontend/src/components/LocationAssignment.js

import { useState, useEffect } from 'react';
import { warehouseLocationsService } from '../services/warehouseLocationsService';
import { useTranslation } from '../hooks/useTranslation';

/**
 * LocationAssignment component - shows current location(s) for an inventory item
 * and allows assigning/unassigning from warehouse locations.
 *
 * Props:
 * - inventoryId: string - The inventory item UUID
 * - warehouseId: string - The warehouse UUID (to fetch available locations)
 * - currentLocations: Array - Current locations assigned to this item [{id, location_code, description}]
 * - onAssignmentChange: function - Callback when assignment changes
 */
const LocationAssignment = ({ inventoryId, warehouseId, currentLocations = [], onAssignmentChange }) => {
  const { t } = useTranslation();
  const [locations, setLocations] = useState([]);
  const [selectedLocationId, setSelectedLocationId] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [assignedLocations, setAssignedLocations] = useState(currentLocations);

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

  // Update assigned locations when prop changes
  useEffect(() => {
    setAssignedLocations(currentLocations);
  }, [currentLocations]);

  const handleAssign = async () => {
    if (!selectedLocationId || !inventoryId) return;

    setLoading(true);
    setError(null);

    try {
      await warehouseLocationsService.assignParts(selectedLocationId, [inventoryId]);

      // Find the location object to add to assigned list
      const assignedLocation = locations.find(loc => loc.id === selectedLocationId);
      if (assignedLocation) {
        const updated = [...assignedLocations, assignedLocation];
        setAssignedLocations(updated);
        if (onAssignmentChange) onAssignmentChange(updated);
      }

      setSelectedLocationId('');
    } catch (err) {
      console.error('Error assigning location:', err);
      setError(err.message || t('warehouseLocations.errorAssigning') || 'Failed to assign location');
    } finally {
      setLoading(false);
    }
  };

  const handleUnassign = async (locationId) => {
    if (!locationId || !inventoryId) return;

    setLoading(true);
    setError(null);

    try {
      await warehouseLocationsService.unassignPart(locationId, inventoryId);

      const updated = assignedLocations.filter(loc => loc.id !== locationId);
      setAssignedLocations(updated);
      if (onAssignmentChange) onAssignmentChange(updated);
    } catch (err) {
      console.error('Error unassigning location:', err);
      setError(err.message || t('warehouseLocations.errorUnassigning') || 'Failed to remove location');
    } finally {
      setLoading(false);
    }
  };

  // Filter out already-assigned locations from the dropdown
  const assignedIds = new Set(assignedLocations.map(loc => loc.id));
  const availableLocations = locations.filter(loc => !assignedIds.has(loc.id));

  return (
    <div className="space-y-3">
      {/* Current Locations */}
      {assignedLocations.length > 0 && (
        <div>
          <label className="block text-xs font-medium text-gray-500 uppercase tracking-wider mb-1">
            {t('warehouseLocations.currentLocations') || 'Current Locations'}
          </label>
          <div className="flex flex-wrap gap-2">
            {assignedLocations.map(loc => (
              <span
                key={loc.id}
                className="inline-flex items-center gap-1 px-2 py-1 bg-green-100 text-green-800 text-sm rounded-md"
              >
                <span className="font-medium">{loc.location_code}</span>
                {loc.description && (
                  <span className="text-green-600 text-xs">({loc.description})</span>
                )}
                <button
                  onClick={() => handleUnassign(loc.id)}
                  disabled={loading}
                  className="ml-1 text-green-600 hover:text-red-600 disabled:opacity-50"
                  title={t('warehouseLocations.removeLocation') || 'Remove from location'}
                >
                  ×
                </button>
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Assign New Location */}
      <div>
        <label className="block text-xs font-medium text-gray-500 uppercase tracking-wider mb-1">
          {t('warehouseLocations.assignToLocation') || 'Assign to Location'}
        </label>
        <div className="flex items-center gap-2">
          <select
            value={selectedLocationId}
            onChange={(e) => setSelectedLocationId(e.target.value)}
            disabled={loading || availableLocations.length === 0}
            className="flex-1 px-3 py-2 border border-gray-300 rounded-md text-sm focus:ring-blue-500 focus:border-blue-500 disabled:opacity-50"
          >
            <option value="">
              {availableLocations.length === 0
                ? (t('warehouseLocations.noLocationsAvailable') || 'No locations available')
                : (t('warehouseLocations.selectLocation') || 'Select a location...')}
            </option>
            {availableLocations.map(loc => (
              <option key={loc.id} value={loc.id}>
                {loc.location_code}{loc.description ? ` - ${loc.description}` : ''}
              </option>
            ))}
          </select>
          <button
            onClick={handleAssign}
            disabled={loading || !selectedLocationId}
            className="px-3 py-2 bg-blue-600 text-white text-sm rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed whitespace-nowrap"
          >
            {loading
              ? (t('common.loading') || '...')
              : (t('warehouseLocations.assign') || 'Assign')}
          </button>
        </div>
      </div>

      {/* Error Display */}
      {error && (
        <p className="text-sm text-red-600">{error}</p>
      )}
    </div>
  );
};

export default LocationAssignment;
