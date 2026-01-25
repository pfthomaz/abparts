// frontend/src/components/FarmSiteForm.js

import { useState } from 'react';
import { useTranslation } from '../hooks/useTranslation';

const FarmSiteForm = ({ farmSite, onSubmit, onCancel }) => {
  const { t } = useTranslation();
  const [formData, setFormData] = useState({
    name: farmSite?.name || '',
    location: farmSite?.location || '',
    description: farmSite?.description || '',
    active: farmSite?.active !== undefined ? farmSite.active : true,
  });
  const [error, setError] = useState(null);
  const [submitting, setSubmitting] = useState(false);

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

    try {
      await onSubmit(formData);
    } catch (err) {
      setError(err.message || t('netCleaning.farmSites.failedToSave'));
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
          {t('netCleaning.farmSites.name')} <span className="text-red-500">{t('netCleaning.farmSites.required')}</span>
        </label>
        <input
          type="text"
          name="name"
          value={formData.name}
          onChange={handleChange}
          required
          maxLength={200}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          placeholder={t('netCleaning.farmSites.namePlaceholder')}
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          {t('netCleaning.farmSites.location')}
        </label>
        <input
          type="text"
          name="location"
          value={formData.location}
          onChange={handleChange}
          maxLength={500}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          placeholder={t('netCleaning.farmSites.locationPlaceholder')}
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          {t('netCleaning.farmSites.description')}
        </label>
        <textarea
          name="description"
          value={formData.description}
          onChange={handleChange}
          rows={3}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          placeholder={t('netCleaning.farmSites.descriptionPlaceholder')}
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
          {t('netCleaning.farmSites.active')}
        </label>
      </div>

      <div className="flex gap-3 pt-4">
        <button
          type="submit"
          disabled={submitting}
          className="flex-1 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg disabled:opacity-50"
        >
          {submitting ? t('netCleaning.farmSites.saving') : (farmSite ? t('netCleaning.farmSites.update') : t('netCleaning.farmSites.create'))}
        </button>
        <button
          type="button"
          onClick={onCancel}
          disabled={submitting}
          className="flex-1 bg-gray-300 hover:bg-gray-400 text-gray-800 px-4 py-2 rounded-lg disabled:opacity-50"
        >
          {t('netCleaning.farmSites.cancel')}
        </button>
      </div>
    </form>
  );
};

export default FarmSiteForm;
