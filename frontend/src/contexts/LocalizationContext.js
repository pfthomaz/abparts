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
  },
  TR: {
    code: 'TR',
    name: 'Turkey',
    language: 'tr',
    currency: 'TRY',
    dateFormat: 'dd.MM.yyyy',
    numberFormat: 'tr-TR',
    rtl: false,
    flag: '🇹🇷'
  },
  NO: {
    code: 'NO',
    name: 'Norway',
    language: 'no',
    currency: 'NOK',
    dateFormat: 'dd.MM.yyyy',
    numberFormat: 'no-NO',
    rtl: false,
    flag: '🇳🇴'
  },
  HR: {
    code: 'HR',
    name: 'Croatia',
    language: 'en',
    currency: 'EUR',
    dateFormat: 'dd.MM.yyyy',
    numberFormat: 'hr-HR',
    rtl: false,
    flag: '🇭🇷'
  },
  IT: {
    code: 'IT',
    name: 'Italy',
    language: 'en',
    currency: 'EUR',
    dateFormat: 'dd/MM/yyyy',
    numberFormat: 'it-IT',
    rtl: false,
    flag: '🇮🇹'
  }
};

// Supported languages
const SUPPORTED_LANGUAGES = {
  en: {
    code: 'en',
    name: 'English',
    nativeName: 'English',
    rtl: false,
    flag: '🇺🇸'
  },
  el: {
    code: 'el',
    name: 'Greek',
    nativeName: 'Ελληνικά',
    rtl: false,
    flag: '🇬🇷'
  },
  ar: {
    code: 'ar',
    name: 'Arabic',
    nativeName: 'العربية',
    rtl: true,
    flag: '🇸🇦'
  },
  es: {
    code: 'es',
    name: 'Spanish',
    nativeName: 'Español',
    rtl: false,
    flag: '🇪🇸'
  },
  tr: {
    code: 'tr',
    name: 'Turkish',
    nativeName: 'Türkçe',
    rtl: false,
    flag: '🇹🇷'
  },
  no: {
    code: 'no',
    name: 'Norwegian',
    nativeName: 'Norsk',
    rtl: false,
    flag: '🇳🇴'
  }
};

// Default language fallback order
const LANGUAGE_FALLBACK_ORDER = ['en', 'el', 'ar', 'es', 'tr', 'no'];

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
    // PRIORITY 1: Check if user has preferred_language from backend
    if (user?.preferred_language) {
      if (SUPPORTED_LANGUAGES[user.preferred_language]) {
        setCurrentLanguage(user.preferred_language);
        setUserPreferences(prev => ({
          ...prev,
          language: user.preferred_language
        }));
        return; // Exit early - user preference takes priority
      }
    }

    // PRIORITY 2: Try to get saved preferences from localStorage
    const savedPreferences = localStorage.getItem('localizationPreferences');
    if (savedPreferences) {
      try {
        const parsed = JSON.parse(savedPreferences);
        setUserPreferences(parsed);
        setCurrentLanguage(parsed.language || 'en');
        setCurrentCountry(parsed.country || 'GR');
        return;
      } catch (error) {
        console.error('Error parsing saved localization preferences:', error);
      }
    }

    // PRIORITY 3: If user is logged in and has organization country, use that as default
    if (user?.organization?.country) {
      const orgCountry = user.organization.country;
      if (SUPPORTED_COUNTRIES[orgCountry]) {
        setCurrentCountry(orgCountry);
        const countryConfig = SUPPORTED_COUNTRIES[orgCountry];
        setCurrentLanguage(countryConfig.language);
        setUserPreferences(prev => ({
          ...prev,
          country: orgCountry,
          language: countryConfig.language
        }));
      }
    }
  }, [user]);

  // Save preferences to localStorage whenever they change
  useEffect(() => {
    localStorage.setItem('localizationPreferences', JSON.stringify(userPreferences));
  }, [userPreferences]);

  // Update language preference
  const updateLanguage = async (languageCode) => {
    if (SUPPORTED_LANGUAGES[languageCode]) {
      setCurrentLanguage(languageCode);
      setUserPreferences(prev => ({
        ...prev,
        language: languageCode
      }));

      // Dispatch custom event for components that need to know about language changes
      window.dispatchEvent(new CustomEvent('languageChanged', { 
        detail: { language: languageCode } 
      }));

      // Save to backend if user is logged in
      if (user?.id) {
        try {
          const token = localStorage.getItem('authToken');
          const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000';
          const response = await fetch(`${API_BASE_URL}/users/${user.id}`, {
            method: 'PUT',
            headers: {
              'Content-Type': 'application/json',
              'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({
              preferred_language: languageCode
            })
          });

          if (!response.ok) {
            console.error('Failed to save language preference to backend');
          }
        } catch (error) {
          console.error('Error saving language preference:', error);
        }
      }
    }
  };

  // Update country preference
  const updateCountry = async (countryCode) => {
    if (SUPPORTED_COUNTRIES[countryCode]) {
      setCurrentCountry(countryCode);
      setUserPreferences(prev => ({
        ...prev,
        country: countryCode
      }));

      // Save to backend if user is logged in
      if (user?.id) {
        try {
          const token = localStorage.getItem('authToken');
          const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000';
          const response = await fetch(`${API_BASE_URL}/users/${user.id}`, {
            method: 'PUT',
            headers: {
              'Content-Type': 'application/json',
              'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({
              preferred_country: countryCode
            })
          });

          if (!response.ok) {
            console.error('Failed to save country preference to backend');
          }
        } catch (error) {
          console.error('Error saving country preference:', error);
        }
      }
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