// frontend/src/utils/organizationTypeConfig.js

import { OrganizationType } from '../services/organizationsService';

/**
 * Get translated organization type configuration
 * @param {Function} t - Translation function from useTranslation hook
 * @returns {Object} Organization type configuration with translated labels and descriptions
 */
export const getOrganizationTypeConfig = (t) => {
  return {
    [OrganizationType.ORASEAS_EE]: {
      label: t('organizationTypes.oraseaseLabel'),
      description: t('organizationTypes.oraseaseDesc'),
      color: 'bg-blue-100 text-blue-800',
      icon: '🏢',
      singleton: true
    },
    [OrganizationType.BOSSAQUA]: {
      label: t('organizationTypes.bossaquaLabel'),
      description: t('organizationTypes.bossaquaDesc'),
      color: 'bg-green-100 text-green-800',
      icon: '🏭',
      singleton: true
    },
    [OrganizationType.CUSTOMER]: {
      label: t('organizationTypes.customerLabel'),
      description: t('organizationTypes.customerDesc'),
      color: 'bg-purple-100 text-purple-800',
      icon: '🏪',
      singleton: false
    },
    [OrganizationType.SUPPLIER]: {
      label: t('organizationTypes.supplierLabel'),
      description: t('organizationTypes.supplierDesc'),
      color: 'bg-orange-100 text-orange-800',
      icon: '📦',
      singleton: false
    }
  };
};
