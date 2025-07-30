// frontend/src/components/MultilingualPartName.js

import React, { useState, useEffect } from 'react';

/**
 * MultilingualPartName component for handling compound multilingual strings
 * Supports display and editing of part names in multiple languages
 * Format: "English Name | Greek Name | Arabic Name" or similar compound strings
 */
const MultilingualPartName = ({
  value = '',
  onChange,
  isEditing = false,
  preferredLanguage = 'en',
  supportedLanguages = ['en', 'el', 'ar', 'es'],
  className = '',
  placeholder = 'Enter part name...',
  required = false,
  disabled = false
}) => {
  const [parsedNames, setParsedNames] = useState({});
  const [displayName, setDisplayName] = useState('');

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

    // Handle compound string format: "English | Greek | Arabic"
    const parts = value.split('|').map(part => part.trim());
    const parsed = {};

    // Map parts to supported languages in order
    const langs = supportedLanguages || ['en', 'el', 'ar', 'es'];
    langs.forEach((lang, index) => {
      if (parts[index]) {
        parsed[lang] = parts[index];
      }
    });

    setParsedNames(parsed);

    // Set display name based on preferred language with fallback
    const displayValue = parsed[preferredLanguage] ||
      parsed[langs[0]] ||
      parts[0] ||
      value;
    setDisplayName(displayValue);
  }, [value, preferredLanguage]);

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
    const langs = supportedLanguages || ['en', 'el', 'ar', 'es'];
    const compoundString = langs
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
          <span className="language-indicator ml-2 text-xs text-gray-500 bg-gray-100 px-2 py-1 rounded">
            {languageLabels[preferredLanguage] || preferredLanguage.toUpperCase()}
            <span className="ml-1 text-gray-400">
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
        {(supportedLanguages || ['en', 'el', 'ar', 'es']).map((language) => (
          <div key={language} className="language-input-group">
            <label
              htmlFor={`name-${language}`}
              className="block text-sm font-medium text-gray-700 mb-1"
            >
              {languageLabels[language] || language.toUpperCase()}
              {language === (supportedLanguages || ['en', 'el', 'ar', 'es'])[0] && required && (
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
              required={language === (supportedLanguages || ['en', 'el', 'ar', 'es'])[0] && required}
              disabled={disabled}
              dir={language === 'ar' ? 'rtl' : 'ltr'}
            />
          </div>
        ))}
      </div>

      {/* Preview of compound string */}
      <div className="mt-3 p-2 bg-gray-50 rounded-md">
        <div className="text-xs font-medium text-gray-600 mb-1">Preview:</div>
        <div className="text-sm text-gray-800">
          {(supportedLanguages || ['en', 'el', 'ar', 'es'])
            .map(lang => parsedNames[lang] || '')
            .filter(name => name.trim() !== '')
            .join(' | ') || 'No names entered'}
        </div>
      </div>
    </div>
  );
};

export default MultilingualPartName;