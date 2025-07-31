// frontend/src/contexts/LocalizationContext.js

import React, { createContext, useContext, useState, useEffect } from 'react';
import { useAuth } from '../AuthContext';

// Supported countries and their configurations
const SUPPORTED_COUNTRIES = {
  GR: {
    code: 'GR',
    name: 'Greece',
    language: 'el',
    currency: 'EUR',
    dateFormat: 'dd/MM/yyyy',
    numberFormat: 'el-GR',
    rtl: false,
    flag: '🇬🇷'
  },
  KSA: {
    code: 'KSA',
    name: 'Saudi Arabia',
    language: 'ar',
    currency: 'SAR',
    dateFormat: 'dd/MM/yyyy',
    numberFormat: 'ar-SA',
    rtl: true,
    flag: '🇸🇦'
  },
  ES: {
    code: 'ES',
    name: 'Spain',
    language: 'es',
    currency: 'EUR',
    dateFormat: 'dd/MM/yyyy',
    numberFormat: 'es-ES',
    rtl: false,
    flag: '🇪🇸'
  },
  CY: {
    code: 'CY',
    name: 'Cyprus',
    language: 'el',
    currency: 'EUR',
    dateFormat: 'dd/MM/yyyy',
    numberFormat: 'el-CY',
    rtl: false,
    flag: '🇨🇾'
  },
  OM: {
    code: 'OM',
    name: 'Oman',
    language: 'ar',
    currency: 'OMR',
    dateFormat: 'dd/MM/yyyy',
    numberFormat: 'ar-OM',
    rtl: true,
    flag: '🇴🇲'
  }
};

// Supported languages
const SUPPORTED_LANGUAGES = {
  en: {
    code: 'en',
    name: 'English',
    nativeName: 'English',
    rtl: false
  },
  el: {
    code: 'el',
    name: 'Greek',
    nativeName: 'Ελληνικά',
    rtl: false
  },
  ar: {
    code: 'ar',
    name: 'Arabic',
    nativeName: 'العربية',
    rtl: true
  },
  es: {
    code: 'es',
    name: 'Spanish',
    nativeName: 'Español',
    rtl: false
  }
};

// Default language fallback order
const LANGUAGE_FALLBACK_ORDER = ['en', 'el', 'ar', 'es'];

const LocalizationContext = createContext(null);

export const LocalizationProvider = ({ children }) => {
  const { user } = useAuth();
  const [currentLanguage, setCurrentLanguage] = useState('en');
  const [currentCountry, setCurrentCountry] = useState('GR');
  const [userPreferences, setUserPreferences] = useState({
    language: 'en',
    country: 'GR',
    dateFormat: 'auto',
    numberFormat: 'auto',
    currency: 'auto'
  });

  // Initialize localization settings
  useEffect(() => {
    // Try to get saved preferences from localStorage
    const savedPreferences = localStorage.getItem('localizationPreferences');
    if (savedPreferences) {
      try {
        const parsed = JSON.parse(savedPreferences);
        setUserPreferences(parsed);
        setCurrentLanguage(parsed.language || 'en');
        setCurrentCountry(parsed.country || 'GR');
      } catch (error) {
        console.error('Error parsing saved localization preferences:', error);
      }
    }

    // If user is logged in and has organization country, use that as default
    if (user?.organization?.country) {
      const orgCountry = user.organization.country;
      if (SUPPORTED_COUNTRIES[orgCountry]) {
        setCurrentCountry(orgCountry);
        // Update language based on country if not explicitly set
        if (!savedPreferences) {
          const countryConfig = SUPPORTED_COUNTRIES[orgCountry];
          setCurrentLanguage(countryConfig.language);
          setUserPreferences(prev => ({
            ...prev,
            country: orgCountry,
            language: countryConfig.language
          }));
        }
      }
    }
  }, [user]);

  // Save preferences to localStorage whenever they change
  useEffect(() => {
    localStorage.setItem('localizationPreferences', JSON.stringify(userPreferences));
  }, [userPreferences]);

  // Update language preference
  const updateLanguage = (languageCode) => {
    if (SUPPORTED_LANGUAGES[languageCode]) {
      setCurrentLanguage(languageCode);
      setUserPreferences(prev => ({
        ...prev,
        language: languageCode
      }));
    }
  };

  // Update country preference
  const updateCountry = (countryCode) => {
    if (SUPPORTED_COUNTRIES[countryCode]) {
      setCurrentCountry(countryCode);
      setUserPreferences(prev => ({
        ...prev,
        country: countryCode
      }));
    }
  };

  // Get current country configuration
  const getCountryConfig = () => {
    return SUPPORTED_COUNTRIES[currentCountry] || SUPPORTED_COUNTRIES.GR;
  };

  // Get current language configuration
  const getLanguageConfig = () => {
    return SUPPORTED_LANGUAGES[currentLanguage] || SUPPORTED_LANGUAGES.en;
  };

  // Format date according to current locale
  const formatDate = (date, options = {}) => {
    if (!date) return '';

    const dateObj = typeof date === 'string' ? new Date(date) : date;
    const countryConfig = getCountryConfig();

    // Use user's preferred format or country default
    const locale = userPreferences.numberFormat === 'auto'
      ? countryConfig.numberFormat
      : userPreferences.numberFormat;

    const defaultOptions = {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    };

    return dateObj.toLocaleDateString(locale, { ...defaultOptions, ...options });
  };

  // Format number according to current locale
  const formatNumber = (number, options = {}) => {
    if (number === null || number === undefined) return '';

    const countryConfig = getCountryConfig();
    const locale = userPreferences.numberFormat === 'auto'
      ? countryConfig.numberFormat
      : userPreferences.numberFormat;

    return Number(number).toLocaleString(locale, options);
  };

  // Format currency according to current locale
  const formatCurrency = (amount, options = {}) => {
    if (amount === null || amount === undefined) return '';

    const countryConfig = getCountryConfig();
    const currency = userPreferences.currency === 'auto'
      ? countryConfig.currency
      : userPreferences.currency;

    const locale = userPreferences.numberFormat === 'auto'
      ? countryConfig.numberFormat
      : userPreferences.numberFormat;

    return Number(amount).toLocaleString(locale, {
      style: 'currency',
      currency: currency,
      ...options
    });
  };

  // Parse multilingual string and return preferred language version
  const parseMultilingualString = (multilingualString, fallbackLanguage = null) => {
    if (!multilingualString) return '';

    // If it's not a compound string, return as-is
    if (!multilingualString.includes('|')) {
      return multilingualString;
    }

    // Parse compound string: "English | Greek | Arabic"
    const parts = multilingualString.split('|').map(part => part.trim());
    const languages = LANGUAGE_FALLBACK_ORDER;

    // Try to find the preferred language
    const preferredLang = fallbackLanguage || currentLanguage;
    const preferredIndex = languages.indexOf(preferredLang);

    if (preferredIndex !== -1 && parts[preferredIndex]) {
      return parts[preferredIndex];
    }

    // Fallback to first available language
    for (let i = 0; i < languages.length; i++) {
      if (parts[i]) {
        return parts[i];
      }
    }

    // Final fallback to first part
    return parts[0] || multilingualString;
  };

  // Get RTL direction for current language
  const isRTL = () => {
    const languageConfig = getLanguageConfig();
    return languageConfig.rtl;
  };

  // Get text direction class
  const getTextDirection = () => {
    return isRTL() ? 'rtl' : 'ltr';
  };

  // Get direction-aware margin/padding classes
  const getDirectionClass = (baseClass) => {
    if (!isRTL()) return baseClass;

    // Convert left/right classes for RTL
    return baseClass
      .replace(/ml-/g, 'temp-mr-')
      .replace(/mr-/g, 'ml-')
      .replace(/temp-mr-/g, 'mr-')
      .replace(/pl-/g, 'temp-pr-')
      .replace(/pr-/g, 'pl-')
      .replace(/temp-pr-/g, 'pr-')
      .replace(/left-/g, 'temp-right-')
      .replace(/right-/g, 'left-')
      .replace(/temp-right-/g, 'right-');
  };

  const contextValue = {
    // Current settings
    currentLanguage,
    currentCountry,
    userPreferences,

    // Configuration objects
    supportedCountries: SUPPORTED_COUNTRIES,
    supportedLanguages: SUPPORTED_LANGUAGES,

    // Update functions
    updateLanguage,
    updateCountry,
    setUserPreferences,

    // Utility functions
    getCountryConfig,
    getLanguageConfig,
    formatDate,
    formatNumber,
    formatCurrency,
    parseMultilingualString,
    isRTL,
    getTextDirection,
    getDirectionClass
  };

  return (
    <LocalizationContext.Provider value={contextValue}>
      <div dir={getTextDirection()} className={isRTL() ? 'rtl' : 'ltr'}>
        {children}
      </div>
    </LocalizationContext.Provider>
  );
};

// Custom hook to use localization context
export const useLocalization = () => {
  const context = useContext(LocalizationContext);
  if (!context) {
    throw new Error('useLocalization must be used within a LocalizationProvider');
  }
  return context;
};

export default LocalizationContext;