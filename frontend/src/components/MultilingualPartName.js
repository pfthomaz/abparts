// frontend/src/components/MultilingualPartName.js

import React, { useState, useEffect } from 'react';
import { useLocalization } from '../contexts/LocalizationContext';

/**
 * MultilingualPartName component for handling compound multilingual strings
 * Supports display and editing of part names in multiple languages
 * Format: "English Name | Greek Name | Arabic Name" or similar compound strings
 */
const MultilingualPartName = ({
  value = '',
  onChange,
  isEditing = false,
  preferredLanguage = null, // Will use context if not provided
  supportedLanguages = null, // Will use context if not provided
  className = '',
  placeholder = 'Enter part name...',
  required = false,
  disabled = false
}) => {
  const {
    currentLanguage,
    supportedLanguages: contextSupportedLanguages,
    parseMultilingualString,
    isRTL,
    getDirectionClass
  } = useLocalization();

  const [parsedNames, setParsedNames] = useState({});
  const [displayName, setDisplayName] = useState('');

  // Use context values or fallback to props
  const effectivePreferredLanguage = preferredLanguage || currentLanguage;
  const effectiveSupportedLanguages = supportedLanguages || Object.keys(contextSupportedLanguages);

  // Language labels for UI
  const languageLabels = {
    en: 'English',
    el: 'Greek (Ελληνικά)',
    ar: 'Arabic (العربية)',
    es: 'Spanish (Español)',
    cy: 'Greek (Cyprus)',
    om: 'Arabic (Oman)',
    ksa: 'Arabic (Saudi Arabia)'
  };

  // Parse compound string into individual language components
  useEffect(() => {
    if (!value) {
      setParsedNames({});
      setDisplayName('');
      return;
    }

    // Use the localization context to parse the multilingual string
    const displayValue = parseMultilingualString(value, effectivePreferredLanguage);
    setDisplayName(displayValue);

    // Also parse for editing mode
    if (value.includes('|')) {
      const parts = value.split('|').map(part => part.trim());
      const parsed = {};

      effectiveSupportedLanguages.forEach((lang, index) => {
        if (parts[index]) {
          parsed[lang] = parts[index];
        }
      });

      setParsedNames(parsed);
    } else {
      // Single language value
      setParsedNames({ [effectivePreferredLanguage]: value });
    }
  }, [value, effectivePreferredLanguage, parseMultilingualString]);

  // Handle changes in editing mode
  const handleLanguageChange = (language, newValue) => {
    const updatedNames = { ...parsedNames, [language]: newValue };

    // Remove empty values
    Object.keys(updatedNames).forEach(key => {
      if (!updatedNames[key] || updatedNames[key].trim() === '') {
        delete updatedNames[key];
      }
    });

    setParsedNames(updatedNames);

    // Construct compound string
    const compoundString = effectiveSupportedLanguages
      .map(lang => updatedNames[lang] || '')
      .filter(name => name.trim() !== '')
      .join(' | ');

    if (onChange) {
      onChange(compoundString);
    }
  };

  // Display mode - show the name in preferred language with language indicator
  if (!isEditing) {
    const hasMultipleLanguages = Object.keys(parsedNames).length > 1;

    return (
      <div className={`multilingual-part-name ${className}`}>
        <span className="part-name-display">
          {displayName || value || 'No name provided'}
        </span>
        {hasMultipleLanguages && (
          <span className={`language-indicator text-xs text-gray-500 bg-gray-100 px-2 py-1 rounded ${getDirectionClass('ml-2')}`}>
            {languageLabels[effectivePreferredLanguage] || effectivePreferredLanguage.toUpperCase()}
            <span className={getDirectionClass('ml-1 text-gray-400')}>
              (+{Object.keys(parsedNames).length - 1} more)
            </span>
          </span>
        )}

        {/* Tooltip showing all languages on hover */}
        {hasMultipleLanguages && (
          <div className="hidden group-hover:block absolute z-10 bg-white border border-gray-300 rounded-md shadow-lg p-3 mt-1">
            <div className="text-sm font-medium text-gray-700 mb-2">All Languages:</div>
            {Object.entries(parsedNames).map(([lang, name]) => (
              <div key={lang} className="text-sm text-gray-600 mb-1">
                <span className="font-medium">{languageLabels[lang] || lang.toUpperCase()}:</span> {name}
              </div>
            ))}
          </div>
        )}
      </div>
    );
  }

  // Editing mode - show input fields for each supported language
  return (
    <div className={`multilingual-part-name-editor ${className}`}>
      <div className="space-y-3">
        {effectiveSupportedLanguages.map((language) => (
          <div key={language} className="language-input-group">
            <label
              htmlFor={`name-${language}`}
              className="block text-sm font-medium text-gray-700 mb-1"
            >
              {languageLabels[language] || language.toUpperCase()}
              {language === effectiveSupportedLanguages[0] && required && (
                <span className="text-red-500 ml-1">*</span>
              )}
            </label>
            <input
              type="text"
              id={`name-${language}`}
              value={parsedNames[language] || ''}
              onChange={(e) => handleLanguageChange(language, e.target.value)}
              placeholder={`${placeholder} (${languageLabels[language] || language})`}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500 text-sm"
              required={language === effectiveSupportedLanguages[0] && required}
              disabled={disabled}
              dir={contextSupportedLanguages[language]?.rtl ? 'rtl' : 'ltr'}
            />
          </div>
        ))}
      </div>

      {/* Preview of compound string */}
      <div className="mt-3 p-2 bg-gray-50 rounded-md">
        <div className="text-xs font-medium text-gray-600 mb-1">Preview:</div>
        <div className="text-sm text-gray-800">
          {effectiveSupportedLanguages
            .map(lang => parsedNames[lang] || '')
            .filter(name => name.trim() !== '')
            .join(' | ') || 'No names entered'}
        </div>
      </div>
    </div>
  );
};

export default MultilingualPartName;