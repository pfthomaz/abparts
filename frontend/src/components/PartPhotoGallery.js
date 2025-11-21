// frontend/src/components/PartPhotoGallery.js

import React, { useState, useEffect, useRef, useImperativeHandle, forwardRef } from 'react';
import { API_BASE_URL } from '../services/api';
import { partsService } from '../services/partsService';

/**
 * PartPhotoGallery component for managing up to 4 part images
 * Supports viewing, uploading, removing, and reordering images
 * 
 * Simplified architecture to avoid circular dependencies and initialization issues
 */
const PartPhotoGallery = forwardRef(({
  images = [],
  onImagesChange,
  isEditing = false,
  maxImages = 4,
  className = '',
  disabled = false
}, ref) => {
  // Simplified state management
  const [currentImages, setCurrentImages] = useState([]);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState(null);
  const [selectedImageIndex, setSelectedImageIndex] = useState(null);

  // Track previous image URLs to prevent unnecessary parent notifications
  const previousImageUrls = useRef([]);

  // Initialize images from props - only when props change
  useEffect(() => {
    console.log('PartPhotoGallery: images prop changed', images);
    if (Array.isArray(images)) {
      const processedImages = images.map((url, index) => ({
        id: `existing-${index}-${Date.now()}`,
        url: url,
        isExisting: true
      }));
      console.log('PartPhotoGallery: processed images', processedImages);
      setCurrentImages(processedImages);
    }
  }, [images]);

  // Expose methods to parent component
  useImperativeHandle(ref, () => ({
    getCurrentImageUrls: () => currentImages.map(img => img.url)
  }));

  // Handle file selection and immediate upload
  const handleFileSelect = async (event) => {
    const files = Array.from(event.target.files);

    if (currentImages.length + files.length > maxImages) {
      setError(`You can only upload a maximum of ${maxImages} images per part.`);
      return;
    }

    setError(null);
    event.target.value = ''; // Clear input

    if (files.length === 0) return;

    setUploading(true);

    try {
      const uploadPromises = files.map(async (file) => {
        const formData = new FormData();
        formData.append('file', file);

        const response = await partsService.uploadImage(formData);
        return {
          id: `uploaded-${Date.now()}-${Math.random()}`,
          url: response.url,
          isExisting: false
        };
      });

      const uploadedImages = await Promise.all(uploadPromises);

      // Add uploaded images to current list
      const newImages = [...currentImages, ...uploadedImages];
      setCurrentImages(newImages);

    } catch (uploadError) {
      console.error('Upload error:', uploadError);
      setError(`Upload failed: ${uploadError.message || 'Unknown error'}`);
    } finally {
      setUploading(false);
    }
  };

  // Remove image
  const handleRemoveImage = (index) => {
    const newImages = currentImages.filter((_, i) => i !== index);
    setCurrentImages(newImages);
  };

  // Move image position
  const handleMoveImage = (fromIndex, toIndex) => {
    if (toIndex < 0 || toIndex >= currentImages.length) return;

    const newImages = [...currentImages];
    [newImages[fromIndex], newImages[toIndex]] = [newImages[toIndex], newImages[fromIndex]];
    setCurrentImages(newImages);
  };

  // Image modal component
  const ImageModal = ({ imageUrl, onClose }) => {
    console.log('ImageModal rendering with URL:', imageUrl);
    return (
      <div
        className="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50"
        onClick={onClose}
        style={{ zIndex: 9999 }}
      >
        <div className="relative max-w-4xl max-h-screen p-4">
          <button
            onClick={onClose}
            className="absolute top-2 right-2 text-white bg-black bg-opacity-50 rounded-full w-8 h-8 flex items-center justify-center hover:bg-opacity-75 z-10"
          >
            ✕
          </button>
          <img
            src={imageUrl.startsWith('/static/images') ? `${API_BASE_URL}${imageUrl}` : imageUrl}
            alt="Full size part"
            className="max-w-full max-h-screen object-contain"
            onClick={(e) => e.stopPropagation()}
          />
        </div>
      </div>
    );
  };

  // Display mode - show images in a grid
  if (!isEditing) {
    return (
      <>
        <div className={`part-photo-gallery ${className}`}>
          {currentImages.length > 0 ? (
            <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
              {currentImages.map((image, index) => (
                <div 
                  key={image.id} 
                  className="relative group cursor-pointer"
                  onClick={() => {
                    console.log('Image clicked, index:', index);
                    setSelectedImageIndex(index);
                  }}
                >
                  <img
                    src={image.url.startsWith('/static/images') ? `${API_BASE_URL}${image.url}` : image.url}
                    alt={`Part ${index + 1}`}
                    className="w-full h-24 object-cover rounded-md shadow-sm hover:shadow-md transition-shadow"
                    onError={(e) => {
                      e.target.onerror = null;
                      e.target.src = "https://placehold.co/100x100?text=Image+Error";
                    }}
                  />
                  <div className="absolute inset-0 bg-black bg-opacity-0 group-hover:bg-opacity-20 transition-opacity rounded-md flex items-center justify-center pointer-events-none">
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
        </div>

        {/* Image modal - render outside the container for proper z-index */}
        {selectedImageIndex !== null && currentImages[selectedImageIndex] && (
          <ImageModal
            imageUrl={currentImages[selectedImageIndex].url}
            onClose={() => {
              console.log('Closing modal');
              setSelectedImageIndex(null);
            }}
          />
        )}
      </>
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
            disabled={disabled || uploading || currentImages.length >= maxImages}
            className="hidden"
            id="image-upload"
          />
          <label
            htmlFor="image-upload"
            className={`cursor-pointer ${disabled || uploading || currentImages.length >= maxImages ? 'cursor-not-allowed opacity-50' : ''}`}
          >
            <div className="text-4xl mb-2">📷</div>
            <p className="text-sm text-gray-600">
              {currentImages.length >= maxImages
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
      {currentImages.length > 0 && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {currentImages.map((image, index) => (
            <div key={image.id} className="relative group">
              <img
                src={image.url.startsWith('/static/images') ? `${API_BASE_URL}${image.url}` : image.url}
                alt={`Part ${index + 1}`}
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
                    title="Remove"
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
                    disabled={disabled || uploading || index === currentImages.length - 1}
                    className="bg-blue-500 text-white rounded p-1 text-xs hover:bg-blue-600 disabled:opacity-50"
                    title="Move right"
                  >
                    →
                  </button>
                </div>
              </div>
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
});

export default PartPhotoGallery;