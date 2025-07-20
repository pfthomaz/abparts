// frontend/src/pages/Organizations.js

import React, { useState, useEffect, useCallback, useMemo } from 'react';
import { organizationsService, OrganizationType, ORGANIZATION_TYPE_CONFIG } from '../services/organizationsService';
import { useAuth } from '../AuthContext';
import Modal from '../components/Modal';
import OrganizationForm from '../components/OrganizationForm';

const Organizations = () => {
  const { user } = useAuth();

  // State management
  const [organizations, setOrganizations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showModal, setShowModal] = useState(false);
  const [editingOrganization, setEditingOrganization] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterType, setFilterType] = useState('all');
  const [viewMode, setViewMode] = useState('cards'); // 'cards' or 'hierarchy'
  const [hierarchyData, setHierarchyData] = useState([]);
  const [loadingHierarchy, setLoadingHierarchy] = useState(false);

  // Check permissions
  const canManageOrganizations = user?.role === 'super_admin' || user?.role === 'admin';

  const fetchOrganizations = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await organizationsService.getOrganizations();
      const data = response.data || response;
      setOrganizations(data);
    } catch (err) {
      setError(err.message || 'Failed to fetch organizations.');
    } finally {
      setLoading(false);
    }
  }, []);

  const fetchHierarchy = useCallback(async () => {
    setLoadingHierarchy(true);
    try {
      const response = await organizationsService.getOrganizationHierarchy();
      const data = response.data || response;
      setHierarchyData(data);
    } catch (err) {
      console.error('Failed to fetch hierarchy:', err);
      setHierarchyData([]);
    } finally {
      setLoadingHierarchy(false);
    }
  }, []);

  useEffect(() => {
    fetchOrganizations();
    if (viewMode === 'hierarchy') {
      fetchHierarchy();
    }
  }, [fetchOrganizations, fetchHierarchy, viewMode]);

  const filteredOrganizations = useMemo(() => {
    return organizations
      .filter(org => {
        if (filterType === 'all') return true;
        return org.organization_type === filterType;
      })
      .filter(org => {
        if (!searchTerm) return true;
        const term = searchTerm.toLowerCase();
        return org.name.toLowerCase().includes(term);
      });
  }, [organizations, searchTerm, filterType]);

  const handleCreateOrUpdate = async (orgData) => {
    try {
      if (editingOrganization) {
        const response = await organizationsService.updateOrganization(editingOrganization.id, orgData);
        const updatedOrg = response.data || response;
        setOrganizations(prev =>
          prev.map(org => org.id === editingOrganization.id ? updatedOrg : org)
        );
      } else {
        const response = await organizationsService.createOrganization(orgData);
        const newOrg = response.data || response;
        setOrganizations(prev => [newOrg, ...prev]);
      }
      closeModal();
      if (viewMode === 'hierarchy') {
        fetchHierarchy();
      }
    } catch (err) {
      console.error("Error creating/updating organization:", err);
      // Re-throw to be caught by the form's error handling
      throw err;
    }
  };

  const handleDelete = async (orgId) => {
    if (!window.confirm("Are you sure you want to delete this organization? This action cannot be undone.")) {
      return;
    }
    setError(null);
    try {
      await organizationsService.deleteOrganization(orgId);
      setOrganizations(prev => prev.filter(org => org.id !== orgId));
      if (viewMode === 'hierarchy') {
        fetchHierarchy();
      }
    } catch (err) {
      setError(err.response?.data?.detail || err.message || 'Failed to delete organization.');
    }
  };

  const openModal = (org = null) => {
    setEditingOrganization(org);
    setShowModal(true);
  };

  const closeModal = () => {
    setShowModal(false);
    setEditingOrganization(null);
  };

  const getOrganizationTypeInfo = (type) => {
    return ORGANIZATION_TYPE_CONFIG[type] || {
      label: type,
      description: '',
      color: 'bg-gray-100 text-gray-800',
      icon: '🏢',
      singleton: false
    };
  };

  const renderHierarchyNode = (node, level = 0) => {
    const config = getOrganizationTypeInfo(node.organization_type);
    const paddingLeft = level * 20;

    return (
      <div key={node.id} className="mb-2">
        <div
          className="flex items-center p-3 bg-white rounded-lg shadow-sm border border-gray-200 hover:shadow-md transition-shadow"
          style={{ marginLeft: `${paddingLeft}px` }}
        >
          <span className="text-lg mr-3">{config.icon}</span>
          <div className="flex-1">
            <h4 className="font-semibold text-gray-900">{node.name}</h4>
            <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${config.color}`}>
              {config.label}
            </span>
          </div>
          {canManageOrganizations && (
            <div className="flex space-x-2">
              <button
                onClick={() => openModal(organizations.find(org => org.id === node.id))}
                className="text-indigo-600 hover:text-indigo-900 text-sm"
              >
                Edit
              </button>
              <button
                onClick={() => handleDelete(node.id)}
                className="text-red-600 hover:text-red-900 text-sm"
              >
                Delete
              </button>
            </div>
          )}
        </div>
        {node.children && node.children.map(child => renderHierarchyNode(child, level + 1))}
      </div>
    );
  };

  return (
    <div>
      {/* Header */}
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-3xl font-bold text-gray-800">Organizations</h1>
          <p className="text-gray-600 mt-1">Manage organization hierarchy and relationships</p>
        </div>
        <div className="flex items-center space-x-3">
          {/* View Mode Toggle */}
          <div className="flex rounded-md shadow-sm">
            <button
              onClick={() => setViewMode('cards')}
              className={`px-4 py-2 text-sm font-medium rounded-l-md border ${viewMode === 'cards'
                ? 'bg-indigo-600 text-white border-indigo-600'
                : 'bg-white text-gray-700 border-gray-300 hover:bg-gray-50'
                }`}
            >
              Cards
            </button>
            <button
              onClick={() => setViewMode('hierarchy')}
              className={`px-4 py-2 text-sm font-medium rounded-r-md border-t border-r border-b ${viewMode === 'hierarchy'
                ? 'bg-indigo-600 text-white border-indigo-600'
                : 'bg-white text-gray-700 border-gray-300 hover:bg-gray-50'
                } -ml-px`}
            >
              Hierarchy
            </button>
          </div>

          {canManageOrganizations && (
            <button
              onClick={() => openModal()}
              className="bg-indigo-600 text-white py-2 px-4 rounded-md hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 transition duration-150 ease-in-out font-semibold"
            >
              Add Organization
            </button>
          )}
        </div>
      </div>

      {/* Loading and Error States */}
      {loading && <p className="text-gray-500">Loading organizations...</p>}
      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative mb-4" role="alert">
          <strong className="font-bold">Error: </strong>
          <span className="block sm:inline">{error}</span>
        </div>
      )}

      {/* Search and Filter Bar (only for cards view) */}
      {viewMode === 'cards' && (
        <div className="bg-white p-4 rounded-lg shadow-md mb-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label htmlFor="search" className="block text-sm font-medium text-gray-700">Search by Name</label>
              <input
                type="text"
                id="search"
                placeholder="Search organizations..."
                className="mt-1 w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-indigo-500 focus:border-indigo-500"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
              />
            </div>
            <div>
              <label htmlFor="filterType" className="block text-sm font-medium text-gray-700">Filter by Type</label>
              <select
                id="filterType"
                className="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm rounded-md"
                value={filterType}
                onChange={(e) => setFilterType(e.target.value)}
              >
                <option value="all">All Types</option>
                {Object.values(OrganizationType).map((type) => {
                  const config = getOrganizationTypeInfo(type);
                  return (
                    <option key={type} value={type}>
                      {config.icon} {config.label}
                    </option>
                  );
                })}
              </select>
            </div>
          </div>
        </div>
      )}

      {/* Content */}
      {viewMode === 'cards' ? (
        // Cards View
        !loading && filteredOrganizations.length === 0 ? (
          <div className="text-center py-10 bg-white rounded-lg shadow-md">
            <h3 className="text-xl font-semibold text-gray-700">No Organizations Found</h3>
            <p className="text-gray-500 mt-2">
              {organizations.length > 0 ? 'Try adjusting your search or filter criteria.' : 'There are no organizations in the system yet.'}
            </p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-12">
            {filteredOrganizations.map((org) => {
              const config = getOrganizationTypeInfo(org.organization_type);
              return (
                <div key={org.id} className="bg-white p-6 rounded-lg shadow-md border border-gray-200 hover:shadow-lg transition-shadow">
                  <div className="flex items-start justify-between mb-3">
                    <h3 className="text-xl font-semibold text-gray-900 flex-1">{org.name}</h3>
                    <span className="text-2xl">{config.icon}</span>
                  </div>

                  <div className="mb-3">
                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${config.color}`}>
                      {config.label}
                    </span>
                  </div>

                  {org.parent_organization_name && (
                    <p className="text-gray-600 mb-2">
                      <span className="font-medium">Parent:</span> {org.parent_organization_name}
                    </p>
                  )}

                  <div className="mb-2">
                    <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${org.is_active
                      ? 'bg-green-100 text-green-800'
                      : 'bg-red-100 text-red-800'
                      }`}>
                      {org.is_active ? 'Active' : 'Inactive'}
                    </span>
                  </div>

                  {org.address && <p className="text-gray-600 mb-1 text-sm"><span className="font-medium">Address:</span> {org.address}</p>}
                  {org.contact_info && <p className="text-gray-600 mb-1 text-sm"><span className="font-medium">Contact:</span> {org.contact_info}</p>}

                  <div className="mt-4 flex justify-between items-center">
                    <div className="text-xs text-gray-500">
                      <div>Warehouses: {org.warehouses_count || 0}</div>
                      <div>Users: {org.users_count || 0}</div>
                    </div>

                    {canManageOrganizations && (
                      <div className="flex space-x-2">
                        <button
                          onClick={() => openModal(org)}
                          className="bg-indigo-500 text-white py-1 px-3 rounded-md hover:bg-indigo-600 text-sm transition-colors"
                        >
                          Edit
                        </button>
                        <button
                          onClick={() => handleDelete(org.id)}
                          className="bg-red-500 text-white py-1 px-3 rounded-md hover:bg-red-600 text-sm transition-colors"
                        >
                          Delete
                        </button>
                      </div>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        )
      ) : (
        // Hierarchy View
        <div className="bg-gray-50 p-6 rounded-lg">
          {loadingHierarchy ? (
            <p className="text-gray-500">Loading hierarchy...</p>
          ) : hierarchyData.length === 0 ? (
            <div className="text-center py-10">
              <h3 className="text-xl font-semibold text-gray-700">No Hierarchy Data</h3>
              <p className="text-gray-500 mt-2">Unable to load organization hierarchy.</p>
            </div>
          ) : (
            <div className="space-y-2">
              {hierarchyData.map(node => renderHierarchyNode(node))}
            </div>
          )}
        </div>
      )}

      {/* Modal */}
      <Modal
        show={showModal}
        onClose={closeModal}
        title={editingOrganization ? "Edit Organization" : "Add New Organization"}
      >
        <OrganizationForm
          initialData={editingOrganization || {}}
          onSubmit={handleCreateOrUpdate}
          onClose={closeModal}
        />
      </Modal>
    </div>
  );
};

export default Organizations;
