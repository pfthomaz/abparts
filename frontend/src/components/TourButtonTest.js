import React, { useState } from 'react';
import { useTour } from '../contexts/TourContext';

const TourButtonTest = () => {
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const { startTour } = useTour();

  const testTour = () => {
    const steps = [
      {
        target: 'body',
        content: 'Welcome to the ABParts tour system! This is a test to make sure everything is working.',
        title: 'Tour System Test',
        placement: 'center',
        disableBeacon: true,
      }
    ];
    
    startTour('test-tour', steps);
  };

  return (
    <>
      {/* Large, obvious test button */}
      <div className="fixed bottom-6 right-6 z-50">
        <button
          onClick={testTour}
          className="bg-red-600 hover:bg-red-700 text-white rounded-lg px-6 py-4 shadow-lg text-lg font-bold"
          title="Test Tour System"
        >
          🎯 TEST TOUR
        </button>
      </div>

      {/* Simple menu toggle */}
      <div className="fixed bottom-6 right-40 z-50">
        <button
          onClick={() => setIsMenuOpen(!isMenuOpen)}
          className="bg-blue-600 hover:bg-blue-700 text-white rounded-full p-4 shadow-lg text-xl"
          title="Help Menu"
        >
          {isMenuOpen ? '✕' : '?'}
        </button>
      </div>

      {/* Simple menu */}
      {isMenuOpen && (
        <div className="fixed bottom-20 right-40 z-50 bg-white rounded-lg shadow-xl border border-gray-200 w-64 p-4">
          <h3 className="text-lg font-semibold text-gray-900 mb-2">
            Tour Menu
          </h3>
          <button
            onClick={testTour}
            className="w-full text-left p-2 rounded hover:bg-gray-50 border border-gray-200"
          >
            🧪 Test Tour System
          </button>
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

export default TourButtonTest;