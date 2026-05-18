// frontend/src/components/StartPickingButton.js

import React, { useState, useCallback } from 'react';
import { useTranslation } from '../hooks/useTranslation';
import { warehouseLocationsService } from '../services/warehouseLocationsService';
import { api } from '../services/api';
import OrderPickList from './OrderPickList';

/**
 * StartPickingButton - Self-contained component that adds a "Start Picking" button
 * to any order detail view. When clicked, opens a full-screen mobile-optimized
 * pick list overlay with location data for each order item.
 *
 * Props:
 *   order - The order object with its items array
 *   warehouseId - The warehouse ID to fetch location data for items
 */
const StartPickingButton = ({ order, warehouseId }) => {
  const { t } = useTranslation();
  const [isOpen, setIsOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const [pickItems, setPickItems] = useState([]);
  const [error, setError] = useState(null);
  const [showCelebration, setShowCelebration] = useState(false);

  const fetchLocationData = useCallback(async () => {
    if (!order?.items?.length || !warehouseId) return;

    setLoading(true);
    setError(null);

    try {
      // Fetch all inventory for this warehouse to find inventory IDs for each part
      const warehouseInventory = await api.get(
        `/inventory/warehouse/${warehouseId}?limit=1000`
      );

      const inventoryList = Array.isArray(warehouseInventory)
        ? warehouseInventory
        : warehouseInventory?.items || [];

      // Build a map: part_id -> inventory record
      const partInventoryMap = {};
      for (const inv of inventoryList) {
        partInventoryMap[inv.part_id] = inv;
      }

      // For each order item, look up its location via the inventory record
      const itemsWithLocations = await Promise.all(
        order.items.map(async (item) => {
          let locationCode = null;
          let inventoryId = null;

          const inventoryRecord = partInventoryMap[item.part_id];
          if (inventoryRecord) {
            inventoryId = inventoryRecord.id;

            try {
              const locations = await warehouseLocationsService.getLocationsForPart(inventoryRecord.id);
              if (locations && locations.length > 0) {
                locationCode = locations[0].location_code;
              }
            } catch {
              // No location assigned - that's fine
            }
          }

          return {
            id: item.id,
            part_name: item.part_name || item.part?.name || 'Unknown Part',
            sku: item.part_number || item.part?.part_number || null,
            quantity: Number(item.quantity) || 1,
            inventory_id: inventoryId,
            location_code: locationCode,
          };
        })
      );

      setPickItems(itemsWithLocations);
    } catch (err) {
      setError(err.message || 'Failed to load pick list data');
    } finally {
      setLoading(false);
    }
  }, [order, warehouseId]);

  const handleStartPicking = async () => {
    setIsOpen(true);
    setShowCelebration(false);
    await fetchLocationData();
  };

  const handleComplete = () => {
    setShowCelebration(true);
  };

  const handleClose = () => {
    setIsOpen(false);
    setShowCelebration(false);
    setPickItems([]);
    setError(null);
  };

  // Don't render if no order or no items
  if (!order?.items?.length) return null;

  return (
    <>
      {/* Start Picking Button - large, prominent, green */}
      <button
        onClick={handleStartPicking}
        className="w-full sm:w-auto inline-flex items-center justify-center gap-2 px-6 py-3 bg-green-600 hover:bg-green-700 text-white text-lg font-bold rounded-xl shadow-lg hover:shadow-xl transition-all duration-200 active:scale-95"
      >
        <span className="text-xl">🚀</span>
        {t('pickList.startPicking') || 'Start Picking'}
      </button>

      {/* Full-screen picking overlay */}
      {isOpen && (
        <div className="fixed inset-0 z-50 bg-white flex flex-col">
          {/* Header bar */}
          <div className="flex items-center justify-between px-4 py-3 bg-gray-50 border-b border-gray-200 shadow-sm">
            <h2 className="text-lg font-bold text-gray-800 truncate">
              📋 {t('pickList.title') || 'Pick List'}
            </h2>
            <button
              onClick={handleClose}
              className="flex-shrink-0 ml-2 p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-200 rounded-lg transition-colors"
              aria-label="Close"
            >
              <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          {/* Content area */}
          <div className="flex-1 overflow-hidden flex flex-col">
            {/* Loading state */}
            {loading && (
              <div className="flex-1 flex flex-col items-center justify-center p-8">
                <div className="animate-spin rounded-full h-12 w-12 border-4 border-green-500 border-t-transparent mb-4"></div>
                <p className="text-gray-600 text-lg">
                  {t('pickList.loadingLocations') || 'Loading locations...'}
                </p>
              </div>
            )}

            {/* Error state */}
            {error && !loading && (
              <div className="flex-1 flex flex-col items-center justify-center p-8">
                <div className="text-4xl mb-3">⚠️</div>
                <p className="text-red-600 text-center mb-4">{error}</p>
                <button
                  onClick={fetchLocationData}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                >
                  {t('common.retry') || 'Retry'}
                </button>
              </div>
            )}

            {/* Celebration overlay when all items picked */}
            {showCelebration && !loading && (
              <div className="flex-1 flex flex-col items-center justify-center p-8 bg-gradient-to-b from-green-50 to-white">
                <div className="text-6xl mb-4 animate-bounce">🎉</div>
                <h3 className="text-2xl font-bold text-green-800 mb-2">
                  {t('pickList.allPicked') || 'All items picked!'}
                </h3>
                <p className="text-green-600 mb-6 text-center">
                  {t('pickList.orderReady') || 'Order is ready for packing'}
                </p>
                <div className="flex gap-3">
                  <button
                    onClick={handleClose}
                    className="px-6 py-3 bg-green-600 text-white text-lg font-bold rounded-xl hover:bg-green-700 transition-colors shadow-lg"
                  >
                    ✅ {t('pickList.done') || 'Done'}
                  </button>
                </div>
              </div>
            )}

            {/* Pick list */}
            {!loading && !error && !showCelebration && pickItems.length > 0 && (
              <OrderPickList
                orderItems={pickItems}
                onComplete={handleComplete}
              />
            )}
          </div>
        </div>
      )}
    </>
  );
};

export default StartPickingButton;
