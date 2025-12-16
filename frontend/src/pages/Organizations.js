// frontend/src/pages/Organizations.js

import React, { useState, useEffect, useCallback, useMemo } from 'react';
import { organizationsService, OrganizationType } from '../services/organizationsService';
import { useAuth } from '../AuthContext';
import Modal from '../components/Modal';
import OrganizationForm from '../components/OrganizationForm';
import PermissionGuard from '../components/PermissionGuard';
import { PERMISSIONS } from '../utils/permissions';
import { useTranslation } from '../hooks/useTranslation';
import { getOrganizationTypeConfig } from '../utils/organizationTypeConfig';

const Organizations = () => {
  const { t } = useTranslation();
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

  // Check permissions using the new permission system
  const canManageOrganizations = user?.role === 'super_admin'; // Only super_admin can manage organizations

  const fetchOrganizations = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await organizationsService.getOrganizations();
      const data = response.data || response;
      setOrganizations(data);
    } catch (err) {
      setError(err.message || t('organizations.failedToFetch'));
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
        await organizationsService.updateOrganization(editingOrganization.id, orgData);
        // Refetch the updated organization to get the latest logo_url with cache-busting
        const updatedOrgResponse = await organizationsService.getOrganization(editingOrganization.id);
        const updatedOrg = updatedOrgResponse.data || updatedOrgResponse;
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
    if (!window.confirm(t('organizations.deleteConfirm'))) {
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
      setError(err.response?.data?.detail || err.message || t('organizations.failedToDelete'));
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
    const ORGANIZATION_TYPE_CONFIG = getOrganizationTypeConfig(t);
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
          <PermissionGuard permission={PERMISSIONS.MANAGE_ORGANIZATIONS} hideIfNoPermission={true}>
            <div className="flex space-x-2">
              <button
                onClick={() => openModal(organizations.find(org => org.id === node.id))}
                className="text-indigo-600 hover:text-indigo-900 text-sm"
              >
                {t('users.edit')}
              </button>
              <button
                onClick={() => handleDelete(node.id)}
                className="text-red-600 hover:text-red-900 text-sm"
              >
                {t('common.delete')}
              </button>
            </div>
          </PermissionGuard>
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
          <h1 className="text-3xl font-bold text-gray-800">{t('organizations.title')}</h1>
          <p className="text-gray-600 mt-1">{t('organizations.subtitle')}</p>
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
              {t('organizations.cards')}
            </button>
            <button
              onClick={() => setViewMode('hierarchy')}
              className={`px-4 py-2 text-sm font-medium rounded-r-md border-t border-r border-b ${viewMode === 'hierarchy'
                ? 'bg-indigo-600 text-white border-indigo-600'
                : 'bg-white text-gray-700 border-gray-300 hover:bg-gray-50'
                } -ml-px`}
            >
              {t('organizations.hierarchy')}
            </button>
          </div>

          <PermissionGuard permission={PERMISSIONS.MANAGE_ORGANIZATIONS} hideIfNoPermission={true}>
            <button
              onClick={() => openModal()}
              className="bg-indigo-600 text-white py-2 px-4 rounded-md hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 transition duration-150 ease-in-out font-semibold"
            >
              {t('organizations.addOrganization')}
            </button>
          </PermissionGuard>
        </div>
      </div>

      {/* Loading and Error States */}
      {loading && <p className="text-gray-500">{t('organizations.loadingOrganizations')}</p>}
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
              <label htmlFor="search" className="block text-sm font-medium text-gray-700">{t('organizations.searchByName')}</label>
              <input
                type="text"
                id="search"
                placeholder={t('organizations.searchPlaceholder')}
                className="mt-1 w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-indigo-500 focus:border-indigo-500"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
              />
            </div>
            <div>
              <label htmlFor="filterType" className="block text-sm font-medium text-gray-700">{t('organizations.filterByType')}</label>
              <select
                id="filterType"
                className="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm rounded-md"
                value={filterType}
                onChange={(e) => setFilterType(e.target.value)}
              >
                <option value="all">{t('organizations.allTypes')}</option>
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
            <h3 className="text-xl font-semibold text-gray-700">{t('organizations.noOrganizationsFound')}</h3>
            <p className="text-gray-500 mt-2">
              {organizations.length > 0 ? t('organizations.adjustSearchCriteria') : t('organizations.noOrganizationsYet')}
            </p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-12">
            {filteredOrganizations.map((org) => {
              const config = getOrganizationTypeInfo(org.organization_type);
              return (
                <div key={org.id} className="bg-white p-6 rounded-lg shadow-md border border-gray-200 hover:shadow-lg transition-shadow">
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex items-center space-x-3 flex-1">
                      {/* Organization Logo */}
                      {org.logo_data_url ? (
                        <img
                          src={org.logo_data_url}
                          alt={`${org.name} logo`}
                          className="w-12 h-12 rounded-lg object-contain border border-gray-200 bg-white flex-shrink-0"
                          onError={(e) => {
                            e.target.style.display = 'none';
                          }}
                        />
                      ) : (
                        <div className="w-12 h-12 rounded-lg bg-gray-100 flex items-center justify-center flex-shrink-0 border border-gray-200">
                          <span className="text-gray-400 text-xs">{t('organizations.noLogo')}</span>
                        </div>
                      )}
                      <h3 className="text-xl font-semibold text-gray-900">{org.name}</h3>
                    </div>
                    <span className="text-2xl">{config.icon}</span>
                  </div>

                  <div className="mb-3">
                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${config.color}`}>
                      {config.label}
                    </span>
                  </div>

                  {org.parent_organization_name && (
                    <p className="text-gray-600 mb-2">
                      <span className="font-medium">{t('organizations.parent')}:</span> {org.parent_organization_name}
                    </p>
                  )}

                  <div className="mb-2">
                    <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${org.is_active
                      ? 'bg-green-100 text-green-800'
                      : 'bg-red-100 text-red-800'
                      }`}>
                      {org.is_active ? t('users.activeStatus') : t('users.inactiveStatus')}
                    </span>
                  </div>

                  {org.address && <p className="text-gray-600 mb-1 text-sm"><span className="font-medium">{t('organizations.address')}:</span> {org.address}</p>}
                  {org.contact_info && <p className="text-gray-600 mb-1 text-sm"><span className="font-medium">{t('organizations.contact')}:</span> {org.contact_info}</p>}

                  <div className="mt-4 flex justify-between items-center">
                    <div className="text-xs text-gray-500">
                      <div>{t('organizations.warehouses')}: {org.warehouses_count || 0}</div>
                      <div>{t('users.users')}: {org.users_count || 0}</div>
                    </div>

                    <PermissionGuard permission={PERMISSIONS.MANAGE_ORGANIZATIONS} hideIfNoPermission={true}>
                      <div className="flex space-x-2">
                        <button
                          onClick={() => openModal(org)}
                          className="bg-indigo-500 text-white py-1 px-3 rounded-md hover:bg-indigo-600 text-sm transition-colors"
                        >
                          {t('users.edit')}
                        </button>
                        <button
                          onClick={() => handleDelete(org.id)}
                          className="bg-red-500 text-white py-1 px-3 rounded-md hover:bg-red-600 text-sm transition-colors"
                        >
                          {t('common.delete')}
                        </button>
                      </div>
                    </PermissionGuard>
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
            <p className="text-gray-500">{t('organizations.loadingHierarchy')}</p>
          ) : hierarchyData.length === 0 ? (
            <div className="text-center py-10">
              <h3 className="text-xl font-semibold text-gray-700">{t('organizations.noHierarchyData')}</h3>
              <p className="text-gray-500 mt-2">{t('organizations.unableToLoadHierarchy')}</p>
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
        isOpen={showModal}
        onClose={closeModal}
        title={editingOrganization ? t('organizations.editOrganization') : t('organizations.addNewOrganization')}
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
