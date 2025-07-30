// frontend/src/utils/countryFlags.js

/**
 * Country flag emojis and display information for supported countries
 */
export const COUNTRY_FLAGS = {
  GR: {
    flag: '🇬🇷',
    name: 'Greece',
    code: 'GR'
  },
  KSA: {
    flag: '🇸🇦',
    name: 'Saudi Arabia',
    code: 'KSA'
  },
  ES: {
    flag: '🇪🇸',
    name: 'Spain',
    code: 'ES'
  },
  CY: {
    flag: '🇨🇾',
    name: 'Cyprus',
    code: 'CY'
  },
  OM: {
    flag: '🇴🇲',
    name: 'Oman',
    code: 'OM'
  }
};

/**
 * Get country flag emoji by country code
 * @param {string} countryCode - Country code (GR, KSA, ES, CY, OM)
 * @returns {string} Flag emoji or empty string if not found
 */
export const getCountryFlag = (countryCode) => {
  return COUNTRY_FLAGS[countryCode]?.flag || '';
};

/**
 * Get country name by country code
 * @param {string} countryCode - Country code (GR, KSA, ES, CY, OM)
 * @returns {string} Country name or country code if not found
 */
export const getCountryName = (countryCode) => {
  return COUNTRY_FLAGS[countryCode]?.name || countryCode;
};

/**
 * Get formatted country display (flag + name)
 * @param {string} countryCode - Country code (GR, KSA, ES, CY, OM)
 * @returns {string} Formatted display string
 */
export const getCountryDisplay = (countryCode) => {
  const country = COUNTRY_FLAGS[countryCode];
  if (!country) return countryCode;
  return `${country.flag} ${country.name}`;
};

/**
 * Get all supported countries as array
 * @returns {Array} Array of country objects
 */
export const getSupportedCountries = () => {
  return Object.values(COUNTRY_FLAGS);
};