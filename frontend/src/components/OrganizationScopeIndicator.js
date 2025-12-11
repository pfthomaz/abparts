// frontend/src/components/OrganizationScopeIndicator.js

import React, { useState } from 'react';
import { useAuth } from '../AuthContext';
import { getAccessScope, isSuperAdmin } from '../utils/permissions';
import { useTranslation } from '../hooks/useTranslation';

/**
 * OrganizationScopeIndicator component shows the current data access scope
 * and allows super admins to switch between organizations
 */
const OrganizationScopeIndicator = ({
  showOrganizationSelector = false,
  onOrganizationChange,
  availableOrganizations = [],
  currentOrganizationId,
  className = ''
}) => {
  const { user } = useAuth();
  const { t } = useTranslation();
  const [isExpanded, setIsExpanded] = useState(false);
  const accessScope = getAccessScope(user);

  if (!user) return null;

  const handleOrganizationChange = (orgId) => {
    if (onOrganizationChange) {
      onOrganizationChange(orgId);
    }
    setIsExpanded(false);
  };

  const getCurrentOrganization = () => {
    if (currentOrganizationId) {
      return availableOrganizations.find(org => org.id === currentOrganizationId);
    }
    return user.organization;
  };

  const currentOrg = getCurrentOrganization();

  return (
    <div className={`bg-white border border-gray-200 rounded-lg p-3 sm:p-4 ${className}`}>
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between space-y-3 sm:space-y-0">
        <div className="flex items-center space-x-3 min-w-0 flex-1">
          {/* Access Scope Icon */}
          <div className={`w-8 h-8 flex-shrink-0 rounded-full flex items-center justify-center ${accessScope.canAccessAllOrganizations
            ? 'bg-purple-100 text-purple-600'
            : 'bg-blue-100 text-blue-600'
            }`}>
            {accessScope.canAccessAllOrganizations ? (
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3.055 11H5a2 2 0 012 2v1a2 2 0 002 2 2 2 0 012 2v2.945M8 3.935V5.5A2.5 2.5 0 0010.5 8h.5a2 2 0 012 2 2 2 0 104 0 2 2 0 012-2h1.064M15 20.488V18a2 2 0 012-2h3.064M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            ) : (
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-4m-5 0H9m0 0H5m0 0h2M7 7h10M7 11h4m6 0h2M7 15h10" />
              </svg>
            )}
          </div>

          {/* Organization Info */}
          <div className="min-w-0 flex-1">
            <div className="flex flex-col sm:flex-row sm:items-center sm:space-x-2 space-y-1 sm:space-y-0">
              <h3 className="text-sm font-medium text-gray-900 truncate">
                {accessScope.canAccessAllOrganizations ? t('organizationScope.globalAccess') : t('organizationScope.organizationAccess')}
              </h3>
              <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium self-start ${accessScope.canAccessAllOrganizations
                ? 'bg-purple-100 text-purple-800'
                : 'bg-blue-100 text-blue-800'
                }`}>
                {t(`organizationScope.accessLevels.${accessScope.accessLevel}`)}
              </span>
            </div>
            <p className="text-xs sm:text-sm text-gray-500 truncate">
              {accessScope.canAccessAllOrganizations
                ? `${t('organizationScope.viewing')}: ${currentOrg?.name || t('organizationScope.allOrganizations')}`
                : `${t('organizationScope.limitedTo')}: ${currentOrg?.name || t('organizationScope.yourOrganization')}`
              }
            </p>
          </div>
        </div>

        {/* Organization Selector for Super Admins */}
        {showOrganizationSelector && isSuperAdmin(user) && availableOrganizations.length > 0 && (
          <div className="relative flex-shrink-0">
            <button
              onClick={() => setIsExpanded(!isExpanded)}
              className="flex items-center space-x-2 px-3 py-2 border border-gray-300 rounded-md text-xs sm:text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            >
              <span className="hidden sm:inline">{t('organizationScope.switchOrganization')}</span>
              <span className="sm:hidden">{t('organizationScope.switch')}</span>
              <svg className={`w-4 h-4 transform transition-transform ${isExpanded ? 'rotate-180' : ''}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
              </svg>
            </button>

            {isExpanded && (
              <div className="absolute right-0 mt-2 w-64 bg-white rounded-md shadow-lg z-50 border border-gray-200">
                <div className="py-1">
                  <button
                    onClick={() => handleOrganizationChange(null)}
                    className={`w-full text-left px-4 py-2 text-sm hover:bg-gray-100 ${!currentOrganizationId ? 'bg-blue-50 text-blue-700' : 'text-gray-700'
                      }`}
                  >
                    <div className="flex items-center space-x-2">
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3.055 11H5a2 2 0 012 2v1a2 2 0 002 2 2 2 0 012 2v2.945M8 3.935V5.5A2.5 2.5 0 0010.5 8h.5a2 2 0 012 2 2 2 0 104 0 2 2 0 012-2h1.064M15 20.488V18a2 2 0 012-2h3.064M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                      <span>{t('organizationScope.allOrganizations')}</span>
                    </div>
                  </button>
                  {availableOrganizations.map((org) => (
                    <button
                      key={org.id}
                      onClick={() => handleOrganizationChange(org.id)}
                      className={`w-full text-left px-4 py-2 text-sm hover:bg-gray-100 ${currentOrganizationId === org.id ? 'bg-blue-50 text-blue-700' : 'text-gray-700'
                        }`}
                    >
                      <div className="flex items-center space-x-2">
                        <div className={`w-3 h-3 rounded-full ${org.organization_type === 'oraseas_ee' ? 'bg-blue-500' :
                          org.organization_type === 'bossaqua' ? 'bg-green-500' :
                            org.organization_type === 'customer' ? 'bg-purple-500' :
                              'bg-orange-500'
                          }`}></div>
                        <span className="truncate">{org.name}</span>
                        <span className="text-xs text-gray-500 flex-shrink-0">
                          ({org.organization_type})
                        </span>
                      </div>
                    </button>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Data Scope Details - Hidden on mobile to save space */}
      <div className="hidden md:block mt-4 pt-4 border-t border-gray-200">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
          <div>
            <span className="text-gray-500">{t('organizationScope.dataAccess')}:</span>
            <div className="font-medium text-gray-900">
              {accessScope.restrictions.dataFiltering === 'none' ? t('organizationScope.unrestricted') : t('organizationScope.organizationScoped')}
            </div>
          </div>
          <div>
            <span className="text-gray-500">{t('organizationScope.userManagement')}:</span>
            <div className="font-medium text-gray-900">
              {accessScope.restrictions.userManagement === 'all-organizations' ? t('organizationScope.allOrganizations') : t('organizationScope.ownOrganization')}
            </div>
          </div>
          <div>
            <span className="text-gray-500">{t('organizationScope.reporting')}:</span>
            <div className="font-medium text-gray-900">
              {accessScope.restrictions.reporting === 'global' ? t('organizationScope.globalReports') : t('organizationScope.organizationReports')}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default OrganizationScopeIndicator;