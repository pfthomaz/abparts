// frontend/src/pages/Organizations.js

import React, { useState, useEffect, useCallback, useMemo } from 'react';
import { organizationsService } from '../services/organizationsService';
import Modal from '../components/Modal';
import OrganizationForm from '../components/OrganizationForm';

const Organizations = () => {
  const [organizations, setOrganizations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showModal, setShowModal] = useState(false);
  const [editingOrganization, setEditingOrganization] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterType, setFilterType] = useState('all');

  const fetchOrganizations = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await organizationsService.getOrganizations();
      setOrganizations(data);
    } catch (err) {
      setError(err.message || 'Failed to fetch organizations.');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchOrganizations();
  }, [fetchOrganizations]);

  const filteredOrganizations = useMemo(() => {
    return organizations
      .filter(org => {
        if (filterType === 'all') return true;
        return org.type === filterType;
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
      } else {
        await organizationsService.createOrganization(orgData);
      }

      await fetchOrganizations();
      closeModal();
    } catch (err) {
      console.error("Error creating/updating organization:", err);
      // Re-throw to be caught by the form's error handling
      throw err;
    }
  };

  const handleDelete = async (orgId) => {
    if (!window.confirm("Are you sure you want to delete this organization?")) {
      return;
    }
    setError(null);
    try {
      await organizationsService.deleteOrganization(orgId);
      await fetchOrganizations();
    } catch (err) {
      setError(err.message || 'Failed to delete organization.');
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

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold text-gray-800">Organizations</h1>
        <button
          onClick={() => openModal()}
          className="bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition duration-150 ease-in-out font-semibold"
        >
          Add Organization
        </button>
      </div>

      {loading && <p className="text-gray-500">Loading organizations...</p>}
      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative mb-4" role="alert">
          <strong className="font-bold">Error: </strong>
          <span className="block sm:inline">{error}</span>
        </div>
      )}

      {/* Search and Filter Bar */}
      <div className="bg-white p-4 rounded-lg shadow-md mb-6">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label htmlFor="search" className="block text-sm font-medium text-gray-700">Search by Name</label>
            <input
              type="text"
              id="search"
              placeholder="e.g., Customer A..."
              className="mt-1 w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
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
              <option value="Customer">Customer</option>
              <option value="Warehouse">Warehouse</option>
              <option value="Supplier">Supplier</option>
            </select>
          </div>
        </div>
      </div>

      {!loading && filteredOrganizations.length === 0 ? (
        <div className="text-center py-10 bg-white rounded-lg shadow-md">
          <h3 className="text-xl font-semibold text-gray-700">No Organizations Found</h3>
          <p className="text-gray-500 mt-2">
            {organizations.length > 0 ? 'Try adjusting your search or filter criteria.' : 'There are no organizations in the system yet.'}
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-12">
          {filteredOrganizations.map((org) => (
            <div key={org.id} className="bg-gray-50 p-6 rounded-lg shadow-md border border-gray-200">
              <h3 className="text-2xl font-semibold text-blue-700 mb-2">{org.name}</h3>
              <p className="text-gray-600 mb-1"><span className="font-medium">Type:</span> {org.type}</p>
              {org.address && <p className="text-gray-600 mb-1"><span className="font-medium">Address:</span> {org.address}</p>}
              {org.contact_info && <p className="text-gray-600 mb-1"><span className="font-medium">Contact:</span> {org.contact_info}</p>}
              <p className="text-sm text-gray-400 mt-3">ID: {org.id}</p>
              <div className="mt-4 flex space-x-2">
                <button onClick={() => openModal(org)} className="bg-yellow-500 text-white py-1 px-3 rounded-md hover:bg-yellow-600 text-sm">
                  Edit
                </button>
                <button onClick={() => handleDelete(org.id)} className="bg-red-500 text-white py-1 px-3 rounded-md hover:bg-red-600 text-sm">
                  Delete
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

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
