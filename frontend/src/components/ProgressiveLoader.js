import React from 'react';

/**
 * Progressive loading indicator component for large datasets
 * @param {boolean} isLoading - Whether data is currently loading
 * @param {boolean} isSearching - Whether search is in progress
 * @param {number} totalItems - Total number of items
 * @param {number} displayedItems - Number of items currently displayed
 * @param {string} itemType - Type of items being loaded (e.g., "parts")
 */
const ProgressiveLoader = ({
  isLoading = false,
  isSearching = false,
  totalItems = 0,
  displayedItems = 0,
  itemType = "items"
}) => {
  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-8">
        <div className="text-gray-500">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-2"></div>
          <p>Loading {itemType}...</p>
        </div>
      </div>
    );
  }

  if (isSearching) {
    return (
      <div className="flex items-center justify-center py-4">
        <div className="text-gray-500 flex items-center">
          <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600 mr-2"></div>
          <p className="text-sm">Searching {itemType}...</p>
        </div>
      </div>
    );
  }

  if (totalItems > 0 && displayedItems > 0) {
    return (
      <div className="text-center py-4 text-sm text-gray-500">
        Showing {displayedItems} of {totalItems} {itemType}
        {displayedItems < totalItems && (
          <span className="ml-2 text-blue-600">
            ({totalItems - displayedItems} more available)
          </span>
        )}
      </div>
    );
  }

  return null;
};

/**
 * Search status indicator component
 * @param {boolean} isSearching - Whether search is in progress
 * @param {string} searchTerm - Current search term
 * @param {number} resultCount - Number of search results
 */
export const SearchStatusIndicator = ({ isSearching, searchTerm, resultCount }) => {
  if (isSearching && searchTerm) {
    return (
      <div className="flex items-center text-sm text-gray-500 mb-2">
        <div className="animate-spin rounded-full h-3 w-3 border-b-2 border-blue-600 mr-2"></div>
        <span>Searching for "{searchTerm}"...</span>
      </div>
    );
  }

  if (searchTerm && !isSearching) {
    return (
      <div className="text-sm text-gray-600 mb-2">
        Found {resultCount} result{resultCount !== 1 ? 's' : ''} for "{searchTerm}"
      </div>
    );
  }

  return null;
};

export default ProgressiveLoader;