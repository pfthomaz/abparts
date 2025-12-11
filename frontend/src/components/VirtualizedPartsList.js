import React, { useState, useRef, useMemo, memo } from 'react';
import PartCard from './PartCard';

/**
 * Virtualized parts list component for handling large datasets efficiently
 * Only renders visible items to improve performance with thousands of parts
 */
const VirtualizedPartsList = memo(({
  parts,
  onEdit,
  onDelete,
  itemHeight = 400, // Estimated height of each part card
  containerHeight = 600, // Height of the scrollable container
  overscan = 5 // Number of items to render outside visible area
}) => {
  const [scrollTop, setScrollTop] = useState(0);
  const containerRef = useRef(null);

  // Calculate visible range
  const visibleRange = useMemo(() => {
    const startIndex = Math.max(0, Math.floor(scrollTop / itemHeight) - overscan);
    const endIndex = Math.min(
      parts.length - 1,
      Math.ceil((scrollTop + containerHeight) / itemHeight) + overscan
    );
    return { startIndex, endIndex };
  }, [scrollTop, itemHeight, containerHeight, parts.length, overscan]);

  // Get visible items
  const visibleItems = useMemo(() => {
    return parts.slice(visibleRange.startIndex, visibleRange.endIndex + 1);
  }, [parts, visibleRange]);

  // Handle scroll events
  const handleScroll = (e) => {
    setScrollTop(e.target.scrollTop);
  };

  // Total height of all items
  const totalHeight = parts.length * itemHeight;

  // Offset for visible items
  const offsetY = visibleRange.startIndex * itemHeight;

  return (
    <div
      ref={containerRef}
      className="overflow-auto border border-gray-200 rounded-lg"
      style={{ height: containerHeight }}
      onScroll={handleScroll}
    >
      <div style={{ height: totalHeight, position: 'relative' }}>
        <div
          style={{
            transform: `translateY(${offsetY}px)`,
            position: 'absolute',
            top: 0,
            left: 0,
            right: 0,
          }}
        >
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 p-6">
            {visibleItems.map((part, index) => (
              <PartCard
                key={part.id}
                part={part}
                onEdit={onEdit}
                onDelete={onDelete}
              />
            ))}
          </div>
        </div>
      </div>
    </div>
  );
});

/**
 * Performance monitoring component for large datasets
 */
export const PerformanceMonitor = memo(({
  totalItems,
  visibleItems,
  renderTime
}) => {
  if (process.env.NODE_ENV !== 'development') {
    return null;
  }

  return (
    <div className="text-xs text-gray-500 p-2 bg-gray-100 rounded">
      Performance: {totalItems} total, {visibleItems} visible, {renderTime}ms render
    </div>
  );
});

VirtualizedPartsList.displayName = 'VirtualizedPartsList';
PerformanceMonitor.displayName = 'PerformanceMonitor';

export default VirtualizedPartsList;