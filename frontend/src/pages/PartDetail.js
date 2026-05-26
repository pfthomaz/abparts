// frontend/src/pages/PartDetail.js

import { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useTranslation } from '../hooks/useTranslation';
import { api } from '../services/api';

const PartDetail = () => {
  const { partId } = useParams();
  const navigate = useNavigate();
  const { t } = useTranslation();

  const [part, setPart] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [activePhoto, setActivePhoto] = useState(0);
  const galleryRef = useRef(null);

  useEffect(() => {
    const fetchPart = async () => {
      setLoading(true);
      setError(null);
      try {
        const data = await api.get(`/parts/${partId}`);
        setPart(data);
      } catch (err) {
        console.error('Failed to fetch part:', err);
        if (err.response?.status === 404) {
          setError('not_found');
        } else {
          setError('server_error');
        }
      } finally {
        setLoading(false);
      }
    };

    if (partId) {
      fetchPart();
    }
  }, [partId]);

  // Loading state - skeleton
  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 p-4">
        <div className="max-w-lg mx-auto space-y-4">
          <div className="animate-pulse">
            <div className="bg-gray-200 rounded-2xl h-28 mb-4"></div>
            <div className="bg-gray-200 rounded-lg h-5 w-48 mb-6"></div>
          </div>
          {[1, 2, 3].map((i) => (
            <div key={i} className="animate-pulse bg-white rounded-xl p-4 shadow-sm">
              <div className="space-y-3">
                <div className="bg-gray-200 rounded h-5 w-3/4"></div>
                <div className="bg-gray-200 rounded h-4 w-1/2"></div>
                <div className="bg-gray-200 rounded h-4 w-2/3"></div>
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
              ? (t('partDetail.notFound') || 'Part Not Found')
              : (t('partDetail.error') || 'Something Went Wrong')}
          </h1>
          <p className="text-gray-600">
            {error === 'not_found'
              ? (t('partDetail.notFoundDescription') || 'This part could not be found. It may have been removed.')
              : (t('partDetail.errorDescription') || 'Could not load part data. Please try again.')}
          </p>
          <div className="flex flex-col gap-3 pt-4">
            <button
              onClick={() => navigate('/scan')}
              className="w-full bg-blue-600 text-white px-6 py-3 rounded-xl text-lg font-semibold hover:bg-blue-700 active:bg-blue-800 transition-colors"
            >
              📷 {t('partDetail.scanAnother') || 'Scan Another'}
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

  const photos = part?.image_urls || [];

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
            {t('partDetail.title') || 'Part Detail'}
          </span>
          <button
            onClick={() => navigate('/scan')}
            className="text-blue-600 hover:text-blue-800 p-2 -mr-2 rounded-lg active:bg-blue-50"
            aria-label={t('partDetail.scanAnother') || 'Scan Another'}
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 9V5a2 2 0 012-2h4M3 15v4a2 2 0 002 2h4m8-18h4a2 2 0 012 2v4m0 6v4a2 2 0 01-2 2h-4" />
            </svg>
          </button>
        </div>
      </div>

      <div className="max-w-lg mx-auto px-4 pt-6 space-y-5">
        {/* Part Header */}
        <div className="bg-gradient-to-br from-indigo-600 to-indigo-700 rounded-2xl p-6 text-center shadow-lg">
          <div className="text-indigo-200 text-sm font-medium uppercase tracking-wide mb-1">
            {part.sku || part.part_number || (t('partDetail.part') || 'Part')}
          </div>
          <div className="text-white text-2xl sm:text-3xl font-black tracking-tight leading-tight">
            {part.name}
          </div>
          {part.category && (
            <div className="mt-2 inline-flex items-center bg-indigo-500/30 rounded-full px-3 py-1">
              <span className="text-indigo-100 text-sm font-medium">
                {part.category}
              </span>
            </div>
          )}
        </div>

        {/* Photo Gallery */}
        {photos.length > 0 && (
          <div className="bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden">
            <div
              ref={galleryRef}
              className="relative w-full aspect-square bg-gray-100 overflow-hidden"
            >
              <img
                src={photos[activePhoto]}
                alt={`${part.name} - ${activePhoto + 1}`}
                className="w-full h-full object-contain"
              />
              {photos.length > 1 && (
                <div className="absolute bottom-3 left-0 right-0 flex justify-center gap-1.5">
                  {photos.map((_, idx) => (
                    <button
                      key={idx}
                      onClick={() => setActivePhoto(idx)}
                      className={`w-2.5 h-2.5 rounded-full transition-colors ${
                        idx === activePhoto ? 'bg-indigo-600' : 'bg-gray-300'
                      }`}
                      aria-label={`Photo ${idx + 1}`}
                    />
                  ))}
                </div>
              )}
            </div>
            {/* Thumbnail strip for multiple photos */}
            {photos.length > 1 && (
              <div className="flex gap-2 p-3 overflow-x-auto">
                {photos.map((url, idx) => (
                  <button
                    key={idx}
                    onClick={() => setActivePhoto(idx)}
                    className={`flex-shrink-0 w-16 h-16 rounded-lg overflow-hidden border-2 transition-colors ${
                      idx === activePhoto ? 'border-indigo-600' : 'border-transparent'
                    }`}
                  >
                    <img
                      src={url}
                      alt={`Thumbnail ${idx + 1}`}
                      className="w-full h-full object-cover"
                    />
                  </button>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Part Details Card */}
        <div className="bg-white rounded-xl border border-gray-200 p-5 shadow-sm space-y-4">
          <h2 className="text-lg font-semibold text-gray-900">
            {t('partDetail.details') || 'Details'}
          </h2>

          <div className="space-y-3">
            {part.sku && (
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-500 font-medium">
                  {t('partDetail.sku') || 'SKU'}
                </span>
                <span className="text-sm text-gray-900 font-mono">
                  {part.sku}
                </span>
              </div>
            )}
            {part.part_number && (
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-500 font-medium">
                  {t('partDetail.partNumber') || 'Part Number'}
                </span>
                <span className="text-sm text-gray-900 font-mono">
                  {part.part_number}
                </span>
              </div>
            )}
            {part.category && (
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-500 font-medium">
                  {t('partDetail.category') || 'Category'}
                </span>
                <span className="text-sm text-gray-900">
                  {part.category}
                </span>
              </div>
            )}
            {part.manufacturer && (
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-500 font-medium">
                  {t('partDetail.manufacturer') || 'Manufacturer'}
                </span>
                <span className="text-sm text-gray-900">
                  {part.manufacturer}
                </span>
              </div>
            )}
          </div>

          {part.description && (
            <div className="pt-3 border-t border-gray-100">
              <span className="text-sm text-gray-500 font-medium block mb-1">
                {t('partDetail.description') || 'Description'}
              </span>
              <p className="text-sm text-gray-700 leading-relaxed">
                {part.description}
              </p>
            </div>
          )}
        </div>

        {/* Stock Indicator */}
        <div className="bg-white rounded-xl border border-gray-200 p-5 shadow-sm">
          <h2 className="text-lg font-semibold text-gray-900 mb-3">
            {t('partDetail.stockInfo') || 'Stock'}
          </h2>
          <div className="flex items-center gap-3">
            <div className={`w-3 h-3 rounded-full ${
              part.total_quantity > 0 ? 'bg-green-500' : 'bg-red-500'
            }`}></div>
            <span className={`text-sm font-medium ${
              part.total_quantity > 0 ? 'text-green-700' : 'text-red-700'
            }`}>
              {part.total_quantity > 0
                ? (t('partDetail.inStock') || 'In Stock')
                : (t('partDetail.outOfStock') || 'Out of Stock')}
            </span>
            {part.total_quantity != null && part.total_quantity > 0 && (
              <span className="text-sm text-gray-500">
                ({Number(part.total_quantity)} {t('partDetail.units') || 'units'})
              </span>
            )}
          </div>
        </div>
      </div>

      {/* Fixed bottom action bar */}
      <div className="fixed bottom-0 left-0 right-0 bg-white border-t border-gray-200 px-4 pt-4 shadow-lg fixed-bottom-bar" style={{ paddingBottom: 'max(1rem, env(safe-area-inset-bottom))' }}>
        <div className="max-w-lg mx-auto">
          <button
            onClick={() => navigate('/scan')}
            className="w-full bg-blue-600 text-white px-6 py-4 rounded-xl text-lg font-semibold hover:bg-blue-700 active:bg-blue-800 transition-colors flex items-center justify-center gap-2 touch-action-manipulation"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 9V5a2 2 0 012-2h4M3 15v4a2 2 0 002 2h4m8-18h4a2 2 0 012 2v4m0 6v4a2 2 0 01-2 2h-4" />
            </svg>
            {t('partDetail.scanAnother') || 'Scan Another'}
          </button>
        </div>
      </div>
    </div>
  );
};

export default PartDetail;
