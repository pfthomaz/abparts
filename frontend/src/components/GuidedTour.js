import React from 'react';
import Joyride, { STATUS } from 'react-joyride';
import { useTour } from '../contexts/TourContext';
import { useTranslation } from '../hooks/useTranslation';

const GuidedTour = () => {
  const { tourState, stopTour, setTourState } = useTour();
  const { t } = useTranslation();

  const handleJoyrideCallback = (data) => {
    const { status, type, index } = data;

    if ([STATUS.FINISHED, STATUS.SKIPPED].includes(status)) {
      stopTour();
    } else if (type === 'step:after') {
      setTourState(prev => ({
        ...prev,
        stepIndex: index + 1
      }));
    }
  };

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

  const locale = {
    back: t('tour.back'),
    close: t('tour.close'),
    last: t('tour.finish'),
    next: t('tour.next'),
    skip: t('tour.skip'),
  };

  return (
    <Joyride
      callback={handleJoyrideCallback}
      continuous={true}
      run={tourState.run}
      scrollToFirstStep={true}
      showProgress={true}
      showSkipButton={true}
      stepIndex={tourState.stepIndex}
      steps={tourState.steps}
      styles={joyrideStyles}
      locale={locale}
      disableOverlayClose={true}
      disableCloseOnEsc={false}
      hideCloseButton={false}
      spotlightClicks={false}
      spotlightPadding={4}
    />
  );
};

export default GuidedTour;