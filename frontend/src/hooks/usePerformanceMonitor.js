import { useEffect, useRef, useState } from 'react';

/**
 * Hook for monitoring component render performance
 * Useful for optimizing large dataset rendering
 */
export const usePerformanceMonitor = (componentName = 'Component') => {
  const renderStartTime = useRef(performance.now());
  const [renderTime, setRenderTime] = useState(0);
  const renderCount = useRef(0);

  useEffect(() => {
    const endTime = performance.now();
    const duration = endTime - renderStartTime.current;
    setRenderTime(duration);
    renderCount.current += 1;

    if (process.env.NODE_ENV === 'development' && duration > 16) {
      console.warn(`${componentName} render took ${duration.toFixed(2)}ms (>16ms threshold)`);
    }

    // Reset for next render
    renderStartTime.current = performance.now();
  }, [componentName]);

  return {
    renderTime: renderTime.toFixed(2),
    renderCount: renderCount.current
  };
};

/**
 * Hook for throttling expensive operations
 * Useful for search filtering with large datasets
 */
export const useThrottle = (callback, delay) => {
  const lastRun = useRef(Date.now());

  return (...args) => {
    if (Date.now() - lastRun.current >= delay) {
      callback(...args);
      lastRun.current = Date.now();
    }
  };
};

/**
 * Hook for measuring component mount/unmount performance
 */
export const useMountPerformance = (componentName = 'Component') => {
  const mountTime = useRef(performance.now());

  useEffect(() => {
    const mountDuration = performance.now() - mountTime.current;
    const currentMountTime = mountTime.current;

    if (process.env.NODE_ENV === 'development') {
      console.log(`${componentName} mounted in ${mountDuration.toFixed(2)}ms`);
    }

    return () => {
      const unmountTime = performance.now();
      if (process.env.NODE_ENV === 'development') {
        console.log(`${componentName} unmounted after ${(unmountTime - currentMountTime).toFixed(2)}ms`);
      }
    };
  }, [componentName]);
};