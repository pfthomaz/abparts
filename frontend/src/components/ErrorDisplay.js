// frontend/src/components/ErrorDisplay.js

import React from 'react';
import PropTypes from 'prop-types';
import { ERROR_TYPES } from '../utils/errorUtils';

/**
 * A reusable component for displaying errors with retry functionality
 */
const ErrorDisplay = ({
  message,
  type = ERROR_TYPES.UNKNOWN,
  onRetry,
  retryCount = 0,
  className = ''
}) => {
  // Determine background color based on error type
  const getBgColor = () => {
    switch (type) {
      case ERROR_TYPES.NETWORK:
        return 'bg-orange-100 border-orange-400 text-orange-700';
      case ERROR_TYPES.AUTH:
        return 'bg-blue-100 border-blue-400 text-blue-700';
      case ERROR_TYPES.PERMISSION:
        return 'bg-yellow-100 border-yellow-400 text-yellow-700';
      case ERROR_TYPES.VALIDATION:
        return 'bg-purple-100 border-purple-400 text-purple-700';
      case ERROR_TYPES.TIMEOUT:
        return 'bg-orange-100 border-orange-400 text-orange-700';
      default:
        return 'bg-red-100 border-red-400 text-red-700';
    }
  };

  // Get guidance message based on retry count and error type
  const getGuidanceMessage = () => {
    if (retryCount > 2) {
      switch (type) {
        case ERROR_TYPES.NETWORK:
          return 'Check your internet connection or try again later.';
        case ERROR_TYPES.AUTH:
          return 'Try logging out and logging back in.';
        case ERROR_TYPES.SERVER:
          return 'Our servers may be experiencing issues. Please try again later.';
        default:
          return 'If this issue persists, please contact support.';
      }
    }
    return null;
  };

  const guidance = getGuidanceMessage();
  const bgColorClass = getBgColor();

  return (
    <div className={`${bgColorClass} border px-4 py-3 rounded relative mb-4 ${className}`} role="alert">
      <div className="flex items-center justify-between">
        <div>
          <strong className="font-bold">Error: </strong>
          <span className="block sm:inline">{message}</span>
          {guidance && (
            <p className="text-sm mt-2 font-medium">
              {guidance}
            </p>
          )}
        </div>
        {onRetry && (
          <button
            onClick={onRetry}
            className="bg-gray-600 text-white px-3 py-1 rounded text-sm hover:bg-gray-700 ml-4"
            aria-label="Retry"
          >
            Retry
          </button>
        )}
      </div>
    </div>
  );
};

ErrorDisplay.propTypes = {
  message: PropTypes.string.isRequired,
  type: PropTypes.oneOf(Object.values(ERROR_TYPES)),
  onRetry: PropTypes.func,
  retryCount: PropTypes.number,
  className: PropTypes.string
};

export default ErrorDisplay;