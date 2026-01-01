import React, { createContext, useContext, useState, useCallback } from 'react';

const TourContext = createContext();

export const useTour = () => {
  const context = useContext(TourContext);
  if (!context) {
    throw new Error('useTour must be used within a TourProvider');
  }
  return context;
};

export const TourProvider = ({ children }) => {
  const [activeTour, setActiveTour] = useState(null);
  const [tourState, setTourState] = useState({
    run: false,
    stepIndex: 0,
    steps: []
  });

  const startTour = useCallback((tourId, steps) => {
    setActiveTour(tourId);
    setTourState({
      run: true,
      stepIndex: 0,
      steps: steps || []
    });
  }, []);

  const stopTour = useCallback(() => {
    setActiveTour(null);
    setTourState({
      run: false,
      stepIndex: 0,
      steps: []
    });
  }, []);

  const nextStep = useCallback(() => {
    setTourState(prev => ({
      ...prev,
      stepIndex: prev.stepIndex + 1
    }));
  }, []);

  const prevStep = useCallback(() => {
    setTourState(prev => ({
      ...prev,
      stepIndex: Math.max(0, prev.stepIndex - 1)
    }));
  }, []);

  const value = {
    activeTour,
    tourState,
    startTour,
    stopTour,
    nextStep,
    prevStep,
    setTourState
  };

  return (
    <TourContext.Provider value={value}>
      {children}
    </TourContext.Provider>
  );
};