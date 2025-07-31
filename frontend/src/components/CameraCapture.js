// frontend/src/components/CameraCapture.js

import React, { useState, useRef, useCallback } from 'react';

const CameraCapture = ({ onCapture, onClose, maxPhotos = 4, existingPhotos = [] }) => {
  const [isCapturing, setIsCapturing] = useState(false);
  const [stream, setStream] = useState(null);
  const [capturedPhotos, setCapturedPhotos] = useState(existingPhotos);
  const [error, setError] = useState('');
  const [cameraFacing, setCameraFacing] = useState('environment'); // 'user' for front, 'environment' for back

  const videoRef = useRef(null);
  const canvasRef = useRef(null);

  // Check if device supports camera
  const isCameraSupported = () => {
    return !!(navigator.mediaDevices && navigator.mediaDevices.getUserMedia);
  };

  // Start camera stream
  const startCamera = useCallback(async () => {
    if (!isCameraSupported()) {
      setError('Camera is not supported on this device');
      return;
    }

    try {
      setError('');
      const constraints = {
        video: {
          facingMode: cameraFacing,
          width: { ideal: 1280 },
          height: { ideal: 720 }
        }
      };

      const mediaStream = await navigator.mediaDevices.getUserMedia(constraints);
      setStream(mediaStream);

      if (videoRef.current) {
        videoRef.current.srcObject = mediaStream;
        videoRef.current.play();
      }

      setIsCapturing(true);
    } catch (err) {
      console.error('Error accessing camera:', err);
      setError('Unable to access camera. Please check permissions.');
    }
  }, [cameraFacing]);

  // Stop camera stream
  const stopCamera = useCallback(() => {
    if (stream) {
      stream.getTracks().forEach(track => track.stop());
      setStream(null);
    }
    setIsCapturing(false);
  }, [stream]);

  // Capture photo from video stream
  const capturePhoto = useCallback(() => {
    if (!videoRef.current || !canvasRef.current) return;

    const video = videoRef.current;
    const canvas = canvasRef.current;
    const context = canvas.getContext('2d');

    // Set canvas dimensions to match video
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;

    // Draw current video frame to canvas
    context.drawImage(video, 0, 0, canvas.width, canvas.height);

    // Convert canvas to blob
    canvas.toBlob((blob) => {
      if (blob) {
        const photoUrl = URL.createObjectURL(blob);
        const newPhoto = {
          id: Date.now(),
          url: photoUrl,
          blob: blob,
          timestamp: new Date().toISOString()
        };

        setCapturedPhotos(prev => [...prev, newPhoto]);
      }
    }, 'image/jpeg', 0.8);
  }, []);

  // Remove captured photo
  const removePhoto = useCallback((photoId) => {
    setCapturedPhotos(prev => {
      const updated = prev.filter(photo => photo.id !== photoId);
      // Revoke object URL to free memory
      const photoToRemove = prev.find(photo => photo.id === photoId);
      if (photoToRemove && photoToRemove.url.startsWith('blob:')) {
        URL.revokeObjectURL(photoToRemove.url);
      }
      return updated;
    });
  }, []);

  // Switch camera (front/back)
  const switchCamera = useCallback(() => {
    setCameraFacing(prev => prev === 'user' ? 'environment' : 'user');
    if (isCapturing) {
      stopCamera();
      // Restart with new facing mode
      setTimeout(() => {
        startCamera();
      }, 100);
    }
  }, [isCapturing, stopCamera, startCamera]);

  // Handle file input (fallback for devices without camera)
  const handleFileInput = useCallback((event) => {
    const files = Array.from(event.target.files);

    files.forEach(file => {
      if (file.type.startsWith('image/')) {
        const photoUrl = URL.createObjectURL(file);
        const newPhoto = {
          id: Date.now() + Math.random(),
          url: photoUrl,
          blob: file,
          timestamp: new Date().toISOString()
        };

        setCapturedPhotos(prev => [...prev, newPhoto]);
      }
    });

    // Clear input
    event.target.value = '';
  }, []);

  // Submit captured photos
  const handleSubmit = useCallback(() => {
    onCapture(capturedPhotos);
    stopCamera();
    onClose();
  }, [capturedPhotos, onCapture, stopCamera, onClose]);

  // Cleanup on unmount
  React.useEffect(() => {
    return () => {
      stopCamera();
      // Cleanup object URLs
      capturedPhotos.forEach(photo => {
        if (photo.url.startsWith('blob:')) {
          URL.revokeObjectURL(photo.url);
        }
      });
    };
  }, [stopCamera, capturedPhotos]);

  const canCaptureMore = capturedPhotos.length < maxPhotos;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-90 z-50 flex flex-col">
      {/* Header */}
      <div className="bg-white p-4 flex items-center justify-between">
        <h2 className="text-lg font-semibold text-gray-900">
          Capture Part Photos ({capturedPhotos.length}/{maxPhotos})
        </h2>
        <button
          onClick={() => {
            stopCamera();
            onClose();
          }}
          className="p-2 text-gray-400 hover:text-gray-600 rounded-full hover:bg-gray-100"
        >
          <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>

      {/* Error Message */}
      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 mx-4 rounded">
          {error}
        </div>
      )}

      {/* Camera View */}
      <div className="flex-1 flex flex-col items-center justify-center p-4">
        {!isCapturing ? (
          <div className="text-center space-y-4">
            <div className="w-32 h-32 bg-gray-200 rounded-full flex items-center justify-center mx-auto">
              <svg className="w-16 h-16 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z" />
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 13a3 3 0 11-6 0 3 3 0 016 0z" />
              </svg>
            </div>

            {isCameraSupported() ? (
              <button
                onClick={startCamera}
                disabled={!canCaptureMore}
                className="bg-blue-600 text-white px-6 py-3 rounded-lg font-semibold hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {canCaptureMore ? 'Start Camera' : 'Maximum photos reached'}
              </button>
            ) : (
              <div className="space-y-2">
                <p className="text-white text-sm">Camera not available</p>
                <label className="bg-blue-600 text-white px-6 py-3 rounded-lg font-semibold hover:bg-blue-700 cursor-pointer inline-block">
                  Choose Photos
                  <input
                    type="file"
                    accept="image/*"
                    multiple
                    onChange={handleFileInput}
                    className="hidden"
                    disabled={!canCaptureMore}
                  />
                </label>
              </div>
            )}
          </div>
        ) : (
          <div className="w-full max-w-md">
            <div className="relative bg-black rounded-lg overflow-hidden">
              <video
                ref={videoRef}
                className="w-full h-auto"
                autoPlay
                playsInline
                muted
              />

              {/* Camera Controls Overlay */}
              <div className="absolute bottom-4 left-0 right-0 flex items-center justify-center space-x-4">
                {/* Switch Camera */}
                <button
                  onClick={switchCamera}
                  className="bg-white bg-opacity-20 text-white p-3 rounded-full hover:bg-opacity-30 transition-colors"
                >
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                  </svg>
                </button>

                {/* Capture Button */}
                <button
                  onClick={capturePhoto}
                  disabled={!canCaptureMore}
                  className="bg-white text-gray-900 p-4 rounded-full hover:bg-gray-100 disabled:opacity-50 disabled:cursor-not-allowed shadow-lg"
                >
                  <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z" />
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 13a3 3 0 11-6 0 3 3 0 016 0z" />
                  </svg>
                </button>

                {/* Stop Camera */}
                <button
                  onClick={stopCamera}
                  className="bg-white bg-opacity-20 text-white p-3 rounded-full hover:bg-opacity-30 transition-colors"
                >
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Hidden canvas for photo capture */}
        <canvas ref={canvasRef} className="hidden" />
      </div>

      {/* Captured Photos Preview */}
      {capturedPhotos.length > 0 && (
        <div className="bg-white p-4">
          <h3 className="text-sm font-semibold text-gray-900 mb-3">Captured Photos</h3>
          <div className="flex space-x-2 overflow-x-auto pb-2">
            {capturedPhotos.map((photo) => (
              <div key={photo.id} className="relative flex-shrink-0">
                <img
                  src={photo.url}
                  alt="Captured"
                  className="w-16 h-16 object-cover rounded-lg border border-gray-200"
                />
                <button
                  onClick={() => removePhoto(photo.id)}
                  className="absolute -top-2 -right-2 bg-red-500 text-white rounded-full w-6 h-6 flex items-center justify-center text-xs hover:bg-red-600"
                >
                  ×
                </button>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Bottom Actions */}
      <div className="bg-white p-4 flex space-x-3">
        {/* File Input Fallback */}
        {!isCapturing && isCameraSupported() && canCaptureMore && (
          <label className="flex-1 bg-gray-100 text-gray-700 py-3 px-4 rounded-lg font-semibold text-center hover:bg-gray-200 cursor-pointer">
            Choose Files
            <input
              type="file"
              accept="image/*"
              multiple
              onChange={handleFileInput}
              className="hidden"
            />
          </label>
        )}

        <button
          onClick={handleSubmit}
          className="flex-1 bg-blue-600 text-white py-3 px-4 rounded-lg font-semibold hover:bg-blue-700"
        >
          Use Photos ({capturedPhotos.length})
        </button>
      </div>
    </div>
  );
};

export default CameraCapture;