// frontend/src/components/NetCleaningRecordForm.js

import { useState, useEffect } from 'react';
import { useTranslation } from '../hooks/useTranslation';
import { useAuth } from '../AuthContext';

const NetCleaningRecordForm = ({ record, nets, farmSites, machines, onSubmit, onCancel }) => {
  const { t } = useTranslation();
  const { user, token } = useAuth();
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
      } catch (err) {
        console.error('Error fetching organization users:', err);
        setOrganizationUsers([]);
      } finally {
        setLoadingUsers(false);
      }
    };

    fetchOrganizationUsers();
  }, [selectedFarmSiteId, farmSites, token]);

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
      await onSubmit(submitData);
    } catch (err) {
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
