// frontend/src/components/DataScopeIndicator.js

import React from 'react';
import { useAuth } from '../AuthContext';
import { useOrganization } from '../contexts/OrganizationContext';
import { isSuperAdmin } from '../utils/permissions';

/**
 * DataScopeIndicator component to show users what data scope they're viewing
 */
const DataScopeIndicator = ({ showOnAllPages = false, className = '' }) => {
  const { user } = useAuth();
  const { selectedOrganization, isSuperAdminMode } = useOrganization();

  // Don't show for regular users unless explicitly requested
  if (!showOnAllPages && !isSuperAdmin(user)) {
    return null;
  }

  const getDataScopeInfo = () => {
    if (isSuperAdmin(user)) {
      if (selectedOrganization) {
        return {
          scope: 'Organization-Specific',
          description: `Viewing data for ${selectedOrganization.name}`,
          icon: '🔍',
          bgColor: 'bg-blue-50',
          textColor: 'text-blue-800',
          borderColor: 'border-blue-200'
        };
      } else {
        return {
          scope: 'Global View',
          description: 'Viewing data across all organizations',
          icon: '🌐',
          bgColor: 'bg-purple-50',
          textColor: 'text-purple-800',
          borderColor: 'border-purple-200'
        };
      }
    } else {
      return {
        scope: 'Organization Data',
        description: `Viewing data for ${user.organization?.name || 'your organization'}`,
        icon: '🏢',
        bgColor: 'bg-gray-50',
        textColor: 'text-gray-800',
        borderColor: 'border-gray-200'
      };
    }
  };

  const scopeInfo = getDataScopeInfo();

  return (
    <div className={`flex items-center space-x-2 px-3 py-2 rounded-md border ${scopeInfo.bgColor} ${scopeInfo.textColor} ${scopeInfo.borderColor} ${className}`}>
      <span className="text-sm">{scopeInfo.icon}</span>
      <div className="text-sm">
        <span className="font-medium">{scopeInfo.scope}:</span>
        <span className="ml-1">{scopeInfo.description}</span>
      </div>
      {isSuperAdmin(user) && (
        <div className="text-xs bg-white bg-opacity-50 px-2 py-0.5 rounded">
          Super Admin
        </div>
      )}
    </div>
  );
};

export default DataScopeIndicator;