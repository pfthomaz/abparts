// frontend/src/components/NetForm.js

import { useState, useEffect } from 'react';
import { useTranslation } from '../hooks/useTranslation';

// Material options based on the image provided
const MATERIAL_OPTIONS = [
  'polyester',
  'polypropylene',
  'polyethylene',
  'galvanizedSteel',
  'spectra',
  'copper',
  'thornD',
  'dyneema',
  'other'
];

const NetForm = ({ net, farmSites, onSubmit, onCancel, preselectedFarmSiteId }) => {
  const { t } = useTranslation();
  const [formData, setFormData] = useState({
    farm_site_id: net?.farm_site_id || preselectedFarmSiteId || '',
    name: net?.name || '',
    diameter: net?.diameter || '',
    vertical_depth: net?.vertical_depth || '',
    cone_depth: net?.cone_depth || '',
    mesh_size: net?.mesh_size || '',
    material: net?.material || '',
    notes: net?.notes || '',
    active: net?.active !== undefined ? net.active : true,
  });
  const [error, setError] = useState(null);
  const [submitting, setSubmitting] = useState(false);

  // Update farm_site_id if preselectedFarmSiteId changes
  useEffect(() => {
    if (preselectedFarmSiteId && !net) {
      setFormData(prev => ({ ...prev, farm_site_id: preselectedFarmSiteId }));
    }
  }, [preselectedFarmSiteId, net]);

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setSubmitting(true);

    // Convert numeric fields
    const submitData = {
      ...formData,
      diameter: formData.diameter ? parseFloat(formData.diameter) : null,
      vertical_depth: formData.vertical_depth ? parseFloat(formData.vertical_depth) : null,
      cone_depth: formData.cone_depth ? parseFloat(formData.cone_depth) : null,
    };

    try {
      await onSubmit(submitData);
    } catch (err) {
      setError(err.message || t('netCleaning.nets.failedToSave'));
      setSubmitting(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
          {error}
        </div>
      )}

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          {t('netCleaning.nets.farmSite')} <span className="text-red-500">{t('netCleaning.nets.required')}</span>
        </label>
        <select
          name="farm_site_id"
          value={formData.farm_site_id}
          onChange={handleChange}
          required
          disabled={!!preselectedFarmSiteId} // Disable if preselected
          className={`w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent ${preselectedFarmSiteId ? 'bg-gray-100 cursor-not-allowed' : ''}`}
        >
          <option value="">{t('netCleaning.nets.selectFarmSite')}</option>
          {farmSites.map(site => (
            <option key={site.id} value={site.id}>{site.name}</option>
          ))}
        </select>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          {t('netCleaning.nets.name')} <span className="text-red-500">{t('netCleaning.nets.required')}</span>
        </label>
        <input
          type="text"
          name="name"
          value={formData.name}
          onChange={handleChange}
          required
          maxLength={200}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          placeholder={t('netCleaning.nets.namePlaceholder')}
        />
      </div>

      <div className="grid grid-cols-3 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            {t('netCleaning.nets.diameterLabel')}
          </label>
          <input
            type="number"
            name="diameter"
            value={formData.diameter}
            onChange={handleChange}
            step="0.01"
            min="0"
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            {t('netCleaning.nets.verticalDepthLabel')}
          </label>
          <input
            type="number"
            name="vertical_depth"
            value={formData.vertical_depth}
            onChange={handleChange}
            step="0.01"
            min="0"
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            {t('netCleaning.nets.coneDepthLabel')}
          </label>
          <input
            type="number"
            name="cone_depth"
            value={formData.cone_depth}
            onChange={handleChange}
            step="0.01"
            min="0"
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        </div>
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            {t('netCleaning.nets.meshSize')}
          </label>
          <input
            type="text"
            name="mesh_size"
            value={formData.mesh_size}
            onChange={handleChange}
            maxLength={50}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            placeholder={t('netCleaning.nets.meshPlaceholder')}
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            {t('netCleaning.nets.material')}
          </label>
          <select
            name="material"
            value={formData.material}
            onChange={handleChange}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="">{t('netCleaning.nets.selectMaterial')}</option>
            {MATERIAL_OPTIONS.map(option => (
              <option key={option} value={option}>
                {t(`netCleaning.nets.materials.${option}`)}
              </option>
            ))}
          </select>
        </div>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          {t('netCleaning.nets.notes')}
        </label>
        <textarea
          name="notes"
          value={formData.notes}
          onChange={handleChange}
          rows={3}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        />
      </div>

      <div className="flex items-center">
        <input
          type="checkbox"
          name="active"
          id="active"
          checked={formData.active}
          onChange={handleChange}
          className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
        />
        <label htmlFor="active" className="ml-2 block text-sm text-gray-700">
          {t('netCleaning.nets.active')}
        </label>
      </div>

      <div className="flex gap-3 pt-4">
        <button
          type="submit"
          disabled={submitting}
          className="flex-1 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg disabled:opacity-50"
        >
          {submitting ? t('netCleaning.nets.saving') : (net ? t('netCleaning.nets.update') : t('netCleaning.nets.create'))}
        </button>
        <button
          type="button"
          onClick={onCancel}
          disabled={submitting}
          className="flex-1 bg-gray-300 hover:bg-gray-400 text-gray-800 px-4 py-2 rounded-lg disabled:opacity-50"
        >
          {t('netCleaning.nets.cancel')}
        </button>
      </div>
    </form>
  );
};

export default NetForm;
