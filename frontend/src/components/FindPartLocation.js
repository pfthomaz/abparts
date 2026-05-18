// frontend/src/components/FindPartLocation.js

import React, { useState, useCallback } from 'react';
import { useTranslation } from '../hooks/useTranslation';
import { warehouseLocationsService } from '../services/warehouseLocationsService';

/**
 * FindPartLocation - A compact component that shows where a part is stored.
 * 
 * Displays a "📍 Where is this?" button. When clicked, fetches and displays
 * the location code(s) for the given inventory item prominently.
 * 
 * Props:
 *   - inventoryId (string, required): The inventory UUID to look up locations for
 * 
 * Mobile-friendly with large touch targets.
 */
const FindPartLocation = ({ inventoryId }) => {
  const { t } = useTranslation();
  const [locations, setLocations] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [isOpen, setIsOpen] = useState(false);

  const fetchLocations = useCallback(async () => {
    if (!inventoryId) return;

    setLoading(true);
    setError(null);

    try {
      const result = await warehouseLocationsService.getLocationsForPart(inventoryId);
      setLocations(result || []);
      setIsOpen(true);
    } catch (err) {
      console.error('Failed to fetch part locations:', err);
      setError(err.message || 'Failed to fetch locations');
    } finally {
      setLoading(false);
    }
  }, [inventoryId]);

  const handleClick = () => {
    if (isOpen) {
      // Toggle closed
      setIsOpen(false);
    } else {
      fetchLocations();
    }
  };

  return (
    <div className="inline-block">
      {/* Where is this? button - large touch target for mobile */}
      <button
        onClick={handleClick}
        disabled={loading || !inventoryId}
        className="inline-flex items-center gap-1.5 px-3 py-2 text-sm font-medium 
                   text-blue-700 bg-blue-50 border border-blue-200 rounded-lg
                   hover:bg-blue-100 hover:border-blue-300
                   active:bg-blue-200
                   disabled:opacity-50 disabled:cursor-not-allowed
                   transition-colors duration-150
                   min-h-[44px] min-w-[44px]"
        aria-label={t('warehouseLocations.whereIsThis') || 'Where is this?'}
      >
        {loading ? (
          <svg className="animate-spin h-4 w-4 text-blue-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
        ) : (
          <span className="text-base">📍</span>
        )}
        <span className="whitespace-nowrap">
          {t('warehouseLocations.whereIsThis') || 'Where is this?'}
        </span>
        {isOpen && (
          <svg className="h-4 w-4 text-blue-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 15l7-7 7 7" />
          </svg>
        )}
      </button>

      {/* Location result display */}
      {isOpen && !loading && (
        <div className="mt-2">
          {error && (
            <div className="text-sm text-red-600 bg-red-50 border border-red-200 rounded-lg px-3 py-2">
              {error}
            </div>
          )}

          {!error && locations && locations.length === 0 && (
            <div className="text-sm text-gray-500 bg-gray-50 border border-gray-200 rounded-lg px-3 py-2">
              {t('warehouseLocations.noLocationAssigned') || 'No location assigned'}
            </div>
          )}

          {!error && locations && locations.length > 0 && (
            <div className="flex flex-wrap gap-2">
              {locations.map((loc) => (
                <div
                  key={loc.id}
                  className="inline-flex items-center gap-2 px-3 py-2 
                             bg-green-50 border border-green-300 rounded-lg"
                >
                  <span className="text-lg font-bold text-green-800">
                    {loc.location_code}
                  </span>
                  {loc.description && (
                    <span className="text-xs text-green-600">
                      {loc.description}
                    </span>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default FindPartLocation;
