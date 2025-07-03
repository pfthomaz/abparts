// frontend/src/pages/Inventory.js

import React, { useState, useEffect, useCallback } from 'react';
import { useAuth } from '../AuthContext';
import Modal from '../components/Modal';
import InventoryForm from '../components/InventoryForm';

const Inventory = () => {
  const { token } = useAuth();
  const [inventoryItems, setInventoryItems] = useState([]);
  const [organizations, setOrganizations] = useState([]);
  const [parts, setParts] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [showModal, setShowModal] = useState(false);
  const [editingInventory, setEditingInventory] = useState(null);
  const [isEditMode, setIsEditMode] = useState(false);

  const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000';

  const fetchData = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const [inventoryRes, orgsRes, partsRes] = await Promise.all([
        fetch(`${API_BASE_URL}/inventory`, { headers: { 'Authorization': `Bearer ${token}` } }),
        fetch(`${API_BASE_URL}/organizations`, { headers: { 'Authorization': `Bearer ${token}` } }),
        fetch(`${API_BASE_URL}/parts`, { headers: { 'Authorization': `Bearer ${token}` } }),
      ]);

      if (!inventoryRes.ok) throw new Error(`Failed to fetch inventory: ${inventoryRes.status}`);
      if (!orgsRes.ok) throw new Error(`Failed to fetch organizations: ${orgsRes.status}`);
      if (!partsRes.ok) throw new Error(`Failed to fetch parts: ${partsRes.status}`);

      const inventoryData = await inventoryRes.json();
      const orgsData = await orgsRes.json();
      const partsData = await partsRes.json();

      setInventoryItems(inventoryData);
      setOrganizations(orgsData);
      setParts(partsData);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, [token, API_BASE_URL]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const handleCreateOrUpdate = async (inventoryData) => {
    const url = editingInventory
      ? `${API_BASE_URL}/inventory/${editingInventory.id}`
      : `${API_BASE_URL}/inventory`;
    const method = editingInventory ? 'PUT' : 'POST';

    try {
      const response = await fetch(url, {
        method,
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify(inventoryData),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
      }

      await fetchData();
      setShowModal(false);
      setEditingInventory(null);
      setIsEditMode(false);
    } catch (err) {
      console.error("Error creating/updating inventory item:", err);
      throw err;
    }
  };

  const handleDelete = async (inventoryId) => {
    if (!window.confirm("Are you sure you want to delete this inventory item?")) {
      return;
    }
    try {
      const response = await fetch(`${API_BASE_URL}/inventory/${inventoryId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (!response.ok && response.status !== 204) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
      }

      await fetchData();
    } catch (err) {
      setError(err.message);
    }
  };

  const openModal = (inventory = null) => {
    setEditingInventory(inventory);
    setIsEditMode(!!inventory);
    setShowModal(true);
  };

  const closeModal = () => {
    setShowModal(false);
    setEditingInventory(null);
    setIsEditMode(false);
  };

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold text-gray-800">Inventory</h1>
        <button
          onClick={() => openModal()}
          className="bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition duration-150 ease-in-out font-semibold"
        >
          Add Inventory Item
        </button>
      </div>

      {loading && <p>Loading...</p>}
      {error && <p className="text-red-500">{error}</p>}

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-12">
        {inventoryItems.map((item) => (
          <div key={item.id} className="bg-gray-50 p-6 rounded-lg shadow-md border border-gray-200">
            <h3 className="text-2xl font-semibold text-orange-700 mb-2">
              {parts.find(p => p.id === item.part_id)?.name || 'Unknown Part'}
            </h3>
            <p className="text-gray-600 mb-1"><span className="font-medium">Location:</span> {organizations.find(o => o.id === item.organization_id)?.name || 'Unknown Organization'}</p>
            <p className="text-gray-600 mb-1"><span className="font-medium">Current Stock:</span> {item.current_stock}</p>
            <p className="text-gray-600 mb-1"><span className="font-medium">Min Stock Rec:</span> {item.minimum_stock_recommendation}</p>
            {item.reorder_threshold_set_by && <p className="text-gray-600 mb-1"><span className="font-medium">Set By:</span> {item.reorder_threshold_set_by}</p>}
            <p className="text-sm text-gray-400 mt-3">ID: {item.id}</p>
            <div className="mt-4 flex space-x-2">
              <button
                onClick={() => openModal(item)}
                className="bg-yellow-500 text-white py-1 px-3 rounded-md hover:bg-yellow-600 text-sm"
              >
                Edit
              </button>
              <button
                onClick={() => handleDelete(item.id)}
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
        title={editingInventory ? "Edit Inventory Item" : "Add New Inventory Item"}
      >
        <InventoryForm
          initialData={editingInventory || {}}
          organizations={organizations}
          parts={parts}
          onSubmit={handleCreateOrUpdate}
          onClose={closeModal}
          isEditMode={isEditMode}
        />
      </Modal>
    </div>
  );
};

export default Inventory;
