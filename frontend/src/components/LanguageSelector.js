// frontend/src/components/LanguageSelector.js

import React, { useState } from 'react';
import { useLocalization } from '../contexts/LocalizationContext';

/**
 * LanguageSelector component for user profile settings
 * Allows users to select their preferred language and country/region
 */
const LanguageSelector = ({
  className = '',
  showCountrySelector = true,
  showAdvancedOptions = false,
  disabled = false
}) => {
  const {
    currentLanguage,
    currentCountry,
    userPreferences,
    supportedLanguages,
    supportedCountries,
    updateLanguage,
    updateCountry,
    setUserPreferences
  } = useLocalization();

  const [showAdvanced, setShowAdvanced] = useState(showAdvancedOptions);

  // Handle language change
  const handleLanguageChange = (languageCode) => {
    updateLanguage(languageCode);
  };

  // Handle country change
  const handleCountryChange = (countryCode) => {
    updateCountry(countryCode);
  };

  // Handle advanced preference changes
  const handleAdvancedChange = (key, value) => {
    setUserPreferences(prev => ({
      ...prev,
      [key]: value
    }));
  };

  return (
    <div className={`language-selector ${className}`}>
      <div className="space-y-6">
        {/* Language Selection */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-3">
            Preferred Language
          </label>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {Object.values(supportedLanguages).map((language) => (
              <label
                key={language.code}
                className={`
                  relative flex items-center p-4 border rounded-lg cursor-pointer transition-colors
                  ${currentLanguage === language.code
                    ? 'border-blue-500 bg-blue-50'
                    : 'border-gray-300 hover:border-gray-400'
                  }
                  ${disabled ? 'opacity-50 cursor-not-allowed' : ''}
                `}
              >
                <input
                  type="radio"
                  name="language"
                  value={language.code}
                  checked={currentLanguage === language.code}
                  onChange={(e) => handleLanguageChange(e.target.value)}
                  disabled={disabled}
                  className="sr-only"
                />

                <div className="flex items-center flex-1">
                  <span className="text-2xl mr-3">{language.flag}</span>
                  <div className="flex-1">
                    <div className="font-medium text-gray-900">
                      {language.name}
                    </div>
                    <div
                      className="text-sm text-gray-500"
                      dir={language.rtl ? 'rtl' : 'ltr'}
                    >
                      {language.nativeName}
                    </div>
                  </div>

                  {language.rtl && (
                    <div className="ml-2 text-xs bg-orange-100 text-orange-800 px-2 py-1 rounded">
                      RTL
                    </div>
                  )}
                </div>

                {currentLanguage === language.code && (
                  <div className="absolute top-2 right-2">
                    <div className="w-4 h-4 bg-blue-500 rounded-full flex items-center justify-center">
                      <div className="w-2 h-2 bg-white rounded-full"></div>
                    </div>
                  </div>
                )}
              </label>
            ))}
          </div>
        </div>

        {/* Country/Region Selection */}
        {showCountrySelector && (
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-3">
              Country/Region
            </label>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
              {Object.values(supportedCountries).map((country) => (
                <label
                  key={country.code}
                  className={`
                    relative flex items-center p-3 border rounded-lg cursor-pointer transition-colors
                    ${currentCountry === country.code
                      ? 'border-blue-500 bg-blue-50'
                      : 'border-gray-300 hover:border-gray-400'
                    }
                    ${disabled ? 'opacity-50 cursor-not-allowed' : ''}
                  `}
                >
                  <input
                    type="radio"
                    name="country"
                    value={country.code}
                    checked={currentCountry === country.code}
                    onChange={(e) => handleCountryChange(e.target.value)}
                    disabled={disabled}
                    className="sr-only"
                  />

                  <div className="flex items-center flex-1">
                    <span className="text-2xl mr-3">{country.flag}</span>
                    <div className="flex-1">
                      <div className="font-medium text-gray-900 text-sm">
                        {country.name}
                      </div>
                      <div className="text-xs text-gray-500">
                        {country.currency} • {country.language.toUpperCase()}
                      </div>
                    </div>
                  </div>

                  {currentCountry === country.code && (
                    <div className="absolute top-1 right-1">
                      <div className="w-3 h-3 bg-blue-500 rounded-full flex items-center justify-center">
                        <div className="w-1.5 h-1.5 bg-white rounded-full"></div>
                      </div>
                    </div>
                  )}
                </label>
              ))}
            </div>
          </div>
        )}

        {/* Advanced Options Toggle */}
        <div>
          <button
            type="button"
            onClick={() => setShowAdvanced(!showAdvanced)}
            className="flex items-center text-sm text-blue-600 hover:text-blue-800"
            disabled={disabled}
          >
            <span className={`transform transition-transform ${showAdvanced ? 'rotate-90' : ''}`}>
              ▶
            </span>
            <span className="ml-2">Advanced Formatting Options</span>
          </button>
        </div>

        {/* Advanced Options */}
        {showAdvanced && (
          <div className="bg-gray-50 p-4 rounded-lg space-y-4">
            <h4 className="font-medium text-gray-900">Formatting Preferences</h4>

            {/* Date Format */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Date Format
              </label>
              <select
                value={userPreferences.dateFormat}
                onChange={(e) => handleAdvancedChange('dateFormat', e.target.value)}
                disabled={disabled}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500 text-sm"
              >
                <option value="auto">Auto (based on country)</option>
                <option value="dd/MM/yyyy">DD/MM/YYYY</option>
                <option value="MM/dd/yyyy">MM/DD/YYYY</option>
                <option value="yyyy-MM-dd">YYYY-MM-DD</option>
              </select>
            </div>

            {/* Number Format */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Number Format
              </label>
              <select
                value={userPreferences.numberFormat}
                onChange={(e) => handleAdvancedChange('numberFormat', e.target.value)}
                disabled={disabled}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500 text-sm"
              >
                <option value="auto">Auto (based on country)</option>
                <option value="en-US">1,234.56 (US)</option>
                <option value="en-GB">1,234.56 (UK)</option>
                <option value="de-DE">1.234,56 (German)</option>
                <option value="fr-FR">1 234,56 (French)</option>
                <option value="ar-SA">١٬٢٣٤٫٥٦ (Arabic)</option>
              </select>
            </div>

            {/* Currency */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Currency Display
              </label>
              <select
                value={userPreferences.currency}
                onChange={(e) => handleAdvancedChange('currency', e.target.value)}
                disabled={disabled}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500 text-sm"
              >
                <option value="auto">Auto (based on country)</option>
                <option value="EUR">EUR (€)</option>
                <option value="USD">USD ($)</option>
                <option value="SAR">SAR (ر.س)</option>
                <option value="OMR">OMR (ر.ع.)</option>
              </select>
            </div>

            {/* Preview */}
            <div className="mt-4 p-3 bg-white border rounded-md">
              <div className="text-sm font-medium text-gray-700 mb-2">Preview:</div>
              <div className="space-y-1 text-sm text-gray-600">
                <div>Date: {new Date().toLocaleDateString()}</div>
                <div>Number: {(1234.56).toLocaleString()}</div>
                <div>Currency: {(1234.56).toLocaleString(undefined, { style: 'currency', currency: 'EUR' })}</div>
              </div>
            </div>
          </div>
        )}

        {/* Current Settings Summary */}
        <div className="bg-blue-50 p-4 rounded-lg">
          <h4 className="font-medium text-blue-900 mb-2">Current Settings</h4>
          <div className="space-y-1 text-sm text-blue-800">
            <div>
              <span className="font-medium">Language:</span> {supportedLanguages[currentLanguage]?.name} ({supportedLanguages[currentLanguage]?.nativeName})
            </div>
            <div>
              <span className="font-medium">Country:</span> {supportedCountries[currentCountry]?.flag} {supportedCountries[currentCountry]?.name}
            </div>
            <div>
              <span className="font-medium">Text Direction:</span> {supportedLanguages[currentLanguage]?.rtl ? 'Right-to-Left (RTL)' : 'Left-to-Right (LTR)'}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LanguageSelector;