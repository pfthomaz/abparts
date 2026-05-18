import React, { useEffect, useRef, useState } from 'react';
import { Html5Qrcode } from 'html5-qrcode';
import { useTranslation } from '../hooks/useTranslation';

/**
 * QRScannerWrapper - Reusable QR code scanner component
 * Wraps html5-qrcode library in a React component with proper lifecycle management.
 *
 * Props:
 *   onScanSuccess(decodedText) - Called when a QR code is successfully scanned
 *   onScanError(error) - Called on scan errors (optional)
 *   onClose() - Called when user closes the scanner
 */
const QRScannerWrapper = ({ onScanSuccess, onScanError, onClose }) => {
  const { t } = useTranslation();
  const scannerRef = useRef(null);
  const html5QrcodeRef = useRef(null);
  const [status, setStatus] = useState('initializing'); // initializing | scanning | denied | error
  const [errorMessage, setErrorMessage] = useState('');

  useEffect(() => {
    let isMounted = true;

    const startScanner = async () => {
      const scannerId = 'qr-scanner-viewport';

      // Wait for the DOM element to be available
      if (!document.getElementById(scannerId)) {
        return;
      }

      try {
        const html5Qrcode = new Html5Qrcode(scannerId);
        html5QrcodeRef.current = html5Qrcode;

        const config = {
          fps: 10,
          qrbox: (viewfinderWidth, viewfinderHeight) => {
            // Responsive QR box - 70% of the smaller dimension, min 200px, max 300px
            const minDimension = Math.min(viewfinderWidth, viewfinderHeight);
            const size = Math.max(200, Math.min(300, Math.floor(minDimension * 0.7)));
            return { width: size, height: size };
          },
          aspectRatio: 1.0,
          // iOS requires playsinline for inline video playback
          videoConstraints: {
            facingMode: 'environment',
            width: { ideal: 1280 },
            height: { ideal: 720 },
          },
        };

        await html5Qrcode.start(
          { facingMode: 'environment' },
          config,
          (decodedText) => {
            if (isMounted && onScanSuccess) {
              onScanSuccess(decodedText);
            }
          },
          (scanError) => {
            // This fires frequently when no QR is in view - only forward meaningful errors
            if (onScanError && scanError && !scanError.includes('No MultiFormat Readers')) {
              onScanError(scanError);
            }
          }
        );

        if (isMounted) {
          setStatus('scanning');
        }
      } catch (err) {
        if (!isMounted) return;

        const errorMsg = err?.message || String(err);

        if (
          errorMsg.includes('NotAllowedError') ||
          errorMsg.includes('Permission') ||
          errorMsg.includes('denied')
        ) {
          setStatus('denied');
          setErrorMessage(
            t('qrScanner.permissionDenied') ||
            'Camera permission was denied. Please allow camera access in your browser settings and try again.'
          );
        } else if (
          errorMsg.includes('NotFoundError') ||
          errorMsg.includes('no camera')
        ) {
          setStatus('error');
          setErrorMessage(
            t('qrScanner.noCameraFound') ||
            'No camera found on this device.'
          );
        } else {
          setStatus('error');
          setErrorMessage(
            t('qrScanner.initError') ||
            `Failed to initialize scanner: ${errorMsg}`
          );
        }
      }
    };

    startScanner();

    return () => {
      isMounted = false;
      // Cleanup: stop the scanner on unmount
      if (html5QrcodeRef.current) {
        html5QrcodeRef.current
          .stop()
          .then(() => {
            html5QrcodeRef.current.clear();
          })
          .catch(() => {
            // Scanner may already be stopped
          });
      }
    };
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  return (
    <div className="relative w-full max-w-lg mx-auto">
      {/* Close button */}
      <div className="flex justify-between items-center mb-3">
        <h2 className="text-lg font-semibold text-gray-900">
          {t('qrScanner.title') || 'QR Scanner'}
        </h2>
        {onClose && (
          <button
            onClick={onClose}
            className="p-2 text-gray-500 hover:text-gray-700 rounded-full hover:bg-gray-100"
            aria-label={t('common.close') || 'Close'}
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        )}
      </div>

      {/* Loading state */}
      {status === 'initializing' && (
        <div className="bg-gray-100 rounded-lg p-12 text-center border-2 border-dashed border-gray-300">
          <div className="animate-spin w-8 h-8 border-4 border-blue-500 border-t-transparent rounded-full mx-auto mb-4"></div>
          <p className="text-gray-600 text-sm">
            {t('qrScanner.initializing') || 'Initializing camera...'}
          </p>
          <p className="text-gray-400 text-xs mt-2">
            {t('qrScanner.allowCamera') || 'Please allow camera access when prompted'}
          </p>
        </div>
      )}

      {/* Scanner viewport */}
      <div
        id="qr-scanner-viewport"
        ref={scannerRef}
        className={`w-full rounded-lg overflow-hidden qr-scanner-viewport ${status === 'initializing' ? 'h-0' : ''}`}
        style={{ maxHeight: '70vh' }}
      />

      {/* Permission denied state */}
      {status === 'denied' && (
        <div className="bg-red-50 rounded-lg p-6 text-center border border-red-200">
          <div className="text-4xl mb-3">🚫</div>
          <h3 className="text-red-800 font-medium mb-2">
            {t('qrScanner.cameraBlocked') || 'Camera Access Blocked'}
          </h3>
          <p className="text-red-600 text-sm mb-4">{errorMessage}</p>
          <div className="space-y-2">
            <button
              onClick={() => window.location.reload()}
              className="w-full px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 text-sm font-medium"
            >
              {t('qrScanner.tryAgain') || 'Try Again'}
            </button>
            {onClose && (
              <button
                onClick={onClose}
                className="w-full px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 text-sm"
              >
                {t('common.close') || 'Close'}
              </button>
            )}
          </div>
        </div>
      )}

      {/* Generic error state */}
      {status === 'error' && (
        <div className="bg-yellow-50 rounded-lg p-6 text-center border border-yellow-200">
          <div className="text-4xl mb-3">⚠️</div>
          <h3 className="text-yellow-800 font-medium mb-2">
            {t('qrScanner.scannerError') || 'Scanner Error'}
          </h3>
          <p className="text-yellow-700 text-sm mb-4">{errorMessage}</p>
          {onClose && (
            <button
              onClick={onClose}
              className="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 text-sm"
            >
              {t('common.close') || 'Close'}
            </button>
          )}
        </div>
      )}

      {/* Scanning hint */}
      {status === 'scanning' && (
        <p className="text-center text-gray-500 text-sm mt-3">
          {t('qrScanner.scanHint') || 'Point your camera at a QR code on a shelf label'}
        </p>
      )}
    </div>
  );
};

export default QRScannerWrapper;
