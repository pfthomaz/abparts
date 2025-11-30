// frontend/src/App.js

import React from 'react';
import {
  BrowserRouter as Router,
  Routes,
  Route,
  Navigate,
} from 'react-router-dom';
import './index.css'; // Import Tailwind CSS base styles
import { useAuth } from './AuthContext'; // Import useAuth hook
import { LocalizationProvider } from './contexts/LocalizationContext'; // Import LocalizationProvider
import LoginForm from './components/LoginForm'; // Import LoginForm component
import Layout from './components/Layout'; // Import Layout component
import ProtectedRoute from './components/ProtectedRoute'; // Import ProtectedRoute component
import PermissionErrorBoundary from './components/PermissionErrorBoundary'; // Import PermissionErrorBoundary
import { PERMISSIONS } from './utils/permissions'; // Import permissions
import Dashboard from './pages/Dashboard';
import Organizations from './pages/Organizations';
import Parts from './pages/Parts';
import Orders from './pages/Orders';
import Stocktake from './pages/Stocktake';
import Machines from './pages/Machines'; // New: Import Machines page
import UsersPage from './pages/UsersPage'; // New: Import UsersPage
import AcceptInvitation from './pages/AcceptInvitation'; // New: Import AcceptInvitation page
import UserProfile from './pages/UserProfile'; // New: Import UserProfile page
import Security from './pages/Security'; // New: Import Security page
import Warehouses from './pages/Warehouses'; // New: Import Warehouses page
import Transactions from './pages/Transactions'; // New: Import Transactions page
import OrganizationManagement from './pages/OrganizationManagement'; // New: Import OrganizationManagement page
import Configuration from './pages/Configuration'; // New: Import Configuration page
import StockAdjustments from './pages/StockAdjustments'; // New: Import StockAdjustments page
import SessionTimeoutWarning from './components/SessionTimeoutWarning'; // New: Import SessionTimeoutWarning component
import MachineHoursReminderModal from './components/MachineHoursReminderModal'; // New: Import MachineHoursReminderModal
import { useState, useEffect } from 'react';
import { api } from './services/api';

function App() {
  const { token, loadingUser, user } = useAuth();
  const [showHoursReminder, setShowHoursReminder] = useState(false);
  const [machinesNeedingUpdate, setMachinesNeedingUpdate] = useState([]);

  // Check for machine hours reminders on login
  useEffect(() => {
    const checkHoursReminders = async () => {
      if (!token || !user) return;
      
      try {
        const response = await api.get('/machines/check-hours-reminders');
        
        if (response.is_reminder_day && response.machines_needing_update.length > 0) {
          setMachinesNeedingUpdate(response.machines_needing_update);
          setShowHoursReminder(true);
        }
      } catch (error) {
        console.error('Failed to check hours reminders:', error);
      }
    };

    // Check reminders when user logs in
    if (token && user) {
      checkHoursReminders();
    }
  }, [token, user]);

  if (loadingUser) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gray-100">
        <p className="text-xl text-gray-700">Checking authentication...</p>
      </div>
    );
  }

  return (
    <LocalizationProvider>
      <Router>
        {/* Global session timeout warning - only shows when user is authenticated */}
        {token && <SessionTimeoutWarning />}
        
        {/* Machine Hours Reminder Modal */}
        {showHoursReminder && (
          <MachineHoursReminderModal
            machines={machinesNeedingUpdate}
            onClose={() => setShowHoursReminder(false)}
            onHoursSaved={() => {
              setShowHoursReminder(false);
              // Optionally refresh data
            }}
          />
        )}

        <Routes>
          <Route
            path="/login"
            element={!token ? <LoginForm /> : <Navigate to="/" />}
          />
          <Route
            path="/accept-invitation"
            element={<AcceptInvitation />}
          />
          <Route
            path="/*"
            element={token ? <Layout /> : <Navigate to="/login" />}
          >
            <Route index element={
              <PermissionErrorBoundary feature="Dashboard">
                <Dashboard />
              </PermissionErrorBoundary>
            } />
            <Route
              path="organizations"
              element={
                <PermissionErrorBoundary
                  feature="Organizations Management"
                  requiredPermission={PERMISSIONS.VIEW_ALL_ORGANIZATIONS}
                  requiredRole="super_admin"
                >
                  <ProtectedRoute
                    permission={PERMISSIONS.VIEW_ALL_ORGANIZATIONS}
                    requiredRole="super_admin"
                    feature="Organizations Management"
                  >
                    <Organizations />
                  </ProtectedRoute>
                </PermissionErrorBoundary>
              }
            />
            <Route
              path="parts"
              element={
                <PermissionErrorBoundary
                  feature="Parts Catalog"
                  requiredPermission={PERMISSIONS.VIEW_PARTS}
                  resource="parts"
                  action="view"
                >
                  <ProtectedRoute
                    permission={PERMISSIONS.VIEW_PARTS}
                    feature="Parts Catalog"
                  >
                    <Parts />
                  </ProtectedRoute>
                </PermissionErrorBoundary>
              }
            />
            {/* Inventory route removed - functionality moved to Warehouses page */}
            <Route
              path="orders"
              element={
                <PermissionErrorBoundary
                  feature="Order Management"
                  requiredPermission={PERMISSIONS.ORDER_PARTS}
                  resource="orders"
                  action="view"
                >
                  <ProtectedRoute
                    permission={PERMISSIONS.ORDER_PARTS}
                    feature="Order Management"
                  >
                    <Orders />
                  </ProtectedRoute>
                </PermissionErrorBoundary>
              }
            />
            <Route
              path="stocktake"
              element={
                <PermissionErrorBoundary
                  feature="Stocktake Management"
                  requiredPermission={PERMISSIONS.ADJUST_INVENTORY}
                  requiredRole="admin"
                  resource="inventory"
                  action="manage"
                >
                  <ProtectedRoute
                    permission={PERMISSIONS.ADJUST_INVENTORY}
                    requiredRole="admin"
                    feature="Stocktake Management"
                  >
                    <Stocktake />
                  </ProtectedRoute>
                </PermissionErrorBoundary>
              }
            />
            <Route
              path="machines"
              element={
                <PermissionErrorBoundary
                  feature="Machine Management"
                  requiredPermission={PERMISSIONS.VIEW_ORG_MACHINES}
                  resource="machines"
                  action="view"
                >
                  <ProtectedRoute
                    permissions={[PERMISSIONS.VIEW_ORG_MACHINES, PERMISSIONS.VIEW_ALL_MACHINES]}
                    feature="Machine Management"
                  >
                    <Machines />
                  </ProtectedRoute>
                </PermissionErrorBoundary>
              }
            />
            <Route
              path="users"
              element={
                <PermissionErrorBoundary
                  feature="User Management"
                  requiredPermission={PERMISSIONS.MANAGE_ORG_USERS}
                  requiredRole="admin"
                  resource="users"
                  action="manage"
                >
                  <ProtectedRoute
                    permissions={[PERMISSIONS.MANAGE_ORG_USERS, PERMISSIONS.MANAGE_ALL_USERS]}
                    requiredRole="admin"
                    feature="User Management"
                  >
                    <UsersPage />
                  </ProtectedRoute>
                </PermissionErrorBoundary>
              }
            />
            <Route path="profile" element={
              <PermissionErrorBoundary feature="User Profile">
                <UserProfile />
              </PermissionErrorBoundary>
            } />
            <Route path="security" element={
              <PermissionErrorBoundary feature="Security Center">
                <Security />
              </PermissionErrorBoundary>
            } />
            <Route
              path="warehouses"
              element={
                <PermissionErrorBoundary
                  feature="Warehouse Management"
                  requiredPermission={PERMISSIONS.VIEW_WAREHOUSES}
                  resource="warehouses"
                  action="view"
                >
                  <ProtectedRoute
                    permission={PERMISSIONS.VIEW_WAREHOUSES}
                    feature="Warehouse Management"
                  >
                    <Warehouses />
                  </ProtectedRoute>
                </PermissionErrorBoundary>
              }
            />
            <Route
              path="stock-adjustments"
              element={
                <PermissionErrorBoundary
                  feature="Stock Adjustments"
                  requiredPermission={PERMISSIONS.ADJUST_INVENTORY}
                  requiredRole="admin"
                  resource="inventory"
                  action="adjust"
                >
                  <ProtectedRoute
                    permission={PERMISSIONS.ADJUST_INVENTORY}
                    requiredRole="admin"
                    feature="Stock Adjustments"
                  >
                    <StockAdjustments />
                  </ProtectedRoute>
                </PermissionErrorBoundary>
              }
            />
            <Route
              path="transactions"
              element={
                <PermissionErrorBoundary
                  feature="Transaction Management"
                  requiredPermission={PERMISSIONS.VIEW_ORG_TRANSACTIONS}
                  resource="transactions"
                  action="view"
                >
                  <ProtectedRoute
                    permission={PERMISSIONS.VIEW_ORG_TRANSACTIONS}
                    feature="Transaction Management"
                  >
                    <Transactions />
                  </ProtectedRoute>
                </PermissionErrorBoundary>
              }
            />
            <Route
              path="organization-management"
              element={
                <PermissionErrorBoundary
                  feature="Organization Management"
                  requiredPermission={PERMISSIONS.VIEW_ALL_ORGANIZATIONS}
                  requiredRole="admin"
                >
                  <ProtectedRoute
                    permissions={[PERMISSIONS.VIEW_ALL_ORGANIZATIONS, PERMISSIONS.MANAGE_ORG_USERS]}
                    requiredRole="admin"
                    feature="Organization Management"
                  >
                    <OrganizationManagement />
                  </ProtectedRoute>
                </PermissionErrorBoundary>
              }
            />
            <Route
              path="configuration"
              element={
                <PermissionErrorBoundary
                  feature="Administrative Configuration"
                  requiredRole="admin"
                >
                  <ProtectedRoute
                    requiredRole="admin"
                    feature="Administrative Configuration"
                  >
                    <Configuration />
                  </ProtectedRoute>
                </PermissionErrorBoundary>
              }
            />
          </Route>
        </Routes>
      </Router>
    </LocalizationProvider>
  );
}

export default App;
