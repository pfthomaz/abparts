// frontend/src/hooks/useTranslation.js

import { useState, useEffect, useCallback } from 'react';
import { useLocalization } from '../contexts/LocalizationContext';

// Import translation files
import enTranslations from '../locales/en.json';
import elTranslations from '../locales/el.json';
import arTranslations from '../locales/ar.json';
import esTranslations from '../locales/es.json';
import trTranslations from '../locales/tr.json';
import noTranslations from '../locales/no.json';

const translations = {
  en: enTranslations,
  el: elTranslations,
  ar: arTranslations,
  es: esTranslations,
  tr: trTranslations,
  no: noTranslations
};

/**
 * Custom hook for translations
 * @returns {Object} Translation utilities
 */
export const useTranslation = () => {
  const { currentLanguage } = useLocalization();
  const [currentTranslations, setCurrentTranslations] = useState(translations[currentLanguage] || translations.en);

  // Update translations when language changes
  useEffect(() => {
    setCurrentTranslations(translations[currentLanguage] || translations.en);
  }, [currentLanguage]);

  /**
   * Get translation for a key
   * @param {string} key - Translation key in dot notation (e.g., 'common.save')
   * @param {Object} params - Parameters to replace in translation (e.g., {min: 5})
   * @returns {string} Translated text
   */
  const t = useCallback((key, params = {}) => {
    if (!key) return '';

    // Split the key by dots to navigate nested objects
    const keys = key.split('.');
    let value = currentTranslations;

    // Navigate through the nested structure
    for (const k of keys) {
      if (value && typeof value === 'object' && k in value) {
        value = value[k];
      } else {
        // Key not found, return the key itself as fallback
        console.warn(`Translation key not found: ${key} (failed at: ${k})`);
        return key;
      }
    }

    // If value is not a string, return the key
    if (typeof value !== 'string') {
      console.warn(`Translation value is not a string: ${key}, got:`, typeof value, value);
      return key;
    }

    // Replace parameters in the translation
    let translatedText = value;
    Object.keys(params).forEach(param => {
      const regex = new RegExp(`{{${param}}}`, 'g');
      translatedText = translatedText.replace(regex, params[param]);
    });

    return translatedText;
  }, [currentTranslations, currentLanguage]);

  /**
   * Check if a translation key exists
   * @param {string} key - Translation key
   * @returns {boolean} True if key exists
   */
  const hasTranslation = useCallback((key) => {
    if (!key) return false;

    const keys = key.split('.');
    let value = currentTranslations;

    for (const k of keys) {
      if (value && typeof value === 'object' && k in value) {
        value = value[k];
      } else {
        return false;
      }
    }

    return typeof value === 'string';
  }, [currentTranslations]);

  /**
   * Get all translations for a namespace
   * @param {string} namespace - Namespace (e.g., 'common', 'users')
   * @returns {Object} All translations in that namespace
   */
  const getNamespace = useCallback((namespace) => {
    return currentTranslations[namespace] || {};
  }, [currentTranslations]);

  return {
    t,
    hasTranslation,
    getNamespace,
    currentLanguage,
    availableLanguages: Object.keys(translations)
  };
};

export default useTranslation;
