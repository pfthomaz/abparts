// frontend/src/components/VoiceInterface.js

import React, { useState, useEffect, useRef, useCallback } from 'react';
import { useTranslation } from '../hooks/useTranslation';
import { useLocalization } from '../contexts/LocalizationContext';
import speechManager from '../utils/speechSynthesisManager';

const VoiceInterface = React.forwardRef(({ 
  onSpeechResult, 
  onSpeechError, 
  isEnabled = true,
  autoSpeak = false,
  className = "",
  onVoiceCommand = null
}, ref) => {
  const { t } = useTranslation();
  const { currentLanguage } = useLocalization();
  
  const [isListening, setIsListening] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [isSupported, setIsSupported] = useState(false);
  const [hasPermission, setHasPermission] = useState(null);
  const [error, setError] = useState(null);
  const [availableVoices, setAvailableVoices] = useState([]);
  
  const recognitionRef = useRef(null);
  const speechSynthesisRef = useRef(null);
  const currentUtteranceRef = useRef(null);

  // Language mapping for speech recognition with fallbacks
  const getLanguageCode = useCallback((language) => {
    const languageMap = {
      'en': 'en-US',
      'el': 'el-GR', 
      'ar': 'ar-SA',
      'es': 'es-ES',
      'tr': 'tr-TR',
      'no': 'nb-NO'
    };
    return languageMap[language] || 'en-US';
  }, []);

  // Voice command patterns for different languages
  const getVoiceCommands = useCallback((language) => {
    const commands = {
      'en': {
        'clear': /^(clear|reset|new chat|start over)$/i,
        'help': /^(help|what can you do|commands)$/i,
        'stop': /^(stop|cancel|nevermind)$/i,
        'repeat': /^(repeat|say again|what)$/i
      },
      'el': {
        'clear': /^(καθάρισε|επαναφορά|νέα συνομιλία|ξεκίνα από την αρχή)$/i,
        'help': /^(βοήθεια|τι μπορείς να κάνεις|εντολές)$/i,
        'stop': /^(σταμάτα|ακύρωση|δεν πειράζει)$/i,
        'repeat': /^(επανάλαβε|πες το ξανά|τι)$/i
      },
      'ar': {
        'clear': /^(امسح|إعادة تعيين|محادثة جديدة|ابدأ من جديد)$/i,
        'help': /^(مساعدة|ماذا يمكنك أن تفعل|الأوامر)$/i,
        'stop': /^(توقف|إلغاء|لا يهم)$/i,
        'repeat': /^(كرر|قل مرة أخرى|ماذا)$/i
      },
      'es': {
        'clear': /^(limpiar|reiniciar|nuevo chat|empezar de nuevo)$/i,
        'help': /^(ayuda|qué puedes hacer|comandos)$/i,
        'stop': /^(parar|cancelar|no importa)$/i,
        'repeat': /^(repetir|di otra vez|qué)$/i
      },
      'tr': {
        'clear': /^(temizle|sıfırla|yeni sohbet|baştan başla)$/i,
        'help': /^(yardım|ne yapabilirsin|komutlar)$/i,
        'stop': /^(dur|iptal|önemli değil)$/i,
        'repeat': /^(tekrarla|tekrar söyle|ne)$/i
      },
      'no': {
        'clear': /^(tøm|tilbakestill|ny chat|start på nytt)$/i,
        'help': /^(hjelp|hva kan du gjøre|kommandoer)$/i,
        'stop': /^(stopp|avbryt|ikke noe)$/i,
        'repeat': /^(gjenta|si igjen|hva)$/i
      }
    };
    return commands[language] || commands['en'];
  }, []);

  // Get best voice for current language
  const getBestVoice = useCallback((language) => {
    if (!availableVoices.length) return null;
    
    const langCode = getLanguageCode(language);
    const primaryLang = langCode.split('-')[0];
    
    // Try to find exact match first
    let voice = availableVoices.find(v => v.lang === langCode);
    
    // Fallback to language family match
    if (!voice) {
      voice = availableVoices.find(v => v.lang.startsWith(primaryLang));
    }
    
    // Fallback to default voice
    if (!voice) {
      voice = availableVoices.find(v => v.default) || availableVoices[0];
    }
    
    return voice;
  }, [availableVoices, getLanguageCode]);

  // Load available voices
  useEffect(() => {
    const loadVoices = () => {
      if (speechSynthesisRef.current) {
        const voices = speechSynthesisRef.current.getVoices();
        setAvailableVoices(voices);
      }
    };

    loadVoices();
    
    // Some browsers load voices asynchronously
    if (speechSynthesisRef.current) {
      speechSynthesisRef.current.onvoiceschanged = loadVoices;
    }
  }, []);

  // Initialize speech recognition and synthesis
  useEffect(() => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    const speechSynthesis = window.speechSynthesis;
    
    if (SpeechRecognition && speechSynthesis) {
      setIsSupported(true);
      speechSynthesisRef.current = speechSynthesis;
      
      // Workaround for Chrome speech synthesis bug
      // Resume speech synthesis if it gets paused unexpectedly
      const resumeSpeechSynthesis = () => {
        if (speechSynthesis.paused && speechSynthesis.speaking) {
          console.log('VoiceInterface: Resuming paused speech synthesis');
          speechSynthesis.resume();
        }
      };
      
      // Set up interval to check for paused speech
      const resumeInterval = setInterval(resumeSpeechSynthesis, 1000);
      
      // Prevent React development mode from interfering with speech
      const protectSpeech = () => {
        if (currentUtteranceRef.current && speechSynthesis.speaking) {
          // Don't let React interrupt ongoing speech
          return;
        }
      };
      
      // Monitor for React interference
      const protectionInterval = setInterval(protectSpeech, 100);
      
      const recognition = new SpeechRecognition();
      recognition.continuous = false;
      recognition.interimResults = false;
      recognition.maxAlternatives = 1;
      recognition.lang = getLanguageCode(currentLanguage);
      
      recognition.onstart = () => {
        setIsListening(true);
        setError(null);
      };
      
      recognition.onresult = (event) => {
        const transcript = event.results[0][0].transcript.trim();
        setIsProcessing(true);
        
        // Check for voice commands first
        const commands = getVoiceCommands(currentLanguage);
        let commandHandled = false;
        
        for (const [command, pattern] of Object.entries(commands)) {
          if (pattern.test(transcript)) {
            if (onVoiceCommand) {
              onVoiceCommand(command, transcript);
              commandHandled = true;
              break;
            }
          }
        }
        
        // If not a command, pass to speech result handler
        if (!commandHandled && onSpeechResult) {
          onSpeechResult(transcript);
        }
        
        setTimeout(() => {
          setIsProcessing(false);
        }, 500);
      };
      
      recognition.onerror = (event) => {
        setIsListening(false);
        setIsProcessing(false);
        
        let errorMessage;
        let shouldShowError = true;
        
        switch (event.error) {
          case 'not-allowed':
            errorMessage = t('aiAssistant.voice.microphonePermissionDenied');
            setHasPermission(false);
            break;
          case 'no-speech':
            // Don't show error for no-speech - it's often normal behavior
            shouldShowError = false;
            break;
          case 'aborted':
            // Don't show error for aborted - user intentionally stopped
            shouldShowError = false;
            break;
          case 'network':
            errorMessage = 'Network error occurred during speech recognition.';
            break;
          case 'language-not-supported':
            errorMessage = `Language ${getLanguageCode(currentLanguage)} not supported. Falling back to English.`;
            // Fallback to English
            recognition.lang = 'en-US';
            break;
          default:
            // Only show error for actual problematic errors
            if (event.error !== 'no-speech' && event.error !== 'aborted') {
              errorMessage = t('aiAssistant.voice.speechRecognitionError');
            } else {
              shouldShowError = false;
            }
        }
        
        if (shouldShowError && errorMessage) {
          setError(errorMessage);
          if (onSpeechError) {
            onSpeechError(new Error(errorMessage));
          }
        }
      };
      
      recognition.onend = () => {
        setIsListening(false);
      };
      
      recognitionRef.current = recognition;
      
      return () => {
        clearInterval(resumeInterval);
        clearInterval(protectionInterval);
        if (recognitionRef.current && recognitionRef.current.abort) {
          recognitionRef.current.abort();
        }
        if (currentUtteranceRef.current && speechSynthesisRef.current) {
          speechSynthesisRef.current.cancel();
        }
      };
    } else {
      setIsSupported(false);
      setError(t('aiAssistant.voice.voiceNotSupported'));
    }
  }, [currentLanguage, getLanguageCode, onSpeechResult, onSpeechError, onVoiceCommand, getVoiceCommands, t]);

  // Request microphone permission
  const requestMicrophonePermission = useCallback(async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      stream.getTracks().forEach(track => track.stop());
      setHasPermission(true);
      return true;
    } catch (error) {
      setHasPermission(false);
      setError(t('aiAssistant.voice.microphonePermissionDenied'));
      return false;
    }
  }, [t]);

  // Start listening
  const startListening = useCallback(async () => {
    if (!isSupported || !recognitionRef.current || isListening) return;
    
    // Check/request permission first
    if (hasPermission === null) {
      const granted = await requestMicrophonePermission();
      if (!granted) return;
    } else if (hasPermission === false) {
      setError(t('aiAssistant.voice.microphonePermissionDenied'));
      return;
    }
    
    try {
      // Update language before starting
      recognitionRef.current.lang = getLanguageCode(currentLanguage);
      recognitionRef.current.start();
    } catch (error) {
      setError(t('aiAssistant.voice.speechRecognitionError'));
      if (onSpeechError) {
        onSpeechError(error);
      }
    }
  }, [isSupported, isListening, hasPermission, requestMicrophonePermission, getLanguageCode, currentLanguage, t, onSpeechError]);

  // Stop listening
  const stopListening = useCallback(() => {
    if (recognitionRef.current && isListening) {
      recognitionRef.current.stop();
    }
  }, [isListening]);

  // Speak text with language-specific voice using global manager
  const speakText = useCallback((text) => {
    console.log('VoiceInterface: Starting speech via global manager:', text.substring(0, 50) + '...');
    
    // Set up callbacks for state management
    speechManager.setCallbacks({
      onStart: () => {
        console.log('VoiceInterface: Speech started via global manager');
        setIsSpeaking(true);
      },
      onEnd: () => {
        console.log('VoiceInterface: Speech ended via global manager');
        setIsSpeaking(false);
      },
      onError: (error) => {
        console.log('VoiceInterface: Speech error via global manager:', error);
        if (error !== 'interrupted') {
          console.error('VoiceInterface: Non-interrupted speech error:', error);
        }
        setIsSpeaking(false);
      }
    });
    
    // Use global speech manager
    speechManager.speak(text, {
      language: currentLanguage,
      rate: currentLanguage === 'ar' ? 0.7 : 0.8,
      pitch: 1,
      volume: 0.9
    }).then((started) => {
      if (started) {
        console.log('VoiceInterface: Speech successfully started via global manager');
      } else {
        console.log('VoiceInterface: Speech was interrupted via global manager');
      }
    }).catch((error) => {
      console.error('VoiceInterface: Failed to start speech via global manager:', error);
      setIsSpeaking(false);
    });
  }, [currentLanguage]);

  // Stop speaking using global manager
  const stopSpeaking = useCallback(() => {
    console.log('VoiceInterface: Stopping speech via global manager');
    speechManager.cancel();
    setIsSpeaking(false);
  }, []);

  // Auto-speak functionality (exposed for parent components)
  const handleAutoSpeak = useCallback((text) => {
    if (autoSpeak && isEnabled && text) {
      speakText(text);
    }
  }, [autoSpeak, isEnabled, speakText]);

  // Expose methods to parent component via ref
  React.useImperativeHandle(ref, () => ({
    speakText,
    stopSpeaking,
    handleAutoSpeak,
    isListening,
    isSpeaking: speechManager.isSpeaking(),
    startListening,
    stopListening
  }), [speakText, stopSpeaking, handleAutoSpeak, isListening, startListening, stopListening]);

  if (!isEnabled) return null;

  return (
    <div className={`voice-interface ${className}`}>
      {/* Voice Input Button */}
      <div className="flex items-center space-x-2">
        {isSupported ? (
          <>
            <button
              onClick={isListening ? stopListening : startListening}
              disabled={isProcessing}
              className={`p-2 rounded-full transition-all duration-200 ${
                isListening 
                  ? 'bg-red-500 hover:bg-red-600 text-white animate-pulse' 
                  : 'bg-gray-100 hover:bg-gray-200 text-gray-600'
              } ${isProcessing ? 'opacity-50 cursor-not-allowed' : ''}`}
              title={isListening ? t('aiAssistant.voice.stopListening') : t('aiAssistant.voice.startListening')}
            >
              {isProcessing ? (
                <svg className="w-5 h-5 animate-spin" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                </svg>
              ) : isListening ? (
                <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M7 4a3 3 0 016 0v4a3 3 0 11-6 0V4zm4 10.93A7.001 7.001 0 0017 8a1 1 0 10-2 0A5 5 0 015 8a1 1 0 00-2 0 7.001 7.001 0 006 6.93V17H6a1 1 0 100 2h8a1 1 0 100-2h-3v-2.07z" clipRule="evenodd" />
                </svg>
              ) : (
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
                </svg>
              )}
            </button>

            {/* Voice status indicator */}
            {(isListening || isProcessing) && (
              <div className="flex items-center space-x-2 text-sm">
                <div className="flex space-x-1">
                  <div className="w-1 h-4 bg-blue-500 rounded animate-pulse"></div>
                  <div className="w-1 h-6 bg-blue-500 rounded animate-pulse" style={{ animationDelay: '0.1s' }}></div>
                  <div className="w-1 h-4 bg-blue-500 rounded animate-pulse" style={{ animationDelay: '0.2s' }}></div>
                </div>
                <span className="text-gray-600">
                  {isProcessing ? t('aiAssistant.voice.processing') : t('aiAssistant.voice.listening')}
                </span>
              </div>
            )}
          </>
        ) : (
          <div className="text-sm text-gray-500" title={t('aiAssistant.voice.voiceNotSupported')}>
            <svg className="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M18.364 18.364A9 9 0 005.636 5.636m12.728 12.728L5.636 5.636m12.728 12.728L18.364 5.636M5.636 18.364l12.728-12.728" />
            </svg>
          </div>
        )}
      </div>

      {/* Error display */}
      {error && (
        <div className="mt-2 text-xs text-red-600 bg-red-50 px-2 py-1 rounded">
          {error}
        </div>
      )}
    </div>
  );
});

VoiceInterface.displayName = 'VoiceInterface';

// Higher-order component for voice-enabled text responses
export const withVoiceResponse = (WrappedComponent) => {
  return React.forwardRef((props, ref) => {
    const voiceInterfaceRef = useRef(null);
    
    const speakResponse = useCallback((text) => {
      if (voiceInterfaceRef.current?.speakText) {
        voiceInterfaceRef.current.speakText(text);
      }
    }, []);
    
    const stopSpeaking = useCallback(() => {
      if (voiceInterfaceRef.current?.stopSpeaking) {
        voiceInterfaceRef.current.stopSpeaking();
      }
    }, []);
    
    return (
      <WrappedComponent
        {...props}
        ref={ref}
        voiceInterfaceRef={voiceInterfaceRef}
        speakResponse={speakResponse}
        stopSpeaking={stopSpeaking}
      />
    );
  });
};

export default VoiceInterface;