// frontend/src/components/PartPhotoGallery.js

import React, { useState, useEffect } from 'react';
import { API_BASE_URL } from '../services/api';
import { partsService } from '../services/partsService';

/**
 * PartPhotoGallery component for managing up to 4 part images
 * Supports viewing, uploading, removing, and reordering images
 */
const PartPhotoGallery = ({
  images = [],
  onImagesChange,
  isEditing = false,
  maxImages = 4,
  className = '',
  disabled = false
}) => {
  const [imageList, setImageList] = useState([]);
  const [selectedFiles, setSelectedFiles] = useState([]);
  const [imagePreviews, setImagePreviews] = useState([]);
  const [removedImages, setRemovedImages] = useState([]);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState(null);
  const [selectedImageIndex, setSelectedImageIndex] = useState(null);

  // Initialize images from props
  useEffect(() => {
    const processedImages = (images || []).map((url, index) => ({
      id: `existing-${index}`,
      url: url,
      isExisting: true,
      isUploaded: true
    }));
    setImageList(processedImages);
    setImagePreviews(processedImages.map(img => img.url));
  }, [images]);

  // Handle file selection
  const handleFileSelect = (event) => {
    const files = Array.from(event.target.files);
    const currentImageCount = imageList.length - removedImages.length;

    if (currentImageCount + files.length > maxImages) {
      setError(`You can only upload a maximum of ${maxImages} images per part.`);
      return;
    }

    setError(null);

    // Create preview URLs for new files
    const newPreviews = files.map(file => URL.createObjectURL(file));
    const newImages = files.map((file, index) => ({
      id: `new-${Date.now()}-${index}`,
      file: file,
      url: newPreviews[index],
      isExisting: false,
      isUploaded: false
    }));

    setSelectedFiles(prev => [...prev, ...files]);
    setImageList(prev => [...prev, ...newImages]);
    setImagePreviews(prev => [...prev, ...newPreviews]);

    // Clear the input
    event.target.value = '';
  };

  // Remove image
  const handleRemoveImage = (index) => {
    const imageToRemove = imageList[index];

    if (imageToRemove.isExisting) {
      // Mark existing image for removal
      setRemovedImages(prev => [...prev, imageToRemove.url]);
    } else {
      // Remove from selected files
      const fileIndex = selectedFiles.findIndex(file =>
        URL.createObjectURL(file) === imageToRemove.url
      );
      if (fileIndex !== -1) {
        setSelectedFiles(prev => prev.filter((_, i) => i !== fileIndex));
      }

      // Revoke object URL to prevent memory leaks
      URL.revokeObjectURL(imageToRemove.url);
    }

    // Remove from image list and previews
    setImageList(prev => prev.filter((_, i) => i !== index));
    setImagePreviews(prev => prev.filter((_, i) => i !== index));

    // Update parent component
    updateParentImages();
  };

  // Move image position
  const handleMoveImage = (fromIndex, toIndex) => {
    if (toIndex < 0 || toIndex >= imageList.length) return;

    const newImageList = [...imageList];
    const newPreviews = [...imagePreviews];

    // Swap positions
    [newImageList[fromIndex], newImageList[toIndex]] = [newImageList[toIndex], newImageList[fromIndex]];
    [newPreviews[fromIndex], newPreviews[toIndex]] = [newPreviews[toIndex], newPreviews[fromIndex]];

    setImageList(newImageList);
    setImagePreviews(newPreviews);
    updateParentImages();
  };

  // Upload new images
  const uploadNewImages = async () => {
    if (selectedFiles.length === 0) return [];

    setUploading(true);
    const uploadedUrls = [];

    try {
      for (const file of selectedFiles) {
        const formData = new FormData();
        formData.append('file', file);

        const response = await partsService.uploadImage(formData);
        uploadedUrls.push(response.url);
      }

      setSelectedFiles([]);
      return uploadedUrls;
    } catch (uploadError) {
      setError(`Failed to upload images: ${uploadError.message}`);
      throw uploadError;
    } finally {
      setUploading(false);
    }
  };

  // Update parent component with current image state
  const updateParentImages = () => {
    if (!onImagesChange) return;

    const existingImages = imageList
      .filter(img => img.isExisting && !removedImages.includes(img.url))
      .map(img => img.url);

    const newImageUrls = imageList
      .filter(img => !img.isExisting && img.isUploaded)
      .map(img => img.url);

    onImagesChange([...existingImages, ...newImageUrls], removedImages);
  };

  // Handle save (upload new images and update state)
  const handleSave = async () => {
    try {
      const uploadedUrls = await uploadNewImages();

      // Update image list with uploaded URLs
      const updatedImageList = imageList.map(img => {
        if (!img.isExisting && !img.isUploaded) {
          const uploadedIndex = selectedFiles.findIndex(file =>
            URL.createObjectURL(file) === img.url
          );
          if (uploadedIndex !== -1) {
            return {
              ...img,
              url: uploadedUrls[uploadedIndex],
              isUploaded: true
            };
          }
        }
        return img;
      });

      setImageList(updatedImageList);
      updateParentImages();

      return true;
    } catch (error) {
      return false;
    }
  };

  // Image modal for full-size viewing
  const ImageModal = ({ imageUrl, onClose }) => (
    <div className="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50" onClick={onClose}>
      <div className="max-w-4xl max-h-4xl p-4">
        <img
          src={imageUrl.startsWith('/static/images') ? `${API_BASE_URL}${imageUrl}` : imageUrl}
          alt="Full size part image"
          className="max-w-full max-h-full object-contain"
          onClick={(e) => e.stopPropagation()}
        />
        <button
          onClick={onClose}
          className="absolute top-4 right-4 text-white bg-black bg-opacity-50 rounded-full p-2 hover:bg-opacity-75"
        >
          ✕
        </button>
      </div>
    </div>
  );

  // Display mode - show images in a grid
  if (!isEditing) {
    return (
      <div className={`part-photo-gallery ${className}`}>
        {imageList.length > 0 ? (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
            {imageList.map((image, index) => (
              <div key={image.id} className="relative group cursor-pointer">
                <img
                  src={image.url.startsWith('/static/images') ? `${API_BASE_URL}${image.url}` : image.url}
                  alt={`Part image ${index + 1}`}
                  className="w-full h-24 object-cover rounded-md shadow-sm hover:shadow-md transition-shadow"
                  onClick={() => setSelectedImageIndex(index)}
                  onError={(e) => {
                    e.target.onerror = null;
                    e.target.src = "https://placehold.co/100x100?text=Image+Error";
                  }}
                />
                <div className="absolute inset-0 bg-black bg-opacity-0 group-hover:bg-opacity-20 transition-opacity rounded-md flex items-center justify-center">
                  <span className="text-white text-sm opacity-0 group-hover:opacity-100 transition-opacity">
                    Click to enlarge
                  </span>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-8 text-gray-500">
            <div className="text-4xl mb-2">📷</div>
            <p>No images available</p>
          </div>
        )}

        {/* Image modal */}
        {selectedImageIndex !== null && (
          <ImageModal
            imageUrl={imageList[selectedImageIndex]?.url}
            onClose={() => setSelectedImageIndex(null)}
          />
        )}
      </div>
    );
  }

  // Editing mode - show upload interface and image management
  return (
    <div className={`part-photo-gallery-editor ${className}`}>
      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
          {error}
        </div>
      )}

      {/* Upload area */}
      <div className="mb-4">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Part Images (Max {maxImages})
        </label>
        <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center hover:border-gray-400 transition-colors">
          <input
            type="file"
            multiple
            accept="image/*"
            onChange={handleFileSelect}
            disabled={disabled || uploading || imageList.length >= maxImages}
            className="hidden"
            id="image-upload"
          />
          <label
            htmlFor="image-upload"
            className={`cursor-pointer ${disabled || uploading || imageList.length >= maxImages ? 'cursor-not-allowed opacity-50' : ''}`}
          >
            <div className="text-4xl mb-2">📷</div>
            <p className="text-sm text-gray-600">
              {imageList.length >= maxImages
                ? `Maximum ${maxImages} images reached`
                : 'Click to upload images or drag and drop'
              }
            </p>
            <p className="text-xs text-gray-500 mt-1">
              PNG, JPG, GIF up to 10MB each
            </p>
          </label>
        </div>
      </div>

      {/* Image grid with management controls */}
      {imageList.length > 0 && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {imageList.map((image, index) => (
            <div key={image.id} className="relative group">
              <img
                src={image.url.startsWith('/static/images') ? `${API_BASE_URL}${image.url}` : image.url}
                alt={`Part image ${index + 1}`}
                className="w-full h-24 object-cover rounded-md shadow-sm"
                onError={(e) => {
                  e.target.onerror = null;
                  e.target.src = "https://placehold.co/100x100?text=Image+Error";
                }}
              />

              {/* Image controls overlay */}
              <div className="absolute inset-0 bg-black bg-opacity-0 group-hover:bg-opacity-50 transition-opacity rounded-md">
                <div className="absolute top-1 right-1 opacity-0 group-hover:opacity-100 transition-opacity">
                  <button
                    type="button"
                    onClick={() => handleRemoveImage(index)}
                    disabled={disabled || uploading}
                    className="bg-red-500 text-white rounded-full p-1 text-xs hover:bg-red-600 disabled:opacity-50"
                    title="Remove image"
                  >
                    ✕
                  </button>
                </div>

                {/* Move controls */}
                <div className="absolute bottom-1 left-1 opacity-0 group-hover:opacity-100 transition-opacity flex space-x-1">
                  <button
                    type="button"
                    onClick={() => handleMoveImage(index, index - 1)}
                    disabled={disabled || uploading || index === 0}
                    className="bg-blue-500 text-white rounded p-1 text-xs hover:bg-blue-600 disabled:opacity-50"
                    title="Move left"
                  >
                    ←
                  </button>
                  <button
                    type="button"
                    onClick={() => handleMoveImage(index, index + 1)}
                    disabled={disabled || uploading || index === imageList.length - 1}
                    className="bg-blue-500 text-white rounded p-1 text-xs hover:bg-blue-600 disabled:opacity-50"
                    title="Move right"
                  >
                    →
                  </button>
                </div>
              </div>

              {/* Upload status indicator */}
              {!image.isUploaded && (
                <div className="absolute inset-0 bg-yellow-100 bg-opacity-75 rounded-md flex items-center justify-center">
                  <span className="text-yellow-800 text-xs font-medium">
                    {uploading ? 'Uploading...' : 'Pending upload'}
                  </span>
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {/* Upload status */}
      {uploading && (
        <div className="mt-4 text-center">
          <div className="inline-flex items-center">
            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600 mr-2"></div>
            <span className="text-sm text-gray-600">Uploading images...</span>
          </div>
        </div>
      )}
    </div>
  );
};

// Export the component and the save handler for external use
export default PartPhotoGallery;
export { PartPhotoGallery };