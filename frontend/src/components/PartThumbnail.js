// frontend/src/components/PartThumbnail.js
//
// Small part photo that enlarges on tap. Images come from the authenticated
// /images/parts/{id} endpoint, so they are fetched with the session token and
// shown as object URLs; thumbnails load only once scrolled into view.

import React, { useCallback, useEffect, useRef, useState } from 'react';
import { API_BASE_URL } from '../services/api';

// "partId:index" -> Promise<object URL>; shared so filtering/re-rendering never refetches.
const imageCache = new Map();

const loadPartImage = (partId, index) => {
  const key = `${partId}:${index}`;
  if (!imageCache.has(key)) {
    const token = localStorage.getItem('authToken');
    const promise = fetch(`${API_BASE_URL}/images/parts/${partId}?index=${index}`, {
      headers: token ? { Authorization: `Bearer ${token}` } : {},
    })
      .then((res) => {
        if (!res.ok) throw new Error(`Image request failed with status ${res.status}`);
        return res.blob();
      })
      .then((blob) => URL.createObjectURL(blob));
    promise.catch(() => imageCache.delete(key)); // let a later render retry
    imageCache.set(key, promise);
  }
  return imageCache.get(key);
};

const usePartImage = (partId, index, enabled) => {
  const [state, setState] = useState({ url: null, failed: false });
  useEffect(() => {
    if (!enabled) return undefined;
    let cancelled = false;
    setState({ url: null, failed: false });
    loadPartImage(partId, index).then(
      (url) => { if (!cancelled) setState({ url, failed: false }); },
      () => { if (!cancelled) setState({ url: null, failed: true }); }
    );
    return () => { cancelled = true; };
  }, [partId, index, enabled]);
  return state;
};

const PartImageViewer = ({ partId, imageCount, title, subtitle, onClose }) => {
  const [index, setIndex] = useState(0);
  const { url, failed } = usePartImage(partId, index, true);
  const many = imageCount > 1;
  const step = useCallback((d) => setIndex((i) => (i + d + imageCount) % imageCount), [imageCount]);

  useEffect(() => {
    const onKey = (e) => {
      if (e.key === 'Escape') onClose();
      else if (many && e.key === 'ArrowRight') step(1);
      else if (many && e.key === 'ArrowLeft') step(-1);
    };
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, [many, step, onClose]);

  return (
    <div className="fixed inset-0 z-[70] flex flex-col bg-black/90" onClick={onClose}>
      <div className="flex shrink-0 items-start justify-between gap-2 p-3 text-white">
        <div className="min-w-0">
          <div className="font-semibold break-words">{title}</div>
          {subtitle && <div className="text-sm text-gray-300 break-words">{subtitle}</div>}
        </div>
        <button
          type="button"
          onClick={onClose}
          className="h-10 w-10 shrink-0 rounded-full bg-white/15 text-xl active:bg-white/30"
          aria-label="Close"
        >✕</button>
      </div>

      <div className="relative flex min-h-0 flex-1 items-center justify-center px-2">
        {url ? (
          <img
            src={url}
            alt={title}
            className="max-h-full max-w-full rounded object-contain"
            onClick={(e) => e.stopPropagation()}
          />
        ) : (
          <div className="text-sm text-gray-300">{failed ? 'Image unavailable' : 'Loading…'}</div>
        )}
        {many && (
          <>
            <button
              type="button"
              onClick={(e) => { e.stopPropagation(); step(-1); }}
              className="absolute left-2 h-12 w-12 rounded-full bg-white/15 text-2xl text-white active:bg-white/30"
              aria-label="Previous image"
            >‹</button>
            <button
              type="button"
              onClick={(e) => { e.stopPropagation(); step(1); }}
              className="absolute right-2 h-12 w-12 rounded-full bg-white/15 text-2xl text-white active:bg-white/30"
              aria-label="Next image"
            >›</button>
          </>
        )}
      </div>

      {many && (
        <div className="shrink-0 p-3 text-center text-sm text-gray-300">{index + 1} / {imageCount}</div>
      )}
    </div>
  );
};

const PartThumbnail = ({ partId, imageCount = 0, title, subtitle, size = 'h-14 w-14' }) => {
  const ref = useRef(null);
  const [visible, setVisible] = useState(false);
  const [open, setOpen] = useState(false);
  const hasImage = imageCount > 0;
  const { url, failed } = usePartImage(partId, 0, hasImage && visible);

  useEffect(() => {
    if (!hasImage || visible || !ref.current) return undefined;
    if (typeof IntersectionObserver === 'undefined') { setVisible(true); return undefined; }
    const observer = new IntersectionObserver(
      ([entry]) => { if (entry.isIntersecting) { setVisible(true); observer.disconnect(); } },
      { rootMargin: '200px' }
    );
    observer.observe(ref.current);
    return () => observer.disconnect();
  }, [hasImage, visible]);

  if (!hasImage) {
    return (
      <div
        className={`${size} flex shrink-0 items-center justify-center rounded-md border border-dashed border-gray-300 bg-gray-50 text-[10px] text-gray-400`}
        title="No photo"
      >No photo</div>
    );
  }

  return (
    <>
      <button
        ref={ref}
        type="button"
        onClick={() => setOpen(true)}
        className={`${size} relative shrink-0 overflow-hidden rounded-md border border-gray-200 bg-gray-100 active:opacity-80`}
        aria-label={`Show photo of ${title}`}
      >
        {url && <img src={url} alt="" className="h-full w-full object-cover" />}
        {!url && (
          <span className="absolute inset-0 flex items-center justify-center text-[10px] text-gray-400">
            {failed ? 'No photo' : '…'}
          </span>
        )}
        {imageCount > 1 && (
          <span className="absolute bottom-0 right-0 rounded-tl bg-black/60 px-1 text-[10px] font-medium text-white">{imageCount}</span>
        )}
      </button>
      {open && (
        <PartImageViewer
          partId={partId}
          imageCount={imageCount}
          title={title}
          subtitle={subtitle}
          onClose={() => setOpen(false)}
        />
      )}
    </>
  );
};

export default PartThumbnail;
