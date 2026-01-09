// Utility to handle image URLs in both development and production

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000';

/**
 * Get the full URL for a static image
 * In development: prepends API_BASE_URL to /static paths
 * In production: uses the path as-is (nginx proxies /static/)
 */
export const getImageUrl = (imagePath) => {
  if (!imagePath) return null;
  
  // If it's already a full URL, return as-is
  if (imagePath.startsWith('http://') || imagePath.startsWith('https://')) {
    return imagePath;
  }
  
  // In development, prepend API_BASE_URL for /static paths
  if (imagePath.startsWith('/static') && process.env.NODE_ENV === 'development') {
    return `${API_BASE_URL}${imagePath}`;
  }
  
  // In production or for non-static paths, return as-is
  return imagePath;
};
