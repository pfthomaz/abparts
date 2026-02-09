// frontend/src/components/NetCleaningRecordForm.js

import { useState, useEffect } from 'react';
import { useTranslation } from '../hooks/useTranslation';
import { useAuth } from '../AuthContext';
import { useOffline } from '../contexts/OfflineContext';
import { 
  saveOfflineNetCleaningRecord, 
  saveOfflineNetCleaningPhoto,
  cacheData,
  getCachedItemsByIndex,
  STORES
} from '../db/indexedDB';
import { queueNetCleaningRecord, queueNetCleaningPhoto } from '../services/syncQueueManager';

const NetCleaningRecordForm = ({ record, nets, farmSites, machines, onSubmit, onCancel }) => {
  const { t } = useTranslation();
  const { user, token } = useAuth();
  const { isOnline } = useOffline();
  
  // DEBUG: Log props
  console.log('[NetCleaningRecordForm] Received props:', {
    farmSitesCount: farmSites?.length,
    farmSites: farmSites,
    netsCount: nets?.length,
    machinesCount: machines?.length
  });
  const [formData, setFormData] = useState({
    net_id: record?.net_id || '',
    machine_id: record?.machine_id || '',
    operator_name: record?.operator_name || '',
    cleaning_mode: record?.cleaning_mode || 1,
    depth_1: record?.depth_1 || '',
    depth_2: record?.depth_2 || '',
    depth_3: record?.depth_3 || '',
    start_time: record?.start_time ? record.start_time.slice(0, 16) : '',
    end_time: record?.end_time ? record.end_time.slice(0, 16) : '',
    notes: record?.notes || '',
  });
  const [selectedFarmSiteId, setSelectedFarmSiteId] = useState('');
  const [organizationUsers, setOrganizationUsers] = useState([]);
  const [loadingUsers, setLoadingUsers] = useState(false);
  const [error, setError] = useState(null);
  const [submitting, setSubmitting] = useState(false);
  const [photos, setPhotos] = useState([]);
  const [photoPreview, setPhotoPreview] = useState([]);

  // Set initial farm site if editing
  useEffect(() => {
    if (record && record.net_id) {
      const net = nets.find(n => n.id === record.net_id);
      if (net) {
        setSelectedFarmSiteId(net.farm_site_id);
      }
    }
  }, [record, nets]);

  // Fetch organization users based on selected farm site's organization
  useEffect(() => {
    const fetchOrganizationUsers = async () => {
      if (!token) return;
      
      // Get the organization_id from the selected farm site
      let targetOrganizationId = null;
      
      if (selectedFarmSiteId) {
        const selectedFarmSite = farmSites.find(fs => fs.id === selectedFarmSiteId);
        if (selectedFarmSite) {
          targetOrganizationId = selectedFarmSite.organization_id;
        }
      }
      
      // If no farm site selected yet, don't fetch users
      if (!targetOrganizationId) {
        setOrganizationUsers([]);
        return;
      }
      
      // If offline, load from cache
      if (!isOnline) {
        // console.log('[NetCleaningRecordForm] Loading users from cache (offline)...');
        try {
          const cachedUsers = await getCachedItemsByIndex(
            STORES.USERS, 
            'organization_id', 
            targetOrganizationId
          );
          const activeUsers = cachedUsers.filter(u => u.is_active);
          setOrganizationUsers(activeUsers);
          // console.log(`[NetCleaningRecordForm] Loaded ${activeUsers.length} users from cache`);
        } catch (err) {
          console.error('[NetCleaningRecordForm] Error loading cached users:', err);
          setOrganizationUsers([]);
        }
        return;
      }
      
      // Online - fetch from API
      setLoadingUsers(true);
      try {
        const response = await fetch(
          `${process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000'}/users/organization/${targetOrganizationId}/users`,
          {
            headers: {
              'Authorization': `Bearer ${token}`,
              'Content-Type': 'application/json',
            },
          }
        );

        if (!response.ok) {
          throw new Error('Failed to fetch organization users');
        }

        const users = await response.json();
        // Filter to only active users
        const activeUsers = users.filter(u => u.is_active);
        setOrganizationUsers(activeUsers);
        
        // Cache users for offline use
        // console.log(`[NetCleaningRecordForm] Caching ${activeUsers.length} users for offline use...`);
        await cacheData(STORES.USERS, activeUsers);
      } catch (err) {
        console.error('Error fetching organization users:', err);
        setOrganizationUsers([]);
      } finally {
        setLoadingUsers(false);
      }
    };

    fetchOrganizationUsers();
  }, [selectedFarmSiteId, farmSites, token, isOnline]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleFarmSiteChange = (e) => {
    setSelectedFarmSiteId(e.target.value);
    setFormData(prev => ({ ...prev, net_id: '' }));
  };

  const handleModeChange = (e) => {
    const mode = parseInt(e.target.value);
    setFormData(prev => ({
      ...prev,
      cleaning_mode: mode,
      // Clear depths that aren't needed for this mode
      depth_2: mode < 2 ? '' : prev.depth_2,
      depth_3: mode < 3 ? '' : prev.depth_3,
    }));
  };

  const handlePhotoChange = (e) => {
    const files = Array.from(e.target.files);
    setPhotos(prevPhotos => [...prevPhotos, ...files]);
    
    // Create preview URLs
    files.forEach(file => {
      const reader = new FileReader();
      reader.onloadend = () => {
        setPhotoPreview(prev => [...prev, reader.result]);
      };
      reader.readAsDataURL(file);
    });
  };

  const removePhoto = (index) => {
    setPhotos(prev => prev.filter((_, i) => i !== index));
    setPhotoPreview(prev => prev.filter((_, i) => i !== index));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setSubmitting(true);

    // Validate times if both are provided
    if (formData.start_time && formData.end_time) {
      const start = new Date(formData.start_time);
      const end = new Date(formData.end_time);
      if (end <= start) {
        setError(t('netCleaning.records.endTimeAfterStart'));
        setSubmitting(false);
        return;
      }
    }

    // Determine status based on whether end_time is provided
    const status = formData.end_time ? 'completed' : 'in_progress';

    // Convert to proper format
    const submitData = {
      net_id: formData.net_id,
      machine_id: formData.machine_id || null,
      operator_name: formData.operator_name,
      cleaning_mode: parseInt(formData.cleaning_mode),
      depth_1: formData.depth_1 ? parseFloat(formData.depth_1) : null,
      depth_2: formData.depth_2 ? parseFloat(formData.depth_2) : null,
      depth_3: formData.depth_3 ? parseFloat(formData.depth_3) : null,
      start_time: new Date(formData.start_time).toISOString(),
      end_time: formData.end_time ? new Date(formData.end_time).toISOString() : null,
      status: status,
      notes: formData.notes || null,
    };

    try {
      // If offline, save to IndexedDB
      if (!isOnline) {
        // console.log('[NetCleaningRecordForm] Saving offline...');
        
        // Generate temporary ID
        const tempId = `temp_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
        
        // Add metadata for offline record
        const offlineRecord = {
          ...submitData,
          id: tempId,
          created_at: new Date().toISOString(),
          synced: false,
          organization_id: user.organization_id,
        };
        
        // Save record to IndexedDB
        await saveOfflineNetCleaningRecord(offlineRecord);
        
        // Queue for sync
        await queueNetCleaningRecord(offlineRecord);
        
        // Save photos if any
        if (photos.length > 0) {
          // console.log(`[NetCleaningRecordForm] Saving ${photos.length} photos offline...`);
          for (let i = 0; i < photos.length; i++) {
            const photo = photos[i];
            const photoTempId = `temp_photo_${Date.now()}_${i}_${Math.random().toString(36).substr(2, 9)}`;
            
            // Convert file to base64
            const base64 = await new Promise((resolve) => {
              const reader = new FileReader();
              reader.onloadend = () => resolve(reader.result);
              reader.readAsDataURL(photo);
            });
            
            const photoData = {
              id: photoTempId,
              record_id: tempId,
              photo_data: base64,
              filename: photo.name,
              created_at: new Date().toISOString(),
              synced: false,
            };
            
            await saveOfflineNetCleaningPhoto(photoData);
            await queueNetCleaningPhoto(photoData);
          }
        }
        
        // Show success message
        alert(t('netCleaning.records.savedOffline'));
        
        // Call onSubmit to refresh the list
        if (onSubmit) {
          await onSubmit(submitData, true); // Pass true to indicate offline save
        }
      } else {
        // Online - submit normally
        await onSubmit(submitData);
      }
    } catch (err) {
      console.error('[NetCleaningRecordForm] Error saving:', err);
      setError(err.message || t('netCleaning.records.failedToSave'));
      setSubmitting(false);
    }
  };

  const filteredNets = nets.filter(net => 
    !selectedFarmSiteId || net.farm_site_id === selectedFarmSiteId
  );

  return (
    <form onSubmit={handleSubmit} className="space-y-4 max-h-[70vh] overflow-y-auto px-1">
      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
          {error}
        </div>
      )}

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          {t('netCleaning.records.farmSite')} <span className="text-red-500">{t('netCleaning.records.required')}</span>
        </label>
        <select
          value={selectedFarmSiteId}
          onChange={handleFarmSiteChange}
          required
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        >
          <option value="">{t('netCleaning.records.selectFarmSite')}</option>
          {farmSites.map(site => (
            <option key={site.id} value={site.id}>{site.name}</option>
          ))}
        </select>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          {t('netCleaning.records.net')} <span className="text-red-500">{t('netCleaning.records.required')}</span>
        </label>
        <select
          name="net_id"
          value={formData.net_id}
          onChange={handleChange}
          required
          disabled={!selectedFarmSiteId}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:bg-gray-100"
        >
          <option value="">{t('netCleaning.records.selectNet')}</option>
          {filteredNets.map(net => (
            <option key={net.id} value={net.id}>{net.name}</option>
          ))}
        </select>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          {t('netCleaning.records.machine')}
        </label>
        <select
          name="machine_id"
          value={formData.machine_id}
          onChange={handleChange}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        >
          <option value="">{t('netCleaning.records.noMachineSelected')}</option>
          {machines.map(machine => (
            <option key={machine.id} value={machine.id}>{machine.name}</option>
          ))}
        </select>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          {t('netCleaning.records.operatorName')} <span className="text-red-500">{t('netCleaning.records.required')}</span>
        </label>
        <select
          name="operator_name"
          value={formData.operator_name}
          onChange={handleChange}
          required
          disabled={loadingUsers || !selectedFarmSiteId}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:bg-gray-100"
        >
          <option value="">
            {!selectedFarmSiteId 
              ? t('netCleaning.records.selectFarmSiteFirst') 
              : loadingUsers 
                ? t('common.loading') 
                : t('netCleaning.records.selectOperator')}
          </option>
          {organizationUsers.map(orgUser => (
            <option key={orgUser.id} value={orgUser.name || orgUser.username}>
              {orgUser.name || orgUser.username}
            </option>
          ))}
        </select>
        {!isOnline && organizationUsers.length === 0 && selectedFarmSiteId && (
          <p className="text-xs text-yellow-600 mt-1">
            {t('netCleaning.records.noUsersOffline')}
          </p>
        )}
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          {t('netCleaning.records.cleaningMode')} <span className="text-red-500">{t('netCleaning.records.required')}</span>
        </label>
        <select
          name="cleaning_mode"
          value={formData.cleaning_mode}
          onChange={handleModeChange}
          required
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        >
          <option value={1}>{t('netCleaning.records.mode1')}</option>
          <option value={2}>{t('netCleaning.records.mode2')}</option>
          <option value={3}>{t('netCleaning.records.mode3')}</option>
        </select>
      </div>

      <div className="grid grid-cols-3 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            {t('netCleaning.records.depth1')} <span className="text-red-500">{t('netCleaning.records.required')}</span>
          </label>
          <input
            type="number"
            name="depth_1"
            value={formData.depth_1}
            onChange={handleChange}
            required
            step="0.01"
            min="0"
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        </div>

        {formData.cleaning_mode >= 2 && (
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              {t('netCleaning.records.depth2')} <span className="text-red-500">{t('netCleaning.records.required')}</span>
            </label>
            <input
              type="number"
              name="depth_2"
              value={formData.depth_2}
              onChange={handleChange}
              required
              step="0.01"
              min="0"
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>
        )}

        {formData.cleaning_mode === 3 && (
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              {t('netCleaning.records.depth3')} <span className="text-red-500">{t('netCleaning.records.required')}</span>
            </label>
            <input
              type="number"
              name="depth_3"
              value={formData.depth_3}
              onChange={handleChange}
              required
              step="0.01"
              min="0"
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>
        )}
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            {t('netCleaning.records.startTime')} <span className="text-red-500">{t('netCleaning.records.required')}</span>
          </label>
          <input
            type="datetime-local"
            name="start_time"
            value={formData.start_time}
            onChange={handleChange}
            required
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
          <p className="text-xs text-gray-500 mt-1">{t('netCleaning.records.dateTimeHelp')}</p>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            {t('netCleaning.records.endTime')} <span className="text-gray-500 text-xs">({t('netCleaning.records.optional')})</span>
          </label>
          <input
            type="datetime-local"
            name="end_time"
            value={formData.end_time}
            onChange={handleChange}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
          <p className="text-xs text-gray-500 mt-1">{t('netCleaning.records.endTimeHelp')}</p>
        </div>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          {t('netCleaning.records.notes')}
        </label>
        <textarea
          name="notes"
          value={formData.notes}
          onChange={handleChange}
          rows={3}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          placeholder={t('netCleaning.records.notesPlaceholder')}
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          {t('netCleaning.records.photos')} <span className="text-gray-500 text-xs">({t('netCleaning.records.optional')})</span>
        </label>
        <input
          type="file"
          accept="image/*"
          multiple
          capture="environment"
          onChange={handlePhotoChange}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        />
        <p className="text-xs text-gray-500 mt-1">
          {isOnline 
            ? t('netCleaning.records.photosHelp') 
            : t('netCleaning.records.photosOfflineHelp')}
        </p>
        
        {photoPreview.length > 0 && (
          <div className="mt-3 grid grid-cols-3 gap-2">
            {photoPreview.map((preview, index) => (
              <div key={index} className="relative">
                <img 
                  src={preview} 
                  alt={`Preview ${index + 1}`} 
                  className="w-full h-24 object-cover rounded border"
                />
                <button
                  type="button"
                  onClick={() => removePhoto(index)}
                  className="absolute top-1 right-1 bg-red-500 text-white rounded-full w-6 h-6 flex items-center justify-center text-xs hover:bg-red-600"
                >
                  ×
                </button>
              </div>
            ))}
          </div>
        )}
      </div>

      {!isOnline && (
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-3">
          <div className="flex items-start">
            <svg className="w-5 h-5 text-yellow-600 mt-0.5 mr-2" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
            </svg>
            <div className="flex-1">
              <p className="text-sm font-medium text-yellow-800">
                {t('netCleaning.records.offlineMode')}
              </p>
              <p className="text-xs text-yellow-700 mt-1">
                {t('netCleaning.records.offlineModeHelp')}
              </p>
            </div>
          </div>
        </div>
      )}

      <div className="flex gap-3 pt-4">
        <button
          type="submit"
          disabled={submitting}
          className="flex-1 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg disabled:opacity-50"
        >
          {submitting ? t('netCleaning.records.saving') : (record ? t('netCleaning.records.update') : t('netCleaning.records.create'))}
        </button>
        <button
          type="button"
          onClick={onCancel}
          disabled={submitting}
          className="flex-1 bg-gray-300 hover:bg-gray-400 text-gray-800 px-4 py-2 rounded-lg disabled:opacity-50"
        >
          {t('netCleaning.records.cancel')}
        </button>
      </div>
    </form>
  );
};

export default NetCleaningRecordForm;
