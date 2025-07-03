// frontend/src/pages/Organizations.js

import React, { useState, useEffect, useCallback } from 'react';
import { useAuth } from '../AuthContext';
import Modal from '../components/Modal';
import OrganizationForm from '../components/OrganizationForm';

const Organizations = () => {
  const { token } = useAuth();
  const [organizations, setOrganizations] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [showModal, setShowModal] = useState(false);
  const [editingOrganization, setEditingOrganization] = useState(null);

  const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000';

  const fetchOrganizations = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`${API_BASE_URL}/organizations`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });
      if (!response.ok) {
        throw new Error(`Failed to fetch organizations: ${response.status}`);
      }
      const data = await response.json();
      setOrganizations(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, [token, API_BASE_URL]);

  useEffect(() => {
    fetchOrganizations();
  }, [fetchOrganizations]);

  const handleCreateOrUpdate = async (orgData) => {
    const url = editingOrganization
      ? `${API_BASE_URL}/organizations/${editingOrganization.id}`
      : `${API_BASE_URL}/organizations`;
    const method = editingOrganization ? 'PUT' : 'POST';

    try {
      const response = await fetch(url, {
        method,
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify(orgData),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
      }

      await fetchOrganizations();
      setShowModal(false);
      setEditingOrganization(null);
    } catch (err) {
      console.error("Error creating/updating organization:", err);
      throw err;
    }
  };

  const handleDelete = async (orgId) => {
    if (!window.confirm("Are you sure you want to delete this organization?")) {
      return;
    }
    try {
      const response = await fetch(`${API_BASE_URL}/organizations/${orgId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (!response.ok && response.status !== 204) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
      }

      await fetchOrganizations();
    } catch (err) {
      setError(err.message);
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

      {loading && <p>Loading...</p>}
      {error && <p className="text-red-500">{error}</p>}

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-12">
        {organizations.map((org) => (
          <div key={org.id} className="bg-gray-50 p-6 rounded-lg shadow-md border border-gray-200">
            <h3 className="text-2xl font-semibold text-blue-700 mb-2">{org.name}</h3>
            <p className="text-gray-600 mb-1"><span className="font-medium">Type:</span> {org.type}</p>
            {org.address && <p className="text-gray-600 mb-1"><span className="font-medium">Address:</span> {org.address}</p>}
            {org.contact_info && <p className="text-gray-600 mb-1"><span className="font-medium">Contact:</span> {org.contact_info}</p>}
            <p className="text-sm text-gray-400 mt-3">ID: {org.id}</p>
            <div className="mt-4 flex space-x-2">
              <button
                onClick={() => openModal(org)}
                className="bg-yellow-500 text-white py-1 px-3 rounded-md hover:bg-yellow-600 text-sm"
              >
                Edit
              </button>
              <button
                onClick={() => handleDelete(org.id)}
                className="bg-red-500 text-white py-1 px-3 rounded-md hover:bg-red-600 text-sm"
              >
                Delete
              </button>
            </div>
          </div>
        ))}
      </div>

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
