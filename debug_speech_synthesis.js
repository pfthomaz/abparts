// Debug script for speech synthesis issues
// Run this in browser console to diagnose TTS problems

console.log('=== AutoBoss AI Assistant Speech Synthesis Debug ===');

// Test 1: Check Web Speech API availability
console.log('\n1. Web Speech API Support:');
console.log('  - speechSynthesis available:', !!window.speechSynthesis);
console.log('  - SpeechSynthesisUtterance available:', !!window.SpeechSynthesisUtterance);

if (!window.speechSynthesis) {
  console.error('❌ Speech Synthesis not supported in this browser');
  return;
}

// Test 2: Check current state
console.log('\n2. Current Speech Synthesis State:');
console.log('  - speaking:', window.speechSynthesis.speaking);
console.log('  - pending:', window.speechSynthesis.pending);
console.log('  - paused:', window.speechSynthesis.paused);

// Test 3: Available voices
console.log('\n3. Available Voices:');
const voices = window.speechSynthesis.getVoices();
console.log('  - Total voices:', voices.length);

if (voices.length === 0) {
  console.warn('⚠️ No voices loaded yet. Waiting for voices...');
  window.speechSynthesis.onvoiceschanged = () => {
    const newVoices = window.speechSynthesis.getVoices();
    console.log('  - Voices loaded:', newVoices.length);
    listVoicesByLanguage(newVoices);
  };
} else {
  listVoicesByLanguage(voices);
}

function listVoicesByLanguage(voices) {
  const languageGroups = {
    'en': voices.filter(v => v.lang.startsWith('en')),
    'el': voices.filter(v => v.lang.startsWith('el')),
    'ar': voices.filter(v => v.lang.startsWith('ar')),
    'es': voices.filter(v => v.lang.startsWith('es')),
    'tr': voices.filter(v => v.lang.startsWith('tr')),
    'no': voices.filter(v => v.lang.startsWith('no') || v.lang.startsWith('nb'))
  };
  
  Object.entries(languageGroups).forEach(([lang, langVoices]) => {
    if (langVoices.length > 0) {
      console.log(`  - ${lang.toUpperCase()}: ${langVoices.length} voices`);
      langVoices.forEach((voice, index) => {
        const marker = voice.default ? ' (default)' : '';
        console.log(`    ${index + 1}. ${voice.name} (${voice.lang})${marker}`);
      });
    } else {
      console.log(`  - ${lang.toUpperCase()}: ❌ No voices available`);
    }
  });
}

// Test 4: Test speech synthesis with different approaches
console.log('\n4. Testing Speech Synthesis:');

function testSpeech(text, options = {}) {
  return new Promise((resolve, reject) => {
    console.log(`  Testing: "${text}"`);
    
    // Cancel any ongoing speech
    window.speechSynthesis.cancel();
    
    setTimeout(() => {
      const utterance = new SpeechSynthesisUtterance(text);
      
      // Apply options
      if (options.voice) utterance.voice = options.voice;
      if (options.rate) utterance.rate = options.rate;
      if (options.pitch) utterance.pitch = options.pitch;
      if (options.volume) utterance.volume = options.volume;
      if (options.lang) utterance.lang = options.lang;
      
      utterance.onstart = () => {
        console.log('    ✓ Speech started');
      };
      
      utterance.onend = () => {
        console.log('    ✓ Speech completed successfully');
        resolve();
      };
      
      utterance.onerror = (event) => {
        console.error('    ❌ Speech error:', event.error);
        reject(event.error);
      };
      
      utterance.onpause = () => {
        console.log('    ⏸️ Speech paused');
      };
      
      utterance.onresume = () => {
        console.log('    ▶️ Speech resumed');
      };
      
      console.log('    Starting speech synthesis...');
      window.speechSynthesis.speak(utterance);
      
      // Check if speech actually started
      setTimeout(() => {
        if (!window.speechSynthesis.speaking) {
          console.warn('    ⚠️ Speech synthesis did not start within 500ms');
        }
      }, 500);
      
    }, 100); // Small delay to ensure cancel is processed
  });
}

// Test with simple text
console.log('\n5. Running Test Speech:');
testSpeech('Hello, this is a test of the AutoBoss AI Assistant speech synthesis.', {
  rate: 0.8,
  pitch: 1,
  volume: 0.9
}).then(() => {
  console.log('✅ Basic speech test completed successfully');
}).catch((error) => {
  console.error('❌ Basic speech test failed:', error);
});

// Utility functions for manual testing
window.debugSpeech = {
  testBasic: () => testSpeech('This is a basic test'),
  testLong: () => testSpeech('This is a longer test message to see if the speech synthesis can handle more complex text without cutting off prematurely. The AutoBoss AI Assistant should be able to speak this entire message clearly.'),
  testLanguages: () => {
    const tests = [
      { text: 'Hello, how are you today?', lang: 'en-US' },
      { text: 'Γεια σας, πώς είστε σήμερα;', lang: 'el-GR' },
      { text: 'مرحبا، كيف حالك اليوم؟', lang: 'ar-SA' },
      { text: '¡Hola! ¿Cómo estás hoy?', lang: 'es-ES' },
      { text: 'Merhaba, bugün nasılsın?', lang: 'tr-TR' },
      { text: 'Hei, hvordan har du det i dag?', lang: 'nb-NO' }
    ];
    
    tests.forEach((test, index) => {
      setTimeout(() => {
        console.log(`Testing ${test.lang}:`, test.text);
        testSpeech(test.text, { lang: test.lang });
      }, index * 3000);
    });
  },
  cancel: () => {
    window.speechSynthesis.cancel();
    console.log('Speech synthesis cancelled');
  },
  getState: () => {
    return {
      speaking: window.speechSynthesis.speaking,
      pending: window.speechSynthesis.pending,
      paused: window.speechSynthesis.paused
    };
  }
};

console.log('\n6. Manual Testing Functions Available:');
console.log('  - debugSpeech.testBasic() - Test basic speech');
console.log('  - debugSpeech.testLong() - Test long message');
console.log('  - debugSpeech.testLanguages() - Test all languages');
console.log('  - debugSpeech.cancel() - Cancel current speech');
console.log('  - debugSpeech.getState() - Get current synthesis state');

console.log('\n=== Debug Complete ===');
console.log('If speech is cutting off, try:');
console.log('1. Check browser permissions for audio');
console.log('2. Ensure no other audio is playing');
console.log('3. Try different voices with debugSpeech.testBasic()');
console.log('4. Check console for error messages during speech');