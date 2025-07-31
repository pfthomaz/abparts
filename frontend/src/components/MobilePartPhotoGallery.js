// frontend/src/components/MobilePartPhotoGallery.js

import React, { useState } from 'react';
import CameraCapture from './CameraCapture';

const MobilePartPhotoGallery = ({
  photos = [],
  onPhotosChange,
  maxPhotos = 4,
  editable = true,
  className = ''
}) => {
  const [showCamera, setShowCamera] = useState(false);
  const [selectedPhoto, setSelectedPhoto] = useState(null);

  const handleCameraCapture = (capturedPhotos) => {
    // Convert captured photos to the format expected by the parent component
    const newPhotos = capturedPhotos.map(photo => ({
      id: photo.id,
      url: photo.url,
      blob: photo.blob,
      timestamp: photo.timestamp
    }));

    // Combine with existing photos, respecting maxPhotos limit
    const allPhotos = [...photos, ...newPhotos];
    const limitedPhotos = allPhotos.slice(0, maxPhotos);

    if (onPhotosChange) {
      onPhotosChange(limitedPhotos);
    }
  };

  const removePhoto = (photoId) => {
    const updatedPhotos = photos.filter(photo => photo.id !== photoId);

    // Revoke object URL to free memory if it's a blob URL
    const photoToRemove = photos.find(photo => photo.id === photoId);
    if (photoToRemove && photoToRemove.url && photoToRemove.url.startsWith('blob:')) {
      URL.revokeObjectURL(photoToRemove.url);
    }

    if (onPhotosChange) {
      onPhotosChange(updatedPhotos);
    }
  };

  const handleFileInput = (event) => {
    const files = Array.from(event.target.files);
    const remainingSlots = maxPhotos - photos.length;
    const filesToProcess = files.slice(0, remainingSlots);

    const newPhotos = filesToProcess.map(file => ({
      id: Date.now() + Math.random(),
      url: URL.createObjectURL(file),
      blob: file,
      timestamp: new Date().toISOString()
    }));

    const allPhotos = [...photos, ...newPhotos];

    if (onPhotosChange) {
      onPhotosChange(allPhotos);
    }

    // Clear input
    event.target.value = '';
  };

  const canAddMore = photos.length < maxPhotos;

  return (
    <div className={`space-y-4 ${className}`}>
      {/* Photo Grid */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        {photos.map((photo, index) => (
          <div key={photo.id} className="relative group">
            <div
              className="aspect-square min-h-[120px] sm:min-h-0 bg-gray-100 rounded-lg overflow-hidden border-2 border-gray-200 cursor-pointer hover:border-blue-300 transition-colors"
              onClick={() => setSelectedPhoto(photo)}
            >
              <img
                src={photo.url}
                alt={`Part photo ${index + 1}`}
                className="w-full h-full object-cover"
                loading="lazy"
              />
            </div>

            {/* Remove button */}
            {editable && (
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  removePhoto(photo.id);
                }}
                className="absolute -top-2 -right-2 bg-red-500 text-white rounded-full w-6 h-6 flex items-center justify-center text-sm hover:bg-red-600 shadow-lg opacity-0 group-hover:opacity-100 transition-opacity"
              >
                ×
              </button>
            )}

            {/* Photo number indicator */}
            <div className="absolute bottom-1 left-1 bg-black bg-opacity-50 text-white text-xs px-2 py-1 rounded">
              {index + 1}
            </div>
          </div>
        ))}

        {/* Add Photo Button */}
        {editable && canAddMore && (
          <div className="aspect-square min-h-[120px] sm:min-h-0 border-2 border-dashed border-gray-300 rounded-lg flex flex-col items-center justify-center space-y-2 hover:border-blue-400 hover:bg-blue-50 transition-colors cursor-pointer group">
            <div className="flex flex-col items-center space-y-2">
              {/* Camera Button */}
              <button
                onClick={() => setShowCamera(true)}
                className="p-3 bg-blue-100 text-blue-600 rounded-full hover:bg-blue-200 transition-colors group-hover:scale-110 transform duration-200"
              >
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z" />
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 13a3 3 0 11-6 0 3 3 0 016 0z" />
                </svg>
              </button>

              <span className="text-xs text-gray-500 font-medium">Camera</span>

              {/* File Input Alternative */}
              <label className="text-xs text-blue-600 hover:text-blue-800 cursor-pointer underline">
                or choose files
                <input
                  type="file"
                  accept="image/*"
                  multiple
                  onChange={handleFileInput}
                  className="hidden"
                />
              </label>
            </div>
          </div>
        )}
      </div>

      {/* Photo Counter */}
      <div className="flex items-center justify-between text-sm text-gray-600">
        <span>{photos.length} of {maxPhotos} photos</span>
        {photos.length > 0 && (
          <span className="text-xs text-gray-500">Tap photo to view full size</span>
        )}
      </div>

      {/* Camera Modal */}
      {showCamera && (
        <CameraCapture
          onCapture={handleCameraCapture}
          onClose={() => setShowCamera(false)}
          maxPhotos={maxPhotos - photos.length}
          existingPhotos={photos}
        />
      )}

      {/* Photo Viewer Modal */}
      {selectedPhoto && (
        <div className="fixed inset-0 bg-black bg-opacity-90 z-50 flex items-center justify-center p-4">
          <div className="relative max-w-full max-h-full">
            <img
              src={selectedPhoto.url}
              alt="Full size part photo"
              className="max-w-full max-h-full object-contain"
            />

            {/* Close button */}
            <button
              onClick={() => setSelectedPhoto(null)}
              className="absolute top-4 right-4 bg-white bg-opacity-20 text-white p-2 rounded-full hover:bg-opacity-30 transition-colors"
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>

            {/* Photo info */}
            <div className="absolute bottom-4 left-4 bg-black bg-opacity-50 text-white px-3 py-2 rounded-lg text-sm">
              {selectedPhoto.timestamp && (
                <div>Captured: {new Date(selectedPhoto.timestamp).toLocaleString()}</div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Mobile-specific styles handled by Tailwind CSS classes */}
    </div>
  );
};

export default MobilePartPhotoGallery;