import React, { useMemo, useCallback, useEffect, useState, useRef } from 'react';
import Joyride, { STATUS } from 'react-joyride';
import { useTour } from '../contexts/TourContext';
import { useTranslation } from '../hooks/useTranslation';

const GuidedTour = () => {
  const { tourState, stopTour, setTourState } = useTour();
  const { t, currentLanguage } = useTranslation();
  const [forceUpdate, setForceUpdate] = useState(0);
  const joyrideRef = useRef(null);

  // Force DOM manipulation as fallback for stubborn Joyride locale
  useEffect(() => {
    if (tourState.run && currentLanguage === 'el') {
      const updateJoyrideButtons = () => {
        // Find and update Next button
        const nextButton = document.querySelector('.react-joyride__tooltip button[data-action="next"]');
        if (nextButton && nextButton.textContent.includes('Next')) {
          nextButton.textContent = nextButton.textContent.replace(/Next/g, 'Επόμενο');
        }

        // Find and update Step counter
        const stepCounter = document.querySelector('.react-joyride__tooltip [data-action="next"]');
        if (stepCounter && stepCounter.textContent.includes('Step')) {
          stepCounter.textContent = stepCounter.textContent
            .replace(/Step/g, 'Βήμα')
            .replace(/of/g, 'από');
        }

        // Alternative: Find by button text content
        const buttons = document.querySelectorAll('.react-joyride__tooltip button');
        buttons.forEach(button => {
          if (button.textContent.includes('Next (Step')) {
            const match = button.textContent.match(/Next \(Step (\d+) of (\d+)\)/);
            if (match) {
              button.textContent = `Επόμενο (Βήμα ${match[1]} από ${match[2]})`;
            }
          }
        });
      };

      // Update immediately and on mutations
      const observer = new MutationObserver(() => {
        updateJoyrideButtons();
      });

      // Start observing
      const joyrideContainer = document.querySelector('.react-joyride__tooltip');
      if (joyrideContainer) {
        observer.observe(joyrideContainer, { 
          childList: true, 
          subtree: true, 
          characterData: true 
        });
        updateJoyrideButtons(); // Initial update
      }

      // Fallback: Update every 500ms for first 5 seconds
      const intervals = [];
      for (let i = 0; i < 10; i++) {
        intervals.push(setTimeout(updateJoyrideButtons, i * 500));
      }

      return () => {
        observer.disconnect();
        intervals.forEach(clearTimeout);
      };
    }
  }, [tourState.run, tourState.stepIndex, currentLanguage]);

  // Listen for language changes in localStorage to force re-render
  useEffect(() => {
    const handleStorageChange = () => {
      setForceUpdate(prev => prev + 1);
    };

    window.addEventListener('storage', handleStorageChange);
    
    // Also listen for custom language change events
    const handleLanguageChange = () => {
      setForceUpdate(prev => prev + 1);
      
      // Force Joyride to restart if it's running
      if (tourState.run && joyrideRef.current) {
        // Stop and restart the tour to force locale update
        setTimeout(() => {
          setTourState(prev => ({ ...prev, run: false }));
          setTimeout(() => {
            setTourState(prev => ({ ...prev, run: true, stepIndex: 0 }));
          }, 100);
        }, 50);
      }
    };

    window.addEventListener('languageChanged', handleLanguageChange);

    return () => {
      window.removeEventListener('storage', handleStorageChange);
      window.removeEventListener('languageChanged', handleLanguageChange);
    };
  }, [tourState.run, setTourState]);

  // Translate the steps before passing to Joyride
  const translatedSteps = useMemo(() => {
    return tourState.steps.map(step => ({
      ...step,
      title: t(step.title),
      content: t(step.content)
    }));
  }, [tourState.steps, t, currentLanguage, forceUpdate]);

  const handleJoyrideCallback = useCallback((data) => {
    const { status, type, index, action } = data;

    // Handle close button click and other ways to stop the tour
    if ([STATUS.FINISHED, STATUS.SKIPPED].includes(status) || action === 'close') {
      stopTour();
    } else if (type === 'step:after') {
      setTourState(prev => ({
        ...prev,
        stepIndex: index + 1
      }));
    }
  }, [stopTour, setTourState]);

  const joyrideStyles = {
    options: {
      primaryColor: '#3B82F6', // Blue-500
      backgroundColor: '#FFFFFF',
      textColor: '#1F2937', // Gray-800
      overlayColor: 'rgba(0, 0, 0, 0.5)',
      spotlightShadow: '0 0 15px rgba(0, 0, 0, 0.5)',
      beaconSize: 36,
      zIndex: 10000,
    },
    tooltip: {
      borderRadius: 8,
      fontSize: 14,
      padding: 20,
      maxWidth: 400,
    },
    tooltipContainer: {
      textAlign: 'left',
    },
    tooltipTitle: {
      fontSize: 18,
      fontWeight: 600,
      marginBottom: 10,
      color: '#1F2937',
    },
    tooltipContent: {
      fontSize: 14,
      lineHeight: 1.5,
      color: '#4B5563',
    },
    buttonNext: {
      backgroundColor: '#3B82F6',
      borderRadius: 6,
      color: '#FFFFFF',
      fontSize: 14,
      fontWeight: 500,
      padding: '8px 16px',
      border: 'none',
      cursor: 'pointer',
    },
    buttonBack: {
      backgroundColor: 'transparent',
      border: '1px solid #D1D5DB',
      borderRadius: 6,
      color: '#6B7280',
      fontSize: 14,
      fontWeight: 500,
      padding: '8px 16px',
      cursor: 'pointer',
      marginRight: 8,
    },
    buttonSkip: {
      backgroundColor: 'transparent',
      border: 'none',
      color: '#6B7280',
      fontSize: 14,
      cursor: 'pointer',
      padding: '8px 16px',
    },
    buttonClose: {
      backgroundColor: 'transparent',
      border: 'none',
      color: '#6B7280',
      fontSize: 18,
      cursor: 'pointer',
      position: 'absolute',
      right: 10,
      top: 10,
    },
  };

  // Create locale object with explicit structure and force re-creation on language change
  const locale = useMemo(() => {
    // Force fresh translation calls each time
    const nextText = t('tour.next');
    const stepText = t('tour.step');
    const ofText = t('tour.of');
    
    const localeObj = {
      back: t('tour.back') || 'Back',
      close: t('tour.close') || 'Close', 
      last: t('tour.finish') || 'Finish',
      next: nextText || 'Next',
      skip: t('tour.skip') || 'Skip',
      open: t('tour.open') || 'Open',
      step: stepText || 'Step',
      of: ofText || 'of'
    };
    
    // If translations are not Greek, force them for Greek language
    if (currentLanguage === 'el' && nextText !== 'Επόμενο') {
      localeObj.next = 'Επόμενο';
      localeObj.step = 'Βήμα';
      localeObj.of = 'από';
    }
    
    return localeObj;
  }, [t, currentLanguage, forceUpdate]);

  // Force component re-render when locale changes by using key
  const joyrideKey = useMemo(() => {
    const currentLang = currentLanguage || 'en';
    const timestamp = Date.now(); // Add timestamp to ensure uniqueness
    return `joyride-${currentLang}-${forceUpdate}-${timestamp}-${locale.next}-${locale.step}-${locale.of}`;
  }, [currentLanguage, forceUpdate, locale.next, locale.step, locale.of]);

  return (
    <Joyride
      ref={joyrideRef}
      key={joyrideKey}
      callback={handleJoyrideCallback}
      continuous={true}
      run={tourState.run}
      scrollToFirstStep={true}
      showProgress={true}
      showSkipButton={true}
      stepIndex={tourState.stepIndex}
      steps={translatedSteps}
      styles={joyrideStyles}
      locale={locale}
      disableOverlayClose={true}
      disableCloseOnEsc={false}
      hideCloseButton={false}
      spotlightClicks={false}
      spotlightPadding={4}
      floaterProps={{
        disableAnimation: true,
      }}
    />
  );
};

export default GuidedTour;