// frontend/src/components/FloatingActionButton.js

import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useTranslation } from '../hooks/useTranslation';

const FloatingActionButton = () => {
  const [isOpen, setIsOpen] = useState(false);
  const navigate = useNavigate();
  const { t } = useTranslation();

  const actions = [
    {
      id: 'wash-nets',
      label: t('fab.washNets'),
      icon: '🌊',
      color: 'bg-teal-500 hover:bg-teal-600',
      path: '/net-cleaning-records/new',
      onClick: () => navigate('/net-cleaning-records')
    },
    {
      id: 'daily-service',
      label: t('fab.dailyService'),
      icon: '🔧',
      color: 'bg-orange-500 hover:bg-orange-600',
      path: '/daily-operations',
      onClick: () => navigate('/daily-operations')
    },
    {
      id: 'order-parts',
      label: t('fab.orderParts'),
      icon: '📦',
      color: 'bg-blue-500 hover:bg-blue-600',
      path: '/orders',
      onClick: () => navigate('/orders')
    }
  ];

  const handleActionClick = (action) => {
    action.onClick();
    setIsOpen(false);
  };

  return (
    <>
      {/* Backdrop */}
      {isOpen && (
        <div
          className="fixed inset-0 bg-black bg-opacity-30 z-40 transition-opacity"
          onClick={() => setIsOpen(false)}
        />
      )}

      {/* Action Menu */}
      <div className="fixed right-4 md:right-8 z-50 flex flex-col-reverse items-end space-y-reverse space-y-3"
        style={{
          bottom: 'max(13rem, calc(8.75rem + env(safe-area-inset-bottom)))'
        }}
      >
        {isOpen && actions.map((action, index) => (
          <div
            key={action.id}
            className="flex items-center space-x-3 animate-fade-in-up"
            style={{ animationDelay: `${index * 50}ms` }}
          >
            {/* Label */}
            <span className="bg-gray-900 text-white px-3 py-2 rounded-lg text-sm font-medium shadow-lg whitespace-nowrap">
              {action.label}
            </span>
            
            {/* Action Button */}
            <button
              onClick={() => handleActionClick(action)}
              className={`${action.color} text-white w-14 h-14 rounded-full shadow-lg 
                flex items-center justify-center text-2xl
                transform transition-all duration-200 hover:scale-110 active:scale-95
                focus:outline-none focus:ring-4 focus:ring-opacity-50`}
              aria-label={action.label}
            >
              {action.icon}
            </button>
          </div>
        ))}
      </div>

      {/* Main FAB */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className={`fixed right-4 md:right-8 z-50
          w-16 h-16 rounded-full shadow-2xl
          flex items-center justify-center text-white text-2xl
          transform transition-all duration-300
          focus:outline-none focus:ring-4 focus:ring-blue-300 focus:ring-opacity-50
          ${isOpen 
            ? 'bg-red-500 hover:bg-red-600 rotate-45' 
            : 'bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700 hover:scale-110'
          }
          active:scale-95`}
        style={{
          bottom: 'max(9rem, calc(4.75rem + env(safe-area-inset-bottom)))'
        }}
        aria-label={isOpen ? t('fab.close') : t('fab.quickActions')}
        aria-expanded={isOpen}
      >
        {isOpen ? '✕' : '+'}
      </button>

      <style jsx>{`
        @keyframes fade-in-up {
          from {
            opacity: 0;
            transform: translateY(10px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }
        .animate-fade-in-up {
          animation: fade-in-up 0.3s ease-out forwards;
        }
      `}</style>
    </>
  );
};

export default FloatingActionButton;
