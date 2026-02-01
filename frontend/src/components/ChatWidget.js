// frontend/src/components/ChatWidget.js

import React, { useState, useRef, useEffect, useCallback } from 'react';
import { useAuth } from '../AuthContext';
import { useTranslation } from '../hooks/useTranslation';
import { useLocalization } from '../contexts/LocalizationContext';
import { usePWA } from '../contexts/PWAContext';
import VoiceInterface from './VoiceInterface';
import EscalationModal from './EscalationModal';
import { machinesService } from '../services/machinesService';

const ChatWidget = ({ isOpen, onToggle }) => {
  const { t } = useTranslation();
  const { user } = useAuth();
  const { currentLanguage, isRTL } = useLocalization();
  const { isOnline, queueMessage, messageQueue, connectionQuality, showNotification } = usePWA();
  
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
  const [showEscalationModal, setShowEscalationModal] = useState(false);
  const [currentSessionId, setCurrentSessionId] = useState(null);
  const [confidenceScore, setConfidenceScore] = useState(null);
  
  // Troubleshooting mode state
  const [troubleshootingMode, setTroubleshootingMode] = useState(false);
  const [currentStepId, setCurrentStepId] = useState(null);
  const [awaitingFeedback, setAwaitingFeedback] = useState(false);
  const [currentStepData, setCurrentStepData] = useState(null);
  
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);
  const voiceInterfaceRef = useRef(null);
  const chatWidgetRef = useRef(null);
  
  // Mobile-specific state
  const [isMobile, setIsMobile] = useState(false);
  const [isFullScreen, setIsFullScreen] = useState(false);
  const [touchStart, setTouchStart] = useState(null);
  const [touchEnd, setTouchEnd] = useState(null);
  
  // Minimum swipe distance (in px) to trigger actions
  const minSwipeDistance = 50;

  // Auto-scroll to bottom when new messages are added
  const scrollToBottom = () => {
    if (messagesEndRef.current && typeof messagesEndRef.current.scrollIntoView === 'function') {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);
  
  // Handle queued messages when coming back online
  useEffect(() => {
    const handleProcessQueue = async (event) => {
      const { messages: queuedMessages } = event.detail;
      
      if (queuedMessages && queuedMessages.length > 0 && isOnline) {
        console.log('[ChatWidget] Processing queued messages:', queuedMessages.length);
        
        // Process each queued message
        for (const queuedMsg of queuedMessages) {
          try {
            await sendQueuedMessage(queuedMsg);
          } catch (error) {
            console.error('[ChatWidget] Error sending queued message:', error);
          }
        }
      }
    };
    
    window.addEventListener('pwa-process-queue', handleProcessQueue);
    return () => window.removeEventListener('pwa-process-queue', handleProcessQueue);
  }, [isOnline]);
  
  // Send a queued message
  const sendQueuedMessage = async (queuedMsg) => {
    try {
      const token = localStorage.getItem('token');
      const baseUrl = process.env.NODE_ENV === 'production' 
        ? '/ai'
        : (process.env.REACT_APP_AI_ASSISTANT_URL || 'http://localhost:8001');
      
      const response = await fetch(`${baseUrl}/api/ai/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(token && { 'Authorization': `Bearer ${token}` })
        },
        body: JSON.stringify(queuedMsg.payload)
      });

      if (response.ok) {
        const data = await response.json();
        
        // Add assistant response
        const assistantMessage = {
          id: Date.now() + 1,
          sender: 'assistant',
          content: data.response,
          timestamp: new Date(),
          type: 'text'
        };
        
        setMessages(prev => [...prev, assistantMessage]);
        
        // Show notification if app is in background
        if (document.hidden) {
          showNotification(t('aiAssistant.notifications.newMessage'), {
            body: data.response.substring(0, 100) + '...',
            tag: 'ai-message'
          });
        }
      }
    } catch (error) {
      console.error('[ChatWidget] Error sending queued message:', error);
    }
  };
  
  // Detect mobile device and screen size
  useEffect(() => {
    const checkMobile = () => {
      const isMobileDevice = window.innerWidth < 768; // Tailwind md breakpoint
      setIsMobile(isMobileDevice);
      
      // Auto full-screen on very small devices
      if (window.innerWidth < 640 && isOpen && !isMinimized) {
        setIsFullScreen(true);
      }
    };
    
    checkMobile();
    window.addEventListener('resize', checkMobile);
    
    return () => window.removeEventListener('resize', checkMobile);
  }, [isOpen, isMinimized]);
  
  // Touch gesture handlers for swipe to minimize/close
  const onTouchStart = useCallback((e) => {
    setTouchEnd(null);
    setTouchStart(e.targetTouches[0].clientY);
  }, []);
  
  const onTouchMove = useCallback((e) => {
    setTouchEnd(e.targetTouches[0].clientY);
  }, []);
  
  const onTouchEnd = useCallback(() => {
    if (!touchStart || !touchEnd) return;
    
    const distance = touchStart - touchEnd;
    const isDownSwipe = distance < -minSwipeDistance;
    const isUpSwipe = distance > minSwipeDistance;
    
    // Swipe down to minimize
    if (isDownSwipe && !isMinimized) {
      handleMinimize();
    }
    
    // Swipe up to maximize when minimized
    if (isUpSwipe && isMinimized) {
      handleMinimize();
    }
    
    // Reset touch state
    setTouchStart(null);
    setTouchEnd(null);
  }, [touchStart, touchEnd, isMinimized]);
  
  // Prevent body scroll when chat is open on mobile
  useEffect(() => {
    if (isMobile && isOpen && !isMinimized) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = '';
    }
    
    return () => {
      document.body.style.overflow = '';
    };
  }, [isMobile, isOpen, isMinimized]);

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

  // Escalation handlers
  const handleEscalateSession = async (escalationData) => {
    try {
      const token = localStorage.getItem('token');
      
      // In production, use the nginx proxy path; in development, use the environment variable
      const baseUrl = process.env.NODE_ENV === 'production' 
        ? '/ai' // Use nginx proxy path in production
        : (process.env.REACT_APP_AI_ASSISTANT_URL || 'http://localhost:8001');
      
      const apiUrl = `${baseUrl}/api/ai/sessions/${currentSessionId}/escalate`;
      
      const response = await fetch(apiUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(token && { 'Authorization': `Bearer ${token}` })
        },
        body: JSON.stringify(escalationData)
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      
      // Add escalation confirmation message
      const escalationMessage = {
        id: Date.now(),
        sender: 'system',
        content: t('aiAssistant.messages.escalationCreated', { 
          ticketNumber: data.ticket_number 
        }),
        timestamp: new Date(),
        type: 'escalation',
        ticketInfo: data
      };
      
      setMessages(prev => [...prev, escalationMessage]);
      
      // Show expert contact information if available
      if (data.expert_contact_info) {
        const contactMessage = {
          id: Date.now() + 1,
          sender: 'assistant',
          content: t('aiAssistant.messages.expertContact', {
            contactName: data.expert_contact_info.primary_contact?.name,
            contactPhone: data.expert_contact_info.primary_contact?.phone,
            contactEmail: data.expert_contact_info.primary_contact?.email
          }),
          timestamp: new Date(),
          type: 'contact'
        };
        
        setMessages(prev => [...prev, contactMessage]);
      }
      
    } catch (error) {
      console.error('Error escalating session:', error);
      
      // Add error message
      const errorMessage = {
        id: Date.now(),
        sender: 'system',
        content: t('aiAssistant.messages.escalationError'),
        timestamp: new Date(),
        type: 'error'
      };
      
      setMessages(prev => [...prev, errorMessage]);
    }
  };

  const handleShowEscalation = () => {
    setShowEscalationModal(true);
  };

  // Step feedback handler
  const handleStepFeedback = async (feedback) => {
    if (!currentStepId || !currentSessionId) {
      console.error('Missing step ID or session ID for feedback');
      return;
    }

    setAwaitingFeedback(false);
    setIsLoading(true);

    // Add user feedback message
    const feedbackMessage = {
      id: Date.now(),
      sender: 'user',
      content: feedback === 'worked' 
        ? t('aiAssistant.feedback.worked')
        : feedback === 'partially_worked'
        ? t('aiAssistant.feedback.partiallyWorked')
        : t('aiAssistant.feedback.didntWork'),
      timestamp: new Date(),
      type: 'feedback'
    };
    setMessages(prev => [...prev, feedbackMessage]);

    try {
      const token = localStorage.getItem('token');
      const baseUrl = process.env.NODE_ENV === 'production' 
        ? '/ai'
        : (process.env.REACT_APP_AI_ASSISTANT_URL || 'http://localhost:8001');
      
      const response = await fetch(`${baseUrl}/api/ai/chat/step-feedback`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(token && { 'Authorization': `Bearer ${token}` })
        },
        body: JSON.stringify({
          session_id: currentSessionId,
          step_id: currentStepId,
          feedback: feedback,
          language: currentLanguage,
          user_id: user?.id
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();

      if (data.workflow_status === 'completed') {
        // Workflow complete
        setTroubleshootingMode(false);
        setCurrentStepId(null);
        setCurrentStepData(null);
        setCurrentSessionId(null); // Clear session when troubleshooting completes
        
        const completionMessage = {
          id: Date.now() + 1,
          sender: 'system',
          content: data.completion_message || t('aiAssistant.troubleshooting.workflowComplete'),
          timestamp: new Date(),
          type: 'completion'
        };
        setMessages(prev => [...prev, completionMessage]);
        
      } else if (data.workflow_status === 'escalated') {
        // Workflow escalated
        setTroubleshootingMode(false);
        setCurrentStepId(null);
        setCurrentStepData(null);
        setCurrentSessionId(null); // Clear session when troubleshooting escalates
        
        const escalationMessage = {
          id: Date.now() + 1,
          sender: 'system',
          content: data.completion_message || t('aiAssistant.troubleshooting.workflowEscalated'),
          timestamp: new Date(),
          type: 'escalation'
        };
        setMessages(prev => [...prev, escalationMessage]);
        
      } else if (data.next_step) {
        // Continue with next step
        const nextStepMessage = {
          id: Date.now() + 1,
          sender: 'assistant',
          content: data.next_step.response,
          timestamp: new Date(),
          type: 'diagnostic_step',
          stepData: data.next_step.step_data
        };
        
        setMessages(prev => [...prev, nextStepMessage]);
        setCurrentStepId(data.next_step.step_data.step_id);
        setCurrentStepData(data.next_step.step_data);
        setAwaitingFeedback(true);
      }

      setIsLoading(false);

    } catch (error) {
      console.error('Error submitting step feedback:', error);
      
      const errorMessage = {
        id: Date.now() + 1,
        sender: 'system',
        content: t('aiAssistant.errors.feedbackError'),
        timestamp: new Date(),
        type: 'error'
      };
      setMessages(prev => [...prev, errorMessage]);
      setIsLoading(false);
      setAwaitingFeedback(true); // Allow retry
    }
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
    
    // Check if offline
    if (!isOnline) {
      // Queue message for later
      const requestPayload = {
        message: userMessage.content,
        user_id: user?.id,
        machine_id: selectedMachine?.id || null,
        language: currentLanguage,
        conversation_history: messages.map(msg => ({
          role: msg.sender === 'user' ? 'user' : 'assistant',
          content: msg.content,
          timestamp: msg.timestamp.getTime() / 1000
        }))
      };
      
      queueMessage({ payload: requestPayload, userMessage });
      
      // Add offline notification message
      const offlineMessage = {
        id: Date.now() + 1,
        sender: 'system',
        content: t('pwa.offline.messageQueued'),
        timestamp: new Date(),
        type: 'info'
      };
      setMessages(prev => [...prev, offlineMessage]);
      return;
    }
    
    setIsLoading(true);

    // Prepare request payload
    const requestPayload = {
      message: userMessage.content,
      session_id: currentSessionId, // Include session_id for troubleshooting continuity
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
      
      // In production, use the nginx proxy path; in development, use the environment variable
      const baseUrl = process.env.NODE_ENV === 'production' 
        ? '/ai' // Use nginx proxy path in production
        : (process.env.REACT_APP_AI_ASSISTANT_URL || 'http://localhost:8001');
      
      const apiUrl = `${baseUrl}/api/ai/chat`;
      console.log('AI Assistant API URL:', apiUrl);
      console.log('Request payload:', requestPayload);
      
      // Add timeout for low-bandwidth connections
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 30000); // 30 second timeout
      
      // Call AI Assistant API
      const response = await fetch(apiUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(token && { 'Authorization': `Bearer ${token}` })
        },
        body: JSON.stringify(requestPayload),
        signal: controller.signal
      });
      
      clearTimeout(timeoutId);

      if (!response.ok) {
        // Check if it's an offline error from service worker
        if (response.status === 503) {
          const errorData = await response.json();
          if (errorData.offline) {
            // Queue the message
            queueMessage({ payload: requestPayload, userMessage });
            
            const offlineMessage = {
              id: Date.now() + 1,
              sender: 'system',
              content: t('pwa.offline.messageQueued'),
              timestamp: new Date(),
              type: 'info'
            };
            setMessages(prev => [...prev, offlineMessage]);
            setIsLoading(false);
            return;
          }
        }
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      
      // Store session ID from response for troubleshooting continuity
      if (data.session_id) {
        setCurrentSessionId(data.session_id);
      }
      
      // Check if this is a troubleshooting step
      if (data.message_type === 'diagnostic_step' && data.step_data) {
        setTroubleshootingMode(true);
        setCurrentStepId(data.step_data.step_id);
        setCurrentStepData(data.step_data);
        setAwaitingFeedback(true);
        
        const assistantMessage = {
          id: Date.now() + 1,
          sender: 'assistant',
          content: data.response,
          timestamp: new Date(),
          type: 'diagnostic_step',
          stepData: data.step_data
        };
        
        setMessages(prev => [...prev, assistantMessage]);
      } else {
        // Regular chat message
        const assistantMessage = {
          id: Date.now() + 1,
          sender: 'assistant',
          content: data.response,
          timestamp: new Date(),
          type: 'text'
        };
        
        setMessages(prev => [...prev, assistantMessage]);
      }
      
      setIsLoading(false);
      
      // Show notification if app is in background
      if (document.hidden) {
        showNotification(t('aiAssistant.notifications.newMessage'), {
          body: data.response.substring(0, 100) + '...',
          tag: 'ai-message'
        });
      }
      
      // Auto-speak is handled by the useEffect that watches messages array
      // No need for duplicate speech call here
      
    } catch (error) {
      console.error('Error sending message:', error);
      
      // Check if it's a timeout or network error
      if (error.name === 'AbortError') {
        const timeoutMessage = {
          id: Date.now() + 1,
          sender: 'system',
          content: t('pwa.connection.timeout'),
          timestamp: new Date(),
          type: 'error'
        };
        setMessages(prev => [...prev, timeoutMessage]);
      } else if (!isOnline || error.message.includes('Failed to fetch')) {
        // Queue the message if offline
        queueMessage({ payload: requestPayload, userMessage });
        
        const offlineMessage = {
          id: Date.now() + 1,
          sender: 'system',
          content: t('pwa.offline.messageQueued'),
          timestamp: new Date(),
          type: 'info'
        };
        setMessages(prev => [...prev, offlineMessage]);
      } else {
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
      }
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

  // Responsive sizing based on device
  const getWidgetStyles = () => {
    if (isMobile) {
      if (isFullScreen && !isMinimized) {
        return {
          width: '100vw',
          height: '100vh',
          maxHeight: '100vh',
          left: 0,
          bottom: 0,
          right: 0,
          top: 0,
          borderRadius: 0
        };
      }
      return {
        width: 'calc(100vw - 1rem)',
        height: isMinimized ? '3.5rem' : 'calc(100vh - 6rem)',
        maxHeight: 'calc(100vh - 6rem)',
        left: '0.5rem',
        right: '0.5rem',
        bottom: 'max(4rem, calc(1rem + env(safe-area-inset-bottom)))'
      };
    }
    
    // Desktop/tablet styles
    return {
      width: 'min(28rem, calc(100vw - 2rem))',
      height: isMinimized ? '3.5rem' : 'min(32rem, calc(100vh - 13rem))',
      maxHeight: 'calc(100vh - 13rem)',
      left: '1rem',
      bottom: 'max(10.5rem, calc(5.5rem + env(safe-area-inset-bottom)))'
    };
  };

  return (
    <div 
      ref={chatWidgetRef}
      className={`fixed z-50 transition-all duration-300 ${
        isFullScreen && isMobile && !isMinimized ? 'inset-0' : ''
      }`}
      style={!isFullScreen || isMinimized ? getWidgetStyles() : undefined}
    >
      {/* Chat Window */}
      <div 
        className={`bg-white shadow-2xl border border-gray-200 transition-all duration-300 h-full ${
          isFullScreen && isMobile && !isMinimized ? 'rounded-none' : 'rounded-lg'
        }`}
        onTouchStart={onTouchStart}
        onTouchMove={onTouchMove}
        onTouchEnd={onTouchEnd}
      >
        {/* Header */}
        <div className="flex items-center justify-between p-3 md:p-4 bg-blue-600 text-white rounded-t-lg touch-manipulation" style={{
          minHeight: isMobile ? '56px' : '48px'
        }}>
          {/* Swipe indicator for mobile */}
          {isMobile && !isMinimized && (
            <div className="absolute top-1 left-1/2 transform -translate-x-1/2 w-12 h-1 bg-blue-400 rounded-full opacity-50"></div>
          )}
          
          <div className="flex items-center space-x-2 flex-1 min-w-0 mr-2">
            <div className="w-7 h-7 md:w-8 md:h-8 bg-blue-500 rounded-full flex items-center justify-center flex-shrink-0">
              <svg className="w-4 h-4 md:w-5 md:h-5" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M18 10c0 3.866-3.582 7-8 7a8.841 8.841 0 01-4.083-.98L2 17l1.338-3.123C2.493 12.767 2 11.434 2 10c0-3.866 3.582-7 8-7s8 3.134 8 7zM7 9H5v2h2V9zm8 0h-2v2h2V9zM9 9h2v2H9V9z" clipRule="evenodd" />
              </svg>
            </div>
            <div className="min-w-0 flex-1">
              <h3 className="font-semibold text-xs md:text-sm truncate">{t('aiAssistant.title')}</h3>
              <p className="text-xs text-blue-100 truncate">
                {selectedMachine ? 
                  `${selectedMachine.name} (${selectedMachine.model_type})` : 
                  t('aiAssistant.subtitle')
                }
              </p>
            </div>
          </div>
          <div className="flex items-center gap-1 flex-shrink-0">
            {/* Voice settings button - larger touch target on mobile */}
            <button
              onClick={() => setAutoSpeak(!autoSpeak)}
              className={`p-2 md:p-1.5 rounded transition-colors touch-manipulation ${
                autoSpeak 
                  ? 'bg-green-500 hover:bg-green-600 text-white' 
                  : 'bg-red-500 hover:bg-red-600 text-white'
              }`}
              style={{ minWidth: isMobile ? '36px' : '32px', minHeight: isMobile ? '36px' : '32px' }}
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
                className="p-2 md:p-1.5 hover:bg-blue-700 rounded transition-colors text-red-200 touch-manipulation"
                style={{ minWidth: isMobile ? '36px' : '32px', minHeight: isMobile ? '36px' : '32px' }}
                title={t('aiAssistant.voice.stopSpeaking')}
              >
                <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8 7a1 1 0 00-1 1v4a1 1 0 001 1h4a1 1 0 001-1V8a1 1 0 00-1-1H8z" clipRule="evenodd" />
                </svg>
              </button>
            )}
            {/* Machine selector button - hide on very small screens when minimized */}
            {(!isMobile || !isMinimized) && (
              <button
                onClick={() => setShowMachineSelector(!showMachineSelector)}
                className="p-2 md:p-1.5 hover:bg-blue-700 rounded transition-colors touch-manipulation"
                style={{ minWidth: isMobile ? '36px' : '32px', minHeight: isMobile ? '36px' : '32px' }}
                title={t('aiAssistant.selectMachine')}
              >
                <svg className="w-6 h-6" viewBox="0 0 50 50" fill="none" stroke="currentColor">
                  {/* AutoBoss machine icon */}
                  <defs>
                    <linearGradient id="deckGrad" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="0" stopColor="currentColor" stopOpacity="0.3"/>
                      <stop offset="1" stopColor="currentColor" stopOpacity="0.15"/>
                    </linearGradient>
                  </defs>
                  <rect x="8" y="7" width="34" height="30" rx="6" fill="none" stroke="currentColor" strokeWidth="1.1"/>
                  <g fill="url(#deckGrad)" stroke="currentColor" strokeWidth="0.9" strokeLinejoin="round">
                    <rect x="14" y="10" width="22" height="22" rx="2.2"/>
                    <path d="M25 10 v22" fill="none"/>
                  </g>
                  <g fill="currentColor" fillOpacity="0.2" stroke="currentColor" strokeWidth="0.9" strokeLinejoin="round">
                    <rect x="23" y="31.5" width="4" height="6" rx="0.8"/>
                    <rect x="21.3" y="35.5" width="7.4" height="4" rx="0.9"/>
                  </g>
                  <g fill="none" stroke="currentColor" strokeWidth="0.9" strokeLinecap="round" strokeLinejoin="round">
                    <path d="M12.2 28.5 L7.5 32.2" />
                    <path d="M37.8 28.5 L42.5 32.2" />
                  </g>
                  <g fill="currentColor" fillOpacity="0.25" stroke="currentColor" strokeWidth="0.9">
                    <ellipse cx="6.3" cy="35.7" rx="5.2" ry="3.9"/>
                    <ellipse cx="43.7" cy="35.7" rx="5.2" ry="3.9"/>
                    <circle cx="6.3" cy="35.7" r="1.1" fill="currentColor" fillOpacity="0.5" stroke="none"/>
                    <circle cx="43.7" cy="35.7" r="1.1" fill="currentColor" fillOpacity="0.5" stroke="none"/>
                  </g>
                </svg>
              </button>
            )}
            {/* Escalation button */}
            <button
              onClick={handleShowEscalation}
              className="p-2 md:p-1.5 hover:bg-red-700 bg-red-600 rounded transition-colors touch-manipulation"
              style={{ minWidth: isMobile ? '36px' : '32px', minHeight: isMobile ? '36px' : '32px' }}
              title={t('aiAssistant.escalate')}
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 16.5c-.77.833.192 2.5 1.732 2.5z" />
              </svg>
            </button>
            {/* Full screen toggle for mobile */}
            {isMobile && !isMinimized && (
              <button
                onClick={() => setIsFullScreen(!isFullScreen)}
                className="p-2 md:p-1.5 hover:bg-blue-700 rounded transition-colors touch-manipulation"
                style={{ minWidth: isMobile ? '36px' : '32px', minHeight: isMobile ? '36px' : '32px' }}
                title={isFullScreen ? t('aiAssistant.chatWidget.exitFullScreen') : t('aiAssistant.chatWidget.fullScreen')}
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  {isFullScreen ? (
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 9V4.5M9 9H4.5M9 9L3.75 3.75M9 15v4.5M9 15H4.5M9 15l-5.25 5.25M15 9h4.5M15 9V4.5M15 9l5.25-5.25M15 15h4.5M15 15v4.5m0-4.5l5.25 5.25" />
                  ) : (
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 8V4m0 0h4M4 4l5 5m11-1V4m0 0h-4m4 0l-5 5M4 16v4m0 0h4m-4 0l5-5m11 5l-5-5m5 5v-4m0 4h-4" />
                  )}
                </svg>
              </button>
            )}
            <button
              onClick={handleMinimize}
              className="p-2 md:p-1.5 hover:bg-blue-700 rounded transition-colors touch-manipulation"
              style={{ minWidth: isMobile ? '36px' : '32px', minHeight: isMobile ? '36px' : '32px' }}
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
              className="p-2 md:p-1.5 hover:bg-blue-700 rounded transition-colors touch-manipulation"
              style={{ minWidth: isMobile ? '36px' : '32px', minHeight: isMobile ? '36px' : '32px' }}
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
          <div className="bg-white border-b border-gray-200 p-3 md:p-4">
            <div className="mb-2 flex items-center justify-between">
              <h4 className="text-sm md:text-base font-medium text-gray-700">{t('aiAssistant.selectMachine')}</h4>
              {selectedMachine && (
                <button
                  onClick={handleClearMachine}
                  className="text-xs md:text-sm text-red-600 hover:text-red-800 touch-manipulation p-1"
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
              <div className={`space-y-1 overflow-y-auto ${
                isMobile ? 'max-h-48' : 'max-h-32'
              }`}>
                {availableMachines.map((machine) => (
                  <button
                    key={machine.id}
                    onClick={() => handleMachineSelect(machine)}
                    className={`w-full text-left p-3 md:p-2 rounded text-sm md:text-base transition-colors touch-manipulation ${
                      selectedMachine?.id === machine.id
                        ? 'bg-blue-100 text-blue-800 border border-blue-200'
                        : 'hover:bg-gray-100 active:bg-gray-200 text-gray-700'
                    }`}
                  >
                    <div className="font-medium truncate">{machine.name}</div>
                    <div className="text-xs md:text-sm text-gray-500 truncate">
                      {machine.model_type} • {machine.latest_hours || 0}h
                      {!isMobile && ` • ${machine.customer_organization_name || 'Unknown Org'}`}
                    </div>
                  </button>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Chat Content - Hidden when minimized */}
        {!isMinimized && (
          <div className="flex flex-col" style={{ 
            height: isMobile && isFullScreen ? 'calc(100vh - 3.5rem)' : 'calc(100% - 3.5rem)'
          }}>
            {/* Messages Area */}
            <div className="flex-1 p-3 md:p-4 overflow-y-auto bg-gray-50 min-h-0 overscroll-contain" style={{
              maxHeight: isMobile ? 'calc(100% - 5rem)' : undefined
            }}>
              <div className="space-y-3 md:space-y-4">
                {messages.map((message) => (
                  <div
                    key={message.id}
                    className={`flex ${message.sender === 'user' ? 
                      (isRTL() ? 'justify-start' : 'justify-end') : 
                      (isRTL() ? 'justify-end' : 'justify-start')
                    }`}
                  >
                    {/* Troubleshooting Step Message */}
                    {message.type === 'diagnostic_step' && message.stepData ? (
                      <div className={`${
                        isMobile ? 'max-w-[90%]' : 'max-w-md lg:max-w-lg'
                      } w-full`}>
                        <div className="bg-blue-50 border-l-4 border-blue-500 rounded-lg p-4 shadow-sm">
                          {/* Step Header */}
                          <div className="flex items-center justify-between mb-3">
                            <span className="text-sm font-semibold text-blue-800 flex items-center gap-2">
                              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
                              </svg>
                              {t('aiAssistant.troubleshooting.stepNumber', { number: message.stepData.step_number || 1 })}
                            </span>
                            <span className="text-xs text-blue-600 bg-blue-100 px-2 py-1 rounded">
                              ⏱ {t('aiAssistant.troubleshooting.estimatedTime', { minutes: message.stepData.estimated_duration || 15 })}
                            </span>
                          </div>
                          
                          {/* Success Rate Badge */}
                          {message.stepData.confidence_score && message.stepData.confidence_score > 0 && (
                            <div className="mb-2">
                              <span className="text-xs text-blue-700 bg-blue-100 px-2 py-1 rounded-full inline-flex items-center gap-1">
                                <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
                                  <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                                </svg>
                                {t('aiAssistant.troubleshooting.successRate', { rate: Math.round((message.stepData.confidence_score || 0.7) * 100) })}
                              </span>
                            </div>
                          )}
                          
                          {/* Step Instruction */}
                          <p className="text-gray-800 mb-3 leading-relaxed">{message.content}</p>
                          
                          {/* Safety Warnings */}
                          {message.stepData.safety_warnings && message.stepData.safety_warnings.length > 0 && (
                            <div className="mt-3 p-3 bg-yellow-50 border border-yellow-200 rounded-md">
                              <p className="text-xs font-semibold text-yellow-800 flex items-center gap-1 mb-1">
                                <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                                  <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                                </svg>
                                {t('aiAssistant.troubleshooting.safetyWarning')}
                              </p>
                              <ul className="text-xs text-yellow-700 list-disc list-inside space-y-1">
                                {message.stepData.safety_warnings.map((warning, idx) => (
                                  <li key={idx}>{warning}</li>
                                ))}
                              </ul>
                            </div>
                          )}
                          
                          {/* Feedback Buttons */}
                          {awaitingFeedback && message.id === messages[messages.length - 1].id && !isLoading && (
                            <div className="mt-4 pt-3 border-t border-blue-200">
                              <p className="text-sm font-medium text-gray-700 mb-2">
                                {t('aiAssistant.feedback.provideFeedback')}
                              </p>
                              <div className="flex flex-col sm:flex-row gap-2">
                                <button
                                  onClick={() => handleStepFeedback('worked')}
                                  className="flex-1 bg-green-500 hover:bg-green-600 active:bg-green-700 text-white px-4 py-2.5 rounded-md font-medium transition-colors touch-manipulation flex items-center justify-center gap-2"
                                  style={{ minHeight: isMobile ? '44px' : '40px' }}
                                >
                                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                                  </svg>
                                  {t('aiAssistant.feedback.worked')}
                                </button>
                                <button
                                  onClick={() => handleStepFeedback('partially_worked')}
                                  className="flex-1 bg-yellow-500 hover:bg-yellow-600 active:bg-yellow-700 text-white px-4 py-2.5 rounded-md font-medium transition-colors touch-manipulation flex items-center justify-center gap-2"
                                  style={{ minHeight: isMobile ? '44px' : '40px' }}
                                >
                                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                                  </svg>
                                  {t('aiAssistant.feedback.partiallyWorked')}
                                </button>
                                <button
                                  onClick={() => handleStepFeedback('didnt_work')}
                                  className="flex-1 bg-red-500 hover:bg-red-600 active:bg-red-700 text-white px-4 py-2.5 rounded-md font-medium transition-colors touch-manipulation flex items-center justify-center gap-2"
                                  style={{ minHeight: isMobile ? '44px' : '40px' }}
                                >
                                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                                  </svg>
                                  {t('aiAssistant.feedback.didntWork')}
                                </button>
                              </div>
                            </div>
                          )}
                          
                          {/* Timestamp */}
                          <div className="mt-2 text-xs text-gray-500">
                            {formatTime(message.timestamp)}
                          </div>
                        </div>
                      </div>
                    ) : (
                      /* Regular Message */
                      <div
                        className={`${
                          isMobile ? 'max-w-[85%]' : 'max-w-xs lg:max-w-md'
                        } px-3 py-2 rounded-lg text-sm md:text-base ${
                          message.sender === 'user'
                            ? 'bg-blue-600 text-white'
                            : message.sender === 'system' && message.type === 'info'
                            ? 'bg-green-100 text-green-800 border border-green-200'
                            : message.sender === 'system' && message.type === 'completion'
                            ? 'bg-green-100 text-green-800 border border-green-200'
                            : message.sender === 'system' && message.type === 'escalation'
                            ? 'bg-orange-100 text-orange-800 border border-orange-200'
                            : message.sender === 'system'
                            ? 'bg-red-100 text-red-800 border border-red-200'
                            : 'bg-white text-gray-800 border border-gray-200'
                        }`}
                      >
                        <p className="break-words whitespace-pre-wrap">{message.content}</p>
                        <div className={`flex items-center justify-between mt-1 gap-2 ${
                          message.sender === 'user' ? 'text-blue-100' : 'text-gray-500'
                        }`}>
                          <p className="text-xs flex-shrink-0">
                            {formatTime(message.timestamp)}
                          </p>
                          {/* Speak button for assistant messages */}
                          {message.sender === 'assistant' && message.type === 'text' && (
                            <button
                              onClick={() => speakResponse(message.content)}
                              className={`p-1.5 md:p-1 rounded hover:bg-opacity-20 hover:bg-gray-500 transition-colors touch-manipulation ${
                                message.sender === 'user' ? 'text-blue-100' : 'text-gray-400 hover:text-gray-600'
                              }`}
                              title={t('aiAssistant.voice.speakResponse')}
                            >
                              <svg className="w-3 h-3 md:w-4 md:h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15.536 8.464a5 5 0 010 7.072m2.828-9.9a9 9 0 010 14.142M8.5 6.5v11m-3-5.5h7" />
                              </svg>
                            </button>
                          )}
                        </div>
                      </div>
                    )}
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
                        <span className="text-xs md:text-sm text-gray-500">{t('aiAssistant.chatWidget.typing')}</span>
                      </div>
                    </div>
                  </div>
                )}
              </div>
              <div ref={messagesEndRef} />
            </div>

            {/* Input Area */}
            <div className={`flex-shrink-0 p-3 md:p-4 border-t border-gray-200 bg-white ${
              isFullScreen && isMobile ? '' : 'rounded-b-lg'
            }`}
            style={{
              paddingBottom: isMobile ? 'max(0.75rem, env(safe-area-inset-bottom))' : undefined,
              position: isMobile ? 'sticky' : 'relative',
              bottom: 0,
              zIndex: 10
            }}>
              <form onSubmit={handleSendMessage} className="flex space-x-2 items-end">
                <div className="flex-1 flex space-x-2 items-end">
                  <input
                    ref={inputRef}
                    type="text"
                    value={inputMessage}
                    onChange={(e) => setInputMessage(e.target.value)}
                    placeholder={t('aiAssistant.messages.placeholder')}
                    className={`flex-1 px-3 py-2.5 md:py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm md:text-base touch-manipulation ${
                      isRTL() ? 'text-right' : 'text-left'
                    }`}
                    style={{
                      minHeight: isMobile ? '44px' : '40px',
                      fontSize: isMobile ? '16px' : undefined // Prevents zoom on iOS
                    }}
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
                  className={`flex-shrink-0 ${
                    isMobile ? 'px-3 py-2.5' : 'px-4 py-2'
                  } bg-blue-600 text-white rounded-md hover:bg-blue-700 active:bg-blue-800 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors touch-manipulation`}
                  style={{
                    minHeight: isMobile ? '44px' : '40px',
                    minWidth: isMobile ? '44px' : '40px'
                  }}
                >
                  <svg className={`${isMobile ? 'w-5 h-5' : 'w-4 h-4'}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
                  </svg>
                </button>
              </form>
            </div>
          </div>
        )}
      </div>
      
      {/* Escalation Modal */}
      <EscalationModal
        isOpen={showEscalationModal}
        onClose={() => setShowEscalationModal(false)}
        onEscalate={handleEscalateSession}
        sessionId={currentSessionId}
        confidenceScore={confidenceScore}
      />
    </div>
  );
};

export default ChatWidget;