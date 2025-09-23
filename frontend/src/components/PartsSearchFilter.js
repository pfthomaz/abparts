import { memo } from 'react';
import { PartCategoryFilter } from './PartCategoryBadge';
import { SearchStatusIndicator } from './ProgressiveLoader';

/**
 * Optimized search and filter component for parts
 * Uses React.memo to prevent unnecessary re-renders
 */
const PartsSearchFilter = memo(({
  searchTerm,
  onSearchChange,
  filterProprietary,
  onProprietaryChange,
  filterPartType,
  onPartTypeChange,
  isSearching = false,
  resultCount = 0
}) => {
  return (
    <div className="bg-white p-4 rounded-lg shadow-md mb-6">
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="md:col-span-1">
          <label htmlFor="search" className="block text-sm font-medium text-gray-700">
            Search
          </label>
          <div className="relative mt-1">
            <input
              type="text"
              id="search"
              placeholder="By name or number..."
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500 transition-colors duration-150"
              value={searchTerm}
              onChange={(e) => onSearchChange(e.target.value)}
            />
            {isSearching && (
              <div className="absolute right-3 top-1/2 transform -translate-y-1/2">
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600"></div>
              </div>
            )}
          </div>
        </div>

        <div>
          <label htmlFor="filterProprietary" className="block text-sm font-medium text-gray-700">
            Proprietary
          </label>
          <select
            id="filterProprietary"
            className="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm rounded-md transition-colors duration-150"
            value={filterProprietary}
            onChange={(e) => onProprietaryChange(e.target.value)}
          >
            <option value="all">All</option>
            <option value="yes">Yes</option>
            <option value="no">No</option>
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Part Category
          </label>
          <PartCategoryFilter
            value={filterPartType}
            onChange={onPartTypeChange}
            showAll={true}
          />
        </div>
      </div>

      {/* Search status indicator */}
      <div className="mt-3">
        <SearchStatusIndicator
          isSearching={isSearching}
          searchTerm={searchTerm}
          resultCount={resultCount}
        />
      </div>
    </div>
  );
});

PartsSearchFilter.displayName = 'PartsSearchFilter';

export default PartsSearchFilter;