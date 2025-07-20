// frontend/src/components/PartForm.js

import React, { useState, useEffect } from 'react';
import { partsService } from '../services/partsService';
import { API_BASE_URL } from '../services/api';

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

  const [selectedFiles, setSelectedFiles] = useState([]); // State to hold File objects
  const [imagePreviews, setImagePreviews] = useState([]); // State to hold image data URLs for preview
  const [removedImageUrls, setRemovedImageUrls] = useState([]); // State to track removed existing images
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

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

    // Set image previews for existing images if editing
    if (initialData.image_urls && initialData.image_urls.length > 0) {
      setImagePreviews(initialData.image_urls);
    } else {
      setImagePreviews([]); // Clear previews if no initial images
    }
    setSelectedFiles([]); // Clear selected files on data change
    setRemovedImageUrls([]); // Clear removed images on data change
  }, [initialData]);

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData((prevData) => ({
      ...prevData,
      [name]: type === 'checkbox' ? checked : value,
    }));
  };

  const handleFileChange = (e) => {
    const files = Array.from(e.target.files);
    if (files.length + imagePreviews.length > 4) {
      setError("You can upload a maximum of 4 images per part.");
      return;
    }
    setSelectedFiles(files);

    // Generate previews for newly selected files
    const newPreviews = files.map(file => URL.createObjectURL(file));
    // For creation, replace existing previews with new ones. For editing, it's more complex.
    // For simplicity, for now, new selections REPLACE old selections in the form's UI.
    // When submitting, all previous image_urls (if editing) AND new uploads will be sent.
    setImagePreviews(prevPreviews => [
      ...prevPreviews.filter(url => !url.startsWith('blob:')), // Keep existing URLs, remove old blob URLs
      ...newPreviews
    ]);
    setError(null);
  };

  const handleRemoveImage = (indexToRemove) => {
    const imageUrl = imagePreviews[indexToRemove];
    if (imageUrl.startsWith('blob:')) {
      // If it's a file preview (starts with blob:), remove from selectedFiles
      setSelectedFiles(prevFiles => {
        const newFiles = prevFiles.filter((_, index) => index !== (indexToRemove - (imagePreviews.filter(url => !url.startsWith('blob:')).length)));
        // Revoke URL objects to prevent memory leaks
        URL.revokeObjectURL(imageUrl);
        return newFiles;
      });
    } else {
      // If it's an existing image URL, add it to the list of URLs to be removed on submit.
      setRemovedImageUrls(prev => [...prev, imageUrl]);
    }
    setImagePreviews(prevPreviews => prevPreviews.filter((_, index) => index !== indexToRemove));
  };


  const uploadImages = async () => {
    if (selectedFiles.length === 0) return [];

    const uploadedUrls = [];
    for (const file of selectedFiles) {
      const formData = new FormData();
      formData.append('file', file);

      try {
        const data = await partsService.uploadImage(formData);
        uploadedUrls.push(data.url);
      } catch (uploadError) {
        console.error("Image upload failed:", uploadError);
        setError(`Failed to upload image ${file.name}: ${uploadError.message}`);
        throw uploadError; // Stop submission if any image upload fails
      }
    }
    return uploadedUrls;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      // First, upload new images
      const newImageUrls = await uploadImages();

      // Filter out any URLs that the user has marked for removal
      const existingUrls = (initialData.image_urls || []).filter(url => !removedImageUrls.includes(url));

      // Combine the remaining existing URLs with the newly uploaded ones
      const finalImageUrls = [...existingUrls, ...newImageUrls];

      // Prepare data, converting empty strings to null for optional int fields
      const dataToSend = {
        ...formData,
        manufacturer_part_number: formData.manufacturer_part_number === '' ? null : formData.manufacturer_part_number,
        manufacturer_delivery_time_days: formData.manufacturer_delivery_time_days === '' ? null : parseInt(formData.manufacturer_delivery_time_days, 10),
        local_supplier_delivery_time_days: formData.local_supplier_delivery_time_days === '' ? null : parseInt(formData.local_supplier_delivery_time_days, 10),
        image_urls: finalImageUrls, // Set the combined image URLs
      };

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
        <label htmlFor="name" className="block text-sm font-medium text-gray-700 mb-1">
          Part Name
        </label>
        <input
          type="text"
          id="name"
          name="name"
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
          value={formData.name}
          onChange={handleChange}
          required
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

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label htmlFor="part_type" className="block text-sm font-medium text-gray-700 mb-1">
            Part Type
          </label>
          <select
            id="part_type"
            name="part_type"
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
            value={formData.part_type}
            onChange={handleChange}
            disabled={loading}
          >
            <option value="consumable">Consumable (Whole Units)</option>
            <option value="bulk_material">Bulk Material (Measurable Quantities)</option>
          </select>
        </div>

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
        <label htmlFor="part_images" className="block text-sm font-medium text-gray-700 mb-1">
          Part Images (Max 4)
        </label>
        <input
          type="file"
          id="part_images"
          name="part_images"
          accept="image/*"
          multiple
          onChange={handleFileChange}
          className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
          disabled={loading || imagePreviews.length >= 4} // Disable if max images already selected/previewed
        />
        {imagePreviews.length > 0 && (
          <div className="mt-4 grid grid-cols-2 gap-4">
            {imagePreviews.map((src, index) => (
              <div key={index} className="relative group">
                <img src={src.startsWith('/static/images') ? `${API_BASE_URL}${src}` : src} alt={`Part Preview ${index + 1}`} className="w-full h-32 object-cover rounded-md shadow-sm" />
                <button
                  type="button"
                  onClick={() => handleRemoveImage(index)}
                  className="absolute top-1 right-1 bg-red-500 text-white rounded-full p-1 text-xs opacity-0 group-hover:opacity-100 transition-opacity"
                  aria-label={`Remove image ${index + 1}`}
                  disabled={loading}
                >
                  &times;
                </button>
              </div>
            ))}
          </div>
        )}
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
