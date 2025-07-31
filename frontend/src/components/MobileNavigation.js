// frontend/src/components/MobileNavigation.js

import React, { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { useAuth } from '../AuthContext';
import { getNavigationItems, hasPermission, PERMISSIONS } from '../utils/permissions';
import PermissionGuard from './PermissionGuard';

const MobileNavigation = () => {
  const { user } = useAuth();
  const location = useLocation();
  const [isOpen, setIsOpen] = useState(false);

  const navigationItems = getNavigationItems(user);

  // Filter to show only essential warehouse operations for mobile
  const mobileEssentialItems = navigationItems.filter(item =>
    ['/', '/inventory', '/orders', '/machines', '/parts', '/warehouses'].includes(item.path)
  );

  // Quick action items for mobile
  const quickActions = [
    {
      path: '/orders',
      label: 'Order Parts',
      icon: (
        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 11V7a4 4 0 00-8 0v4M8 11v6h8v-6M8 11H6a2 2 0 00-2 2v6a2 2 0 002 2h12a2 2 0 002-2v-6a2 2 0 00-2-2h-2" />
        </svg>
      ),
      permission: PERMISSIONS.ORDER_PARTS,
      color: 'bg-blue-500'
    },
    {
      path: '/machines',
      label: 'Record Hours',
      icon: (
        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      ),
      permission: PERMISSIONS.VIEW_ORG_MACHINES,
      color: 'bg-green-500'
    },
    {
      path: '/inventory',
      label: 'Check Stock',
      icon: (
        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" />
        </svg>
      ),
      permission: PERMISSIONS.VIEW_INVENTORY,
      color: 'bg-purple-500'
    },
    {
      path: '/transactions',
      label: 'Use Parts',
      icon: (
        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7h12m0 0l-4-4m4 4l-4 4m0 6H4m0 0l4 4m-4-4l4-4" />
        </svg>
      ),
      permission: PERMISSIONS.RECORD_PART_USAGE,
      color: 'bg-orange-500'
    }
  ];

  return (
    <>
      {/* Mobile Bottom Navigation Bar */}
      <div className="fixed bottom-0 left-0 right-0 bg-white border-t border-gray-200 z-50 lg:hidden">
        <div className="grid grid-cols-5 h-16">
          {/* Dashboard */}
          <Link
            to="/"
            className={`flex flex-col items-center justify-center space-y-1 text-xs font-medium transition-colors
              ${location.pathname === '/'
                ? 'text-blue-600 bg-blue-50'
                : 'text-gray-600 hover:text-gray-900 active:bg-gray-100'}`}
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2H5a2 2 0 00-2-2z" />
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 5a2 2 0 012-2h4a2 2 0 012 2v6H8V5z" />
            </svg>
            <span>Home</span>
          </Link>

          {/* Inventory */}
          <PermissionGuard permission={PERMISSIONS.VIEW_INVENTORY} hideIfNoPermission={true}>
            <Link
              to="/inventory"
              className={`flex flex-col items-center justify-center space-y-1 text-xs font-medium transition-colors
                ${location.pathname === '/inventory'
                  ? 'text-blue-600 bg-blue-50'
                  : 'text-gray-600 hover:text-gray-900 active:bg-gray-100'}`}
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" />
              </svg>
              <span>Stock</span>
            </Link>
          </PermissionGuard>

          {/* Quick Actions Menu */}
          <button
            onClick={() => setIsOpen(true)}
            className="flex flex-col items-center justify-center space-y-1 text-xs font-medium text-gray-600 hover:text-gray-900 active:bg-gray-100 transition-colors"
          >
            <div className="relative">
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
              </svg>
              <div className="absolute -top-1 -right-1 w-3 h-3 bg-blue-500 rounded-full"></div>
            </div>
            <span>Actions</span>
          </button>

          {/* Orders */}
          <PermissionGuard permission={PERMISSIONS.ORDER_PARTS} hideIfNoPermission={true}>
            <Link
              to="/orders"
              className={`flex flex-col items-center justify-center space-y-1 text-xs font-medium transition-colors
                ${location.pathname === '/orders'
                  ? 'text-blue-600 bg-blue-50'
                  : 'text-gray-600 hover:text-gray-900 active:bg-gray-100'}`}
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 11V7a4 4 0 00-8 0v4M8 11v6h8v-6M8 11H6a2 2 0 00-2 2v6a2 2 0 002 2h12a2 2 0 002-2v-6a2 2 0 00-2-2h-2" />
              </svg>
              <span>Orders</span>
            </Link>
          </PermissionGuard>

          {/* Machines */}
          <PermissionGuard permission={PERMISSIONS.VIEW_ORG_MACHINES} hideIfNoPermission={true}>
            <Link
              to="/machines"
              className={`flex flex-col items-center justify-center space-y-1 text-xs font-medium transition-colors
                ${location.pathname === '/machines'
                  ? 'text-blue-600 bg-blue-50'
                  : 'text-gray-600 hover:text-gray-900 active:bg-gray-100'}`}
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
              </svg>
              <span>Machines</span>
            </Link>
          </PermissionGuard>
        </div>
      </div>

      {/* Quick Actions Modal */}
      {isOpen && (
        <div className="fixed inset-0 bg-black bg-opacity-50 z-50 lg:hidden">
          <div className="fixed bottom-0 left-0 right-0 bg-white rounded-t-3xl p-6 max-h-[80vh] overflow-y-auto">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-bold text-gray-900">Quick Actions</h2>
              <button
                onClick={() => setIsOpen(false)}
                className="p-2 text-gray-400 hover:text-gray-600 rounded-full hover:bg-gray-100"
              >
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>

            {/* Quick Action Buttons */}
            <div className="grid grid-cols-2 gap-4 mb-6">
              {quickActions.map((action) => (
                <PermissionGuard key={action.path} permission={action.permission} hideIfNoPermission={true}>
                  <Link
                    to={action.path}
                    onClick={() => setIsOpen(false)}
                    className={`${action.color} text-white rounded-2xl p-4 flex flex-col items-center space-y-2 
                      shadow-lg hover:shadow-xl transform hover:scale-105 transition-all duration-200
                      active:scale-95 touch-manipulation`}
                  >
                    {action.icon}
                    <span className="font-semibold text-sm text-center">{action.label}</span>
                  </Link>
                </PermissionGuard>
              ))}
            </div>

            {/* All Navigation Items */}
            <div className="border-t border-gray-200 pt-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">All Features</h3>
              <div className="space-y-2">
                {mobileEssentialItems.map((item) => (
                  <PermissionGuard key={item.path} permission={item.permission} hideIfNoPermission={true}>
                    <Link
                      to={item.path}
                      onClick={() => setIsOpen(false)}
                      className={`flex items-center space-x-3 p-3 rounded-xl transition-colors
                        ${location.pathname === item.path
                          ? 'bg-blue-50 text-blue-700'
                          : 'text-gray-700 hover:bg-gray-100 active:bg-gray-200'}`}
                    >
                      <div className="w-8 h-8 flex items-center justify-center">
                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                        </svg>
                      </div>
                      <div>
                        <div className="font-medium">{item.label}</div>
                        <div className="text-xs text-gray-500">{item.description}</div>
                      </div>
                    </Link>
                  </PermissionGuard>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Add bottom padding to main content to account for mobile nav */}
      <style jsx>{`
        @media (max-width: 1023px) {
          main {
            padding-bottom: 80px !important;
          }
        }
      `}</style>
    </>
  );
};

export default MobileNavigation;