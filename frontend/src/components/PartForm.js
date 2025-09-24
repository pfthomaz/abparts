// frontend/src/components/PartForm.js

import React, { useState, useEffect, useRef } from 'react';
import { partsService } from '../services/partsService';
import { API_BASE_URL } from '../services/api';
import MultilingualPartName from './MultilingualPartName';
import PartPhotoGallery from './PartPhotoGallery';
import { PartCategorySelector } from './PartCategoryBadge';

function PartForm({ initialData = {}, onSubmit, onClose }) {
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

  const [removedImageUrls, setRemovedImageUrls] = useState([]); // State to track removed existing images
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

    setRemovedImageUrls([]); // Clear removed images on data change
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

      // Prepare data, converting empty strings to null for optional int fields
      const dataToSend = {
        ...formData,
        manufacturer_part_number: formData.manufacturer_part_number === '' ? null : formData.manufacturer_part_number,
        manufacturer_delivery_time_days: formData.manufacturer_delivery_time_days === '' ? null : parseInt(formData.manufacturer_delivery_time_days, 10),
        local_supplier_delivery_time_days: formData.local_supplier_delivery_time_days === '' ? null : parseInt(formData.local_supplier_delivery_time_days, 10),
        image_urls: currentImageUrls
      };

      console.log('PartForm: Submitting data:', dataToSend); // Debug log
      console.log('PartForm: Image URLs:', dataToSend.image_urls); // Debug log

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
          <strong className="font-bold">Error:</strong>
          <span className="block sm:inline ml-2">{error}</span>
        </div>
      )}
      <div>
        <label htmlFor="part_number" className="block text-sm font-medium text-gray-700 mb-1">
          Part Number
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
          Part Name (Multilingual)
        </label>
        <MultilingualPartName
          value={formData.name}
          onChange={(value) => setFormData(prev => ({ ...prev, name: value }))}
          isEditing={true}
          preferredLanguage="en"
          supportedLanguages={['en', 'el', 'ar', 'es']}
          placeholder="Enter part name"
          required={true}
          disabled={loading}
        />
      </div>
      <div>
        <label htmlFor="description" className="block text-sm font-medium text-gray-700 mb-1">
          Description
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
          Part Category
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
            Unit of Measure
          </label>
          <select
            id="unit_of_measure"
            name="unit_of_measure"
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
            value={formData.unit_of_measure}
            onChange={handleChange}
            disabled={loading}
          >
            <option value="pieces">Pieces</option>
            <option value="liters">Liters</option>
            <option value="kg">Kilograms</option>
            <option value="meters">Meters</option>
            <option value="gallons">Gallons</option>
            <option value="pounds">Pounds</option>
            <option value="feet">Feet</option>
            <option value="boxes">Boxes</option>
            <option value="sets">Sets</option>
          </select>
        </div>
      </div>

      <div>
        <label htmlFor="manufacturer_part_number" className="block text-sm font-medium text-gray-700 mb-1">
          Manufacturer Part Number
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
          Proprietary (BossAqua exclusive part)
        </label>
      </div>
      <div>
        <label htmlFor="manufacturer_delivery_time_days" className="block text-sm font-medium text-gray-700 mb-1">
          Manufacturer Delivery Time (Days)
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
          Local Supplier Delivery Time (Days)
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
          isEditing={true}
          maxImages={4}
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
          Cancel
        </button>
        <button
          type="submit"
          className="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
          disabled={loading}
        >
          {loading ? 'Submitting...' : (initialData.id ? 'Update Part' : 'Create Part')}
        </button>
      </div>
    </form>
  );
}

export default PartForm;
