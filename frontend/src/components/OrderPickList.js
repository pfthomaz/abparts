// frontend/src/components/OrderPickList.js

import React, { useState, useMemo } from 'react';
import { useTranslation } from '../hooks/useTranslation';

/**
 * OrderPickList - Mobile-optimized pick list for warehouse order fulfillment.
 * 
 * Shows order items sorted by location code for efficient walking path.
 * Workers can mark items as picked with large touch-friendly checkboxes.
 * Displays real-time progress and a celebration state when complete.
 * 
 * Props:
 *   orderItems - Array of order line items: [{ id, part_name, sku, quantity, inventory_id, location_code }]
 *   onComplete - Callback when all items are picked
 *   onItemPicked(itemId) - Optional callback when an item is checked
 */
const OrderPickList = ({ orderItems = [], onComplete, onItemPicked }) => {
  const { t } = useTranslation();
  const [pickedItems, setPickedItems] = useState(new Set());

  const totalItems = orderItems.length;
  const pickedCount = pickedItems.size;
  const allPicked = totalItems > 0 && pickedCount === totalItems;
  const progressPercent = totalItems > 0 ? (pickedCount / totalItems) * 100 : 0;

  // Sort items by location_code for efficient walking path
  // Unpicked items first (sorted by location), then picked items at the bottom
  const sortedItems = useMemo(() => {
    const sorted = [...orderItems].sort((a, b) => {
      const aCode = (a.location_code || '').toLowerCase();
      const bCode = (b.location_code || '').toLowerCase();
      return aCode.localeCompare(bCode, undefined, { numeric: true });
    });

    // Separate picked and unpicked
    const unpicked = sorted.filter(item => !pickedItems.has(item.id));
    const picked = sorted.filter(item => pickedItems.has(item.id));

    return [...unpicked, ...picked];
  }, [orderItems, pickedItems]);

  const handleTogglePicked = (itemId) => {
    setPickedItems(prev => {
      const next = new Set(prev);
      if (next.has(itemId)) {
        next.delete(itemId);
      } else {
        next.add(itemId);
        // Notify parent about the pick
        if (onItemPicked) {
          onItemPicked(itemId);
        }
        // Check if all items are now picked
        if (next.size === totalItems && onComplete) {
          // Delay slightly so the UI updates first
          setTimeout(() => onComplete(), 300);
        }
      }
      return next;
    });
  };

  // Get a color for the location badge based on the location code
  const getLocationColor = (locationCode) => {
    if (!locationCode) return 'bg-gray-100 text-gray-600';
    const colors = [
      'bg-blue-100 text-blue-700',
      'bg-purple-100 text-purple-700',
      'bg-indigo-100 text-indigo-700',
      'bg-teal-100 text-teal-700',
      'bg-orange-100 text-orange-700',
      'bg-pink-100 text-pink-700',
    ];
    // Simple hash based on first char
    const charCode = locationCode.charCodeAt(0);
    return colors[charCode % colors.length];
  };

  if (totalItems === 0) {
    return (
      <div className="flex flex-col items-center justify-center p-8 text-center">
        <div className="text-4xl mb-3">📦</div>
        <p className="text-gray-500 text-lg">
          {t('pickList.noItems') || 'No items to pick'}
        </p>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-full">
      {/* Header with progress - always visible */}
      <div className="sticky top-0 z-10 bg-white border-b border-gray-200 px-4 py-3 shadow-sm">
        {/* Progress text */}
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm font-medium text-gray-700">
            {t('pickList.progress') || 'Progress'}
          </span>
          <span className="text-sm font-bold text-gray-900">
            {pickedCount}/{totalItems} {t('pickList.itemsPicked') || 'items picked'}
          </span>
        </div>

        {/* Progress bar */}
        <div className="w-full bg-gray-200 rounded-full h-3 overflow-hidden">
          <div
            className={`h-full rounded-full transition-all duration-500 ease-out ${
              allPicked ? 'bg-green-500' : 'bg-blue-500'
            }`}
            style={{ width: `${progressPercent}%` }}
          />
        </div>
      </div>

      {/* Celebration state when all items picked */}
      {allPicked && (
        <div className="bg-green-50 border-b border-green-200 px-4 py-6 text-center">
          <div className="text-4xl mb-2">🎉</div>
          <p className="text-lg font-bold text-green-800">
            {t('pickList.allPicked') || 'All items picked!'}
          </p>
          <p className="text-sm text-green-600 mt-1">
            {t('pickList.orderReady') || 'Order is ready for packing'}
          </p>
        </div>
      )}

      {/* Items list */}
      <div className="flex-1 overflow-y-auto">
        <ul className="divide-y divide-gray-100">
          {sortedItems.map((item) => {
            const isPicked = pickedItems.has(item.id);

            return (
              <li
                key={item.id}
                className={`px-4 py-4 transition-colors duration-200 ${
                  isPicked ? 'bg-gray-50 opacity-60' : 'bg-white'
                }`}
              >
                <button
                  type="button"
                  className="w-full flex items-center gap-3 text-left"
                  onClick={() => handleTogglePicked(item.id)}
                  aria-label={`${isPicked ? 'Unmark' : 'Mark'} ${item.part_name} as picked`}
                  style={{ touchAction: 'manipulation' }}
                >
                  {/* Checkbox - large touch target (min 44px) */}
                  <div
                    className={`flex-shrink-0 w-11 h-11 rounded-lg border-2 flex items-center justify-center transition-all duration-200 ${
                      isPicked
                        ? 'bg-green-500 border-green-500'
                        : 'border-gray-300 bg-white hover:border-blue-400'
                    }`}
                  >
                    {isPicked && (
                      <svg className="w-6 h-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={3}>
                        <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
                      </svg>
                    )}
                  </div>

                  {/* Item details */}
                  <div className="flex-1 min-w-0">
                    {/* Part name */}
                    <p className={`text-base font-medium truncate ${
                      isPicked ? 'line-through text-gray-400' : 'text-gray-900'
                    }`}>
                      {item.part_name}
                    </p>

                    {/* SKU and quantity */}
                    <div className="flex items-center gap-2 mt-0.5">
                      {item.sku && (
                        <span className="text-xs text-gray-500">
                          {item.sku}
                        </span>
                      )}
                      <span className={`text-sm font-semibold ${
                        isPicked ? 'text-gray-400' : 'text-gray-700'
                      }`}>
                        ×{item.quantity}
                      </span>
                    </div>
                  </div>

                  {/* Location badge - prominent and easy to spot */}
                  <div className="flex-shrink-0">
                    {item.location_code ? (
                      <span className={`inline-flex items-center px-3 py-1.5 rounded-lg text-sm font-bold ${
                        isPicked ? 'bg-gray-100 text-gray-400' : getLocationColor(item.location_code)
                      }`}>
                        📍 {item.location_code}
                      </span>
                    ) : (
                      <span className="inline-flex items-center px-3 py-1.5 rounded-lg text-sm font-medium bg-gray-100 text-gray-400">
                        {t('pickList.noLocation') || '—'}
                      </span>
                    )}
                  </div>
                </button>
              </li>
            );
          })}
        </ul>
      </div>
    </div>
  );
};

export default OrderPickList;
