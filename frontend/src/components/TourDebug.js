import React from 'react';
import { useTour } from '../contexts/TourContext';

const TourDebug = () => {
  const { activeTour, tourState } = useTour();

  return (
    <div className="fixed top-4 left-4 bg-yellow-100 border border-yellow-400 text-yellow-700 px-4 py-3 rounded z-50">
      <strong className="font-bold">Tour Debug:</strong>
      <div className="text-sm mt-1">
        <div>Active Tour: {activeTour || 'None'}</div>
        <div>Tour Running: {tourState.run ? 'Yes' : 'No'}</div>
        <div>Steps: {tourState.steps.length}</div>
        <div>TourContext: {activeTour !== undefined ? 'Working' : 'Not Working'}</div>
      </div>
    </div>
  );
};

export default TourDebug;