// Global Speech Synthesis Manager
// This runs outside of React's render cycle to avoid interruptions

class SpeechSynthesisManager {
  constructor() {
    this.synthesis = window.speechSynthesis;
    this.currentUtterance = null;
    this.isInitialized = false;
    this.voices = [];
    this.callbacks = {
      onStart: null,
      onEnd: null,
      onError: null
    };
    
    this.init();
  }
  
  init() {
    if (!this.synthesis) {
      console.warn('SpeechSynthesisManager: Speech synthesis not supported');
      return;
    }
    
    this.loadVoices();
    this.synthesis.onvoiceschanged = () => this.loadVoices();
    this.isInitialized = true;
    
    // Prevent browser from pausing speech
    setInterval(() => {
      if (this.synthesis.paused && this.synthesis.speaking) {
        console.log('SpeechSynthesisManager: Resuming paused speech');
        this.synthesis.resume();
      }
    }, 1000);
  }
  
  loadVoices() {
    this.voices = this.synthesis.getVoices();
    console.log('SpeechSynthesisManager: Loaded', this.voices.length, 'voices');
  }
  
  getBestVoice(language = 'en') {
    const languageMap = {
      'en': 'en-US',
      'el': 'el-GR', 
      'ar': 'ar-SA',
      'es': 'es-ES',
      'tr': 'tr-TR',
      'no': 'nb-NO'
    };
    
    const langCode = languageMap[language] || 'en-US';
    const primaryLang = langCode.split('-')[0];
    
    // Try exact match first
    let voice = this.voices.find(v => v.lang === langCode);
    
    // Fallback to language family
    if (!voice) {
      voice = this.voices.find(v => v.lang.startsWith(primaryLang));
    }
    
    // Fallback to default
    if (!voice) {
      voice = this.voices.find(v => v.default) || this.voices[0];
    }
    
    return voice;
  }
  
  speak(text, options = {}) {
    if (!this.isInitialized || !text) {
      console.warn('SpeechSynthesisManager: Cannot speak - not initialized or no text');
      return false;
    }
    
    // Cancel any ongoing speech
    this.cancel();
    
    return new Promise((resolve, reject) => {
      // Wait for cancellation to complete
      setTimeout(() => {
        try {
          const utterance = new SpeechSynthesisUtterance(text);
          const voice = this.getBestVoice(options.language || 'en');
          
          if (voice) {
            utterance.voice = voice;
            utterance.lang = voice.lang;
          }
          
          utterance.rate = options.rate || 0.8;
          utterance.pitch = options.pitch || 1;
          utterance.volume = options.volume || 0.9;
          
          utterance.onstart = () => {
            console.log('SpeechSynthesisManager: Speech started');
            if (this.callbacks.onStart) this.callbacks.onStart();
            resolve(true);
          };
          
          utterance.onend = () => {
            console.log('SpeechSynthesisManager: Speech ended');
            this.currentUtterance = null;
            if (this.callbacks.onEnd) this.callbacks.onEnd();
          };
          
          utterance.onerror = (event) => {
            console.log('SpeechSynthesisManager: Speech error:', event.error);
            this.currentUtterance = null;
            if (this.callbacks.onError) this.callbacks.onError(event.error);
            
            // Don't reject for "interrupted" errors as they're often normal
            if (event.error === 'interrupted') {
              resolve(false);
            } else {
              reject(new Error(event.error));
            }
          };
          
          this.currentUtterance = utterance;
          this.synthesis.speak(utterance);
          
          // Fallback timeout
          setTimeout(() => {
            if (!this.synthesis.speaking) {
              console.warn('SpeechSynthesisManager: Speech did not start, retrying...');
              this.synthesis.speak(utterance);
            }
          }, 500);
          
        } catch (error) {
          console.error('SpeechSynthesisManager: Error creating utterance:', error);
          reject(error);
        }
      }, 100);
    });
  }
  
  cancel() {
    if (this.synthesis) {
      this.synthesis.cancel();
      this.currentUtterance = null;
    }
  }
  
  isSpeaking() {
    return this.synthesis ? this.synthesis.speaking : false;
  }
  
  setCallbacks(callbacks) {
    this.callbacks = { ...this.callbacks, ...callbacks };
  }
}

// Create global instance
const speechManager = new SpeechSynthesisManager();

export default speechManager;