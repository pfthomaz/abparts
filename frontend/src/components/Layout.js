// frontend/src/components/Layout.js

import React, { useState, useEffect, useRef } from 'react';
import { Link, Outlet, useLocation } from 'react-router-dom';
import { useAuth } from '../AuthContext';
import { getNavigationItems, getUIConfiguration, isSuperAdmin } from '../utils/permissions';
import PermissionGuard from './PermissionGuard';
import OrganizationScopeIndicator from './OrganizationScopeIndicator';
import MobileNavigation from './MobileNavigation';
import OfflineStatusIndicator from './OfflineStatusIndicator';

const Layout = () => {
  const { user, logout } = useAuth();
  const [showUserMenu, setShowUserMenu] = useState(false);
  const [showMobileMenu, setShowMobileMenu] = useState(false);
  const userMenuRef = useRef(null);
  const location = useLocation();

  // Close user menu when clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (userMenuRef.current && !userMenuRef.current.contains(event.target)) {
        setShowUserMenu(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);

  // Get navigation items and UI configuration based on user permissions
  const navigationItems = getNavigationItems(user);
  const uiConfig = getUIConfiguration(user);

  // Group navigation items by category
  const navigationByCategory = navigationItems.reduce((acc, item) => {
    const category = item.category || 'other';
    if (!acc[category]) acc[category] = [];
    acc[category].push(item);
    return acc;
  }, {});

  const categoryOrder = ['core', 'inventory', 'operations', 'administration'];
  const categoryLabels = {
    core: 'Core',
    inventory: 'Inventory',
    operations: 'Operations',
    administration: 'Administration'
  };

  const getRoleDisplayName = (role) => {
    switch (role) {
      case 'super_admin':
        return 'Super Admin';
      case 'admin':
        return 'Admin';
      case 'user':
        return 'User';
      default:
        return role;
    }
  };

  return (
    <div className="min-h-screen bg-gray-100">
      <header className="bg-white shadow-md">
        <nav className="container mx-auto px-4 py-4">
          <div className="flex justify-between items-center">
            <div className="flex items-center space-x-8">
              <Link to="/" className="text-2xl font-bold text-gray-800">
                ABParts
              </Link>

              {/* Desktop Navigation */}
              <div className="hidden lg:flex items-center space-x-1">
                {categoryOrder.map(category => {
                  if (!uiConfig.navigationCategories[category] || !navigationByCategory[category]) return null;

                  return (
                    <div key={category} className="relative group">
                      <button className="px-3 py-2 text-sm font-medium text-gray-600 hover:text-gray-800 rounded-md hover:bg-gray-100">
                        {categoryLabels[category]}
                        <svg className="w-4 h-4 inline ml-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                        </svg>
                      </button>

                      {/* Dropdown Menu */}
                      <div className="absolute left-0 mt-1 w-64 bg-white rounded-md shadow-lg py-1 z-50 border border-gray-200 opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200">
                        {navigationByCategory[category].map((item) => {
                          if (item.path === '/') return null; // Skip dashboard

                          return (
                            <PermissionGuard
                              key={item.path}
                              permission={item.permission}
                              hideIfNoPermission={true}
                            >
                              <Link
                                to={item.path}
                                className={`block px-4 py-2 text-sm hover:bg-gray-100 ${location.pathname === item.path ? 'bg-blue-50 text-blue-700' : 'text-gray-700'
                                  }`}
                              >
                                <div className="flex items-center justify-between">
                                  <div>
                                    <div className="font-medium">{item.label}</div>
                                    <div className="text-xs text-gray-500">{item.description}</div>
                                  </div>
                                  {item.accessScope && (
                                    <span className={`text-xs px-2 py-0.5 rounded-full ${item.accessScope === 'global'
                                      ? 'bg-purple-100 text-purple-700'
                                      : 'bg-blue-100 text-blue-700'
                                      }`}>
                                      {item.accessScope}
                                    </span>
                                  )}
                                </div>
                              </Link>
                            </PermissionGuard>
                          );
                        })}
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>

            <div className="flex items-center space-x-4">
              {/* Mobile menu button */}
              <button
                onClick={() => setShowMobileMenu(!showMobileMenu)}
                className="lg:hidden p-2 rounded-md text-gray-600 hover:text-gray-800 hover:bg-gray-100"
              >
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
                </svg>
              </button>

              {/* User Menu Dropdown */}
              <div className="relative" ref={userMenuRef}>
                <button
                  onClick={() => setShowUserMenu(!showUserMenu)}
                  className="flex items-center space-x-2 text-gray-700 hover:text-gray-900 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 rounded-md px-3 py-2"
                >
                  <div className="w-8 h-8 bg-blue-500 text-white rounded-full flex items-center justify-center text-sm font-semibold">
                    {(user.name || user.username).charAt(0).toUpperCase()}
                  </div>
                  <div className="text-left hidden sm:block">
                    <div className="font-semibold">{user.name || user.username}</div>
                    <div className="text-xs text-gray-500 flex items-center space-x-1">
                      <span>{getRoleDisplayName(user.role)}</span>
                      {isSuperAdmin(user) && (
                        <span className="inline-flex items-center px-1.5 py-0.5 rounded-full text-xs font-medium bg-purple-100 text-purple-800">
                          Global
                        </span>
                      )}
                    </div>
                  </div>
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                  </svg>
                </button>

                {/* Dropdown Menu */}
                {showUserMenu && (
                  <div className="absolute right-0 mt-2 w-64 bg-white rounded-md shadow-lg py-1 z-50 border border-gray-200">
                    {/* User Info Header */}
                    <div className="px-4 py-3 border-b border-gray-100">
                      <div className="flex items-center space-x-3">
                        <div className="w-10 h-10 bg-blue-500 text-white rounded-full flex items-center justify-center font-semibold">
                          {(user.name || user.username).charAt(0).toUpperCase()}
                        </div>
                        <div>
                          <div className="font-medium text-gray-900">{user.name || user.username}</div>
                          <div className="text-sm text-gray-500">{user.email}</div>
                          <div className="text-xs text-gray-400">
                            {getRoleDisplayName(user.role)} • {user.organization?.name}
                          </div>
                        </div>
                      </div>
                    </div>

                    <Link
                      to="/profile"
                      onClick={() => setShowUserMenu(false)}
                      className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 flex items-center space-x-2"
                    >
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                      </svg>
                      <span>My Profile</span>
                    </Link>
                    <Link
                      to="/security"
                      onClick={() => setShowUserMenu(false)}
                      className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 flex items-center space-x-2"
                    >
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                      </svg>
                      <span>Security Center</span>
                    </Link>

                    {/* Admin Features */}
                    <PermissionGuard permission={['manage_org_users', 'manage_all_users']} hideIfNoPermission={true}>
                      <div className="border-t border-gray-100 mt-1 pt-1">
                        <div className="px-4 py-2 text-xs font-medium text-gray-500 uppercase tracking-wide">
                          Administration
                        </div>
                        <Link
                          to="/users"
                          onClick={() => setShowUserMenu(false)}
                          className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 flex items-center space-x-2"
                        >
                          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197m13.5-9a2.5 2.5 0 11-5 0 2.5 2.5 0 015 0z" />
                          </svg>
                          <span>User Management</span>
                        </Link>
                      </div>
                    </PermissionGuard>

                    <div className="border-t border-gray-100 mt-1 pt-1">
                      <button
                        onClick={() => {
                          setShowUserMenu(false);
                          logout();
                        }}
                        className="block w-full text-left px-4 py-2 text-sm text-red-700 hover:bg-red-50 flex items-center space-x-2"
                      >
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
                        </svg>
                        <span>Logout</span>
                      </button>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Mobile Navigation Menu */}
          {showMobileMenu && (
            <div className="lg:hidden mt-4 border-t border-gray-200 pt-4">
              <div className="space-y-4">
                {categoryOrder.map(category => {
                  if (!uiConfig.navigationCategories[category] || !navigationByCategory[category]) return null;

                  return (
                    <div key={category} className="space-y-2">
                      <div className="px-3 py-1 text-xs font-semibold text-gray-500 uppercase tracking-wide">
                        {categoryLabels[category]}
                      </div>
                      <div className="space-y-1">
                        {navigationByCategory[category].map((item) => {
                          if (item.path === '/') return null; // Skip dashboard

                          return (
                            <PermissionGuard
                              key={item.path}
                              permission={item.permission}
                              hideIfNoPermission={true}
                            >
                              <Link
                                to={item.path}
                                onClick={() => setShowMobileMenu(false)}
                                className={`block px-3 py-2 rounded-md text-sm font-medium ${location.pathname === item.path
                                  ? 'bg-blue-100 text-blue-700'
                                  : 'text-gray-600 hover:text-gray-800 hover:bg-gray-100'
                                  }`}
                              >
                                <div className="flex items-center justify-between">
                                  <div>
                                    <div className="font-medium">{item.label}</div>
                                    <div className="text-xs text-gray-500 mt-0.5">{item.description}</div>
                                  </div>
                                  {item.accessScope && (
                                    <span className={`text-xs px-2 py-0.5 rounded-full ${item.accessScope === 'global'
                                      ? 'bg-purple-100 text-purple-700'
                                      : 'bg-blue-100 text-blue-700'
                                      }`}>
                                      {item.accessScope}
                                    </span>
                                  )}
                                </div>
                              </Link>
                            </PermissionGuard>
                          );
                        })}
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          )}
        </nav>
      </header>

      {/* Organization Scope Indicator for Super Admins */}
      {uiConfig.showGlobalFilters && (
        <div className="bg-gray-50 border-b border-gray-200">
          <div className="container mx-auto px-4 py-2">
            <OrganizationScopeIndicator
              showOrganizationSelector={true}
              className="max-w-4xl"
            />
          </div>
        </div>
      )}

      {/* Offline Status Indicator */}
      <OfflineStatusIndicator />

      <main className="container mx-auto p-4 pb-20 lg:pb-4">
        <Outlet />
      </main>

      {/* Mobile Navigation */}
      <MobileNavigation />
    </div>
  );
};

export default Layout;
