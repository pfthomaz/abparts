// frontend/src/components/ChatWidget.js

import React, { useState, useRef, useEffect } from 'react';
import { useAuth } from '../AuthContext';
import { useTranslation } from '../hooks/useTranslation';
import { useLocalization } from '../contexts/LocalizationContext';
import VoiceInterface from './VoiceInterface';
import { machinesService } from '../services/machinesService';

const ChatWidget = ({ isOpen, onToggle }) => {
  const { t } = useTranslation();
  const { user } = useAuth();
  const { currentLanguage, isRTL } = useLocalization();
  
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isMinimized, setIsMinimized] = useState(false);
  const [selectedMachine, setSelectedMachine] = useState(null);
  const [availableMachines, setAvailableMachines] = useState([]);
  const [showMachineSelector, setShowMachineSelector] = useState(false);
  const [isLoadingMachines, setIsLoadingMachines] = useState(false);
  const [voiceEnabled, setVoiceEnabled] = useState(true);
  const [autoSpeak, setAutoSpeak] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);
  const voiceInterfaceRef = useRef(null);

  // Auto-scroll to bottom when new messages are added
  const scrollToBottom = () => {
    if (messagesEndRef.current && typeof messagesEndRef.current.scrollIntoView === 'function') {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Focus input when chat opens
  useEffect(() => {
    if (isOpen && !isMinimized && inputRef.current) {
      inputRef.current.focus();
    }
  }, [isOpen, isMinimized]);

  // Initialize with welcome message
  useEffect(() => {
    if (isOpen && messages.length === 0) {
      const welcomeMessage = {
        id: Date.now(),
        sender: 'assistant',
        content: t('aiAssistant.messages.welcomeMessage'),
        timestamp: new Date(),
        type: 'text'
      };
      setMessages([welcomeMessage]);
      
      // Load available machines when chat opens
      loadAvailableMachines();
    }
  }, [isOpen, messages.length, t]);

  // Load available machines for the user
  const loadAvailableMachines = async () => {
    if (!user?.id) return;
    
    setIsLoadingMachines(true);
    try {
      // Use the existing ABParts machines service
      const response = await machinesService.getMachines();
      // Handle both response.data and direct array response
      const machinesData = Array.isArray(response) ? response : (response.data || []);
      setAvailableMachines(machinesData);
    } catch (error) {
      console.error('ChatWidget: Error loading machines:', error);
      setAvailableMachines([]);
    } finally {
      setIsLoadingMachines(false);
    }
  };

  const handleMachineSelect = (machine) => {
    setSelectedMachine(machine);
    setShowMachineSelector(false);
    
    // Add a system message about machine selection
    const machineMessage = {
      id: Date.now(),
      sender: 'system',
      content: t('aiAssistant.messages.machineSelected', { 
        machineName: machine.name, 
        modelType: machine.model_type 
      }),
      timestamp: new Date(),
      type: 'info'
    };
    setMessages(prev => [...prev, machineMessage]);
  };

  const handleClearMachine = () => {
    setSelectedMachine(null);
    
    // Add a system message about machine clearing
    const clearMessage = {
      id: Date.now(),
      sender: 'system',
      content: t('aiAssistant.messages.machineCleared'),
      timestamp: new Date(),
      type: 'info'
    };
    setMessages(prev => [...prev, clearMessage]);
  };

  // Voice input handlers
  const handleSpeechResult = (transcript) => {
    setInputMessage(transcript);
    // Auto-focus the input field after speech recognition
    if (inputRef.current) {
      inputRef.current.focus();
    }
  };

  const handleSpeechError = (error) => {
    console.error('Speech recognition error:', error);
    // Error is already handled by VoiceInterface component
  };

  const handleVoiceCommand = (command, transcript) => {
    switch (command) {
      case 'clear':
        setMessages([]);
        setSelectedMachine(null);
        // Add welcome message after clearing
        setTimeout(() => {
          const welcomeMessage = {
            id: Date.now(),
            sender: 'assistant',
            content: t('aiAssistant.messages.welcomeMessage'),
            timestamp: new Date(),
            type: 'text'
          };
          setMessages([welcomeMessage]);
        }, 100);
        break;
      case 'help':
        const helpMessage = {
          id: Date.now(),
          sender: 'assistant',
          content: t('aiAssistant.messages.welcomeMessage'),
          timestamp: new Date(),
          type: 'text'
        };
        setMessages(prev => [...prev, helpMessage]);
        break;
      case 'stop':
        stopSpeaking();
        break;
      case 'repeat':
        if (messages.length > 0) {
          const lastAssistantMessage = messages
            .slice()
            .reverse()
            .find(msg => msg.sender === 'assistant' && msg.type === 'text');
          if (lastAssistantMessage) {
            speakResponse(lastAssistantMessage.content);
          }
        }
        break;
      default:
        // If command not recognized, treat as regular input
        handleSpeechResult(transcript);
    }
  };

  const speakResponse = (text) => {
    if (voiceInterfaceRef.current?.speakText) {
      voiceInterfaceRef.current.speakText(text);
    }
  };

  const stopSpeaking = () => {
    if (voiceInterfaceRef.current?.stopSpeaking) {
      voiceInterfaceRef.current.stopSpeaking();
    }
  };

  // Listen for speaking state changes from VoiceInterface
  useEffect(() => {
    const checkSpeakingState = () => {
      if (voiceInterfaceRef.current?.isSpeaking !== undefined) {
        const currentSpeakingState = voiceInterfaceRef.current.isSpeaking;
        setIsSpeaking(prevState => {
          // Only update if state actually changed to avoid unnecessary re-renders
          return prevState !== currentSpeakingState ? currentSpeakingState : prevState;
        });
      }
    };
    
    // Reduced frequency to avoid interference with speech synthesis
    const interval = setInterval(checkSpeakingState, 500);
    return () => clearInterval(interval);
  }, []);

  // Auto-speak assistant responses if enabled
  useEffect(() => {
    if (autoSpeak && messages.length > 0) {
      const lastMessage = messages[messages.length - 1];
      if (lastMessage.sender === 'assistant' && lastMessage.type === 'text') {
        // Use a longer delay and ensure we're not in a re-render cycle
        const timeoutId = setTimeout(() => {
          // Double-check that auto-speak is still enabled and component is still mounted
          if (autoSpeak && voiceInterfaceRef.current) {
            console.log('ChatWidget: Triggering auto-speak for message:', lastMessage.content.substring(0, 50) + '...');
            speakResponse(lastMessage.content);
          }
        }, 2000); // Even longer delay to ensure all React updates are complete
        
        return () => {
          console.log('ChatWidget: Clearing auto-speak timeout');
          clearTimeout(timeoutId);
        };
      }
    }
  }, [messages, autoSpeak]);

  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (!inputMessage.trim() || isLoading) return;

    const userMessage = {
      id: Date.now(),
      sender: 'user',
      content: inputMessage.trim(),
      timestamp: new Date(),
      type: 'text'
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsLoading(true);

    // Prepare request payload
    const requestPayload = {
      message: userMessage.content,
      user_id: user?.id,
      machine_id: selectedMachine?.id || null,
      language: currentLanguage, // Use current language from localization context
      conversation_history: messages.map(msg => ({
        role: msg.sender === 'user' ? 'user' : 'assistant',
        content: msg.content,
        timestamp: msg.timestamp.getTime() / 1000
      }))
    };

    try {

      // Get auth token
      const token = localStorage.getItem('token');
      
      const apiUrl = `${process.env.REACT_APP_AI_ASSISTANT_URL || 'http://localhost:8001'}/api/ai/chat`;
      console.log('AI Assistant API URL:', apiUrl);
      console.log('Request payload:', requestPayload);
      
      // Call AI Assistant API
      const response = await fetch(apiUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(token && { 'Authorization': `Bearer ${token}` })
        },
        body: JSON.stringify(requestPayload)
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      
      const assistantMessage = {
        id: Date.now() + 1,
        sender: 'assistant',
        content: data.response,
        timestamp: new Date(),
        type: 'text'
      };
      
      setMessages(prev => [...prev, assistantMessage]);
      setIsLoading(false);
      
      // Auto-speak is handled by the useEffect that watches messages array
      // No need for duplicate speech call here
      
    } catch (error) {
      console.error('Error sending message:', error);
      console.error('Request details:', {
        url: `${process.env.REACT_APP_AI_ASSISTANT_URL || 'http://localhost:8001'}/api/ai/chat`,
        payload: requestPayload,
        error: error.message
      });
      const errorMessage = {
        id: Date.now() + 1,
        sender: 'system',
        content: t('aiAssistant.errors.connectionError'),
        timestamp: new Date(),
        type: 'error'
      };
      setMessages(prev => [...prev, errorMessage]);
      setIsLoading(false);
    }
  };

  const handleMinimize = () => {
    setIsMinimized(!isMinimized);
  };

  const handleClose = () => {
    onToggle();
  };

  const formatTime = (timestamp) => {
    return new Date(timestamp).toLocaleTimeString(currentLanguage, {
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  if (!isOpen) return null;

  return (
    <div className="fixed left-4 z-50" style={{ bottom: '6.5rem' }}>
      {/* Chat Window */}
      <div className={`bg-white rounded-lg shadow-2xl border border-gray-200 transition-all duration-300 ${
        isMinimized ? 'h-14 w-80 sm:w-96 md:w-[28rem]' : 'w-80 sm:w-96 md:w-[28rem]'
      }`}
      style={{
        height: isMinimized ? '3.5rem' : 'min(32rem, calc(100vh - 13rem))',
        maxHeight: 'calc(100vh - 13rem)'
      }}>
        {/* Header */}
        <div className="flex items-center justify-between p-4 bg-blue-600 text-white rounded-t-lg">
          <div className="flex items-center space-x-2">
            <div className="w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center">
              <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M18 10c0 3.866-3.582 7-8 7a8.841 8.841 0 01-4.083-.98L2 17l1.338-3.123C2.493 12.767 2 11.434 2 10c0-3.866 3.582-7 8-7s8 3.134 8 7zM7 9H5v2h2V9zm8 0h-2v2h2V9zM9 9h2v2H9V9z" clipRule="evenodd" />
              </svg>
            </div>
            <div>
              <h3 className="font-semibold text-sm">{t('aiAssistant.title')}</h3>
              <p className="text-xs text-blue-100">
                {selectedMachine ? 
                  `${selectedMachine.name} (${selectedMachine.model_type})` : 
                  t('aiAssistant.subtitle')
                }
              </p>
            </div>
          </div>
          <div className="flex items-center space-x-1">
            {/* Voice settings button */}
            <button
              onClick={() => setAutoSpeak(!autoSpeak)}
              className={`p-1 rounded transition-colors ${
                autoSpeak 
                  ? 'bg-green-500 hover:bg-green-600 text-white' 
                  : 'bg-red-500 hover:bg-red-600 text-white'
              }`}
              title={autoSpeak ? t('aiAssistant.voice.disableVoice') : t('aiAssistant.voice.enableVoice')}
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                {autoSpeak ? (
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15.536 8.464a5 5 0 010 7.072m2.828-9.9a9 9 0 010 14.142M8.5 6.5v11m-3-5.5h7" />
                ) : (
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5.586 15H4a1 1 0 01-1-1v-4a1 1 0 011-1h1.586l4.707-4.707C10.923 3.663 12 4.109 12 5v14c0 .891-1.077 1.337-1.707.707L5.586 15z M17 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2" />
                )}
              </svg>
            </button>
            {/* Stop speaking button - only show when speaking */}
            {isSpeaking && (
              <button
                onClick={stopSpeaking}
                className="p-1 hover:bg-blue-700 rounded transition-colors text-red-200"
                title={t('aiAssistant.voice.stopSpeaking')}
              >
                <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8 7a1 1 0 00-1 1v4a1 1 0 001 1h4a1 1 0 001-1V8a1 1 0 00-1-1H8z" clipRule="evenodd" />
                </svg>
              </button>
            )}
            {/* Machine selector button */}
            <button
              onClick={() => setShowMachineSelector(!showMachineSelector)}
              className="p-1 hover:bg-blue-700 rounded transition-colors"
              title={t('aiAssistant.selectMachine')}
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
              </svg>
            </button>
            <button
              onClick={handleMinimize}
              className="p-1 hover:bg-blue-700 rounded transition-colors"
              title={isMinimized ? t('aiAssistant.chatWidget.maximize') : t('aiAssistant.chatWidget.minimize')}
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                {isMinimized ? (
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 15l7-7 7 7" />
                ) : (
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                )}
              </svg>
            </button>
            <button
              onClick={handleClose}
              className="p-1 hover:bg-blue-700 rounded transition-colors"
              title={t('common.close')}
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>

        {/* Machine Selector Dropdown */}
        {!isMinimized && showMachineSelector && (
          <div className="bg-white border-b border-gray-200 p-3">
            <div className="mb-2 flex items-center justify-between">
              <h4 className="text-sm font-medium text-gray-700">{t('aiAssistant.selectMachine')}</h4>
              {selectedMachine && (
                <button
                  onClick={handleClearMachine}
                  className="text-xs text-red-600 hover:text-red-800"
                >
                  {t('aiAssistant.clearMachine')}
                </button>
              )}
            </div>
            
            {isLoadingMachines ? (
              <div className="text-sm text-gray-500">{t('common.loading')}</div>
            ) : availableMachines.length === 0 ? (
              <div className="text-sm text-gray-500">{t('aiAssistant.noMachines')}</div>
            ) : (
              <div className="space-y-1 max-h-32 overflow-y-auto">
                {availableMachines.map((machine) => (
                  <button
                    key={machine.id}
                    onClick={() => handleMachineSelect(machine)}
                    className={`w-full text-left p-2 rounded text-sm transition-colors ${
                      selectedMachine?.id === machine.id
                        ? 'bg-blue-100 text-blue-800 border border-blue-200'
                        : 'hover:bg-gray-100 text-gray-700'
                    }`}
                  >
                    <div className="font-medium">{machine.name}</div>
                    <div className="text-xs text-gray-500">
                      {machine.model_type} • {machine.latest_hours || 0}h • {machine.customer_organization_name || 'Unknown Org'}
                    </div>
                  </button>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Chat Content - Hidden when minimized */}
        {!isMinimized && (
          <div className="flex flex-col h-full">
            {/* Messages Area */}
            <div className="flex-1 p-4 overflow-y-auto bg-gray-50 min-h-0">
              <div className="space-y-3">
                {messages.map((message) => (
                  <div
                    key={message.id}
                    className={`flex ${message.sender === 'user' ? 
                      (isRTL() ? 'justify-start' : 'justify-end') : 
                      (isRTL() ? 'justify-end' : 'justify-start')
                    }`}
                  >
                    <div
                      className={`max-w-xs lg:max-w-md px-3 py-2 rounded-lg text-sm ${
                        message.sender === 'user'
                          ? 'bg-blue-600 text-white'
                          : message.sender === 'system' && message.type === 'info'
                          ? 'bg-green-100 text-green-800 border border-green-200'
                          : message.sender === 'system'
                          ? 'bg-red-100 text-red-800 border border-red-200'
                          : 'bg-white text-gray-800 border border-gray-200'
                      }`}
                    >
                      <p className="break-words">{message.content}</p>
                      <div className={`flex items-center justify-between mt-1 ${
                        message.sender === 'user' ? 'text-blue-100' : 'text-gray-500'
                      }`}>
                        <p className="text-xs">
                          {formatTime(message.timestamp)}
                        </p>
                        {/* Speak button for assistant messages */}
                        {message.sender === 'assistant' && message.type === 'text' && (
                          <button
                            onClick={() => speakResponse(message.content)}
                            className={`ml-2 p-1 rounded hover:bg-opacity-20 hover:bg-gray-500 transition-colors ${
                              message.sender === 'user' ? 'text-blue-100' : 'text-gray-400 hover:text-gray-600'
                            }`}
                            title={t('aiAssistant.voice.speakResponse')}
                          >
                            <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15.536 8.464a5 5 0 010 7.072m2.828-9.9a9 9 0 010 14.142M8.5 6.5v11m-3-5.5h7" />
                            </svg>
                          </button>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
                
                {/* Loading indicator */}
                {isLoading && (
                  <div className={`flex ${isRTL() ? 'justify-end' : 'justify-start'}`}>
                    <div className="bg-white text-gray-800 border border-gray-200 px-3 py-2 rounded-lg">
                      <div className="flex items-center space-x-2">
                        <div className="flex space-x-1">
                          <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                          <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                          <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                        </div>
                        <span className="text-xs text-gray-500">{t('aiAssistant.chatWidget.typing')}</span>
                      </div>
                    </div>
                  </div>
                )}
              </div>
              <div ref={messagesEndRef} />
            </div>

            {/* Input Area */}
            <div className="flex-shrink-0 p-4 border-t border-gray-200 bg-white rounded-b-lg">
              <form onSubmit={handleSendMessage} className="flex space-x-2">
                <div className="flex-1 flex space-x-2">
                  <input
                    ref={inputRef}
                    type="text"
                    value={inputMessage}
                    onChange={(e) => setInputMessage(e.target.value)}
                    placeholder={t('aiAssistant.messages.placeholder')}
                    className={`flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm ${
                      isRTL() ? 'text-right' : 'text-left'
                    }`}
                    disabled={isLoading}
                    dir={isRTL() ? 'rtl' : 'ltr'}
                  />
                  {/* Voice Interface */}
                  <VoiceInterface
                    ref={voiceInterfaceRef}
                    onSpeechResult={handleSpeechResult}
                    onSpeechError={handleSpeechError}
                    onVoiceCommand={handleVoiceCommand}
                    isEnabled={voiceEnabled}
                    autoSpeak={autoSpeak}
                    className="flex-shrink-0"
                  />
                </div>
                <button
                  type="submit"
                  disabled={!inputMessage.trim() || isLoading}
                  className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                >
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
                  </svg>
                </button>
              </form>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default ChatWidget;