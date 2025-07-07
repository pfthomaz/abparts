// frontend/src/pages/Parts.js

import React, { useState, useEffect, useCallback, useMemo } from 'react';
import { partsService } from '../services/partsService';
import Modal from '../components/Modal';
import PartForm from '../components/PartForm';

const Parts = () => {
  const [parts, setParts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showModal, setShowModal] = useState(false);
  const [editingPart, setEditingPart] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterProprietary, setFilterProprietary] = useState('all');
  const [filterConsumable, setFilterConsumable] = useState('all');

  const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000';

  const fetchParts = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await partsService.getParts();
      setParts(data);
    } catch (err) {
      setError(err.message || 'Failed to fetch parts.');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchParts();
  }, [fetchParts]);

  const filteredParts = useMemo(() => {
    return parts
      .filter(part => {
        if (!searchTerm) return true;
        const term = searchTerm.toLowerCase();
        return (
          part.name.toLowerCase().includes(term) ||
          part.part_number.toLowerCase().includes(term)
        );
      })
      .filter(part => {
        if (filterProprietary === 'all') return true;
        return part.is_proprietary === (filterProprietary === 'yes');
      })
      .filter(part => {
        if (filterConsumable === 'all') return true;
        return part.is_consumable === (filterConsumable === 'yes');
      });
  }, [parts, searchTerm, filterProprietary, filterConsumable]);

  const handleCreateOrUpdate = async (partData) => {
    try {
      if (editingPart) {
        await partsService.updatePart(editingPart.id, partData);
      } else {
        await partsService.createPart(partData);
      }

      await fetchParts();
      setShowModal(false);
      setEditingPart(null);
    } catch (err) {
      console.error("Error creating/updating part:", err);
      // Re-throw to be caught by the form's error handling
      throw err;
    }
  };

  const handleDelete = async (partId) => {
    if (!window.confirm("Are you sure you want to delete this part?")) {
      return;
    }
    setError(null);
    try {
      await partsService.deletePart(partId);
      await fetchParts();
    } catch (err) {
      setError(err.message || 'Failed to delete part.');
    }
  };

  const openModal = (part = null) => {
    setEditingPart(part);
    setShowModal(true);
  };

  const closeModal = () => {
    setShowModal(false);
    setEditingPart(null);
  };

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold text-gray-800">Parts</h1>
        <button
          onClick={() => openModal()}
          className="bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition duration-150 ease-in-out font-semibold"
        >
          Add Part
        </button>
      </div>

      {loading && <p className="text-gray-500">Loading parts...</p>}
      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative mb-4" role="alert">
          <strong className="font-bold">Error: </strong>
          <span className="block sm:inline">{error}</span>
        </div>
      )}

      {/* Search and Filter Bar */}
      <div className="bg-white p-4 rounded-lg shadow-md mb-6">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="md:col-span-1">
            <label htmlFor="search" className="block text-sm font-medium text-gray-700">Search</label>
            <input
              type="text"
              id="search"
              placeholder="By name or number..."
              className="mt-1 w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </div>
          <div>
            <label htmlFor="filterProprietary" className="block text-sm font-medium text-gray-700">Proprietary</label>
            <select
              id="filterProprietary"
              className="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm rounded-md"
              value={filterProprietary}
              onChange={(e) => setFilterProprietary(e.target.value)}
            >
              <option value="all">All</option>
              <option value="yes">Yes</option>
              <option value="no">No</option>
            </select>
          </div>
          <div>
            <label htmlFor="filterConsumable" className="block text-sm font-medium text-gray-700">Consumable</label>
            <select
              id="filterConsumable"
              className="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm rounded-md"
              value={filterConsumable}
              onChange={(e) => setFilterConsumable(e.target.value)}
            >
              <option value="all">All</option>
              <option value="yes">Yes</option>
              <option value="no">No</option>
            </select>
          </div>
        </div>
      </div>

      {!loading && filteredParts.length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-12">
          {filteredParts.map((part) => (
          <div key={part.id} className="bg-gray-50 p-6 rounded-lg shadow-md border border-gray-200">
            <h3 className="text-2xl font-semibold text-purple-700 mb-2">{part.name}</h3>
            <p className="text-gray-600 mb-1"><span className="font-medium">Part #:</span> {part.part_number}</p>
            {part.description && <p className="text-gray-600 mb-1"><span className="font-medium">Description:</span> {part.description}</p>}
            <p className="text-gray-600 mb-1">
              <span className="font-medium">Proprietary:</span> {part.is_proprietary ? 'Yes' : 'No'}
            </p>
            <p className="text-gray-600 mb-1">
              <span className="font-medium">Consumable:</span> {part.is_consumable ? 'Yes' : 'No'}
            </p>
            {part.image_urls && part.image_urls.length > 0 && (
              <div className="mt-3">
                <span className="font-medium text-gray-600">Images:</span>
                <div className="grid grid-cols-2 gap-2 mt-1">
                  {part.image_urls.map((imageUrl, imgIndex) => (
                    <img
                      key={imgIndex}
                      src={`${API_BASE_URL}${imageUrl}`}
                      alt={`Part Image ${imgIndex + 1}`}
                      className="w-full h-24 object-cover rounded-md shadow-sm"
                      onError={(e) => {
                        e.target.onerror = null;
                        e.target.src = "https://placehold.co/100x100?text=Image+Error";
                      }}
                    />
                  ))}
                </div>
              </div>
            )}
            <p className="text-sm text-gray-400 mt-3">ID: {part.id}</p>
            <div className="mt-4 flex space-x-2">
              <button
                onClick={() => openModal(part)}
                className="bg-yellow-500 text-white py-1 px-3 rounded-md hover:bg-yellow-600 text-sm"
              >
                Edit
              </button>
              <button
                onClick={() => handleDelete(part.id)}
                className="bg-red-500 text-white py-1 px-3 rounded-md hover:bg-red-600 text-sm"
              >
                Delete
              </button>
            </div>
          </div>
          ))}
        </div>
      )}

      {!loading && filteredParts.length === 0 && (
        <div className="text-center py-10 bg-white rounded-lg shadow-md">
          <h3 className="text-xl font-semibold text-gray-700">No Parts Found</h3>
          <p className="text-gray-500 mt-2">
            {parts.length > 0 ? 'Try adjusting your search or filter criteria.' : 'There are no parts in the system yet.'}
          </p>
        </div>
      )}

      <Modal
        show={showModal}
        onClose={closeModal}
        title={editingPart ? "Edit Part" : "Add New Part"}
      >
        <PartForm
          initialData={editingPart || {}}
          onSubmit={handleCreateOrUpdate}
          onClose={closeModal}
        />
      </Modal>
    </div>
  );
};

export default Parts;
