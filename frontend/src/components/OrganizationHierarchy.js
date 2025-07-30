// frontend/src/components/OrganizationHierarchy.js

import React, { useState, useEffect } from 'react';
import { useAuth } from '../AuthContext';
import { organizationsService, ORGANIZATION_TYPE_CONFIG } from '../services/organizationsService';
import { getCountryFlag } from '../utils/countryFlags';

const OrganizationHierarchy = ({ onOrganizationSelect, selectedOrganizationId }) => {
  const { user } = useAuth();
  const [hierarchyData, setHierarchyData] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [expandedNodes, setExpandedNodes] = useState(new Set());
  const [includeInactive, setIncludeInactive] = useState(false);

  // Load organization hierarchy
  const loadHierarchy = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await organizationsService.getOrganizationHierarchy();
      setHierarchyData(response.data || response);

      // Auto-expand root nodes
      const rootIds = (response.data || response).map(org => org.id);
      setExpandedNodes(new Set(rootIds));
    } catch (err) {
      console.error('Failed to load organization hierarchy:', err);
      setError('Failed to load organization hierarchy. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadHierarchy();
  }, [includeInactive]);

  // Toggle node expansion
  const toggleNode = (nodeId) => {
    const newExpanded = new Set(expandedNodes);
    if (newExpanded.has(nodeId)) {
      newExpanded.delete(nodeId);
    } else {
      newExpanded.add(nodeId);
    }
    setExpandedNodes(newExpanded);
  };

  // Handle organization selection
  const handleOrganizationClick = (organization) => {
    if (onOrganizationSelect) {
      onOrganizationSelect(organization);
    }
  };

  // Render a single organization node
  const renderOrganizationNode = (org, depth = 0) => {
    const hasChildren = org.children && org.children.length > 0;
    const isExpanded = expandedNodes.has(org.id);
    const isSelected = selectedOrganizationId === org.id;
    const config = ORGANIZATION_TYPE_CONFIG[org.organization_type];

    // Filter children based on active status
    const visibleChildren = hasChildren
      ? org.children.filter(child => includeInactive || child.is_active)
      : [];

    return (
      <div key={org.id} className="select-none">
        {/* Organization Node */}
        <div
          className={`flex items-center py-2 px-3 hover:bg-gray-50 cursor-pointer rounded-md ${isSelected ? 'bg-indigo-50 border-l-4 border-indigo-500' : ''
            }`}
          style={{ marginLeft: `${depth * 20}px` }}
          onClick={() => handleOrganizationClick(org)}
        >
          {/* Expand/Collapse Button */}
          <div className="w-6 h-6 flex items-center justify-center mr-2">
            {hasChildren && visibleChildren.length > 0 ? (
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  toggleNode(org.id);
                }}
                className="w-4 h-4 flex items-center justify-center text-gray-400 hover:text-gray-600"
              >
                {isExpanded ? (
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                  </svg>
                ) : (
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                  </svg>
                )}
              </button>
            ) : (
              <div className="w-4 h-4"></div>
            )}
          </div>

          {/* Organization Icon */}
          <div className="flex-shrink-0 mr-3">
            <span className="text-lg">{config?.icon || '🏢'}</span>
          </div>

          {/* Organization Info */}
          <div className="flex-1 min-w-0">
            <div className="flex items-center space-x-2">
              <p className={`text-sm font-medium truncate ${isSelected ? 'text-indigo-900' : 'text-gray-900'
                }`}>
                {org.name}
              </p>
              {org.country && (
                <span className="text-sm">
                  {getCountryFlag(org.country)}
                </span>
              )}
              {!org.is_active && (
                <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800">
                  Inactive
                </span>
              )}
            </div>
            <div className="flex items-center space-x-2 mt-1">
              <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium ${config?.color || 'bg-gray-100 text-gray-800'}`}>
                {config?.label || org.organization_type}
              </span>
              {hasChildren && (
                <span className="text-xs text-gray-500">
                  {visibleChildren.length} {visibleChildren.length === 1 ? 'child' : 'children'}
                </span>
              )}
            </div>
          </div>
        </div>

        {/* Children Nodes */}
        {hasChildren && isExpanded && visibleChildren.length > 0 && (
          <div className="ml-4">
            {visibleChildren.map(child => renderOrganizationNode(child, depth + 1))}
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h3 className="text-lg font-medium text-gray-900">Organization Hierarchy</h3>
          <p className="text-sm text-gray-500">
            Visual representation of organization structure
          </p>
        </div>
        <button
          onClick={loadHierarchy}
          disabled={loading}
          className="inline-flex items-center px-3 py-2 border border-gray-300 shadow-sm text-sm leading-4 font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50"
        >
          <svg className={`-ml-0.5 mr-2 h-4 w-4 ${loading ? 'animate-spin' : ''}`} xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
          Refresh
        </button>
      </div>

      {/* Controls */}
      <div className="flex items-center space-x-4">
        <label className="flex items-center">
          <input
            type="checkbox"
            checked={includeInactive}
            onChange={(e) => setIncludeInactive(e.target.checked)}
            className="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded"
          />
          <span className="ml-2 text-sm text-gray-700">Include inactive organizations</span>
        </label>
        <div className="flex items-center space-x-2">
          <button
            onClick={() => setExpandedNodes(new Set(hierarchyData.map(org => org.id)))}
            className="text-sm text-indigo-600 hover:text-indigo-500"
          >
            Expand All
          </button>
          <span className="text-gray-300">|</span>
          <button
            onClick={() => setExpandedNodes(new Set())}
            className="text-sm text-indigo-600 hover:text-indigo-500"
          >
            Collapse All
          </button>
        </div>
      </div>

      {/* Error Display */}
      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative">
          <span className="block sm:inline">{error}</span>
        </div>
      )}

      {/* Loading State */}
      {loading && (
        <div className="flex justify-center py-8">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
        </div>
      )}

      {/* Hierarchy Tree */}
      {!loading && (
        <div className="bg-white border border-gray-200 rounded-lg p-4">
          {hierarchyData.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              No organizations found. Create your first organization to get started.
            </div>
          ) : (
            <div className="space-y-1">
              {hierarchyData
                .filter(org => includeInactive || org.is_active)
                .map(org => renderOrganizationNode(org))}
            </div>
          )}
        </div>
      )}

      {/* Legend */}
      <div className="bg-gray-50 rounded-lg p-4">
        <h4 className="text-sm font-medium text-gray-900 mb-3">Organization Types</h4>
        <div className="grid grid-cols-2 gap-3">
          {Object.entries(ORGANIZATION_TYPE_CONFIG).map(([type, config]) => (
            <div key={type} className="flex items-center space-x-2">
              <span className="text-lg">{config.icon}</span>
              <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium ${config.color}`}>
                {config.label}
              </span>
              <span className="text-xs text-gray-500">{config.description}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default OrganizationHierarchy;