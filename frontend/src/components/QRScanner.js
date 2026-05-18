// frontend/src/components/QRScanner.js
// Full QR Scanner page - scans QR codes and navigates to location detail

import { useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { useTranslation } from '../hooks/useTranslation';
import QRScannerWrapper from './QRScannerWrapper';

/**
 * Parses a scanned QR URL to extract warehouse_id and location_code.
 * Expected URL format: .../locate/{warehouse_id}/{location_code}
 * Returns { warehouseId, locationCode } or null if invalid.
 */
function parseLocationUrl(url) {
  try {
    // Try to match the /locate/{warehouse_id}/{location_code} pattern
    // Works with full URLs or just paths
    const pattern = /\/locate\/([^/]+)\/([^/]+)/;
    const match = url.match(pattern);
    if (match) {
      return {
        warehouseId: decodeURIComponent(match[1]),
        locationCode: decodeURIComponent(match[2]),
      };
    }
    return null;
  } catch {
    return null;
  }
}

const QRScanner = () => {
  const navigate = useNavigate();
  const { t } = useTranslation();
  const [error, setError] = useState('');
  const [lastScanned, setLastScanned] = useState(null);
  const [manualCode, setManualCode] = useState('');
  const [manualWarehouseId, setManualWarehouseId] = useState('');

  const handleScanSuccess = useCallback((decodedText) => {
    const parsed = parseLocationUrl(decodedText);

    if (parsed) {
      setError('');
      setLastScanned({
        warehouseId: parsed.warehouseId,
        locationCode: parsed.locationCode,
        timestamp: new Date(),
      });
      // Navigate to the location detail page
      navigate(`/locate/${parsed.warehouseId}/${parsed.locationCode}`);
    } else {
      // Invalid QR code - not a location URL
      setError(t('qrScanner.invalidQr') || 'Not a valid location QR code');
      // Clear error after 3 seconds to allow scanning again
      setTimeout(() => setError(''), 3000);
    }
  }, [navigate, t]);

  const handleClose = useCallback(() => {
    navigate(-1);
  }, [navigate]);

  const handleManualSubmit = (e) => {
    e.preventDefault();
    const code = manualCode.trim();
    const warehouseId = manualWarehouseId.trim();

    if (!code) return;

    if (warehouseId) {
      navigate(`/locate/${warehouseId}/${code}`);
    } else {
      // If no warehouse ID provided, try to use the code as a full path
      // or show an error
      setError(t('qrScanner.enterWarehouseId') || 'Please enter a warehouse ID');
      setTimeout(() => setError(''), 3000);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col overflow-x-hidden">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 px-4 py-3 flex items-center justify-between sticky top-0 z-10">
        <button
          onClick={handleClose}
          className="p-2 -ml-2 text-gray-600 hover:text-gray-900 rounded-lg hover:bg-gray-100"
          aria-label={t('common.back') || 'Back'}
        >
          <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
          </svg>
        </button>
        <h1 className="text-lg font-semibold text-gray-900">
          {t('qrScanner.scanTitle') || 'Scan QR Code'}
        </h1>
        <button
          onClick={handleClose}
          className="p-2 -mr-2 text-gray-600 hover:text-gray-900 rounded-lg hover:bg-gray-100"
          aria-label={t('common.close') || 'Close'}
        >
          <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>

      {/* Scanner Area */}
      <div className="flex-1 flex flex-col items-center px-4 py-4">
        {/* Error message */}
        {error && (
          <div className="w-full max-w-lg mb-4 bg-red-50 border border-red-200 rounded-lg px-4 py-3 flex items-center gap-2">
            <svg className="w-5 h-5 text-red-500 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <p className="text-red-700 text-sm font-medium">{error}</p>
          </div>
        )}

        {/* QR Scanner */}
        <div className="w-full max-w-lg">
          <QRScannerWrapper
            onScanSuccess={handleScanSuccess}
            onClose={handleClose}
          />
        </div>

        {/* Last scanned indicator */}
        {lastScanned && (
          <div className="w-full max-w-lg mt-4 bg-green-50 border border-green-200 rounded-lg px-4 py-3">
            <div className="flex items-center gap-2">
              <svg className="w-5 h-5 text-green-600 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
              <div>
                <p className="text-green-800 text-sm font-medium">
                  {t('qrScanner.lastScanned') || 'Last scanned'}: {lastScanned.locationCode}
                </p>
                <p className="text-green-600 text-xs">
                  {lastScanned.timestamp.toLocaleTimeString()}
                </p>
              </div>
            </div>
          </div>
        )}

        {/* Divider */}
        <div className="w-full max-w-lg my-6 flex items-center gap-3">
          <div className="flex-1 border-t border-gray-300"></div>
          <span className="text-gray-500 text-sm font-medium">
            {t('qrScanner.orManualEntry') || 'or enter manually'}
          </span>
          <div className="flex-1 border-t border-gray-300"></div>
        </div>

        {/* Manual entry */}
        <form onSubmit={handleManualSubmit} className="w-full max-w-lg space-y-3">
          <div>
            <label htmlFor="manual-warehouse" className="block text-sm font-medium text-gray-700 mb-1">
              {t('qrScanner.warehouseId') || 'Warehouse ID'}
            </label>
            <input
              id="manual-warehouse"
              type="text"
              value={manualWarehouseId}
              onChange={(e) => setManualWarehouseId(e.target.value)}
              placeholder={t('qrScanner.warehouseIdPlaceholder') || 'e.g., warehouse-uuid'}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg text-base focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            />
          </div>
          <div>
            <label htmlFor="manual-code" className="block text-sm font-medium text-gray-700 mb-1">
              {t('qrScanner.locationCode') || 'Location Code'}
            </label>
            <input
              id="manual-code"
              type="text"
              value={manualCode}
              onChange={(e) => setManualCode(e.target.value)}
              placeholder={t('qrScanner.locationCodePlaceholder') || 'e.g., A1, B3-top'}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg text-base focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            />
          </div>
          <button
            type="submit"
            disabled={!manualCode.trim() || !manualWarehouseId.trim()}
            className="w-full px-4 py-3 bg-blue-600 text-white rounded-lg font-medium text-base hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
          >
            {t('qrScanner.goToLocation') || 'Go to Location'}
          </button>
        </form>
      </div>
    </div>
  );
};

export default QRScanner;
