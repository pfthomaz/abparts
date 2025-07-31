// frontend/src/components/LocalizedText.js

import React from 'react';
import { useLocalization } from '../contexts/LocalizationContext';

/**
 * LocalizedText component for displaying multilingual content with fallback logic
 * Handles compound multilingual strings and provides consistent formatting
 */
const LocalizedText = ({
  text,
  fallbackLanguage = null,
  className = '',
  showLanguageIndicator = false,
  showAllLanguages = false,
  maxLength = null,
  truncate = false,
  as = 'span',
  ...props
}) => {
  const {
    parseMultilingualString,
    currentLanguage,
    supportedLanguages,
    isRTL,
    getTextDirection
  } = useLocalization();

  if (!text) {
    return null;
  }

  // Parse the multilingual string
  const displayText = parseMultilingualString(text, fallbackLanguage);

  // Handle truncation
  const finalText = truncate && maxLength && displayText.length > maxLength
    ? `${displayText.substring(0, maxLength)}...`
    : displayText;

  // Parse all languages if needed
  const allLanguages = text.includes('|')
    ? text.split('|').map((part, index) => ({
      text: part.trim(),
      language: ['en', 'el', 'ar', 'es'][index] || 'unknown'
    })).filter(item => item.text)
    : [{ text: displayText, language: currentLanguage }];

  // Determine text direction for the current content
  const textDirection = getTextDirection();
  const isCurrentRTL = isRTL();

  // Create the component
  const Component = as;

  // Show all languages mode
  if (showAllLanguages && allLanguages.length > 1) {
    return (
      <div className={`localized-text-all ${className}`} {...props}>
        {allLanguages.map((item, index) => {
          const langConfig = supportedLanguages[item.language];
          const isLangRTL = langConfig?.rtl || false;

          return (
            <div
              key={index}
              className={`mb-2 ${index === allLanguages.length - 1 ? 'mb-0' : ''}`}
              dir={isLangRTL ? 'rtl' : 'ltr'}
            >
              <Component
                className={`block ${isLangRTL ? 'text-right' : 'text-left'}`}
              >
                {item.text}
              </Component>
              {showLanguageIndicator && (
                <span className="text-xs text-gray-500 ml-2">
                  ({langConfig?.name || item.language})
                </span>
              )}
            </div>
          );
        })}
      </div>
    );
  }

  // Single language display mode
  return (
    <Component
      className={`localized-text ${className}`}
      dir={textDirection}
      {...props}
    >
      {finalText}
      {showLanguageIndicator && allLanguages.length > 1 && (
        <span className={`language-indicator text-xs text-gray-500 ${isCurrentRTL ? 'mr-2' : 'ml-2'}`}>
          ({supportedLanguages[currentLanguage]?.name || currentLanguage})
          {allLanguages.length > 1 && (
            <span className="text-gray-400">
              {` (+${allLanguages.length - 1} more)`}
            </span>
          )}
        </span>
      )}
    </Component>
  );
};

/**
 * LocalizedDate component for displaying dates with proper localization
 */
export const LocalizedDate = ({
  date,
  options = {},
  className = '',
  showTime = false,
  relative = false,
  ...props
}) => {
  const { formatDate, currentLanguage } = useLocalization();

  if (!date) {
    return <span className={className} {...props}>—</span>;
  }

  const dateObj = typeof date === 'string' ? new Date(date) : date;

  // Show relative time (e.g., "2 hours ago")
  if (relative) {
    const now = new Date();
    const diffMs = now - dateObj;
    const diffMinutes = Math.floor(diffMs / (1000 * 60));
    const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
    const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));

    let relativeText;
    if (diffMinutes < 1) {
      relativeText = 'Just now';
    } else if (diffMinutes < 60) {
      relativeText = `${diffMinutes} minute${diffMinutes !== 1 ? 's' : ''} ago`;
    } else if (diffHours < 24) {
      relativeText = `${diffHours} hour${diffHours !== 1 ? 's' : ''} ago`;
    } else if (diffDays < 7) {
      relativeText = `${diffDays} day${diffDays !== 1 ? 's' : ''} ago`;
    } else {
      relativeText = formatDate(dateObj, options);
    }

    return (
      <span className={className} title={formatDate(dateObj, { ...options, weekday: 'long' })} {...props}>
        {relativeText}
      </span>
    );
  }

  // Default date formatting
  const defaultOptions = showTime
    ? { hour: '2-digit', minute: '2-digit', ...options }
    : options;

  return (
    <span className={className} {...props}>
      {formatDate(dateObj, defaultOptions)}
    </span>
  );
};

/**
 * LocalizedNumber component for displaying numbers with proper localization
 */
export const LocalizedNumber = ({
  value,
  options = {},
  className = '',
  currency = false,
  percentage = false,
  ...props
}) => {
  const { formatNumber, formatCurrency } = useLocalization();

  if (value === null || value === undefined || isNaN(value)) {
    return <span className={className} {...props}>—</span>;
  }

  let formattedValue;
  if (currency) {
    formattedValue = formatCurrency(value, options);
  } else if (percentage) {
    formattedValue = formatNumber(value, { style: 'percent', ...options });
  } else {
    formattedValue = formatNumber(value, options);
  }

  return (
    <span className={className} {...props}>
      {formattedValue}
    </span>
  );
};

/**
 * RTLWrapper component for handling RTL content within LTR layouts
 */
export const RTLWrapper = ({ children, force = false, className = '' }) => {
  const { isRTL } = useLocalization();

  const shouldApplyRTL = force || isRTL();

  return (
    <div
      className={`${shouldApplyRTL ? 'rtl' : 'ltr'} ${className}`}
      dir={shouldApplyRTL ? 'rtl' : 'ltr'}
    >
      {children}
    </div>
  );
};

export default LocalizedText;