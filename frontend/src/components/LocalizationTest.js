// frontend/src/components/LocalizationTest.js

import React from 'react';
import { useLocalization } from '../contexts/LocalizationContext';
import LocalizedText, { LocalizedDate, LocalizedNumber } from './LocalizedText';
import MultilingualPartName from './MultilingualPartName';

/**
 * Test component to demonstrate localization features
 * This can be temporarily added to any page to test the functionality
 */
const LocalizationTest = () => {
  const {
    currentLanguage,
    currentCountry,
    supportedLanguages,
    supportedCountries,
    formatDate,
    formatNumber,
    formatCurrency,
    parseMultilingualString,
    isRTL,
    updateLanguage,
    updateCountry
  } = useLocalization();

  // Test data
  const testMultilingualString = "Engine Filter | Φίλτρο Κινητήρα | مرشح المحرك | Filtro de Motor";
  const testDate = new Date();
  const testNumber = 1234.56;
  const testCurrency = 999.99;

  return (
    <div className="bg-white p-6 rounded-lg shadow-lg max-w-4xl mx-auto">
      <h2 className="text-2xl font-bold mb-6 text-gray-800">Localization Test Component</h2>

      {/* Current Settings */}
      <div className="mb-6 p-4 bg-blue-50 rounded-lg">
        <h3 className="text-lg font-semibold mb-3 text-blue-900">Current Settings</h3>
        <div className="grid grid-cols-2 gap-4 text-sm">
          <div>
            <span className="font-medium">Language:</span> {currentLanguage} ({supportedLanguages[currentLanguage]?.name})
          </div>
          <div>
            <span className="font-medium">Country:</span> {currentCountry} ({supportedCountries[currentCountry]?.name})
          </div>
          <div>
            <span className="font-medium">RTL Mode:</span> {isRTL() ? 'Yes' : 'No'}
          </div>
          <div>
            <span className="font-medium">Currency:</span> {supportedCountries[currentCountry]?.currency}
          </div>
        </div>
      </div>

      {/* Language Switcher */}
      <div className="mb-6 p-4 bg-gray-50 rounded-lg">
        <h3 className="text-lg font-semibold mb-3 text-gray-800">Quick Language Switch</h3>
        <div className="flex flex-wrap gap-2">
          {Object.values(supportedLanguages).map((lang) => (
            <button
              key={lang.code}
              onClick={() => updateLanguage(lang.code)}
              className={`px-3 py-2 rounded-md text-sm font-medium transition-colors ${currentLanguage === lang.code
                  ? 'bg-blue-600 text-white'
                  : 'bg-white text-gray-700 border border-gray-300 hover:bg-gray-50'
                }`}
            >
              {lang.nativeName}
            </button>
          ))}
        </div>
      </div>

      {/* Country Switcher */}
      <div className="mb-6 p-4 bg-gray-50 rounded-lg">
        <h3 className="text-lg font-semibold mb-3 text-gray-800">Quick Country Switch</h3>
        <div className="flex flex-wrap gap-2">
          {Object.values(supportedCountries).map((country) => (
            <button
              key={country.code}
              onClick={() => updateCountry(country.code)}
              className={`px-3 py-2 rounded-md text-sm font-medium transition-colors ${currentCountry === country.code
                  ? 'bg-green-600 text-white'
                  : 'bg-white text-gray-700 border border-gray-300 hover:bg-gray-50'
                }`}
            >
              {country.flag} {country.name}
            </button>
          ))}
        </div>
      </div>

      {/* Multilingual Text Test */}
      <div className="mb-6 p-4 bg-yellow-50 rounded-lg">
        <h3 className="text-lg font-semibold mb-3 text-yellow-900">Multilingual Text Test</h3>
        <div className="space-y-3">
          <div>
            <span className="font-medium">Original String:</span>
            <div className="text-sm text-gray-600 mt-1">{testMultilingualString}</div>
          </div>
          <div>
            <span className="font-medium">Parsed for Current Language:</span>
            <div className="text-lg mt-1">
              <LocalizedText text={testMultilingualString} showLanguageIndicator={true} />
            </div>
          </div>
          <div>
            <span className="font-medium">All Languages:</span>
            <div className="mt-1">
              <LocalizedText text={testMultilingualString} showAllLanguages={true} />
            </div>
          </div>
        </div>
      </div>

      {/* MultilingualPartName Component Test */}
      <div className="mb-6 p-4 bg-purple-50 rounded-lg">
        <h3 className="text-lg font-semibold mb-3 text-purple-900">MultilingualPartName Component</h3>
        <div className="space-y-4">
          <div>
            <span className="font-medium">Display Mode:</span>
            <div className="mt-2">
              <MultilingualPartName
                value={testMultilingualString}
                isEditing={false}
                className="text-lg"
              />
            </div>
          </div>
          <div>
            <span className="font-medium">Edit Mode:</span>
            <div className="mt-2">
              <MultilingualPartName
                value={testMultilingualString}
                isEditing={true}
                onChange={(value) => console.log('Changed to:', value)}
                className="text-sm"
              />
            </div>
          </div>
        </div>
      </div>

      {/* Date Formatting Test */}
      <div className="mb-6 p-4 bg-green-50 rounded-lg">
        <h3 className="text-lg font-semibold mb-3 text-green-900">Date Formatting Test</h3>
        <div className="grid grid-cols-2 gap-4 text-sm">
          <div>
            <span className="font-medium">Context formatDate:</span>
            <div>{formatDate(testDate)}</div>
          </div>
          <div>
            <span className="font-medium">LocalizedDate Component:</span>
            <div><LocalizedDate date={testDate} /></div>
          </div>
          <div>
            <span className="font-medium">With Time:</span>
            <div><LocalizedDate date={testDate} showTime={true} /></div>
          </div>
          <div>
            <span className="font-medium">Relative:</span>
            <div><LocalizedDate date={new Date(Date.now() - 2 * 60 * 60 * 1000)} relative={true} /></div>
          </div>
        </div>
      </div>

      {/* Number Formatting Test */}
      <div className="mb-6 p-4 bg-red-50 rounded-lg">
        <h3 className="text-lg font-semibold mb-3 text-red-900">Number Formatting Test</h3>
        <div className="grid grid-cols-2 gap-4 text-sm">
          <div>
            <span className="font-medium">Context formatNumber:</span>
            <div>{formatNumber(testNumber)}</div>
          </div>
          <div>
            <span className="font-medium">LocalizedNumber Component:</span>
            <div><LocalizedNumber value={testNumber} /></div>
          </div>
          <div>
            <span className="font-medium">Currency:</span>
            <div><LocalizedNumber value={testCurrency} currency={true} /></div>
          </div>
          <div>
            <span className="font-medium">Percentage:</span>
            <div><LocalizedNumber value={0.1234} percentage={true} /></div>
          </div>
        </div>
      </div>

      {/* RTL Test */}
      <div className="mb-6 p-4 bg-indigo-50 rounded-lg">
        <h3 className="text-lg font-semibold mb-3 text-indigo-900">RTL Layout Test</h3>
        <div className="space-y-3">
          <div>
            <span className="font-medium">Current Direction:</span> {isRTL() ? 'Right-to-Left' : 'Left-to-Right'}
          </div>
          <div className="p-3 bg-white rounded border">
            <div className="text-sm text-gray-600 mb-2">Sample text with direction-aware styling:</div>
            <div className={`text-lg ${isRTL() ? 'text-right' : 'text-left'}`}>
              This text should align according to the current language direction.
            </div>
          </div>
          {isRTL() && (
            <div className="p-3 bg-white rounded border" dir="rtl">
              <div className="text-sm text-gray-600 mb-2">Arabic text sample:</div>
              <div className="text-lg text-right">
                هذا نص تجريبي باللغة العربية لاختبار الاتجاه من اليمين إلى اليسار
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Raw Data Display */}
      <div className="p-4 bg-gray-100 rounded-lg">
        <h3 className="text-lg font-semibold mb-3 text-gray-800">Raw Context Data</h3>
        <pre className="text-xs text-gray-600 overflow-auto">
          {JSON.stringify({
            currentLanguage,
            currentCountry,
            isRTL: isRTL(),
            testParsed: parseMultilingualString(testMultilingualString),
            formattedDate: formatDate(testDate),
            formattedNumber: formatNumber(testNumber),
            formattedCurrency: formatCurrency(testCurrency)
          }, null, 2)}
        </pre>
      </div>
    </div>
  );
};

export default LocalizationTest;