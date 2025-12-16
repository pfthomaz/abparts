// frontend/src/components/OrganizationForm.js

import React, { useState, useEffect } from 'react';
import { useAuth } from '../AuthContext';
import { OrganizationType, organizationsService } from '../services/organizationsService';
import { getSupportedCountries, getCountryDisplay } from '../utils/countryFlags';
import OrganizationLogoUpload from './OrganizationLogoUpload';
import { useTranslation } from '../hooks/useTranslation';
import { getOrganizationTypeConfig } from '../utils/organizationTypeConfig';

function OrganizationForm({ initialData = {}, onSubmit, onClose }) {
  const { t } = useTranslation();
  const { user } = useAuth();
  const [formData, setFormData] = useState({
    name: '',
    organization_type: OrganizationType.CUSTOMER, // Default type
    parent_organization_id: '',
    country: '',
    address: '',
    contact_info: '',
    is_active: true,
    ...initialData, // Pre-fill if initialData is provided (for editing)
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [potentialParents, setPotentialParents] = useState([]);
  const [loadingParents, setLoadingParents] = useState(false);

  const isEditing = !!initialData.id;

  useEffect(() => {
    // Update form data if initialData changes (e.g., when editing a different organization)
    setFormData({
      name: '',
      organization_type: OrganizationType.CUSTOMER,
      parent_organization_id: '',
      country: '',
      address: '',
      contact_info: '',
      is_active: true,
      ...initialData,
    });
  }, [initialData]);

  // Load potential parent organizations when organization type changes
  useEffect(() => {
    const loadPotentialParents = async () => {
      if (formData.organization_type === OrganizationType.SUPPLIER) {
        try {
          setLoadingParents(true);
          const response = await organizationsService.getPotentialParentOrganizations(formData.organization_type);
          setPotentialParents(response.data || response);
        } catch (error) {
          console.error('Failed to load potential parents:', error);
          setPotentialParents([]);
        } finally {
          setLoadingParents(false);
        }
      } else {
        setPotentialParents([]);
        setFormData(prev => ({ ...prev, parent_organization_id: '' }));
      }
    };

    loadPotentialParents();
  }, [formData.organization_type]);

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData((prevData) => ({
      ...prevData,
      [name]: type === 'checkbox' ? checked : value,
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      // Validate with backend first
      // Clean up the data before validation - convert empty strings to null for UUID fields
      const validationData = {
        ...formData,
        parent_organization_id: formData.parent_organization_id || null,
        country: formData.country || null,
        address: formData.address || null,
        contact_info: formData.contact_info || null,
      };

      await organizationsService.validateOrganization(validationData, initialData.id);

      // Clean up empty strings
      const cleanedData = {
        ...formData,
        parent_organization_id: formData.parent_organization_id || undefined,
        country: formData.country || undefined,
        address: formData.address || undefined,
        contact_info: formData.contact_info || undefined
      };

      // Remove logo fields from submission - logos are handled separately via upload endpoint
      delete cleanedData.logo_url;
      delete cleanedData.logo_data_url;

      // Call the onSubmit prop function (passed from parent component)
      await onSubmit(cleanedData);
    } catch (err) {
      console.error('Form submission error:', err);

      if (err.response?.data?.detail) {
        // Handle string error messages
        if (typeof err.response.data.detail === 'string') {
          setError(err.response.data.detail);
        } else if (Array.isArray(err.response.data.detail)) {
          // Handle Pydantic validation errors (array format)
          const errorMessages = err.response.data.detail.map(error =>
            `${error.loc?.join('.')} ${error.msg}`
          ).join('; ');
          setError(errorMessages);
        } else {
          setError(t('organizationForm.validationFailed'));
        }
      } else {
        setError(err.message || t('organizationForm.unexpectedError'));
      }
    } finally {
      setLoading(false);
    }
  };

  const getOrganizationTypeInfo = (type) => {
    const ORGANIZATION_TYPE_CONFIG = getOrganizationTypeConfig(t);
    return ORGANIZATION_TYPE_CONFIG[type];
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative" role="alert">
          <strong className="font-bold">{t('userInvitation.error')}</strong>
          <span className="block sm:inline ml-2">{error}</span>
        </div>
      )}

      {/* Organization Logo Upload (only when editing) */}
      {isEditing && initialData.id && (
        <div className="bg-gray-50 p-4 rounded-lg border border-gray-200">
          <h4 className="text-sm font-medium text-gray-700 mb-3">{t('organizationForm.organizationLogo')}</h4>
          <OrganizationLogoUpload
            organizationId={initialData.id}
            currentLogoUrl={formData.logo_data_url}
            onLogoUpdated={(newUrl) => {
              setFormData(prev => ({ ...prev, logo_data_url: newUrl }));
            }}
          />
        </div>
      )}

      {/* Organization Name */}
      <div>
        <label htmlFor="name" className="block text-sm font-medium text-gray-700 mb-1">
          {t('organizationForm.organizationName')} *
        </label>
        <input
          type="text"
          id="name"
          name="name"
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-indigo-500 focus:border-indigo-500"
          value={formData.name}
          onChange={handleChange}
          required
          disabled={loading}
          placeholder={t('organizationForm.organizationNamePlaceholder')}
        />
      </div>

      {/* Organization Type */}
      <div>
        <label htmlFor="organization_type" className="block text-sm font-medium text-gray-700 mb-1">
          {t('organizationForm.organizationType')} *
        </label>
        <select
          id="organization_type"
          name="organization_type"
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-indigo-500 focus:border-indigo-500"
          value={formData.organization_type}
          onChange={handleChange}
          required
          disabled={loading || isEditing} // Prevent changing type after creation
        >
          {Object.values(OrganizationType).map((type) => {
            const config = getOrganizationTypeInfo(type);
            return (
              <option key={type} value={type}>
                {config.icon} {config.label} - {config.description}
              </option>
            );
          })}
        </select>

        {/* Show singleton warning */}
        {formData.organization_type && getOrganizationTypeInfo(formData.organization_type).singleton && (
          <p className="mt-1 text-sm text-amber-600">
            {t('organizationForm.singletonWarning', { type: getOrganizationTypeInfo(formData.organization_type).label })}
          </p>
        )}
      </div>

      {/* Country Selection */}
      <div>
        <label htmlFor="country" className="block text-sm font-medium text-gray-700 mb-1">
          {t('organizationForm.country')}
        </label>
        <select
          id="country"
          name="country"
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-indigo-500 focus:border-indigo-500"
          value={formData.country || ''}
          onChange={handleChange}
          disabled={loading}
        >
          <option value="">{t('organizationForm.selectCountry')}</option>
          {getSupportedCountries().map((country) => (
            <option key={country.code} value={country.code}>
              {getCountryDisplay(country.code)}
            </option>
          ))}
        </select>
      </div>

      {/* Parent Organization (for suppliers) */}
      {formData.organization_type === OrganizationType.SUPPLIER && (
        <div>
          <label htmlFor="parent_organization_id" className="block text-sm font-medium text-gray-700 mb-1">
            {t('organizationForm.parentOrganization')} *
          </label>
          <select
            id="parent_organization_id"
            name="parent_organization_id"
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-indigo-500 focus:border-indigo-500"
            value={formData.parent_organization_id}
            onChange={handleChange}
            required
            disabled={loading || loadingParents}
          >
            <option value="">{t('organizationForm.selectParentOrganization')}</option>
            {potentialParents.map((parent) => (
              <option key={parent.id} value={parent.id}>
                {getOrganizationTypeInfo(parent.organization_type).icon} {parent.name}
              </option>
            ))}
          </select>
          {loadingParents && (
            <p className="mt-1 text-sm text-gray-500">{t('organizationForm.loadingParentOrganizations')}</p>
          )}
        </div>
      )}

      {/* Address */}
      <div>
        <label htmlFor="address" className="block text-sm font-medium text-gray-700 mb-1">
          {t('organizations.address')}
        </label>
        <textarea
          id="address"
          name="address"
          rows="3"
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-indigo-500 focus:border-indigo-500"
          value={formData.address}
          onChange={handleChange}
          disabled={loading}
          placeholder={t('organizationForm.addressPlaceholder')}
        />
      </div>

      {/* Contact Info */}
      <div>
        <label htmlFor="contact_info" className="block text-sm font-medium text-gray-700 mb-1">
          {t('organizationForm.contactInformation')}
        </label>
        <textarea
          id="contact_info"
          name="contact_info"
          rows="3"
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-indigo-500 focus:border-indigo-500"
          value={formData.contact_info}
          onChange={handleChange}
          disabled={loading}
          placeholder={t('organizationForm.contactPlaceholder')}
        />
      </div>

      {/* Active Status */}
      <div className="flex items-center">
        <input
          id="is_active"
          name="is_active"
          type="checkbox"
          checked={formData.is_active}
          onChange={handleChange}
          className="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded"
          disabled={loading}
        />
        <label htmlFor="is_active" className="ml-2 block text-sm text-gray-900">
          {t('organizationForm.organizationIsActive')}
        </label>
      </div>

      {/* Form Actions */}
      <div className="flex justify-end space-x-3 mt-6 pt-4 border-t border-gray-200">
        <button
          type="button"
          onClick={onClose}
          className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-200 rounded-md hover:bg-gray-300 focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-offset-2"
          disabled={loading}
        >
          {t('userInvitation.cancel')}
        </button>
        <button
          type="submit"
          className="px-4 py-2 text-sm font-medium text-white bg-indigo-600 rounded-md hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed"
          disabled={loading}
        >
          {loading ? (
            <span className="flex items-center">
              <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              {isEditing ? t('organizationForm.updating') : t('organizationForm.creating')}
            </span>
          ) : (
            isEditing ? t('organizationForm.updateOrganization') : t('organizationForm.createOrganization')
          )}
        </button>
      </div>
    </form>
  );
}

export default OrganizationForm;
