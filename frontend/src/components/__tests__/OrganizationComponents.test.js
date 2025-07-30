// frontend/src/components/__tests__/OrganizationComponents.test.js

import { getCountryFlag, getCountryDisplay, getSupportedCountries } from '../../utils/countryFlags';

describe('Organization Components', () => {
  describe('Country Flags Utility', () => {
    test('should return correct flag for country code', () => {
      expect(getCountryFlag('GR')).toBe('🇬🇷');
      expect(getCountryFlag('KSA')).toBe('🇸🇦');
      expect(getCountryFlag('ES')).toBe('🇪🇸');
      expect(getCountryFlag('CY')).toBe('🇨🇾');
      expect(getCountryFlag('OM')).toBe('🇴🇲');
    });

    test('should return empty string for unknown country code', () => {
      expect(getCountryFlag('XX')).toBe('');
    });

    test('should return correct display format', () => {
      expect(getCountryDisplay('GR')).toBe('🇬🇷 Greece');
      expect(getCountryDisplay('KSA')).toBe('🇸🇦 Saudi Arabia');
    });

    test('should return all supported countries', () => {
      const countries = getSupportedCountries();
      expect(countries).toHaveLength(5);
      expect(countries.map(c => c.code)).toEqual(['GR', 'KSA', 'ES', 'CY', 'OM']);
    });
  });

  describe('Component Imports', () => {
    test('should be able to import all new components', () => {
      // Test that components can be imported without errors
      expect(() => {
        require('../OrganizationHierarchy');
        require('../SupplierManager');
        require('../OrganizationWarehouseWorkflow');
      }).not.toThrow();
    });
  });
});