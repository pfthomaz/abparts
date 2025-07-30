// frontend/src/pages/OrganizationManagement.js

import React, { useState } from 'react';
import { useAuth } from '../AuthContext';
import OrganizationHierarchy from '../components/OrganizationHierarchy';
import SupplierManager from '../components/SupplierManager';
import OrganizationWarehouseWorkflow from '../components/OrganizationWarehouseWorkflow';
import { isSuperAdmin, isAdmin } from '../utils/permissions';

const OrganizationManagement = () => {
  const { user } = useAuth();
  const [selectedOrganization, setSelectedOrganization] = useState(null);
  const [activeTab, setActiveTab] = useState('hierarchy');

  // Handle organization selection from hierarchy
  const handleOrganizationSelect = (organization) => {
    setSelectedOrganization(organization);
    // Auto-switch to suppliers tab if a customer organization is selected
    if (organization.organization_type === 'customer') {
      setActiveTab('suppliers');
    }
  };

  const tabs = [
    { id: 'hierarchy', name: 'Organization Hierarchy', icon: '🌳' },
    { id: 'suppliers', name: 'Supplier Management', icon: '📦' },
    { id: 'warehouses', name: 'Warehouse Management', icon: '🏪' }
  ];

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="px-4 py-6 sm:px-0">
          <div className="border-b border-gray-200 pb-5">
            <h1 className="text-3xl font-bold leading-6 text-gray-900">
              Organization Management
            </h1>
            <p className="mt-2 max-w-4xl text-sm text-gray-500">
              Manage organizations, suppliers, and warehouses with enhanced UI components
            </p>
          </div>
        </div>

        {/* Selected Organization Info */}
        {selectedOrganization && (
          <div className="px-4 sm:px-0 mb-6">
            <div className="bg-white overflow-hidden shadow rounded-lg">
              <div className="px-4 py-5 sm:p-6">
                <div className="flex items-center space-x-3">
                  <div className="flex-shrink-0">
                    <span className="text-2xl">🏢</span>
                  </div>
                  <div className="flex-1">
                    <h3 className="text-lg leading-6 font-medium text-gray-900">
                      Selected: {selectedOrganization.name}
                    </h3>
                    <p className="mt-1 max-w-2xl text-sm text-gray-500">
                      {selectedOrganization.organization_type} organization
                      {selectedOrganization.country && ` • ${selectedOrganization.country}`}
                    </p>
                  </div>
                  <button
                    onClick={() => setSelectedOrganization(null)}
                    className="text-gray-400 hover:text-gray-600"
                  >
                    <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Tab Navigation */}
        <div className="px-4 sm:px-0">
          <div className="border-b border-gray-200">
            <nav className="-mb-px flex space-x-8" aria-label="Tabs">
              {tabs.map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`${activeTab === tab.id
                      ? 'border-indigo-500 text-indigo-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                    } whitespace-nowrap py-2 px-1 border-b-2 font-medium text-sm flex items-center space-x-2`}
                >
                  <span>{tab.icon}</span>
                  <span>{tab.name}</span>
                </button>
              ))}
            </nav>
          </div>
        </div>

        {/* Tab Content */}
        <div className="px-4 sm:px-0 mt-6">
          {activeTab === 'hierarchy' && (
            <div className="bg-white shadow rounded-lg p-6">
              <OrganizationHierarchy
                onOrganizationSelect={handleOrganizationSelect}
                selectedOrganizationId={selectedOrganization?.id}
              />
            </div>
          )}

          {activeTab === 'suppliers' && (
            <div className="bg-white shadow rounded-lg p-6">
              {selectedOrganization ? (
                <SupplierManager
                  organizationId={selectedOrganization.id}
                  onSupplierChange={() => {
                    // Refresh hierarchy when suppliers change
                    console.log('Supplier changed, refreshing data...');
                  }}
                />
              ) : (
                <div className="text-center py-12">
                  <div className="mx-auto flex items-center justify-center h-12 w-12 rounded-full bg-gray-100">
                    <span className="text-2xl">📦</span>
                  </div>
                  <h3 className="mt-2 text-sm font-medium text-gray-900">No organization selected</h3>
                  <p className="mt-1 text-sm text-gray-500">
                    Select an organization from the hierarchy to manage its suppliers.
                  </p>
                </div>
              )}
            </div>
          )}

          {activeTab === 'warehouses' && (
            <div className="bg-white shadow rounded-lg p-6">
              {selectedOrganization ? (
                <OrganizationWarehouseWorkflow
                  organizationId={selectedOrganization.id}
                  onWarehouseCreated={(warehouse) => {
                    console.log('Warehouse created:', warehouse);
                  }}
                />
              ) : (
                <div className="text-center py-12">
                  <div className="mx-auto flex items-center justify-center h-12 w-12 rounded-full bg-gray-100">
                    <span className="text-2xl">🏪</span>
                  </div>
                  <h3 className="mt-2 text-sm font-medium text-gray-900">No organization selected</h3>
                  <p className="mt-1 text-sm text-gray-500">
                    Select an organization from the hierarchy to manage its warehouses.
                  </p>
                </div>
              )}
            </div>
          )}
        </div>

        {/* Permission Notice */}
        {!isSuperAdmin(user) && !isAdmin(user) && (
          <div className="px-4 sm:px-0 mt-6">
            <div className="bg-yellow-50 border border-yellow-200 rounded-md p-4">
              <div className="flex">
                <div className="flex-shrink-0">
                  <svg className="h-5 w-5 text-yellow-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                    <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                  </svg>
                </div>
                <div className="ml-3">
                  <h3 className="text-sm font-medium text-yellow-800">
                    Limited Access
                  </h3>
                  <div className="mt-2 text-sm text-yellow-700">
                    <p>
                      Some organization management features may be limited based on your role.
                      Contact your administrator for additional permissions.
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default OrganizationManagement;