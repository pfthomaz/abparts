// frontend/src/pages/WarehouseLocations.js

import { useState, useEffect, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useTranslation } from '../hooks/useTranslation';
import { warehouseLocationsService } from '../services/warehouseLocationsService';
import { warehouseService } from '../services/warehouseService';
import { api } from '../services/api';
import Modal from '../components/Modal';

const WarehouseLocations = () => {
  const { warehouse_id } = useParams();
  const navigate = useNavigate();
  const { t } = useTranslation();

  const [warehouse, setWarehouse] = useState(null);
  const [locations, setLocations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  // Modal states
  const [showAddModal, setShowAddModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [editingLocation, setEditingLocation] = useState(null);
  const [deletingLocation, setDeletingLocation] = useState(null);
  const [formLoading, setFormLoading] = useState(false);

  // Form state
  const [formData, setFormData] = useState({ location_code: '', description: '' });
  const [formError, setFormError] = useState('');

  // Label printing / selection mode state
  const [selectionMode, setSelectionMode] = useState(false);
  const [selectedIds, setSelectedIds] = useState(new Set());
  const [labelLoading, setLabelLoading] = useState(false);

  // Assign parts modal state
  const [showAssignModal, setShowAssignModal] = useState(false);
  const [assigningLocation, setAssigningLocation] = useState(null);
  const [locationParts, setLocationParts] = useState([]);
  const [warehouseInventory, setWarehouseInventory] = useState([]);
  const [inventorySearch, setInventorySearch] = useState('');
  const [assignLoading, setAssignLoading] = useState(false);
  const [partsLoading, setPartsLoading] = useState(false);

  const fetchWarehouse = useCallback(async () => {
    try {
      const data = await warehouseService.getWarehouse(warehouse_id);
      setWarehouse(data);
    } catch (err) {
      console.error('Failed to fetch warehouse:', err);
      setError('Failed to load warehouse details');
    }
  }, [warehouse_id]);

  const fetchLocations = useCallback(async () => {
    try {
      const data = await warehouseLocationsService.getLocations(warehouse_id);
      setLocations(data);
    } catch (err) {
      console.error('Failed to fetch locations:', err);
      setError('Failed to load locations');
    }
  }, [warehouse_id]);

  useEffect(() => {
    const loadData = async () => {
      setLoading(true);
      await Promise.all([fetchWarehouse(), fetchLocations()]);
      setLoading(false);
    };
    loadData();
  }, [fetchWarehouse, fetchLocations]);

  // Stats
  const totalLocations = locations.length;
  const occupiedLocations = locations.filter(loc => (loc.parts_count || 0) > 0).length;
  const emptyLocations = totalLocations - occupiedLocations;

  // Handlers
  const handleOpenAdd = () => {
    setFormData({ location_code: '', description: '' });
    setFormError('');
    setShowAddModal(true);
  };

  const handleOpenEdit = (location) => {
    setEditingLocation(location);
    setFormData({
      location_code: location.location_code,
      description: location.description || '',
    });
    setFormError('');
    setShowEditModal(true);
  };

  const handleOpenDelete = (location) => {
    setDeletingLocation(location);
    setShowDeleteConfirm(true);
  };

  const handleCreateLocation = async (e) => {
    e.preventDefault();
    if (!formData.location_code.trim()) {
      setFormError(t('warehouseLocations.locationCodeRequired') || 'Location code is required');
      return;
    }

    setFormLoading(true);
    setFormError('');
    try {
      await warehouseLocationsService.createLocation(warehouse_id, {
        location_code: formData.location_code.trim(),
        description: formData.description.trim() || null,
      });
      setShowAddModal(false);
      await fetchLocations();
    } catch (err) {
      const detail = err?.response?.data?.detail || err.message || 'Failed to create location';
      setFormError(detail);
    } finally {
      setFormLoading(false);
    }
  };

  const handleUpdateLocation = async (e) => {
    e.preventDefault();
    if (!formData.location_code.trim()) {
      setFormError(t('warehouseLocations.locationCodeRequired') || 'Location code is required');
      return;
    }

    setFormLoading(true);
    setFormError('');
    try {
      await warehouseLocationsService.updateLocation(editingLocation.id, {
        location_code: formData.location_code.trim(),
        description: formData.description.trim() || null,
      });
      setShowEditModal(false);
      setEditingLocation(null);
      await fetchLocations();
    } catch (err) {
      const detail = err?.response?.data?.detail || err.message || 'Failed to update location';
      setFormError(detail);
    } finally {
      setFormLoading(false);
    }
  };

  const handleDeleteLocation = async () => {
    setFormLoading(true);
    try {
      await warehouseLocationsService.deleteLocation(deletingLocation.id);
      setShowDeleteConfirm(false);
      setDeletingLocation(null);
      await fetchLocations();
    } catch (err) {
      const detail = err?.response?.data?.detail || err.message || 'Failed to delete location';
      setError(detail);
      setShowDeleteConfirm(false);
      setDeletingLocation(null);
    } finally {
      setFormLoading(false);
    }
  };

  // Label printing handlers
  const handleEnterSelectionMode = () => {
    setSelectionMode(true);
    setSelectedIds(new Set());
  };

  const handleExitSelectionMode = () => {
    setSelectionMode(false);
    setSelectedIds(new Set());
  };

  const handleToggleSelect = (locationId) => {
    setSelectedIds((prev) => {
      const next = new Set(prev);
      if (next.has(locationId)) {
        next.delete(locationId);
      } else {
        next.add(locationId);
      }
      return next;
    });
  };

  const handleSelectAll = () => {
    if (selectedIds.size === locations.length) {
      setSelectedIds(new Set());
    } else {
      setSelectedIds(new Set(locations.map((loc) => loc.id)));
    }
  };

  const handlePrintSelected = async () => {
    if (selectedIds.size === 0) return;
    setLabelLoading(true);
    setError('');
    try {
      await warehouseLocationsService.generateLabels(warehouse_id, Array.from(selectedIds));
      handleExitSelectionMode();
    } catch (err) {
      setError(err.message || 'Failed to generate labels');
    } finally {
      setLabelLoading(false);
    }
  };

  const handlePrintAll = async () => {
    setLabelLoading(true);
    setError('');
    try {
      await warehouseLocationsService.generateAllLabels(warehouse_id);
      handleExitSelectionMode();
    } catch (err) {
      setError(err.message || 'Failed to generate labels');
    } finally {
      setLabelLoading(false);
    }
  };

  // --- Assign Parts Handlers ---
  const handleOpenAssign = async (location) => {
    setAssigningLocation(location);
    setShowAssignModal(true);
    setPartsLoading(true);
    setInventorySearch('');

    try {
      // Fetch parts currently at this location
      const parts = await warehouseLocationsService.getPartsAtLocation(location.id);
      setLocationParts(parts || []);

      // Fetch all inventory for this warehouse
      const inventory = await api.get(`/inventory/warehouse/${warehouse_id}?limit=500`);
      setWarehouseInventory(inventory || []);
    } catch (err) {
      console.error('Failed to load assign data:', err);
      setError(err.message || 'Failed to load inventory data');
    } finally {
      setPartsLoading(false);
    }
  };

  const handleAssignPart = async (inventoryId) => {
    setAssignLoading(true);
    try {
      const updatedParts = await warehouseLocationsService.assignParts(assigningLocation.id, [inventoryId]);
      setLocationParts(updatedParts || []);
      await fetchLocations(); // Refresh parts_count on cards
    } catch (err) {
      const detail = err?.response?.data?.detail || err.message || 'Failed to assign part';
      setError(detail);
    } finally {
      setAssignLoading(false);
    }
  };

  const handleUnassignPart = async (inventoryId) => {
    setAssignLoading(true);
    try {
      await warehouseLocationsService.unassignPart(assigningLocation.id, inventoryId);
      setLocationParts((prev) => prev.filter((p) => p.inventory_id !== inventoryId));
      await fetchLocations(); // Refresh parts_count on cards
    } catch (err) {
      const detail = err?.response?.data?.detail || err.message || 'Failed to unassign part';
      setError(detail);
    } finally {
      setAssignLoading(false);
    }
  };

  // Filter inventory for the search box, excluding already-assigned parts
  const assignedInventoryIds = new Set(locationParts.map((p) => p.inventory_id));
  const filteredInventory = warehouseInventory.filter((item) => {
    if (assignedInventoryIds.has(item.id)) return false;
    if (!inventorySearch.trim()) return true;
    const search = inventorySearch.toLowerCase();
    const partName = (item.part_name || '').toLowerCase();
    const partNumber = (item.part_number || '').toLowerCase();
    return partName.includes(search) || partNumber.includes(search);
  });

  // Loading state
  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-gray-500 text-lg">
          {t('common.loading') || 'Loading...'}
        </div>
      </div>
    );
  }

  return (
    <div className={`space-y-6 ${selectionMode ? 'pb-24 sm:pb-20' : ''}`}>
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <button
              onClick={() => navigate('/warehouses')}
              className="text-blue-600 hover:text-blue-800 text-sm"
            >
              ← {t('warehouseLocations.backToWarehouses') || 'Back to Warehouses'}
            </button>
          </div>
          <h1 className="text-2xl font-bold text-gray-900">
            {t('warehouseLocations.title') || 'Locations'}
          </h1>
          {warehouse && (
            <p className="text-gray-600">
              {warehouse.name} — {t('warehouseLocations.subtitle') || 'Manage shelf locations'}
            </p>
          )}
        </div>

        <div className="flex items-center gap-2">
          {locations.length > 0 && !selectionMode && (
            <button
              onClick={handleEnterSelectionMode}
              className="bg-purple-600 text-white px-4 py-2 rounded-md hover:bg-purple-700 focus:outline-none focus:ring-2 focus:ring-purple-500 whitespace-nowrap"
            >
              🏷️ {t('warehouseLocations.printLabels') || 'Print Labels'}
            </button>
          )}
          <button
            onClick={handleOpenAdd}
            className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 whitespace-nowrap"
          >
            + {t('warehouseLocations.addLocation') || 'Add Location'}
          </button>
        </div>
      </div>

      {/* Error */}
      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
          {error}
          <button
            onClick={() => setError('')}
            className="ml-2 text-red-500 hover:text-red-700 font-bold"
          >
            ×
          </button>
        </div>
      )}

      {/* Quick Stats */}
      <div className="grid grid-cols-3 gap-4">
        <div className="bg-white rounded-lg border border-gray-200 p-4 text-center">
          <div className="text-2xl font-bold text-gray-900">{totalLocations}</div>
          <div className="text-sm text-gray-500">
            {t('warehouseLocations.totalLocations') || 'Total Locations'}
          </div>
        </div>
        <div className="bg-white rounded-lg border border-green-200 p-4 text-center">
          <div className="text-2xl font-bold text-green-700">{occupiedLocations}</div>
          <div className="text-sm text-gray-500">
            {t('warehouseLocations.occupied') || 'Occupied'}
          </div>
        </div>
        <div className="bg-white rounded-lg border border-gray-200 p-4 text-center">
          <div className="text-2xl font-bold text-gray-500">{emptyLocations}</div>
          <div className="text-sm text-gray-500">
            {t('warehouseLocations.empty') || 'Empty'}
          </div>
        </div>
      </div>

      {/* Locations Grid */}
      {locations.length === 0 ? (
        <div className="bg-white rounded-lg border border-gray-200 p-12 text-center">
          <div className="text-gray-400 text-5xl mb-4">📍</div>
          <h3 className="text-lg font-medium text-gray-700 mb-2">
            {t('warehouseLocations.noLocations') || 'No locations yet'}
          </h3>
          <p className="text-gray-500 mb-4">
            {t('warehouseLocations.noLocationsDescription') || 'Create your first shelf location to start organizing parts.'}
          </p>
          <button
            onClick={handleOpenAdd}
            className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700"
          >
            + {t('warehouseLocations.addLocation') || 'Add Location'}
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
          {selectionMode && (
            <div className="col-span-full flex items-center gap-3 mb-2">
              <label className="flex items-center gap-2 text-sm text-gray-700 cursor-pointer">
                <input
                  type="checkbox"
                  checked={selectedIds.size === locations.length && locations.length > 0}
                  onChange={handleSelectAll}
                  className="w-4 h-4 text-purple-600 rounded border-gray-300 focus:ring-purple-500"
                />
                {t('warehouseLocations.selectAll') || 'Select All'}
              </label>
              <span className="text-sm text-gray-500">
                ({selectedIds.size}/{locations.length} {t('warehouseLocations.selected') || 'selected'})
              </span>
            </div>
          )}
          {locations.map((location) => {
            const hasParts = (location.parts_count || 0) > 0;
            const isSelected = selectedIds.has(location.id);
            return (
              <div
                key={location.id}
                className={`bg-white rounded-lg border-2 shadow-sm hover:shadow-md transition-shadow relative ${
                  selectionMode && isSelected
                    ? 'border-purple-400 ring-2 ring-purple-200'
                    : hasParts
                    ? 'border-green-300 bg-green-50'
                    : 'border-gray-200'
                }`}
                onClick={selectionMode ? () => handleToggleSelect(location.id) : undefined}
                style={selectionMode ? { cursor: 'pointer' } : undefined}
              >
                {/* Selection checkbox */}
                {selectionMode && (
                  <div className="absolute top-3 right-3">
                    <input
                      type="checkbox"
                      checked={isSelected}
                      onChange={() => handleToggleSelect(location.id)}
                      onClick={(e) => e.stopPropagation()}
                      className="w-5 h-5 text-purple-600 rounded border-gray-300 focus:ring-purple-500"
                    />
                  </div>
                )}
                {/* Card Content */}
                <div className="p-4">
                  {/* Location Code */}
                  <div className="flex justify-between items-start mb-2">
                    <h3 className="text-xl font-bold text-gray-900">
                      {location.location_code}
                    </h3>
                    <span
                      className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium ${
                        hasParts
                          ? 'bg-green-100 text-green-800'
                          : 'bg-gray-100 text-gray-600'
                      }`}
                    >
                      {location.parts_count || 0} {t('warehouseLocations.parts') || 'parts'}
                    </span>
                  </div>

                  {/* Description */}
                  {location.description && (
                    <p className="text-sm text-gray-600 mb-3 line-clamp-2">
                      {location.description}
                    </p>
                  )}

                  {!location.description && (
                    <p className="text-sm text-gray-400 italic mb-3">
                      {t('warehouseLocations.noDescription') || 'No description'}
                    </p>
                  )}

                  {/* Actions */}
                  {!selectionMode && (
                    <div className="flex justify-end gap-2 pt-2 border-t border-gray-100">
                      <button
                        onClick={() => handleOpenAssign(location)}
                        className="text-green-600 hover:text-green-800 text-sm font-medium"
                      >
                        📦 {t('warehouseLocations.manageParts') || 'Parts'}
                      </button>
                      <button
                        onClick={() => handleOpenEdit(location)}
                        className="text-indigo-600 hover:text-indigo-800 text-sm font-medium"
                      >
                        {t('common.edit') || 'Edit'}
                      </button>
                      <button
                        onClick={() => handleOpenDelete(location)}
                        className="text-red-600 hover:text-red-800 text-sm font-medium"
                      >
                        {t('common.delete') || 'Delete'}
                      </button>
                    </div>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Add Location Modal */}
      <Modal
        isOpen={showAddModal}
        onClose={() => setShowAddModal(false)}
        title={t('warehouseLocations.addLocation') || 'Add Location'}
        size="small"
      >
        <form onSubmit={handleCreateLocation} className="space-y-4">
          {formError && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-3 py-2 rounded text-sm">
              {formError}
            </div>
          )}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              {t('warehouseLocations.locationCode') || 'Location Code'} *
            </label>
            <input
              type="text"
              value={formData.location_code}
              onChange={(e) => setFormData({ ...formData, location_code: e.target.value })}
              placeholder="e.g. A1, B3-top"
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              maxLength={50}
              autoFocus
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              {t('warehouseLocations.description') || 'Description'}
            </label>
            <input
              type="text"
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              placeholder={t('warehouseLocations.descriptionPlaceholder') || 'Optional description'}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <div className="flex justify-end gap-3 pt-2">
            <button
              type="button"
              onClick={() => setShowAddModal(false)}
              className="px-4 py-2 text-gray-700 bg-gray-100 rounded-md hover:bg-gray-200"
            >
              {t('common.cancel') || 'Cancel'}
            </button>
            <button
              type="submit"
              disabled={formLoading}
              className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
            >
              {formLoading
                ? (t('common.saving') || 'Saving...')
                : (t('common.create') || 'Create')}
            </button>
          </div>
        </form>
      </Modal>

      {/* Edit Location Modal */}
      <Modal
        isOpen={showEditModal}
        onClose={() => {
          setShowEditModal(false);
          setEditingLocation(null);
        }}
        title={t('warehouseLocations.editLocation') || 'Edit Location'}
        size="small"
      >
        <form onSubmit={handleUpdateLocation} className="space-y-4">
          {formError && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-3 py-2 rounded text-sm">
              {formError}
            </div>
          )}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              {t('warehouseLocations.locationCode') || 'Location Code'} *
            </label>
            <input
              type="text"
              value={formData.location_code}
              onChange={(e) => setFormData({ ...formData, location_code: e.target.value })}
              placeholder="e.g. A1, B3-top"
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              maxLength={50}
              autoFocus
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              {t('warehouseLocations.description') || 'Description'}
            </label>
            <input
              type="text"
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              placeholder={t('warehouseLocations.descriptionPlaceholder') || 'Optional description'}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <div className="flex justify-end gap-3 pt-2">
            <button
              type="button"
              onClick={() => {
                setShowEditModal(false);
                setEditingLocation(null);
              }}
              className="px-4 py-2 text-gray-700 bg-gray-100 rounded-md hover:bg-gray-200"
            >
              {t('common.cancel') || 'Cancel'}
            </button>
            <button
              type="submit"
              disabled={formLoading}
              className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
            >
              {formLoading
                ? (t('common.saving') || 'Saving...')
                : (t('common.save') || 'Save')}
            </button>
          </div>
        </form>
      </Modal>

      {/* Delete Confirmation Modal */}
      <Modal
        isOpen={showDeleteConfirm}
        onClose={() => {
          setShowDeleteConfirm(false);
          setDeletingLocation(null);
        }}
        title={t('warehouseLocations.deleteLocation') || 'Delete Location'}
        size="small"
      >
        <div className="space-y-4">
          <p className="text-gray-700">
            {t('warehouseLocations.deleteConfirmation') || 'Are you sure you want to delete location'}{' '}
            <strong>{deletingLocation?.location_code}</strong>?
          </p>
          {(deletingLocation?.parts_count || 0) > 0 && (
            <div className="bg-yellow-50 border border-yellow-200 text-yellow-800 px-3 py-2 rounded text-sm">
              ⚠️ {t('warehouseLocations.deleteWarningHasParts') || 'This location has parts assigned. They will be unassigned.'}
            </div>
          )}
          <div className="flex justify-end gap-3 pt-2">
            <button
              type="button"
              onClick={() => {
                setShowDeleteConfirm(false);
                setDeletingLocation(null);
              }}
              className="px-4 py-2 text-gray-700 bg-gray-100 rounded-md hover:bg-gray-200"
            >
              {t('common.cancel') || 'Cancel'}
            </button>
            <button
              type="button"
              onClick={handleDeleteLocation}
              disabled={formLoading}
              className="px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 disabled:opacity-50"
            >
              {formLoading
                ? (t('common.deleting') || 'Deleting...')
                : (t('common.delete') || 'Delete')}
            </button>
          </div>
        </div>
      </Modal>

      {/* Assign Parts Modal */}
      <Modal
        isOpen={showAssignModal}
        onClose={() => {
          setShowAssignModal(false);
          setAssigningLocation(null);
          setLocationParts([]);
          setWarehouseInventory([]);
        }}
        title={`${t('warehouseLocations.manageParts') || 'Manage Parts'} — ${assigningLocation?.location_code || ''}`}
        size="large"
      >
        <div className="space-y-4">
          {partsLoading ? (
            <div className="flex items-center justify-center py-8">
              <div className="text-gray-500">{t('common.loading') || 'Loading...'}</div>
            </div>
          ) : (
            <>
              {/* Currently assigned parts */}
              <div>
                <h3 className="text-sm font-semibold text-gray-700 mb-2">
                  {t('warehouseLocations.currentParts') || 'Currently at this location'} ({locationParts.length})
                </h3>
                {locationParts.length === 0 ? (
                  <div className="bg-gray-50 rounded-lg p-4 text-center text-gray-500 text-sm">
                    {t('warehouseLocations.noPartsAssigned') || 'No parts assigned to this location yet.'}
                  </div>
                ) : (
                  <div className="space-y-2 max-h-48 overflow-y-auto">
                    {locationParts.map((part) => (
                      <div
                        key={part.inventory_id}
                        className="flex items-center justify-between bg-green-50 border border-green-200 rounded-lg px-3 py-2"
                      >
                        <div className="flex-1 min-w-0">
                          <span className="font-medium text-gray-900 text-sm truncate block">
                            {part.part_name}
                          </span>
                          {part.sku && (
                            <span className="text-xs text-gray-500 font-mono">{part.sku}</span>
                          )}
                        </div>
                        <div className="flex items-center gap-2 ml-2">
                          <span className="text-xs bg-green-100 text-green-800 px-2 py-0.5 rounded font-medium">
                            {t('warehouseLocations.qty') || 'Qty'}: {Number(part.quantity)}
                          </span>
                          <button
                            onClick={() => handleUnassignPart(part.inventory_id)}
                            disabled={assignLoading}
                            className="text-red-500 hover:text-red-700 text-sm font-medium disabled:opacity-50"
                            title={t('warehouseLocations.unassign') || 'Remove from location'}
                          >
                            ✕
                          </button>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>

              {/* Divider */}
              <hr className="border-gray-200" />

              {/* Add parts from inventory */}
              <div>
                <h3 className="text-sm font-semibold text-gray-700 mb-2">
                  {t('warehouseLocations.addParts') || 'Add parts from warehouse inventory'}
                </h3>
                <input
                  type="text"
                  value={inventorySearch}
                  onChange={(e) => setInventorySearch(e.target.value)}
                  placeholder={t('warehouseLocations.searchParts') || 'Search by part name or SKU...'}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 mb-3"
                />
                {filteredInventory.length === 0 ? (
                  <div className="bg-gray-50 rounded-lg p-4 text-center text-gray-500 text-sm">
                    {warehouseInventory.length === 0
                      ? (t('warehouseLocations.noInventory') || 'No inventory items in this warehouse.')
                      : (t('warehouseLocations.noMatchingParts') || 'No matching parts found. All parts may already be assigned.')}
                  </div>
                ) : (
                  <div className="space-y-2 max-h-56 overflow-y-auto">
                    {filteredInventory.slice(0, 50).map((item) => (
                      <div
                        key={item.id}
                        className="flex items-center justify-between bg-white border border-gray-200 rounded-lg px-3 py-2 hover:bg-blue-50 hover:border-blue-200 transition-colors"
                      >
                        <div className="flex-1 min-w-0">
                          <span className="font-medium text-gray-900 text-sm truncate block">
                            {item.part_name || 'Unknown Part'}
                          </span>
                          <span className="text-xs text-gray-500 font-mono">
                            {item.part_number || ''}
                            {item.current_stock != null && ` • Stock: ${Number(item.current_stock)}`}
                          </span>
                        </div>
                        <button
                          onClick={() => handleAssignPart(item.id)}
                          disabled={assignLoading}
                          className="ml-2 bg-blue-600 text-white px-3 py-1 rounded text-sm font-medium hover:bg-blue-700 disabled:opacity-50 whitespace-nowrap"
                        >
                          + {t('warehouseLocations.assign') || 'Assign'}
                        </button>
                      </div>
                    ))}
                    {filteredInventory.length > 50 && (
                      <p className="text-xs text-gray-500 text-center pt-2">
                        {t('warehouseLocations.showingFirst50') || 'Showing first 50 results. Refine your search.'}
                      </p>
                    )}
                  </div>
                )}
              </div>
            </>
          )}

          {/* Close button */}
          <div className="flex justify-end pt-2">
            <button
              type="button"
              onClick={() => {
                setShowAssignModal(false);
                setAssigningLocation(null);
                setLocationParts([]);
                setWarehouseInventory([]);
              }}
              className="px-4 py-2 text-gray-700 bg-gray-100 rounded-md hover:bg-gray-200"
            >
              {t('common.close') || 'Close'}
            </button>
          </div>
        </div>
      </Modal>

      {/* Floating Action Bar for Label Printing */}
      {selectionMode && (
        <div className="fixed bottom-16 sm:bottom-0 left-0 right-0 bg-white border-t border-gray-200 shadow-lg z-50 px-4 py-3">
          <div className="max-w-7xl mx-auto flex items-center justify-between gap-3">
            <span className="text-sm font-medium text-gray-700">
              {selectedIds.size} {t('warehouseLocations.selected') || 'selected'}
            </span>
            <div className="flex items-center gap-2">
              <button
                onClick={handlePrintSelected}
                disabled={selectedIds.size === 0 || labelLoading}
                className="bg-purple-600 text-white px-4 py-2 rounded-md hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed text-sm font-medium"
              >
                {labelLoading
                  ? (t('warehouseLocations.generating') || 'Generating...')
                  : (t('warehouseLocations.printSelected') || 'Print Selected')}
              </button>
              <button
                onClick={handlePrintAll}
                disabled={labelLoading}
                className="bg-indigo-600 text-white px-4 py-2 rounded-md hover:bg-indigo-700 disabled:opacity-50 text-sm font-medium"
              >
                {t('warehouseLocations.printAll') || 'Print All'}
              </button>
              <button
                onClick={handleExitSelectionMode}
                disabled={labelLoading}
                className="px-4 py-2 text-gray-700 bg-gray-100 rounded-md hover:bg-gray-200 text-sm font-medium"
              >
                {t('common.cancel') || 'Cancel'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default WarehouseLocations;
