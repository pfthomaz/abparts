// frontend/src/pages/LocationDetail.js

import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useTranslation } from '../hooks/useTranslation';
import { API_BASE_URL } from '../services/api';

const LocationDetail = () => {
  const { warehouse_id, location_code } = useParams();
  const navigate = useNavigate();
  const { t } = useTranslation();

  const [locationData, setLocationData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchLocationData = async () => {
      setLoading(true);
      setError(null);
      try {
        const response = await fetch(
          `${API_BASE_URL}/locate/${warehouse_id}/${encodeURIComponent(location_code)}`
        );
        if (!response.ok) {
          if (response.status === 404) {
            setError('not_found');
          } else {
            setError('server_error');
          }
          return;
        }
        const data = await response.json();
        setLocationData(data);
      } catch (err) {
        console.error('Failed to fetch location:', err);
        setError('network_error');
      } finally {
        setLoading(false);
      }
    };

    if (warehouse_id && location_code) {
      fetchLocationData();
    }
  }, [warehouse_id, location_code]);

  // Loading state - skeleton
  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 p-4">
        <div className="max-w-lg mx-auto space-y-4">
          {/* Skeleton header */}
          <div className="animate-pulse">
            <div className="bg-gray-200 rounded-2xl h-28 mb-4"></div>
            <div className="bg-gray-200 rounded-lg h-5 w-48 mb-6"></div>
          </div>
          {/* Skeleton cards */}
          {[1, 2, 3].map((i) => (
            <div key={i} className="animate-pulse bg-white rounded-xl p-4 shadow-sm">
              <div className="flex gap-4">
                <div className="bg-gray-200 rounded-lg w-20 h-20"></div>
                <div className="flex-1 space-y-3">
                  <div className="bg-gray-200 rounded h-5 w-3/4"></div>
                  <div className="bg-gray-200 rounded h-4 w-1/2"></div>
                  <div className="bg-gray-200 rounded h-8 w-16"></div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  // Error state
  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 p-4 flex items-center justify-center">
        <div className="max-w-sm w-full text-center space-y-4">
          <div className="text-6xl">
            {error === 'not_found' ? '🔍' : '⚠️'}
          </div>
          <h1 className="text-2xl font-bold text-gray-900">
            {error === 'not_found'
              ? (t('locationDetail.notFound') || 'Location Not Found')
              : (t('locationDetail.error') || 'Something Went Wrong')}
          </h1>
          <p className="text-gray-600">
            {error === 'not_found'
              ? (t('locationDetail.notFoundDescription') || `Location "${location_code}" was not found in this warehouse.`)
              : (t('locationDetail.errorDescription') || 'Could not load location data. Please try again.')}
          </p>
          <div className="flex flex-col gap-3 pt-4">
            <button
              onClick={() => navigate('/scan')}
              className="w-full bg-blue-600 text-white px-6 py-3 rounded-xl text-lg font-semibold hover:bg-blue-700 active:bg-blue-800 transition-colors"
            >
              📷 {t('locationDetail.scanAnother') || 'Scan Another'}
            </button>
            <button
              onClick={() => navigate(-1)}
              className="w-full bg-gray-100 text-gray-700 px-6 py-3 rounded-xl text-lg font-medium hover:bg-gray-200 active:bg-gray-300 transition-colors"
            >
              ← {t('common.back') || 'Back'}
            </button>
          </div>
        </div>
      </div>
    );
  }

  // Success state
  const { location_code: code, description, parts_count, parts } = locationData;

  return (
    <div className="min-h-screen bg-gray-50 pb-28">
      {/* Top navigation bar */}
      <div className="sticky top-0 z-10 bg-white border-b border-gray-200 px-4 py-3">
        <div className="max-w-lg mx-auto flex items-center justify-between">
          <button
            onClick={() => navigate(-1)}
            className="text-gray-600 hover:text-gray-900 p-2 -ml-2 rounded-lg active:bg-gray-100"
            aria-label={t('common.back') || 'Back'}
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            </svg>
          </button>
          <span className="text-sm font-medium text-gray-500">
            {t('locationDetail.title') || 'Location Detail'}
          </span>
          <button
            onClick={() => navigate('/scan')}
            className="text-blue-600 hover:text-blue-800 p-2 -mr-2 rounded-lg active:bg-blue-50"
            aria-label={t('locationDetail.scanAnother') || 'Scan Another'}
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 9V5a2 2 0 012-2h4M3 15v4a2 2 0 002 2h4m8-18h4a2 2 0 012 2v4m0 6v4a2 2 0 01-2 2h-4" />
            </svg>
          </button>
        </div>
      </div>

      <div className="max-w-lg mx-auto px-4 pt-6 space-y-5">
        {/* Location Header Badge */}
        <div className="bg-gradient-to-br from-blue-600 to-blue-700 rounded-2xl p-6 text-center shadow-lg">
          <div className="text-blue-200 text-sm font-medium uppercase tracking-wide mb-1">
            {t('locationDetail.locationCode') || 'Location'}
          </div>
          <div className="text-white text-4xl sm:text-5xl font-black tracking-tight">
            {code}
          </div>
          {description && (
            <div className="text-blue-100 text-base mt-2">
              {description}
            </div>
          )}
        </div>

        {/* Parts count summary */}
        <div className="flex items-center justify-between px-1">
          <h2 className="text-lg font-semibold text-gray-900">
            {t('locationDetail.partsHere') || 'Parts at this location'}
          </h2>
          <span className="bg-gray-100 text-gray-700 px-3 py-1 rounded-full text-sm font-medium">
            {parts_count} {parts_count === 1
              ? (t('locationDetail.part') || 'part')
              : (t('locationDetail.parts') || 'parts')}
          </span>
        </div>

        {/* Parts List */}
        {parts && parts.length > 0 ? (
          <div className="space-y-3">
            {parts.map((part) => (
              <div
                key={part.inventory_id}
                className="bg-white rounded-xl border border-gray-200 p-4 shadow-sm hover:shadow-md transition-shadow"
              >
                <div className="flex gap-4 items-start">
                  {/* Part Photo */}
                  <div className="flex-shrink-0">
                    {part.photo_url ? (
                      <img
                        src={part.photo_url}
                        alt={part.part_name}
                        className="w-20 h-20 sm:w-24 sm:h-24 rounded-lg object-cover bg-gray-100 max-w-full"
                        onError={(e) => {
                          e.target.style.display = 'none';
                          e.target.nextSibling.style.display = 'flex';
                        }}
                      />
                    ) : null}
                    <div
                      className={`w-20 h-20 sm:w-24 sm:h-24 rounded-lg bg-gray-100 items-center justify-center ${
                        part.photo_url ? 'hidden' : 'flex'
                      }`}
                    >
                      <svg className="w-10 h-10 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" />
                      </svg>
                    </div>
                  </div>

                  {/* Part Info */}
                  <div className="flex-1 min-w-0">
                    <h3 className="text-lg font-bold text-gray-900 leading-tight truncate">
                      {part.part_name}
                    </h3>
                    {part.sku && (
                      <p className="text-sm text-gray-500 mt-0.5 font-mono">
                        {part.sku}
                      </p>
                    )}
                    {/* Quantity - prominent */}
                    <div className="mt-2 inline-flex items-center gap-1.5 bg-green-50 border border-green-200 rounded-lg px-3 py-1.5">
                      <span className="text-green-700 text-xs font-medium uppercase">
                        {t('locationDetail.qty') || 'Qty'}
                      </span>
                      <span className="text-green-800 text-xl font-black">
                        {Number(part.quantity)}
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          /* Empty state - location exists but no parts */
          <div className="bg-white rounded-xl border border-gray-200 p-8 text-center">
            <div className="text-5xl mb-3">📦</div>
            <h3 className="text-lg font-semibold text-gray-700 mb-1">
              {t('locationDetail.noParts') || 'No parts here'}
            </h3>
            <p className="text-gray-500 text-sm">
              {t('locationDetail.noPartsDescription') || 'This location is empty. No parts have been assigned yet.'}
            </p>
          </div>
        )}
      </div>

      {/* Fixed bottom action bar with safe-area-inset for notched phones */}
      <div className="fixed bottom-0 left-0 right-0 bg-white border-t border-gray-200 px-4 pt-4 shadow-lg fixed-bottom-bar" style={{ paddingBottom: 'max(1rem, env(safe-area-inset-bottom))' }}>
        <div className="max-w-lg mx-auto">
          <button
            onClick={() => navigate('/scan')}
            className="w-full bg-blue-600 text-white px-6 py-4 rounded-xl text-lg font-semibold hover:bg-blue-700 active:bg-blue-800 transition-colors flex items-center justify-center gap-2 touch-action-manipulation"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 9V5a2 2 0 012-2h4M3 15v4a2 2 0 002 2h4m8-18h4a2 2 0 012 2v4m0 6v4a2 2 0 01-2 2h-4" />
            </svg>
            {t('locationDetail.scanAnother') || 'Scan Another'}
          </button>
        </div>
      </div>
    </div>
  );
};

export default LocationDetail;
