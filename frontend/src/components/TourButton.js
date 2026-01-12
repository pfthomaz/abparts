import React, { useState } from 'react';
import { QuestionMarkCircleIcon, XMarkIcon } from '@heroicons/react/24/outline';
import { useNavigate } from 'react-router-dom';
import { useTour } from '../contexts/TourContext';
import { useTranslation } from '../hooks/useTranslation';
import { tourSteps } from '../data/tourSteps';

const TourButton = () => {
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const { startTour } = useTour();
  const { t } = useTranslation();
  const navigate = useNavigate();

  const availableTours = [
    {
      id: 'parts-ordering',
      title: t('tour.partsOrdering.title'),
      description: t('tour.partsOrdering.description'),
      icon: '📦',
      steps: tourSteps.partsOrdering,
      route: '/orders'
    },
    {
      id: 'parts-usage',
      title: t('tour.partsUsage.title'),
      description: t('tour.partsUsage.description'),
      icon: '🔧',
      steps: tourSteps.partsUsage,
      route: '/machines'
    },
    {
      id: 'daily-operations',
      title: t('tour.dailyOperations.title'),
      description: t('tour.dailyOperations.description'),
      icon: '📋',
      steps: tourSteps.dailyOperations,
      route: '/daily-operations'
    },
    {
      id: 'scheduled-maintenance',
      title: t('tour.scheduledMaintenance.title'),
      description: t('tour.scheduledMaintenance.description'),
      icon: '⚙️',
      steps: tourSteps.scheduledMaintenance,
      route: '/maintenance-executions'
    }
  ];

  const handleTourStart = (tour, isInteractive = false) => {
    setIsMenuOpen(false);
    
    if (isInteractive) {
      // Navigate to the relevant page first, then start tour
      navigate(tour.route);
      // Small delay to let the page load
      setTimeout(() => {
        startTour(tour.id, tour.steps);
      }, 500);
    } else {
      startTour(tour.id, tour.steps);
    }
  };

  return (
    <>
      {/* Help Button */}
      <div 
        className="fixed right-4 z-50"
        style={{
          bottom: 'max(5rem, calc(0.75rem + env(safe-area-inset-bottom)))'
        }}
      >
        <button
          onClick={() => setIsMenuOpen(!isMenuOpen)}
          className="bg-blue-600 hover:bg-blue-700 text-white rounded-full shadow-lg transition-all duration-200 hover:scale-105 p-3 sm:p-4"
          title={t('tour.helpButton')}
        >
          {isMenuOpen ? (
            <XMarkIcon className="h-5 w-5 sm:h-6 sm:w-6" />
          ) : (
            <QuestionMarkCircleIcon className="h-5 w-5 sm:h-6 sm:w-6" />
          )}
        </button>
      </div>

      {/* Tour Menu */}
      {isMenuOpen && (
        <div 
          className="fixed right-4 z-50 bg-white rounded-lg shadow-xl border border-gray-200 w-80 max-h-96 overflow-y-auto"
          style={{
            bottom: 'max(9rem, calc(4.75rem + env(safe-area-inset-bottom)))'
          }}
        >
          <div className="p-4 border-b border-gray-200">
            <h3 className="text-lg font-semibold text-gray-900">
              {t('tour.menuTitle')}
            </h3>
            <p className="text-sm text-gray-600 mt-1">
              {t('tour.menuDescription')}
            </p>
          </div>
          
          <div className="p-2">
            {availableTours.map((tour) => (
              <div key={tour.id} className="border-b border-gray-100 last:border-b-0">
                <div className="flex items-start space-x-3 p-3">
                  <span className="text-2xl">{tour.icon}</span>
                  <div className="flex-1 min-w-0">
                    <h4 className="text-sm font-medium text-gray-900 truncate">
                      {tour.title}
                    </h4>
                    <p className="text-xs text-gray-600 mt-1 line-clamp-2">
                      {tour.description}
                    </p>
                  </div>
                </div>
                <div className="flex space-x-2 px-3 pb-3">
                  <button
                    onClick={() => handleTourStart(tour, false)}
                    className="flex-1 text-xs bg-blue-50 text-blue-700 px-2 py-1 rounded hover:bg-blue-100 transition-colors"
                  >
                    📖 {t('tour.quickGuide')}
                  </button>
                  <button
                    onClick={() => handleTourStart(tour, true)}
                    className="flex-1 text-xs bg-green-50 text-green-700 px-2 py-1 rounded hover:bg-green-100 transition-colors"
                  >
                    🎯 {t('tour.interactive')}
                  </button>
                </div>
              </div>
            ))}
          </div>
          
          <div className="p-4 border-t border-gray-200 bg-gray-50">
            <p className="text-xs text-gray-500 text-center">
              {t('tour.menuFooter')}
            </p>
          </div>
        </div>
      )}

      {/* Backdrop */}
      {isMenuOpen && (
        <div
          className="fixed inset-0 z-40"
          onClick={() => setIsMenuOpen(false)}
        />
      )}
    </>
  );
};

export default TourButton;