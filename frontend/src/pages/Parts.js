// frontend/src/pages/Parts.js

import React, { useState, useEffect, useCallback } from 'react';
import { useAuth } from '../AuthContext';
import Modal from '../components/Modal';
import PartForm from '../components/PartForm';

const Parts = () => {
  const { token } = useAuth();
  const [parts, setParts] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [showModal, setShowModal] = useState(false);
  const [editingPart, setEditingPart] = useState(null);

  const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000';

  const fetchParts = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`${API_BASE_URL}/parts`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });
      if (!response.ok) {
        throw new Error(`Failed to fetch parts: ${response.status}`);
      }
      const data = await response.json();
      setParts(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, [token, API_BASE_URL]);

  useEffect(() => {
    fetchParts();
  }, [fetchParts]);

  const handleCreateOrUpdate = async (partData) => {
    const url = editingPart
      ? `${API_BASE_URL}/parts/${editingPart.id}`
      : `${API_BASE_URL}/parts`;
    const method = editingPart ? 'PUT' : 'POST';

    try {
      const response = await fetch(url, {
        method,
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify(partData),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
      }

      await fetchParts();
      setShowModal(false);
      setEditingPart(null);
    } catch (err) {
      console.error("Error creating/updating part:", err);
      throw err;
    }
  };

  const handleDelete = async (partId) => {
    if (!window.confirm("Are you sure you want to delete this part?")) {
      return;
    }
    try {
      const response = await fetch(`${API_BASE_URL}/parts/${partId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (!response.ok && response.status !== 204) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
      }

      await fetchParts();
    } catch (err) {
      setError(err.message);
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

      {loading && <p>Loading...</p>}
      {error && <p className="text-red-500">{error}</p>}

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-12">
        {parts.map((part) => (
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
