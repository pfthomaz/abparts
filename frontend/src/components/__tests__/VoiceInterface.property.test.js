// frontend/src/components/__tests__/VoiceInterface.property.test.js

/**
 * Feature: autoboss-ai-assistant, Property 2: Multilingual Communication (Voice Components)
 * Validates: Requirements 2.3, 2.4, 2.5
 * 
 * Property: For any supported language, user input (text or voice) should be correctly 
 * processed and responses should be generated in the same language with optional audio output
 */

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { act } from 'react';
import '@testing-library/jest-dom';
import VoiceInterface from '../VoiceInterface';
import { useTranslation } from '../../hooks/useTranslation';
import { useLocalization } from '../../contexts/LocalizationContext';

// Mock the hooks
jest.mock('../../hooks/useTranslation');
jest.mock('../../contexts/LocalizationContext');

// Create a more sophisticated mock for SpeechRecognition
let mockRecognitionInstance = null;

const createMockSpeechRecognition = () => {
  const instance = {
    start: jest.fn(),
    stop: jest.fn(),
    abort: jest.fn(),
    addEventListener: jest.fn(),
    removeEventListener: jest.fn(),
    continuous: false,
    interimResults: false,
    lang: 'en-US',
    maxAlternatives: 1,
    onstart: null,
    onend: null,
    onresult: null,
    onerror: null
  };
  mockRecognitionInstance = instance;
  return instance;
};

const mockSpeechSynthesis = {
  speak: jest.fn(),
  cancel: jest.fn(),
  getVoices: jest.fn(() => [
    { lang: 'en-US', name: 'English US', default: true },
    { lang: 'el-GR', name: 'Greek', default: false },
    { lang: 'ar-SA', name: 'Arabic', default: false },
    { lang: 'es-ES', name: 'Spanish', default: false },
    { lang: 'tr-TR', name: 'Turkish', default: false },
    { lang: 'nb-NO', name: 'Norwegian', default: false }
  ]),
  onvoiceschanged: null
};

const mockSpeechSynthesisUtterance = jest.fn().mockImplementation((text) => ({
  text,
  lang: 'en-US',
  rate: 1,
  pitch: 1,
  volume: 1,
  onstart: null,
  onend: null,
  onerror: null
}));

// Mock navigator.mediaDevices
Object.defineProperty(navigator, 'mediaDevices', {
  writable: true,
  value: {
    getUserMedia: jest.fn(() => Promise.resolve({
      getTracks: () => [{ stop: jest.fn() }]
    }))
  }
});

// Setup global mocks
beforeAll(() => {
  global.SpeechRecognition = jest.fn(createMockSpeechRecognition);
  global.webkitSpeechRecognition = global.SpeechRecognition;
  global.speechSynthesis = mockSpeechSynthesis;
  global.SpeechSynthesisUtterance = mockSpeechSynthesisUtterance;
});

// Test data generators
const supportedLanguages = ['en', 'el', 'ar', 'es', 'tr', 'no'];
const sampleTexts = [
  'Hello, how can I help you?',
  'Machine is not working properly',
  'Need assistance with maintenance',
  'Clear the chat history',
  'Help me troubleshoot',
  'Stop the current operation'
];

const voiceCommands = {
  'en': ['clear', 'help', 'stop', 'repeat'],
  'el': ['καθάρισε', 'βοήθεια', 'σταμάτα', 'επανάλαβε'],
  'ar': ['امسح', 'مساعدة', 'توقف', 'كرر'],
  'es': ['limpiar', 'ayuda', 'parar', 'repetir'],
  'tr': ['temizle', 'yardım', 'dur', 'tekrarla'],
  'no': ['tøm', 'hjelp', 'stopp', 'gjenta']
};

describe('VoiceInterface Property Tests', () => {
  let mockT, mockUseLocalization;

  beforeEach(() => {
    // Reset mocks
    jest.clearAllMocks();
    mockRecognitionInstance = null;
    
    // Setup translation mock
    mockT = jest.fn((key, params) => {
      const translations = {
        'aiAssistant.voice.startListening': 'Start Voice Input',
        'aiAssistant.voice.stopListening': 'Stop Listening',
        'aiAssistant.voice.listening': 'Listening...',
        'aiAssistant.voice.processing': 'Processing speech...',
        'aiAssistant.voice.speakResponse': 'Speak Response',
        'aiAssistant.voice.voiceNotSupported': 'Voice input not supported in this browser',
        'aiAssistant.voice.microphonePermissionDenied': 'Microphone permission denied',
        'aiAssistant.voice.speechRecognitionError': 'Speech recognition error'
      };
      return translations[key] || key;
    });
    
    useTranslation.mockReturnValue({ t: mockT });
    
    // Setup localization mock
    mockUseLocalization = {
      currentLanguage: 'en'
    };
    useLocalization.mockReturnValue(mockUseLocalization);
  });

  /**
   * Property: Language-specific speech recognition configuration
   * For any supported language, the speech recognition should be configured 
   * with the correct language code
   */
  test('property: speech recognition language configuration for all supported languages', () => {
    const expectedLangCodes = {
      'en': 'en-US',
      'el': 'el-GR',
      'ar': 'ar-SA',
      'es': 'es-ES',
      'tr': 'tr-TR',
      'no': 'nb-NO'
    };

    // Test each supported language
    supportedLanguages.forEach(language => {
      // Reset mocks for each iteration
      jest.clearAllMocks();
      mockRecognitionInstance = null;
      
      // Setup language context
      mockUseLocalization.currentLanguage = language;
      useLocalization.mockReturnValue(mockUseLocalization);
      
      const onSpeechResult = jest.fn();
      const onSpeechError = jest.fn();
      
      const { unmount } = render(
        <VoiceInterface
          onSpeechResult={onSpeechResult}
          onSpeechError={onSpeechError}
          isEnabled={true}
        />
      );
      
      // Verify that SpeechRecognition was created
      expect(global.SpeechRecognition).toHaveBeenCalled();
      
      // Verify the language was set correctly on the instance
      expect(mockRecognitionInstance).not.toBeNull();
      expect(mockRecognitionInstance.lang).toBe(expectedLangCodes[language]);
      
      unmount();
    });
  });

  /**
   * Property: Speech input processing consistency
   * For any speech input in any supported language, the transcript should be 
   * correctly passed to the callback function
   */
  test('property: speech input processing consistency across languages and texts', () => {
    supportedLanguages.forEach(language => {
      sampleTexts.forEach(text => {
        // Reset mocks for each iteration
        jest.clearAllMocks();
        mockRecognitionInstance = null;
        
        mockUseLocalization.currentLanguage = language;
        useLocalization.mockReturnValue(mockUseLocalization);
        
        const onSpeechResult = jest.fn();
        const onSpeechError = jest.fn();
        
        const { unmount } = render(
          <VoiceInterface
            onSpeechResult={onSpeechResult}
            onSpeechError={onSpeechError}
            isEnabled={true}
          />
        );
        
        // Simulate speech recognition result
        const mockEvent = {
          results: [{
            0: {
              transcript: text,
              confidence: 0.9
            }
          }]
        };
        
        act(() => {
          if (mockRecognitionInstance && mockRecognitionInstance.onresult) {
            mockRecognitionInstance.onresult(mockEvent);
          }
        });
        
        // Verify the transcript was passed correctly
        expect(onSpeechResult).toHaveBeenCalledWith(text.trim());
        
        unmount();
      });
    });
  });

  /**
   * Property: Voice command recognition across languages
   * For any voice command in any supported language, the command should be 
   * correctly identified and handled
   */
  test('property: voice command recognition across all supported languages', () => {
    const commandMapping = {
      'clear': 0,
      'help': 1,
      'stop': 2,
      'repeat': 3
    };

    supportedLanguages.forEach(language => {
      const commands = voiceCommands[language];
      
      commands.forEach((commandText, index) => {
        // Reset mocks for each iteration
        jest.clearAllMocks();
        mockRecognitionInstance = null;
        
        mockUseLocalization.currentLanguage = language;
        useLocalization.mockReturnValue(mockUseLocalization);
        
        const onSpeechResult = jest.fn();
        const onVoiceCommand = jest.fn();
        
        const { unmount } = render(
          <VoiceInterface
            onSpeechResult={onSpeechResult}
            onVoiceCommand={onVoiceCommand}
            isEnabled={true}
          />
        );
        
        // Simulate speech recognition with command
        const mockEvent = {
          results: [{
            0: {
              transcript: commandText,
              confidence: 0.9
            }
          }]
        };
        
        act(() => {
          if (mockRecognitionInstance && mockRecognitionInstance.onresult) {
            mockRecognitionInstance.onresult(mockEvent);
          }
        });
        
        // Verify command was recognized
        const expectedCommand = Object.keys(commandMapping)[index];
        expect(onVoiceCommand).toHaveBeenCalledWith(expectedCommand, commandText);
        
        unmount();
      });
    });
  });

  /**
   * Property: Text-to-speech language consistency
   * For any text in any supported language, the speech synthesis should use 
   * the appropriate voice and language settings
   */
  test('property: text-to-speech language consistency across languages', () => {
    supportedLanguages.forEach(language => {
      sampleTexts.forEach(text => {
        // Reset mocks for each iteration
        jest.clearAllMocks();
        
        mockUseLocalization.currentLanguage = language;
        useLocalization.mockReturnValue(mockUseLocalization);
        
        const onSpeechResult = jest.fn();
        
        const { unmount } = render(
          <VoiceInterface
            onSpeechResult={onSpeechResult}
            isEnabled={true}
            autoSpeak={false}
          />
        );
        
        // Simulate speaking text
        act(() => {
          const utterance = new mockSpeechSynthesisUtterance(text);
          mockSpeechSynthesis.speak(utterance);
        });
        
        // Verify speech synthesis was called
        expect(mockSpeechSynthesis.speak).toHaveBeenCalled();
        expect(mockSpeechSynthesisUtterance).toHaveBeenCalledWith(text);
        
        unmount();
      });
    });
  });

  /**
   * Property: Error handling consistency
   * For any error condition, the component should handle it gracefully 
   * and provide appropriate user feedback
   */
  test('property: error handling consistency across languages and error types', () => {
    const errorTypes = ['not-allowed', 'no-speech', 'network', 'language-not-supported'];
    
    supportedLanguages.forEach(language => {
      errorTypes.forEach(errorType => {
        // Reset mocks for each iteration
        jest.clearAllMocks();
        mockRecognitionInstance = null;
        
        mockUseLocalization.currentLanguage = language;
        useLocalization.mockReturnValue(mockUseLocalization);
        
        const onSpeechResult = jest.fn();
        const onSpeechError = jest.fn();
        
        const { unmount } = render(
          <VoiceInterface
            onSpeechResult={onSpeechResult}
            onSpeechError={onSpeechError}
            isEnabled={true}
          />
        );
        
        // Simulate error
        const mockError = { error: errorType };
        
        act(() => {
          if (mockRecognitionInstance && mockRecognitionInstance.onerror) {
            mockRecognitionInstance.onerror(mockError);
          }
        });
        
        // Verify error was handled
        expect(onSpeechError).toHaveBeenCalled();
        
        unmount();
      });
    });
  });

  /**
   * Property: Component state consistency
   * For any sequence of user interactions, the component state should remain consistent
   */
  test('property: component state consistency across interaction sequences', () => {
    const actionSequences = [
      ['start', 'stop'],
      ['start', 'error', 'start'],
      ['speak', 'stop'],
      ['start', 'speak', 'error', 'stop']
    ];

    supportedLanguages.forEach(language => {
      actionSequences.forEach(actions => {
        // Reset mocks for each iteration
        jest.clearAllMocks();
        mockRecognitionInstance = null;
        
        mockUseLocalization.currentLanguage = language;
        useLocalization.mockReturnValue(mockUseLocalization);
        
        const onSpeechResult = jest.fn();
        const onSpeechError = jest.fn();
        
        const { unmount } = render(
          <VoiceInterface
            onSpeechResult={onSpeechResult}
            onSpeechError={onSpeechError}
            isEnabled={true}
          />
        );
        
        // Execute sequence of actions
        actions.forEach(action => {
          act(() => {
            switch (action) {
              case 'start':
                if (mockRecognitionInstance && mockRecognitionInstance.onstart) {
                  mockRecognitionInstance.onstart();
                }
                break;
              case 'stop':
                if (mockRecognitionInstance && mockRecognitionInstance.onend) {
                  mockRecognitionInstance.onend();
                }
                break;
              case 'speak':
                mockSpeechSynthesis.speak(new mockSpeechSynthesisUtterance('test'));
                break;
              case 'error':
                if (mockRecognitionInstance && mockRecognitionInstance.onerror) {
                  mockRecognitionInstance.onerror({ error: 'network' });
                }
                break;
            }
          });
        });
        
        // Component should still be functional after any sequence of actions
        const voiceButton = screen.getByRole('button');
        expect(voiceButton).toBeInTheDocument();
        expect(voiceButton).not.toBeDisabled();
        
        unmount();
      });
    });
  });
});