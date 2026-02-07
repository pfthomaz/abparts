// frontend/src/components/PartForm.js

import { useState, useEffect, useRef } from 'react';
import { useTranslation } from '../hooks/useTranslation';
import MultilingualPartName from './MultilingualPartName';
import PartPhotoGallery from './PartPhotoGallery';
import { PartCategorySelector } from './PartCategoryBadge';

function PartForm({ initialData = {}, onSubmit, onClose }) {
  const { t } = useTranslation();
  const [formData, setFormData] = useState({
    part_number: '',
    name: '',
    description: '',
    part_type: 'consumable',
    is_proprietary: false,
    unit_of_measure: 'pieces',
    manufacturer_part_number: '',
    manufacturer_delivery_time_days: '',
    local_supplier_delivery_time_days: '',
    image_urls: [], // Initialize with empty array for image URLs
    ...initialData,
  });

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const photoGalleryRef = useRef(null);

  useEffect(() => {
    // Reset form data when initialData changes (e.g., opening for new vs. edit)
    const resetData = {
      part_number: '',
      name: '',
      description: '',
      part_type: 'consumable',
      is_proprietary: false,
      unit_of_measure: 'pieces',
      manufacturer_part_number: '',
      manufacturer_delivery_time_days: '',
      local_supplier_delivery_time_days: '',
      image_urls: [], // Ensure image_urls is reset
    };

    setFormData({ ...resetData, ...initialData });
  }, [initialData]);

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
      // Get current image URLs from the photo gallery component
      const currentImageUrls = photoGalleryRef.current?.getCurrentImageUrls() || [];
      // console.log('PartForm: Retrieved image URLs from gallery:', currentImageUrls);
      // console.log('PartForm: Current formData.image_urls:', formData.image_urls);

      // Prepare data, converting empty strings to null for optional int fields
      const dataToSend = {
        ...formData,
        manufacturer_part_number: formData.manufacturer_part_number === '' ? null : formData.manufacturer_part_number,
        manufacturer_delivery_time_days: formData.manufacturer_delivery_time_days === '' ? null : parseInt(formData.manufacturer_delivery_time_days, 10),
        local_supplier_delivery_time_days: formData.local_supplier_delivery_time_days === '' ? null : parseInt(formData.local_supplier_delivery_time_days, 10),
        image_urls: currentImageUrls
      };

      // console.log('PartForm: Final data being sent:', dataToSend);
      // console.log('PartForm: Final image URLs being sent:', dataToSend.image_urls);

      // Remove deprecated field if it exists
      delete dataToSend.is_consumable;

      await onSubmit(dataToSend);
      onClose(); // Close modal on successful submission
    } catch (err) {
      setError(err.message || 'An unexpected error occurred during submission.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative" role="alert">
          <strong className="font-bold">{t('common.error')}:</strong>
          <span className="block sm:inline ml-2">{error}</span>
        </div>
      )}
      <div>
        <label htmlFor="part_number" className="block text-sm font-medium text-gray-700 mb-1">
          {t('partForm.partNumber')}
        </label>
        <input
          type="text"
          id="part_number"
          name="part_number"
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
          value={formData.part_number}
          onChange={handleChange}
          required
          disabled={loading}
        />
      </div>
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          {t('partForm.partNameMultilingual')}
        </label>
        <MultilingualPartName
          value={formData.name}
          onChange={(value) => setFormData(prev => ({ ...prev, name: value }))}
          isEditing={true}
          preferredLanguage="en"
          supportedLanguages={['en', 'el', 'ar', 'es']}
          placeholder={t('partForm.enterPartName')}
          required={true}
          disabled={loading}
        />
      </div>
      <div>
        <label htmlFor="description" className="block text-sm font-medium text-gray-700 mb-1">
          {t('partForm.description')}
        </label>
        <textarea
          id="description"
          name="description"
          rows="3"
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
          value={formData.description || ''}
          onChange={handleChange}
          disabled={loading}
        ></textarea>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-3">
          {t('partForm.partCategory')}
        </label>
        <PartCategorySelector
          value={formData.part_type}
          onChange={(value) => setFormData(prev => ({ ...prev, part_type: value }))}
          disabled={loading}
          required={true}
        />
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">

        <div>
          <label htmlFor="unit_of_measure" className="block text-sm font-medium text-gray-700 mb-1">
            {t('partForm.unitOfMeasure')}
          </label>
          <select
            id="unit_of_measure"
            name="unit_of_measure"
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
            value={formData.unit_of_measure}
            onChange={handleChange}
            disabled={loading}
          >
            <option value="pieces">{t('partForm.units.pieces')}</option>
            <option value="liters">{t('partForm.units.liters')}</option>
            <option value="kg">{t('partForm.units.kilograms')}</option>
            <option value="meters">{t('partForm.units.meters')}</option>
            <option value="gallons">{t('partForm.units.gallons')}</option>
            <option value="pounds">{t('partForm.units.pounds')}</option>
            <option value="feet">{t('partForm.units.feet')}</option>
            <option value="boxes">{t('partForm.units.boxes')}</option>
            <option value="sets">{t('partForm.units.sets')}</option>
          </select>
        </div>
      </div>

      <div>
        <label htmlFor="manufacturer_part_number" className="block text-sm font-medium text-gray-700 mb-1">
          {t('partForm.manufacturerPartNumber')}
        </label>
        <input
          type="text"
          id="manufacturer_part_number"
          name="manufacturer_part_number"
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
          value={formData.manufacturer_part_number || ''}
          onChange={handleChange}
          disabled={loading}
        />
      </div>

      <div className="flex items-center">
        <input
          type="checkbox"
          id="is_proprietary"
          name="is_proprietary"
          className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
          checked={formData.is_proprietary}
          onChange={handleChange}
          disabled={loading}
        />
        <label htmlFor="is_proprietary" className="ml-2 block text-sm text-gray-900">
          {t('partForm.proprietary')}
        </label>
      </div>
      <div>
        <label htmlFor="manufacturer_delivery_time_days" className="block text-sm font-medium text-gray-700 mb-1">
          {t('partForm.manufacturerDeliveryTime')}
        </label>
        <input
          type="number"
          id="manufacturer_delivery_time_days"
          name="manufacturer_delivery_time_days"
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
          value={formData.manufacturer_delivery_time_days || ''}
          onChange={handleChange}
          min="0"
          disabled={loading}
        />
      </div>
      <div>
        <label htmlFor="local_supplier_delivery_time_days" className="block text-sm font-medium text-gray-700 mb-1">
          {t('partForm.localSupplierDeliveryTime')}
        </label>
        <input
          type="number"
          id="local_supplier_delivery_time_days"
          name="local_supplier_delivery_time_days"
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
          value={formData.local_supplier_delivery_time_days || ''}
          onChange={handleChange}
          min="0"
          disabled={loading}
        />
      </div>

      {/* Image Upload Section */}
      <div>
        <PartPhotoGallery
          ref={photoGalleryRef}
          images={formData.image_urls || []}
          onImagesChange={(imageUrls) => {
            // console.log('PartForm: Received image URLs from gallery:', imageUrls);
            setFormData(prev => ({
              ...prev,
              image_urls: imageUrls
            }));
          }}
          isEditing={true}
          maxImages={20}
          disabled={loading}
        />
      </div>

      <div className="flex justify-end space-x-3 mt-6">
        <button
          type="button"
          onClick={onClose}
          className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-200 rounded-md hover:bg-gray-300 focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-offset-2"
          disabled={loading}
        >
          {t('common.cancel')}
        </button>
        <button
          type="submit"
          className="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
          disabled={loading}
        >
          {loading ? t('partForm.submitting') : (initialData.id ? t('partForm.updatePart') : t('partForm.createPart'))}
        </button>
      </div>
    </form>
  );
}

export default PartForm;
