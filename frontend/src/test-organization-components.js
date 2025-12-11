// frontend/src/test-organization-components.js
// Simple test script to verify the new organization components

import React from 'react';
import { createRoot } from 'react-dom/client';
import { BrowserRouter } from 'react-router-dom';
import { AuthProvider } from './AuthContext';

// Import the new components
import OrganizationHierarchy from './components/OrganizationHierarchy';
import SupplierManager from './components/SupplierManager';
import OrganizationWarehouseWorkflow from './components/OrganizationWarehouseWorkflow';
import { getCountryFlag, getCountryDisplay, getSupportedCountries } from './utils/countryFlags';

// Test the country flags utility
console.log('Testing country flags utility:');
console.log('GR flag:', getCountryFlag('GR'));
console.log('KSA display:', getCountryDisplay('KSA'));
console.log('Supported countries:', getSupportedCountries());

// Mock user for testing
const mockUser = {
  id: 'test-user-id',
  username: 'superadmin',
  role: 'super_admin',
  organization_id: 'test-org-id',
  organization: {
    id: 'test-org-id',
    name: 'Test Organization'
  }
};

// Test component rendering
const TestApp = () => {
  return (
    <BrowserRouter>
      <AuthProvider>
        <div className="p-4 space-y-8">
          <h1 className="text-2xl font-bold">Organization Components Test</h1>

          <div className="border p-4 rounded">
            <h2 className="text-lg font-semibold mb-4">Organization Hierarchy</h2>
            <OrganizationHierarchy
              onOrganizationSelect={(org) => console.log('Selected organization:', org)}
            />
          </div>

          <div className="border p-4 rounded">
            <h2 className="text-lg font-semibold mb-4">Supplier Manager</h2>
            <SupplierManager
              organizationId="test-org-id"
              onSupplierChange={() => console.log('Supplier changed')}
            />
          </div>

          <div className="border p-4 rounded">
            <h2 className="text-lg font-semibold mb-4">Warehouse Workflow</h2>
            <OrganizationWarehouseWorkflow
              organizationId="test-org-id"
              onWarehouseCreated={(warehouse) => console.log('Warehouse created:', warehouse)}
            />
          </div>
        </div>
      </AuthProvider>
    </BrowserRouter>
  );
};

// Only run if this file is executed directly (for testing)
if (typeof window !== 'undefined' && window.location.pathname === '/test-components') {
  const container = document.getElementById('root');
  const root = createRoot(container);
  root.render(<TestApp />);
}

export default TestApp;