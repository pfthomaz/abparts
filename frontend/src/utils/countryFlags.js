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
  UK: {
    flag: '🇬🇧',
    name: 'United Kingdom',
    code: 'UK'
  },
  NO: {
    flag: '🇳🇴',
    name: 'Norway',
    code: 'NO'
  },
  CA: {
    flag: '🇨🇦',
    name: 'Canada',
    code: 'CA'
  },
  NZ: {
    flag: '🇳🇿',
    name: 'New Zealand',
    code: 'NZ'
  },
  TR: {
    flag: '🇹🇷',
    name: 'Turkey',
    code: 'TR'
  },
  OM: {
    flag: '🇴🇲',
    name: 'Oman',
    code: 'OM'
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
  SA: {
    flag: '🇸🇦',
    name: 'Saudi Arabia',
    code: 'SA'
  }
};

/**
 * Get country flag emoji by country code
 * @param {string} countryCode - Country code (GR, UK, NO, CA, NZ, TR, OM, ES, CY, SA)
 * @returns {string} Flag emoji or empty string if not found
 */
export const getCountryFlag = (countryCode) => {
  return COUNTRY_FLAGS[countryCode]?.flag || '';
};

/**
 * Get country name by country code
 * @param {string} countryCode - Country code (GR, UK, NO, CA, NZ, TR, OM, ES, CY, SA)
 * @returns {string} Country name or country code if not found
 */
export const getCountryName = (countryCode) => {
  return COUNTRY_FLAGS[countryCode]?.name || countryCode;
};

/**
 * Get formatted country display (flag + name)
 * @param {string} countryCode - Country code (GR, UK, NO, CA, NZ, TR, OM, ES, CY, SA)
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