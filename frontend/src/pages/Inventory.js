// frontend/src/pages/Inventory.js

import React, { useState, useEffect, useCallback, useMemo } from 'react';
import { inventoryService } from '../services/inventoryService';
import { api } from '../services/api'; // For fetching related data
import Modal from '../components/Modal';
import InventoryForm from '../components/InventoryForm';

const Inventory = () => {
  const [inventoryItems, setInventoryItems] = useState([]);
  const [organizations, setOrganizations] = useState([]);
  const [parts, setParts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showModal, setShowModal] = useState(false);
  const [editingInventory, setEditingInventory] = useState(null);
  const [isEditMode, setIsEditMode] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterOrgId, setFilterOrgId] = useState('all');

  const fetchData = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const [inventoryData, orgsData, partsData] = await Promise.all([
        inventoryService.getInventory(),
        api.get('/organizations'),
        api.get('/parts'),
      ]);

      setInventoryItems(inventoryData);
      setOrganizations(orgsData);
      setParts(partsData);
    } catch (err) {
      setError(err.message || 'Failed to fetch inventory data.');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const partsMap = useMemo(() => {
    return new Map(parts.map(p => [p.id, p]));
  }, [parts]);

  const organizationsMap = useMemo(() => {
    return new Map(organizations.map(o => [o.id, o]));
  }, [organizations]);

  const filteredInventoryItems = useMemo(() => {
    return inventoryItems
      .map(item => {
        // Augment item with part and organization details for easier filtering and display
        // Using Maps for O(1) lookup is much more performant than Array.find() in a loop
        const part = partsMap.get(item.part_id);
        const organization = organizationsMap.get(item.organization_id);
        return {
          ...item,
          partName: part ? part.name : 'Unknown Part',
          partNumber: part ? part.part_number : '',
          organizationName: organization ? organization.name : 'Unknown Organization',
        };
      })
      .filter(item => {
        if (filterOrgId === 'all') return true;
        return item.organization_id === filterOrgId;
      })
      .filter(item => {
        if (!searchTerm) return true;
        const term = searchTerm.toLowerCase();
        return item.partName.toLowerCase().includes(term) || item.partNumber.toLowerCase().includes(term);
      });
  }, [inventoryItems, partsMap, organizationsMap, searchTerm, filterOrgId]);

  const handleCreateOrUpdate = async (inventoryData) => {
    try {
      if (editingInventory) {
        await inventoryService.updateInventoryItem(editingInventory.id, inventoryData);
      } else {
        await inventoryService.createInventoryItem(inventoryData);
      }

      await fetchData();
      closeModal();
    } catch (err) {
      console.error("Error creating/updating inventory item:", err);
      // Re-throw to be caught by the form's error handling
      throw err;
    }
  };

  const handleDelete = async (inventoryId) => {
    if (!window.confirm("Are you sure you want to delete this inventory item?")) {
      return;
    }
    setError(null);
    try {
      await inventoryService.deleteInventoryItem(inventoryId);
      await fetchData();
    } catch (err) {
      setError(err.message || 'Failed to delete inventory item.');
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

      {loading && <p className="text-gray-500">Loading inventory...</p>}
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
            <label htmlFor="search" className="block text-sm font-medium text-gray-700">Search by Part</label>
            <input
              type="text"
              id="search"
              placeholder="Name or number..."
              className="mt-1 w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </div>
          <div>
            <label htmlFor="filterOrganization" className="block text-sm font-medium text-gray-700">Filter by Organization</label>
            <select
              id="filterOrganization"
              className="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm rounded-md"
              value={filterOrgId}
              onChange={(e) => setFilterOrgId(e.target.value)}
            >
              <option value="all">All Organizations</option>
              {organizations.map(org => (
                <option key={org.id} value={org.id}>{org.name}</option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {!loading && filteredInventoryItems.length === 0 ? (
        <div className="text-center py-10 bg-white rounded-lg shadow-md">
          <h3 className="text-xl font-semibold text-gray-700">No Inventory Items Found</h3>
          <p className="text-gray-500 mt-2">
            {inventoryItems.length > 0 ? 'Try adjusting your search or filter criteria.' : 'There are no inventory items in the system yet.'}
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-12">
          {filteredInventoryItems.map((item) => (
            <div key={item.id} className="bg-gray-50 p-6 rounded-lg shadow-md border border-gray-200">
              <h3 className="text-2xl font-semibold text-orange-700 mb-2">
                {item.partName}
              </h3>
              <p className="text-gray-600 mb-1"><span className="font-medium">Location:</span> {item.organizationName}</p>
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
      )}

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
