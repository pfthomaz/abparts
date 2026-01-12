import React, { useState } from 'react';
import { useTour } from '../contexts/TourContext';
import { useTranslation } from '../hooks/useTranslation';
import { tourSteps } from '../data/tourSteps';

const TourButtonSimple = () => {
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const { startTour } = useTour();
  const { t } = useTranslation();

  const availableTours = [
    {
      id: 'parts-ordering',
      title: t('tour.partsOrdering.title'),
      description: t('tour.partsOrdering.description'),
      icon: '📦',
      steps: tourSteps.partsOrdering
    },
    {
      id: 'parts-usage',
      title: t('tour.partsUsage.title'),
      description: t('tour.partsUsage.description'),
      icon: '🔧',
      steps: tourSteps.partsUsage
    },
    {
      id: 'daily-operations',
      title: t('tour.dailyOperations.title'),
      description: t('tour.dailyOperations.description'),
      icon: '📋',
      steps: tourSteps.dailyOperations
    },
    {
      id: 'scheduled-maintenance',
      title: t('tour.scheduledMaintenance.title'),
      description: t('tour.scheduledMaintenance.description'),
      icon: '⚙️',
      steps: tourSteps.scheduledMaintenance
    }
  ];

  const handleTourStart = (tour) => {
    setIsMenuOpen(false);
    startTour(tour.id, tour.steps);
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
          className="bg-blue-600 hover:bg-blue-700 text-white rounded-full shadow-lg transition-all duration-200 hover:scale-105 text-lg sm:text-xl p-2 sm:p-3"
          title={t('tour.helpButton')}
        >
          {isMenuOpen ? '✕' : '?'}
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
              <button
                key={tour.id}
                onClick={() => handleTourStart(tour)}
                className="w-full text-left p-3 rounded-lg hover:bg-gray-50 transition-colors duration-150 border-b border-gray-100 last:border-b-0"
              >
                <div className="flex items-start space-x-3">
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
              </button>
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

export default TourButtonSimple;